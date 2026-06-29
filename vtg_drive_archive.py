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
from urllib.parse import quote


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "data"
DRIVE_SCOPE = "https://www.googleapis.com/auth/drive"
DRIVE_API = "https://www.googleapis.com/drive/v3"
DRIVE_UPLOAD_API = "https://www.googleapis.com/upload/drive/v3"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
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
    canonical = str(metadata.get("canonical_storm_key") or "").strip().lower()
    if canonical:
        return canonical
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
    for marker in ("data/", "VTG_IMG/"):
        marker_index = path.find(marker)
        if marker_index >= 0:
            return path[marker_index:]
    return path.lstrip("/")


def local_path_for_asset(path: str, output_root: Path) -> Path:
    normalized = normalize_asset_path(path)
    if normalized.startswith(("data/", "VTG_IMG/")):
        return PROJECT_ROOT / normalized
    return output_root / normalized


def archive_manifest_path_for_asset(output_root: Path, image_path: str) -> Path:
    local_path = local_path_for_asset(image_path, output_root)
    try:
        relative_parts = local_path.resolve().relative_to(output_root.resolve()).parts
    except ValueError:
        relative_parts = local_path.parts
    if len(relative_parts) >= 2 and str(relative_parts[0]).isdigit():
        return output_root / relative_parts[0] / relative_parts[1] / "drive_archive.json"
    return output_root / "drive_archive.json"


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
    target_storm_key: str = "",
    target_is_officially_ended: bool = False,
    target_system_dir: Path | None = None,
) -> list[ArchiveCandidate]:
    active_data_times = active_window_data_times(manifest)
    now = utc_now()
    candidates: dict[str, ArchiveCandidate] = {}

    metadata_paths = (
        sorted((target_system_dir / "metadata" / "runs").glob("*.json"))
        if target_system_dir is not None
        else sorted(output_root.glob("[0-9][0-9][0-9][0-9]/*/metadata/runs/*.json"))
    )
    for metadata_path in metadata_paths:
        metadata = load_json(metadata_path, None)
        if not isinstance(metadata, dict):
            continue
        storm_key = storm_key_from_metadata(metadata)
        if target_storm_key and storm_key != target_storm_key:
            continue
        image_path = normalize_asset_path(metadata.get("image_path") or "")
        if not image_path or not image_path.lower().endswith(".png"):
            continue
        local_path = local_path_for_asset(image_path, output_root)
        if not local_path.exists():
            continue
        if not target_is_officially_ended and metadata_is_active(
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
            storm_key=storm_key,
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
    return f"https://drive.usercontent.google.com/download?id={file_id}&export=view&authuser=0"


def quote_drive_query(value: str) -> str:
    return str(value).replace("\\", "\\\\").replace("'", "\\'")


class DriveClient:
    def __init__(self, auth_config: dict):
        import requests

        self._requests = requests
        self.session = requests.Session()
        self.folder_cache: dict[tuple[str, str], str] = {}
        self.auth_mode = str(auth_config.get("mode") or "")
        self.credentials = None
        self._request_class = None
        self.oauth_client_id = ""
        self.oauth_client_secret = ""
        self.oauth_refresh_token = ""
        self.access_token_expires_at = 0.0

        if self.auth_mode == "service_account":
            from google.auth.transport.requests import Request as GoogleAuthRequest
            from google.oauth2 import service_account

            self._request_class = GoogleAuthRequest
            self.credentials = service_account.Credentials.from_service_account_info(
                auth_config["service_account_info"],
                scopes=[DRIVE_SCOPE],
            )
        elif self.auth_mode == "oauth_refresh_token":
            self.oauth_client_id = str(auth_config.get("client_id") or "").strip()
            self.oauth_client_secret = str(auth_config.get("client_secret") or "").strip()
            self.oauth_refresh_token = str(auth_config.get("refresh_token") or "").strip()
            if not self.oauth_client_id or not self.oauth_client_secret or not self.oauth_refresh_token:
                raise SystemExit("GOOGLE_DRIVE_CLIENT_ID, GOOGLE_DRIVE_CLIENT_SECRET, and GOOGLE_DRIVE_REFRESH_TOKEN are required for OAuth uploads.")
        else:
            raise SystemExit("Unknown Google Drive auth mode.")

        self.refresh()

    def refresh(self) -> None:
        if self.auth_mode == "service_account":
            if self.credentials is None or self._request_class is None:
                raise RuntimeError("Service account credentials are not initialized.")
            if not self.credentials.valid:
                self.credentials.refresh(self._request_class())
            self.session.headers.update({"Authorization": f"Bearer {self.credentials.token}"})
            return

        response = self._requests.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": self.oauth_client_id,
                "client_secret": self.oauth_client_secret,
                "refresh_token": self.oauth_refresh_token,
                "grant_type": "refresh_token",
            },
            timeout=60,
        )
        if response.status_code >= 400:
            details = response.text[:500]
            try:
                error_code = str(response.json().get("error") or "")
            except (TypeError, ValueError):
                error_code = ""
            if error_code == "invalid_grant":
                details += (
                    " The refresh token has expired or was revoked. If the OAuth app is in Testing, "
                    "publish it as In production, authorize again, and replace GOOGLE_DRIVE_REFRESH_TOKEN."
                )
            raise RuntimeError(f"Google OAuth token refresh failed: HTTP {response.status_code} {details}")
        payload = response.json()
        access_token = str(payload.get("access_token") or "").strip()
        if not access_token:
            raise RuntimeError("Google OAuth token refresh did not return an access token.")
        self.access_token_expires_at = time.time() + float(payload.get("expires_in") or 3600)
        self.session.headers.update({"Authorization": f"Bearer {access_token}"})

    def token_is_stale(self) -> bool:
        if self.auth_mode == "service_account":
            return bool(self.credentials and self.credentials.expired)
        return time.time() >= self.access_token_expires_at - 60.0

    def request(self, method: str, url: str, **kwargs):
        if self.token_is_stale():
            self.refresh()
        response = self.session.request(method, url, timeout=120, **kwargs)
        if response.status_code >= 400:
            details = response.text[:500]
            if response.status_code == 403 and "Service Accounts do not have storage quota" in response.text:
                details += " Use OAuth refresh-token auth for My Drive uploads, or upload to a Google Workspace shared drive."
            raise RuntimeError(f"Drive API {method} {url} failed: HTTP {response.status_code} {details}")
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

    def ensure_public_reader(self, file_id: str) -> bool:
        clean_id = str(file_id or "").strip()
        if not clean_id:
            return False
        encoded_id = quote(clean_id, safe="")
        permissions = self.request(
            "GET",
            f"{DRIVE_API}/files/{encoded_id}/permissions",
            params={
                "fields": "permissions(id,type,role,deleted)",
                "supportsAllDrives": "true",
            },
        ).json().get("permissions", [])
        for permission in permissions:
            if permission.get("type") != "anyone" or permission.get("deleted"):
                continue
            if permission.get("role") in {"reader", "commenter", "writer", "owner"}:
                return False
        self.request(
            "POST",
            f"{DRIVE_API}/files/{encoded_id}/permissions",
            params={
                "fields": "id",
                "supportsAllDrives": "true",
            },
            json={
                "type": "anyone",
                "role": "reader",
            },
        )
        return True


def service_account_info_from_args(args: argparse.Namespace) -> dict:
    if args.service_account_json_file:
        return json.loads(Path(args.service_account_json_file).read_text(encoding="utf-8"))
    raw = str(args.service_account_json or "").strip()
    if not raw:
        raise SystemExit("Google Drive auth is required for uploads. Prefer OAuth secrets for My Drive, or provide GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON for shared drives.")
    return json.loads(raw)


def drive_auth_config_from_args(args: argparse.Namespace) -> dict:
    refresh_token = str(args.oauth_refresh_token or "").strip()
    if refresh_token:
        return {
            "mode": "oauth_refresh_token",
            "client_id": args.oauth_client_id,
            "client_secret": args.oauth_client_secret,
            "refresh_token": refresh_token,
        }
    return {
        "mode": "service_account",
        "service_account_info": service_account_info_from_args(args),
    }


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
    payload = {
        key: value
        for key, value in base_payload.items()
        if key not in {"version", "updated_at_utc", "drive_folder_id", "images"}
    }
    payload.update({
        "version": max(1, int(base_payload.get("version") or 1)),
        "updated_at_utc": format_utc_stamp(),
        "drive_folder_id": folder_id,
        "images": {path: images[path] for path in sorted(images)},
    })
    return payload


def load_archive_manifests(output_root: Path, explicit_path: Path | None) -> tuple[dict[Path, dict], dict[str, dict]]:
    paths = [explicit_path] if explicit_path else sorted(output_root.glob("[0-9][0-9][0-9][0-9]/*/drive_archive.json"))
    payloads: dict[Path, dict] = {}
    merged_images: dict[str, dict] = {}
    for path in paths:
        if path is None:
            continue
        payload, images = load_archive_manifest(path)
        payloads[path] = payload
        merged_images.update(images)
    return payloads, merged_images


def archive_target_state(
    output_root: Path,
    storm_key: str,
) -> tuple[Path | None, dict]:
    normalized_key = str(storm_key or "").strip().lower()
    if not normalized_key:
        return None, {}
    for path in sorted(output_root.glob("[0-9][0-9][0-9][0-9]/*/metadata/archive_status.json")):
        status = load_json(path, {})
        if isinstance(status, dict) and str(status.get("storm_key") or "").strip().lower() == normalized_key:
            return path.parent.parent / "drive_archive.json", status
    return None, {}


def target_has_unarchived_local_images(
    target_archive_path: Path | None,
    archived_images: dict[str, dict],
) -> bool:
    if target_archive_path is None:
        return False
    image_dir = target_archive_path.parent / "images"
    for path in image_dir.glob("*.png"):
        image_path = relative_asset_path(path)
        if not archived_images.get(image_path, {}).get("file_id"):
            return True
    return False


def run(args: argparse.Namespace) -> int:
    if args.repair_only:
        args.repair_permissions = True
    output_root = args.output_root
    manifest_path = args.manifest_path or output_root / "manifest.json"
    manifest = load_json(manifest_path, {})
    if not isinstance(manifest, dict):
        manifest = {}
    target_storm_key = str(args.storm_key or "").strip().lower()
    target_archive_path, target_status = archive_target_state(output_root, target_storm_key)
    target_is_officially_ended = bool(
        target_storm_key
        and isinstance(target_status, dict)
        and str(target_status.get("official_status") or "").strip().lower() == "ended"
    )
    if target_storm_key and not target_is_officially_ended:
        raise SystemExit(
            f"Refusing targeted archive for {target_storm_key}: "
            "its per-system metadata/archive_status.json does not confirm official_status=ended."
        )
    archive_manifest_path = target_archive_path if target_storm_key else args.archive_manifest_path
    archive_payloads, archived_images = load_archive_manifests(output_root, archive_manifest_path)
    candidates = collect_archive_candidates(
        output_root=output_root,
        manifest=manifest,
        archived_images=archived_images,
        active_recency_hours=args.active_recency_hours,
        target_storm_key=target_storm_key,
        target_is_officially_ended=target_is_officially_ended,
        target_system_dir=target_archive_path.parent if target_archive_path is not None else None,
    )
    already_archived = [item for item in candidates if archived_images.get(item.image_path, {}).get("file_id")]
    upload_candidates = [item for item in candidates if item not in already_archived]
    if args.repair_only:
        upload_candidates = []
    if args.max_files and args.max_files > 0:
        upload_candidates = upload_candidates[:args.max_files]

    changed_paths: set[str] = set()
    touched_archive_paths: set[Path] = set()
    deleted_count = 0
    uploaded_count = 0
    reused_count = 0
    public_permission_count = 0
    total_upload_bytes = sum(item.size for item in upload_candidates)

    print(json.dumps({
        "candidate_count": len(candidates),
        "already_archived_count": len(already_archived),
        "upload_candidate_count": len(upload_candidates),
        "upload_candidate_bytes": total_upload_bytes,
        "target_storm_key": target_storm_key,
        "target_is_officially_ended": target_is_officially_ended,
        "auth_mode": "oauth_refresh_token" if str(args.oauth_refresh_token or "").strip() else "service_account",
        "delete_local_after_upload": bool(args.delete_local_after_upload),
        "repair_permissions": bool(args.repair_permissions),
        "repair_only": bool(args.repair_only),
        "dry_run": bool(args.dry_run),
    }, ensure_ascii=False, indent=2))

    if args.dry_run:
        preview = [item.image_path for item in upload_candidates[:20]]
        print(json.dumps({"upload_preview": preview}, ensure_ascii=False, indent=2))
        return 0

    folder_id = str(args.drive_folder_id or "").strip()
    if not folder_id:
        raise SystemExit("VTG_ARCHIVE_DRIVE_FOLDER_ID is required for uploads.")
    drive = DriveClient(drive_auth_config_from_args(args)) if upload_candidates or args.repair_permissions else None

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
        if drive and file_payload.get("id"):
            if drive.ensure_public_reader(str(file_payload["id"])):
                public_permission_count += 1
        archived_images[candidate.image_path] = archive_entry(
            file_payload,
            candidate,
            archived_images.get(candidate.image_path),
        )
        touched_archive_paths.add(archive_manifest_path_for_asset(output_root, candidate.image_path))
        time.sleep(max(0.0, args.upload_delay_seconds))

    if args.repair_permissions and drive:
        repaired_ids: set[str] = set()
        for path, entry in sorted(archived_images.items()):
            file_id = str(entry.get("file_id") or "").strip()
            if not file_id or file_id in repaired_ids:
                continue
            repaired_ids.add(file_id)
            if drive.ensure_public_reader(file_id):
                public_permission_count += 1
                print(f"Published Drive file for {path}")

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

    if args.archive_manifest_path:
        touched_archive_paths.add(args.archive_manifest_path)
    elif upload_candidates or args.repair_permissions:
        for image_path in archived_images:
            touched_archive_paths.add(archive_manifest_path_for_asset(output_root, image_path))

    for archive_manifest_path in sorted(touched_archive_paths):
        images_for_manifest = {
            image_path: entry
            for image_path, entry in archived_images.items()
            if archive_manifest_path_for_asset(output_root, image_path) == archive_manifest_path
        }
        archive_payload = archive_payloads.get(archive_manifest_path, {})
        archive_manifest = build_archive_manifest(archive_payload, images_for_manifest, folder_id=folder_id)
        if archive_manifest != archive_payload:
            write_json(archive_manifest_path, archive_manifest)
            changed_paths.add(relative_asset_path(archive_manifest_path))

    append_changed_paths(args.changed_paths_file, changed_paths)
    target_incomplete = bool(
        target_storm_key
        and target_has_unarchived_local_images(target_archive_path, archived_images)
    )
    print(json.dumps({
        "uploaded_count": uploaded_count,
        "reused_count": reused_count,
        "public_permission_count": public_permission_count,
        "deleted_local_count": deleted_count,
        "archive_manifest_count": len(touched_archive_paths),
        "changed_path_count": len(changed_paths),
        "target_incomplete": target_incomplete,
    }, ensure_ascii=False, indent=2))
    return 2 if target_incomplete else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upload ended VTG images to Google Drive and build archive manifest.")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--manifest-path", type=Path, default=None)
    parser.add_argument("--archive-manifest-path", type=Path, default=None, help="Legacy single archive manifest path. Default writes per-system drive_archive.json files.")
    parser.add_argument("--storm-key", default="", help="Archive only one officially ended canonical system, for example typ_2026_07.")
    parser.add_argument("--service-account-json", default=os.getenv("GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON", ""))
    parser.add_argument("--service-account-json-file", type=Path, default=None)
    parser.add_argument("--oauth-client-id", default=os.getenv("GOOGLE_DRIVE_CLIENT_ID", ""))
    parser.add_argument("--oauth-client-secret", default=os.getenv("GOOGLE_DRIVE_CLIENT_SECRET", ""))
    parser.add_argument("--oauth-refresh-token", default=os.getenv("GOOGLE_DRIVE_REFRESH_TOKEN", ""))
    parser.add_argument("--drive-folder-id", default=os.getenv("VTG_ARCHIVE_DRIVE_FOLDER_ID", ""))
    parser.add_argument("--changed-paths-file", type=Path, default=None)
    parser.add_argument("--max-files", type=int, default=0, help="Maximum new files to upload; 0 means no limit.")
    parser.add_argument("--active-recency-hours", type=float, default=DEFAULT_ACTIVE_RECENCY_HOURS)
    parser.add_argument("--upload-delay-seconds", type=float, default=0.0)
    parser.add_argument("--delete-local-after-upload", action="store_true")
    parser.add_argument("--repair-permissions", action="store_true", help="Ensure existing Drive archive files are readable by anyone with the link.")
    parser.add_argument("--repair-only", action="store_true", help="Skip new uploads and only repair permissions for files already listed in the archive manifest.")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(run(parse_args()))
