from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import sys
import tempfile
import time
from collections import defaultdict
from dataclasses import asdict, is_dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

LAYER_URL = "https://dmdw.kma.go.kr/uwa/rest/iwa/Typhoon/retLayerInfoTyphoon.json"
DATA_URL = "https://dmdw.kma.go.kr/uwa/rest/iwa/ObservationSite/retTyphoonDataImg.json"

DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "data" / "dmdw"
DEFAULT_REQUEST_DELAY = 0.15
KST = timezone(timedelta(hours=9), "KST")
DMDW_POINT_COLUMNS = [
    "model_index",
    "lead_hour",
    "valid_time",
    "lat",
    "lon",
    "pressure_hpa",
    "wind",
    "speed",
    "direction",
    "radius_15",
]

REQUEST_EXTENT = {
    "PROJ": "LCC",
    "STARTX": "-3672626.727296781",
    "STARTY": "8443989.722987227",
    "ENDX": "3840128.828258775",
    "ENDY": "603856.3896538913",
    "ZOOMLVL": "7",
    "chgProjectionLevel": "7",
    "nCntrLonLat": "126.966,37.570999999999756",
}

DMDW_MODEL_MAP = {
    "AIGEFS": "AIGEFS",
    "AIGFS": "AGFS",
    "CMC": "CMC",
    "CMC_EPS": "CMC_EPS",
    "EC_AIFS": "ECMWF_AIFS",
    "EC_AIFS_SINGLE": "ECMWF_AIFS",
    "ECMWF": "ECMWF",
    "ECMWF_AIFS": "ECMWF_AIFS",
    "ECMWF_EPS": "ECMWF_EPS",
    "ECMWF_HRES": "ECMWF",
    "FNV3": "FNV3",
    "FNV3_LARGE_ENSEMBLE": "FNV3",
    "GALWEM": "AFUM",
    "GEFS": "GFS_EPS",
    "GFS": "GFS",
    "GFS_EPS": "GFS_EPS",
    "HAFS": "HAFS",
    "HAFS_A": "HAFS",
    "HAFS-A": "HAFS",
    "HAFS_B": "HAFS",
    "HAFS-B": "HAFS",
    "HWRF": "HWRF",
    "JENS": "TEPS",
    "JGSM": "JGSM",
    "KIM": "KIM_6h",
    "KIM_3H": "KIM_3h",
    "KIM_6H": "KIM_6h",
    "KIM_EPS": "KIM_EPS",
    "NAVGEM": "NAVGEM",
    "TEPS": "TEPS",
    "UKMO": "UKM",
    "UKM": "UKM",
}

NON_MODEL_LAYER_TOKENS = {
    "NOTICE",
    "LASTNOTICE",
    "KMA_NOTICE",
    "TYP_NOTICE",
}


class DmdwAuthError(RuntimeError):
    pass


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(second=0, microsecond=0)


def floor_to_cycle(value: datetime) -> datetime:
    base = value.replace(minute=0, second=0, microsecond=0)
    remainder = base.hour % 6
    if remainder:
        base -= timedelta(hours=remainder)
    return base


def latest_dmdw_collection_cycle(value: datetime | None = None) -> datetime:
    """Return the DMDW cycle expected to be available in the current KST window."""
    now_kst = (value or utc_now()).astimezone(KST)
    local_date = now_kst.date()
    hour = now_kst.hour

    if hour < 1:
        target_date = local_date - timedelta(days=1)
        target_hour = 6
    elif hour < 7:
        target_date = local_date - timedelta(days=1)
        target_hour = 12
    elif hour < 13:
        target_date = local_date - timedelta(days=1)
        target_hour = 18
    elif hour < 19:
        target_date = local_date
        target_hour = 0
    else:
        target_date = local_date
        target_hour = 6

    return datetime(
        target_date.year,
        target_date.month,
        target_date.day,
        target_hour,
        tzinfo=timezone.utc,
    )


def parse_cycle(value: str | None) -> datetime:
    text = str(value or "").strip()
    if not text or text.lower() in {"latest", "latest-dmdw", "latest-kst"}:
        return latest_dmdw_collection_cycle()
    if text.lower() in {"latest-6h", "latest-floor"}:
        return floor_to_cycle(utc_now())
    if re.fullmatch(r"\d{10}", text):
        fmt = "%Y%m%d%H"
    elif re.fullmatch(r"\d{12}", text):
        fmt = "%Y%m%d%H%M"
    else:
        raise SystemExit("--cycle must be YYYYmmddHH, YYYYmmddHHMM, or latest.")
    cycle = datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
    if cycle.hour not in {0, 6, 12, 18}:
        raise SystemExit("--cycle hour must be one of 00, 06, 12, 18 UTC.")
    return cycle.replace(minute=0, second=0, microsecond=0)


def stamp(value: datetime) -> str:
    return value.strftime("%Y%m%d%H%M")


def cycle_key(value: datetime) -> str:
    return value.strftime("%Y%m%d%H")


def safe_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return None
    try:
        number = float(text)
    except (TypeError, ValueError):
        return None
    if math.isnan(number):
        return None
    return number


def safe_int(value: Any) -> int | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return int(float(text))
    except (TypeError, ValueError):
        return None


def read_optional_text(path: Path | None) -> str:
    if path is None or not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def read_required_text(path: Path | None, env_name: str, label: str) -> str:
    # Prefer an explicit file path over the environment variable.
    # In GitHub Actions fresh-login mode, DMDW_COOKIE can still contain an old
    # repository secret while --cookie-file points to the newly generated session.
    if path and path.exists():
        value = path.read_text(encoding="utf-8").strip()
        if value:
            print(f"Using {label} from file: {path} ({len(value)} characters).")
            return value

    env_value = os.environ.get(env_name, "").strip()
    if env_value:
        print(f"Using {label} from environment variable: {env_name} ({len(env_value)} characters).")
        return env_value

    raise SystemExit(f"{label} is required via {env_name} or file path.")


def make_headers(cookie: str, csrf: str = "") -> dict[str, str]:
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://dmdw.kma.go.kr",
        "Referer": "https://dmdw.kma.go.kr/uwa/iwa/iwaMain.kaf",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/146.0.0.0 Safari/537.36"
        ),
        "X-Requested-With": "XMLHttpRequest",
        "Cookie": cookie,
    }
    if csrf:
        headers["X-Csrf-Token"] = csrf
    return headers


def iter_dicts(obj: Any) -> Iterable[dict[str, Any]]:
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from iter_dicts(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from iter_dicts(item)


def first_existing(row: dict[str, Any], keys: list[str]) -> Any:
    for key in keys:
        if key in row and row[key] not in (None, ""):
            return row[key]
    return None


def looks_like_model_name(value: Any) -> bool:
    text = str(value or "").strip().upper()
    if not text:
        return False
    tokens = [
        "ECMWF",
        "EC_AIFS",
        "AIFS",
        "KIM",
        "GFS",
        "GEFS",
        "UKMO",
        "CMC",
        "NAVGEM",
        "JGSM",
        "TEPS",
        "JENS",
        "HAFS",
        "HWRF",
        "COAMPS",
        "GALWEM",
        "AIGFS",
        "AIGEFS",
        "FNV3",
        "MEM",
    ]
    return any(token in text for token in tokens)


def looks_like_non_model_layer(*values: Any) -> bool:
    joined = "_".join(str(value or "").strip().upper() for value in values)
    if any(token in joined for token in NON_MODEL_LAYER_TOKENS):
        return True
    return "통보문" in joined or "최종" in joined


def extract_layer_candidates(layer_json: dict[str, Any]) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    src_keys = [
        "src",
        "typSrc",
        "lyrTitle",
        "lyrTitleEn",
        "model",
        "modelNm",
        "modelName",
        "mdlNm",
        "title",
        "titleEn",
        "name",
        "dataNm",
        "dataName",
    ]
    title_keys = ["lyrTitle", "title", "name", "modelNm", "modelName", "src"]
    title_en_keys = ["lyrTitleEn", "titleEn", "nameEn", "modelNameEn", "src"]
    map_idx_keys = ["mapLyrIdx", "mapLyrId", "lyrIdx", "layerIdx", "idx"]
    map_nm_keys = ["mapLyrNm", "layerNm", "lyrNm", "layerName"]

    for row in iter_dicts(layer_json):
        src = first_existing(row, src_keys)
        title = first_existing(row, title_keys)
        title_en = first_existing(row, title_en_keys)
        map_idx = first_existing(row, map_idx_keys)
        map_nm = first_existing(row, map_nm_keys)
        if not any(looks_like_model_name(value) for value in (src, title, title_en)):
            continue
        if looks_like_non_model_layer(src, title, title_en, map_nm):
            continue

        src_final = str(src or title or title_en or "").strip()
        if not src_final:
            continue
        candidate = {
            "src": src_final,
            "lyrTitle": str(title or src_final).strip(),
            "lyrTitleEn": str(title_en or title or src_final).strip(),
            "mapLyrIdx": "" if map_idx is None else str(map_idx).strip(),
            "mapLyrNm": "" if map_nm is None else str(map_nm).strip(),
        }
        candidates.append(candidate)

    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str, str, str, str]] = set()
    for candidate in candidates:
        key = (
            candidate["src"],
            candidate["lyrTitle"],
            candidate["lyrTitleEn"],
            candidate["mapLyrIdx"],
            candidate["mapLyrNm"],
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(candidate)
    return sorted(unique, key=lambda item: (item["src"], item["mapLyrIdx"], item["mapLyrNm"]))


def is_auth_failure(response: Any, text: str) -> bool:
    content_type = response.headers.get("Content-Type", "").lower()
    if response.status_code in {401, 403}:
        return True
    if "application/json" not in content_type and ("login" in text.lower() or "<html" in text.lower()):
        return True
    return False


def post_json(
    session: Any,
    url: str,
    *,
    headers: dict[str, str],
    payload: dict[str, str],
    timeout: int,
) -> dict[str, Any]:
    response = session.post(url, headers=headers, data=payload, timeout=timeout)
    text = response.text
    if is_auth_failure(response, text):
        raise DmdwAuthError(f"DMDW auth failed or expired at {url} (HTTP {response.status_code}).")
    try:
        return response.json()
    except ValueError as exc:
        preview = text[:300].replace("\n", " ")
        raise RuntimeError(f"DMDW JSON parse failed at {url}: {preview}") from exc


def dmdw_display_time(cycle: datetime) -> datetime:
    return cycle.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)


def o_tm_seq_from_start_time(cycle: datetime, start_time: str) -> str | None:
    start = parse_valid_time(start_time)
    if start is None:
        return None
    delta_hours = int(round((cycle - start).total_seconds() / 3600.0))
    if delta_hours < 0:
        return None
    return str(delta_hours // 6 + 1)


def resolve_o_tm_seq(cycle: datetime, explicit: str | None, job: Any) -> str:
    if explicit:
        return str(explicit).strip()
    from_job = job_value(job, "dmdw_o_tm_seq", None)
    if from_job not in (None, ""):
        return str(from_job)
    start_time = job_value(job, "dmdw_start_time", "")
    derived = o_tm_seq_from_start_time(cycle, str(start_time or ""))
    if derived:
        return derived
    raise SystemExit(
        "DMDW oTmSeq could not be derived. Use --auto-active, or provide "
        "--o-tm-seq, or provide --start-time for manual runs."
    )


def base_request_fields(*, year: int, typ_seq: int, storm_kind: str, cycle: datetime, o_tm_seq: str) -> dict[str, str]:
    cycle_stamp = stamp(cycle)
    ret_time = stamp(dmdw_display_time(cycle))
    code_time = stamp(cycle + timedelta(hours=10))
    return {
        **REQUEST_EXTENT,
        "oReqYy": str(year),
        "_metaToken": "",
        "beforeAfterChk": "",
        "yyyy": str(year),
        "code": f"1_{code_time}_{typ_seq}_{o_tm_seq}",
        "comparetime": cycle_stamp,
        "comparetime2": cycle_stamp,
        "comparetime1": f"{year}01010000",
        "oTypSeq": str(typ_seq),
        "oTmSeq": str(o_tm_seq),
        "modValue": "2",
        "scrImgType": "2",
        "oNm": storm_kind.lower(),
        "analTime": ret_time,
        "foreTime": ret_time,
        "retDateTime": ret_time,
        "weatherType": "3",
        "reqSeq": "923328357",
        "rsn": f"R{int(time.time() * 1000)}",
        "selectedMenuTmp": "undefined#undefined#undefined#undefined#undefined#undefined#undefined#undefined#undefined#undefined",
        "selectedAnalForeTm": f"{ret_time}_{ret_time}",
        "reloadFlag": "false",
    }


def layer_payload(*, year: int, typ_seq: int, storm_kind: str, cycle: datetime, o_tm_seq: str) -> dict[str, str]:
    fields = base_request_fields(year=year, typ_seq=typ_seq, storm_kind=storm_kind, cycle=cycle, o_tm_seq=o_tm_seq)
    return {
        "oReqYy": fields["oReqYy"],
        "oTypSeq": fields["oTypSeq"],
        "comparetime2": fields["comparetime2"],
        "oTmSeq": fields["oTmSeq"],
        "modValue": fields["modValue"],
        "_metaToken": fields["_metaToken"],
    }


def data_payload(
    *,
    year: int,
    typ_seq: int,
    storm_kind: str,
    cycle: datetime,
    o_tm_seq: str,
    candidate: dict[str, str],
) -> dict[str, str]:
    payload = base_request_fields(year=year, typ_seq=typ_seq, storm_kind=storm_kind, cycle=cycle, o_tm_seq=o_tm_seq)
    src = candidate.get("src") or candidate.get("lyrTitle") or ""
    title = candidate.get("lyrTitle") or src
    title_en = candidate.get("lyrTitleEn") or title
    payload.update({
        "src": src,
        "lyrTitle": title,
        "lyrTitleEn": title_en,
        "mapLyrIdx": candidate.get("mapLyrIdx") or "8",
        "mapLyrNm": candidate.get("mapLyrNm") or f"WeatherLayer_Typhoon_{candidate.get('mapLyrIdx') or '8'}",
    })
    return payload


def normalize_raw_model_id(value: str) -> str:
    return str(value or "").strip().upper().replace(" ", "_")


def mapped_model_id(raw_model_id: str) -> str:
    raw = normalize_raw_model_id(raw_model_id)
    if re.match(r"^EC_AIFS_MEM_?\d+$", raw):
        return "ECMWF_AIFS_EPS"
    if re.match(r"^ECMWF_MEM_?\d+$", raw):
        return "ECMWF_EPS"
    if re.match(r"^CMC_MEM_?\d+$", raw):
        return "CMC_EPS"
    if re.match(r"^GFS_MEM_?\d+$", raw):
        return "GFS_EPS"
    if re.match(r"^KIM_MEM_?\d+$", raw):
        return "KIM_EPS"
    if re.match(r"^FNMOC_MEM_?\d+$", raw):
        return "FNMOC_EPS"
    return DMDW_MODEL_MAP.get(raw, raw)


def member_id(raw_model_id: str) -> str | None:
    match = re.search(r"_MEM_?(\d+)$", normalize_raw_model_id(raw_model_id))
    if not match:
        return None
    return match.group(1).zfill(3)


def parse_valid_time(value: str) -> datetime | None:
    text = str(value or "").strip()
    if not re.fullmatch(r"\d{12}", text):
        return None
    try:
        return datetime.strptime(text, "%Y%m%d%H%M").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def computed_lead_hour(valid_time: str, cycle: datetime) -> int | None:
    valid = parse_valid_time(valid_time)
    if valid is None:
        return None
    return int(round((valid - cycle).total_seconds() / 3600.0))


def normalized_point(raw_point: dict[str, Any], *, cycle: datetime) -> dict[str, Any]:
    point = raw_point.get("point") or [None, None]
    lon = point[0] if len(point) >= 1 else None
    lat = point[1] if len(point) >= 2 else None
    valid_time = str(raw_point.get("typTm") or "").strip()
    raw_lead = safe_int(raw_point.get("typFt"))
    return {
        "valid_time": valid_time,
        "lead_hour": computed_lead_hour(valid_time, cycle),
        "raw_lead_hour": raw_lead,
        "lat": safe_float(lat),
        "lon": safe_float(lon),
        "pressure_hpa": safe_float(raw_point.get("typPs")),
        "wind": safe_float(raw_point.get("typWs")),
        "speed": safe_float(raw_point.get("typSp")),
        "direction": safe_float(raw_point.get("typDir")),
        "radius_15": safe_float(raw_point.get("typRad15")),
        "raw_model_id": raw_point.get("typSrc"),
    }


def extract_track_points(data: dict[str, Any], *, candidate: dict[str, str], cycle: datetime) -> list[dict[str, Any]]:
    result = data.get("body", {}).get("result", {})
    rtn = result.get("rtnParam", {})
    points = rtn.get("typoints", [])
    rows: list[dict[str, Any]] = []
    if not isinstance(points, list):
        return rows
    fallback_model = candidate.get("src") or rtn.get("src") or ""
    for point in points:
        if not isinstance(point, dict):
            continue
        row = normalized_point(point, cycle=cycle)
        lead_hour = row.get("lead_hour")
        if not isinstance(lead_hour, int) or lead_hour < 0:
            continue
        row["raw_model_id"] = row.get("raw_model_id") or fallback_model
        rows.append(row)
    return rows


def point_count(points: list[dict[str, Any]]) -> int:
    unique = {
        (
            point.get("valid_time"),
            point.get("lat"),
            point.get("lon"),
        )
        for point in points
        if point.get("valid_time") and point.get("lat") is not None and point.get("lon") is not None
    }
    return len(unique)


def max_lead(points: list[dict[str, Any]]) -> int | None:
    leads = [point.get("lead_hour") for point in points if isinstance(point.get("lead_hour"), int)]
    return max(leads) if leads else None


def compact_number(value: Any) -> int | float | None:
    number = safe_float(value)
    if number is None:
        return None
    if float(number).is_integer():
        return int(number)
    return round(float(number), 4)


def compact_schema_v2_payload(payload: dict[str, Any]) -> dict[str, Any]:
    point_columns = payload.get("point_columns") or []
    points = payload.get("points") or []
    source_models = payload.get("models") or []
    column_index = {str(column): idx for idx, column in enumerate(point_columns)}
    required = {"model_index", "lead_hour", "valid_time", "lat", "lon"}
    if not isinstance(points, list) or not isinstance(source_models, list) or not required <= set(column_index):
        return payload

    compact_models: list[dict[str, Any]] = []
    compact_points: list[list[Any]] = []
    model_index_map: dict[int, int] = {}

    def value(row: list[Any], column: str) -> Any:
        index = column_index.get(column)
        if index is None or index >= len(row):
            return None
        return row[index]

    for row in points:
        if not isinstance(row, list):
            continue
        lead_hour = value(row, "lead_hour")
        if not isinstance(lead_hour, int) or lead_hour < 0:
            continue
        old_model_index = value(row, "model_index")
        if not isinstance(old_model_index, int) or not (0 <= old_model_index < len(source_models)):
            continue

        if old_model_index not in model_index_map:
            source_model = source_models[old_model_index]
            if not isinstance(source_model, dict):
                source_model = {}
            new_model_index = len(compact_models)
            model_index_map[old_model_index] = new_model_index
            compact_models.append({
                "index": new_model_index,
                "raw_model_id": source_model.get("raw_model_id"),
                "model_id": source_model.get("model_id"),
                "member_id": source_model.get("member_id"),
                "point_count": 0,
                "row_count": 0,
                "max_lead_hour": None,
            })

        new_model_index = model_index_map[old_model_index]
        compact_points.append([
            new_model_index,
            lead_hour,
            value(row, "valid_time"),
            compact_number(value(row, "lat")),
            compact_number(value(row, "lon")),
            compact_number(value(row, "pressure_hpa")),
            compact_number(value(row, "wind")),
            compact_number(value(row, "speed")),
            compact_number(value(row, "direction")),
            compact_number(value(row, "radius_15")),
        ])
        model = compact_models[new_model_index]
        model["point_count"] += 1
        model["row_count"] += 1
        model["max_lead_hour"] = max(
            lead_hour,
            model["max_lead_hour"] if isinstance(model.get("max_lead_hour"), int) else lead_hour,
        )

    return {
        "schema_version": 2,
        "source": "DMDW",
        "cycle": payload.get("cycle"),
        "cycle_utc": payload.get("cycle_utc"),
        "time_basis": payload.get("time_basis"),
        "request": payload.get("request"),
        "storm": payload.get("storm"),
        "layer_candidate_count": payload.get("layer_candidate_count"),
        "model_count": len(compact_models),
        "point_count": len(compact_points),
        "models": compact_models,
        "point_columns": DMDW_POINT_COLUMNS,
        "points": compact_points,
    }


def compact_dmdw_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("schema_version") == 2:
        return compact_schema_v2_payload(payload)

    compact_models: list[dict[str, Any]] = []
    compact_points: list[list[Any]] = []
    for model in payload.get("models") or []:
        if not isinstance(model, dict):
            continue
        points = [
            point for point in (model.get("points") or [])
            if isinstance(point, dict)
            and isinstance(point.get("lead_hour"), int)
            and point.get("lead_hour") >= 0
        ]
        if not points:
            continue

        model_index = len(compact_models)
        compact_models.append({
            "index": model_index,
            "raw_model_id": model.get("raw_model_id"),
            "model_id": model.get("model_id"),
            "member_id": model.get("member_id"),
            "point_count": point_count(points),
            "row_count": len(points),
            "max_lead_hour": max_lead(points),
        })
        for point in points:
            compact_points.append([
                model_index,
                point.get("lead_hour"),
                point.get("valid_time"),
                compact_number(point.get("lat")),
                compact_number(point.get("lon")),
                compact_number(point.get("pressure_hpa")),
                compact_number(point.get("wind")),
                compact_number(point.get("speed")),
                compact_number(point.get("direction")),
                compact_number(point.get("radius_15")),
            ])

    return {
        "schema_version": 2,
        "source": "DMDW",
        "cycle": payload.get("cycle"),
        "cycle_utc": payload.get("cycle_utc"),
        "time_basis": payload.get("time_basis"),
        "request": payload.get("request"),
        "storm": payload.get("storm"),
        "layer_candidate_count": payload.get("layer_candidate_count"),
        "model_count": len(compact_models),
        "point_count": len(compact_points),
        "models": compact_models,
        "point_columns": DMDW_POINT_COLUMNS,
        "points": compact_points,
    }


def fetch_one_storm(
    *,
    session: Any,
    headers: dict[str, str],
    year: int,
    typ_seq: int,
    storm_kind: str,
    cycle: datetime,
    o_tm_seq: str,
    request_delay: float,
    max_models: int | None,
) -> dict[str, Any]:
    layer = post_json(
        session,
        LAYER_URL,
        headers=headers,
        payload=layer_payload(year=year, typ_seq=typ_seq, storm_kind=storm_kind, cycle=cycle, o_tm_seq=o_tm_seq),
        timeout=30,
    )
    candidates = extract_layer_candidates(layer)
    if max_models:
        candidates = candidates[:max(0, max_models)]

    models: list[dict[str, Any]] = []
    summary: list[dict[str, Any]] = []
    for index, candidate in enumerate(candidates, start=1):
        raw_id = candidate.get("src") or candidate.get("lyrTitle") or ""
        print(f"[{index}/{len(candidates)}] DMDW {raw_id} mapLyrIdx={candidate.get('mapLyrIdx') or '-'}")
        try:
            data = post_json(
                session,
                DATA_URL,
                headers=headers,
                payload=data_payload(
                    year=year,
                    typ_seq=typ_seq,
                    storm_kind=storm_kind,
                    cycle=cycle,
                    o_tm_seq=o_tm_seq,
                    candidate=candidate,
                ),
                timeout=30,
            )
            points = extract_track_points(data, candidate=candidate, cycle=cycle)
            message = data.get("message")
            status_code = data.get("statusCode")
            error = ""
        except Exception as exc:
            points = []
            message = str(exc)
            status_code = None
            error = type(exc).__name__

        normalized_raw = normalize_raw_model_id(raw_id)
        model = {
            "raw_model_id": normalized_raw,
            "model_id": mapped_model_id(normalized_raw),
            "member_id": member_id(normalized_raw),
            "candidate": candidate,
            "points": points,
        }
        models.append(model)
        summary.append({
            "raw_model_id": normalized_raw,
            "model_id": model["model_id"],
            "member_id": model["member_id"],
            "statusCode": status_code,
            "message": message,
            "point_count": point_count(points),
            "row_count": len(points),
            "max_lead_hour": max_lead(points),
            "error": error,
        })
        if request_delay > 0:
            time.sleep(request_delay)

    return {
        "schema_version": 1,
        "source": "DMDW",
        "cycle": cycle_key(cycle),
        "cycle_utc": stamp(cycle),
        "time_basis": "DMDW typTm stored as received; lead_hour is computed as typTm minus comparetime. Only forecast points with lead_hour >= 0 are stored.",
        "request": {
            "year": year,
            "storm_kind": storm_kind.lower(),
            "typ_seq": typ_seq,
            "o_tm_seq": o_tm_seq,
        },
        "layer_candidate_count": len(candidates),
        "summary": summary,
        "models": models,
    }


def write_json_if_changed(path: Path, payload: dict[str, Any]) -> bool:
    text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"
    previous = path.read_text(encoding="utf-8") if path.exists() else None
    if previous == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)
    return True


def append_changed_path(path: Path | None, changed: Path) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        try:
            rel = changed.relative_to(PROJECT_ROOT).as_posix()
        except ValueError:
            rel = changed.as_posix()
        handle.write(rel + "\n")


def row_start_time(row: dict[str, Any]) -> str:
    return str(row.get("TM_ST") or "").strip()


def best_start_time_for_rows(rows: list[dict[str, Any]], cycle: datetime) -> str:
    choices: list[tuple[datetime, str]] = []
    for row in rows:
        start_text = row_start_time(row)
        start_dt = parse_valid_time(start_text)
        if start_dt is None or start_dt > cycle:
            continue
        choices.append((start_dt, start_text))
    if not choices:
        return ""
    return max(choices, key=lambda item: item[0])[1]


def dmdw_start_time_for_job(
    job: Any,
    *,
    td_rows: list[dict[str, Any]],
    typ_rows: list[dict[str, Any]],
    cycle: datetime,
) -> str:
    year = safe_int(job_value(job, "year"))
    if year is None:
        return ""
    kind = storm_kind_for_job(job)
    if kind == "typ":
        number = safe_int(job_value(job, "data_typ_number", job_value(job, "typ_number")))
        rows = [
            row for row in typ_rows
            if safe_int(row.get("YY")) == year and safe_int(row.get("SEQ")) == number
        ]
        return best_start_time_for_rows(rows, cycle)

    td_number = safe_int(job_value(job, "td_number", job_value(job, "data_typ_number", job_value(job, "typ_number"))))
    rows = [
        row for row in td_rows
        if safe_int(row.get("YY")) == year and safe_int(row.get("TD")) == td_number
    ]
    return best_start_time_for_rows(rows, cycle)


def job_as_dict(job: Any) -> dict[str, Any]:
    if isinstance(job, dict):
        return dict(job)
    if is_dataclass(job):
        return asdict(job)
    return dict(getattr(job, "__dict__", {}))


def annotate_jobs_with_dmdw_sequence(
    jobs: list[Any],
    *,
    td_rows: list[dict[str, Any]],
    typ_rows: list[dict[str, Any]],
    cycle: datetime,
) -> list[dict[str, Any]]:
    annotated: list[dict[str, Any]] = []
    for job in jobs:
        record = job_as_dict(job)
        start_time = dmdw_start_time_for_job(record, td_rows=td_rows, typ_rows=typ_rows, cycle=cycle)
        if start_time:
            record["dmdw_start_time"] = start_time
            seq = o_tm_seq_from_start_time(cycle, start_time)
            if seq:
                record["dmdw_o_tm_seq"] = seq
        annotated.append(record)
    return annotated


def load_active_jobs(cycle: datetime, auth_key: str) -> list[Any]:
    import vtg_auto

    data_time = stamp(cycle)
    activity_time = cycle + timedelta(hours=4)
    years = {cycle.year - 1, cycle.year, cycle.year + 1}
    cache_dir = Path(os.environ.get("RUNNER_TEMP", tempfile.gettempdir())) / "dmdw_kma_apihub_cache"
    td_rows: list[dict[str, Any]] = []
    typ_rows: list[dict[str, Any]] = []
    for year in sorted(years):
        td_rows.extend(vtg_auto.fetch_td_rows(year, auth_key, cache_dir=cache_dir))
        typ_rows.extend(vtg_auto.fetch_typ_rows(year, auth_key, cache_dir=cache_dir))
    jobs = vtg_auto.build_storm_jobs(
        now=activity_time,
        data_time=data_time,
        td_rows=td_rows,
        typ_rows=typ_rows,
        manual_map=vtg_auto.load_manual_map(PROJECT_ROOT / "vtg_manual_atcf_map.json"),
        auth_key=auth_key,
        atcf_search_positive_radius=vtg_auto.DEFAULT_ATCF_SEARCH_POSITIVE_RADIUS,
        atcf_search_negative_radius=vtg_auto.DEFAULT_ATCF_SEARCH_NEGATIVE_RADIUS,
        atcf_position_max_distance_km=vtg_auto.DEFAULT_ATCF_POSITION_MAX_DISTANCE_KM,
        atcf_position_min_distance_gap_km=vtg_auto.DEFAULT_ATCF_POSITION_MIN_DISTANCE_GAP_KM,
        resolve_atcf=False,
        activity_cycle_time=cycle,
    )
    return annotate_jobs_with_dmdw_sequence(jobs, td_rows=td_rows, typ_rows=typ_rows, cycle=cycle)


def manual_job_from_args(args: argparse.Namespace, cycle: datetime) -> list[dict[str, Any]]:
    if args.year is None or args.typ_seq is None:
        raise SystemExit("Manual mode requires --year and --typ-seq.")
    storm_kind = str(args.storm_kind or "typ").lower()
    if storm_kind not in {"typ", "td"}:
        raise SystemExit("--storm-kind must be typ or td.")
    key_prefix = "typ" if storm_kind == "typ" else "td"
    return [{
        "year": int(args.year),
        "typ_number": int(args.typ_seq),
        "data_typ_number": int(args.typ_seq),
        "stage": storm_kind.upper(),
        "storm_key": f"{key_prefix}_{int(args.year)}_{int(args.typ_seq):02d}",
        "canonical_storm_stage": storm_kind.upper(),
        "canonical_typ_number": int(args.typ_seq),
        "canonical_typ_name": "NONAME",
        "canonical_typ_name_ko": "",
        "data_time": stamp(cycle),
        "dmdw_start_time": str(args.start_time or "").strip(),
    }]


def job_value(job: Any, key: str, default: Any = None) -> Any:
    if isinstance(job, dict):
        return job.get(key, default)
    return getattr(job, key, default)


def storm_kind_for_job(job: Any) -> str:
    stage = str(job_value(job, "stage", "")).upper()
    return "td" if stage.startswith("TD") else "typ"


def storm_output_path(output_root: Path, *, cycle: datetime, job: Any) -> Path:
    year = int(job_value(job, "year", cycle.year))
    storm_key = str(job_value(job, "storm_key", f"storm_{year}")).lower()
    return output_root / str(year) / cycle_key(cycle) / f"{storm_key}.json"


def update_index(output_root: Path, written_paths: list[Path]) -> Path | None:
    if not written_paths:
        return None
    by_cycle: dict[str, list[str]] = defaultdict(list)
    for path in sorted(written_paths):
        try:
            rel = path.relative_to(output_root).as_posix()
        except ValueError:
            rel = path.as_posix()
        parts = rel.split("/")
        if len(parts) >= 3:
            by_cycle[f"{parts[0]}/{parts[1]}"].append(rel)
    index_path = output_root / "index.json"
    previous = {}
    if index_path.exists():
        try:
            previous = json.loads(index_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            previous = {}
    cycles = dict(previous.get("cycles") or {})
    for key, rels in by_cycle.items():
        cycles[key] = sorted(set(cycles.get(key, []) + rels))
    payload = {
        "schema_version": 1,
        "source": "DMDW",
        "updated_at_utc": stamp(utc_now()),
        "cycles": dict(sorted(cycles.items())),
    }
    if write_json_if_changed(index_path, payload):
        return index_path
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync DMDW typhoon model tracks into sanitized JSON files.")
    parser.add_argument("--auto-active", action="store_true", help="Use APIHUB active TD/TYP rows to choose storms.")
    parser.add_argument(
        "--cycle",
        default="latest",
        help=(
            "Target cycle UTC: YYYYmmddHH, YYYYmmddHHMM, latest "
            "(KST DMDW collection window), or latest-6h."
        ),
    )
    parser.add_argument("--year", type=int, default=None)
    parser.add_argument("--typ-seq", type=int, default=None)
    parser.add_argument("--storm-kind", choices=["typ", "td"], default="typ")
    parser.add_argument("--start-time", default="", help="Manual storm start UTC, YYYYmmddHHMM, used to derive DMDW oTmSeq.")
    parser.add_argument("--o-tm-seq", default=None, help="Override DMDW oTmSeq. Auto-active runs derive it from KMA TM_ST.")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--cookie-file", type=Path, default=BASE_DIR / "cookie.txt")
    parser.add_argument("--csrf-file", type=Path, default=BASE_DIR / "csrf.txt")
    parser.add_argument("--auth-key", default=os.getenv("KMA_APIHUB_AUTH_KEY", ""))
    parser.add_argument("--request-delay", type=float, default=DEFAULT_REQUEST_DELAY)
    parser.add_argument("--max-models", type=int, default=None, help="Debug limit for model requests.")
    parser.add_argument("--changed-paths-file", type=Path, default=None)
    parser.add_argument(
        "--allow-empty-models",
        action="store_true",
        help="Write files even when DMDW returns no forecast model points.",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def forecast_point_total(payload: dict[str, Any]) -> int:
    points = payload.get("points")
    if isinstance(points, list):
        return len(points)

    total = 0
    for model in payload.get("models") or []:
        if isinstance(model, dict):
            points = model.get("points")
            if isinstance(points, list):
                total += len(points)
    return total


def main() -> int:
    args = parse_args()
    cycle = parse_cycle(args.cycle)

    if args.auto_active:
        if not args.auth_key:
            raise SystemExit("KMA_APIHUB_AUTH_KEY or --auth-key is required for --auto-active.")
        jobs = load_active_jobs(cycle, args.auth_key)
    else:
        jobs = manual_job_from_args(args, cycle)

    if not jobs:
        print(f"No DMDW storm jobs for {cycle_key(cycle)}.")
        return 0

    print(f"DMDW target cycle: {cycle_key(cycle)} jobs={len(jobs)}")
    for job in jobs:
        job_o_tm_seq = resolve_o_tm_seq(cycle, args.o_tm_seq, job)
        print(
            " - "
            f"{job_value(job, 'storm_key')} "
            f"kind={storm_kind_for_job(job)} "
            f"data_typ_number={job_value(job, 'data_typ_number', job_value(job, 'typ_number'))} "
            f"oTmSeq={job_o_tm_seq} "
            f"start={job_value(job, 'dmdw_start_time', '-')}"
        )

    if args.dry_run:
        print("Dry run requested; no DMDW HTTP requests or files will be written.")
        return 0

    cookie = read_required_text(args.cookie_file, "DMDW_COOKIE", "DMDW cookie")
    csrf = read_optional_text(args.csrf_file)
    if csrf:
        print(f"Using DMDW CSRF token from file: {args.csrf_file} ({len(csrf)} characters).")
    else:
        csrf = os.environ.get("DMDW_CSRF", "").strip()
        if csrf:
            print(f"Using DMDW CSRF token from environment variable: DMDW_CSRF ({len(csrf)} characters).")
        else:
            print("No DMDW CSRF token found; continuing with cookie-only authentication.")
    headers = make_headers(cookie, csrf)
    written_paths: list[Path] = []

    import requests

    with requests.Session() as session:
        for job in jobs:
            job_o_tm_seq = resolve_o_tm_seq(cycle, args.o_tm_seq, job)
            year = int(job_value(job, "year", cycle.year))
            typ_seq = int(job_value(job, "data_typ_number", job_value(job, "typ_number")))
            kind = storm_kind_for_job(job)
            payload = fetch_one_storm(
                session=session,
                headers=headers,
                year=year,
                typ_seq=typ_seq,
                storm_kind=kind,
                cycle=cycle,
                o_tm_seq=job_o_tm_seq,
                request_delay=args.request_delay,
                max_models=args.max_models,
            )
            payload["storm"] = {
                "storm_key": job_value(job, "storm_key"),
                "stage": job_value(job, "stage"),
                "canonical_storm_stage": job_value(job, "canonical_storm_stage"),
                "canonical_typ_number": job_value(job, "canonical_typ_number"),
                "canonical_typ_name": job_value(job, "canonical_typ_name"),
                "canonical_typ_name_ko": job_value(job, "canonical_typ_name_ko"),
                "data_typ_number": typ_seq,
                "dmdw_start_time": job_value(job, "dmdw_start_time", ""),
                "dmdw_o_tm_seq": job_o_tm_seq,
            }
            payload = compact_dmdw_payload(payload)
            out_path = storm_output_path(args.output_root, cycle=cycle, job=job)
            if not args.allow_empty_models and forecast_point_total(payload) == 0:
                print(f"Skipping {out_path}: DMDW returned no forecast model points.")
                continue
            if write_json_if_changed(out_path, payload):
                print(f"Wrote {out_path}")
                written_paths.append(out_path)
                append_changed_path(args.changed_paths_file, out_path)
            else:
                print(f"Unchanged {out_path}")

    index_path = update_index(args.output_root, written_paths)
    if index_path is not None:
        append_changed_path(args.changed_paths_file, index_path)
        print(f"Wrote {index_path}")

    print(f"DMDW sync complete. changed_files={len(written_paths) + (1 if index_path else 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
