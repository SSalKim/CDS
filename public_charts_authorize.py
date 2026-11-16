"""Authorize the separate chart Drive locally and register secrets without printing tokens."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess


SECRET_PREFIXES = ("PUBLIC_CHARTS_DRIVE_", "PUBLIC_CHARTS_DRIVE2_", "PUBLIC_CHARTS_ICON_DRIVE_")
SECRET_SUFFIXES = ("CLIENT_ID", "CLIENT_SECRET", "REFRESH_TOKEN", "FOLDER_ID", "ACCOUNT_EMAIL")


def secret_names(prefix):
    if prefix not in SECRET_PREFIXES:
        raise ValueError("Only dedicated chart Drive secret prefixes are allowed")
    return tuple(prefix + name for name in SECRET_SUFFIXES)


def github_cli():
    executable = shutil.which("gh")
    if executable:
        return executable
    installed = Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "GitHub CLI/gh.exe"
    if installed.is_file():
        return str(installed)
    raise SystemExit("Install GitHub CLI and run gh auth login before authorization.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client-secrets", type=Path, required=True)
    parser.add_argument("--folder-id", required=True)
    parser.add_argument("--account-email", required=True)
    parser.add_argument("--register-repo", required=True, help="Explicit OWNER/REPO receiving dedicated chart Drive secrets")
    parser.add_argument("--secret-prefix", choices=SECRET_PREFIXES, default=SECRET_PREFIXES[0],
                        help="Use PUBLIC_CHARTS_DRIVE2_ for the second chart Drive account")
    args = parser.parse_args()
    from google_auth_oauthlib.flow import InstalledAppFlow
    from vtg_drive_archive import DriveClient
    from public_charts_drive import ChartDriveStore
    gh = github_cli()
    subprocess.run([gh, "auth", "status"], check=True, capture_output=True)
    config = json.loads(args.client_secrets.read_text(encoding="utf-8"))
    if "installed" not in config:
        parser.error("Create an OAuth Desktop app client and use its downloaded JSON")
    flow = InstalledAppFlow.from_client_config(config, scopes=["https://www.googleapis.com/auth/drive"])
    credentials = flow.run_local_server(port=0, access_type="offline", prompt="consent select_account",
                                        login_hint=args.account_email, authorization_prompt_message="Open the browser to authorize the NEW chart Drive account.",
                                        success_message="Authorization complete. Return to the terminal; tokens will not be displayed.")
    if not credentials.refresh_token:
        raise SystemExit("Google did not return an offline refresh token. No secrets were changed.")
    client = DriveClient({"mode": "oauth_refresh_token", "client_id": config["installed"]["client_id"],
                          "client_secret": config["installed"]["client_secret"], "refresh_token": credentials.refresh_token})
    ChartDriveStore(client, args.folder_id, args.account_email).verify_account_and_folder()
    values = {"CLIENT_ID": config["installed"]["client_id"], "CLIENT_SECRET": config["installed"]["client_secret"],
              "REFRESH_TOKEN": credentials.refresh_token, "FOLDER_ID": args.folder_id, "ACCOUNT_EMAIL": args.account_email}
    for name, value in zip(secret_names(args.secret_prefix), (values[key] for key in SECRET_SUFFIXES)):
        subprocess.run([gh, "secret", "set", name, "--repo", args.register_repo],
                       input=value.encode("utf-8"), check=True, capture_output=True)
    print(f"Five dedicated {args.secret_prefix}* secrets registered. VTG settings were not changed.")
    if args.secret_prefix != SECRET_PREFIXES[0]:
        print("Existing PUBLIC_CHARTS_DRIVE_* settings were not changed.")


if __name__ == "__main__":
    main()
