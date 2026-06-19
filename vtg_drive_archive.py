from __future__ import annotations

import argparse
import json
import mimetypes
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "VTG_IMG"
DEFAULT_ARCHIVE_MANIFEST = DEFAULT_OUTPUT_ROOT / "drive_archive_manifest.json"
DRIVE_SCOPE = "https://www.googleapis.com/auth/drive"
DRIVE_API = "https://www.googleapis.com/drive/v3"
DRIVE_UPLOAD_API = "https://www.googleapis.com/upload/drive/v3"
DEFAULT_ACTIVE_RECENCY_HOURS = 30.0


@dataclass(frozen=True)
class ArchiveCandidate:
    image_path: str
    local_path: Path
    data_time: str
    storm_key: str
    size: int


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def format_utc_stamp(value: datetime | None = None) -> str:
    return (value or utc_now()).strftime("%Y%m%d%H%M%S")


def parse_utc_stamp(value: str) -> datetime | None:
    raw = str(value or "").strip()
    if not raw or not raw[:10].isdigit():
        return None
    try:
        year = int(raw[0:4])
        month = int(raw[4:6])
        day = int(raw[6:8])
        hour = int(raw[8:10])
        minute = int(raw[10:12] or "0")
        return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)
    except ValueError:
        return None


def load_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return fallback


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp_path.replace(path)


def relative_asset_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def metadata_int(value: Any) -> int | None:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def storm_key_from_metadata(metadata: dict) -> str:
    data_time = str(metadata.get("data_time") or "")
    year = str(metadata.get("storm_year") or data_time[:4] or "").strip()
    number = metadata_int(metadata.get("typ_number"))
    if not year or number is None:
        return ""
    prefix = "td" if str(metadata.get("storm_stage") or "TYP").upper() == "TD" else "typ"
    return f"{prefix}_{year}_{number:02d}"


def normalized_manifest_images(payload: Any) -> dict[str, dict]:
    if not isinstance(payload, dict):
        return {}
    images = payload.get("images")
    if isinstance(images, dict):
        result: dict[str, dict] = {}
        for path, value in images.items():
            image_path = normalize_asset_path(path)
            if not image_path:
                continue
            if isinstance(value, dict):
                result[image_path] = dict(value)
            elif isinstance(value, str):
                result[image_path] = {"url": value}
        return result
    if isinstance(images, list):
        result = {}
        for item in images:
            if not isinstance(item, dict):
                continue
            image_path = normalize_asset_path(item.get("image_path") or item.get("path") or "")
            if image_path:
                result[image_path] = dict(item)
        return result
    return {}


def normalize_asset_path(value: Any) -> str:
    path = str(value or "").replace("\\", "/").strip()
    if not path:
        return ""
    marker = "VTG_IMG/"
    marker_index = path.find(marker)
    if marker_index >= 0:
        return path[marker_index:]
    return path.lstrip("/")


def local_path_for_asset(path: str, output_root: Path) -> Path:
    normalized = normalize_asset_path(path)
    if normalized.startswith("VTG_IMG/"):
        return PROJECT_ROOT / normalized
    return output_root / normalized


def active_window_data_times(manifest: dict) -> set[str]:
    windows = manifest.get("active_windows") if isinstance(manifest, dict) else []
    result: set[str] = set()
    if isinstance(windows, list):
        for window in windows:
            if isinstance(window, dict):
                data_time = str(window.get("data_time") or "").strip()
                if data_time:
                    result.add(data_time)
                    result.add(data_time[:10])
    return result


def metadata_is_active(metadata: dict, *, active_data_times: set[str], now: datetime, recency_hours: float) -> bool:
    data_time = str(metadata.get("data_time") or "").strip()
    if not data_time:
        return False
    if data_time in active_data_times or data_time[:10] in active_data_times:
        return True
    parsed = parse_utc_stamp(data_time)
    if parsed is None:
        return False
    diff_hours = (now - parsed).total_seconds() / 3600.0
    return -6.0 <= diff_hours <= recency_hours


def collect_archive_candidates(
    *,
    output_root: Path,
    manifest: dict,
    archived_images: dict[str, dict],
    active_recency_hours: float,
) -> list[ArchiveCandidate]:
    metadata_root = output_root / "metadata"
    active_data_times = active_window_data_times(manifest)
    now = utc_now()
    candidates: dict[str, ArchiveCandidate] = {}

    for metadata_path in sorted(metadata_root.glob("*.json")):
        metadata = load_json(metadata_path, None)
        if not isinstance(metadata, dict):
            continue
        image_path = normalize_asset_path(metadata.get("image_path") or "")
        if not image_path or not image_path.lower().endswith(".png"):
            continue
        local_path = local_path_for_asset(image_path, output_root)
        if not local_path.exists():
            continue
        if metadata_is_active(
            metadata,
            active_data_times=active_data_times,
            now=now,
            recency_hours=active_recency_hours,
        ):
            continue
        try:
            size = local_path.stat().st_size
        except OSError:
            continue
        candidates[image_path] = ArchiveCandidate(
            image_path=image_path,
            local_path=local_path,
            data_time=str(metadata.get("data_time") or ""),
            storm_key=storm_key_from_metadata(metadata),
            size=size,
        )

    return sorted(
        candidates.values(),
        key=lambda item: (
            item.data_time,
            item.storm_key,
            item.image_path,
        ),
    )


def drive_url(file_id: str) -> str:
    return f"https://drive.google.com/uc?export=view&id={file_id}"


def quote_drive_query(value: str) -> str:
    return str(value).replace("\\", "\\\\").replace("'", "\\'")


class DriveClient:
    def __init__(self, service_account_info: dict):
        from google.auth.transport.requests import Request as GoogleAuthRequest
        from google.oauth2 import service_account
        import requests

        self._request_class = GoogleAuthRequest
        self._requests = requests
        self.credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=[DRIVE_SCOPE],
        )
        self.session = requests.Session()
        self.folder_cache: dict[tuple[str, str], str] = {}
        self.refresh()

    def refresh(self) -> None:
        if not self.credentials.valid:
            self.credentials.refresh(self._request_class())
        self.session.headers.update({"Authorization": f"Bearer {self.credentials.token}"})

    def request(self, method: str, url: str, **kwargs):
        if self.credentials.expired:
            self.refresh()
        response = self.session.request(method, url, timeout=120, **kwargs)
        if response.status_code >= 400:
            raise RuntimeError(f"Drive API {method} {url} failed: HTTP {response.status_code} {response.text[:500]}")
        return response

    def list_files(self, query: str, *, fields: str) -> list[dict]:
        files: list[dict] = []
        page_token = ""
        while True:
            params = {
                "q": query,
                "fields": f"nextPageToken,files({fields})",
                "pageSize": 1000,
                "supportsAllDrives": "true",
                "includeItemsFromAllDrives": "true",
            }
            if page_token:
                params["pageToken"] = page_token
            payload = self.request("GET", f"{DRIVE_API}/files", params=params).json()
            files.extend(payload.get("files", []))
            page_token = str(payload.get("nextPageToken") or "")
            if not page_token:
                return files

    def ensure_folder(self, parent_id: str, name: str) -> str:
        key = (parent_id, name)
        if key in self.folder_cache:
            return self.folder_cache[key]
        query = (
            f"'{quote_drive_query(parent_id)}' in parents and "
            f"name = '{quote_drive_query(name)}' and "
            "mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        )
        folders = self.list_files(query, fields="id,name")
        if folders:
            folder_id = str(folders[0]["id"])
            self.folder_cache[key] = folder_id
            return folder_id

        metadata = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id],
        }
        payload = self.request(
            "POST",
            f"{DRIVE_API}/files",
            params={"fields": "id,name", "supportsAllDrives": "true"},
            json=metadata,
        ).json()
        folder_id = str(payload["id"])
        self.folder_cache[key] = folder_id
        return folder_id

    def ensure_folder_path(self, root_folder_id: str, parts: list[str]) -> str:
        folder_id = root_folder_id
        for part in parts:
            if part:
                folder_id = self.ensure_folder(folder_id, part)
        return folder_id

    def find_file_by_vtg_path(self, image_path: str) -> dict | None:
        query = (
            "appProperties has { "
            f"key='vtg_path' and value='{quote_drive_query(image_path)}' "
            "} and trashed = false"
        )
        files = self.list_files(query, fields="id,name,size,md5Checksum,appProperties")
        return files[0] if files else None

    def find_file_by_name(self, parent_id: str, name: str) -> dict | None:
        query = (
            f"'{quote_drive_query(parent_id)}' in parents and "
            f"name = '{quote_drive_query(name)}' and "
            "mimeType != 'application/vnd.google-apps.folder' and trashed = false"
        )
        files = self.list_files(query, fields="id,name,size,md5Checksum,appProperties")
        return files[0] if files else None

    def upload_file(self, candidate: ArchiveCandidate, parent_id: str) -> dict:
        mime_type = mimetypes.guess_type(candidate.local_path.name)[0] or "application/octet-stream"
        metadata = {
            "name": candidate.local_path.name,
            "parents": [parent_id],
            "appProperties": {"vtg_path": candidate.image_path},
        }
        start = self.request(
            "POST",
            f"{DRIVE_UPLOAD_API}/files",
            params={
                "uploadType": "resumable",
                "fields": "id,name,size,md5Checksum,webViewLink",
                "supportsAllDrives": "true",
            },
            headers={
                "Content-Type": "application/json; charset=UTF-8",
                "X-Upload-Content-Type": mime_type,
                "X-Upload-Content-Length": str(candidate.size),
            },
            json=metadata,
        )
        upload_url = start.headers.get("Location")
        if not upload_url:
            raise RuntimeError("Drive API did not return a resumable upload URL.")
        with candidate.local_path.open("rb") as handle:
            response = self.request(
                "PUT",
                upload_url,
                headers={
                    "Content-Type": mime_type,
                    "Content-Length": str(candidate.size),
                },
                data=handle,
            )
        return response.json()


def service_account_info_from_args(args: argparse.Namespace) -> dict:
    if args.service_account_json_file:
        return json.loads(Path(args.service_account_json_file).read_text(encoding="utf-8"))
    raw = str(args.service_account_json or "").strip()
    if not raw:
        raise SystemExit("GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON is required for uploads.")
    return json.loads(raw)


def load_archive_manifest(path: Path) -> tuple[dict, dict[str, dict]]:
    payload = load_json(path, {})
    if not isinstance(payload, dict):
        payload = {}
    return payload, normalized_manifest_images(payload)


def archive_entry(file_payload: dict, candidate: ArchiveCandidate, existing: dict | None = None) -> dict:
    file_id = str(file_payload.get("id") or (existing or {}).get("file_id") or "").strip()
    entry = dict(existing or {})
    entry.update({
        "file_id": file_id,
        "url": drive_url(file_id),
        "size": candidate.size,
        "storm_key": candidate.storm_key,
        "data_time": candidate.data_time,
    })
    checksum = file_payload.get("md5Checksum")
    if checksum:
        entry["md5"] = checksum
    if not entry.get("uploaded_at_utc"):
        entry["uploaded_at_utc"] = format_utc_stamp()
    return entry


def remove_empty_parents(path: Path, stop_at: Path) -> None:
    try:
        stop = stop_at.resolve()
    except OSError:
        stop = stop_at.absolute()
    current = path
    while current != stop and stop in current.parents:
        try:
            current.rmdir()
        except OSError:
            return
        current = current.parent


def append_changed_paths(path: Path | None, changed_paths: set[str]) -> None:
    if path is None:
        return
    existing: set[str] = set()
    if path.exists():
        existing = {line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}
    merged = sorted(existing | {item for item in changed_paths if item})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(merged) + ("\n" if merged else ""), encoding="utf-8")


def build_archive_manifest(base_payload: dict, images: dict[str, dict], *, folder_id: str) -> dict:
    return {
        "version": 1,
        "updated_at_utc": format_utc_stamp(),
        "drive_folder_id": folder_id,
        "images": {path: images[path] for path in sorted(images)},
    }


def run(args: argparse.Namespace) -> int:
    output_root = args.output_root
    manifest_path = args.manifest_path or output_root / "manifest.json"
    archive_manifest_path = args.archive_manifest_path
    manifest = load_json(manifest_path, {})
    if not isinstance(manifest, dict):
        manifest = {}
    archive_payload, archived_images = load_archive_manifest(archive_manifest_path)
    candidates = collect_archive_candidates(
        output_root=output_root,
        manifest=manifest,
        archived_images=archived_images,
        active_recency_hours=args.active_recency_hours,
    )
    already_archived = [item for item in candidates if archived_images.get(item.image_path, {}).get("file_id")]
    upload_candidates = [item for item in candidates if item not in already_archived]
    if args.max_files and args.max_files > 0:
        upload_candidates = upload_candidates[:args.max_files]

    changed_paths: set[str] = set()
    deleted_count = 0
    uploaded_count = 0
    reused_count = 0
    total_upload_bytes = sum(item.size for item in upload_candidates)

    print(json.dumps({
        "candidate_count": len(candidates),
        "already_archived_count": len(already_archived),
        "upload_candidate_count": len(upload_candidates),
        "upload_candidate_bytes": total_upload_bytes,
        "delete_local_after_upload": bool(args.delete_local_after_upload),
        "dry_run": bool(args.dry_run),
    }, ensure_ascii=False, indent=2))

    if args.dry_run:
        preview = [item.image_path for item in upload_candidates[:20]]
        print(json.dumps({"upload_preview": preview}, ensure_ascii=False, indent=2))
        return 0

    folder_id = str(args.drive_folder_id or "").strip()
    if not folder_id:
        raise SystemExit("VTG_ARCHIVE_DRIVE_FOLDER_ID is required for uploads.")
    drive = DriveClient(service_account_info_from_args(args)) if upload_candidates else None

    for index, candidate in enumerate(upload_candidates, start=1):
        relative_parts = Path(candidate.image_path).parent.parts
        parent_id = drive.ensure_folder_path(folder_id, list(relative_parts)) if drive else folder_id
        existing_file = drive.find_file_by_vtg_path(candidate.image_path) if drive else None
        if existing_file is None and drive:
            existing_file = drive.find_file_by_name(parent_id, candidate.local_path.name)
        if existing_file:
            file_payload = existing_file
            reused_count += 1
            print(f"[{index}/{len(upload_candidates)}] Reusing Drive file for {candidate.image_path}")
        else:
            file_payload = drive.upload_file(candidate, parent_id) if drive else {}
            uploaded_count += 1
            print(f"[{index}/{len(upload_candidates)}] Uploaded {candidate.image_path}")
        archived_images[candidate.image_path] = archive_entry(
            file_payload,
            candidate,
            archived_images.get(candidate.image_path),
        )
        time.sleep(max(0.0, args.upload_delay_seconds))

    safe_to_delete = [
        item for item in candidates
        if archived_images.get(item.image_path, {}).get("file_id") and item.local_path.exists()
    ]
    if args.delete_local_after_upload:
        for candidate in safe_to_delete:
            candidate.local_path.unlink()
            changed_paths.add(relative_asset_path(candidate.local_path))
            deleted_count += 1
            remove_empty_parents(candidate.local_path.parent, output_root)

    archive_manifest = build_archive_manifest(archive_payload, archived_images, folder_id=folder_id)
    if archive_manifest != archive_payload:
        write_json(archive_manifest_path, archive_manifest)
        changed_paths.add(relative_asset_path(archive_manifest_path))

    append_changed_paths(args.changed_paths_file, changed_paths)
    print(json.dumps({
        "uploaded_count": uploaded_count,
        "reused_count": reused_count,
        "deleted_local_count": deleted_count,
        "archive_manifest": relative_asset_path(archive_manifest_path),
        "changed_path_count": len(changed_paths),
    }, ensure_ascii=False, indent=2))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upload ended VTG images to Google Drive and build archive manifest.")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--manifest-path", type=Path, default=None)
    parser.add_argument("--archive-manifest-path", type=Path, default=DEFAULT_ARCHIVE_MANIFEST)
    parser.add_argument("--service-account-json", default=os.getenv("GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON", ""))
    parser.add_argument("--service-account-json-file", type=Path, default=None)
    parser.add_argument("--drive-folder-id", default=os.getenv("VTG_ARCHIVE_DRIVE_FOLDER_ID", ""))
    parser.add_argument("--changed-paths-file", type=Path, default=None)
    parser.add_argument("--max-files", type=int, default=0, help="Maximum new files to upload; 0 means no limit.")
    parser.add_argument("--active-recency-hours", type=float, default=DEFAULT_ACTIVE_RECENCY_HOURS)
    parser.add_argument("--upload-delay-seconds", type=float, default=0.0)
    parser.add_argument("--delete-local-after-upload", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(run(parse_args()))
