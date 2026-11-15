"""Authorize the separate chart Drive locally and register secrets without printing tokens."""
import argparse
import json
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client-secrets", type=Path, required=True)
    parser.add_argument("--folder-id", required=True)
    parser.add_argument("--account-email", required=True)
    parser.add_argument("--register-repo", required=True, help="Explicit OWNER/REPO receiving only PUBLIC_CHARTS_DRIVE_* secrets")
    args = parser.parse_args()
    from google_auth_oauthlib.flow import InstalledAppFlow
    from vtg_drive_archive import DriveClient
    from public_charts_drive import ChartDriveStore
    subprocess.run(["gh", "auth", "status"], check=True, capture_output=True)
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
    for suffix, value in values.items():
        subprocess.run(["gh", "secret", "set", "PUBLIC_CHARTS_DRIVE_" + suffix, "--repo", args.register_repo],
                       input=value.encode("utf-8"), check=True, capture_output=True)
    print("Five dedicated PUBLIC_CHARTS_DRIVE_* secrets registered. VTG settings were not changed.")


if __name__ == "__main__":
    main()
