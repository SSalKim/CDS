from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "data"
ARCHIVE_MANIFEST_NAME = "drive_archive.json"
ARCHIVE_STATUS_PATH = Path("metadata") / "archive_status.json"
STORM_KEY_RE = re.compile(r"^(typ|td)_(\d{4})_(\d{2})$", re.IGNORECASE)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def format_utc_stamp(value: datetime | None = None) -> str:
    return (value or utc_now()).strftime("%Y%m%d%H%M%S")


def parse_utc_stamp(value: Any) -> datetime | None:
    raw = str(value or "").strip()
    if len(raw) < 10 or not raw[:10].isdigit():
        return None
    try:
        return datetime(
            int(raw[0:4]),
            int(raw[4:6]),
            int(raw[6:8]),
            int(raw[8:10]),
            int(raw[10:12] or "0"),
            tzinfo=timezone.utc,
        )
    except ValueError:
        return None


def load_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return fallback


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def relative_asset_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def append_changed_paths(path: Path | None, changed_paths: set[str]) -> None:
    if path is None:
        return
    existing: set[str] = set()
    if path.exists():
        existing = {line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}
    merged = sorted(existing | {item for item in changed_paths if item})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(merged) + ("\n" if merged else ""), encoding="utf-8")


def write_targets(path: Path | None, targets: list[str]) -> None:
    if path is None:
        return
    unique = sorted({target for target in targets if target})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(unique) + ("\n" if unique else ""), encoding="utf-8")


def read_targets(path: Path | None) -> list[str]:
    if path is None or not path.exists():
        return []
    return sorted({line.strip().lower() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()})


def storm_key_from_system_dir(system_dir: Path) -> str:
    manifest = load_json(system_dir / "manifest.json", {})
    key = str(manifest.get("storm_key") or "").strip().lower() if isinstance(manifest, dict) else ""
    if STORM_KEY_RE.fullmatch(key):
        return key

    match = re.match(r"^(TYP|TD)_(\d{2})(\d{2})_", system_dir.name, re.IGNORECASE)
    year = system_dir.parent.name
    if not match or not year.isdigit():
        return ""
    return f"{match.group(1).lower()}_{year}_{int(match.group(3)):02d}"


def system_dirs_by_storm_key(output_root: Path) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for system_dir in sorted(output_root.glob("[0-9][0-9][0-9][0-9]/*")):
        if not system_dir.is_dir():
            continue
        key = storm_key_from_system_dir(system_dir)
        if key:
            result[key] = system_dir
    return result


def local_images(system_dir: Path) -> list[Path]:
    return sorted(path for path in (system_dir / "images").glob("*.png") if path.is_file())


def archived_image_paths(payload: dict) -> set[str]:
    images = payload.get("images") if isinstance(payload, dict) else None
    if not isinstance(images, dict):
        return set()
    return {
        str(path).replace("\\", "/").strip()
        for path, record in images.items()
        if isinstance(record, dict) and str(record.get("file_id") or "").strip()
    }


def all_local_images_are_archived(system_dir: Path, payload: dict) -> bool:
    images = local_images(system_dir)
    if not images:
        return True
    archived = archived_image_paths(payload)
    return all(relative_asset_path(path) in archived for path in images)


def load_kma_rows(cache_dir: Path, endpoint: str) -> list[dict]:
    rows: list[dict] = []
    for path in sorted(cache_dir.glob(f"{endpoint}_[0-9][0-9][0-9][0-9].json")):
        payload = load_json(path, {})
        cached_rows = payload.get("rows") if isinstance(payload, dict) else None
        if isinstance(cached_rows, list):
            rows.extend(row for row in cached_rows if isinstance(row, dict))
    return rows


def official_ended_systems(cache_dir: Path, now: datetime) -> dict[str, dict]:
    ended: dict[str, dict] = {}
    td_rows = load_kma_rows(cache_dir, "td_lst")
    active_linked_typhoons: set[tuple[int, int]] = set()
    for row in td_rows:
        try:
            year = int(row.get("YY"))
            linked_typ_number = int(row.get("TYP") or 0)
        except (TypeError, ValueError):
            continue
        start_time = parse_utc_stamp(row.get("TM_ST"))
        end_time = parse_utc_stamp(row.get("TM_ED"))
        if (
            linked_typ_number > 0
            and (start_time is None or start_time <= now)
            and (end_time is None or now < end_time)
        ):
            active_linked_typhoons.add((year, linked_typ_number))

    for row in load_kma_rows(cache_dir, "typ_lst"):
        try:
            year = int(row.get("YY"))
            number = int(row.get("SEQ"))
        except (TypeError, ValueError):
            continue
        end_time = parse_utc_stamp(row.get("TM_ED"))
        if (
            str(row.get("NOW") or "").strip() != "2"
            or end_time is None
            or end_time > now
            or (year, number) in active_linked_typhoons
        ):
            continue
        ended[f"typ_{year}_{number:02d}"] = {
            "source": "KMA typ_lst",
            "official_status": "ended",
            "official_end_utc": format_utc_stamp(end_time),
        }

    for row in td_rows:
        try:
            year = int(row.get("YY"))
            number = int(row.get("TD"))
            linked_typ_number = int(row.get("TYP") or 0)
        except (TypeError, ValueError):
            continue
        end_time = parse_utc_stamp(row.get("TM_ED"))
        if linked_typ_number > 0 or end_time is None or end_time > now:
            continue
        ended[f"td_{year}_{number:02d}"] = {
            "source": "KMA td_lst",
            "official_status": "ended",
            "official_end_utc": format_utc_stamp(end_time),
        }
    return ended


def archive_payload(system_dir: Path) -> dict:
    payload = load_json(system_dir / ARCHIVE_MANIFEST_NAME, {})
    return payload if isinstance(payload, dict) else {}


def archive_state(system_dir: Path) -> dict:
    payload = load_json(system_dir / ARCHIVE_STATUS_PATH, {})
    return payload if isinstance(payload, dict) else {}


def save_archive_state(system_dir: Path, state: dict, changed_paths: set[str]) -> None:
    path = system_dir / ARCHIVE_STATUS_PATH
    updated = dict(state)
    updated["version"] = max(1, int(updated.get("version") or 1))
    updated["updated_at_utc"] = format_utc_stamp()
    write_json(path, updated)
    changed_paths.add(relative_asset_path(path))


def pending_state(storm_key: str, official: dict, previous: dict | None = None) -> dict:
    now_stamp = format_utc_stamp()
    result = dict(previous or {})
    result.update({
        "state": "pending",
        "storm_key": storm_key,
        "official_status": "ended",
        "official_source": official.get("source"),
        "official_end_utc": official.get("official_end_utc"),
        "updated_at_utc": now_stamp,
    })
    result.setdefault("detected_at_utc", now_stamp)
    result.setdefault("dispatch_attempts", 0)
    result.pop("failure_reason", None)
    return result


def command_scan(args: argparse.Namespace) -> int:
    now = parse_utc_stamp(args.now) if args.now else utc_now()
    if now is None:
        raise SystemExit("--now must be a UTC timestamp such as YYYYmmddHHMM.")
    ended = official_ended_systems(args.kma_cache_dir, now)
    systems = system_dirs_by_storm_key(args.output_root)
    changed_paths: set[str] = set()
    targets: list[str] = []
    stale_before = now - timedelta(hours=max(1.0, args.stale_dispatch_hours))

    for storm_key, system_dir in sorted(systems.items()):
        if storm_key not in ended or not local_images(system_dir):
            continue
        payload = archive_payload(system_dir)
        state = archive_state(system_dir)
        current_state = str(state.get("state") or "").strip().lower()

        if all_local_images_are_archived(system_dir, payload):
            if current_state != "completed":
                completed = dict(state)
                completed.update({
                    "state": "completed",
                    "storm_key": storm_key,
                    "official_status": "ended",
                    "official_source": ended[storm_key].get("source"),
                    "official_end_utc": ended[storm_key].get("official_end_utc"),
                    "completed_at_utc": format_utc_stamp(now),
                    "updated_at_utc": format_utc_stamp(now),
                })
                save_archive_state(system_dir, completed, changed_paths)
            continue

        if current_state in {"completed", "failed"}:
            continue
        if current_state == "dispatching":
            dispatched_at = parse_utc_stamp(state.get("dispatched_at_utc") or state.get("updated_at_utc"))
            if dispatched_at is None or dispatched_at > stale_before:
                continue
            state = pending_state(storm_key, ended[storm_key], state)
            state["recovered_stale_dispatch_at_utc"] = format_utc_stamp(now)
            save_archive_state(system_dir, state, changed_paths)
        elif current_state != "pending":
            state = pending_state(storm_key, ended[storm_key], state)
            save_archive_state(system_dir, state, changed_paths)
        targets.append(storm_key)

    append_changed_paths(args.changed_paths_file, changed_paths)
    write_targets(args.targets_file, targets)
    print(json.dumps({
        "official_ended_count": len(ended),
        "pending_archive_count": len(targets),
        "pending_storm_keys": targets,
        "changed_path_count": len(changed_paths),
    }, ensure_ascii=False, indent=2))
    return 0


def command_claim(args: argparse.Namespace) -> int:
    systems = system_dirs_by_storm_key(args.output_root)
    changed_paths: set[str] = set()
    claimed: list[str] = []
    for storm_key in read_targets(args.targets_file):
        system_dir = systems.get(storm_key)
        if system_dir is None:
            continue
        state = archive_state(system_dir)
        if str(state.get("state") or "").strip().lower() != "pending":
            continue
        now_stamp = format_utc_stamp()
        state.update({
            "state": "dispatching",
            "storm_key": storm_key,
            "dispatched_at_utc": now_stamp,
            "updated_at_utc": now_stamp,
            "dispatch_attempts": int(state.get("dispatch_attempts") or 0) + 1,
        })
        save_archive_state(system_dir, state, changed_paths)
        claimed.append(storm_key)

    append_changed_paths(args.changed_paths_file, changed_paths)
    write_targets(args.claimed_targets_file, claimed)
    print(json.dumps({
        "claimed_count": len(claimed),
        "claimed_storm_keys": claimed,
        "changed_path_count": len(changed_paths),
    }, ensure_ascii=False, indent=2))
    return 0


def command_mark(args: argparse.Namespace) -> int:
    storm_key = str(args.storm_key or "").strip().lower()
    if not STORM_KEY_RE.fullmatch(storm_key):
        raise SystemExit("--storm-key must look like typ_2026_07 or td_2026_11.")
    systems = system_dirs_by_storm_key(args.output_root)
    system_dir = systems.get(storm_key)
    if system_dir is None:
        raise SystemExit(f"Could not find system directory for {storm_key}.")

    state = archive_state(system_dir)
    now_stamp = format_utc_stamp()
    state.update({
        "state": args.state,
        "storm_key": storm_key,
        "updated_at_utc": now_stamp,
    })
    if args.state == "completed":
        state["completed_at_utc"] = now_stamp
        state.pop("failure_reason", None)
    elif args.state == "failed":
        state["failed_at_utc"] = now_stamp
        state["failure_reason"] = str(args.message or "Archive workflow failed.")[:500]
    elif args.state == "pending":
        state.pop("failure_reason", None)

    changed_paths: set[str] = set()
    save_archive_state(system_dir, state, changed_paths)
    append_changed_paths(args.changed_paths_file, changed_paths)
    print(json.dumps({"storm_key": storm_key, "state": args.state}, ensure_ascii=False))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Track one-time automatic VTG Drive archive dispatches.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="Detect officially ended systems that still have local PNGs.")
    scan.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    scan.add_argument("--kma-cache-dir", type=Path, default=None)
    scan.add_argument("--changed-paths-file", type=Path, default=None)
    scan.add_argument("--targets-file", type=Path, default=None)
    scan.add_argument("--now", default="")
    scan.add_argument("--stale-dispatch-hours", type=float, default=24.0)

    claim = subparsers.add_parser("claim", help="Mark pending systems as dispatching before API calls.")
    claim.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    claim.add_argument("--targets-file", type=Path, required=True)
    claim.add_argument("--claimed-targets-file", type=Path, required=True)
    claim.add_argument("--changed-paths-file", type=Path, default=None)

    mark = subparsers.add_parser("mark", help="Record the final state of a system archive workflow.")
    mark.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    mark.add_argument("--storm-key", required=True)
    mark.add_argument("--state", choices=("pending", "completed", "failed"), required=True)
    mark.add_argument("--message", default="")
    mark.add_argument("--changed-paths-file", type=Path, default=None)

    args = parser.parse_args()
    if args.command == "scan" and args.kma_cache_dir is None:
        args.kma_cache_dir = args.output_root / "cache" / "kma_apihub"
    return args


def main() -> int:
    args = parse_args()
    if args.command == "scan":
        return command_scan(args)
    if args.command == "claim":
        return command_claim(args)
    return command_mark(args)


if __name__ == "__main__":
    raise SystemExit(main())
