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
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parent
KMA_LIST_BASE_URL = (os.getenv("KMA_APIHUB_BASE_URL") or "https://apihub-pub.kma.go.kr/api/typ01/url").rstrip("/")
KMA_FALLBACK_LIST_BASE_URL = (os.getenv("KMA_APIHUB_FALLBACK_BASE_URL") or "https://apihub.kma.go.kr/api/typ01/url").rstrip("/")
KMA_FALLBACK_AUTH_KEY = os.getenv("KMA_APIHUB_FALLBACK_AUTH_KEY", "").strip()
TD_LIST_ENDPOINT = "td_lst.php"
TYP_LIST_ENDPOINT = "typ_lst.php"
NRL_ATCF_SECTOR_URL = "https://science.nrlmry.navy.mil/geoips/tcdat/sectors/atcf_sector_file"
BDECK_SOURCE_URLS = (
    ("RAL.UCAR", "https://hurricanes.ral.ucar.edu/realtime/plots/{ral_basin_dir}/{year}/{atcf_id}/b{atcf_id}.dat"),
    ("NATYPHOON", "https://www.natyphoon.top/atcf/temp/b{atcf_id}.dat"),
)
KMA_GTS_NOW_URL = f"{KMA_LIST_BASE_URL}/typ_gts_now.php"
KMA_TYP_NOW_URL = f"{KMA_LIST_BASE_URL}/typ_now.php"
KMA_TD_NOW_URL = f"{KMA_LIST_BASE_URL}/td_now.php"
ACTIVE_MODEL_TARGET = 39
DEFAULT_ATCF_SEARCH_POSITIVE_RADIUS = 10
DEFAULT_ATCF_SEARCH_NEGATIVE_RADIUS = 5
DEFAULT_ATCF_POSITION_MAX_DISTANCE_KM = 600.0
DEFAULT_ATCF_POSITION_MIN_DISTANCE_GAP_KM = 100.0
DEFAULT_DATELINE_CANDIDATE_LONGITUDE_DEGREES = float(os.getenv("VTG_DATELINE_CANDIDATE_LONGITUDE_DEGREES", "170"))
# Rare cross-basin systems or known KMA/JTWC mapping exceptions.
# User manual map values still override these defaults.
BUILTIN_MANUAL_ATCF_MAP = {
    "2023:TYP08": "ep052023",  # Dora crossed the date line from the eastern Pacific.
    "DORA": "ep052023",
}
VALID_FCST_HOURS = (120, 240)
CYCLE_HOURS = (0, 6, 12, 18)
WINDOW_START_OFFSET_HOURS = 4
WINDOW_END_OFFSET_HOURS = 10
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
    "canonical_storm_key",
    "canonical_storm_stage",
    "canonical_typ_number",
    "canonical_typ_name",
    "canonical_typ_name_ko",
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
    "source_availability_path",
    "smca_aicon_snapshot_path",
    "no_output",
    "no_output_reason",
)
STATUS_METADATA_KEYS = MANIFEST_METADATA_KEYS + ("render_signature",)
HTTP_FETCH_CACHE_DIR: Path | None = None
HTTP_FETCH_CACHE_TTL_SECONDS = 6 * 3600
BDECK_TEXT_CACHE: dict[str, str | None] = {}
BDECK_SOURCE_TEXT_CACHE: dict[tuple[str, str], str | None] = {}
ATCF_SECTOR_ENTRIES_CACHE: list["AtcfSectorEntry"] | None = None
BDECK_FETCH_STATS = {
    "cache_hits": 0,
    "fetches": 0,
    "successes": 0,
    "missing": 0,
    "errors": 0,
    "fallbacks": 0,
}
DEFAULT_ATCF_POSITION_PARALLEL_WORKERS = max(1, int(os.getenv("ATCF_POSITION_PARALLEL_WORKERS", "6")))
DEFAULT_ATCF_POSITION_BDECK_TIMEOUT = float(os.getenv("ATCF_POSITION_BDECK_TIMEOUT", "10"))

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
    canonical_storm_stage: str
    canonical_typ_number: int | None
    canonical_typ_name: str
    canonical_typ_name_ko: str
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
class AtcfSectorEntry:
    atcf_id: str
    storm_name: str
    basin: str
    wind_kt: int | None
    pressure_hpa: int | None
    point: TrackPoint


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
    if stamp_year == year:
        return text

    month = int(text[4:6])
    # KMA list rows are keyed by season year (YY), but a storm can genuinely
    # cross New Year. Preserve only plausible adjacent-year boundary stamps:
    # late-year starts from YY-1 and early-year ends in YY+1. An adjacent year
    # in the middle of the year is treated as a source typo. This corrects the
    # 2022 TD02 row published as 202104090000-202104100000 while still keeping
    # legitimate Dec/Jan cross-year storms intact.
    plausible_cross_year = (
        (stamp_year == year - 1 and month >= 11)
        or (stamp_year == year + 1 and month <= 2)
    )
    if plausible_cross_year:
        return text
    return f"{year:04d}{text[4:]}"


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


def ceil_to_cycle_boundary(value: datetime) -> datetime:
    base = value.replace(minute=0, second=0, microsecond=0)
    if value.minute or value.second or value.microsecond:
        base += timedelta(hours=1)
    remainder = base.hour % 6
    if remainder:
        base += timedelta(hours=(6 - remainder))
    return base


def floor_to_cycle_boundary(value: datetime) -> datetime:
    base = value.replace(minute=0, second=0, microsecond=0)
    remainder = base.hour % 6
    if remainder:
        base -= timedelta(hours=remainder)
    return base


def active_at(now: datetime, start_text: str, end_text: str) -> bool:
    start = parse_utc_stamp(start_text)
    end = parse_utc_stamp(end_text)
    if start and now < start:
        return False
    if end and now > end:
        return False
    return True


def active_at_regular_cycle(cycle_time: datetime, start_text: str, end_text: str) -> bool:
    start = parse_utc_stamp(start_text)
    end = parse_utc_stamp(end_text)
    if start:
        start = ceil_to_cycle_boundary(start)
    if end:
        end = floor_to_cycle_boundary(end)
    if start and end and start > end:
        return False
    if start and cycle_time < start:
        return False
    if end and cycle_time > end:
        return False
    return True


def row_active_for_time(row: dict, *, probe_time: datetime, cycle_time: datetime | None = None) -> bool:
    if cycle_time is not None:
        return active_at_regular_cycle(cycle_time, row.get("TM_ST", ""), row.get("TM_ED", ""))
    return active_at(probe_time, row.get("TM_ST", ""), row.get("TM_ED", ""))


def fetch_text_cache_path(url: str) -> Path | None:
    if HTTP_FETCH_CACHE_DIR is None:
        return None
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
    return HTTP_FETCH_CACHE_DIR / "http" / f"{digest}.txt"


def read_fetch_text_cache(path: Path | None) -> str | None:
    if path is None or not path.exists():
        return None
    try:
        if HTTP_FETCH_CACHE_TTL_SECONDS > 0 and time.time() - path.stat().st_mtime > HTTP_FETCH_CACHE_TTL_SECONDS:
            return None
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def write_fetch_text_cache(path: Path | None, text: str) -> None:
    if path is None:
        return
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
        tmp_path.write_text(text, encoding="utf-8")
        tmp_path.replace(path)
    except OSError as exc:
        print(f"Warning: failed to write HTTP text cache {path}: {exc}")


def fetch_text(
    url: str,
    *,
    timeout: float = 12,
    retries: int = 2,
    retry_delay: float = 3.0,
    use_cache: bool = True,
) -> str:
    cache_path = fetch_text_cache_path(url) if use_cache else None
    cached = read_fetch_text_cache(cache_path)
    if cached is not None:
        return cached

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
        except (URLError, TimeoutError, OSError) as exc:
            last_error = exc
            if attempt >= retries:
                raise
        time.sleep(retry_delay)
    else:
        raise last_error or TimeoutError(f"request failed: {url}")

    for encoding in ("utf-8", "cp949", "euc-kr"):
        try:
            text = data.decode(encoding)
            write_fetch_text_cache(cache_path, text)
            return text
        except UnicodeDecodeError:
            continue
    text = data.decode("utf-8", errors="replace")
    write_fetch_text_cache(cache_path, text)
    return text


def should_try_kma_fallback(exc: Exception) -> bool:
    if isinstance(exc, HTTPError):
        return exc.code >= 500 or exc.code in {403, 408, 429}
    return isinstance(exc, (URLError, TimeoutError, OSError))


def fetch_kma_text(
    primary_url: str,
    fallback_url: str,
    *,
    label: str,
    timeout: float = 12,
    retries: int = 2,
    retry_delay: float = 3.0,
    use_cache: bool = True,
) -> str:
    try:
        return fetch_text(
            primary_url,
            timeout=timeout,
            retries=retries,
            retry_delay=retry_delay,
            use_cache=use_cache,
        )
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        if not fallback_url or not should_try_kma_fallback(exc):
            raise
        print(f"KMA APIHUB {label} primary endpoint failed ({exc}); trying fallback endpoint.")
        try:
            return fetch_text(
                fallback_url,
                timeout=timeout,
                retries=retries,
                retry_delay=retry_delay,
                use_cache=use_cache,
            )
        except (HTTPError, URLError, TimeoutError, OSError) as fallback_exc:
            print(f"KMA APIHUB {label} fallback endpoint failed ({fallback_exc}).")
            raise exc


def kma_endpoint_url(endpoint: str, *, base_url: str = KMA_LIST_BASE_URL) -> str:
    return f"{base_url.rstrip('/')}/{endpoint}"


def kma_list_url(endpoint: str, year: int, auth_key: str, *, base_url: str = KMA_LIST_BASE_URL) -> str:
    query = urlencode({
        "YY": year,
        "disp": "1",
        "help": "1",
        "authKey": auth_key,
    })
    return f"{kma_endpoint_url(endpoint, base_url=base_url)}?{query}"


def kma_gts_now_url(data_time: str, auth_key: str, *, mode: str = "2", base_url: str = KMA_LIST_BASE_URL) -> str:
    query = urlencode({
        "src": "",
        "tm": data_time,
        "mode": mode,
        "disp": "1",
        "help": "0",
        "authKey": auth_key,
    })
    return f"{kma_endpoint_url('typ_gts_now.php', base_url=base_url)}?{query}"


def kma_now_url(endpoint_url: str, data_time: str, auth_key: str, *, typ_number: int | None) -> str:
    query = urlencode({
        "src": "",
        "typ": "" if typ_number is None else str(int(typ_number)),
        "tm": data_time,
        "mode": "0",
        "disp": "1",
        "help": "0",
        "authKey": auth_key,
    })
    return f"{endpoint_url}?{query}"


def kma_now_fallback_url(endpoint_url: str, data_time: str, typ_number: int | None) -> str:
    if not KMA_FALLBACK_AUTH_KEY:
        return ""
    endpoint = endpoint_url.rsplit("/", 1)[-1]
    return kma_now_url(
        kma_endpoint_url(endpoint, base_url=KMA_FALLBACK_LIST_BASE_URL),
        data_time,
        KMA_FALLBACK_AUTH_KEY,
        typ_number=typ_number,
    )


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


def parse_kma_csv_any_lines(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for raw_line in str(text or "").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            parsed = next(csv.reader([line]))
        except csv.Error:
            continue
        if parsed and parsed[-1].strip() == "=":
            parsed = parsed[:-1]
        rows.append([value.strip() for value in parsed])
    return rows


def kma_cache_path(cache_dir: Path, endpoint: str, year: int) -> Path:
    return cache_dir / f"{Path(endpoint).stem}_{year}.json"


def kma_cache_asset_paths(cache_dir: Path, years: set[int]) -> list[Path]:
    return [
        path
        for year in sorted(years)
        for endpoint in (TD_LIST_ENDPOINT, TYP_LIST_ENDPOINT)
        if (path := kma_cache_path(cache_dir, endpoint, year)).exists()
    ]


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
        # Activity lists change whenever a TD forms or a storm changes stage.
        # The persisted parsed-row cache below is only an outage fallback; never
        # let the generic HTTP cache hide a newly issued system for up to 6 hours.
        return fetch_kma_text(
            kma_list_url(endpoint, year, auth_key),
            kma_list_url(endpoint, year, KMA_FALLBACK_AUTH_KEY, base_url=KMA_FALLBACK_LIST_BASE_URL)
            if KMA_FALLBACK_AUTH_KEY else "",
            label=f"{Path(endpoint).stem} {year}",
            timeout=20,
            retries=2,
            retry_delay=5.0,
            use_cache=False,
        )
    except HTTPError as exc:
        if exc.code < 500:
            raise
        print(f"KMA APIHUB {Path(endpoint).stem} {year} failed with HTTP {exc.code}; trying cached rows.")
        return None
    except (URLError, TimeoutError, OSError) as exc:
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


def normalize_kma_now_time(value: str) -> str:
    text = str(value or "").strip().split(".", 1)[0]
    if len(text) >= 12 and text[:12].isdigit():
        return text[:12]
    if len(text) >= 10 and text[:10].isdigit():
        return f"{text[:10]}00"
    return ""


def kma_now_row_numbers(row: list[str]) -> set[int]:
    numbers: set[int] = set()
    for value in row[:6]:
        number = safe_int(str(value or "").strip().split(".", 1)[0])
        if number is not None and 1 <= number <= 99:
            numbers.add(number)
    return numbers


def kma_now_row_time(row: list[str], data_time: str) -> str:
    target = normalize_kma_now_time(data_time)
    for value in row:
        time_text = normalize_kma_now_time(value)
        if time_text and time_text[:10] == target[:10]:
            return time_text
    return ""


def kma_now_row_lat_lon(row: list[str]) -> tuple[float, float] | None:
    pairs = [(7, 8), (5, 6), (4, 5), (6, 7), (8, 9)]
    pairs.extend((index, index + 1) for index in range(max(0, len(row) - 1)))
    seen: set[tuple[int, int]] = set()
    for lat_index, lon_index in pairs:
        if (lat_index, lon_index) in seen or lon_index >= len(row):
            continue
        seen.add((lat_index, lon_index))
        lat = safe_float(row[lat_index])
        lon = safe_float(row[lon_index])
        if lat is None or lon is None:
            continue
        if -90.0 <= lat <= 90.0 and 0.0 <= lon <= 360.0:
            return lat, lon
    return None


def kma_now_point_from_text(
    text: str | None,
    *,
    data_time: str,
    typ_number: int | None,
    require_number_match: bool,
) -> TrackPoint | None:
    if not text or "NODATA" in text.upper():
        return None
    target_number = int(typ_number) if typ_number else None
    for row in parse_kma_csv_any_lines(text):
        time_utc = kma_now_row_time(row, data_time)
        if not time_utc:
            continue
        if target_number is not None:
            row_numbers = kma_now_row_numbers(row)
            if row_numbers and target_number not in row_numbers:
                continue
            if require_number_match and target_number not in row_numbers:
                continue
        lat_lon = kma_now_row_lat_lon(row)
        if lat_lon is None:
            continue
        lat, lon = lat_lon
        return TrackPoint(time_utc=time_utc, lat=lat, lon=lon)
    return None


def kma_now_endpoint_candidates(
    *,
    typ_number: int,
    stage: str | None,
) -> list[tuple[str, str, int | None, int | None]]:
    candidates: list[tuple[str, str, int | None, int | None]] = []
    seen: set[tuple[str, int | None, int | None]] = set()

    def add(label: str, endpoint: str, query_number: int | None, filter_number: int | None = None) -> None:
        query_value = int(query_number) if query_number else None
        filter_value = int(filter_number) if filter_number else query_value
        if query_value is None and filter_value is None:
            return
        key = (endpoint, query_value, filter_value)
        if key in seen:
            return
        seen.add(key)
        candidates.append((label, endpoint, query_value, filter_value))

    stage_text = str(stage or "").strip().upper()
    if stage_text == "TD":
        add("td_now", KMA_TD_NOW_URL, typ_number)
        add("typ_now", KMA_TYP_NOW_URL, typ_number)
    else:
        add("typ_now", KMA_TYP_NOW_URL, typ_number)
        add("td_now", KMA_TD_NOW_URL, typ_number)
    add("typ_now", KMA_TYP_NOW_URL, None, typ_number)
    add("td_now", KMA_TD_NOW_URL, None, typ_number)
    return candidates


def fetch_kma_now_reference_point(
    *,
    typ_number: int,
    data_time: str,
    auth_key: str,
    stage: str | None,
) -> TrackPoint | None:
    for label, endpoint, query_number, filter_number in kma_now_endpoint_candidates(typ_number=typ_number, stage=stage):
        try:
            text = fetch_kma_text(
                kma_now_url(endpoint, data_time, auth_key, typ_number=query_number),
                kma_now_fallback_url(endpoint, data_time, query_number),
                label=label,
                timeout=15,
                retries=1,
                retry_delay=3.0,
            )
        except (HTTPError, URLError, TimeoutError, OSError):
            continue
        point = kma_now_point_from_text(
            text,
            data_time=data_time,
            typ_number=filter_number,
            require_number_match=query_number is None,
        )
        if point is None:
            continue
        number_label = "all" if query_number is None else f"{query_number:02d}"
        print(
            "KMA 0h reference point is missing from typ_gts_now; using "
            f"{label} mode=0 analysis point ({number_label}): "
            f"{point.lat:.2f}N, {point.lon:.2f}E."
        )
        return point
    return None


def kma_gts_row_source(row: list[str]) -> str:
    # typ_gts_now columns follow KMA_COLUMNS:
    # ... 15D(index 16), 15R(index 17), SRC(index 18), trailing blank(index 19).
    # Older cached/debug rows may omit the final blank column, but SRC should
    # still be index 18. Only fall back to index 17 when the source column is
    # genuinely absent.
    if len(row) > 18:
        return str(row[18] or "").strip().upper()
    if len(row) > 17:
        return str(row[17] or "").strip().upper()
    return ""


def is_apihub_model_zero_source(source: str) -> bool:
    source_text = str(source or "").strip().upper()
    return bool(source_text and source_text != "KMA")


def mean_track_point(points: list[TrackPoint], *, time_utc: str) -> TrackPoint | None:
    if not points:
        return None
    lat = sum(point.lat for point in points) / len(points)
    lon = sum(point.lon for point in points) / len(points)
    return TrackPoint(time_utc=time_utc, lat=lat, lon=lon)


def fetch_kma_reference_point(
    *,
    typ_number: int,
    data_time: str,
    auth_key: str,
    gts_text: str | None = None,
    stage: str | None = None,
) -> TrackPoint | None:
    if gts_text is None:
        try:
            text = fetch_kma_text(
                kma_gts_now_url(data_time, auth_key),
                kma_gts_now_url(data_time, KMA_FALLBACK_AUTH_KEY, base_url=KMA_FALLBACK_LIST_BASE_URL)
                if KMA_FALLBACK_AUTH_KEY else "",
                label="typ_gts_now mode=2",
                timeout=15,
                retries=1,
                retry_delay=3.0,
            )
        except (HTTPError, URLError, TimeoutError, OSError):
            text = ""
    else:
        text = gts_text

    model_zero_points: list[TrackPoint] = []
    unlabeled_zero_points: list[TrackPoint] = []
    for row in parse_kma_csv_lines(text or "", fixed_columns=19):
        if safe_int(row[2]) != typ_number:
            continue
        tmd = safe_int(row[4])
        if tmd != 0:
            continue
        lat = safe_float(row[7])
        lon = safe_float(row[8])
        ft_time = row[6].strip() if len(row) > 6 else ""
        source = kma_gts_row_source(row)
        if lat is None or lon is None or not ft_time:
            continue
        if ft_time[:10] != data_time[:10]:
            continue
        point = TrackPoint(time_utc=ft_time, lat=lat, lon=lon)
        if source == "KMA":
            return point
        if is_apihub_model_zero_source(source):
            model_zero_points.append(point)
        else:
            unlabeled_zero_points.append(point)

    mean_point = mean_track_point(model_zero_points, time_utc=f"{data_time[:10]}00")
    if mean_point is not None:
        print(
            "KMA 0h reference point is missing from typ_gts_now; using the mean of "
            f"{len(model_zero_points)} APIHUB model 0h point(s): "
            f"{mean_point.lat:.2f}N, {mean_point.lon:.2f}E."
        )
        return mean_point

    mean_point = mean_track_point(unlabeled_zero_points, time_utc=f"{data_time[:10]}00")
    if mean_point is not None:
        print(
            "KMA 0h reference point is missing from typ_gts_now; using the mean of "
            f"{len(unlabeled_zero_points)} unlabeled 0h point(s): "
            f"{mean_point.lat:.2f}N, {mean_point.lon:.2f}E."
        )
        return mean_point

    return fetch_kma_now_reference_point(
        typ_number=typ_number,
        data_time=data_time,
        auth_key=auth_key,
        stage=stage,
    )


def normalize_name(value: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(value or "").upper())


ATCF_SECTOR_BASIN_CODES = {
    "W": "wp",
    "E": "ep",
    "C": "cp",
    "L": "al",
    "A": "io",
    "B": "io",
    "S": "sh",
    "P": "sh",
}


def parse_atcf_sector_coord(value: str) -> float | None:
    text = str(value or "").strip().upper()
    match = re.fullmatch(r"(\d+(?:\.\d+)?)([NSEW])", text)
    if not match:
        return None
    coord = float(match.group(1))
    if match.group(2) in {"S", "W"}:
        coord = -coord
    return coord


def parse_atcf_sector_file(text: str) -> list[AtcfSectorEntry]:
    entries: list[AtcfSectorEntry] = []
    for raw_line in str(text or "").splitlines():
        fields = raw_line.split()
        if len(fields) < 9:
            continue
        storm_token = fields[0].upper()
        storm_match = re.fullmatch(r"(\d{2})([A-Z])", storm_token)
        if not storm_match or not re.fullmatch(r"\d{6}", fields[2]) or not re.fullmatch(r"\d{4}", fields[3]):
            continue
        basin_code = ATCF_SECTOR_BASIN_CODES.get(storm_match.group(2))
        if not basin_code:
            continue
        lat = parse_atcf_sector_coord(fields[4])
        lon = parse_atcf_sector_coord(fields[5])
        if lat is None or lon is None:
            continue
        timestamp = f"{fields[2]}{fields[3]}"
        point_time = parse_utc_stamp(f"20{timestamp}")
        if point_time is None:
            continue
        year = point_time.year
        entries.append(AtcfSectorEntry(
            atcf_id=f"{basin_code}{storm_match.group(1)}{year}",
            storm_name=fields[1].strip().upper(),
            basin=fields[6].strip().upper(),
            wind_kt=safe_int(fields[7]),
            pressure_hpa=safe_int(fields[8]),
            point=TrackPoint(time_utc=format_utc_stamp(point_time), lat=lat, lon=lon),
        ))
    return entries


def fetch_atcf_sector_entries() -> list[AtcfSectorEntry]:
    global ATCF_SECTOR_ENTRIES_CACHE
    if ATCF_SECTOR_ENTRIES_CACHE is not None:
        return ATCF_SECTOR_ENTRIES_CACHE
    try:
        text = fetch_text(
            NRL_ATCF_SECTOR_URL,
            timeout=8,
            retries=0,
            use_cache=False,
        )
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        print(f"Warning: failed to fetch NRL ATCF sector file: {exc}")
        ATCF_SECTOR_ENTRIES_CACHE = []
        return ATCF_SECTOR_ENTRIES_CACHE
    ATCF_SECTOR_ENTRIES_CACHE = parse_atcf_sector_file(text)
    if not ATCF_SECTOR_ENTRIES_CACHE:
        print("Warning: NRL ATCF sector file contained no usable entries.")
    else:
        print(f"Loaded {len(ATCF_SECTOR_ENTRIES_CACHE)} active ATCF sector entries from NRL.")
    return ATCF_SECTOR_ENTRIES_CACHE


RAL_UCAR_BASIN_DIRS = {
    "al": "northatlantic",
    "cp": "northcentralpacific",
    "ep": "northeastpacific",
    "io": "northindian",
    "sh": "southernhemisphere",
    "wp": "northwestpacific",
}


def ral_ucar_basin_dir(atcf_id: str) -> str:
    return RAL_UCAR_BASIN_DIRS.get(str(atcf_id or "").strip().lower()[:2], "northwestpacific")


def normalized_longitude(lon: float) -> float:
    return ((float(lon) + 180.0) % 360.0) - 180.0


def is_near_dateline(point: TrackPoint | None) -> bool:
    if point is None:
        return False
    return abs(normalized_longitude(point.lon)) >= DEFAULT_DATELINE_CANDIDATE_LONGITUDE_DEGREES


def central_pacific_dateline_candidate_ids(year: int) -> list[str]:
    return [
        *(f"cp{candidate_number:02d}{year}" for candidate_number in range(90, 100)),
        *(f"cp{candidate_number:02d}{year}" for candidate_number in range(1, 10)),
    ]


def extend_td_atcf_ids_for_dateline(atcf_ids: list[str], *, year: int, kma_point: TrackPoint | None) -> list[str]:
    if not is_near_dateline(kma_point):
        return atcf_ids

    ids: list[str] = []
    seen: set[str] = set()
    for atcf_id in [*atcf_ids, *central_pacific_dateline_candidate_ids(year)]:
        normalized = str(atcf_id or "").strip().lower()
        if normalized and normalized not in seen:
            seen.add(normalized)
            ids.append(normalized)
    print(
        "KMA reference point is near the date line; adding Central Pacific ATCF "
        f"candidates cp90-cp99 and cp01-cp09 for {year}."
    )
    return ids


def atcf_sector_entries_for_year(
    entries: list[AtcfSectorEntry],
    year: int,
    *,
    include_central_pacific: bool = False,
) -> list[AtcfSectorEntry]:
    # KMA TD/TYP products handled here are western North Pacific systems.
    # Date-line TD exceptions may keep Central Pacific ATCF IDs after entering
    # the western Pacific.
    prefixes = ("wp", "cp") if include_central_pacific else ("wp",)
    return [
        entry
        for entry in entries
        if entry.atcf_id.startswith(prefixes)
        and (point_time := parse_utc_stamp(entry.point.time_utc)) is not None
        and abs(point_time.year - year) <= 1
    ]


def atcf_sector_entries_for_cycle(
    entries: list[AtcfSectorEntry],
    year: int,
    data_time: str,
    *,
    include_central_pacific: bool = False,
) -> list[AtcfSectorEntry]:
    target_dt = parse_utc_stamp(data_time)
    if target_dt is None:
        return []
    target_time = format_utc_stamp(target_dt)
    return [
        entry
        for entry in atcf_sector_entries_for_year(
            entries,
            year,
            include_central_pacific=include_central_pacific,
        )
        if entry.point.time_utc == target_time
    ]


def atcf_sector_id_for_year(entry: AtcfSectorEntry, year: int) -> str:
    return f"{entry.atcf_id[:4]}{year}"


def find_atcf_sector_name_match(
    entries: list[AtcfSectorEntry],
    *,
    typ_en: str,
    year: int,
    data_time: str,
    preferred_atcf_id: str | None = None,
) -> AtcfMatch | None:
    target_name = normalize_name(typ_en)
    if not target_name:
        return None
    candidates = [
        entry
        for entry in atcf_sector_entries_for_cycle(entries, year, data_time)
        if normalize_name(entry.storm_name) == target_name
    ]
    if not candidates:
        return None
    preferred_id = str(preferred_atcf_id or "").strip().lower()
    candidates.sort(
        key=lambda entry: (
            atcf_sector_id_for_year(entry, year) != preferred_id,
            entry.point.time_utc,
        )
    )
    selected = candidates[0] if preferred_id and atcf_sector_id_for_year(candidates[0], year) == preferred_id else max(
        candidates,
        key=lambda entry: entry.point.time_utc,
    )
    selected_atcf_id = atcf_sector_id_for_year(selected, year)
    print(
        f"Matched {typ_en} to {selected_atcf_id} from NRL ATCF sector file "
        f"({selected.point.time_utc[:10]})."
    )
    return AtcfMatch(
        atcf_id=selected_atcf_id,
        method="sector_name",
        point=selected.point,
    )


def find_atcf_sector_position_match(
    entries: list[AtcfSectorEntry],
    *,
    year: int,
    data_time: str,
    kma_point: TrackPoint | None,
    preferred_atcf_id: str | None = None,
    max_distance_km: float = DEFAULT_ATCF_POSITION_MAX_DISTANCE_KM,
    min_distance_gap_km: float = DEFAULT_ATCF_POSITION_MIN_DISTANCE_GAP_KM,
) -> AtcfMatch | None:
    if kma_point is None:
        return None
    matches: list[AtcfMatch] = []
    for entry in atcf_sector_entries_for_cycle(
        entries,
        year,
        data_time,
        include_central_pacific=is_near_dateline(kma_point),
    ):
        distance = haversine_km(kma_point.lat, kma_point.lon, entry.point.lat, entry.point.lon)
        if distance <= max_distance_km:
            matches.append(AtcfMatch(
                atcf_id=atcf_sector_id_for_year(entry, year),
                method="sector_position",
                distance_km=distance,
                point=entry.point,
                reference_point=kma_point,
            ))
    if not matches:
        return None
    matches.sort(key=atcf_match_distance)
    selected = matches[0]
    if len(matches) > 1 and atcf_match_distance(matches[1]) - atcf_match_distance(selected) < min_distance_gap_km:
        near_matches = [
            item
            for item in matches
            if atcf_match_distance(item) - atcf_match_distance(selected) < min_distance_gap_km
        ]
        preferred_id = str(preferred_atcf_id or "").strip().lower()
        preferred = next((item for item in near_matches if item.atcf_id == preferred_id), None)
        regular = [item for item in near_matches if not is_invest_atcf_id(item.atcf_id)]
        if preferred is not None:
            selected = preferred
        elif len(regular) == 1:
            selected = regular[0]
        else:
            print(
                "NRL ATCF sector position match is ambiguous: "
                + ", ".join(f"{item.atcf_id}:{atcf_match_distance(item):.1f}km" for item in matches[:4])
            )
            return None
    print(
        f"Matched KMA reference point to {selected.atcf_id} from NRL ATCF sector file "
        f"({atcf_match_distance(selected):.1f} km)."
    )
    return selected


def is_atcf_position_match(match: AtcfMatch | None) -> bool:
    return bool(match and match.method in {"position", "sector_position"})


def ordered_regular_atcf_offsets() -> tuple[list[int], list[int]]:
    # Fast path requested for KMA/JTWC number drift:
    # exact -> +1..+5 -> -1..-3, then wider +6..+10 -> -4..-5.
    return [0, 1, 2, 3, 4, 5, -1, -2, -3], [6, 7, 8, 9, 10, -4, -5]


def make_atcf_ids_from_offsets(*, base_number: int, year: int, offsets: list[int], regular_only: bool = True) -> list[str]:
    ids: list[str] = []
    seen: set[str] = set()

    def add(candidate_number: int) -> None:
        if regular_only and not (1 <= candidate_number <= 89):
            return
        if not regular_only and not (1 <= candidate_number <= 99):
            return
        atcf_id = f"wp{candidate_number:02d}{year}"
        if atcf_id not in seen:
            seen.add(atcf_id)
            ids.append(atcf_id)

    for offset in offsets:
        add(base_number + offset)
    return ids


def candidate_atcf_ids(*, typ_number: int, year: int, positive_radius: int, negative_radius: int) -> list[str]:
    # For named typhoons, search regular ATCF IDs only. Do not scan wp90..wp99
    # because active TYP systems should already have regular JTWC numbers.
    first_offsets, second_offsets = ordered_regular_atcf_offsets()
    return make_atcf_ids_from_offsets(
        base_number=typ_number,
        year=year,
        offsets=first_offsets + second_offsets,
        regular_only=True,
    )


def candidate_td_atcf_ids(*, td_number: int, year: int, linked_typ_number: int | None = None) -> list[str]:
    # For KMA TD systems, prefer the linked future/active TYP number when it is
    # already known. Otherwise, the best regular-ID first guess is TD/2 rounded
    # up. TD can still be an invest in JTWC, so scan wp90..wp99 before looking
    # at lower regular numbers.
    base_number = linked_typ_number if linked_typ_number else math.ceil(td_number / 2)
    base_number = max(1, min(89, int(base_number)))

    groups = (
        make_atcf_ids_from_offsets(
            base_number=base_number,
            year=year,
            offsets=[0, 1, 2, 3, 4, 5],
            regular_only=True,
        ),
        [f"wp{candidate_number:02d}{year}" for candidate_number in range(90, 100)],
        make_atcf_ids_from_offsets(
            base_number=base_number,
            year=year,
            offsets=[-1, -2, -3],
            regular_only=True,
        ),
        make_atcf_ids_from_offsets(
            base_number=base_number,
            year=year,
            offsets=[6, 7, 8, 9, 10],
            regular_only=True,
        ),
        make_atcf_ids_from_offsets(
            base_number=base_number,
            year=year,
            offsets=[-4, -5],
            regular_only=True,
        ),
    )

    ids: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for atcf_id in group:
            if atcf_id not in seen:
                seen.add(atcf_id)
                ids.append(atcf_id)
    return ids


def atcf_storm_number(atcf_id: str) -> int | None:
    match = re.fullmatch(r"[a-z]{2}(\d{2})\d{4}", str(atcf_id or "").strip().lower())
    if not match:
        return None
    return int(match.group(1))


def regular_atcf_storm_number(atcf_id: str) -> int | None:
    number = atcf_storm_number(atcf_id)
    if number is None or not (1 <= number <= 89):
        return None
    return number


def typ_row_for_number(typ_rows: list[dict], *, year: int | str, typ_number: int | None) -> dict | None:
    if not typ_number:
        return None
    year_int = safe_int(year)
    if year_int is None:
        return None
    for row in typ_rows or []:
        if safe_int(row.get("YY")) == year_int and safe_int(row.get("SEQ")) == typ_number:
            return row
    return None


def typ_identity_from_row(row: dict | None) -> tuple[str, str, datetime | None]:
    if not isinstance(row, dict):
        return "", "", None
    typ_en = str(row.get("TYP_EN") or "").strip().upper()
    typ_name_ko = str(row.get("TYP_NAME") or "").strip()
    typ_start = parse_utc_stamp(str(row.get("TM_ST") or ""))
    return typ_en, typ_name_ko, typ_start


def typ_link_payload(typ_number: int, typ_row: dict | None) -> dict:
    typ_en, typ_name_ko, _ = typ_identity_from_row(typ_row)
    return {
        "linked_typ_number": typ_number,
        "canonical_typ_number": typ_number,
        "canonical_typ_name": typ_en or typ_name_ko or "NONAME",
        "canonical_typ_name_ko": typ_name_ko,
    }


def is_invest_atcf_id(atcf_id: str) -> bool:
    number = atcf_storm_number(atcf_id)
    return number is not None and 90 <= number <= 99


def atcf_match_distance(match: AtcfMatch) -> float:
    return match.distance_km if match.distance_km is not None else float("inf")


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


def bdeck_source_slug(source: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(source or "").lower()).strip("_") or "source"


def bdeck_missing_cache_path(atcf_id: str, *, source: str = "NOAA") -> Path | None:
    if HTTP_FETCH_CACHE_DIR is None:
        return None
    return HTTP_FETCH_CACHE_DIR / "bdeck_missing" / bdeck_source_slug(source) / f"{atcf_id.lower()}.missing"


def read_bdeck_missing_cache(path: Path | None) -> bool:
    if path is None or not path.exists():
        return False
    try:
        if HTTP_FETCH_CACHE_TTL_SECONDS > 0 and time.time() - path.stat().st_mtime > HTTP_FETCH_CACHE_TTL_SECONDS:
            return False
        return True
    except OSError:
        return False


def write_bdeck_missing_cache(path: Path | None, reason: str) -> None:
    if path is None:
        return
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(reason + "\n", encoding="utf-8")
    except OSError:
        pass


def fetch_bdeck_text_from_source(
    atcf_id: str,
    *,
    source: str,
    url_template: str,
    timeout: float = 15,
) -> str | None:
    normalized = str(atcf_id or "").strip().lower()
    if not normalized:
        return None
    cache_key = (source, normalized)
    if cache_key in BDECK_SOURCE_TEXT_CACHE:
        BDECK_FETCH_STATS["cache_hits"] += 1
        return BDECK_SOURCE_TEXT_CACHE[cache_key]

    missing_path = bdeck_missing_cache_path(normalized, source=source)
    if read_bdeck_missing_cache(missing_path):
        BDECK_FETCH_STATS["cache_hits"] += 1
        BDECK_FETCH_STATS["missing"] += 1
        BDECK_SOURCE_TEXT_CACHE[cache_key] = None
        return None

    try:
        BDECK_FETCH_STATS["fetches"] += 1
        text = fetch_text(
            url_template.format(
                atcf_id=normalized,
                year=normalized[-4:],
                ral_basin_dir=ral_ucar_basin_dir(normalized),
            ),
            timeout=timeout,
        )
    except HTTPError as exc:
        if 400 <= exc.code < 500:
            BDECK_FETCH_STATS["missing"] += 1
            write_bdeck_missing_cache(missing_path, f"HTTP {exc.code}")
        else:
            BDECK_FETCH_STATS["errors"] += 1
        BDECK_SOURCE_TEXT_CACHE[cache_key] = None
        return None
    except (URLError, TimeoutError):
        BDECK_FETCH_STATS["errors"] += 1
        BDECK_SOURCE_TEXT_CACHE[cache_key] = None
        return None

    BDECK_FETCH_STATS["successes"] += 1
    BDECK_SOURCE_TEXT_CACHE[cache_key] = text
    return text


def fetch_bdeck_text(atcf_id: str, *, timeout: float = 15) -> str | None:
    normalized = str(atcf_id or "").strip().lower()
    if not normalized:
        return None
    if normalized in BDECK_TEXT_CACHE:
        BDECK_FETCH_STATS["cache_hits"] += 1
        return BDECK_TEXT_CACHE[normalized]

    for index, (source, url_template) in enumerate(BDECK_SOURCE_URLS):
        text = fetch_bdeck_text_from_source(
            normalized,
            source=source,
            url_template=url_template,
            timeout=timeout,
        )
        if text:
            if index > 0:
                BDECK_FETCH_STATS["fallbacks"] += 1
                earlier_sources = ", ".join(item[0] for item in BDECK_SOURCE_URLS[:index])
                print(f"BDECK {earlier_sources} source unavailable; using {source} for {normalized}.")
            BDECK_TEXT_CACHE[normalized] = text
            return text

    BDECK_TEXT_CACHE[normalized] = None
    return None


def fetch_bdeck_text_for_reference_time(
    atcf_id: str,
    *,
    reference_time: str,
    timeout: float = 15,
) -> str | None:
    normalized = str(atcf_id or "").strip().lower()
    if not normalized:
        return None

    nearest_fallback: tuple[str, str] | None = None
    for index, (source, url_template) in enumerate(BDECK_SOURCE_URLS):
        text = fetch_bdeck_text_from_source(
            normalized,
            source=source,
            url_template=url_template,
            timeout=timeout,
        )
        if not text:
            continue
        if nearest_fallback is None:
            nearest_fallback = (text, source)
        if not bdeck_track_points(text, reference_time=reference_time):
            continue
        if index > 0:
            BDECK_FETCH_STATS["fallbacks"] += 1
            earlier_sources = ", ".join(item[0] for item in BDECK_SOURCE_URLS[:index])
            print(
                f"BDECK {earlier_sources} source lacks an exact {reference_time[:10]} "
                f"analysis point; using {source} for {normalized}."
            )
        BDECK_TEXT_CACHE[normalized] = text
        return text

    if nearest_fallback is not None:
        text = nearest_fallback[0]
        BDECK_TEXT_CACHE[normalized] = text
        return text

    BDECK_TEXT_CACHE[normalized] = None
    return None


def fetch_bdeck_text_for_data_time(atcf_id: str, *, data_time: str, timeout: float = 15) -> str | None:
    return fetch_bdeck_text_for_reference_time(
        atcf_id,
        reference_time=f"{data_time[:10]}00",
        timeout=timeout,
    )


def bdeck_stats_snapshot() -> dict[str, int]:
    return dict(BDECK_FETCH_STATS)


def bdeck_stats_delta(before: dict[str, int]) -> dict[str, int]:
    return {key: BDECK_FETCH_STATS.get(key, 0) - before.get(key, 0) for key in BDECK_FETCH_STATS}


def bdeck_all_tau0_points(text: str) -> list[TrackPoint]:
    points: list[TrackPoint] = []
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
        if safe_int(row[5]) != 0:
            continue
        time_text = str(row[2] or "").strip()
        if not re.fullmatch(r"\d{10}", time_text):
            continue
        lat = parse_atcf_coord(row[6])
        lon = parse_atcf_coord(row[7])
        if lat is None or lon is None:
            continue
        points.append(TrackPoint(time_utc=f"{time_text}00", lat=lat, lon=lon))
    return points


def bdeck_nearest_track_point(text: str, *, data_time: str, max_offset_hours: int = 12) -> TrackPoint | None:
    target_dt = parse_utc_stamp(f"{data_time[:10]}00")
    if target_dt is None:
        return None
    best: tuple[float, TrackPoint] | None = None
    for point in bdeck_all_tau0_points(text):
        point_dt = parse_utc_stamp(point.time_utc)
        if point_dt is None:
            continue
        offset_hours = abs((point_dt - target_dt).total_seconds()) / 3600.0
        if offset_hours > max_offset_hours:
            continue
        if best is None or offset_hours < best[0]:
            best = (offset_hours, point)
    return best[1] if best else None


def fetch_bdeck_analysis_point(atcf_id: str, *, data_time: str) -> TrackPoint | None:
    text = fetch_bdeck_text_for_data_time(atcf_id, data_time=data_time, timeout=15)
    if not text:
        return None
    points = bdeck_track_points(text, reference_time=f"{data_time[:10]}00")
    if points:
        return points[0]
    nearest = bdeck_nearest_track_point(text, data_time=data_time, max_offset_hours=12)
    if nearest:
        print(
            "BDECK exact 0h analysis point missing; using nearest point "
            f"{nearest.time_utc} for {atcf_id} at {data_time}."
        )
    return nearest


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
    atcf_ids: list[str] | None = None,
) -> AtcfMatch | None:
    target_name = normalize_name(typ_en)
    if not target_name:
        return None

    if atcf_ids is None:
        atcf_ids = candidate_atcf_ids(
            typ_number=typ_number,
            year=year,
            positive_radius=positive_radius,
            negative_radius=negative_radius,
        )

    for atcf_id in atcf_ids:
        text = fetch_bdeck_text(atcf_id, timeout=15)
        if not text:
            continue
        if target_name in normalize_name(text):
            return AtcfMatch(atcf_id=atcf_id, method="name")
    return None


def fetch_bdeck_texts_parallel(
    atcf_ids: list[str],
    *,
    reference_time: str | None = None,
    timeout: float = DEFAULT_ATCF_POSITION_BDECK_TIMEOUT,
    max_workers: int = DEFAULT_ATCF_POSITION_PARALLEL_WORKERS,
) -> dict[str, str | None]:
    unique_ids: list[str] = []
    seen: set[str] = set()
    for atcf_id in atcf_ids:
        normalized = str(atcf_id or "").strip().lower()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        unique_ids.append(normalized)

    if not unique_ids:
        return {}
    fetcher = fetch_bdeck_text_for_reference_time if reference_time else fetch_bdeck_text
    if max_workers <= 1 or len(unique_ids) == 1:
        return {
            atcf_id: (
                fetcher(atcf_id, reference_time=reference_time, timeout=timeout)
                if reference_time
                else fetcher(atcf_id, timeout=timeout)
            )
            for atcf_id in unique_ids
        }

    results: dict[str, str | None] = {}
    worker_count = min(max_workers, len(unique_ids))
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = {
            executor.submit(
                fetcher,
                atcf_id,
                **({"reference_time": reference_time} if reference_time else {}),
                timeout=timeout,
            ): atcf_id
            for atcf_id in unique_ids
        }
        for future in as_completed(futures):
            atcf_id = futures[future]
            try:
                results[atcf_id] = future.result()
            except Exception as exc:
                BDECK_FETCH_STATS["errors"] = BDECK_FETCH_STATS.get("errors", 0) + 1
                print(f"Warning: parallel BDECK fetch failed for {atcf_id}: {exc}", file=sys.stderr)
                results[atcf_id] = None
    return results


def format_atcf_position_candidate(match: AtcfMatch) -> str:
    distance = match.distance_km if match.distance_km is not None else float("inf")
    point = match.point
    if point is None:
        return f"{match.atcf_id}:{distance:.1f}km"
    return (
        f"{match.atcf_id}:{distance:.1f}km "
        f"({point.lat:.2f}N,{point.lon:.2f}E {point.time_utc[:10]})"
    )


def log_atcf_position_diagnostics(
    *,
    data_time: str,
    kma_point: TrackPoint,
    ordered_ids: list[str],
    all_matches: list[AtcfMatch],
    candidates: list[AtcfMatch],
    max_distance_km: float,
    min_distance_gap_km: float,
    preferred_atcf_id: str | None,
    reason: str,
) -> None:
    checked_count = len(ordered_ids)
    bdeck_point_count = len(all_matches)
    print(
        "ATCF position diagnostics: "
        f"data_time={data_time} "
        f"reference={kma_point.lat:.2f}N,{kma_point.lon:.2f}E "
        f"time={kma_point.time_utc[:10]} "
        f"checked_ids={checked_count} "
        f"bdeck_0h_points={bdeck_point_count} "
        f"within_{max_distance_km:.0f}km={len(candidates)} "
        f"preferred={str(preferred_atcf_id or '').strip().lower() or '-'} "
        f"result={reason}."
    )
    if not all_matches:
        print(
            "ATCF position diagnostics: no exact-time BDECK 0h points were found "
            "for the checked IDs: " + ", ".join(ordered_ids)
        )
        return

    top_matches = sorted(all_matches, key=atcf_match_distance)[:8]
    print(
        "ATCF position nearest candidates: "
        + ", ".join(format_atcf_position_candidate(item) for item in top_matches)
    )

    if candidates:
        top_within = sorted(candidates, key=atcf_match_distance)[:8]
        print(
            "ATCF position candidates within threshold: "
            + ", ".join(format_atcf_position_candidate(item) for item in top_within)
        )
        if len(top_within) >= 2:
            gap = atcf_match_distance(top_within[1]) - atcf_match_distance(top_within[0])
            print(
                "ATCF position best-vs-second gap: "
                f"{gap:.1f} km; required >= {min_distance_gap_km:.1f} km."
            )


def find_atcf_position_match(
    *,
    typ_number: int,
    year: int,
    data_time: str,
    kma_point: TrackPoint | None,
    positive_radius: int | None = None,
    negative_radius: int | None = None,
    atcf_ids: list[str] | None = None,
    preferred_atcf_id: str | None = None,
    max_distance_km: float,
    min_distance_gap_km: float,
) -> AtcfMatch | None:
    if kma_point is None:
        print(f"ATCF position diagnostics: skipped for {data_time}; no KMA/APIHUB reference point.")
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

    ordered_ids: list[str] = []
    seen_ids: set[str] = set()
    for atcf_id in atcf_ids:
        normalized = str(atcf_id or "").strip().lower()
        if normalized and normalized not in seen_ids:
            seen_ids.add(normalized)
            ordered_ids.append(normalized)

    # Name matching already stores successful/missing BDECKs in memory, so this
    # parallel fetch reuses those cached results immediately and only downloads
    # candidates that were not opened earlier in this same workflow run.
    bdeck_texts = fetch_bdeck_texts_parallel(ordered_ids, reference_time=kma_point.time_utc)

    all_matches: list[AtcfMatch] = []
    candidates: list[AtcfMatch] = []
    for atcf_id in ordered_ids:
        text = bdeck_texts.get(atcf_id)
        if not text:
            continue
        for point in bdeck_track_points(text, reference_time=kma_point.time_utc):
            distance = haversine_km(kma_point.lat, kma_point.lon, point.lat, point.lon)
            match = AtcfMatch(
                atcf_id=atcf_id,
                method="position",
                distance_km=distance,
                point=point,
                reference_point=kma_point,
            )
            all_matches.append(match)
            if distance <= max_distance_km:
                candidates.append(match)

    all_matches.sort(key=atcf_match_distance)
    candidates.sort(key=atcf_match_distance)

    if not candidates:
        log_atcf_position_diagnostics(
            data_time=data_time,
            kma_point=kma_point,
            ordered_ids=ordered_ids,
            all_matches=all_matches,
            candidates=candidates,
            max_distance_km=max_distance_km,
            min_distance_gap_km=min_distance_gap_km,
            preferred_atcf_id=preferred_atcf_id,
            reason="no_candidate_within_threshold",
        )
        return None

    if len(candidates) >= 2:
        best_distance = atcf_match_distance(candidates[0])
        next_distance = atcf_match_distance(candidates[1])
        if next_distance - best_distance < min_distance_gap_km:
            preferred_id = str(preferred_atcf_id or "").strip().lower()
            preferred_candidate = next(
                (item for item in candidates if item.atcf_id.lower() == preferred_id),
                None,
            )
            ambiguous_candidates = [
                item for item in candidates
                if atcf_match_distance(item) - best_distance < min_distance_gap_km
            ]
            if preferred_candidate is not None:
                nonpreferred_regular_candidates = [
                    item for item in ambiguous_candidates
                    if item.atcf_id.lower() != preferred_id and not is_invest_atcf_id(item.atcf_id)
                ]
                if not nonpreferred_regular_candidates:
                    competitors = ", ".join(
                        f"{item.atcf_id}:{item.distance_km:.1f}km"
                        for item in ambiguous_candidates
                        if item.atcf_id.lower() != preferred_id and item.distance_km is not None
                    )
                    print(
                        "ATCF position ambiguity resolved by preferred regular ID: "
                        f"{preferred_candidate.atcf_id} ({preferred_candidate.distance_km:.1f} km)"
                        + (f" over {competitors}." if competitors else ".")
                    )
                    log_atcf_position_diagnostics(
                        data_time=data_time,
                        kma_point=kma_point,
                        ordered_ids=ordered_ids,
                        all_matches=all_matches,
                        candidates=candidates,
                        max_distance_km=max_distance_km,
                        min_distance_gap_km=min_distance_gap_km,
                        preferred_atcf_id=preferred_atcf_id,
                        reason=f"selected_preferred_{preferred_candidate.atcf_id}",
                    )
                    return preferred_candidate

            regular_candidates = [
                item for item in ambiguous_candidates
                if not is_invest_atcf_id(item.atcf_id)
            ]
            invest_candidates = [
                item for item in ambiguous_candidates
                if is_invest_atcf_id(item.atcf_id)
            ]
            if len(regular_candidates) == 1 and invest_candidates:
                selected_regular = regular_candidates[0]
                competitors = ", ".join(
                    f"{item.atcf_id}:{item.distance_km:.1f}km"
                    for item in ambiguous_candidates
                    if item.atcf_id.lower() != selected_regular.atcf_id.lower()
                    and item.distance_km is not None
                )
                print(
                    "ATCF position ambiguity resolved by sole regular ID: "
                    f"{selected_regular.atcf_id} ({selected_regular.distance_km:.1f} km)"
                    + (f" over {competitors}." if competitors else ".")
                )
                log_atcf_position_diagnostics(
                    data_time=data_time,
                    kma_point=kma_point,
                    ordered_ids=ordered_ids,
                    all_matches=all_matches,
                    candidates=candidates,
                    max_distance_km=max_distance_km,
                    min_distance_gap_km=min_distance_gap_km,
                    preferred_atcf_id=preferred_atcf_id,
                    reason=f"selected_regular_{selected_regular.atcf_id}",
                )
                return selected_regular

            log_atcf_position_diagnostics(
                data_time=data_time,
                kma_point=kma_point,
                ordered_ids=ordered_ids,
                all_matches=all_matches,
                candidates=candidates,
                max_distance_km=max_distance_km,
                min_distance_gap_km=min_distance_gap_km,
                preferred_atcf_id=preferred_atcf_id,
                reason="ambiguous_best_candidates",
            )
            return None

    selected = candidates[0]
    log_atcf_position_diagnostics(
        data_time=data_time,
        kma_point=kma_point,
        ordered_ids=ordered_ids,
        all_matches=all_matches,
        candidates=candidates,
        max_distance_km=max_distance_km,
        min_distance_gap_km=min_distance_gap_km,
        preferred_atcf_id=preferred_atcf_id,
        reason=f"selected_{selected.atcf_id}",
    )
    return selected

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


def kma_list_years_for_windows(windows: list[CycleWindow], fallback_time: datetime) -> set[int]:
    cycle_times = [parse_utc_stamp(window.data_time) for window in windows]
    cycle_times = [value for value in cycle_times if value is not None]
    if not cycle_times:
        cycle_times = [fallback_time]
    years = {value.year for value in cycle_times}
    years.update(value.year - 1 for value in cycle_times if value.month == 1)
    return years


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



def log_timing(label: str, started_at: float) -> None:
    print(f"[timing] {label}: {time.monotonic() - started_at:.1f}s")


def add_timing_elapsed(timings: dict[str, float], key: str, started_at: float) -> None:
    timings[key] = timings.get(key, 0.0) + (time.monotonic() - started_at)


def kma_gts_now_cache_path(cache_dir: Path, data_time: str, mode: str) -> Path:
    return cache_dir / "kma_gts_now" / f"{data_time}_mode{mode}.txt"


def ensure_kma_gts_now_cache(
    *,
    data_time: str,
    auth_key: str,
    cache_dir: Path | None,
    mode: str,
) -> Path | None:
    if cache_dir is None:
        return None
    path = kma_gts_now_cache_path(cache_dir, data_time, mode)
    if path.exists():
        return path
    started_at = time.monotonic()
    try:
        text = fetch_kma_text(
            kma_gts_now_url(data_time, auth_key, mode=mode),
            kma_gts_now_url(data_time, KMA_FALLBACK_AUTH_KEY, mode=mode, base_url=KMA_FALLBACK_LIST_BASE_URL)
            if KMA_FALLBACK_AUTH_KEY else "",
            label=f"typ_gts_now mode={mode} {data_time}",
            timeout=20,
            retries=1,
            retry_delay=3.0,
        )
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        print(f"Warning: failed to prefetch KMA typ_gts_now mode={mode} {data_time}: {exc}")
        return None
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp_path.write_text(text, encoding="utf-8")
    tmp_path.replace(path)
    log_timing(f"prefetch KMA typ_gts_now mode={mode} {data_time}", started_at)
    return path


def read_optional_text(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Warning: failed to read cached text {path}: {exc}")
        return None


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
    merged = dict(BUILTIN_MANUAL_ATCF_MAP)
    if not path:
        return merged
    user_map = load_json(path, {})
    if isinstance(user_map, dict):
        merged.update(user_map)
    return merged


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


def previous_atcf_match_from_status(
    status: dict | None,
    *,
    storm_keys: list[str],
    data_time: str,
    regular_only: bool = False,
) -> AtcfMatch | None:
    cycles = status.get("cycles") if isinstance(status, dict) else None
    if not isinstance(cycles, dict):
        return None
    candidates: list[tuple[str, dict]] = []
    for cycle_time, records in cycles.items():
        cycle_text = str(cycle_time or "")
        if data_time and cycle_text and cycle_text > data_time:
            continue
        if not isinstance(records, dict):
            continue
        candidates.append((cycle_text, records))
    for _, records in sorted(candidates, key=lambda item: item[0], reverse=True):
        for storm_key in storm_keys:
            for suffix in ("_240h", "_120h", ""):
                record = records.get(f"{storm_key}{suffix}")
                if not isinstance(record, dict):
                    continue
                atcf_id = str(record.get("atcf_id") or "").strip().lower()
                if not atcf_id:
                    metadata = record.get("metadata")
                    if isinstance(metadata, dict):
                        atcf_id = str(metadata.get("atcf_id") or "").strip().lower()
                if regular_only and regular_atcf_storm_number(atcf_id) is None:
                    continue
                if atcf_id:
                    print(f"Reusing previous ATCF ID from status for {storm_key}: {atcf_id}")
                    return AtcfMatch(atcf_id=atcf_id, method="previous_status")
    return None


def retain_previous_named_regular_atcf_match(
    current_match: AtcfMatch | None,
    status: dict | None,
    *,
    storm_keys: list[str],
    data_time: str,
    typ_en: str,
) -> AtcfMatch | None:
    """Keep a named storm's established regular ID ahead of a nearby INVEST."""
    if current_match is not None and not is_invest_atcf_id(current_match.atcf_id):
        return current_match

    target_name = normalize_name(typ_en)
    if not target_name:
        return current_match
    previous = previous_atcf_match_from_status(
        status,
        storm_keys=storm_keys,
        data_time=data_time,
        regular_only=True,
    )
    if previous is None or (current_match is not None and previous.atcf_id == current_match.atcf_id):
        return current_match

    text = fetch_bdeck_text(previous.atcf_id, timeout=15)
    if not text or target_name not in normalize_name(text):
        return current_match

    replaced = f" instead of nearby {current_match.atcf_id}" if current_match is not None else ""
    print(
        f"Retaining established regular ATCF ID {previous.atcf_id}{replaced}; "
        f"B-deck name still matches {typ_en}."
    )
    return AtcfMatch(atcf_id=previous.atcf_id, method="previous_regular_name")


def linked_td_number_for_typ(
    td_rows: list[dict],
    *,
    year: int,
    typ_number: int,
    data_time: str = "",
) -> int | None:
    candidates: list[tuple[int, datetime | None, datetime | None]] = []
    for row in td_rows:
        try:
            row_year = int(row.get("YY", 0))
            row_typ_number = int(row.get("TYP", -1))
            row_td_number = int(row.get("TD", 0))
        except (TypeError, ValueError):
            continue
        if row_year != year or row_typ_number != typ_number:
            continue
        candidates.append((
            row_td_number,
            parse_utc_stamp(str(row.get("TM_ST") or "")),
            parse_utc_stamp(str(row.get("TM_ED") or "")),
        ))

    if not candidates:
        return None

    target_time = parse_utc_stamp(data_time) if data_time else None
    if target_time is not None:
        active_candidates = [
            item for item in candidates
            if (item[1] is None or item[1] <= target_time)
            and (item[2] is None or target_time <= item[2])
        ]
        if active_candidates:
            return max(active_candidates, key=lambda item: item[1] or datetime.min.replace(tzinfo=timezone.utc))[0]

        previous_candidates = [
            item for item in candidates
            if item[1] is not None and item[1] <= target_time
        ]
        if previous_candidates:
            return max(previous_candidates, key=lambda item: item[1] or datetime.min.replace(tzinfo=timezone.utc))[0]

    return min(candidates, key=lambda item: item[1] or datetime.max.replace(tzinfo=timezone.utc))[0]


def td_row_represents_td_phase_at_cycle(row: dict, *, data_time: str) -> bool:
    """Return True while a linked TD episode owns the requested cycle.

    td_lst TM_ED is the transition time back to TYP (or dissipation). Treat the
    interval as half-open [TM_ST, TM_ED), so the exact redevelopment cycle is
    rendered as TYP while earlier cycles remain TD. This also keeps short
    episodes such as 00-03UTC active for the 00UTC cycle.
    """
    cycle = parse_utc_stamp(data_time)
    if cycle is None:
        return False
    start = parse_utc_stamp(str(row.get("TM_ST") or ""))
    end = parse_utc_stamp(str(row.get("TM_ED") or ""))
    if start and cycle < start:
        return False
    if end and cycle >= end:
        return False
    return True


def active_linked_td_rows_by_typ(
    td_rows: list[dict],
    *,
    now: datetime,
    cycle_time: datetime | None = None,
    data_time: str = "",
) -> dict[tuple[int, int], list[dict]]:
    active_rows: dict[tuple[int, int], list[dict]] = {}
    for row in td_rows:
        try:
            year = int(row.get("YY", 0))
            td_number = int(row.get("TD", 0))
            typ_number = int(row.get("TYP", 0))
        except (TypeError, ValueError):
            continue
        if typ_number <= 0:
            continue
        if data_time:
            if not td_row_represents_td_phase_at_cycle(row, data_time=data_time):
                continue
        elif not row_active_for_time(row, probe_time=now, cycle_time=cycle_time):
            continue
        active_rows.setdefault((year, typ_number), []).append(row)
    return active_rows


def suppressed_typ_metadata_for_td_phase(
    *,
    td_job: StormJob,
    fcst_hours: int,
    existing_metadata: dict | None = None,
) -> dict:
    metadata = dict(existing_metadata) if isinstance(existing_metadata, dict) else {}
    linked_typ_number = int(td_job.linked_typ_number or 0)
    metadata.update({
        "generated_at_utc": format_utc_stamp(utc_now()),
        "image_path": "",
        "storm_stage": "TYP",
        "storm_year": str(td_job.year),
        "typ_number": linked_typ_number,
        "data_typ_number": linked_typ_number,
        "data_time": td_job.data_time,
        "fcst_hours": fcst_hours,
        "model_count": 0,
        "target_model_count": ACTIVE_MODEL_TARGET,
        "models": [],
        "model_labels": [],
        "no_output": True,
        "no_output_reason": (
            f"Suppressed because linked TD{td_job.typ_number:02d} phase is active."
        ),
    })
    return metadata


def remove_obsolete_typ_artifacts_for_td_phases(
    *,
    output_root: Path,
    jobs: list[StormJob],
    fcst_hours_list: list[int],
    cycle_status: dict,
    window: CycleWindow,
    dry_run: bool,
    changed_paths: set[Path] | None = None,
) -> list[dict]:
    """Remove stale TYP products left by an older TD/TYP phase decision."""
    active_typ_keys = {
        (job.year, job.typ_number)
        for job in jobs
        if not job.stage.startswith("TD_")
    }
    td_phase_jobs: dict[tuple[int, int], StormJob] = {}
    for job in jobs:
        if not job.stage.startswith("TD_") or not job.linked_typ_number:
            continue
        key = (job.year, int(job.linked_typ_number))
        if key in active_typ_keys:
            continue
        td_phase_jobs.setdefault(key, job)

    suppression_entries: list[dict] = []
    for (year, typ_number), td_job in sorted(td_phase_jobs.items()):
        cyclone_id = f"{year % 100:02d}{typ_number:02d}"
        status_prefix = f"typ_{year}_{typ_number:02d}"
        for fcst_hours in dict.fromkeys(fcst_hours_list):
            metadata_paths = sorted(
                (output_root / str(year)).glob(
                    f"TYP_{cyclone_id}_*/metadata/runs/{td_job.data_time}_{fcst_hours}h.json"
                )
            )
            existing_metadata = load_json(metadata_paths[0], None) if metadata_paths else None
            image_paths = sorted(
                (output_root / str(year)).glob(
                    f"TYP_{cyclone_id}_*/images/TYP_{cyclone_id}_*_{td_job.data_time}_{fcst_hours}h.png"
                )
            )
            for image_path in image_paths:
                print(
                    f"Removing obsolete TYP output during linked TD phase: {image_path}"
                    if not dry_run
                    else f"Would remove obsolete TYP output during linked TD phase: {image_path}"
                )
                if not dry_run:
                    if changed_paths is not None:
                        changed_paths.add(image_path)
                    try:
                        image_path.unlink()
                    except FileNotFoundError:
                        pass
                    try:
                        image_path.parent.rmdir()
                    except OSError:
                        pass
            for metadata_path in metadata_paths:
                print(
                    f"Removing obsolete TYP metadata during linked TD phase: {metadata_path}"
                    if not dry_run
                    else f"Would remove obsolete TYP metadata during linked TD phase: {metadata_path}"
                )
                if not dry_run:
                    if changed_paths is not None:
                        changed_paths.add(metadata_path)
                    metadata_path.unlink()

            cycle_status.pop(f"{status_prefix}_{fcst_hours}h", None)
            metadata = suppressed_typ_metadata_for_td_phase(
                td_job=td_job,
                fcst_hours=fcst_hours,
                existing_metadata=existing_metadata,
            )
            suppression_entries.append({
                "job": {
                    "storm_key": status_prefix,
                    "stage": "TYP_SUPPRESSED_BY_TD",
                    "year": year,
                    "data_time": td_job.data_time,
                    "td_number": td_job.typ_number,
                    "linked_td_number": td_job.typ_number,
                    "linked_typ_number": None,
                    "typ_number": typ_number,
                    "typ_name_ko": metadata.get("typ_name_ko", td_job.typ_name_ko),
                    "typ_name": metadata.get("typ_name", td_job.typ_name),
                    "typ_en": metadata.get("typ_name", td_job.typ_en),
                    "atcf_id": metadata.get("atcf_id", td_job.atcf_id or ""),
                    "fcst_hours": fcst_hours,
                    "skip_atcf": bool(metadata.get("skip_atcf", td_job.skip_atcf)),
                },
                "window": asdict(window),
                "result": {
                    "status": "suppressed_td_phase",
                    "metadata": metadata,
                },
            })
    return suppression_entries


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
    kma_gts_now_text: str | None = None,
    activity_cycle_time: datetime | None = None,
    status: dict | None = None,
) -> list[StormJob]:
    total_started_at = time.monotonic()
    timing_stats: dict[str, float] = {
        "atcf_sector": 0.0,
        "atcf_name": 0.0,
        "kma_reference": 0.0,
        "atcf_position": 0.0,
        "bdeck_analysis": 0.0,
    }
    bdeck_before = bdeck_stats_snapshot()
    jobs: list[StormJob] = []
    sector_entries: list[AtcfSectorEntry] = []
    if resolve_atcf:
        started_at = time.monotonic()
        sector_entries = fetch_atcf_sector_entries()
        add_timing_elapsed(timing_stats, "atcf_sector", started_at)
    data_dt = parse_utc_stamp(data_time)
    if not data_dt:
        return jobs

    # KMA can list one named typhoon period broadly in typ_lst.php while td_lst.php
    # contains intermittent weakening/redevelopment TD episodes linked to the same
    # TYP number. In those intervals, prefer the active TD row and suppress the
    # broad TYP row to avoid rendering the system as TYP during a TD phase.
    active_td_links = active_linked_td_rows_by_typ(
        td_rows,
        now=now,
        cycle_time=activity_cycle_time,
        data_time=data_time,
    )

    active_typhoons: list[tuple[int, int]] = []
    seen_typ_keys: set[tuple[int, int]] = set()
    for row in typ_rows:
        try:
            typ_number = int(row["SEQ"])
            year = int(row["YY"])
        except (TypeError, ValueError):
            continue
        typ_key = (year, typ_number)
        if typ_key in seen_typ_keys:
            continue
        is_active = row_active_for_time(row, probe_time=now, cycle_time=activity_cycle_time)
        if not is_active:
            continue
        typ_start_time = parse_utc_stamp(row.get("TM_ST", ""))
        if typ_start_time and data_dt < typ_start_time:
            continue
        if typ_key in active_td_links:
            td_labels = ", ".join(
                f"TD{safe_int(item.get('TD')) or 0:02d}"
                for item in active_td_links.get(typ_key, [])
            )
            print(
                f"Suppressing broad TYP{typ_number:02d} row at {data_time}; "
                f"active linked TD phase detected: {td_labels}."
            )
            continue
        seen_typ_keys.add(typ_key)
        typ_en = row.get("TYP_EN", "").strip().upper()
        typ_name_ko = row.get("TYP_NAME", "").strip()
        linked_td_number = linked_td_number_for_typ(td_rows, year=year, typ_number=typ_number, data_time=data_time)
        typ_atcf_ids = candidate_atcf_ids(
            typ_number=typ_number,
            year=year,
            positive_radius=atcf_search_positive_radius,
            negative_radius=atcf_search_negative_radius,
        )
        manual_id = None
        atcf_match = None
        kma_point = None
        typ_status_keys = [f"typ_{year}_{typ_number:02d}"]
        if resolve_atcf:
            manual_id = manual_atcf_id(
                manual_map,
                year=year,
                td_number=linked_td_number,
                typ_number=typ_number,
                typ_en=typ_en,
            )
            if manual_id:
                atcf_match = AtcfMatch(manual_id, "manual")
            else:
                atcf_match = find_atcf_sector_name_match(
                    sector_entries,
                    typ_en=typ_en,
                    year=year,
                    data_time=data_time,
                    preferred_atcf_id=f"wp{typ_number:02d}{year}",
                )
            if not manual_id:
                atcf_match = retain_previous_named_regular_atcf_match(
                    atcf_match,
                    status,
                    storm_keys=typ_status_keys,
                    data_time=data_time,
                    typ_en=typ_en,
                )
        if resolve_atcf and atcf_match is None and typ_en and sector_entries:
            started_at = time.monotonic()
            kma_point = fetch_kma_reference_point(
                typ_number=typ_number,
                data_time=data_time,
                auth_key=auth_key,
                gts_text=kma_gts_now_text,
                stage="TYP",
            )
            add_timing_elapsed(timing_stats, "kma_reference", started_at)
            started_at = time.monotonic()
            atcf_match = find_atcf_sector_position_match(
                sector_entries,
                year=year,
                data_time=data_time,
                kma_point=kma_point,
                preferred_atcf_id=f"wp{typ_number:02d}{year}",
                max_distance_km=atcf_position_max_distance_km,
                min_distance_gap_km=atcf_position_min_distance_gap_km,
            )
            add_timing_elapsed(timing_stats, "atcf_position", started_at)
        if resolve_atcf and atcf_match is None:
            started_at = time.monotonic()
            atcf_match = find_atcf_match(
                typ_en=typ_en,
                typ_number=typ_number,
                year=year,
                positive_radius=atcf_search_positive_radius,
                negative_radius=atcf_search_negative_radius,
                atcf_ids=typ_atcf_ids,
            )
            add_timing_elapsed(timing_stats, "atcf_name", started_at)
        if resolve_atcf and atcf_match is None and typ_en:
            if kma_point is None:
                started_at = time.monotonic()
                kma_point = fetch_kma_reference_point(
                    typ_number=typ_number,
                    data_time=data_time,
                    auth_key=auth_key,
                    gts_text=kma_gts_now_text,
                    stage="TYP",
                )
                add_timing_elapsed(timing_stats, "kma_reference", started_at)
            started_at = time.monotonic()
            atcf_match = find_atcf_position_match(
                typ_number=typ_number,
                year=year,
                data_time=data_time,
                kma_point=kma_point,
                atcf_ids=typ_atcf_ids,
                preferred_atcf_id=f"wp{typ_number:02d}{year}",
                max_distance_km=atcf_position_max_distance_km,
                min_distance_gap_km=atcf_position_min_distance_gap_km,
            )
            add_timing_elapsed(timing_stats, "atcf_position", started_at)
        if resolve_atcf and atcf_match is None:
            atcf_match = previous_atcf_match_from_status(
                status,
                storm_keys=typ_status_keys,
                data_time=data_time,
            )
        atcf_id = atcf_match.atcf_id if atcf_match else None
        atcf_method = atcf_match.method if atcf_match else ""
        analysis_point = atcf_match.point if atcf_match and atcf_match.method == "position" else None
        if analysis_point is None and atcf_id:
            started_at = time.monotonic()
            analysis_point = fetch_bdeck_analysis_point(atcf_id, data_time=data_time)
            add_timing_elapsed(timing_stats, "bdeck_analysis", started_at)
        analysis_source = "BDECK" if analysis_point else ""
        analysis_match_method = atcf_match.method if analysis_point and atcf_match else ""
        analysis_distance_km = atcf_match.distance_km if analysis_point and atcf_match else None
        if not resolve_atcf:
            reason = "ATCF matching skipped for lightweight precheck."
        elif is_atcf_position_match(atcf_match):
            reason = (
                "ATCF name match not found; using temporary position match "
                f"{atcf_match.atcf_id} ({atcf_match.distance_km:.0f} km)."
            )
        else:
            reason = "" if atcf_id else "ATCF name match not found; generating KMA-only guidance."
        active_typhoons.append((year, typ_number))
        jobs.append(StormJob(
            storm_key=f"typ_{year}_{typ_number:02d}",
            stage="TYP_LINKED" if atcf_id else "TYP_LINKED_ATCF_PENDING",
            year=year,
            data_time=data_time,
            td_number=None,
            linked_td_number=linked_td_number,
            linked_typ_number=None,
            canonical_storm_stage="TYP",
            canonical_typ_number=typ_number,
            canonical_typ_name=typ_en or typ_name_ko or "NONAME",
            canonical_typ_name_ko=typ_name_ko,
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
        linked_typ_row = None
        linked_typ_en = ""
        linked_typ_name_ko = ""
        linked_typ_start = None
        if typ_number != 0:
            linked_typ_row = typ_row_for_number(typ_rows, year=year, typ_number=typ_number)
            linked_typ_en, linked_typ_name_ko, linked_typ_start = typ_identity_from_row(linked_typ_row)

        td_is_active = row_active_for_time(row, probe_time=now, cycle_time=activity_cycle_time)
        # KMA td_lst sometimes ends the pre-typhoon TD row before typ_lst starts,
        # although typ_gts_now still has usable forecast rows in the gap. Keep the
        # linked TD job alive until the named TYP cycle starts so manual/backfill
        # cycles such as 2023101712/18 and 2023101800 are not skipped.
        if not td_is_active and typ_number and linked_typ_start and data_dt < linked_typ_start:
            td_start = parse_utc_stamp(str(row.get("TM_ST") or ""))
            if td_start and data_dt >= ceil_to_cycle_boundary(td_start):
                td_is_active = True
                print(
                    f"Extending linked TD{td_number:02d}->TYP{typ_number:02d} activity "
                    f"through pre-TYP gap at {data_time}."
                )
        if not td_is_active:
            continue

        linked_typ_has_started = bool(typ_number and linked_typ_start and data_dt >= linked_typ_start)
        if typ_number and (year, typ_number) in active_typhoon_set and linked_typ_has_started:
            continue
        display_typ_en = linked_typ_en if linked_typ_has_started else ""
        display_typ_name_ko = linked_typ_name_ko if linked_typ_has_started else ""
        matching_typ_en = linked_typ_en if typ_number else display_typ_en
        td_storm_key = (
            f"td_{year}_{td_number:02d}_typ_{typ_number:02d}"
            if typ_number
            else f"td_{year}_{td_number:02d}"
        )
        status_keys = [td_storm_key]
        if typ_number:
            status_keys.extend([
                f"typ_{year}_{typ_number:02d}",
                f"td_{year}_{td_number:02d}",
            ])

        td_atcf_ids = candidate_td_atcf_ids(td_number=td_number, year=year, linked_typ_number=(typ_number or None))
        td_base_atcf_number = max(1, min(89, typ_number or math.ceil(td_number / 2)))
        manual_id = None
        atcf_match = None
        kma_point = None
        reference_typ_number = td_number
        if resolve_atcf:
            manual_id = manual_atcf_id(
                manual_map,
                year=year,
                td_number=td_number,
                typ_number=typ_number or td_number,
                typ_en=matching_typ_en or display_typ_en,
            )
            atcf_match = AtcfMatch(manual_id, "manual") if manual_id else None
            if atcf_match is None and matching_typ_en:
                atcf_match = find_atcf_sector_name_match(
                    sector_entries,
                    typ_en=matching_typ_en,
                    year=year,
                    data_time=data_time,
                    preferred_atcf_id=(f"wp{typ_number:02d}{year}" if typ_number else None),
                )
            if not manual_id and matching_typ_en:
                atcf_match = retain_previous_named_regular_atcf_match(
                    atcf_match,
                    status,
                    storm_keys=status_keys,
                    data_time=data_time,
                    typ_en=matching_typ_en,
                )
        if resolve_atcf and atcf_match is None and sector_entries:
            started_at = time.monotonic()
            kma_point = fetch_kma_reference_point(
                typ_number=reference_typ_number,
                data_time=data_time,
                auth_key=auth_key,
                gts_text=kma_gts_now_text,
                stage="TD",
            )
            add_timing_elapsed(timing_stats, "kma_reference", started_at)
            started_at = time.monotonic()
            atcf_match = find_atcf_sector_position_match(
                sector_entries,
                year=year,
                data_time=data_time,
                kma_point=kma_point,
                preferred_atcf_id=(f"wp{typ_number:02d}{year}" if typ_number else None),
                max_distance_km=atcf_position_max_distance_km,
                min_distance_gap_km=atcf_position_min_distance_gap_km,
            )
            add_timing_elapsed(timing_stats, "atcf_position", started_at)
        if resolve_atcf and atcf_match is None and matching_typ_en:
            started_at = time.monotonic()
            atcf_match = find_atcf_match(
                typ_en=matching_typ_en,
                typ_number=td_base_atcf_number,
                year=year,
                positive_radius=atcf_search_positive_radius,
                negative_radius=atcf_search_negative_radius,
                atcf_ids=td_atcf_ids,
            )
            add_timing_elapsed(timing_stats, "atcf_name", started_at)
        if resolve_atcf and atcf_match is None:
            if kma_point is None:
                started_at = time.monotonic()
                kma_point = fetch_kma_reference_point(
                    typ_number=reference_typ_number,
                    data_time=data_time,
                    auth_key=auth_key,
                    gts_text=kma_gts_now_text,
                    stage="TD",
                )
                add_timing_elapsed(timing_stats, "kma_reference", started_at)
            td_atcf_ids = extend_td_atcf_ids_for_dateline(td_atcf_ids, year=year, kma_point=kma_point)
            started_at = time.monotonic()
            atcf_match = find_atcf_position_match(
                typ_number=reference_typ_number,
                year=year,
                data_time=data_time,
                kma_point=kma_point,
                atcf_ids=td_atcf_ids,
                preferred_atcf_id=(f"wp{typ_number:02d}{year}" if typ_number else None),
                max_distance_km=atcf_position_max_distance_km,
                min_distance_gap_km=atcf_position_min_distance_gap_km,
            )
            add_timing_elapsed(timing_stats, "atcf_position", started_at)
        if resolve_atcf and atcf_match is None:
            atcf_match = previous_atcf_match_from_status(
                status,
                storm_keys=status_keys,
                data_time=data_time,
            )
        atcf_id = atcf_match.atcf_id if atcf_match else None
        atcf_method = atcf_match.method if atcf_match else ""
        analysis_point = atcf_match.point if atcf_match and atcf_match.method == "position" else None
        if analysis_point is None and atcf_id:
            started_at = time.monotonic()
            analysis_point = fetch_bdeck_analysis_point(atcf_id, data_time=data_time)
            add_timing_elapsed(timing_stats, "bdeck_analysis", started_at)
        analysis_source = "BDECK" if analysis_point else ""
        analysis_match_method = atcf_match.method if analysis_point and atcf_match else ""
        analysis_distance_km = atcf_match.distance_km if analysis_point and atcf_match else None
        if not resolve_atcf:
            stage = "TD_UNLINKED"
            reason = "ATCF matching skipped for lightweight precheck."
        elif typ_number != 0 and is_atcf_position_match(atcf_match):
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
        elif is_atcf_position_match(atcf_match):
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
        canonical_td_stage = "TYP" if typ_number else "TD"
        canonical_td_number = typ_number if typ_number else td_number
        canonical_td_name = (
            linked_typ_en
            or linked_typ_name_ko
            or (display_typ_en if linked_typ_has_started else "")
            or "NONAME"
        )
        jobs.append(StormJob(
            storm_key=td_storm_key,
            stage=stage,
            year=year,
            data_time=data_time,
            td_number=td_number,
            linked_td_number=None,
            linked_typ_number=typ_number or None,
            canonical_storm_stage=canonical_td_stage,
            canonical_typ_number=canonical_td_number,
            canonical_typ_name=canonical_td_name if canonical_td_stage == "TYP" else "NONAME",
            canonical_typ_name_ko=linked_typ_name_ko if canonical_td_stage == "TYP" else "",
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

    total_elapsed = time.monotonic() - total_started_at
    measured_elapsed = sum(timing_stats.values())
    bdeck_delta = bdeck_stats_delta(bdeck_before)
    print(
        "[timing] build storm jobs detail "
        f"{data_time}: jobs={len(jobs)} "
        f"atcf_sector={timing_stats['atcf_sector']:.1f}s "
        f"atcf_name={timing_stats['atcf_name']:.1f}s "
        f"kma_reference={timing_stats['kma_reference']:.1f}s "
        f"atcf_position={timing_stats['atcf_position']:.1f}s "
        f"bdeck_analysis={timing_stats['bdeck_analysis']:.1f}s "
        f"other_active_linking={max(0.0, total_elapsed - measured_elapsed):.1f}s "
        f"bdeck_fetches={bdeck_delta.get('fetches', 0)} "
        f"bdeck_successes={bdeck_delta.get('successes', 0)} "
        f"bdeck_missing={bdeck_delta.get('missing', 0)} "
        f"bdeck_errors={bdeck_delta.get('errors', 0)} "
        f"bdeck_fallbacks={bdeck_delta.get('fallbacks', 0)} "
        f"bdeck_cache_hits={bdeck_delta.get('cache_hits', 0)}"
    )
    return jobs


def canonical_stage_for_job(job: StormJob) -> str:
    stage = str(job.canonical_storm_stage or "").strip().upper()
    if stage in {"TD", "TYP"}:
        return stage
    if job.stage.startswith("TD_") and job.linked_typ_number and job.canonical_typ_number:
        return "TYP"
    return "TD" if job.stage.startswith("TD_") else "TYP"


def canonical_typ_number_for_job(job: StormJob) -> int:
    if job.canonical_typ_number:
        return int(job.canonical_typ_number)
    if canonical_stage_for_job(job) == "TYP" and job.stage.startswith("TD_") and job.linked_typ_number:
        return int(job.linked_typ_number)
    return int(job.typ_number)


def canonical_typ_name_for_job(job: StormJob) -> str:
    name = str(job.canonical_typ_name or "").strip()
    if name:
        return name
    if canonical_stage_for_job(job) == "TYP":
        return str(job.typ_en or job.typ_name or "NONAME").strip() or "NONAME"
    return "NONAME" if job.stage.startswith("TD_") else (str(job.typ_name or "NONAME").strip() or "NONAME")


def canonical_typ_name_ko_for_job(job: StormJob) -> str:
    return str(job.canonical_typ_name_ko or job.typ_name_ko or "").strip()


def system_dir_name_for_parts(year: int | str, stage: str, typ_number: int | str, typ_name: str = "NONAME") -> str:
    year_value = safe_int(year)
    year_suffix = year_value % 100 if year_value is not None else 0
    typ_number_value = safe_int(typ_number) or 0
    stage_label = "TD" if str(stage or "").upper().startswith("TD") else "TYP"
    name = str(typ_name or "NONAME").strip() or "NONAME"
    return f"{stage_label}_{year_suffix:02d}{typ_number_value:02d}_{name}"


def system_dir_name_for_job(job: StormJob) -> str:
    return system_dir_name_for_parts(
        job.year,
        canonical_stage_for_job(job),
        canonical_typ_number_for_job(job),
        canonical_typ_name_for_job(job),
    )


def system_dir_from_job(output_root: Path, job: StormJob) -> Path:
    return output_root / str(job.year) / system_dir_name_for_job(job)


def metadata_path_for(output_root: Path, job: StormJob, fcst_hours: int) -> Path:
    return system_dir_from_job(output_root, job) / "metadata" / "runs" / f"{job.data_time}_{fcst_hours}h.json"


def deterministic_output_path_for(output_root: Path, job: StormJob, fcst_hours: int) -> Path:
    year_str = str(job.year)
    cyclone_id = f"{job.year % 100:02d}{job.typ_number:02d}"
    stage = "TD" if job.stage.startswith("TD_") else "TYP"
    storm_name = job.typ_name or "NONAME"
    file_name = f"{stage}_{cyclone_id}_{storm_name}_{job.data_time}_{fcst_hours}h.png"
    return system_dir_from_job(output_root, job) / "images" / file_name


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
    if status not in {"failed", "restored_previous"}:
        return
    if status == "restored_previous":
        headline = "VTG forced rerun failed; previous output was restored"
    else:
        headline = "VTG generation failed"
    print(
        f"{headline}: "
        f"storm={job.storm_key} data_time={job.data_time} "
        f"fcst_hours={fcst_hours} returncode={result.get('returncode', 'unknown')}",
        file=sys.stderr,
    )
    print_process_output_tail(
        stdout=result.get("stdout"),
        stderr=result.get("stderr"),
        prefix=f"VTG {fcst_hours}h {status}",
    )


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


def metadata_int(value) -> int | None:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def normalized_metadata_stage(metadata: dict) -> str:
    stage = str(metadata.get("storm_stage") or "TYP").strip().upper()
    return "TD" if stage == "TD" else "TYP"


def canonical_stage_from_metadata(metadata: dict) -> str:
    explicit = str(metadata.get("canonical_storm_stage") or "").strip().upper()
    if explicit in {"TD", "TYP"}:
        return explicit
    if normalized_metadata_stage(metadata) == "TD" and metadata_int(metadata.get("linked_typ_number")):
        return "TYP"
    return normalized_metadata_stage(metadata)


def canonical_typ_number_from_metadata(metadata: dict) -> int | None:
    explicit = metadata_int(metadata.get("canonical_typ_number"))
    if explicit:
        return explicit
    if canonical_stage_from_metadata(metadata) == "TYP" and normalized_metadata_stage(metadata) == "TD":
        linked_typ_number = metadata_int(metadata.get("linked_typ_number"))
        if linked_typ_number:
            return linked_typ_number
    return metadata_int(metadata.get("typ_number"))


def canonical_typ_name_from_metadata(metadata: dict) -> str:
    name = str(metadata.get("canonical_typ_name") or "").strip()
    if name:
        return name
    if canonical_stage_from_metadata(metadata) == "TYP" and normalized_metadata_stage(metadata) == "TD":
        linked_name = str(metadata.get("linked_typ_name") or "").strip()
        if linked_name:
            return linked_name
    return str(metadata.get("typ_name") or "NONAME").strip() or "NONAME"


def canonical_typ_name_ko_from_metadata(metadata: dict) -> str:
    return str(metadata.get("canonical_typ_name_ko") or metadata.get("typ_name_ko") or "").strip()


def canonical_storm_key_from_metadata(metadata: dict) -> str:
    data_time = str(metadata.get("data_time") or "")
    year_text = str(metadata.get("storm_year") or data_time[:4] or "0")
    try:
        year = int(year_text)
    except (TypeError, ValueError):
        year = 0
    typ_number = canonical_typ_number_from_metadata(metadata)
    if not year or not typ_number:
        return "unknown"
    prefix = "td" if canonical_stage_from_metadata(metadata) == "TD" else "typ"
    return f"{prefix}_{year}_{typ_number:02d}"


def canonical_metadata_fields(metadata: dict) -> dict:
    storm_key = canonical_storm_key_from_metadata(metadata)
    stage = canonical_stage_from_metadata(metadata)
    typ_number = canonical_typ_number_from_metadata(metadata)
    return {
        "canonical_storm_key": storm_key,
        "canonical_storm_stage": stage,
        "canonical_typ_number": typ_number,
        "canonical_typ_name": canonical_typ_name_from_metadata(metadata),
        "canonical_typ_name_ko": canonical_typ_name_ko_from_metadata(metadata),
    }


def track_history_paths_from_metadata(output_root: Path, metadata: dict) -> list[Path]:
    data_time = str(metadata.get("data_time") or "")
    year = str(metadata.get("storm_year") or data_time[:4] or "").strip()
    typ_number = canonical_typ_number_from_metadata(metadata)
    stage = canonical_stage_from_metadata(metadata)
    typ_name = canonical_typ_name_from_metadata(metadata)
    if not year or not typ_number:
        return []
    system_dir = output_root / year / system_dir_name_for_parts(year, stage, typ_number, typ_name)
    return [system_dir / "metadata" / "track_history.json"]


def existing_typ_name_lookup(
    output_root: Path,
    *,
    years: set[str] | None = None,
) -> dict[tuple[str, int], tuple[str, str]]:
    lookup: dict[tuple[str, int], tuple[str, str]] = {}

    def remember(year: str, typ_number: int | None, typ_name: str, typ_name_ko: str = "") -> None:
        if not year or not typ_number:
            return
        name = str(typ_name or "").strip()
        if not name or name.upper() == "NONAME":
            return
        key = (str(year), int(typ_number))
        current = lookup.get(key)
        if current and current[0].upper() != "NONAME":
            return
        lookup[key] = (name, str(typ_name_ko or "").strip())

    year_dirs = (
        [output_root / year for year in sorted(years)]
        if years is not None
        else sorted(output_root.glob("[0-9][0-9][0-9][0-9]"))
    )
    for path in [year_dir / "index.json" for year_dir in year_dirs if (year_dir / "index.json").exists()]:
        payload = load_json(path, {})
        systems = payload.get("systems") if isinstance(payload, dict) else []
        if not isinstance(systems, list):
            continue
        for system in systems:
            if not isinstance(system, dict):
                continue
            stage = str(system.get("stage") or "").upper()
            if not stage.startswith("TYP"):
                continue
            remember(
                str(system.get("year") or path.parent.name),
                metadata_int(system.get("typ_number")),
                str(system.get("typ_name") or ""),
                str(system.get("typ_name_ko") or ""),
            )

    for year_dir in year_dirs:
        for path in sorted(year_dir.glob("TYP_*/manifest.json")):
            payload = load_json(path, {})
            if isinstance(payload, dict):
                remember(
                    str(payload.get("year") or path.parents[1].name),
                    metadata_int(payload.get("typ_number")),
                    str(payload.get("typ_name") or ""),
                    str(payload.get("typ_name_ko") or ""),
                )
            match = re.match(r"^TYP_(\d{2})(\d{2})_(.+)$", path.parent.name)
            if match:
                remember(path.parents[1].name, int(match.group(2)), match.group(3), "")
    return lookup


def td_typ_link_lookup(td_rows: list[dict], typ_rows: list[dict]) -> dict[tuple[str, int], dict]:
    """Map KMA TD rows to their promoted TYP identity.

    This is intentionally independent from current activity state. When a TD
    has already been promoted, older TD output folders often have no
    linked_typ_number in their stored metadata because the promotion was not
    known at render time. The KMA td_lst row is the authoritative bridge.
    """
    typ_names: dict[tuple[str, int], tuple[str, str]] = {}
    for row in typ_rows or []:
        try:
            year = str(int(row.get("YY", 0)))
            typ_number = int(row.get("SEQ", 0))
        except (TypeError, ValueError):
            continue
        if typ_number <= 0:
            continue
        typ_names[(year, typ_number)] = (
            str(row.get("TYP_EN") or row.get("TYP_NAME") or "").strip().upper(),
            str(row.get("TYP_NAME") or "").strip(),
        )

    links: dict[tuple[str, int], dict] = {}
    for row in td_rows or []:
        try:
            year = str(int(row.get("YY", 0)))
            td_number = int(row.get("TD", 0))
            typ_number = int(row.get("TYP", 0))
        except (TypeError, ValueError):
            continue
        if td_number <= 0 or typ_number <= 0:
            continue
        typ_row = typ_row_for_number(typ_rows, year=year, typ_number=typ_number)
        typ_name, typ_name_ko = typ_names.get((year, typ_number), ("", ""))
        payload = typ_link_payload(typ_number, typ_row)
        if typ_name and payload["canonical_typ_name"] == "NONAME":
            payload["canonical_typ_name"] = typ_name
        if typ_name_ko and not payload["canonical_typ_name_ko"]:
            payload["canonical_typ_name_ko"] = typ_name_ko
        links[(year, td_number)] = payload
    return links


def canonical_target_for_linked_td_metadata(
    output_root: Path,
    metadata: dict,
    typ_names: dict[tuple[str, int], tuple[str, str]],
    *,
    fallback_linked_typ_number: int | None = None,
) -> tuple[Path, dict] | None:
    if normalized_metadata_stage(metadata) != "TD":
        return None
    data_time = str(metadata.get("data_time") or "")
    year = str(metadata.get("storm_year") or data_time[:4] or "").strip()
    if not year:
        return None
    # ATCF IDs (for example 11W) are basin sequence numbers, not KMA TYP numbers.
    # Canonical TD->TYP absorption must come only from explicit KMA linkage metadata.
    linked_typ_number = (
        metadata_int(metadata.get("linked_typ_number"))
        or (
            metadata_int(metadata.get("canonical_typ_number"))
            if str(metadata.get("canonical_storm_stage") or "").strip().upper() == "TYP"
            else None
        )
        or fallback_linked_typ_number
    )
    if not linked_typ_number:
        return None
    canonical_name = str(metadata.get("canonical_typ_name") or "").strip()
    canonical_name_ko = str(metadata.get("canonical_typ_name_ko") or "").strip()
    if not canonical_name or canonical_name.upper() == "NONAME":
        canonical_name, canonical_name_ko = typ_names.get((year, linked_typ_number), ("", ""))
    if not canonical_name or canonical_name.upper() == "NONAME":
        return None
    target_dir = output_root / year / system_dir_name_for_parts(year, "TYP", linked_typ_number, canonical_name)
    fields = {
        "canonical_storm_key": f"typ_{year}_{linked_typ_number:02d}",
        "canonical_storm_stage": "TYP",
        "canonical_typ_number": linked_typ_number,
        "canonical_typ_name": canonical_name,
        "canonical_typ_name_ko": canonical_name_ko,
        "linked_typ_number": linked_typ_number,
    }
    return target_dir, fields


def rewrite_metadata_for_canonical_target(metadata: dict, target_dir: Path, canonical_fields: dict) -> dict:
    updated = {**metadata, **canonical_fields}
    image_path = normalized_image_path(updated.get("image_path"))
    if image_path:
        updated["image_path"] = relative_asset_path(target_dir / "images" / Path(image_path).name)
    data_time = str(updated.get("data_time") or "").strip()
    if data_time:
        target_latest = target_dir / "metadata" / "source_availability" / f"{data_time}.json"
        if metadata_referenced_path_exists(metadata, "source_availability_path") or target_latest.exists():
            updated["source_availability_path"] = relative_asset_path(target_latest)
        else:
            updated.pop("source_availability_path", None)
        updated.pop("source_availability_summary_path", None)
    else:
        updated.pop("source_availability_path", None)
        updated.pop("source_availability_summary_path", None)
    return updated


def move_or_replace_file(source: Path, target: Path, changed_paths: set[Path], *, dry_run: bool) -> None:
    changed_paths.add(source)
    changed_paths.add(target)
    if dry_run or source == target or not source.exists():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        target.unlink()
    shutil.move(str(source), str(target))


def merge_track_history_payloads(target: dict, source: dict, *, canonical_key: str, aliases: list[str]) -> dict:
    priority = {
        "MODEL_0H_MEAN": 1,
        "BDECK": 2,
        "JTWC_BDECK": 2,
        "KMA_OFFICIAL": 3,
        "KMA": 3,
    }
    merged = dict(target) if isinstance(target, dict) else {}
    merged["version"] = max(int(merged.get("version") or 1), int(source.get("version") or 1) if isinstance(source, dict) else 1)
    if canonical_key:
        merged["primary_key"] = canonical_key
    alias_set = {str(item or "").strip() for item in merged.get("aliases", []) if str(item or "").strip()}
    if isinstance(source, dict):
        alias_set.update(str(item or "").strip() for item in source.get("aliases", []) if str(item or "").strip())
    alias_set.update(str(item or "").strip() for item in aliases if str(item or "").strip())
    if canonical_key:
        alias_set.add(canonical_key)
    merged["aliases"] = sorted(alias_set)

    by_time: dict[str, dict] = {}
    for payload in [source if isinstance(source, dict) else {}, target if isinstance(target, dict) else {}]:
        for point in payload.get("points", []) if isinstance(payload.get("points"), list) else []:
            if not isinstance(point, dict):
                continue
            time_key = str(point.get("time_utc") or "").strip()
            if not time_key:
                continue
            existing = by_time.get(time_key)
            source_priority = priority.get(str(point.get("source") or "").upper(), 0)
            existing_priority = priority.get(str(existing.get("source") or "").upper(), 0) if existing else -1
            if existing is None or source_priority >= existing_priority:
                by_time[time_key] = point
    merged["points"] = [by_time[key] for key in sorted(by_time)]
    merged["updated_at_utc"] = format_utc_stamp(utc_now())
    return merged


def merge_drive_archive_payload(target: dict, source: dict, source_dir: Path, target_dir: Path, canonical_key: str) -> dict:
    merged = dict(target) if isinstance(target, dict) else {}
    if not merged:
        merged = {k: v for k, v in source.items() if k != "images"} if isinstance(source, dict) else {}
    images = dict(merged.get("images") or {}) if isinstance(merged.get("images"), dict) else {}
    source_images = source.get("images") if isinstance(source, dict) else {}
    if isinstance(source_images, dict):
        for image_path, record in source_images.items():
            image_name = Path(normalized_image_path(image_path)).name
            new_path = relative_asset_path(target_dir / "images" / image_name)
            new_record = dict(record) if isinstance(record, dict) else {}
            new_record["image_path"] = new_path
            new_record["storm_key"] = canonical_key
            images[new_path] = new_record
    merged["version"] = max(int(merged.get("version") or 1), int(source.get("version") or 1) if isinstance(source, dict) else 1)
    merged["updated_at_utc"] = format_utc_stamp(utc_now())
    merged["images"] = dict(sorted(images.items()))
    return merged


def canonicalize_linked_td_status_records(
    output_root: Path,
    status: dict,
    td_typ_links: dict[tuple[str, int], dict],
    typ_names: dict[tuple[str, int], tuple[str, str]],
    *,
    dry_run: bool = False,
) -> bool:
    cycles = status.get("cycles") if isinstance(status, dict) else None
    if not isinstance(cycles, dict) or not td_typ_links:
        return False

    changed = False
    for cycle_key, cycle_records in cycles.items():
        if not isinstance(cycle_records, dict):
            continue
        for record in cycle_records.values():
            metadata = record.get("metadata") if isinstance(record, dict) else None
            if not isinstance(metadata, dict) or normalized_metadata_stage(metadata) != "TD":
                continue
            data_time = str(metadata.get("data_time") or cycle_key or "").strip()
            year = str(metadata.get("storm_year") or data_time[:4] or "").strip()
            td_number = metadata_int(metadata.get("typ_number"))
            row_link = td_typ_links.get((year, td_number)) if year and td_number else None
            if not isinstance(row_link, dict):
                continue

            linked_metadata = {
                **metadata,
                "linked_typ_number": row_link.get("linked_typ_number") or row_link.get("canonical_typ_number"),
                "canonical_storm_stage": "TYP",
                "canonical_typ_number": row_link.get("canonical_typ_number") or row_link.get("linked_typ_number"),
                "canonical_typ_name": row_link.get("canonical_typ_name") or metadata.get("canonical_typ_name"),
                "canonical_typ_name_ko": row_link.get("canonical_typ_name_ko") or metadata.get("canonical_typ_name_ko"),
            }
            target = canonical_target_for_linked_td_metadata(output_root, linked_metadata, typ_names)
            if target is None:
                continue
            target_dir, canonical_fields = target
            updated_metadata = rewrite_metadata_for_canonical_target(linked_metadata, target_dir, canonical_fields)
            if updated_metadata == metadata:
                continue
            changed = True
            if not dry_run:
                record["metadata"] = updated_metadata
    return changed


def canonicalize_linked_td_outputs(
    output_root: Path,
    *,
    dry_run: bool = False,
    td_typ_links: dict[tuple[str, int], dict] | None = None,
    restrict_to_linked_rows: bool = False,
    status: dict | None = None,
    status_path: Path | None = None,
) -> list[Path]:
    if not output_root.exists():
        return []
    td_typ_links = td_typ_links or {}
    if restrict_to_linked_rows and not td_typ_links:
        return []
    linked_years = {year for year, _ in td_typ_links} if restrict_to_linked_rows else None
    typ_names = existing_typ_name_lookup(output_root, years=linked_years)
    changed_paths: set[Path] = set()
    if canonicalize_linked_td_status_records(
        output_root,
        status or {},
        td_typ_links,
        typ_names,
        dry_run=dry_run,
    ):
        changed_paths.add(status_path or output_root / "status.json")
    for td_dir in sorted(output_root.glob("[0-9][0-9][0-9][0-9]/TD_*")):
        if not td_dir.is_dir():
            continue
        folder_match = re.match(r"^TD_(\d{2})(\d{2})_", td_dir.name, re.IGNORECASE)
        folder_td_number = int(folder_match.group(2)) if folder_match else None
        folder_year = str(td_dir.parent.name)
        row_link = td_typ_links.get((folder_year, folder_td_number)) if folder_td_number is not None else None
        if restrict_to_linked_rows and not isinstance(row_link, dict):
            continue
        run_paths = sorted((td_dir / "metadata" / "runs").glob("*.json"))
        if not run_paths:
            continue
        folder_manifest = load_json(td_dir / "manifest.json", {})
        fallback_linked_typ_number = metadata_int(folder_manifest.get("linked_typ_number")) if isinstance(folder_manifest, dict) else None
        if fallback_linked_typ_number is None and isinstance(row_link, dict):
            fallback_linked_typ_number = metadata_int(row_link.get("linked_typ_number"))
        target_dirs: set[Path] = set()
        migrated_any = False
        skipped_any = False
        for run_path in run_paths:
            metadata = load_json(run_path, None)
            if not isinstance(metadata, dict):
                skipped_any = True
                continue
            if isinstance(row_link, dict):
                metadata = {
                    **metadata,
                    "linked_typ_number": metadata.get("linked_typ_number") or row_link.get("linked_typ_number"),
                    "canonical_storm_stage": metadata.get("canonical_storm_stage") or "TYP",
                    "canonical_typ_number": metadata.get("canonical_typ_number") or row_link.get("canonical_typ_number"),
                    "canonical_typ_name": metadata.get("canonical_typ_name") or row_link.get("canonical_typ_name"),
                    "canonical_typ_name_ko": metadata.get("canonical_typ_name_ko") or row_link.get("canonical_typ_name_ko"),
                }
            target = canonical_target_for_linked_td_metadata(
                output_root,
                metadata,
                typ_names,
                fallback_linked_typ_number=fallback_linked_typ_number,
            )
            if target is None:
                skipped_any = True
                continue
            target_dir, canonical_fields = target
            target_dirs.add(target_dir)
            updated_metadata = rewrite_metadata_for_canonical_target(metadata, target_dir, canonical_fields)

            image_path = normalized_image_path(metadata.get("image_path"))
            if image_path:
                source_image = PROJECT_ROOT / image_path
                target_image = target_dir / "images" / source_image.name
                move_or_replace_file(source_image, target_image, changed_paths, dry_run=dry_run)

            target_run_path = target_dir / "metadata" / "runs" / run_path.name
            changed_paths.add(run_path)
            changed_paths.add(target_run_path)
            if not dry_run:
                write_json(target_run_path, updated_metadata)
                try:
                    run_path.unlink()
                except FileNotFoundError:
                    pass
            migrated_any = True

        if not migrated_any:
            continue

        for target_dir in sorted(target_dirs):
            source_availability_dir = td_dir / "metadata" / "source_availability"
            target_availability_dir = target_dir / "metadata" / "source_availability"
            for source_path in sorted(source_availability_dir.glob("*.json")) if source_availability_dir.exists() else []:
                if source_path.name == "summary.json":
                    continue
                payload = load_json(source_path, None)
                if isinstance(payload, dict):
                    if isinstance(row_link, dict):
                        payload = {
                            **payload,
                            "linked_typ_number": payload.get("linked_typ_number") or row_link.get("linked_typ_number"),
                            "canonical_storm_stage": payload.get("canonical_storm_stage") or "TYP",
                            "canonical_typ_number": payload.get("canonical_typ_number") or row_link.get("canonical_typ_number"),
                            "canonical_typ_name": payload.get("canonical_typ_name") or row_link.get("canonical_typ_name"),
                            "canonical_typ_name_ko": payload.get("canonical_typ_name_ko") or row_link.get("canonical_typ_name_ko"),
                        }
                    target = canonical_target_for_linked_td_metadata(
                        output_root,
                        payload,
                        typ_names,
                        fallback_linked_typ_number=fallback_linked_typ_number,
                    )
                    if target is not None:
                        _, canonical_fields = target
                        payload = rewrite_metadata_for_canonical_target(payload, target_dir, canonical_fields)
                        target_path = target_availability_dir / source_path.name
                        changed_paths.add(source_path)
                        changed_paths.add(target_path)
                        if not dry_run:
                            write_json(target_path, payload)
                            source_path.unlink(missing_ok=True)

            source_summary_path = source_availability_dir / "summary.json"
            if source_summary_path.exists():
                target_summary_path = target_availability_dir / "summary.json"
                changed_paths.add(source_summary_path)
                changed_paths.add(target_summary_path)
                if not dry_run:
                    source_summary_path.unlink(missing_ok=True)
                    target_summary_path.unlink(missing_ok=True)

            source_history_path = td_dir / "metadata" / "track_history.json"
            if source_history_path.exists():
                target_history_path = target_dir / "metadata" / "track_history.json"
                source_history = load_json(source_history_path, {})
                target_history = load_json(target_history_path, {})
                target_manifest = load_json(target_dir / "manifest.json", {})
                canonical_key = str(target_manifest.get("storm_key") or "")
                if not canonical_key:
                    match = re.match(r"^TYP_(\d{2})(\d{2})_", target_dir.name)
                    canonical_key = f"typ_{target_dir.parent.name}_{int(match.group(2)):02d}" if match else ""
                aliases = [canonical_key, f"td_{td_dir.parent.name}_{td_dir.name[5:7]}"]
                merged_history = merge_track_history_payloads(target_history, source_history, canonical_key=canonical_key, aliases=aliases)
                changed_paths.add(source_history_path)
                changed_paths.add(target_history_path)
                if not dry_run:
                    write_json(target_history_path, merged_history)
                    source_history_path.unlink(missing_ok=True)

            source_drive_path = td_dir / "drive_archive.json"
            if source_drive_path.exists():
                target_drive_path = target_dir / "drive_archive.json"
                source_drive = load_json(source_drive_path, {})
                target_drive = load_json(target_drive_path, {})
                target_manifest = load_json(target_dir / "manifest.json", {})
                canonical_key = str(target_manifest.get("storm_key") or "")
                merged_drive = merge_drive_archive_payload(target_drive, source_drive, td_dir, target_dir, canonical_key)
                changed_paths.add(source_drive_path)
                changed_paths.add(target_drive_path)
                if not dry_run:
                    write_json(target_drive_path, merged_drive)
                    source_drive_path.unlink(missing_ok=True)

        changed_paths.add(td_dir / "manifest.json")
        if not dry_run and not skipped_any:
            shutil.rmtree(td_dir, ignore_errors=True)
        elif dry_run:
            print(f"Would canonicalize linked TD folder: {td_dir}")
    return sorted(changed_paths)


def track_history_canonical_key_from_path(path: Path) -> str:
    try:
        system_dir = path.parents[1]
        year = system_dir.parent.name
    except IndexError:
        return ""
    match = re.match(r"^(TYP|TD)_(\d{2})(\d{2})_", system_dir.name, re.IGNORECASE)
    if not match or not re.fullmatch(r"\d{4}", year):
        return ""
    prefix = "typ" if match.group(1).upper() == "TYP" else "td"
    number = int(match.group(3))
    return f"{prefix}_{year}_{number:02d}"


def normalize_track_history_primary_keys(output_root: Path, *, dry_run: bool = False) -> list[Path]:
    """Ensure canonical system folders own their track-history primary_key.

    Linked TD histories are allowed as aliases, but a TYP canonical folder should
    not keep a TD key as primary_key. This keeps later merges and index rebuilds
    deterministic after TD -> TYP absorption.
    """
    changed: list[Path] = []
    for path in sorted(output_root.glob("[0-9][0-9][0-9][0-9]/*/metadata/track_history.json")):
        payload = load_json(path, None)
        if not isinstance(payload, dict):
            continue
        canonical_key = track_history_canonical_key_from_path(path)
        if not canonical_key:
            continue
        previous_primary = str(payload.get("primary_key") or "").strip()
        aliases = {
            str(item or "").strip()
            for item in payload.get("aliases", [])
            if str(item or "").strip()
        }
        if previous_primary:
            aliases.add(previous_primary)
        aliases.add(canonical_key)
        updated = dict(payload)
        updated["primary_key"] = canonical_key
        updated["aliases"] = sorted(aliases)
        if updated == payload:
            continue
        changed.append(path)
        if dry_run:
            print(
                f"Would normalize track history primary_key: {path} "
                f"({previous_primary or '-'} -> {canonical_key})"
            )
            continue
        write_json(path, updated)
        print(
            f"Normalized track history primary_key: {path} "
            f"({previous_primary or '-'} -> {canonical_key})"
        )
    return changed


def status_key_for(job: StormJob, fcst_hours: int) -> str:
    return f"{job.storm_key}_{fcst_hours}h"


def redacted_command(command: list[str]) -> list[str]:
    redacted = command.copy()
    for index, value in enumerate(redacted[:-1]):
        if value == "--auth-key":
            redacted[index + 1] = "***"
    return redacted


def text_tail(value: str | None, limit: int = 4000) -> str:
    text = str(value or "")
    if len(text) <= limit:
        return text
    return text[-limit:]


def print_process_output_tail(
    *,
    stdout: str | None,
    stderr: str | None,
    prefix: str,
    limit: int = 4000,
) -> None:
    stderr_tail = text_tail(stderr, limit).strip()
    stdout_tail = text_tail(stdout, limit).strip()
    if stderr_tail:
        print(f"--- {prefix} stderr tail ---", file=sys.stderr)
        print(stderr_tail, file=sys.stderr)
    if stdout_tail:
        print(f"--- {prefix} stdout tail ---", file=sys.stderr)
        print(stdout_tail, file=sys.stderr)


def print_process_timings(stdout: str | None, *, prefix: str) -> None:
    timing_lines = [line for line in str(stdout or "").splitlines() if line.startswith("[timing]")]
    if not timing_lines:
        return
    print(f"--- {prefix} timing ---")
    for line in timing_lines:
        print(line)


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
            f"retrying in {retry_delay_seconds}s ({attempt + 1}/{retries}).",
            file=sys.stderr,
        )
        print_process_output_tail(
            stdout=completed.stdout,
            stderr=completed.stderr,
            prefix="VTG transient failure",
            limit=3000,
        )
        time.sleep(retry_delay_seconds)

    assert completed is not None
    return completed


def vtg_command(
    *,
    job: StormJob,
    output_root: Path,
    auth_key: str,
    fallback_auth_key: str,
    python: str,
    fcst_hours_list: list[int],
    auto_fcst_hours: bool,
    source_overrides: list[str],
    kma_forecast_text_path: Path | None = None,
    kma_past_text_path: Path | None = None,
    http_cache_dir: Path | None = None,
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
        "--storm-year",
        str(job.year),
        "--fcst-hours",
        ",".join(str(fcst_hours) for fcst_hours in unique_hours),
        "--output-root",
        str(output_root),
        "--auth-key",
        auth_key,
        "--overwrite",
        "--no-show",
    ]
    if fallback_auth_key:
        command.extend(["--fallback-auth-key", fallback_auth_key])
    if kma_forecast_text_path is not None:
        command.extend(["--kma-forecast-text-path", str(kma_forecast_text_path)])
    if kma_past_text_path is not None:
        command.extend(["--kma-past-text-path", str(kma_past_text_path)])
    if http_cache_dir is not None:
        command.extend(["--http-cache-dir", str(http_cache_dir)])
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
    command.extend([
        "--canonical-storm-stage",
        canonical_stage_for_job(job),
        "--canonical-typ-number",
        str(canonical_typ_number_for_job(job)),
        "--canonical-typ-name",
        canonical_typ_name_for_job(job),
    ])
    canonical_name_ko = canonical_typ_name_ko_for_job(job)
    if canonical_name_ko:
        command.extend(["--canonical-typ-name-ko", canonical_name_ko])
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
    fallback_auth_key: str,
    python: str,
    fcst_hours_list: list[int],
    auto_fcst_hours: bool,
    source_overrides: list[str],
    dry_run: bool,
    clear_existing: bool = False,
    kma_forecast_text_path: Path | None = None,
    kma_past_text_path: Path | None = None,
    http_cache_dir: Path | None = None,
) -> dict[int, dict]:
    command, metadata_paths = vtg_command(
        job=job,
        output_root=output_root,
        auth_key=auth_key,
        fallback_auth_key=fallback_auth_key,
        python=python,
        fcst_hours_list=fcst_hours_list,
        auto_fcst_hours=auto_fcst_hours,
        source_overrides=source_overrides,
        kma_forecast_text_path=kma_forecast_text_path,
        kma_past_text_path=kma_past_text_path,
        http_cache_dir=http_cache_dir,
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
    timing_started_at = time.monotonic()
    completed = run_command_with_network_retry(
        command,
        cwd=PROJECT_ROOT,
        retries=1,
        retry_delay_seconds=60,
    )
    print_process_timings(completed.stdout, prefix=f"VTG.py {job.storm_key}")
    log_timing(f"VTG.py {job.storm_key} hours={','.join(str(item) for item in metadata_paths)}", timing_started_at)
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


def record_batch_results(
    *,
    job: StormJob,
    window: CycleWindow,
    due_hours: list[int],
    batch_results: dict[int, dict],
    output_root: Path,
    cycle_status: dict,
    run_entries: list[dict],
    complete_model_count: int,
    final_check_window: bool,
    now: datetime,
) -> None:
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
        completed = model_count >= complete_model_count
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


def manifest_entry_from_metadata(path: Path, metadata: dict) -> dict:
    data_time = str(metadata.get("data_time") or "")
    year = int(str(metadata.get("storm_year") or data_time[:4] or "0") or 0)
    typ_number = int(metadata.get("typ_number") or 0)
    stage = str(metadata.get("storm_stage") or "TYP")
    canonical_fields = canonical_metadata_fields(metadata)
    storm_key = canonical_fields.get("canonical_storm_key") or path.stem
    enriched_metadata = {**metadata, **canonical_fields}
    return {
        "job": {
            "storm_key": storm_key,
            "stage": stage,
            "year": year,
            "data_time": data_time,
            "td_number": metadata.get("typ_number") if stage.upper() == "TD" else None,
            "linked_td_number": metadata.get("linked_td_number"),
            "linked_typ_number": metadata.get("linked_typ_number"),
            "canonical_storm_stage": canonical_fields.get("canonical_storm_stage"),
            "canonical_typ_number": canonical_fields.get("canonical_typ_number"),
            "canonical_typ_name": canonical_fields.get("canonical_typ_name"),
            "canonical_typ_name_ko": canonical_fields.get("canonical_typ_name_ko"),
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
        "result": {"status": "inventory", "metadata": compact_metadata(enriched_metadata)},
        "metadata_path": relative_asset_path(path),
    }


def relative_asset_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def metadata_referenced_path_exists(metadata: dict, key: str) -> bool:
    value = str(metadata.get(key) or "").strip()
    if not value:
        return False
    path = Path(value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.exists()


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

    try:
        parent_year = path.parents[2].name
    except IndexError:
        parent_year = ""
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
        if key not in metadata:
            continue
        if key == "source_availability_path":
            if not metadata_referenced_path_exists(metadata, key):
                continue
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
    if output_root.exists():
        for path in sorted(output_root.glob("[0-9][0-9][0-9][0-9]/*/metadata/runs/*.json")):
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
        for path in sorted(output_root.glob("[0-9][0-9][0-9][0-9]/*/images/*.png")):
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
        result_status = str(entry.get("result", {}).get("status") or "")
        if result_status == "suppressed_td_phase":
            entries_by_key.pop(key, None)
            continue
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
            canonical_typ_number_from_metadata(item.get("result", {}).get("metadata", {}) or {}) or item.get("job", {}).get("typ_number") or 0,
            item.get("job", {}).get("data_time") or "",
            item.get("result", {}).get("metadata", {}).get("fcst_hours") or 0,
        ),
    )


def sort_manifest_inventory(entries: list[dict]) -> list[dict]:
    return sorted(
        entries,
        key=lambda item: (
            item.get("job", {}).get("year") or 0,
            canonical_typ_number_from_metadata(item.get("result", {}).get("metadata", {}) or {}) or item.get("job", {}).get("typ_number") or 0,
            item.get("job", {}).get("data_time") or "",
            item.get("result", {}).get("metadata", {}).get("fcst_hours") or 0,
        ),
    )


def manifest_storm_key_from_metadata(metadata: dict) -> str:
    return canonical_storm_key_from_metadata(metadata)


def manifest_storm_key_from_entry(entry: dict) -> str:
    metadata = entry.get("result", {}).get("metadata") if isinstance(entry, dict) else None
    if isinstance(metadata, dict) and metadata:
        return manifest_storm_key_from_metadata(metadata)
    job = entry.get("job") if isinstance(entry, dict) else None
    if isinstance(job, dict) and job.get("storm_key"):
        return str(job.get("storm_key"))
    return "unknown"


def storm_manifest_path_from_summary(output_root: Path, summary: dict) -> Path:
    year = summary.get("year") or ""
    stage = summary.get("stage") or "TYP"
    typ_number = safe_int(summary.get("typ_number")) or 0
    typ_name = summary.get("typ_name") or "NONAME"
    return output_root / str(year) / system_dir_name_for_parts(year, stage, typ_number, typ_name) / "manifest.json"


def valid_storm_summary(summary: dict) -> bool:
    year = safe_int(summary.get("year"))
    typ_number = safe_int(summary.get("typ_number"))
    stage = str(summary.get("stage") or "").upper()
    return year is not None and year >= 1900 and typ_number is not None and typ_number > 0 and stage in {"TD", "TYP"}


def year_manifest_index_path(output_root: Path, year: int | str) -> Path:
    return output_root / str(year) / "index.json"


def entry_from_existing_manifest_item(item: dict) -> dict:
    if not isinstance(item, dict):
        return {}
    # Existing items are already compact manifest entries.
    return item


def merge_manifest_inventory(existing_inventory: list[dict], run_entries: list[dict]) -> list[dict]:
    entries_by_key: dict[str, dict] = {}
    suppressed_tokens: set[str] = set()

    for entry in existing_inventory or []:
        entry = entry_from_existing_manifest_item(entry)
        metadata = entry.get("result", {}).get("metadata") if isinstance(entry, dict) else None
        if not isinstance(metadata, dict) or not metadata:
            continue
        try:
            fcst_hours = int(metadata.get("fcst_hours") or 0)
        except (TypeError, ValueError):
            continue
        if fcst_hours not in VALID_FCST_HOURS:
            continue
        if metadata_matches_suppression(metadata, suppressed_tokens):
            continue
        entries_by_key[manifest_inventory_key(metadata)] = entry

    for entry in run_entries:
        metadata = entry.get("result", {}).get("metadata") if isinstance(entry, dict) else None
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

    return sort_manifest_inventory(list(entries_by_key.values()))


def storm_summary_from_inventory(storm_key: str, inventory: list[dict]) -> dict:
    latest_entry = None
    for entry in inventory:
        metadata = entry.get("result", {}).get("metadata", {}) if isinstance(entry, dict) else {}
        if not isinstance(metadata, dict):
            continue
        if latest_entry is None or str(metadata.get("data_time") or "") >= str(latest_entry.get("result", {}).get("metadata", {}).get("data_time") or ""):
            latest_entry = entry
    metadata = latest_entry.get("result", {}).get("metadata", {}) if isinstance(latest_entry, dict) else {}
    job = latest_entry.get("job", {}) if isinstance(latest_entry, dict) else {}
    canonical_stage = canonical_stage_from_metadata(metadata) if isinstance(metadata, dict) else ""
    canonical_typ_number = canonical_typ_number_from_metadata(metadata) if isinstance(metadata, dict) else None
    canonical_typ_name = canonical_typ_name_from_metadata(metadata) if isinstance(metadata, dict) else "NONAME"
    canonical_typ_name_ko = canonical_typ_name_ko_from_metadata(metadata) if isinstance(metadata, dict) else ""
    actual_stage = normalized_metadata_stage(metadata) if isinstance(metadata, dict) else ""
    linked_td_number = job.get("linked_td_number") or metadata.get("linked_td_number")
    if canonical_stage == "TYP" and actual_stage == "TD":
        linked_td_number = linked_td_number or metadata_int(metadata.get("typ_number"))
    return {
        "storm_key": storm_key,
        "stage": canonical_stage or job.get("stage") or metadata.get("storm_stage") or "",
        "year": job.get("year") or metadata.get("storm_year") or "",
        "typ_number": canonical_typ_number or job.get("typ_number") or metadata.get("typ_number") or 0,
        "linked_td_number": linked_td_number,
        "linked_typ_number": None if canonical_stage == "TYP" else (job.get("linked_typ_number") or metadata.get("linked_typ_number")),
        "typ_name": canonical_typ_name or job.get("typ_name") or metadata.get("typ_name") or "NONAME",
        "typ_name_ko": canonical_typ_name_ko or job.get("typ_name_ko") or metadata.get("typ_name_ko") or "",
        "latest_data_time": metadata.get("data_time") or "",
        "item_count": len(inventory),
    }


def manifest_payload_changed(previous: dict, payload: dict) -> bool:
    if previous == payload:
        return False
    if isinstance(previous, dict) and previous.get("updated_at_utc"):
        comparable = dict(payload)
        comparable["updated_at_utc"] = previous.get("updated_at_utc")
        if previous == comparable:
            return False
    return True


def storm_manifest_payload(
    storm_key: str,
    inventory: list[dict],
    *,
    updated_at_utc: str,
) -> tuple[dict, dict] | None:
    summary = storm_summary_from_inventory(storm_key, inventory)
    if not valid_storm_summary(summary):
        return None
    return summary, {
        "version": 2,
        "updated_at_utc": updated_at_utc,
        **summary,
        "inventory": inventory,
    }


def year_manifest_payload(year: str, systems: list[dict], *, updated_at_utc: str) -> dict:
    return {
        "version": 2,
        "updated_at_utc": updated_at_utc,
        "year": int(year) if year.isdigit() else year,
        "systems": sorted(systems, key=lambda item: (item.get("typ_number") or 0, item.get("storm_key") or "")),
    }


def write_split_manifest_files(output_root: Path, run_entries: list[dict], *, updated_at_utc: str) -> list[Path]:
    changed_paths: list[Path] = []
    entries_by_storm: dict[tuple[str, str], list[dict]] = {}
    for entry in run_entries:
        metadata = entry.get("result", {}).get("metadata") if isinstance(entry, dict) else None
        if not isinstance(metadata, dict) or not metadata:
            continue
        year = str(metadata.get("storm_year") or metadata.get("data_time", "")[:4] or "0")
        storm_key = manifest_storm_key_from_entry(entry)
        if not year or storm_key == "unknown":
            continue
        entries_by_storm.setdefault((year, storm_key), []).append(entry)

    touched_years: set[str] = set()
    touched_systems: dict[str, list[dict]] = {}
    for (year, storm_key), entries in sorted(entries_by_storm.items()):
        path = storm_manifest_path_from_summary(output_root, storm_summary_from_inventory(storm_key, entries))
        previous = load_json(path, {})
        previous_inventory = previous.get("inventory") if isinstance(previous, dict) else []
        if not isinstance(previous_inventory, list):
            previous_inventory = []
        inventory = merge_manifest_inventory(previous_inventory, entries)
        manifest_parts = storm_manifest_payload(storm_key, inventory, updated_at_utc=updated_at_utc)
        if manifest_parts is None:
            continue
        summary, payload = manifest_parts
        if manifest_payload_changed(previous, payload):
            write_json(path, payload)
            changed_paths.append(path)
        touched_years.add(str(year))
        summary["manifest_path"] = relative_asset_path(path)
        touched_systems.setdefault(str(year), []).append(summary)

    for year in sorted(touched_years):
        path = year_manifest_index_path(output_root, year)
        previous = load_json(path, {})
        systems = previous.get("systems") if isinstance(previous, dict) else []
        if not isinstance(systems, list):
            systems = []
        by_key = {
            str(item.get("storm_key")): item
            for item in systems
            if isinstance(item, dict) and item.get("storm_key")
        }
        for item in touched_systems.get(year, []):
            by_key[str(item["storm_key"])] = item
        payload = year_manifest_payload(year, list(by_key.values()), updated_at_utc=updated_at_utc)
        if manifest_payload_changed(previous, payload):
            write_json(path, payload)
            changed_paths.append(path)

    return changed_paths


def rebuild_split_manifest_files(output_root: Path, inventory: list[dict], *, updated_at_utc: str) -> list[Path]:
    changed_paths: list[Path] = []
    grouped: dict[tuple[str, str], list[dict]] = {}
    for entry in inventory:
        metadata = entry.get("result", {}).get("metadata") if isinstance(entry, dict) else None
        if not isinstance(metadata, dict) or not metadata:
            continue
        year = str(metadata.get("storm_year") or metadata.get("data_time", "")[:4] or "0")
        storm_key = manifest_storm_key_from_metadata(metadata)
        if not year or storm_key == "unknown":
            continue
        grouped.setdefault((year, storm_key), []).append(entry)

    systems_by_year: dict[str, list[dict]] = {}
    for (year, storm_key), entries in sorted(grouped.items()):
        storm_inventory = sort_manifest_inventory(entries)
        manifest_parts = storm_manifest_payload(storm_key, storm_inventory, updated_at_utc=updated_at_utc)
        if manifest_parts is None:
            continue
        summary, payload = manifest_parts
        path = storm_manifest_path_from_summary(output_root, summary)
        previous = load_json(path, {})
        if manifest_payload_changed(previous, payload):
            write_json(path, payload)
            changed_paths.append(path)
        summary["manifest_path"] = relative_asset_path(path)
        systems_by_year.setdefault(str(year), []).append(summary)

    for year, systems in sorted(systems_by_year.items()):
        path = year_manifest_index_path(output_root, year)
        payload = year_manifest_payload(year, systems, updated_at_utc=updated_at_utc)
        previous = load_json(path, {})
        if manifest_payload_changed(previous, payload):
            write_json(path, payload)
            changed_paths.append(path)
    return changed_paths


def root_manifest_indexes(output_root: Path) -> list[dict]:
    indexes = []
    if not output_root.exists():
        return indexes
    for path in sorted(output_root.glob("[0-9][0-9][0-9][0-9]/index.json")):
        year = path.parent.name
        indexes.append({"year": int(year), "path": relative_asset_path(path)})
    return indexes


def split_manifest_inventory_count(output_root: Path, indexes: list[dict] | None = None) -> int:
    total = 0
    for item in indexes if indexes is not None else root_manifest_indexes(output_root):
        path = PROJECT_ROOT / str(item.get("path") or "")
        payload = load_json(path, {})
        systems = payload.get("systems") if isinstance(payload, dict) else []
        if not isinstance(systems, list):
            continue
        for system in systems:
            if isinstance(system, dict):
                try:
                    total += int(system.get("item_count") or 0)
                except (TypeError, ValueError):
                    continue
    return total


def root_manifest_payload(
    *,
    updated_at_utc: str,
    windows: list[CycleWindow],
    complete_model_count: int,
    final_check_before_window_end_minutes: int,
    runs: list[dict],
    output_root: Path,
    inventory_count: int = 0,
    manifest_indexes: list[dict] | None = None,
) -> dict:
    return {
        "version": 3,
        "updated_at_utc": updated_at_utc,
        "window_start_offset_hours": WINDOW_START_OFFSET_HOURS,
        "window_end_offset_hours": WINDOW_END_OFFSET_HOURS,
        "complete_model_count": complete_model_count,
        "final_check_before_window_end_minutes": final_check_before_window_end_minutes,
        "active_windows": [asdict(window) for window in windows],
        "runs": runs,
        "inventory_count": inventory_count,
        "manifest_indexes": manifest_indexes if manifest_indexes is not None else root_manifest_indexes(output_root),
    }


def collect_changed_asset_paths(
    *,
    run_entries: list[dict],
    manifest_path: Path,
    status_path: Path,
    split_manifest_paths: list[Path],
    include_manifest: bool = True,
    include_status: bool = True,
) -> list[str]:
    paths: set[str] = set()
    output_root = manifest_path.parent
    if include_manifest:
        paths.add(relative_asset_path(manifest_path))
    if include_status:
        paths.add(relative_asset_path(status_path))
    for path in split_manifest_paths:
        paths.add(relative_asset_path(path))
    for entry in run_entries:
        result = entry.get("result") if isinstance(entry, dict) else {}
        if isinstance(result, dict):
            metadata_path = result.get("metadata_path")
            if metadata_path:
                paths.add(relative_asset_path(Path(str(metadata_path))))
            metadata = result.get("metadata")
            if isinstance(metadata, dict):
                image_path = str(metadata.get("image_path") or "").strip()
                if image_path:
                    paths.add(relative_asset_path(PROJECT_ROOT / image_path))
                for availability_key in ("source_availability_path", "smca_aicon_snapshot_path"):
                    availability_path = str(metadata.get(availability_key) or "").strip()
                    if availability_path and (PROJECT_ROOT / availability_path).exists():
                        paths.add(relative_asset_path(PROJECT_ROOT / availability_path))
                for history_path in track_history_paths_from_metadata(output_root, metadata):
                    paths.add(relative_asset_path(history_path))
    return sorted(paths)


def write_changed_paths(path: Path | None, paths: list[str]) -> None:
    if path is None:
        return
    unique_paths = sorted({str(item).strip() for item in paths if str(item).strip()})
    path.write_text("\n".join(unique_paths) + ("\n" if unique_paths else ""), encoding="utf-8")


def print_manifest_or_summary(manifest: dict, *, verbose: bool, changed_paths: list[str] | None = None) -> None:
    if verbose:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return
    summary = {
        "updated_at_utc": manifest.get("updated_at_utc"),
        "active_windows": manifest.get("active_windows", []),
        "run_count": len(manifest.get("runs", []) or []),
        "inventory_count": manifest.get("inventory_count", len(manifest.get("inventory", []) or [])),
        "manifest_indexes": manifest.get("manifest_indexes", []),
    }
    if changed_paths is not None:
        summary["changed_path_count"] = len(changed_paths)
        summary["changed_paths_preview"] = changed_paths[:30]
    print(json.dumps(summary, ensure_ascii=False, indent=2))


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
    parser.add_argument("--output-root", type=Path, default=PROJECT_ROOT / "data")
    parser.add_argument("--kma-cache-dir", type=Path, default=None)
    parser.add_argument("--auth-key", default=os.getenv("KMA_APIHUB_AUTH_KEY", ""))
    parser.add_argument("--manual-map", type=Path, default=PROJECT_ROOT / "vtg_manual_atcf_map.json")
    parser.add_argument("--status-path", type=Path, default=None)
    parser.add_argument("--manifest-path", type=Path, default=None)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--fcst-hours", default="120,240", help="Comma/space separated forecast hours to generate.")
    parser.add_argument(
        "--fallback-auth-key",
        default=os.getenv("KMA_APIHUB_FALLBACK_AUTH_KEY", KMA_FALLBACK_AUTH_KEY),
        help="Optional fallback KMA APIHUB auth key for apihub.kma.go.kr.",
    )
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
    parser.add_argument("--changed-paths-file", type=Path, default=None, help="Write generated/updated asset paths for git add --pathspec-from-file.")
    parser.add_argument("--verbose-manifest", action="store_true", help="Print full manifest JSON instead of a compact summary.")
    parser.add_argument("--full-manifest-scan", action="store_true", help="Scan all VTG data assets on every run. Default uses incremental manifest updates.")
    parser.add_argument("--http-cache-dir", type=Path, default=None, help="Shared workflow-local HTTP/KMA cache directory for VTG.py subprocesses.")
    parser.add_argument("--parallel-jobs", type=int, default=int(os.getenv("VTG_PARALLEL_JOBS", "2")), help="Maximum active storm VTG.py subprocesses per cycle.")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    global KMA_FALLBACK_AUTH_KEY
    KMA_FALLBACK_AUTH_KEY = str(args.fallback_auth_key or "").strip()
    explicit_cycle_time: datetime | None = None
    if args.now:
        cycle = parse_cycle_override(args.now)
        if cycle is None:
            raise SystemExit("--now must be target cycle YYYYmmddHH, with HH one of 00, 06, 12, 18.")
        explicit_cycle_time = cycle
        now = cycle_probe_time(cycle)
        print(
            f"Cycle override: {format_utc_stamp(cycle)} -> window probe time {format_utc_stamp(now)} "
            f"(activity judged at cycle time {format_utc_stamp(cycle)})"
        )
    else:
        now = utc_now()

    output_root = args.output_root
    kma_cache_dir = args.kma_cache_dir or output_root / "cache" / "kma_apihub"
    status_path = args.status_path or output_root / "status.json"
    manifest_path = args.manifest_path or output_root / "manifest.json"
    http_cache_dir = args.http_cache_dir or Path(tempfile.gettempdir()) / "vtg_http_cache"
    http_cache_dir.mkdir(parents=True, exist_ok=True)
    global HTTP_FETCH_CACHE_DIR
    HTTP_FETCH_CACHE_DIR = http_cache_dir
    parallel_jobs = max(1, int(args.parallel_jobs or 1))
    windows = active_cycle_windows(now)
    status = load_json(status_path, {"cycles": {}})
    manual_map = load_manual_map(args.manual_map)

    if args.index_only:
        updated_at_utc = format_utc_stamp(now)
        td_typ_links: dict[tuple[str, int], dict] = {}
        years_for_index = {
            int(path.name)
            for path in output_root.glob("[0-9][0-9][0-9][0-9]")
            if path.is_dir() and path.name.isdigit()
        }
        if not years_for_index:
            years_for_index.add(now.year)
        if args.auth_key:
            td_rows_for_index: list[dict] = []
            typ_rows_for_index: list[dict] = []
            for year in sorted(years_for_index):
                try:
                    td_rows_for_index.extend(fetch_td_rows(year, args.auth_key, cache_dir=kma_cache_dir))
                    typ_rows_for_index.extend(fetch_typ_rows(year, args.auth_key, cache_dir=kma_cache_dir))
                except Exception as exc:
                    print(f"Warning: failed to load KMA TD/TYP rows for index-only canonicalization {year}: {exc}")
            td_typ_links = td_typ_link_lookup(td_rows_for_index, typ_rows_for_index)
        canonicalized_paths = canonicalize_linked_td_outputs(
            output_root,
            dry_run=args.dry_run,
            td_typ_links=td_typ_links,
            status=status,
            status_path=status_path,
        )
        canonical_status_changed = status_path in canonicalized_paths
        canonicalized_paths.extend(normalize_track_history_primary_keys(output_root, dry_run=args.dry_run))
        inventory = build_manifest_inventory(output_root, [])
        split_paths = [] if args.dry_run else rebuild_split_manifest_files(output_root, inventory, updated_at_utc=updated_at_utc)
        manifest_indexes = root_manifest_indexes(output_root)
        manifest = root_manifest_payload(
            updated_at_utc=updated_at_utc,
            windows=windows,
            complete_model_count=args.complete_model_count,
            final_check_before_window_end_minutes=args.final_check_before_window_end_minutes,
            runs=[],
            output_root=output_root,
            inventory_count=len(inventory),
            manifest_indexes=manifest_indexes,
        )
        status_for_write = prune_status_for_persistence(
            status,
            active_data_times={window.data_time for window in windows},
            retention_days=args.status_retention_days,
            reference_time=utc_now(),
        )
        changed_paths = collect_changed_asset_paths(
            run_entries=[],
            manifest_path=manifest_path,
            status_path=status_path,
            split_manifest_paths=split_paths,
            include_manifest=True,
            include_status=status_for_write != status or canonical_status_changed,
        )
        changed_paths.extend(relative_asset_path(path) for path in canonicalized_paths)
        changed_paths.extend(relative_asset_path(path) for path in kma_cache_asset_paths(kma_cache_dir, years_for_index))
        changed_paths = sorted(set(changed_paths))
        if not args.dry_run:
            write_json(manifest_path, manifest)
            if status_for_write != status or canonical_status_changed:
                write_json(status_path, status_for_write)
        write_changed_paths(args.changed_paths_file, changed_paths)
        print_manifest_or_summary(manifest, verbose=args.verbose_manifest, changed_paths=changed_paths)
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

    years = kma_list_years_for_windows(windows, now)

    td_rows: list[dict] = []
    typ_rows: list[dict] = []
    for year in sorted(years):
        td_rows.extend(fetch_td_rows(year, args.auth_key, cache_dir=kma_cache_dir))
        typ_rows.extend(fetch_typ_rows(year, args.auth_key, cache_dir=kma_cache_dir))

    latest_td_number = max((safe_int(row.get("TD")) or 0 for row in td_rows), default=0)
    latest_typ_number = max((safe_int(row.get("SEQ")) or 0 for row in typ_rows), default=0)
    print(
        "KMA activity lists: "
        f"td_rows={len(td_rows)} latest_td={latest_td_number:02d} "
        f"typ_rows={len(typ_rows)} latest_typ={latest_typ_number:02d}"
    )

    td_typ_links = td_typ_link_lookup(td_rows, typ_rows)

    run_entries = []
    removed_artifact_paths: set[Path] = set()
    actual_run_count = 0
    render_signature = current_render_signature()
    for window in windows:
        window_started_at = time.monotonic()
        cycle_status = status.setdefault("cycles", {}).setdefault(window.data_time, {})
        final_check_window = is_final_check_window(
            now,
            window,
            args.final_check_before_window_end_minutes,
        )

        kma_forecast_text_path = None
        kma_past_text_path = None
        kma_forecast_text = None
        if not args.check_run_needed:
            kma_forecast_text_path = ensure_kma_gts_now_cache(
                data_time=window.data_time,
                auth_key=args.auth_key,
                cache_dir=http_cache_dir,
                mode="2",
            )
            kma_forecast_text = read_optional_text(kma_forecast_text_path)

        job_started_at = time.monotonic()
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
            kma_gts_now_text=kma_forecast_text,
            activity_cycle_time=explicit_cycle_time,
            status=status,
        )
        log_timing(f"build storm jobs {window.data_time} jobs={len(jobs)}", job_started_at)

        run_entries.extend(remove_obsolete_typ_artifacts_for_td_phases(
            output_root=output_root,
            jobs=jobs,
            fcst_hours_list=fcst_hours_list,
            cycle_status=cycle_status,
            window=window,
            dry_run=args.dry_run or args.check_run_needed,
            changed_paths=removed_artifact_paths,
        ))

        pending_batches: list[tuple[StormJob, list[int], bool]] = []
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
            pending_batches.append((job, due_hours, final_check_window))

        if pending_batches:
            kma_past_text_path = ensure_kma_gts_now_cache(
                data_time=window.data_time,
                auth_key=args.auth_key,
                cache_dir=http_cache_dir,
                mode="0",
            )

            worker_count = min(parallel_jobs, len(pending_batches))
            print(
                f"Running {len(pending_batches)} active storm job(s) for {window.data_time} "
                f"with parallel_jobs={worker_count}."
            )
            render_started_at = time.monotonic()

            if worker_count == 1:
                for job, due_hours, batch_final_check_window in pending_batches:
                    batch_results = run_vtg_batch(
                        job=job,
                        output_root=output_root,
                        auth_key=args.auth_key,
                        fallback_auth_key=KMA_FALLBACK_AUTH_KEY,
                        python=args.python,
                        fcst_hours_list=due_hours,
                        auto_fcst_hours=args.auto_fcst_hours,
                        source_overrides=args.source_override,
                        dry_run=args.dry_run,
                        clear_existing=args.force,
                        kma_forecast_text_path=kma_forecast_text_path,
                        kma_past_text_path=kma_past_text_path,
                        http_cache_dir=http_cache_dir,
                    )
                    record_batch_results(
                        job=job,
                        window=window,
                        due_hours=due_hours,
                        batch_results=batch_results,
                        output_root=output_root,
                        cycle_status=cycle_status,
                        run_entries=run_entries,
                        complete_model_count=args.complete_model_count,
                        final_check_window=batch_final_check_window,
                        now=now,
                    )
            else:
                with ThreadPoolExecutor(max_workers=worker_count) as executor:
                    futures = {
                        executor.submit(
                            run_vtg_batch,
                            job=job,
                            output_root=output_root,
                            auth_key=args.auth_key,
                            fallback_auth_key=KMA_FALLBACK_AUTH_KEY,
                            python=args.python,
                            fcst_hours_list=due_hours,
                            auto_fcst_hours=args.auto_fcst_hours,
                            source_overrides=args.source_override,
                            dry_run=args.dry_run,
                            clear_existing=args.force,
                            kma_forecast_text_path=kma_forecast_text_path,
                            kma_past_text_path=kma_past_text_path,
                            http_cache_dir=http_cache_dir,
                        ): (job, due_hours, batch_final_check_window)
                        for job, due_hours, batch_final_check_window in pending_batches
                    }
                    for future in as_completed(futures):
                        job, due_hours, batch_final_check_window = futures[future]
                        try:
                            batch_results = future.result()
                        except Exception as exc:
                            batch_results = {
                                fcst_hours: {
                                    "status": "failed",
                                    "metadata_path": str(metadata_path_for(output_root, job, fcst_hours)),
                                    "stderr": f"VTG batch raised an exception: {exc}",
                                }
                                for fcst_hours in due_hours
                            }
                        record_batch_results(
                            job=job,
                            window=window,
                            due_hours=due_hours,
                            batch_results=batch_results,
                            output_root=output_root,
                            cycle_status=cycle_status,
                            run_entries=run_entries,
                            complete_model_count=args.complete_model_count,
                            final_check_window=batch_final_check_window,
                            now=now,
                        )

            log_timing(f"render active storm batches {window.data_time}", render_started_at)
        log_timing(f"cycle total before manifest {window.data_time}", window_started_at)

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

    canonicalized_paths = canonicalize_linked_td_outputs(
        output_root,
        dry_run=args.dry_run,
        td_typ_links=td_typ_links,
        restrict_to_linked_rows=True,
        status=status,
        status_path=status_path,
    )
    canonical_status_changed = status_path in canonicalized_paths
    previous_manifest = load_json(manifest_path, {})
    compact_runs = compact_manifest_runs(run_entries)
    updated_at_utc = format_utc_stamp(now)
    if args.full_manifest_scan or canonicalized_paths:
        inventory = build_manifest_inventory(output_root, run_entries)
    else:
        previous_inventory = previous_manifest.get("inventory") if isinstance(previous_manifest, dict) else []
        if not isinstance(previous_inventory, list):
            previous_inventory = []
        inventory = merge_manifest_inventory(previous_inventory, run_entries)
    if args.dry_run:
        split_paths = []
    elif args.full_manifest_scan or canonicalized_paths:
        split_paths = rebuild_split_manifest_files(output_root, inventory, updated_at_utc=updated_at_utc)
    else:
        split_paths = write_split_manifest_files(output_root, run_entries, updated_at_utc=updated_at_utc)
    manifest_indexes = root_manifest_indexes(output_root)
    if args.full_manifest_scan or canonicalized_paths or previous_inventory:
        inventory_count = len(inventory)
    else:
        inventory_count = split_manifest_inventory_count(output_root, manifest_indexes)
    manifest = root_manifest_payload(
        updated_at_utc=updated_at_utc,
        windows=windows,
        complete_model_count=args.complete_model_count,
        final_check_before_window_end_minutes=args.final_check_before_window_end_minutes,
        runs=compact_runs,
        output_root=output_root,
        inventory_count=inventory_count,
        manifest_indexes=manifest_indexes,
    )
    status_for_write = prune_status_for_persistence(
        status,
        active_data_times={window.data_time for window in windows},
        retention_days=args.status_retention_days,
        reference_time=utc_now(),
    )
    should_clear_previous_manifest = not run_entries and bool(previous_manifest.get("runs"))
    inventory_changed = previous_manifest.get("inventory_count") != manifest.get("inventory_count")
    index_changed = previous_manifest.get("manifest_indexes") != manifest.get("manifest_indexes")
    status_changed = status_for_write != status
    should_write_outputs = not args.dry_run and (
        actual_run_count > 0 or should_clear_previous_manifest or inventory_changed or index_changed or status_changed or bool(split_paths) or bool(canonicalized_paths) or bool(removed_artifact_paths)
    )
    changed_paths = collect_changed_asset_paths(
        run_entries=run_entries,
        manifest_path=manifest_path,
        status_path=status_path,
        split_manifest_paths=split_paths,
        include_manifest=should_write_outputs,
        include_status=status_changed or canonical_status_changed or actual_run_count > 0,
    )
    changed_paths.extend(relative_asset_path(path) for path in removed_artifact_paths)
    changed_paths.extend(relative_asset_path(path) for path in canonicalized_paths)
    changed_paths.extend(relative_asset_path(path) for path in kma_cache_asset_paths(kma_cache_dir, years))
    changed_paths = sorted(set(changed_paths))
    if should_write_outputs:
        write_json(manifest_path, manifest)
        if status_changed or canonical_status_changed or actual_run_count > 0:
            write_json(status_path, status_for_write)
    write_changed_paths(args.changed_paths_file, changed_paths)
    print_manifest_or_summary(manifest, verbose=args.verbose_manifest, changed_paths=changed_paths)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
