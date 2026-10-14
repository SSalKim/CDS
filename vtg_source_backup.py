"""Bounded, short-lived guidance backups, stored outside Git in Actions artifacts."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
import re
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
import zlib
from datetime import datetime, timedelta, timezone
from pathlib import Path

from vtg_archive_state import load_kma_rows, official_ended_systems


ARTIFACT_NAME = "vtg-source-backup-v1"
MAX_AGE_HOURS = 48
MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_TOTAL_BYTES = 64 * 1024 * 1024
STORM_RE = re.compile(r"^(typ|td)_\d{4}_\d{2}$")
ENTRY_RE = re.compile(r"^(typ|td)_\d{4}_\d{2}/\d{12}\.json\.gz$")


def cycle_time(cycle: str) -> datetime:
    if not re.fullmatch(r"\d{12}", cycle):
        raise ValueError("Invalid backup cycle")
    return datetime.strptime(cycle, "%Y%m%d%H%M").replace(tzinfo=timezone.utc)


def recent_cycle(cycle: str, now: datetime | None = None) -> bool:
    try:
        age = (now or datetime.now(timezone.utc)) - cycle_time(cycle)
        return timedelta(0) <= age <= timedelta(hours=MAX_AGE_HOURS)
    except ValueError:
        return False


def snapshot_path(root: Path, storm_key: str, cycle: str) -> Path:
    if not STORM_RE.fullmatch(storm_key):
        raise ValueError("Invalid backup storm key")
    cycle_time(cycle)
    return root / storm_key / f"{cycle}.json.gz"


def decode_snapshot(content: bytes) -> dict:
    if len(content) > MAX_FILE_BYTES:
        raise ValueError("Backup file exceeds size limit")
    with gzip.GzipFile(fileobj=io.BytesIO(content)) as handle:
        raw = handle.read(MAX_FILE_BYTES + 1)
    if len(raw) > MAX_FILE_BYTES:
        raise ValueError("Expanded backup exceeds size limit")
    payload = json.loads(raw)
    if not isinstance(payload, dict) or payload.get("version") != 1:
        raise ValueError("Unsupported backup format")
    if not STORM_RE.fullmatch(str(payload.get("storm_key", ""))):
        raise ValueError("Invalid backup identity")
    cycle_time(str(payload.get("cycle", "")))
    if not isinstance(payload.get("rows"), list):
        raise ValueError("Invalid backup rows")
    return payload


def read_snapshot(root: Path, storm_key: str, cycle: str) -> dict | None:
    path = snapshot_path(root, storm_key, cycle)
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return None
        payload = decode_snapshot(path.read_bytes())
        if payload["storm_key"] == storm_key and payload["cycle"] == cycle:
            return payload
    except (OSError, ValueError, EOFError, TypeError, zlib.error):
        pass
    return None


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
        Path(name).replace(path)
    finally:
        Path(name).unlink(missing_ok=True)


def write_snapshot(root: Path, payload: dict) -> None:
    content = json.dumps(payload, ensure_ascii=True, allow_nan=False, separators=(",", ":")).encode()
    if len(content) > MAX_FILE_BYTES:
        raise ValueError("Backup snapshot exceeds size limit")
    atomic_write(snapshot_path(root, payload["storm_key"], payload["cycle"]), gzip.compress(content, mtime=0))


def prune(root: Path, kma_cache_dir: Path, *, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    ended = set(official_ended_systems(kma_cache_dir, now))
    # A TD promoted to a TYP ends with that TYP, not at the promotion itself.
    for row in load_kma_rows(kma_cache_dir, "td_lst"):
        try:
            year, td, typ = int(row["YY"]), int(row["TD"]), int(row.get("TYP") or 0)
        except (KeyError, TypeError, ValueError):
            continue
        if f"typ_{year}_{typ:02d}" in ended:
            ended.add(f"td_{year}_{td:02d}")

    entries = []
    for path in sorted(root.glob("*/*.json.gz")):
        name = path.relative_to(root).as_posix()
        if not ENTRY_RE.fullmatch(name):
            continue
        payload = read_snapshot(root, path.parent.name, path.name[:12])
        aliases = {str(key) for key in (payload or {}).get("storm_keys", [])}
        if payload is None or not recent_cycle(payload["cycle"], now) or ({path.parent.name} | aliases) & ended:
            path.unlink()
            continue
        entries.append((path, payload["cycle"], path.stat().st_size))

    total = sum(size for _, _, size in entries)
    for path, _, size in sorted(entries, key=lambda item: (item[1], str(item[0]))):
        if total <= MAX_TOTAL_BYTES:
            break
        path.unlink()
        total -= size
    files = {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path, _, _ in entries if path.exists()
    }
    for directory in root.glob("*"):
        if STORM_RE.fullmatch(directory.name) and directory.is_dir() and not any(directory.iterdir()):
            directory.rmdir()
    index = {"version": 1, "files": files}
    # Publish an empty index too, so an empty backup replaces an ended storm's artifact.
    atomic_write(root / "index.json", json.dumps(index, sort_keys=True).encode())
    print(f"Source backup: {len(files)} recent storm/cycle snapshot(s), {total} compressed bytes.")
    return index


class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        redirected = super().redirect_request(request, fp, code, msg, headers, newurl)
        if redirected and urllib.parse.urlsplit(request.full_url).netloc != urllib.parse.urlsplit(newurl).netloc:
            redirected.remove_header("Authorization")
        return redirected


def github_request(path: str, *, method: str = "GET", binary: bool = False):
    repository = os.environ["GITHUB_REPOSITORY"]
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", repository):
        raise ValueError("Invalid GitHub repository")
    token = os.environ["GH_TOKEN"]
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repository}/actions/artifacts{path}",
        method=method,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "CDS-VTG-source-backup"},
    )
    with urllib.request.build_opener(SafeRedirect()).open(request, timeout=45) as response:
        content = response.read(MAX_TOTAL_BYTES + MAX_FILE_BYTES + 1)
    if len(content) > MAX_TOTAL_BYTES + MAX_FILE_BYTES:
        raise ValueError("GitHub backup response exceeds size limit")
    return content if binary else (json.loads(content) if content else {})


def list_artifacts() -> list[dict]:
    artifacts = []
    for page in range(1, 11):
        payload = github_request(f"?name={ARTIFACT_NAME}&per_page=100&page={page}")
        batch = payload.get("artifacts", [])
        artifacts.extend(item for item in batch if item.get("name") == ARTIFACT_NAME)
        if len(batch) < 100:
            return sorted(artifacts, key=lambda item: int(item["id"]), reverse=True)
    raise ValueError("Too many source backup artifacts; refusing incomplete cleanup")


def restore_archive(root: Path, content: bytes) -> None:
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        infos = archive.infolist()
        all_names = {info.filename for info in infos}
        names = {info.filename for info in infos if not info.is_dir()}
        if len(infos) != len(all_names) or "index.json" not in names or len(infos) > 1024:
            raise ValueError("Invalid backup artifact index")
        if any(info.is_dir() and not STORM_RE.fullmatch(info.filename.rstrip("/")) for info in infos):
            raise ValueError("Invalid backup artifact directory")
        if sum(info.file_size for info in infos) > MAX_TOTAL_BYTES + MAX_FILE_BYTES:
            raise ValueError("Expanded artifact exceeds size limit")
        if archive.getinfo("index.json").file_size > 1024 * 1024:
            raise ValueError("Backup index exceeds size limit")
        index = json.loads(archive.read("index.json"))
        if not isinstance(index, dict) or index.get("version") != 1 or not isinstance(index.get("files"), dict):
            raise ValueError("Invalid backup index")
        if names != {"index.json", *index["files"]}:
            raise ValueError("Backup artifact has unindexed files")
        verified = {}
        for name, digest in index["files"].items():
            if not ENTRY_RE.fullmatch(name) or archive.getinfo(name).file_size > MAX_FILE_BYTES:
                raise ValueError("Invalid backup path or size")
            data = archive.read(name)
            payload = decode_snapshot(data)
            if hashlib.sha256(data).hexdigest() != digest or name != f"{payload['storm_key']}/{payload['cycle']}.json.gz":
                raise ValueError("Backup artifact integrity mismatch")
            verified[name] = data
    # Validate the entire artifact before replacing any local snapshot.
    for path in root.glob("*/*.json.gz"):
        if ENTRY_RE.fullmatch(path.relative_to(root).as_posix()) and path.relative_to(root).as_posix() not in verified:
            path.unlink()
    for name, data in verified.items():
        atomic_write(root / name, data)


def restore(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    artifacts = [item for item in list_artifacts() if not item.get("expired")]
    if not artifacts:
        print("No previous source backup artifact; starting a new backup.")
        return
    for artifact in artifacts[:3]:
        try:
            restore_archive(root, github_request(f"/{int(artifact['id'])}/zip", binary=True))
            print(f"Restored source backup artifact {artifact['id']}.")
            return
        except (OSError, ValueError, EOFError, zipfile.BadZipFile, zlib.error) as exc:
            print(f"Warning: source backup artifact {artifact['id']} could not be restored ({type(exc).__name__}).")
    raise ValueError("No valid source backup could be restored; previous remote backups are preserved")


def cleanup(keep_id: int) -> None:
    current = github_request(f"/{keep_id}")
    if current.get("name") != ARTIFACT_NAME or current.get("expired"):
        raise ValueError("Cannot confirm the newly uploaded backup")
    if str(current.get("workflow_run", {}).get("id")) != os.environ["GITHUB_RUN_ID"]:
        raise ValueError("New source backup belongs to a different workflow run")
    for artifact in list_artifacts():
        if int(artifact["id"]) < keep_id:
            try:
                github_request(f"/{int(artifact['id'])}", method="DELETE")
            except urllib.error.HTTPError as exc:
                if exc.code != 404:
                    raise
    print("Replaced old source backup artifacts with the newly uploaded backup.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("restore", "prune", "cleanup"))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--kma-cache-dir", type=Path, default=Path("data/cache/kma_apihub"))
    parser.add_argument("--keep-id", type=int)
    args = parser.parse_args()
    try:
        if args.command == "restore":
            restore(args.root)
        elif args.command == "prune":
            prune(args.root, args.kma_cache_dir)
        else:
            if not args.keep_id:
                parser.error("cleanup requires --keep-id")
            cleanup(args.keep_id)
    except (OSError, ValueError, EOFError) as exc:
        # Do not print signed artifact URLs or authentication-bearing exceptions.
        raise SystemExit(f"Source backup {args.command} failed ({type(exc).__name__}); existing remote backups were not replaced.")


if __name__ == "__main__":
    main()
