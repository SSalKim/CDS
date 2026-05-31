from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parent
KMA_LIST_BASE_URL = "https://apihub-pub.kma.go.kr/api/typ01/url"
TD_LIST_ENDPOINT = "td_lst.php"
TYP_LIST_ENDPOINT = "typ_lst.php"
NOAA_BDECK_URL = "https://www.emc.ncep.noaa.gov/gc_wmb/vxt/DECKS/b{atcf_id}.dat"
ACTIVE_MODEL_TARGET = 33
CYCLE_HOURS = (0, 6, 12, 18)
WINDOW_START_OFFSET_HOURS = 3
WINDOW_END_OFFSET_HOURS = 12


@dataclass(frozen=True)
class CycleWindow:
    data_time: str
    cycle_time_utc: str
    start_utc: str
    end_utc: str


@dataclass(frozen=True)
class StormJob:
    storm_key: str
    stage: str
    year: int
    data_time: str
    td_number: int | None
    typ_number: int
    typ_name: str
    typ_en: str
    atcf_id: str | None
    skip_atcf: bool
    reason: str = ""


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(second=0, microsecond=0)


def parse_utc_stamp(value: str) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return datetime.strptime(text[:12], "%Y%m%d%H%M").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def format_utc_stamp(value: datetime) -> str:
    return value.strftime("%Y%m%d%H%M")


def active_at(now: datetime, start_text: str, end_text: str) -> bool:
    start = parse_utc_stamp(start_text)
    end = parse_utc_stamp(end_text)
    if start and now < start:
        return False
    if end and now > end:
        return False
    return True


def fetch_text(url: str, *, timeout: float = 12) -> str:
    request = Request(url, headers={"User-Agent": "CDS-VTG-Auto/1.0"})
    with urlopen(request, timeout=timeout) as response:
        data = response.read()
    for encoding in ("utf-8", "cp949", "euc-kr"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def kma_list_url(endpoint: str, year: int, auth_key: str) -> str:
    query = urlencode({
        "YY": year,
        "disp": "1",
        "help": "1",
        "authKey": auth_key,
    })
    return f"{KMA_LIST_BASE_URL}/{endpoint}?{query}"


def parse_kma_csv_lines(text: str, *, fixed_columns: int) -> list[list[str]]:
    rows: list[list[str]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parsed = next(csv.reader([line]))
        if parsed and parsed[-1].strip() == "=":
            parsed = parsed[:-1]
        if len(parsed) < fixed_columns:
            continue
        rows.append([value.strip() for value in parsed])
    return rows


def fetch_td_rows(year: int, auth_key: str) -> list[dict]:
    rows = []
    text = fetch_text(kma_list_url(TD_LIST_ENDPOINT, year, auth_key))
    for row in parse_kma_csv_lines(text, fixed_columns=5):
        rows.append({
            "YY": row[0],
            "TD": row[1],
            "TYP": row[2],
            "TM_ST": row[3],
            "TM_ED": row[4],
            "REM": ",".join(row[5:]).strip(),
        })
    return rows


def fetch_typ_rows(year: int, auth_key: str) -> list[dict]:
    rows = []
    text = fetch_text(kma_list_url(TYP_LIST_ENDPOINT, year, auth_key))
    for row in parse_kma_csv_lines(text, fixed_columns=8):
        rows.append({
            "YY": row[0],
            "SEQ": row[1],
            "NOW": row[2],
            "EFF": row[3],
            "TM_ST": row[4],
            "TM_ED": row[5],
            "TYP_NAME": row[6],
            "TYP_EN": row[7],
            "REM": ",".join(row[8:]).strip(),
        })
    return rows


def normalize_name(value: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(value or "").upper())


def candidate_offsets(radius: int) -> list[int]:
    offsets = [0]
    for value in range(1, radius + 1):
        offsets.extend([-value, value])
    return offsets


def find_atcf_id(
    *,
    typ_en: str,
    typ_number: int,
    year: int,
    radius: int,
) -> str | None:
    target_name = normalize_name(typ_en)
    if not target_name:
        return None

    for offset in candidate_offsets(radius):
        candidate_number = typ_number + offset
        if candidate_number < 1 or candidate_number > 99:
            continue
        atcf_id = f"wp{candidate_number:02d}{year}"
        try:
            text = fetch_text(NOAA_BDECK_URL.format(atcf_id=atcf_id), timeout=10)
        except (HTTPError, URLError, TimeoutError):
            continue
        if target_name in normalize_name(text):
            return atcf_id
    return None


def active_cycle_windows(now: datetime) -> list[CycleWindow]:
    windows = []
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    for day_offset in (-1, 0, 1):
        base_day = midnight + timedelta(days=day_offset)
        for hour in CYCLE_HOURS:
            cycle = base_day + timedelta(hours=hour)
            start = cycle + timedelta(hours=WINDOW_START_OFFSET_HOURS)
            end = cycle + timedelta(hours=WINDOW_END_OFFSET_HOURS)
            if start <= now < end:
                windows.append(CycleWindow(
                    data_time=format_utc_stamp(cycle),
                    cycle_time_utc=format_utc_stamp(cycle),
                    start_utc=format_utc_stamp(start),
                    end_utc=format_utc_stamp(end),
                ))
    return sorted(windows, key=lambda item: item.data_time)


def load_json(path: Path, fallback):
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return fallback


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def load_manual_map(path: Path | None) -> dict:
    if not path:
        return {}
    return load_json(path, {})


def manual_atcf_id(manual_map: dict, *, year: int, td_number: int | None, typ_number: int, typ_en: str) -> str | None:
    keys = [
        f"{year}:TYP{typ_number:02d}",
        f"TYP{typ_number:02d}",
        normalize_name(typ_en),
    ]
    if td_number is not None:
        keys.extend([
            f"{year}:TD{td_number:02d}",
            f"TD{td_number:02d}",
        ])
    for key in keys:
        value = manual_map.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip().lower()
    return None


def build_storm_jobs(
    *,
    now: datetime,
    data_time: str,
    td_rows: list[dict],
    typ_rows: list[dict],
    manual_map: dict,
    atcf_search_radius: int,
) -> list[StormJob]:
    jobs: list[StormJob] = []
    data_dt = parse_utc_stamp(data_time)
    if not data_dt:
        return jobs

    active_typhoons = []
    for row in typ_rows:
        try:
            typ_number = int(row["SEQ"])
            year = int(row["YY"])
        except (TypeError, ValueError):
            continue
        is_active = row.get("NOW") == "1" or active_at(now, row.get("TM_ST", ""), row.get("TM_ED", ""))
        if not is_active:
            continue
        if parse_utc_stamp(row.get("TM_ST", "")) and data_dt < parse_utc_stamp(row.get("TM_ST", "")):
            continue
        typ_en = row.get("TYP_EN", "").strip().upper()
        manual_id = manual_atcf_id(
            manual_map,
            year=year,
            td_number=None,
            typ_number=typ_number,
            typ_en=typ_en,
        )
        atcf_id = manual_id or find_atcf_id(
            typ_en=typ_en,
            typ_number=typ_number,
            year=year,
            radius=atcf_search_radius,
        )
        active_typhoons.append(typ_number)
        jobs.append(StormJob(
            storm_key=f"typ_{year}_{typ_number:02d}",
            stage="TYP_LINKED" if atcf_id else "TYP_LINKED_ATCF_PENDING",
            year=year,
            data_time=data_time,
            td_number=None,
            typ_number=typ_number,
            typ_name=typ_en or row.get("TYP_NAME", "").strip() or "NAMELESS",
            typ_en=typ_en,
            atcf_id=atcf_id,
            skip_atcf=not bool(atcf_id),
            reason="" if atcf_id else "ATCF name match not found; generating KMA-only guidance.",
        ))

    active_typhoon_set = set(active_typhoons)
    for row in td_rows:
        try:
            td_number = int(row["TD"])
            typ_number = int(row["TYP"])
            year = int(row["YY"])
        except (TypeError, ValueError):
            continue
        if not active_at(now, row.get("TM_ST", ""), row.get("TM_ED", "")):
            continue
        if typ_number in active_typhoon_set:
            continue
        if typ_number != 0:
            continue
        manual_id = manual_atcf_id(
            manual_map,
            year=year,
            td_number=td_number,
            typ_number=td_number,
            typ_en="",
        )
        jobs.append(StormJob(
            storm_key=f"td_{year}_{td_number:02d}",
            stage="TD_MANUAL_ATCF" if manual_id else "TD_UNLINKED",
            year=year,
            data_time=data_time,
            td_number=td_number,
            typ_number=td_number,
            typ_name="NAMELESS",
            typ_en="",
            atcf_id=manual_id,
            skip_atcf=not bool(manual_id),
            reason="" if manual_id else "TD has no linked typhoon number yet.",
        ))

    return jobs


def metadata_path_for(output_root: Path, job: StormJob) -> Path:
    return output_root / "metadata" / f"{job.data_time}_{job.storm_key}.json"


def redacted_command(command: list[str]) -> list[str]:
    redacted = command.copy()
    for index, value in enumerate(redacted[:-1]):
        if value == "--auth-key":
            redacted[index + 1] = "***"
    return redacted


def run_vtg(
    *,
    job: StormJob,
    output_root: Path,
    auth_key: str,
    python: str,
    dry_run: bool,
) -> dict:
    metadata_path = metadata_path_for(output_root, job)
    command = [
        python,
        str(PROJECT_ROOT / "VTG.py"),
        "--typ-number",
        str(job.typ_number),
        "--typ-name",
        job.typ_name,
        "--storm-stage",
        "TD" if job.stage.startswith("TD_") else "TYP",
        "--data-time",
        job.data_time,
        "--fcst-hours",
        "120",
        "--output-root",
        str(output_root),
        "--metadata-path",
        str(metadata_path),
        "--auth-key",
        auth_key,
        "--overwrite",
        "--no-show",
    ]
    if job.atcf_id:
        command.extend(["--atcf-id", job.atcf_id])
    if job.skip_atcf:
        command.append("--skip-atcf")

    if dry_run:
        return {
            "status": "dry_run",
            "command": redacted_command(command),
            "metadata_path": str(metadata_path),
        }

    # Prevent a failed/stale run from reusing metadata written by an older run.
    try:
        metadata_path.unlink()
    except FileNotFoundError:
        pass

    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    result = {
        "status": "ok" if completed.returncode == 0 else "failed",
        "returncode": completed.returncode,
        "stdout": completed.stdout[-4000:],
        "stderr": completed.stderr[-4000:],
        "metadata_path": str(metadata_path),
    }

    # Only trust newly generated metadata when VTG.py completed successfully.
    if completed.returncode == 0:
        metadata = load_json(metadata_path, None)
        if metadata:
            result["metadata"] = metadata
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run scheduled VTG image generation.")
    parser.add_argument("--now", help="Override current UTC time, YYYYmmddHHMM.")
    parser.add_argument("--output-root", type=Path, default=PROJECT_ROOT / "VTG_IMG")
    parser.add_argument("--auth-key", default=os.getenv("KMA_APIHUB_AUTH_KEY", ""))
    parser.add_argument("--manual-map", type=Path, default=PROJECT_ROOT / "vtg_manual_atcf_map.json")
    parser.add_argument("--status-path", type=Path, default=None)
    parser.add_argument("--manifest-path", type=Path, default=None)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--complete-model-count", type=int, default=ACTIVE_MODEL_TARGET)
    parser.add_argument("--atcf-search-radius", type=int, default=3)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.now:
        now = parse_utc_stamp(args.now)
        if now is None:
            raise SystemExit("--now must be YYYYmmddHHMM")
    else:
        now = utc_now()

    output_root = args.output_root
    status_path = args.status_path or output_root / "vtg_auto_status.json"
    manifest_path = args.manifest_path or output_root / "manifest.json"
    windows = active_cycle_windows(now)
    status = load_json(status_path, {"cycles": {}})
    manual_map = load_manual_map(args.manual_map)

    if not args.auth_key:
        raise SystemExit("KMA_APIHUB_AUTH_KEY is required.")

    years = {now.year}
    for window in windows:
        year = int(window.data_time[:4])
        years.add(year)

    td_rows: list[dict] = []
    typ_rows: list[dict] = []
    for year in sorted(years):
        td_rows.extend(fetch_td_rows(year, args.auth_key))
        typ_rows.extend(fetch_typ_rows(year, args.auth_key))

    run_entries = []
    actual_run_count = 0
    for window in windows:
        cycle_status = status.setdefault("cycles", {}).setdefault(window.data_time, {})
        jobs = build_storm_jobs(
            now=now,
            data_time=window.data_time,
            td_rows=td_rows,
            typ_rows=typ_rows,
            manual_map=manual_map,
            atcf_search_radius=args.atcf_search_radius,
        )
        for job in jobs:
            # Active cycle windows are intentionally retried on every scheduled run.
            # Do not skip a cycle just because it reached the previous complete-model target;
            # late-arriving ATCF/model data can still improve the output.
            actual_run_count += 1
            result = run_vtg(
                job=job,
                output_root=output_root,
                auth_key=args.auth_key,
                python=args.python,
                dry_run=args.dry_run,
            )
            metadata = result.get("metadata") or {}
            model_count = int(metadata.get("model_count") or 0)
            target_count = int(metadata.get("target_model_count") or args.complete_model_count or 0)
            completed = (
                result.get("status") == "ok"
                and target_count > 0
                and model_count >= target_count
            )
            cycle_status[job.storm_key] = {
                "updated_at_utc": format_utc_stamp(now),
                "completed": completed,
                "metadata": metadata,
                "last_status": result.get("status"),
                "reason": job.reason,
            }
            run_entries.append({
                "job": asdict(job),
                "window": asdict(window),
                "result": result,
                "completed": completed,
            })

    previous_manifest = load_json(manifest_path, {})
    manifest = {
        "updated_at_utc": format_utc_stamp(now),
        "window_start_offset_hours": WINDOW_START_OFFSET_HOURS,
        "window_end_offset_hours": WINDOW_END_OFFSET_HOURS,
        "complete_model_count": args.complete_model_count,
        "active_windows": [asdict(window) for window in windows],
        "runs": run_entries,
    }
    should_clear_previous_manifest = not run_entries and bool(previous_manifest.get("runs"))
    should_write_outputs = not args.dry_run and (actual_run_count > 0 or should_clear_previous_manifest)
    if should_write_outputs:
        write_json(manifest_path, manifest)
        write_json(status_path, status)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
