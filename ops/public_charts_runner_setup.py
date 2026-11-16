"""Install a separate, checksum-pinned chart runner without changing VTG."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import shlex
from urllib.request import urlopen

REPOSITORY = "https://github.com/SSalKim/CDS-Public-Charts"
NAME = "LAPTOP-WOOJIN-CHARTS"
URL = "https://github.com/actions/runner/releases/download/v2.338.2/actions-runner-linux-x64-2.338.2.tar.gz"
SHA256 = "baebf204307bac6193480852732f0aba2ae97b6c5597c244f4d5558390147c40"


def install():
    os.umask(0o077)
    home = Path.home().resolve()
    root = home / "actions-runner-cds-public-charts"
    if root.is_symlink() or root.resolve().parent != home:
        raise RuntimeError("Unsafe runner installation path")
    marker = root / ".cds-public-charts-bootstrap"
    if root.exists() and any(root.iterdir()) and not marker.is_file():
        raise RuntimeError("Existing unowned directory will not be changed")
    root.mkdir(mode=0o700, exist_ok=True)
    marker.write_text("cds-public-charts-v1\n", encoding="utf-8")
    old_root = Path(os.environ["RUNNER_WORKSPACE"]).resolve().parents[1]
    if not (old_root / "bin/Runner.Listener").is_file() or old_root == root:
        raise RuntimeError("Existing VTG runner location could not be verified")
    clean = {key: value for key, value in os.environ.items()
             if not key.startswith(("GITHUB_", "ACTIONS_", "RUNNER_", "PUBLIC_CHARTS_"))
             and key not in {"GH_TOKEN", "RUNNER_STATUS_TOKEN", "MIGRATION_PUBLIC_KEY", "MIGRATION_KEY_ID"}}
    clean.update(RUNNER_TRACKING_ID="", CDS_VTG_RUNNER_ROOT=str(old_root))
    if os.geteuid() == 0:
        clean["RUNNER_ALLOW_RUNASROOT"] = "1"
    settings = root / ".runner"
    if settings.exists():
        if json.loads(settings.read_text())["gitHubUrl"].rstrip("/") != REPOSITORY:
            raise RuntimeError("Existing runner belongs to a different repository")
    else:
        with tempfile.TemporaryFile() as archive:
            with urlopen(URL, timeout=90) as response:
                digest = hashlib.sha256()
                while chunk := response.read(1024 * 1024):
                    digest.update(chunk)
                    archive.write(chunk)
            if digest.hexdigest() != SHA256:
                raise RuntimeError("Official runner checksum mismatch")
            archive.seek(0)
            with tarfile.open(fileobj=archive, mode="r:gz") as bundle:
                bundle.extractall(root, filter="data")
        token = os.environ.pop("PUBLIC_CHARTS_RUNNER_BOOTSTRAP_TOKEN")
        result = subprocess.run([str(root / "config.sh"), "--url", REPOSITORY, "--token", token,
                                 "--name", NAME, "--labels", "cds-public-charts", "--work", "_work",
                                 "--unattended"], cwd=root, env=clean, capture_output=True)
        if result.returncode:
            raise RuntimeError("Runner registration failed; secret output withheld")
    executable = (root / "bin/Runner.Listener").resolve()
    running = False
    for process in Path("/proc").iterdir():
        if process.name.isdigit():
            try:
                running |= (process / "exe").resolve(strict=True) == executable
            except (OSError, RuntimeError):
                pass
    if not running:
        with (root / "runner.log").open("ab") as output:
            process = subprocess.Popen(["bash", str(root / "run.sh")], cwd=root, env=clean,
                                       stdin=subprocess.DEVNULL, stdout=output, stderr=subprocess.STDOUT,
                                       start_new_session=True)
        (root / "runner.pid").write_text(str(process.pid), encoding="ascii")
    environment = root / ".env"
    lines = environment.read_text(encoding="utf-8").splitlines() if environment.exists() else []
    lines = [line for line in lines if not line.startswith("CDS_VTG_RUNNER_ROOT=")]
    lines.append("CDS_VTG_RUNNER_ROOT=" + str(old_root))
    environment.write_text("\n".join(lines) + "\n", encoding="utf-8")
    launcher = root / "start-charts.sh"
    launcher.write_text("#!/usr/bin/env bash\nset -euo pipefail\nexport CDS_VTG_RUNNER_ROOT="
                        + shlex.quote(str(old_root)) + "\ncd " + shlex.quote(str(root))
                        + "\nexec ./run.sh\n", encoding="utf-8")
    launcher.chmod(0o700)
    public_key = os.environ.get("MIGRATION_PUBLIC_KEY", "")
    if public_key:
        from nacl.public import PublicKey, SealedBox
        value = os.environ["RUNNER_STATUS_TOKEN"].encode("utf-8")
        if not value:
            raise RuntimeError("Runner status token is missing")
        encrypted = SealedBox(PublicKey(base64.b64decode(public_key))).encrypt(value)
        destination = Path(os.environ["RUNNER_TEMP"]) / "public-charts-runner-status-sealed.json"
        destination.write_text(json.dumps({"key_id": os.environ["MIGRATION_KEY_ID"],
                               "encrypted_value": base64.b64encode(encrypted).decode("ascii")}), encoding="utf-8")
    print(json.dumps({"runner": NAME, "repository": "SSalKim/CDS-Public-Charts",
                      "cpu_logical": os.cpu_count(), "installed": True,
                      "vtg_registration_changed": False, "sealed_status_token": bool(public_key)}))


if __name__ == "__main__":
    try:
        install()
    except Exception:
        raise SystemExit("Runner setup failed; no credential or command output was printed.") from None
