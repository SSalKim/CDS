"""Isolated My Drive storage for public charts; orchestration owns scheduling.

Only PUBLIC_CHARTS_DRIVE_* settings are read. Images are immutable versions;
state and manifest updates use an ETag precondition. Callers must serialize the
first creation of those two JSON entries (Drive names are not unique).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, BinaryIO
from urllib.parse import quote, urlsplit

from vtg_drive_archive import DRIVE_API, DRIVE_UPLOAD_API, DriveClient, drive_url


NAMESPACE = "cds-public-charts-v1"
FOLDER_MIME = "application/vnd.google-apps.folder"
JSON_NAMES = frozenset({"state.json", "manifest.json"})
ENV_PREFIX = "PUBLIC_CHARTS_DRIVE_"
FILE_FIELDS = (
    "id,name,mimeType,size,md5Checksum,parents,appProperties,trashed,"
    "ownedByMe,owners(emailAddress),driveId"
)
IMAGE_TYPES = {".webp": "image/webp", ".png": "image/png",
               ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}
KEY_PATTERN = re.compile(
    r"(?:aifs|gfs|aigfs|cmc)/([0-9]{10})/([0-9]{3})/"
    r"[a-z][a-z0-9_]{0,39}/(?:asia|hkor)\Z"
)


class ChartDriveError(RuntimeError):
    """A sanitized configuration, safety, integrity, or Drive API failure."""


def _file_id(value: Any) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,200}", value):
        raise ChartDriveError("Invalid Drive file or folder ID.")
    if value.casefold() == "root":
        raise ChartDriveError("My Drive root is not an allowed storage target.")
    return value


def _query_literal(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


class ChartDriveStore:
    """One explicitly configured, account-owned personal Drive folder.

    Construction with an injected client performs no IO. Public operations
    verify the account/folder lazily; from_environment verifies immediately.
    JSON files remain private unless sharing was configured outside this store.
    """

    def __init__(self, client: DriveClient | None, folder_id: str, account_email: str):
        self.folder_id = _file_id(folder_id)
        if not isinstance(account_email, str) or not re.fullmatch(
            r"[^\s@]+@[^\s@]+", account_email.strip()
        ):
            raise ChartDriveError("A valid PUBLIC_CHARTS_DRIVE_ACCOUNT_EMAIL is required.")
        self.account_email = account_email.strip().casefold()
        self._client = client
        self._verified = False

    @classmethod
    def from_environment(cls) -> ChartDriveStore:
        """Load only the five dedicated variables, authenticate, then verify."""
        names = ("CLIENT_ID", "CLIENT_SECRET", "REFRESH_TOKEN", "FOLDER_ID", "ACCOUNT_EMAIL")
        settings = {name: os.environ.get(ENV_PREFIX + name, "").strip() for name in names}
        missing = [ENV_PREFIX + name for name in names if not settings[name]]
        if missing:
            raise ChartDriveError("Missing dedicated Drive settings: " + ", ".join(missing))
        # Validate targets before the client makes its initial OAuth request.
        store = cls(None, settings["FOLDER_ID"], settings["ACCOUNT_EMAIL"])
        try:
            store._client = DriveClient({
                "mode": "oauth_refresh_token",
                "client_id": settings["CLIENT_ID"],
                "client_secret": settings["CLIENT_SECRET"],
                "refresh_token": settings["REFRESH_TOKEN"],
            })
        except (Exception, SystemExit):
            raise ChartDriveError("Dedicated Google Drive authentication failed.") from None
        store.verify_account_and_folder()
        return store

    def _request(self, method: str, url: str, **kwargs):
        # The shared client includes response bodies in errors; never expose them.
        try:
            response = self._client.request(method, url, allow_redirects=False, **kwargs)
            if not 200 <= response.status_code < 300:
                raise ValueError("Unexpected HTTP status")
        except (Exception, SystemExit):
            raise ChartDriveError("Google Drive request failed.") from None
        return response

    @staticmethod
    def _json(response) -> dict:
        try:
            value = response.json()
            if not isinstance(value, dict):
                raise ValueError("Expected an object")
            return value
        except (Exception, SystemExit):
            raise ChartDriveError("Google Drive returned invalid metadata.") from None

    def _metadata(self, file_id: str):
        response = self._request(
            "GET", f"{DRIVE_API}/files/{quote(_file_id(file_id), safe='')}",
            params={"fields": FILE_FIELDS},
        )
        metadata = self._json(response)
        if metadata.get("id") != file_id:
            raise ChartDriveError("Google Drive returned an unexpected file ID.")
        return metadata, response.headers.get("ETag")

    def _owned(self, metadata: dict) -> bool:
        owners = metadata.get("owners")
        return (
            metadata.get("ownedByMe") is True
            and not metadata.get("driveId")
            and isinstance(owners, list)
            and len(owners) == 1
            and isinstance(owners[0], dict)
            and str(owners[0].get("emailAddress", "")).casefold() == self.account_email
        )

    def verify_account_and_folder(self) -> dict:
        """Fail closed on a wrong account, root, shared, trashed, or foreign folder."""
        self._verified = False
        about = self._json(self._request(
            "GET", f"{DRIVE_API}/about", params={"fields": "user(emailAddress)"},
        ))
        user = about.get("user")
        if not isinstance(user, dict) or str(user.get("emailAddress", "")).casefold() != self.account_email:
            raise ChartDriveError("Authenticated Drive account does not match the expected account.")
        root = self._json(self._request(
            "GET", f"{DRIVE_API}/files/root", params={"fields": "id"},
        ))
        if not root.get("id") or root["id"] == self.folder_id:
            raise ChartDriveError("My Drive root is not an allowed storage target.")
        folder, _ = self._metadata(self.folder_id)
        if (folder.get("mimeType") != FOLDER_MIME
                or folder.get("trashed") is not False or not self._owned(folder)):
            raise ChartDriveError("Chart folder must be an untrashed, account-owned My Drive folder.")
        self._verified = True
        return {"folder_id": self.folder_id, "account_email": self.account_email}

    def _ensure_verified(self) -> None:
        if not self._verified:
            self.verify_account_and_folder()

    def _managed(self, metadata: dict) -> bool:
        properties = metadata.get("appProperties")
        mime_type = metadata.get("mimeType")
        return (
            isinstance(metadata.get("id"), str)
            and metadata["id"] != self.folder_id
            and metadata.get("parents") == [self.folder_id]
            and metadata.get("trashed") is False
            and self._owned(metadata)
            and isinstance(mime_type, str) and bool(mime_type)
            and not mime_type.startswith("application/vnd.google-apps.")
            and isinstance(properties, dict)
            and properties.get("namespace") == NAMESPACE
        )

    def _require_managed(self, metadata: dict) -> None:
        if not self._managed(metadata):
            raise ChartDriveError("File is not managed directly inside the configured chart folder.")

    def _list(self, query: str) -> list[dict]:
        files = []
        token = None
        seen = set()
        while True:
            params = {"q": query, "spaces": "drive", "pageSize": 1000,
                      "fields": f"nextPageToken,incompleteSearch,files({FILE_FIELDS})"}
            if token:
                params["pageToken"] = token
            payload = self._json(self._request("GET", f"{DRIVE_API}/files", params=params))
            page = payload.get("files")
            if payload.get("incompleteSearch") or not isinstance(page, list):
                raise ChartDriveError("Google Drive inventory was incomplete.")
            if not all(isinstance(item, dict) for item in page):
                raise ChartDriveError("Google Drive returned invalid inventory entries.")
            files.extend(page)
            token = payload.get("nextPageToken")
            if not token:
                return files
            if not isinstance(token, str) or token in seen:
                raise ChartDriveError("Google Drive inventory pagination failed.")
            seen.add(token)

    def _base_query(self) -> str:
        return (
            f"'{_query_literal(self.folder_id)}' in parents and trashed = false and "
            f"appProperties has {{ key='namespace' and value='{NAMESPACE}' }}"
        )

    def inventory(self) -> list[dict]:
        """Return raw metadata for owned, tagged files directly under this folder."""
        self._ensure_verified()
        return [item for item in self._list(self._base_query()) if self._managed(item)]

    @staticmethod
    def _validate_key(key: str) -> None:
        match = KEY_PATTERN.fullmatch(key) if isinstance(key, str) else None
        if not match or int(match[2]) > 240:
            raise ChartDriveError("Invalid public chart key.")
        try:
            datetime.strptime(match[1], "%Y%m%d%H")
        except ValueError:
            raise ChartDriveError("Invalid public chart cycle.") from None

    @staticmethod
    def _hash_stream(handle: BinaryIO) -> tuple[int, str, str]:
        md5 = hashlib.md5(usedforsecurity=False)
        sha256 = hashlib.sha256()
        size = 0
        while chunk := handle.read(1024 * 1024):
            md5.update(chunk)
            sha256.update(chunk)
            size += len(chunk)
        handle.seek(0)
        return size, md5.hexdigest(), sha256.hexdigest()

    @staticmethod
    def _matches(metadata: dict, size: int, md5: str) -> bool:
        return (str(metadata.get("size", "")) == str(size)
                and str(metadata.get("md5Checksum", "")).lower() == md5)

    def _verify_content(self, metadata: dict, size: int, md5: str, key: str) -> None:
        self._require_managed(metadata)
        if metadata["appProperties"].get("key") != key or not self._matches(metadata, size, md5):
            raise ChartDriveError("Google Drive content integrity verification failed.")

    def _permissions(self, file_id: str) -> list[dict]:
        result = []
        token = None
        seen = set()
        while True:
            params = {"fields": "nextPageToken,permissions(id,type,role,deleted)", "pageSize": 100}
            if token:
                params["pageToken"] = token
            payload = self._json(self._request(
                "GET", f"{DRIVE_API}/files/{quote(_file_id(file_id), safe='')}/permissions",
                params=params,
            ))
            page = payload.get("permissions")
            if not isinstance(page, list) or not all(isinstance(item, dict) for item in page):
                raise ChartDriveError("Google Drive returned invalid permissions.")
            result.extend(page)
            token = payload.get("nextPageToken")
            if not token:
                return result
            if not isinstance(token, str) or token in seen:
                raise ChartDriveError("Google Drive permission pagination failed.")
            seen.add(token)

    @staticmethod
    def _has_public_reader(permissions: list[dict]) -> bool:
        public = [item for item in permissions if item.get("type") == "anyone" and not item.get("deleted")]
        if any(item.get("role") != "reader" for item in public):
            raise ChartDriveError("Chart file has an unexpected public permission role.")
        return bool(public)

    def _ensure_public_reader(self, file_id: str) -> None:
        if self._has_public_reader(self._permissions(file_id)):
            return
        self._request(
            "POST", f"{DRIVE_API}/files/{quote(file_id, safe='')}/permissions",
            params={"fields": "id"},
            json={"type": "anyone", "role": "reader", "allowFileDiscovery": False},
        )
        if not self._has_public_reader(self._permissions(file_id)):
            raise ChartDriveError("Google Drive public reader verification failed.")

    def _upload_image(self, handle: BinaryIO, key: str, suffix: str,
                      size: int, sha256: str) -> str:
        response = self._request(
            "POST", f"{DRIVE_UPLOAD_API}/files",
            params={"uploadType": "resumable", "fields": "id"},
            headers={"Content-Type": "application/json; charset=UTF-8",
                     "X-Upload-Content-Type": IMAGE_TYPES[suffix],
                     "X-Upload-Content-Length": str(size)},
            json={"name": key.replace("/", "_") + "_" + sha256[:16] + suffix,
                  "parents": [self.folder_id], "mimeType": IMAGE_TYPES[suffix],
                  "appProperties": {"namespace": NAMESPACE, "kind": "image",
                                    "key": key, "sha256": sha256}},
        )
        location = response.headers.get("Location", "")
        try:
            target = urlsplit(location)
            valid = (target.scheme == "https" and target.hostname == "www.googleapis.com"
                     and target.port in (None, 443) and not target.username
                     and not target.password and not target.fragment
                     and target.path == "/upload/drive/v3/files")
        except ValueError:
            valid = False
        if not valid:
            raise ChartDriveError("Google Drive returned an invalid upload destination.")
        uploaded = self._json(self._request(
            "PUT", location, data=handle,
            headers={"Content-Type": IMAGE_TYPES[suffix], "Content-Length": str(size)},
        ))
        return _file_id(uploaded.get("id"))

    def upload_image(self, path: str | Path, key: str) -> dict:
        """Reuse matching MD5+size; changed bytes create a new immutable file ID."""
        self._validate_key(key)
        try:
            local_path = Path(path)
            suffix = local_path.suffix.lower()
            if suffix not in IMAGE_TYPES:
                raise ChartDriveError("Unsupported chart image type.")
            handle = local_path.open("rb")
        except (OSError, TypeError, ValueError):
            raise ChartDriveError("Chart image could not be opened.") from None
        with handle:
            try:
                size, md5, sha256 = self._hash_stream(handle)
            except OSError:
                raise ChartDriveError("Chart image could not be read.") from None
            if not size:
                raise ChartDriveError("Chart image must not be empty.")
            self._ensure_verified()
            query = self._base_query() + (
                f" and appProperties has {{ key='key' and value='{_query_literal(key)}' }}"
            )
            candidates = self._list(query)
            file_id = None
            for candidate in sorted(candidates, key=lambda item: str(item.get("id", ""))):
                if (not self._managed(candidate) or candidate["appProperties"].get("key") != key
                        or candidate.get("mimeType") != IMAGE_TYPES[suffix]
                        or not self._matches(candidate, size, md5)):
                    continue
                current, _ = self._metadata(_file_id(candidate["id"]))
                self._require_managed(current)
                if (current.get("mimeType") == IMAGE_TYPES[suffix]
                        and current["appProperties"].get("key") == key
                        and self._matches(current, size, md5)):
                    file_id = current["id"]
                    break
            if file_id is None:
                file_id = self._upload_image(handle, key, suffix, size, sha256)
                current, _ = self._metadata(file_id)
                self._verify_content(current, size, md5, key)
                if current.get("mimeType") != IMAGE_TYPES[suffix]:
                    raise ChartDriveError("Google Drive returned an unexpected image type.")
            self._ensure_public_reader(file_id)
            return {"file_id": file_id, "url": drive_url(file_id), "size": size,
                    "md5": md5, "sha256": sha256, "key": key}

    @staticmethod
    def _json_name(name: str) -> None:
        if not isinstance(name, str) or name not in JSON_NAMES:
            raise ChartDriveError("Only state.json and manifest.json are managed JSON names.")

    def _json_entry(self, name: str) -> dict | None:
        self._ensure_verified()
        query = self._base_query() + f" and name = '{_query_literal(name)}'"
        entries = [item for item in self._list(query)
                   if self._managed(item) and item.get("name") == name]
        if len(entries) > 1:
            raise ChartDriveError("Duplicate managed JSON entries require reconciliation.")
        if not entries:
            return None
        self._require_json_entry(entries[0], name)
        return entries[0]

    def _require_json_entry(self, entry: dict, name: str) -> None:
        self._require_managed(entry)
        if (entry.get("name") != name or entry.get("mimeType") != "application/json"
                or entry["appProperties"].get("key") != name
                or entry["appProperties"].get("kind") != "json"):
            raise ChartDriveError("Managed JSON entry has unexpected metadata.")

    def read_json(self, name: str, default: Any = None) -> Any:
        """Return default only when absent, never on an API or integrity error."""
        self._json_name(name)
        entry = self._json_entry(name)
        if entry is None:
            return default
        current, etag = self._metadata(_file_id(entry["id"]))
        self._require_json_entry(current, name)
        response = self._request(
            "GET", f"{DRIVE_API}/files/{quote(current['id'], safe='')}",
            params={"alt": "media"}, headers={"If-Match": etag} if etag else {},
        )
        try:
            data = response.content
            md5 = hashlib.md5(data, usedforsecurity=False).hexdigest()
            self._verify_content(current, len(data), md5, name)
            return json.loads(data.decode("utf-8"))
        except (ValueError, TypeError, UnicodeError):
            raise ChartDriveError("Managed JSON content is invalid.") from None

    def write_json(self, name: str, payload: Any) -> dict:
        """Create/update a private managed JSON blob; reject stale ETag updates."""
        self._json_name(name)
        try:
            data = (json.dumps(payload, ensure_ascii=False, sort_keys=True, allow_nan=False,
                               separators=(",", ":")) + "\n").encode("utf-8")
        except (TypeError, ValueError, UnicodeError):
            raise ChartDriveError("Payload is not valid JSON.") from None
        md5 = hashlib.md5(data, usedforsecurity=False).hexdigest()
        entry = self._json_entry(name)
        metadata = {"name": name, "mimeType": "application/json", "parents": [self.folder_id],
                    "appProperties": {"namespace": NAMESPACE, "key": name, "kind": "json"}}
        method, url, headers = "POST", f"{DRIVE_UPLOAD_API}/files", {}
        if entry is not None:
            current, etag = self._metadata(_file_id(entry["id"]))
            self._require_json_entry(current, name)
            if self._matches(current, len(data), md5):
                return self._json_record(current["id"], name, data, md5)
            if not etag:
                raise ChartDriveError("Managed JSON update requires an ETag precondition.")
            method, url = "PATCH", f"{DRIVE_UPLOAD_API}/files/{quote(current['id'], safe='')}"
            headers["If-Match"] = etag
            metadata = {"mimeType": "application/json"}
        boundary = "chart_" + uuid.uuid4().hex
        body = (
            f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n".encode()
            + json.dumps(metadata).encode("utf-8")
            + f"\r\n--{boundary}\r\nContent-Type: application/json\r\n\r\n".encode()
            + data + f"\r\n--{boundary}--\r\n".encode()
        )
        headers["Content-Type"] = f"multipart/related; boundary={boundary}"
        result = self._json(self._request(
            method, url, params={"uploadType": "multipart", "fields": "id"},
            headers=headers, data=body,
        ))
        file_id = _file_id(result.get("id"))
        if entry is not None and file_id != entry["id"]:
            raise ChartDriveError("Google Drive returned an unexpected JSON file ID.")
        verified, _ = self._metadata(file_id)
        self._require_json_entry(verified, name)
        self._verify_content(verified, len(data), md5, name)
        return self._json_record(file_id, name, data, md5)

    @staticmethod
    def _json_record(file_id: str, name: str, data: bytes, md5: str) -> dict:
        return {"file_id": file_id, "name": name, "size": len(data), "md5": md5,
                "sha256": hashlib.sha256(data).hexdigest()}

    def delete_managed(self, file_id: str) -> None:
        """Permanently delete exactly one freshly verified managed blob ID."""
        clean_id = _file_id(file_id)
        if clean_id == self.folder_id:
            raise ChartDriveError("The chart folder cannot be deleted.")
        self._ensure_verified()
        current, etag = self._metadata(clean_id)
        self._require_managed(current)
        if not etag:
            raise ChartDriveError("Managed deletion requires an ETag precondition.")
        self._request(
            "DELETE", f"{DRIVE_API}/files/{quote(clean_id, safe='')}",
            headers={"If-Match": etag},
        )
