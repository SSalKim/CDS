from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


VALID_TD_2202_START = "202204090000"
VALID_TD_2202_END_EXCLUSIVE = "202204100000"


def parse_data_time_from_image(path: Path) -> str:
    parts = path.stem.rsplit("_", 2)
    return parts[-2] if len(parts) >= 3 else ""


def parse_data_time_from_metadata(path: Path) -> str:
    return path.name[:12] if len(path.name) >= 12 else ""


def is_invalid_td_2202_time(data_time: str) -> bool:
    return not (VALID_TD_2202_START <= data_time < VALID_TD_2202_END_EXCLUSIVE)


def remove_file(path: Path, *, dry_run: bool, removed: list[Path]) -> None:
    if not path.is_file():
        return
    removed.append(path)
    print(f"{'Would remove' if dry_run else 'Removing'}: {path}")
    if not dry_run:
        path.unlink()


def clean_status(status_path: Path, *, dry_run: bool) -> int:
    if not status_path.exists():
        return 0
    try:
        payload = json.loads(status_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 0

    cycles = payload.get("cycles")
    if not isinstance(cycles, dict):
        return 0

    removed_records = 0
    for data_time in list(cycles):
        records = cycles.get(data_time)
        if not isinstance(records, dict):
            continue
        if not is_invalid_td_2202_time(str(data_time)):
            continue
        for key in list(records):
            if str(key).startswith("td_2022_02"):
                print(
                    f"{'Would remove' if dry_run else 'Removing'} status record: "
                    f"{data_time}/{key}"
                )
                removed_records += 1
                if not dry_run:
                    records.pop(key, None)
        if not dry_run and not records:
            cycles.pop(data_time, None)

    if removed_records and not dry_run:
        status_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return removed_records


def clean_track_history(output_root: Path, *, dry_run: bool) -> tuple[int, int]:
    history_dir = output_root / "metadata" / "track_history" / "2022"
    if not history_dir.exists():
        return 0, 0

    target_aliases = {"td_2022_02", "typ_2022_02"}
    changed_files = 0
    removed_points = 0
    for path in sorted(history_dir.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(payload, dict):
            continue

        aliases = {path.stem, str(payload.get("primary_key") or "").strip()}
        aliases.update(str(item or "").strip() for item in payload.get("aliases", []))
        if not (aliases & target_aliases):
            continue

        points = payload.get("points")
        if not isinstance(points, list):
            continue
        kept = []
        removed_here = 0
        for point in points:
            time_utc = str(point.get("time_utc") or "") if isinstance(point, dict) else ""
            if time_utc and time_utc < VALID_TD_2202_START:
                removed_here += 1
                continue
            kept.append(point)
        if not removed_here:
            continue

        changed_files += 1
        removed_points += removed_here
        print(
            f"{'Would clean' if dry_run else 'Cleaning'} track history: "
            f"{path} ({removed_here} bad point(s))"
        )
        if not dry_run:
            payload["points"] = kept
            path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
    return changed_files, removed_points


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Remove VTG artifacts generated from the erroneous KMA 2022 TD02 "
            "2021 timestamp and rebuild manifests."
        )
    )
    parser.add_argument("--output-root", type=Path, default=Path("VTG_IMG"))
    parser.add_argument("--vtg-auto", type=Path, default=Path(__file__).with_name("vtg_auto.py"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    output_root = args.output_root
    removed: list[Path] = []

    # Bad source dates generated TD_2202 both in 2021 and before the actual
    # 2022-04-09 00 UTC genesis. Keep only the valid pre-MEGI TD cycles.
    for storm_dir in sorted((output_root / "2022").glob("TD_2202_*")):
        for path in sorted(storm_dir.glob("TD_2202_*_*_*h.png")):
            data_time = parse_data_time_from_image(path)
            if data_time and is_invalid_td_2202_time(data_time):
                remove_file(path, dry_run=args.dry_run, removed=removed)

    metadata_dir = output_root / "metadata"
    for path in sorted(metadata_dir.glob("*_td_2022_02_*h.json")):
        data_time = parse_data_time_from_metadata(path)
        if data_time and is_invalid_td_2202_time(data_time):
            remove_file(path, dry_run=args.dry_run, removed=removed)

    status_path = output_root / "vtg_auto_status.json"
    removed_status = clean_status(status_path, dry_run=args.dry_run)
    history_files, history_points = clean_track_history(output_root, dry_run=args.dry_run)

    print(
        f"Repair summary: files={len(removed)}, status_records={removed_status}, "
        f"history_files={history_files}, history_points={history_points}, "
        f"dry_run={args.dry_run}"
    )

    if args.dry_run:
        return 0

    command = [
        sys.executable,
        str(args.vtg_auto),
        "--index-only",
        "--output-root",
        str(output_root),
    ]
    print("Rebuilding VTG manifests:", " ".join(command))
    completed = subprocess.run(command, check=False)
    if completed.returncode != 0:
        print(
            "Artifact cleanup completed, but manifest rebuild failed. "
            "Run vtg_auto.py --index-only manually.",
            file=sys.stderr,
        )
        return completed.returncode

    print("Repair completed. Commit deletions and rebuilt manifest files with git add -A VTG_IMG.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
