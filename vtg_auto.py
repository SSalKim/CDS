from __future__ import annotations

import argparse
import csv
import json
import math
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
KMA_GTS_NOW_URL = f"{KMA_LIST_BASE_URL}/typ_gts_now.php"
ACTIVE_MODEL_TARGET = 36
DEFAULT_ATCF_SEARCH_POSITIVE_RADIUS = 10
DEFAULT_ATCF_SEARCH_NEGATIVE_RADIUS = 5
DEFAULT_ATCF_POSITION_MAX_DISTANCE_KM = 600.0
DEFAULT_ATCF_POSITION_MIN_DISTANCE_GAP_KM = 250.0
VALID_FCST_HOURS = (120, 240)
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
    linked_td_number: int | None
    typ_number: int
    typ_name_ko: str
    typ_name: str
    typ_en: str
    atcf_id: str | None
    skip_atcf: bool
    atcf_match_method: str = ""
    reason: str = ""


@dataclass(frozen=True)
class TrackPoint:
    time_utc: str
    lat: float
    lon: float


@dataclass(frozen=True)
class AtcfMatch:
    atcf_id: str
    method: str
    distance_km: float | None = None


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


def kma_gts_now_url(data_time: str, auth_key: str, *, mode: str = "2") -> str:
    query = urlencode({
        "src": "",
        "tm": data_time,
        "mode": mode,
        "disp": "1",
        "help": "0",
        "authKey": auth_key,
    })
    return f"{KMA_GTS_NOW_URL}?{query}"


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


def safe_int(value) -> int | None:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def safe_float(value) -> float | None:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def fetch_kma_reference_point(*, typ_number: int, data_time: str, auth_key: str) -> TrackPoint | None:
    try:
        text = fetch_text(kma_gts_now_url(data_time, auth_key), timeout=12)
    except (HTTPError, URLError, TimeoutError):
        return None

    candidates: list[TrackPoint] = []
    for row in parse_kma_csv_lines(text, fixed_columns=18):
        if safe_int(row[2]) != typ_number:
            continue
        tmd = safe_int(row[4])
        lat = safe_float(row[7])
        lon = safe_float(row[8])
        ft_time = row[6].strip() if len(row) > 6 else ""
        source = row[17].strip().upper() if len(row) > 17 else ""
        if lat is None or lon is None or not ft_time:
            continue
        if ft_time[:10] != data_time[:10]:
            continue
        if tmd == 0 and (not source or source == "KMA"):
            return TrackPoint(time_utc=ft_time, lat=lat, lon=lon)
        if tmd == 0:
            candidates.append(TrackPoint(time_utc=ft_time, lat=lat, lon=lon))
    return candidates[0] if candidates else None


def normalize_name(value: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(value or "").upper())


def candidate_offsets(positive_radius: int, negative_radius: int) -> list[int]:
    offsets = [0]
    for value in range(1, max(positive_radius, negative_radius) + 1):
        if value <= positive_radius:
            offsets.append(value)
        if value <= negative_radius:
            offsets.append(-value)
    return offsets


def candidate_atcf_ids(*, typ_number: int, year: int, positive_radius: int, negative_radius: int) -> list[str]:
    ids: list[str] = []
    seen: set[str] = set()

    def add(candidate_number: int) -> None:
        if candidate_number < 1 or candidate_number > 99:
            return
        atcf_id = f"wp{candidate_number:02d}{year}"
        if atcf_id not in seen:
            seen.add(atcf_id)
            ids.append(atcf_id)

    for offset in candidate_offsets(positive_radius, negative_radius):
        add(typ_number + offset)
    for candidate_number in range(90, 100):
        add(candidate_number)
    return ids


def parse_atcf_coord(value: str) -> float | None:
    text = str(value or "").strip().upper()
    if len(text) < 2:
        return None
    direction = text[-1]
    number = safe_float(text[:-1])
    if number is None:
        return None
    coord = number / 10.0
    if direction in {"S", "W"}:
        return -coord
    if direction in {"N", "E"}:
        return coord
    return None


def bdeck_track_points(text: str, *, reference_time: str) -> list[TrackPoint]:
    points: list[TrackPoint] = []
    target_time = reference_time[:10]
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            row = [item.strip() for item in next(csv.reader([line]))]
        except csv.Error:
            continue
        if len(row) < 8:
            continue
        if row[2] != target_time:
            continue
        if safe_int(row[5]) != 0:
            continue
        lat = parse_atcf_coord(row[6])
        lon = parse_atcf_coord(row[7])
        if lat is None or lon is None:
            continue
        points.append(TrackPoint(time_utc=f"{target_time}00", lat=lat, lon=lon))
    return points


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_km = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlon = math.radians(((lon2 - lon1 + 180.0) % 360.0) - 180.0)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlon / 2.0) ** 2
    return 2.0 * radius_km * math.asin(min(1.0, math.sqrt(a)))


def find_atcf_match(
    *,
    typ_en: str,
    typ_number: int,
    year: int,
    positive_radius: int,
    negative_radius: int,
) -> AtcfMatch | None:
    target_name = normalize_name(typ_en)
    if not target_name:
        return None

    for atcf_id in candidate_atcf_ids(
        typ_number=typ_number,
        year=year,
        positive_radius=positive_radius,
        negative_radius=negative_radius,
    ):
        try:
            text = fetch_text(NOAA_BDECK_URL.format(atcf_id=atcf_id), timeout=10)
        except (HTTPError, URLError, TimeoutError):
            continue
        if target_name in normalize_name(text):
            return AtcfMatch(atcf_id=atcf_id, method="name")
    return None


def find_atcf_position_match(
    *,
    typ_number: int,
    year: int,
    data_time: str,
    kma_point: TrackPoint | None,
    positive_radius: int,
    negative_radius: int,
    max_distance_km: float,
    min_distance_gap_km: float,
) -> AtcfMatch | None:
    if kma_point is None:
        return None

    candidates: list[AtcfMatch] = []
    for atcf_id in candidate_atcf_ids(
        typ_number=typ_number,
        year=year,
        positive_radius=positive_radius,
        negative_radius=negative_radius,
    ):
        try:
            text = fetch_text(NOAA_BDECK_URL.format(atcf_id=atcf_id), timeout=10)
        except (HTTPError, URLError, TimeoutError):
            continue
        for point in bdeck_track_points(text, reference_time=kma_point.time_utc):
            distance = haversine_km(kma_point.lat, kma_point.lon, point.lat, point.lon)
            if distance <= max_distance_km:
                candidates.append(AtcfMatch(atcf_id=atcf_id, method="position", distance_km=distance))

    if not candidates:
        return None
    candidates.sort(key=lambda item: item.distance_km or float("inf"))
    if len(candidates) >= 2:
        best_distance = candidates[0].distance_km or float("inf")
        next_distance = candidates[1].distance_km or float("inf")
        if next_distance - best_distance < min_distance_gap_km:
            return None
    return candidates[0]


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


def linked_td_number_for_typ(td_rows: list[dict], *, year: int, typ_number: int) -> int | None:
    for row in td_rows:
        try:
            if int(row.get("YY", 0)) == year and int(row.get("TYP", -1)) == typ_number:
                return int(row.get("TD", 0))
        except (TypeError, ValueError):
            continue
    return None


def build_storm_jobs(
    *,
    now: datetime,
    data_time: str,
    td_rows: list[dict],
    typ_rows: list[dict],
    manual_map: dict,
    auth_key: str,
    atcf_search_positive_radius: int,
    atcf_search_negative_radius: int,
    atcf_position_max_distance_km: float,
    atcf_position_min_distance_gap_km: float,
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
        typ_name_ko = row.get("TYP_NAME", "").strip()
        linked_td_number = linked_td_number_for_typ(td_rows, year=year, typ_number=typ_number)
        manual_id = manual_atcf_id(
            manual_map,
            year=year,
            td_number=linked_td_number,
            typ_number=typ_number,
            typ_en=typ_en,
        )
        atcf_match = AtcfMatch(manual_id, "manual") if manual_id else find_atcf_match(
            typ_en=typ_en,
            typ_number=typ_number,
            year=year,
            positive_radius=atcf_search_positive_radius,
            negative_radius=atcf_search_negative_radius,
        )
        if atcf_match is None and typ_en:
            kma_point = fetch_kma_reference_point(typ_number=typ_number, data_time=data_time, auth_key=auth_key)
            atcf_match = find_atcf_position_match(
                typ_number=typ_number,
                year=year,
                data_time=data_time,
                kma_point=kma_point,
                positive_radius=atcf_search_positive_radius,
                negative_radius=atcf_search_negative_radius,
                max_distance_km=atcf_position_max_distance_km,
                min_distance_gap_km=atcf_position_min_distance_gap_km,
            )
        atcf_id = atcf_match.atcf_id if atcf_match else None
        atcf_method = atcf_match.method if atcf_match else ""
        if atcf_match and atcf_match.method == "position":
            reason = (
                "ATCF name match not found; using temporary position match "
                f"{atcf_match.atcf_id} ({atcf_match.distance_km:.0f} km)."
            )
        else:
            reason = "" if atcf_id else "ATCF name match not found; generating KMA-only guidance."
        active_typhoons.append(typ_number)
        jobs.append(StormJob(
            storm_key=f"typ_{year}_{typ_number:02d}",
            stage="TYP_LINKED" if atcf_id else "TYP_LINKED_ATCF_PENDING",
            year=year,
            data_time=data_time,
            td_number=None,
            linked_td_number=linked_td_number,
            typ_number=typ_number,
            typ_name_ko=typ_name_ko,
            typ_name=typ_en or typ_name_ko or "NAMELESS",
            typ_en=typ_en,
            atcf_id=atcf_id,
            skip_atcf=not bool(atcf_id),
            atcf_match_method=atcf_method,
            reason=reason,
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
            linked_td_number=None,
            typ_number=td_number,
            typ_name_ko="",
            typ_name="NAMELESS",
            typ_en="",
            atcf_id=manual_id,
            skip_atcf=not bool(manual_id),
            atcf_match_method="manual" if manual_id else "",
            reason="" if manual_id else "TD has no linked typhoon number yet.",
        ))

    return jobs


def metadata_path_for(output_root: Path, job: StormJob, fcst_hours: int) -> Path:
    return output_root / "metadata" / f"{job.data_time}_{job.storm_key}_{fcst_hours}h.json"


def status_key_for(job: StormJob, fcst_hours: int) -> str:
    return f"{job.storm_key}_{fcst_hours}h"


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
    fcst_hours: int,
    auto_fcst_hours: bool,
    source_overrides: list[str],
    dry_run: bool,
) -> dict:
    metadata_path = metadata_path_for(output_root, job, fcst_hours)
    command = [
        python,
        str(PROJECT_ROOT / "VTG.py"),
        "--typ-number",
        str(job.typ_number),
        "--typ-name",
        job.typ_name,
        "--typ-name-ko",
        job.typ_name_ko,
        "--storm-stage",
        "TD" if job.stage.startswith("TD_") else "TYP",
        "--data-time",
        job.data_time,
        "--fcst-hours",
        str(fcst_hours),
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
    if job.linked_td_number is not None:
        command.extend(["--linked-td-number", str(job.linked_td_number)])
    if job.skip_atcf:
        command.append("--skip-atcf")
    if auto_fcst_hours:
        command.append("--auto-fcst-hours")
    for override in source_overrides:
        command.extend(["--source-override", override])

    if dry_run:
        return {
            "status": "dry_run",
            "command": redacted_command(command),
            "metadata_path": str(metadata_path),
        }

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
    metadata = load_json(metadata_path, None)
    if metadata:
        result["metadata"] = metadata
        if metadata.get("no_output"):
            result["status"] = "no_output"
    return result


def manifest_entry_from_metadata(path: Path, metadata: dict) -> dict:
    data_time = str(metadata.get("data_time") or "")
    year = int(str(metadata.get("storm_year") or data_time[:4] or "0") or 0)
    typ_number = int(metadata.get("typ_number") or 0)
    stage = str(metadata.get("storm_stage") or "TYP")
    storm_key_prefix = "td" if stage.upper() == "TD" else "typ"
    storm_key = f"{storm_key_prefix}_{year}_{typ_number:02d}" if year and typ_number else path.stem
    return {
        "job": {
            "storm_key": storm_key,
            "stage": stage,
            "year": year,
            "data_time": data_time,
            "td_number": metadata.get("typ_number") if stage.upper() == "TD" else None,
            "linked_td_number": metadata.get("linked_td_number"),
            "typ_number": typ_number,
            "typ_name_ko": metadata.get("typ_name_ko") or "",
            "typ_name": metadata.get("typ_name") or "NAMELESS",
            "typ_en": metadata.get("typ_name") or "",
            "atcf_id": metadata.get("atcf_id"),
            "fcst_hours": metadata.get("fcst_hours"),
            "skip_atcf": bool(metadata.get("skip_atcf")),
        },
        "window": {"data_time": data_time},
        "result": {"status": "inventory", "metadata": metadata},
        "metadata_path": relative_asset_path(path),
    }


def relative_asset_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def metadata_from_image_path(path: Path, output_root: Path) -> dict | None:
    match = re.match(
        r"^(?P<stage>TYP|TD)_(?P<cyclone_id>\d{4})_(?P<name>.+)_(?P<data_time>\d{10,12})_(?P<fcst_hours>\d{2,3})h\.png$",
        path.name,
        re.IGNORECASE,
    )
    if not match:
        return None

    try:
        fcst_hours = int(match.group("fcst_hours"))
        typ_number = int(match.group("cyclone_id")[-2:])
    except ValueError:
        return None
    if fcst_hours not in VALID_FCST_HOURS:
        return None

    parent_year = path.parent.parent.name if path.parent and path.parent.parent else ""
    storm_year = parent_year if re.fullmatch(r"\d{4}", parent_year) else f"20{match.group('cyclone_id')[:2]}"
    try:
        generated_at = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).strftime("%Y%m%d%H%M%S")
    except OSError:
        generated_at = ""

    stage = match.group("stage").upper()
    return {
        "generated_at_utc": generated_at,
        "image_path": relative_asset_path(path),
        "storm_stage": stage,
        "storm_year": storm_year,
        "typ_number": typ_number,
        "typ_name": match.group("name"),
        "typ_name_ko": "",
        "data_time": match.group("data_time"),
        "fcst_hours": fcst_hours,
        "model_count": 0,
        "target_model_count": ACTIVE_MODEL_TARGET,
        "models": [],
        "skip_atcf": False,
    }


def manifest_inventory_key(metadata: dict) -> str:
    return (
        f"{metadata.get('data_time')}|"
        f"{metadata.get('storm_stage')}|"
        f"{metadata.get('typ_number')}|"
        f"{metadata.get('fcst_hours')}"
    )


def metadata_has_output_image(metadata: dict) -> bool:
    if metadata.get("no_output"):
        return False
    if not str(metadata.get("image_path") or "").strip():
        return False
    if "model_count" not in metadata:
        return True
    try:
        return int(metadata.get("model_count") or 0) > 0
    except (TypeError, ValueError):
        return False


def metadata_model_count(metadata: dict | None) -> int:
    if not isinstance(metadata, dict):
        return 0
    try:
        return int(metadata.get("model_count") or 0)
    except (TypeError, ValueError):
        return 0


def previous_completed_for_target(previous: dict, complete_model_count: int) -> bool:
    if not previous.get("completed"):
        return False
    if previous.get("atcf_match_method") == "position":
        return False
    return metadata_model_count(previous.get("metadata")) >= complete_model_count


def build_manifest_inventory(output_root: Path, run_entries: list[dict]) -> list[dict]:
    entries_by_key: dict[str, dict] = {}
    suppressed_keys: set[str] = set()
    metadata_dir = output_root / "metadata"
    if metadata_dir.exists():
        for path in sorted(metadata_dir.glob("*.json")):
            metadata = load_json(path, None)
            if not isinstance(metadata, dict):
                continue
            try:
                fcst_hours = int(metadata.get("fcst_hours") or 0)
            except (TypeError, ValueError):
                continue
            if fcst_hours not in VALID_FCST_HOURS:
                continue
            key = manifest_inventory_key(metadata)
            if not metadata_has_output_image(metadata):
                suppressed_keys.add(key)
                entries_by_key.pop(key, None)
                continue
            entry = manifest_entry_from_metadata(path, metadata)
            entries_by_key[key] = entry

    if output_root.exists():
        for path in sorted(output_root.glob("[0-9][0-9][0-9][0-9]/*/*.png")):
            metadata = metadata_from_image_path(path, output_root)
            if not metadata:
                continue
            key = manifest_inventory_key(metadata)
            if key in suppressed_keys:
                continue
            if key in entries_by_key:
                existing_metadata = entries_by_key[key].get("result", {}).get("metadata", {})
                if isinstance(existing_metadata, dict):
                    existing_metadata["image_path"] = metadata["image_path"]
                    existing_metadata.setdefault("generated_at_utc", metadata.get("generated_at_utc"))
                    existing_metadata.setdefault("target_model_count", metadata.get("target_model_count"))
                    existing_metadata.setdefault("models", metadata.get("models"))
                continue
            entries_by_key[key] = manifest_entry_from_metadata(path, metadata)

    for entry in run_entries:
        metadata = entry.get("result", {}).get("metadata")
        if not isinstance(metadata, dict) or not metadata:
            continue
        try:
            fcst_hours = int(metadata.get("fcst_hours") or 0)
        except (TypeError, ValueError):
            continue
        if fcst_hours not in VALID_FCST_HOURS:
            continue
        key = manifest_inventory_key(metadata)
        if not metadata_has_output_image(metadata):
            suppressed_keys.add(key)
            entries_by_key.pop(key, None)
            continue
        entries_by_key[key] = entry

    return sorted(
        entries_by_key.values(),
        key=lambda item: (
            item.get("job", {}).get("year") or 0,
            item.get("job", {}).get("typ_number") or 0,
            item.get("job", {}).get("data_time") or "",
            item.get("result", {}).get("metadata", {}).get("fcst_hours") or 0,
        ),
    )


def parse_fcst_hours(value: str) -> list[int]:
    hours: list[int] = []
    for token in str(value or "").replace(",", " ").split():
        try:
            hour = int(token)
        except ValueError:
            raise SystemExit("--fcst-hours must be a comma/space separated list of integers.")
        if hour not in VALID_FCST_HOURS:
            allowed = ", ".join(f"{value}h" for value in VALID_FCST_HOURS)
            raise SystemExit(f"--fcst-hours only supports {allowed}.")
        if hour not in hours:
            hours.append(hour)
    if not hours:
        raise SystemExit("--fcst-hours must include at least one forecast hour.")
    return hours


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run scheduled VTG image generation.")
    parser.add_argument("--now", help="Override current UTC time, YYYYmmddHHMM.")
    parser.add_argument("--output-root", type=Path, default=PROJECT_ROOT / "VTG_IMG")
    parser.add_argument("--auth-key", default=os.getenv("KMA_APIHUB_AUTH_KEY", ""))
    parser.add_argument("--manual-map", type=Path, default=PROJECT_ROOT / "vtg_manual_atcf_map.json")
    parser.add_argument("--status-path", type=Path, default=None)
    parser.add_argument("--manifest-path", type=Path, default=None)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--fcst-hours", default="120,240", help="Comma/space separated forecast hours to generate.")
    parser.add_argument("--auto-fcst-hours", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--source-override", action="append", default=[])
    parser.add_argument("--complete-model-count", type=int, default=ACTIVE_MODEL_TARGET)
    parser.add_argument("--min-run-interval-minutes", type=int, default=0)
    parser.add_argument("--atcf-search-radius", type=int, default=None, help="Legacy symmetric ATCF search radius.")
    parser.add_argument("--atcf-search-positive-radius", type=int, default=DEFAULT_ATCF_SEARCH_POSITIVE_RADIUS)
    parser.add_argument("--atcf-search-negative-radius", type=int, default=DEFAULT_ATCF_SEARCH_NEGATIVE_RADIUS)
    parser.add_argument("--atcf-position-max-distance-km", type=float, default=DEFAULT_ATCF_POSITION_MAX_DISTANCE_KM)
    parser.add_argument("--atcf-position-min-distance-gap-km", type=float, default=DEFAULT_ATCF_POSITION_MIN_DISTANCE_GAP_KM)
    parser.add_argument("--index-only", action="store_true", help="Rebuild manifest inventory from existing PNG/metadata files and exit.")
    parser.add_argument("--force", action="store_true", help="Run even if a previous metadata record met the completion target.")
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

    if args.index_only:
        manifest = {
            "updated_at_utc": format_utc_stamp(now),
            "window_start_offset_hours": WINDOW_START_OFFSET_HOURS,
            "window_end_offset_hours": WINDOW_END_OFFSET_HOURS,
            "complete_model_count": args.complete_model_count,
            "active_windows": [asdict(window) for window in windows],
            "runs": [],
            "inventory": build_manifest_inventory(output_root, []),
        }
        if not args.dry_run:
            write_json(manifest_path, manifest)
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 0

    if not args.auth_key:
        raise SystemExit("KMA_APIHUB_AUTH_KEY is required.")

    fcst_hours_list = parse_fcst_hours(args.fcst_hours)
    atcf_search_positive_radius = (
        args.atcf_search_radius
        if args.atcf_search_radius is not None
        else args.atcf_search_positive_radius
    )
    atcf_search_negative_radius = (
        args.atcf_search_radius
        if args.atcf_search_radius is not None
        else args.atcf_search_negative_radius
    )

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
            auth_key=args.auth_key,
            atcf_search_positive_radius=atcf_search_positive_radius,
            atcf_search_negative_radius=atcf_search_negative_radius,
            atcf_position_max_distance_km=args.atcf_position_max_distance_km,
            atcf_position_min_distance_gap_km=args.atcf_position_min_distance_gap_km,
        )
        for job in jobs:
            for fcst_hours in fcst_hours_list:
                status_key = status_key_for(job, fcst_hours)
                previous = cycle_status.get(status_key, {})
                if previous_completed_for_target(previous, args.complete_model_count) and not args.force:
                    run_entries.append({
                        "job": asdict(job),
                        "window": asdict(window),
                        "result": {"status": "skipped_completed", "metadata": previous.get("metadata")},
                    })
                    continue
                previous_updated = parse_utc_stamp(previous.get("updated_at_utc", ""))
                if (
                    args.min_run_interval_minutes > 0
                    and previous_updated
                    and now - previous_updated < timedelta(minutes=args.min_run_interval_minutes)
                    and not args.force
                ):
                    run_entries.append({
                        "job": asdict(job),
                        "window": asdict(window),
                        "result": {"status": "skipped_recent", "metadata": previous.get("metadata")},
                    })
                    continue
                actual_run_count += 1
                result = run_vtg(
                    job=job,
                    output_root=output_root,
                    auth_key=args.auth_key,
                    python=args.python,
                    fcst_hours=fcst_hours,
                    auto_fcst_hours=args.auto_fcst_hours,
                    source_overrides=args.source_override,
                    dry_run=args.dry_run,
                )
                metadata = result.get("metadata") or {}
                model_count = metadata_model_count(metadata)
                completed = model_count >= args.complete_model_count
                cycle_status[status_key] = {
                    "updated_at_utc": format_utc_stamp(now),
                    "completed": completed,
                    "metadata": metadata,
                    "last_status": result.get("status"),
                    "atcf_id": job.atcf_id,
                    "atcf_match_method": job.atcf_match_method,
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
        "inventory": build_manifest_inventory(output_root, run_entries),
    }
    should_clear_previous_manifest = not run_entries and bool(previous_manifest.get("runs"))
    inventory_changed = previous_manifest.get("inventory") != manifest.get("inventory")
    should_write_outputs = not args.dry_run and (
        actual_run_count > 0 or should_clear_previous_manifest or inventory_changed
    )
    if should_write_outputs:
        write_json(manifest_path, manifest)
        write_json(status_path, status)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
