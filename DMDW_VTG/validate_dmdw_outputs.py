from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SECRET_MARKERS = (
    "AFS2O_SESSION",
    "SCOUTER=",
    "JSESSIONID",
    "DMDW_ID",
    "DMDW_PW",
    "Cookie:",
    "Set-Cookie",
)


@dataclass
class ValidationStats:
    files: int = 0
    models: int = 0
    models_with_points: int = 0
    points: int = 0
    issues: int = 0
    warnings: int = 0


def parse_stamp(value: str) -> datetime | None:
    text = str(value or "").strip()
    if not re.fullmatch(r"\d{12}", text):
        return None
    try:
        return datetime.strptime(text, "%Y%m%d%H%M").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def iter_strings(obj: Any):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for value in obj.values():
            yield from iter_strings(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from iter_strings(value)


def has_secret_marker(payload: Any) -> str:
    for text in iter_strings(payload):
        for marker in SECRET_MARKERS:
            if marker in text:
                return marker
    return ""


def issue(stats: ValidationStats, path: Path, message: str) -> None:
    stats.issues += 1
    print(f"ERROR {path}: {message}", file=sys.stderr)


def warn(stats: ValidationStats, path: Path, message: str) -> None:
    stats.warnings += 1
    print(f"WARN  {path}: {message}")


def validate_point(path: Path, stats: ValidationStats, cycle_dt: datetime, point: dict[str, Any]) -> None:
    stats.points += 1
    valid_time = str(point.get("valid_time") or "")
    valid_dt = parse_stamp(valid_time)
    if valid_dt is None:
        issue(stats, path, f"invalid valid_time={valid_time!r}")
        return

    lead = point.get("lead_hour")
    if isinstance(lead, (int, float)) and lead < 0:
        issue(stats, path, f"negative lead_hour valid_time={valid_time} lead={lead}")
    expected_lead = int(round((valid_dt - cycle_dt).total_seconds() / 3600.0))
    if lead != expected_lead:
        issue(stats, path, f"lead_hour mismatch valid_time={valid_time} lead={lead} expected={expected_lead}")

    lat = point.get("lat")
    lon = point.get("lon")
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
        issue(stats, path, f"missing numeric lat/lon valid_time={valid_time}")
    elif not (-90.0 <= float(lat) <= 90.0 and 0.0 <= float(lon) <= 360.0):
        issue(stats, path, f"out-of-range lat/lon valid_time={valid_time} lat={lat} lon={lon}")


def validate_schema_v1(path: Path, stats: ValidationStats, cycle_dt: datetime, payload: dict[str, Any]) -> None:
    models = payload.get("models")
    if not isinstance(models, list):
        issue(stats, path, "models must be a list")
        return
    if not models:
        warn(stats, path, "no DMDW models in file")

    for model in models:
        if not isinstance(model, dict):
            issue(stats, path, "model entry is not an object")
            continue
        stats.models += 1
        points = model.get("points")
        if not isinstance(points, list):
            issue(stats, path, f"points must be a list for raw_model_id={model.get('raw_model_id')}")
            continue
        if points:
            stats.models_with_points += 1
        for point in points:
            if not isinstance(point, dict):
                issue(stats, path, f"point entry is not an object for raw_model_id={model.get('raw_model_id')}")
                continue
            validate_point(path, stats, cycle_dt, point)


def validate_schema_v2(path: Path, stats: ValidationStats, cycle_dt: datetime, payload: dict[str, Any]) -> None:
    models = payload.get("models")
    if not isinstance(models, list):
        issue(stats, path, "models must be a list")
        return
    stats.models += len(models)
    stats.models_with_points += sum(
        1 for model in models
        if isinstance(model, dict) and int(model.get("point_count") or 0) > 0
    )

    point_columns = payload.get("point_columns")
    points = payload.get("points")
    if not isinstance(point_columns, list) or not all(isinstance(col, str) for col in point_columns):
        issue(stats, path, "point_columns must be a string list")
        return
    if not isinstance(points, list):
        issue(stats, path, "points must be a list")
        return
    if not points:
        warn(stats, path, "no DMDW forecast points in file")

    column_index = {column: idx for idx, column in enumerate(point_columns)}
    required = {"model_index", "lead_hour", "valid_time", "lat", "lon"}
    missing = sorted(required - set(column_index))
    if missing:
        issue(stats, path, f"missing point_columns={','.join(missing)}")
        return

    for row in points:
        if not isinstance(row, list):
            issue(stats, path, "compact point row is not a list")
            continue
        if len(row) < len(point_columns):
            issue(stats, path, f"compact point row has {len(row)} values for {len(point_columns)} columns")
            continue

        model_index = row[column_index["model_index"]]
        if not isinstance(model_index, int) or not (0 <= model_index < len(models)):
            issue(stats, path, f"invalid model_index={model_index!r}")
            continue

        validate_point(
            path,
            stats,
            cycle_dt,
            {
                "lead_hour": row[column_index["lead_hour"]],
                "valid_time": row[column_index["valid_time"]],
                "lat": row[column_index["lat"]],
                "lon": row[column_index["lon"]],
            },
        )


def validate_file(path: Path, stats: ValidationStats) -> None:
    stats.files += 1
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        issue(stats, path, f"failed to parse JSON: {exc}")
        return

    marker = has_secret_marker(payload)
    if marker:
        issue(stats, path, f"secret/session marker found: {marker}")

    schema_version = payload.get("schema_version")
    if schema_version not in {1, 2}:
        issue(stats, path, "schema_version must be 1 or 2")
    if payload.get("source") != "DMDW":
        issue(stats, path, "source must be DMDW")

    cycle_utc = str(payload.get("cycle_utc") or "")
    cycle_dt = parse_stamp(cycle_utc)
    if cycle_dt is None:
        issue(stats, path, f"invalid cycle_utc={cycle_utc!r}")
        return

    if schema_version == 1:
        validate_schema_v1(path, stats, cycle_dt, payload)
    else:
        validate_schema_v2(path, stats, cycle_dt, payload)


def candidate_files(root: Path, cycle: str | None) -> list[Path]:
    if cycle:
        text = str(cycle).strip()
        if not re.fullmatch(r"\d{10}", text):
            raise SystemExit("--cycle must be YYYYmmddHH.")
        return sorted(root.glob(f"*/{text}/*.json"))
    return sorted(path for path in root.glob("*/*/*.json") if path.name != "index.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate sanitized DMDW VTG source JSON files.")
    parser.add_argument("--root", type=Path, default=Path("data/dmdw"))
    parser.add_argument("--cycle", default="")
    parser.add_argument("--require-files", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    files = candidate_files(args.root, args.cycle or None)
    if not files:
        message = f"No DMDW JSON files found under {args.root}"
        if args.require_files:
            print(f"ERROR {message}", file=sys.stderr)
            return 1
        print(message)
        return 0

    stats = ValidationStats()
    for path in files:
        validate_file(path, stats)

    print(
        "DMDW validation summary: "
        f"files={stats.files} "
        f"models={stats.models} "
        f"models_with_points={stats.models_with_points} "
        f"points={stats.points} "
        f"warnings={stats.warnings} "
        f"errors={stats.issues}"
    )
    return 1 if stats.issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
