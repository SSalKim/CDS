from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
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
WINDOW_START_OFFSET_HOURS = 5
WINDOW_END_OFFSET_HOURS = 11
DEFAULT_STATUS_RETENTION_DAYS = 30
MANIFEST_METADATA_KEYS = (
    "generated_at_utc",
    "image_path",
    "storm_stage",
    "storm_year",
    "typ_number",
    "data_typ_number",
    "typ_name",
    "typ_name_ko",
    "linked_td_number",
    "linked_typ_number",
    "atcf_id",
    "extra_atcf_ids",
    "data_time",
    "fcst_hours",
    "intensity",
    "model_count",
    "target_model_count",
    "models",
    "model_labels",
    "skip_atcf",
    "no_output",
    "no_output_reason",
)
STATUS_METADATA_KEYS = MANIFEST_METADATA_KEYS + ("render_signature",)
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/csv,text/plain,*/*",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "close",
}


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
    linked_typ_number: int | None
    typ_number: int
    data_typ_number: int
    typ_name_ko: str
    typ_name: str
    typ_en: str
    atcf_id: str | None
    skip_atcf: bool
    atcf_match_method: str = ""
    reason: str = ""
    analysis_point: TrackPoint | None = None
    analysis_source: str = ""
    analysis_match_method: str = ""
    analysis_distance_km: float | None = None


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
    point: TrackPoint | None = None
    reference_point: TrackPoint | None = None


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


def normalize_kma_list_stamp_year(value: str, year: int) -> str:
    text = str(value or "").strip()
    if not re.fullmatch(r"\d{12}", text):
        return text
    stamp_year = int(text[:4])
    if stamp_year in (2100, 9999):
        return text
    if stamp_year != year:
        return f"{year:04d}{text[4:]}"
    return text


def normalize_kma_list_row_years(row: dict) -> dict:
    try:
        year = int(row.get("YY", 0))
    except (TypeError, ValueError):
        return row
    if not year:
        return row
    normalized = dict(row)
    for key in ("TM_ST", "TM_ED"):
        if key in normalized:
            normalized[key] = normalize_kma_list_stamp_year(str(normalized[key]), year)
    return normalized


def parse_cycle_override(value: str) -> datetime | None:
    text = str(value or "").strip()
    if not re.fullmatch(r"\d{10}", text):
        return None
    try:
        cycle = datetime.strptime(text, "%Y%m%d%H").replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    if cycle.hour not in CYCLE_HOURS:
        return None
    return cycle


def cycle_probe_time(cycle: datetime) -> datetime:
    return cycle + timedelta(hours=WINDOW_START_OFFSET_HOURS)


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


def active_typ_at(now: datetime, row: dict) -> bool:
    now_flag = str(row.get("NOW", "")).strip()
    if now_flag == "1":
        return True
    if now_flag == "2":
        return active_at(now, row.get("TM_ST", ""), row.get("TM_ED", ""))
    return active_at(now, row.get("TM_ST", ""), row.get("TM_ED", ""))


def fetch_text(url: str, *, timeout: float = 12, retries: int = 2, retry_delay: float = 3.0) -> str:
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        request = Request(url, headers=REQUEST_HEADERS)
        try:
            with urlopen(request, timeout=timeout) as response:
                data = response.read()
            break
        except HTTPError as exc:
            last_error = exc
            if exc.code < 500 or attempt >= retries:
                raise
        except (URLError, TimeoutError) as exc:
            last_error = exc
            if attempt >= retries:
                raise
        time.sleep(retry_delay)
    else:
        raise last_error or TimeoutError(f"request failed: {url}")

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


def kma_cache_path(cache_dir: Path, endpoint: str, year: int) -> Path:
    return cache_dir / f"{Path(endpoint).stem}_{year}.json"


def load_cached_kma_rows(cache_dir: Path | None, endpoint: str, year: int) -> list[dict] | None:
    if cache_dir is None:
        return None
    path = kma_cache_path(cache_dir, endpoint, year)
    payload = load_json(path, None)
    if not isinstance(payload, dict):
        return None
    rows = payload.get("rows")
    if not isinstance(rows, list):
        return None
    rows = [normalize_kma_list_row_years(row) if isinstance(row, dict) else row for row in rows]
    print(
        f"Using cached KMA APIHUB {Path(endpoint).stem} rows for {year} "
        f"from {path} (updated_at_utc={payload.get('updated_at_utc', '')})."
    )
    return rows


def write_cached_kma_rows(cache_dir: Path | None, endpoint: str, year: int, rows: list[dict]) -> None:
    if cache_dir is None:
        return
    path = kma_cache_path(cache_dir, endpoint, year)
    previous = load_json(path, None)
    if isinstance(previous, dict) and previous.get("rows") == rows:
        return
    write_json(path, {
        "updated_at_utc": format_utc_stamp(utc_now()),
        "endpoint": endpoint,
        "year": year,
        "rows": rows,
    })


def fetch_kma_list_text(endpoint: str, year: int, auth_key: str, *, cache_dir: Path | None) -> str | None:
    try:
        return fetch_text(kma_list_url(endpoint, year, auth_key), timeout=20, retries=2, retry_delay=5.0)
    except HTTPError as exc:
        if exc.code < 500:
            raise
        print(f"KMA APIHUB {Path(endpoint).stem} {year} failed with HTTP {exc.code}; trying cached rows.")
        return None
    except (URLError, TimeoutError) as exc:
        print(f"KMA APIHUB {Path(endpoint).stem} {year} request failed ({exc}); trying cached rows.")
        return None


def fetch_td_rows(year: int, auth_key: str, *, cache_dir: Path | None = None) -> list[dict]:
    rows = []
    text = fetch_kma_list_text(TD_LIST_ENDPOINT, year, auth_key, cache_dir=cache_dir)
    if text is None:
        cached = load_cached_kma_rows(cache_dir, TD_LIST_ENDPOINT, year)
        if cached is not None:
            return cached
        raise TimeoutError(f"KMA APIHUB {TD_LIST_ENDPOINT} {year} failed and no cache is available.")
    for row in parse_kma_csv_lines(text, fixed_columns=5):
        rows.append({
            "YY": row[0],
            "TD": row[1],
            "TYP": row[2],
            "TM_ST": normalize_kma_list_stamp_year(row[3], year),
            "TM_ED": normalize_kma_list_stamp_year(row[4], year),
            "REM": ",".join(row[5:]).strip(),
        })
    write_cached_kma_rows(cache_dir, TD_LIST_ENDPOINT, year, rows)
    return rows


def fetch_typ_rows(year: int, auth_key: str, *, cache_dir: Path | None = None) -> list[dict]:
    rows = []
    text = fetch_kma_list_text(TYP_LIST_ENDPOINT, year, auth_key, cache_dir=cache_dir)
    if text is None:
        cached = load_cached_kma_rows(cache_dir, TYP_LIST_ENDPOINT, year)
        if cached is not None:
            return cached
        raise TimeoutError(f"KMA APIHUB {TYP_LIST_ENDPOINT} {year} failed and no cache is available.")
    for row in parse_kma_csv_lines(text, fixed_columns=8):
        rows.append({
            "YY": row[0],
            "SEQ": row[1],
            "NOW": row[2],
            "EFF": row[3],
            "TM_ST": normalize_kma_list_stamp_year(row[4], year),
            "TM_ED": normalize_kma_list_stamp_year(row[5], year),
            "TYP_NAME": row[6],
            "TYP_EN": row[7],
            "REM": ",".join(row[8:]).strip(),
        })
    write_cached_kma_rows(cache_dir, TYP_LIST_ENDPOINT, year, rows)
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
        text = fetch_text(kma_gts_now_url(data_time, auth_key), timeout=15, retries=1, retry_delay=3.0)
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
    if not candidates:
        return None

    lat = sum(point.lat for point in candidates) / len(candidates)
    lon = sum(point.lon for point in candidates) / len(candidates)
    return TrackPoint(time_utc=f"{data_time[:10]}00", lat=lat, lon=lon)


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


def candidate_td_atcf_ids(*, td_number: int, year: int) -> list[str]:
    ids: list[str] = []
    seen: set[str] = set()
    start_number = max(1, min(50, math.ceil(td_number / 2)))

    def add(candidate_number: int) -> None:
        if candidate_number < 1 or candidate_number > 99:
            return
        atcf_id = f"wp{candidate_number:02d}{year}"
        if atcf_id not in seen:
            seen.add(atcf_id)
            ids.append(atcf_id)

    add(start_number)
    for offset in range(1, 50):
        for candidate_number in (start_number + offset, start_number - offset):
            if 1 <= candidate_number <= 50:
                add(candidate_number)
        if len(ids) >= 50:
            break
    for candidate_number in range(90, 100):
        add(candidate_number)
    for candidate_number in range(51, 90):
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


def fetch_bdeck_analysis_point(atcf_id: str, *, data_time: str) -> TrackPoint | None:
    try:
        text = fetch_text(NOAA_BDECK_URL.format(atcf_id=atcf_id), timeout=15)
    except (HTTPError, URLError, TimeoutError):
        return None
    points = bdeck_track_points(text, reference_time=f"{data_time[:10]}00")
    return points[0] if points else None


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
            text = fetch_text(NOAA_BDECK_URL.format(atcf_id=atcf_id), timeout=15)
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
    positive_radius: int | None = None,
    negative_radius: int | None = None,
    atcf_ids: list[str] | None = None,
    max_distance_km: float,
    min_distance_gap_km: float,
) -> AtcfMatch | None:
    if kma_point is None:
        return None

    if atcf_ids is None:
        if positive_radius is None or negative_radius is None:
            raise ValueError("positive_radius and negative_radius are required when atcf_ids is not provided.")
        atcf_ids = candidate_atcf_ids(
            typ_number=typ_number,
            year=year,
            positive_radius=positive_radius,
            negative_radius=negative_radius,
        )

    candidates: list[AtcfMatch] = []
    for atcf_id in atcf_ids:
        try:
            text = fetch_text(NOAA_BDECK_URL.format(atcf_id=atcf_id), timeout=15)
        except (HTTPError, URLError, TimeoutError):
            continue
        for point in bdeck_track_points(text, reference_time=kma_point.time_utc):
            distance = haversine_km(kma_point.lat, kma_point.lon, point.lat, point.lon)
            if distance <= max_distance_km:
                candidates.append(AtcfMatch(
                    atcf_id=atcf_id,
                    method="position",
                    distance_km=distance,
                    point=point,
                    reference_point=kma_point,
                ))

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
    except json.JSONDecodeError as exc:
        print(f"Warning: failed to parse JSON {path}: {exc}", file=sys.stderr)
        return fallback
    except OSError as exc:
        print(f"Warning: failed to read JSON {path}: {exc}", file=sys.stderr)
        return fallback


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        tmp_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        tmp_path.replace(path)
    finally:
        try:
            if tmp_path.exists():
                tmp_path.unlink()
        except OSError:
            pass


def write_github_outputs(path: Path | None, outputs: dict[str, object]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for key, value in outputs.items():
            if isinstance(value, bool):
                value = "true" if value else "false"
            handle.write(f"{key}={value}\n")


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
    resolve_atcf: bool = True,
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
        is_active = active_typ_at(now, row)
        if not is_active:
            continue
        if parse_utc_stamp(row.get("TM_ST", "")) and data_dt < parse_utc_stamp(row.get("TM_ST", "")):
            continue
        typ_en = row.get("TYP_EN", "").strip().upper()
        typ_name_ko = row.get("TYP_NAME", "").strip()
        linked_td_number = linked_td_number_for_typ(td_rows, year=year, typ_number=typ_number)
        manual_id = None
        atcf_match = None
        if resolve_atcf:
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
        if resolve_atcf and atcf_match is None and typ_en:
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
        analysis_point = atcf_match.point if atcf_match and atcf_match.method == "position" else None
        if analysis_point is None and atcf_id:
            analysis_point = fetch_bdeck_analysis_point(atcf_id, data_time=data_time)
        analysis_source = "BDECK" if analysis_point else ""
        analysis_match_method = atcf_match.method if analysis_point and atcf_match else ""
        analysis_distance_km = atcf_match.distance_km if analysis_point and atcf_match else None
        if not resolve_atcf:
            reason = "ATCF matching skipped for lightweight precheck."
        elif atcf_match and atcf_match.method == "position":
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
            linked_typ_number=None,
            typ_number=typ_number,
            data_typ_number=typ_number,
            typ_name_ko=typ_name_ko,
            typ_name=typ_en or typ_name_ko or "NONAME",
            typ_en=typ_en,
            atcf_id=atcf_id,
            skip_atcf=not bool(atcf_id),
            atcf_match_method=atcf_method,
            reason=reason,
            analysis_point=analysis_point,
            analysis_source=analysis_source,
            analysis_match_method=analysis_match_method,
            analysis_distance_km=analysis_distance_km,
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

        linked_typ_row = None
        linked_typ_en = ""
        linked_typ_name_ko = ""
        linked_typ_start = None
        if typ_number != 0:
            linked_typ_row = next(
                (
                    item for item in typ_rows
                    if safe_int(item.get("YY")) == year and safe_int(item.get("SEQ")) == typ_number
                ),
                None,
            )
            if linked_typ_row:
                linked_typ_en = str(linked_typ_row.get("TYP_EN") or "").strip().upper()
                linked_typ_name_ko = str(linked_typ_row.get("TYP_NAME") or "").strip()
                linked_typ_start = parse_utc_stamp(str(linked_typ_row.get("TM_ST") or ""))
        linked_typ_has_started = bool(typ_number and linked_typ_start and data_dt >= linked_typ_start)
        display_typ_en = linked_typ_en if linked_typ_has_started else ""
        display_typ_name_ko = linked_typ_name_ko if linked_typ_has_started else ""

        manual_id = None
        atcf_match = None
        if resolve_atcf:
            manual_id = manual_atcf_id(
                manual_map,
                year=year,
                td_number=td_number,
                typ_number=typ_number or td_number,
                typ_en=display_typ_en,
            )
            atcf_match = AtcfMatch(manual_id, "manual") if manual_id else None
            if atcf_match is None and display_typ_en:
                atcf_match = find_atcf_match(
                    typ_en=display_typ_en,
                    typ_number=typ_number,
                    year=year,
                    positive_radius=atcf_search_positive_radius,
                    negative_radius=atcf_search_negative_radius,
                )
        if resolve_atcf and atcf_match is None:
            reference_typ_number = td_number
            kma_point = fetch_kma_reference_point(typ_number=reference_typ_number, data_time=data_time, auth_key=auth_key)
            atcf_match = find_atcf_position_match(
                typ_number=reference_typ_number,
                year=year,
                data_time=data_time,
                kma_point=kma_point,
                atcf_ids=(
                    candidate_atcf_ids(
                        typ_number=typ_number,
                        year=year,
                        positive_radius=atcf_search_positive_radius,
                        negative_radius=atcf_search_negative_radius,
                    )
                    if typ_number
                    else candidate_td_atcf_ids(td_number=td_number, year=year)
                ),
                max_distance_km=atcf_position_max_distance_km,
                min_distance_gap_km=atcf_position_min_distance_gap_km,
            )
        atcf_id = atcf_match.atcf_id if atcf_match else None
        atcf_method = atcf_match.method if atcf_match else ""
        analysis_point = atcf_match.point if atcf_match and atcf_match.method == "position" else None
        if analysis_point is None and atcf_id:
            analysis_point = fetch_bdeck_analysis_point(atcf_id, data_time=data_time)
        analysis_source = "BDECK" if analysis_point else ""
        analysis_match_method = atcf_match.method if analysis_point and atcf_match else ""
        analysis_distance_km = atcf_match.distance_km if analysis_point and atcf_match else None
        if not resolve_atcf:
            stage = "TD_UNLINKED"
            reason = "ATCF matching skipped for lightweight precheck."
        elif typ_number != 0 and atcf_match and atcf_match.method == "position":
            if linked_typ_has_started:
                stage = "TD_LINKED_TYP_POSITION_ATCF"
                reason = (
                    f"TD is linked to typhoon {typ_number}; using temporary position match "
                    f"{atcf_match.atcf_id} ({atcf_match.distance_km:.0f} km)."
                )
            else:
                stage = "TD_PRE_TYP_POSITION_ATCF"
                reason = (
                    f"TD is linked to future typhoon {typ_number}; name withheld until typhoon start; "
                    f"using temporary position match {atcf_match.atcf_id} "
                    f"({atcf_match.distance_km:.0f} km)."
                )
        elif typ_number != 0:
            if linked_typ_has_started:
                stage = "TD_LINKED_TYP"
                reason = "" if atcf_id else f"TD is linked to typhoon {typ_number}; ATCF match not found."
            else:
                stage = "TD_PRE_TYP"
                reason = (
                    f"TD is linked to future typhoon {typ_number}; name withheld until typhoon start."
                    if atcf_id
                    else f"TD is linked to future typhoon {typ_number}; name withheld until typhoon start; ATCF match not found."
                )
        elif atcf_match and atcf_match.method == "position":
            stage = "TD_POSITION_ATCF"
            reason = (
                "TD has no linked typhoon number yet; using temporary position match "
                f"{atcf_match.atcf_id} ({atcf_match.distance_km:.0f} km)."
            )
        elif manual_id:
            stage = "TD_MANUAL_ATCF"
            reason = ""
        else:
            stage = "TD_UNLINKED"
            reason = "TD has no linked typhoon number yet."
        jobs.append(StormJob(
            storm_key=(
                f"td_{year}_{td_number:02d}_typ_{typ_number:02d}"
                if typ_number
                else f"td_{year}_{td_number:02d}"
            ),
            stage=stage,
            year=year,
            data_time=data_time,
            td_number=td_number,
            linked_td_number=None,
            linked_typ_number=typ_number or None,
            typ_number=td_number,
            data_typ_number=td_number,
            typ_name_ko=display_typ_name_ko if typ_number else "",
            typ_name=display_typ_en or display_typ_name_ko or "NONAME",
            typ_en=display_typ_en,
            atcf_id=atcf_id,
            skip_atcf=not bool(atcf_id),
            atcf_match_method=atcf_method,
            reason=reason,
            analysis_point=analysis_point,
            analysis_source=analysis_source,
            analysis_match_method=analysis_match_method,
            analysis_distance_km=analysis_distance_km,
        ))

    return jobs


def metadata_path_for(output_root: Path, job: StormJob, fcst_hours: int) -> Path:
    return output_root / "metadata" / f"{job.data_time}_{job.storm_key}_{fcst_hours}h.json"


def deterministic_output_path_for(output_root: Path, job: StormJob, fcst_hours: int) -> Path:
    year_str = str(job.year)
    cyclone_id = f"{job.year % 100:02d}{job.typ_number:02d}"
    stage = "TD" if job.stage.startswith("TD_") else "TYP"
    storm_name = job.typ_name or "NONAME"
    dir_name = f"{stage}_{cyclone_id}_{storm_name}"
    file_name = f"{stage}_{cyclone_id}_{storm_name}_{job.data_time}_{fcst_hours}h.png"
    return output_root / year_str / dir_name / file_name


def stage_existing_outputs_for_forced_rerun(
    output_root: Path,
    job: StormJob,
    fcst_hours_list: list[int],
    metadata_paths: dict[int, Path] | None = None,
) -> tuple[dict[int, dict[str, Path]], Path | None]:
    root = output_root.resolve()
    backup_root = Path(os.environ.get("RUNNER_TEMP") or tempfile.gettempdir())
    backup_root = backup_root / f"vtg_force_backup_{os.getpid()}_{int(time.time())}"
    backups: dict[int, dict[str, Path]] = {}
    for fcst_hours in dict.fromkeys(fcst_hours_list):
        target = deterministic_output_path_for(output_root, job, fcst_hours)
        try:
            resolved = target.resolve()
        except OSError:
            resolved = target.absolute()
        if not str(resolved).lower().startswith(str(root).lower()):
            raise RuntimeError(f"Refusing to delete output outside {root}: {resolved}")
        if target.exists():
            relative_target = target.relative_to(output_root)
            backup_path = backup_root / relative_target
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(target), str(backup_path))
            backups.setdefault(fcst_hours, {})
            backups[fcst_hours]["target"] = target
            backups[fcst_hours]["target_backup"] = backup_path
            print(f"Staged existing deterministic output before forced rerun: {target}")
        metadata_path = metadata_paths.get(fcst_hours) if metadata_paths else None
        if metadata_path and metadata_path.exists():
            try:
                resolved_metadata = metadata_path.resolve()
            except OSError:
                resolved_metadata = metadata_path.absolute()
            if not str(resolved_metadata).lower().startswith(str(root).lower()):
                raise RuntimeError(f"Refusing to move metadata outside {root}: {resolved_metadata}")
            relative_metadata = metadata_path.relative_to(output_root)
            metadata_backup_path = backup_root / relative_metadata
            metadata_backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(metadata_path), str(metadata_backup_path))
            backups.setdefault(fcst_hours, {})
            backups[fcst_hours]["metadata"] = metadata_path
            backups[fcst_hours]["metadata_backup"] = metadata_backup_path
            print(f"Staged existing metadata before forced rerun: {metadata_path}")
    return backups, backup_root if backups else None


def finish_forced_output_backups(
    backups: dict[int, dict[str, Path]],
    backup_root: Path | None,
    failed_hours: set[int],
) -> None:
    for fcst_hours, paths in backups.items():
        if fcst_hours in failed_hours:
            target = paths.get("target")
            backup_path = paths.get("target_backup")
            if target and backup_path and backup_path.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists():
                    target.unlink()
                shutil.move(str(backup_path), str(target))
                print(f"Restored previous deterministic output after failed forced rerun: {target}")
            metadata_path = paths.get("metadata")
            metadata_backup_path = paths.get("metadata_backup")
            if metadata_path and metadata_backup_path and metadata_backup_path.exists():
                metadata_path.parent.mkdir(parents=True, exist_ok=True)
                if metadata_path.exists():
                    metadata_path.unlink()
                shutil.move(str(metadata_backup_path), str(metadata_path))
                print(f"Restored previous metadata after failed forced rerun: {metadata_path}")
        else:
            backup_path = paths.get("target_backup")
            if backup_path and backup_path.exists():
                backup_path.unlink()
            metadata_backup_path = paths.get("metadata_backup")
            if metadata_backup_path and metadata_backup_path.exists():
                metadata_backup_path.unlink()
    if backup_root and backup_root.exists():
        shutil.rmtree(backup_root, ignore_errors=True)


def log_failed_vtg_result(job: StormJob, fcst_hours: int, result: dict) -> None:
    status = result.get("status")
    if status != "failed":
        return
    print(
        "VTG generation failed: "
        f"storm={job.storm_key} data_time={job.data_time} "
        f"fcst_hours={fcst_hours} returncode={result.get('returncode', 'unknown')}",
        file=sys.stderr,
    )
    stderr = str(result.get("stderr") or "").strip()
    stdout = str(result.get("stdout") or "").strip()
    if stderr:
        print("--- VTG stderr tail ---", file=sys.stderr)
        print(stderr, file=sys.stderr)
    if stdout:
        print("--- VTG stdout tail ---", file=sys.stderr)
        print(stdout, file=sys.stderr)


def is_current_file(path: Path, started_at: float) -> bool:
    try:
        return path.exists() and path.stat().st_mtime >= started_at - 1.0
    except OSError:
        return False


def metadata_output_image_exists(output_root: Path, metadata: dict) -> bool:
    image_path = metadata.get("image_path")
    if not image_path:
        return False
    path = Path(str(image_path))
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    if path.exists():
        return True
    fallback = output_root / Path(str(image_path))
    return fallback.exists()


def status_key_for(job: StormJob, fcst_hours: int) -> str:
    return f"{job.storm_key}_{fcst_hours}h"


def redacted_command(command: list[str]) -> list[str]:
    redacted = command.copy()
    for index, value in enumerate(redacted[:-1]):
        if value == "--auth-key":
            redacted[index + 1] = "***"
    return redacted


def looks_like_transient_network_error(text: str) -> bool:
    haystack = str(text or "").lower()
    markers = (
        "timed out",
        "timeout",
        "connecttimeout",
        "read timed out",
        "temporarily unavailable",
        "temporary failure",
        "connection reset",
        "connection aborted",
        "remote end closed connection",
    )
    return any(marker in haystack for marker in markers)


def run_command_with_network_retry(
    command: list[str],
    *,
    cwd: Path,
    retries: int = 1,
    retry_delay_seconds: int = 60,
) -> subprocess.CompletedProcess[str]:
    completed: subprocess.CompletedProcess[str] | None = None
    for attempt in range(retries + 1):
        completed = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode == 0:
            return completed

        combined_output = f"{completed.stdout}\n{completed.stderr}"
        if attempt >= retries or not looks_like_transient_network_error(combined_output):
            return completed

        print(
            "VTG.py failed with a transient network-looking error; "
            f"retrying in {retry_delay_seconds}s ({attempt + 1}/{retries})."
        )
        time.sleep(retry_delay_seconds)

    assert completed is not None
    return completed


def vtg_command(
    *,
    job: StormJob,
    output_root: Path,
    auth_key: str,
    python: str,
    fcst_hours_list: list[int],
    auto_fcst_hours: bool,
    source_overrides: list[str],
) -> tuple[list[str], dict[int, Path]]:
    unique_hours = list(dict.fromkeys(fcst_hours_list))
    metadata_paths = {fcst_hours: metadata_path_for(output_root, job, fcst_hours) for fcst_hours in unique_hours}
    command = [
        python,
        str(PROJECT_ROOT / "VTG.py"),
        "--typ-number",
        str(job.typ_number),
        "--data-typ-number",
        str(job.data_typ_number),
        "--typ-name",
        job.typ_name,
        "--typ-name-ko",
        job.typ_name_ko,
        "--storm-stage",
        "TD" if job.stage.startswith("TD_") else "TYP",
        "--data-time",
        job.data_time,
        "--fcst-hours",
        ",".join(str(fcst_hours) for fcst_hours in unique_hours),
        "--output-root",
        str(output_root),
        "--auth-key",
        auth_key,
        "--overwrite",
        "--no-show",
    ]
    if len(unique_hours) == 1:
        command.extend(["--metadata-path", str(metadata_paths[unique_hours[0]])])
    if job.atcf_id:
        command.extend(["--atcf-id", job.atcf_id])
    if job.analysis_point:
        command.extend([
            "--analysis-lat",
            f"{job.analysis_point.lat:.4f}",
            "--analysis-lon",
            f"{job.analysis_point.lon:.4f}",
            "--analysis-time",
            job.analysis_point.time_utc,
            "--analysis-source",
            job.analysis_source or "BDECK",
        ])
        if job.analysis_match_method:
            command.extend(["--analysis-match-method", job.analysis_match_method])
        if job.atcf_id:
            command.extend(["--analysis-atcf-id", job.atcf_id])
        if job.analysis_distance_km is not None:
            command.extend(["--analysis-distance-km", f"{job.analysis_distance_km:.1f}"])
    if job.linked_td_number is not None:
        command.extend(["--linked-td-number", str(job.linked_td_number)])
    if job.linked_typ_number is not None:
        command.extend(["--linked-typ-number", str(job.linked_typ_number)])
    if job.skip_atcf:
        command.append("--skip-atcf")
    if auto_fcst_hours:
        command.append("--auto-fcst-hours")
    for override in source_overrides:
        command.extend(["--source-override", override])
    return command, metadata_paths


def run_vtg_batch(
    *,
    job: StormJob,
    output_root: Path,
    auth_key: str,
    python: str,
    fcst_hours_list: list[int],
    auto_fcst_hours: bool,
    source_overrides: list[str],
    dry_run: bool,
    clear_existing: bool = False,
) -> dict[int, dict]:
    command, metadata_paths = vtg_command(
        job=job,
        output_root=output_root,
        auth_key=auth_key,
        python=python,
        fcst_hours_list=fcst_hours_list,
        auto_fcst_hours=auto_fcst_hours,
        source_overrides=source_overrides,
    )

    if dry_run:
        return {
            fcst_hours: {
                "status": "dry_run",
                "command": redacted_command(command),
                "metadata_path": str(metadata_path),
            }
            for fcst_hours, metadata_path in metadata_paths.items()
        }

    forced_backups: dict[int, dict[str, Path]] = {}
    forced_backup_root: Path | None = None
    if clear_existing:
        forced_backups, forced_backup_root = stage_existing_outputs_for_forced_rerun(
            output_root,
            job,
            fcst_hours_list,
            metadata_paths,
        )

    command_started_at = time.time()
    completed = run_command_with_network_retry(
        command,
        cwd=PROJECT_ROOT,
        retries=1,
        retry_delay_seconds=60,
    )
    results: dict[int, dict] = {}
    for fcst_hours, metadata_path in metadata_paths.items():
        metadata_is_current = is_current_file(metadata_path, command_started_at)
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
            if metadata_is_current:
                result["metadata_current"] = True
            if metadata_is_current and metadata.get("no_output"):
                result["status"] = "no_output"
            elif metadata_is_current and metadata_output_image_exists(output_root, metadata):
                result["status"] = "ok"
            elif completed.returncode != 0:
                result["stderr"] = (
                    result["stderr"]
                    + f"\nMetadata was not refreshed for {fcst_hours}h or its image is missing: {metadata_path}"
                )[-4000:]
        elif completed.returncode == 0:
            result["status"] = "failed"
            result["stderr"] = (
                result["stderr"] + f"\nMetadata was not written for {fcst_hours}h: {metadata_path}"
            )[-4000:]
        results[fcst_hours] = result
    if forced_backups:
        failed_hours = {
            fcst_hours
            for fcst_hours, result in results.items()
            if result.get("status") in {"failed", "no_output"}
        }
        finish_forced_output_backups(forced_backups, forced_backup_root, failed_hours)
        for fcst_hours in failed_hours:
            paths = forced_backups.get(fcst_hours, {})
            metadata_path = paths.get("metadata")
            if not metadata_path:
                continue
            restored_metadata = load_json(metadata_path, None)
            if isinstance(restored_metadata, dict) and metadata_output_image_exists(output_root, restored_metadata):
                results[fcst_hours]["status"] = "restored_previous"
                results[fcst_hours]["metadata"] = restored_metadata
                results[fcst_hours]["metadata_current"] = False
                results[fcst_hours]["stderr"] = (
                    str(results[fcst_hours].get("stderr") or "")
                    + "\nRestored previous metadata/image after forced rerun produced no replacement output."
                )[-4000:]
    return results


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
    return run_vtg_batch(
        job=job,
        output_root=output_root,
        auth_key=auth_key,
        python=python,
        fcst_hours_list=[fcst_hours],
        auto_fcst_hours=auto_fcst_hours,
        source_overrides=source_overrides,
        dry_run=dry_run,
    )[fcst_hours]


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
            "linked_typ_number": metadata.get("linked_typ_number"),
            "typ_number": typ_number,
            "data_typ_number": metadata.get("data_typ_number") or typ_number,
            "typ_name_ko": metadata.get("typ_name_ko") or "",
            "typ_name": metadata.get("typ_name") or "NONAME",
            "typ_en": metadata.get("typ_name") or "",
            "atcf_id": metadata.get("atcf_id"),
            "fcst_hours": metadata.get("fcst_hours"),
            "skip_atcf": bool(metadata.get("skip_atcf")),
        },
        "window": {"data_time": data_time},
        "result": {"status": "inventory", "metadata": compact_metadata(metadata)},
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


def normalized_image_path(value: object) -> str:
    return str(value or "").strip().replace("\\", "/")


def manifest_identity_key(metadata: dict) -> str:
    return (
        f"{manifest_inventory_key(metadata)}|"
        f"{metadata.get('data_typ_number') or ''}|"
        f"{metadata.get('linked_td_number') or ''}|"
        f"{metadata.get('linked_typ_number') or ''}|"
        f"{metadata.get('typ_name') or ''}"
    )


def manifest_suppression_tokens(metadata: dict) -> set[str]:
    tokens = {f"identity|{manifest_identity_key(metadata)}"}
    image_path = normalized_image_path(metadata.get("image_path"))
    if image_path:
        tokens.add(f"path|{image_path}")
    return tokens


def metadata_matches_suppression(metadata: dict, suppressed_tokens: set[str]) -> bool:
    return bool(manifest_suppression_tokens(metadata) & suppressed_tokens)


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


def compact_metadata(metadata: dict | None, allowed_keys: tuple[str, ...] = MANIFEST_METADATA_KEYS) -> dict:
    if not isinstance(metadata, dict):
        return {}
    compact = {}
    has_model_labels = bool(metadata.get("model_labels"))
    for key in allowed_keys:
        if key == "models" and has_model_labels:
            continue
        if key in metadata:
            compact[key] = metadata[key]
    return compact


def compact_manifest_entry(entry: dict) -> dict:
    if not isinstance(entry, dict):
        return {}
    result = entry.get("result") if isinstance(entry.get("result"), dict) else {}
    metadata = compact_metadata(result.get("metadata"))
    job = entry.get("job") if isinstance(entry.get("job"), dict) else {}
    window = entry.get("window") if isinstance(entry.get("window"), dict) else {}

    compact_job = {}
    for key in (
        "storm_key",
        "stage",
        "year",
        "data_time",
        "td_number",
        "linked_td_number",
        "typ_number",
        "typ_name_ko",
        "typ_name",
        "typ_en",
        "atcf_id",
        "fcst_hours",
        "skip_atcf",
    ):
        if key in job:
            compact_job[key] = job[key]

    compact_window = {}
    for key in ("data_time", "cycle_time_utc", "start_utc", "end_utc"):
        if key in window:
            compact_window[key] = window[key]

    compact = {
        "job": compact_job,
        "window": compact_window,
        "result": {
            "status": result.get("status", "unknown"),
            "metadata": metadata,
        },
    }
    if "metadata_path" in entry:
        compact["metadata_path"] = entry["metadata_path"]
    if "completed" in entry:
        compact["completed"] = bool(entry.get("completed"))
    if "final_check" in entry:
        compact["final_check"] = bool(entry.get("final_check"))
    return compact


def compact_manifest_runs(run_entries: list[dict]) -> list[dict]:
    return [entry for entry in (compact_manifest_entry(entry) for entry in run_entries) if entry]


def compact_status_record(record: dict) -> dict:
    if not isinstance(record, dict):
        return {}
    compact = {}
    for key in (
        "updated_at_utc",
        "completed",
        "last_status",
        "atcf_id",
        "atcf_match_method",
        "reason",
        "final_checked_at_utc",
        "final_check_window_end_utc",
    ):
        if key in record:
            compact[key] = record[key]
    compact["metadata"] = compact_metadata(record.get("metadata"), STATUS_METADATA_KEYS)
    return compact


def prune_status_for_persistence(
    status: dict,
    *,
    active_data_times: set[str],
    retention_days: int,
    reference_time: datetime,
) -> dict:
    cycles = status.get("cycles") if isinstance(status, dict) else {}
    if not isinstance(cycles, dict):
        return {"cycles": {}}

    cutoff = reference_time - timedelta(days=retention_days) if retention_days > 0 else None
    pruned_cycles = {}
    for data_time, storm_records in sorted(cycles.items()):
        if not isinstance(storm_records, dict):
            continue
        keep_cycle = str(data_time) in active_data_times
        cycle_time = parse_utc_stamp(str(data_time))
        if cutoff is None or (cycle_time and cycle_time >= cutoff):
            keep_cycle = True
        if not keep_cycle:
            continue

        compact_records = {}
        for status_key, record in sorted(storm_records.items()):
            compact_record = compact_status_record(record)
            if compact_record:
                compact_records[status_key] = compact_record
        if compact_records:
            pruned_cycles[str(data_time)] = compact_records
    return {"cycles": pruned_cycles}


def current_render_signature() -> str:
    try:
        return hashlib.sha256((PROJECT_ROOT / "VTG.py").read_bytes()).hexdigest()
    except OSError:
        return ""


def previous_render_signature_matches(previous: dict, render_signature: str) -> bool:
    if not render_signature:
        return True
    metadata = previous.get("metadata")
    if not isinstance(metadata, dict):
        return False
    return metadata.get("render_signature") == render_signature


def previous_completed_for_target(previous: dict, complete_model_count: int, render_signature: str = "") -> bool:
    if not previous.get("completed"):
        return False
    if previous.get("atcf_match_method") == "position":
        return False
    if not previous_render_signature_matches(previous, render_signature):
        return False
    return metadata_model_count(previous.get("metadata")) >= complete_model_count


def is_final_check_window(now: datetime, window: CycleWindow, minutes: int) -> bool:
    if minutes <= 0:
        return False
    end = parse_utc_stamp(window.end_utc)
    if end is None:
        return False
    remaining = end - now
    return timedelta(0) < remaining <= timedelta(minutes=minutes)


def previous_final_check_done(previous: dict, window: CycleWindow) -> bool:
    return (
        previous.get("final_check_window_end_utc") == window.end_utc
        and bool(previous.get("final_checked_at_utc"))
    )


def build_manifest_inventory(output_root: Path, run_entries: list[dict]) -> list[dict]:
    entries_by_key: dict[str, dict] = {}
    suppressed_tokens: set[str] = set()
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
                tokens = manifest_suppression_tokens(metadata)
                suppressed_tokens.update(tokens)
                existing = entries_by_key.get(key)
                existing_metadata = existing.get("result", {}).get("metadata", {}) if isinstance(existing, dict) else {}
                if isinstance(existing_metadata, dict) and metadata_matches_suppression(existing_metadata, tokens):
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
            if metadata_matches_suppression(metadata, suppressed_tokens):
                continue
            if key in entries_by_key:
                existing_metadata = entries_by_key[key].get("result", {}).get("metadata", {})
                if isinstance(existing_metadata, dict):
                    existing_path = normalized_image_path(existing_metadata.get("image_path"))
                    scanned_path = normalized_image_path(metadata.get("image_path"))
                    if not existing_path or existing_path == scanned_path:
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
            tokens = manifest_suppression_tokens(metadata)
            suppressed_tokens.update(tokens)
            existing = entries_by_key.get(key)
            existing_metadata = existing.get("result", {}).get("metadata", {}) if isinstance(existing, dict) else {}
            if isinstance(existing_metadata, dict) and metadata_matches_suppression(existing_metadata, tokens):
                entries_by_key.pop(key, None)
            continue
        entries_by_key[key] = compact_manifest_entry(entry)

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
    parser.add_argument("--now", help="Override target cycle UTC, YYYYmmddHH. HH must be one of 00, 06, 12, 18.")
    parser.add_argument("--output-root", type=Path, default=PROJECT_ROOT / "VTG_IMG")
    parser.add_argument("--kma-cache-dir", type=Path, default=None)
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
    parser.add_argument("--final-check-before-window-end-minutes", type=int, default=10)
    parser.add_argument("--atcf-search-radius", type=int, default=None, help="Legacy symmetric ATCF search radius.")
    parser.add_argument("--atcf-search-positive-radius", type=int, default=DEFAULT_ATCF_SEARCH_POSITIVE_RADIUS)
    parser.add_argument("--atcf-search-negative-radius", type=int, default=DEFAULT_ATCF_SEARCH_NEGATIVE_RADIUS)
    parser.add_argument("--atcf-position-max-distance-km", type=float, default=DEFAULT_ATCF_POSITION_MAX_DISTANCE_KM)
    parser.add_argument("--atcf-position-min-distance-gap-km", type=float, default=DEFAULT_ATCF_POSITION_MIN_DISTANCE_GAP_KM)
    parser.add_argument("--index-only", action="store_true", help="Rebuild manifest inventory from existing PNG/metadata files and exit.")
    parser.add_argument("--check-run-needed", action="store_true", help="Only check whether image generation is needed and exit.")
    parser.add_argument("--github-output", type=Path, default=None, help="Optional GitHub Actions output file for --check-run-needed.")
    parser.add_argument("--force", action="store_true", help="Run even if a previous metadata record met the completion target.")
    parser.add_argument("--status-retention-days", type=int, default=DEFAULT_STATUS_RETENTION_DAYS, help="Keep compact automation status for this many days; use 0 to disable pruning.")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.now:
        cycle = parse_cycle_override(args.now)
        if cycle is None:
            raise SystemExit("--now must be target cycle YYYYmmddHH, with HH one of 00, 06, 12, 18.")
        now = cycle_probe_time(cycle)
        print(f"Cycle override: {format_utc_stamp(cycle)} -> window probe time {format_utc_stamp(now)}")
    else:
        now = utc_now()

    output_root = args.output_root
    kma_cache_dir = args.kma_cache_dir or output_root / "kma_apihub_cache"
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
            "final_check_before_window_end_minutes": args.final_check_before_window_end_minutes,
            "active_windows": [asdict(window) for window in windows],
            "runs": [],
            "inventory": build_manifest_inventory(output_root, []),
        }
        status_for_write = prune_status_for_persistence(
            status,
            active_data_times={window.data_time for window in windows},
            retention_days=args.status_retention_days,
            reference_time=utc_now(),
        )
        if not args.dry_run:
            write_json(manifest_path, manifest)
            if status_for_write != status:
                write_json(status_path, status_for_write)
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
        td_rows.extend(fetch_td_rows(year, args.auth_key, cache_dir=kma_cache_dir))
        typ_rows.extend(fetch_typ_rows(year, args.auth_key, cache_dir=kma_cache_dir))

    run_entries = []
    actual_run_count = 0
    render_signature = current_render_signature()
    for window in windows:
        cycle_status = status.setdefault("cycles", {}).setdefault(window.data_time, {})
        final_check_window = is_final_check_window(
            now,
            window,
            args.final_check_before_window_end_minutes,
        )
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
            resolve_atcf=not args.check_run_needed,
        )
        for job in jobs:
            due_hours: list[int] = []
            for fcst_hours in fcst_hours_list:
                status_key = status_key_for(job, fcst_hours)
                previous = cycle_status.get(status_key, {})
                previous_render_current = previous_render_signature_matches(previous, render_signature)
                previous_completed = previous_completed_for_target(
                    previous,
                    args.complete_model_count,
                    render_signature,
                )
                final_check_due = (
                    previous_completed
                    and final_check_window
                    and not previous_final_check_done(previous, window)
                )
                if previous_completed and not args.force and not final_check_due:
                    run_entries.append({
                        "job": asdict(job),
                        "window": asdict(window),
                        "result": {
                            "status": "skipped_completed",
                            "metadata": previous.get("metadata"),
                            "final_check_window": final_check_window,
                        },
                    })
                    continue
                previous_updated = parse_utc_stamp(previous.get("updated_at_utc", ""))
                if (
                    args.min_run_interval_minutes > 0
                    and previous_updated
                    and now - previous_updated < timedelta(minutes=args.min_run_interval_minutes)
                    and previous_render_current
                    and not args.force
                    and not final_check_due
                ):
                    run_entries.append({
                        "job": asdict(job),
                        "window": asdict(window),
                        "result": {
                            "status": "skipped_recent",
                            "metadata": previous.get("metadata"),
                            "final_check_window": final_check_window,
                        },
                    })
                    continue
                actual_run_count += 1
                if args.check_run_needed:
                    run_entries.append({
                        "job": asdict(job),
                        "window": asdict(window),
                        "result": {
                            "status": "planned",
                            "final_check_window": final_check_window,
                        },
                    })
                    continue
                due_hours.append(fcst_hours)

            if args.check_run_needed or not due_hours:
                continue

            batch_results = run_vtg_batch(
                job=job,
                output_root=output_root,
                auth_key=args.auth_key,
                python=args.python,
                fcst_hours_list=due_hours,
                auto_fcst_hours=args.auto_fcst_hours,
                source_overrides=args.source_override,
                dry_run=args.dry_run,
                clear_existing=args.force,
            )
            for fcst_hours in due_hours:
                status_key = status_key_for(job, fcst_hours)
                result = batch_results.get(fcst_hours, {
                    "status": "failed",
                    "metadata_path": str(metadata_path_for(output_root, job, fcst_hours)),
                    "stderr": "VTG batch run did not return a result for this forecast hour.",
                })
                log_failed_vtg_result(job, fcst_hours, result)
                metadata = result.get("metadata") or {}
                model_count = metadata_model_count(metadata)
                completed = model_count >= args.complete_model_count
                status_record = {
                    "updated_at_utc": format_utc_stamp(now),
                    "completed": completed,
                    "metadata": metadata,
                    "last_status": result.get("status"),
                    "atcf_id": job.atcf_id,
                    "atcf_match_method": job.atcf_match_method,
                    "reason": job.reason,
                }
                if final_check_window:
                    status_record["final_checked_at_utc"] = format_utc_stamp(now)
                    status_record["final_check_window_end_utc"] = window.end_utc
                cycle_status[status_key] = status_record
                run_entries.append({
                    "job": asdict(job),
                    "window": asdict(window),
                    "result": result,
                    "completed": completed,
                    "final_check": final_check_window,
                })

    if args.check_run_needed:
        run_needed = actual_run_count > 0
        payload = {
            "updated_at_utc": format_utc_stamp(now),
            "run_needed": run_needed,
            "deps_needed": run_needed,
            "run_step_needed": run_needed,
            "planned_run_count": actual_run_count,
            "active_windows": [asdict(window) for window in windows],
            "runs": run_entries,
        }
        write_github_outputs(args.github_output, {
            "run_needed": run_needed,
            "deps_needed": run_needed,
            "run_step_needed": run_needed,
            "planned_run_count": actual_run_count,
        })
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    previous_manifest = load_json(manifest_path, {})
    compact_runs = compact_manifest_runs(run_entries)
    inventory = build_manifest_inventory(output_root, run_entries)
    manifest = {
        "updated_at_utc": format_utc_stamp(now),
        "window_start_offset_hours": WINDOW_START_OFFSET_HOURS,
        "window_end_offset_hours": WINDOW_END_OFFSET_HOURS,
        "complete_model_count": args.complete_model_count,
        "final_check_before_window_end_minutes": args.final_check_before_window_end_minutes,
        "active_windows": [asdict(window) for window in windows],
        "runs": compact_runs,
        "inventory": inventory,
    }
    status_for_write = prune_status_for_persistence(
        status,
        active_data_times={window.data_time for window in windows},
        retention_days=args.status_retention_days,
        reference_time=utc_now(),
    )
    should_clear_previous_manifest = not run_entries and bool(previous_manifest.get("runs"))
    inventory_changed = previous_manifest.get("inventory") != manifest.get("inventory")
    status_changed = status_for_write != status
    should_write_outputs = not args.dry_run and (
        actual_run_count > 0 or should_clear_previous_manifest or inventory_changed or status_changed
    )
    if should_write_outputs:
        write_json(manifest_path, manifest)
        write_json(status_path, status_for_write)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
