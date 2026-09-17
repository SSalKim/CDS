"""Small, exact-cycle snapshots shared by the collector and VTG renderer."""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from polarwx_browser import request_identity
from vtg_sources import polarwx_keys


DEFAULT_ROOT = Path(__file__).resolve().parent / "data" / "polarwx"
REFRESH_MINUTES = 15
RAW_FIELDS = ("fhr", "lat", "lon", "time", "mslp", "vmax")


def snapshot_path(root: Path, atcf_id: str, cycle: str) -> Path:
    storm, cycle = request_identity(atcf_id, cycle)
    return root / cycle / f"{storm}.json"


def load_snapshot(root: Path, atcf_id: str, cycle: str) -> dict | None:
    storm, cycle = request_identity(atcf_id, cycle)
    try:
        payload = json.loads(snapshot_path(root, storm, cycle).read_text(encoding="utf-8"))
        if (payload.get("schema") == 1 and payload.get("atcf_id") == storm
                and payload.get("cycle") == cycle and isinstance(payload.get("models"), dict)):
            return payload
    except (OSError, ValueError, AttributeError):
        pass
    return None


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=True, separators=(",", ":")) + "\n", encoding="utf-8")
    temporary.replace(path)


def save_snapshot(root: Path, atcf_id: str, cycle: str, text: str, *, now: datetime | None = None) -> Path:
    storm, cycle = request_identity(atcf_id, cycle)
    raw = json.loads(text)
    models = {
        key: {field: raw[key][field] for field in RAW_FIELDS if isinstance(raw[key].get(field), list)}
        for key in polarwx_keys() if isinstance(raw.get(key), dict)
    }
    path = snapshot_path(root, storm, cycle)
    write_json(path, {"schema": 1, "atcf_id": storm, "cycle": cycle,
                      "fetched_at": (now or datetime.now(timezone.utc)).isoformat(), "models": models})
    return path


def snapshot_is_fresh(snapshot: dict | None, now: datetime) -> bool:
    try:
        age = now - datetime.fromisoformat(snapshot["fetched_at"])
        return timedelta(0) <= age < timedelta(minutes=REFRESH_MINUTES)
    except (TypeError, ValueError, KeyError):
        return False


def queue_request(root: Path, atcf_id: str, cycle: str, *, now: datetime | None = None) -> bool:
    destination = os.environ.get("VTG_POLARWX_REQUEST_DIR")
    if not destination:
        return False
    storm, cycle = request_identity(atcf_id, cycle)
    now = now or datetime.now(timezone.utc)
    cycle_time = datetime.strptime(cycle, "%Y%m%d%H").replace(tzinfo=timezone.utc)
    # The public active-storm UI is not an archive/backfill endpoint.
    if not timedelta(0) <= now - cycle_time <= timedelta(hours=48):
        return False
    if snapshot_is_fresh(load_snapshot(root, storm, cycle), now):
        return False
    path = Path(destination) / f"{storm}-{cycle}.json"
    write_json(path, {"atcf_id": storm, "cycle": cycle})
    print(f"Queued POLARWX prefetch: {storm} {cycle}")
    return True
