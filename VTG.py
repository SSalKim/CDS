# === VORTEX TRACK GUIDANCE with AI Models ===
# ====== Created by WooJin.Kim 20250613 ======
# Refactored 20260527

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urlencode

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.font_manager as fm
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import requests


KMA_COLUMNS = [
    "FT", "YY", "TYP", "SEQ", "TMD", "TYP_TM(UTC)", "FT_TM(UTC)",
    "LAT", "LON", "DIR", "SP", "PS", "WS", "T15", "T25", "RAD",
    "15D", "15R", "SRC", "",
]

ATCF_COLUMNS = ["ATCF_BASIN", "ATCF_NUMBER", "TM10", "MODEL", "FTM", "LATI", "LONG", "WS(KT)", "SLP"]

MODEL_INFO = [
    {"name": "KMA", "color": "blue", "style": "-", "label": "KMA OFCL"},
    {"name": "ECMWF", "color": "#ED2939", "style": "-", "label": "ECMWF", "zorder": 89},
    {"name": "ECMWF_EPS", "color": "#FC6C85", "style": "-", "label": "ECMWF EPS", "zorder": 88},
    {"name": "KIM_3h", "color": "#FA8128", "style": "-", "label": "KIM", "zorder": 87},
    {"name": "KIM_6h", "color": "#FA8128", "style": "-", "label": "KIM", "zorder": 87},
    {"name": "KIM_EPS", "color": "#FFB347", "style": "-", "label": "KIM EPS", "zorder": 86},
    {"name": "UM", "color": "#FFF200", "style": "-", "label": "UM ", "zorder": 85},
    {"name": "UM_GFDL_6h", "color": "#FFF200", "style": "-", "label": "UM", "zorder": 85},
    {"name": "UM_KEPS", "color": "#B8CE9E", "style": "-", "label": "UM EPS", "zorder": 84},
    {"name": "UKM", "color": "#FFF200", "style": "-", "label": "UKMO", "zorder": 85},
    {"name": "UKMO_EPS", "color": "#B8CE9E", "style": "-", "label": "UKMO EPS", "zorder": 84},
    {"name": "GFS", "color": "#03C04A", "style": "-", "label": "GFS", "zorder": 83},
    {"name": "GFS_EPS", "color": "#7DDBA7", "style": "-", "label": "GFS EPS", "zorder": 82},
    {"name": "CMC", "color": "#0CCBF0", "style": "-", "label": "CMC", "zorder": 81},
    {"name": "CMC_EPS", "color": "#AAF7F4", "style": "-", "label": "CMC EPS", "zorder": 80},
    {"name": "NAVGEM", "color": "#4470AD", "style": "-", "label": "NAVGEM", "zorder": 79},
    {"name": "FNMOC_EPS", "color": "#99AFD7", "style": "-", "label": "NAVGEM EPS", "zorder": 78},
    {"name": "JGSM", "color": "#997950", "style": "-", "label": "JGSM", "zorder": 77},
    {"name": "TEPS", "color": "#654321", "style": "-", "label": "JGSM EPS", "zorder": 76},
    {"name": "CTCX", "color": "#78081C", "style": "-", "label": "COAMPS-TC ", "zorder": 75},
    {"name": "COAMPS_EPS", "color": "#A13B4E", "style": "-", "label": "COAMPS-TC EPS", "zorder": 74},
    {"name": "AFUM", "color": "#4F746C", "style": "-", "label": "GALWEM", "zorder": 73},
    {"name": "HAFS", "color": "#9D5E5C", "style": "-", "label": "HAFS", "zorder": 72},
    {"name": "HWRF", "color": "#9E9E9E", "style": "-", "label": "HWRF", "zorder": 71},
    {"name": "ECMWF_AIFS", "color": "#C71585", "style": "--", "label": "ECMWF AIFS", "zorder": 96},
    {"name": "ECMWF_AIFS_EPS", "color": "#E34FA5", "style": "--", "label": "ECMWF AIFS EPS", "zorder": 95},
    {"name": "IFEC_AI", "color": "#C8A3D3", "style": "--", "label": "KMA AIFS-ECMWF", "zorder": 98},
    {"name": "IFKM_AI", "color": "#DDA520", "style": "--", "label": "KMA AIFS-KIM", "zorder": 97},
    {"name": "AGFS", "color": "#E0FF78", "style": "--", "label": "AIGFS", "zorder": 59},
    {"name": "AIGEFS", "color": "#78FF8F", "style": "--", "label": "AIGFS EPS", "zorder": 58},
    {"name": "FNEC_AI", "color": "#004B1C", "style": "--", "label": "FourCastNet-ECMWF", "zorder": 62},
    {"name": "FNKM_AI", "color": "#388E3C", "style": "--", "label": "FourCastNet-KIM", "zorder": 61},
    {"name": "FNUM_AI", "color": "#4BB200", "style": "--", "label": "FourCastNet-UM", "zorder": 60},
    {"name": "PGEC_AI", "color": "#3944BC", "style": "--", "label": "Pangu-Weather-ECMWF", "zorder": 65},
    {"name": "PGKM_AI", "color": "#727EF2", "style": "--", "label": "Pangu-Weather-KIM", "zorder": 64},
    {"name": "PGUM_AI", "color": "#8EA2FF", "style": "--", "label": "Pangu-Weather-UM", "zorder": 63},
    {"name": "GCEC_AI", "color": "#4D248D", "style": "--", "label": "GraphCast-ECMWF", "zorder": 68},
    {"name": "GCKM_AI", "color": "#6C33C6", "style": "--", "label": "GraphCast-KIM", "zorder": 67},
    {"name": "GCUM_AI", "color": "#B57AD5", "style": "--", "label": "GraphCast-UM", "zorder": 66},
    {"name": "GENC", "color": "#9866C7", "style": "--", "label": "GenCast", "zorder": 57},
    {"name": "FNV3", "color": "#DA70D6", "style": "--", "label": "FNV3", "zorder": 99},
    {"name": "HKO_AREC", "color": "#1E90FF", "style": "--", "label": "Aurora-ECMWF", "zorder": 56},
    {"name": "HKO_FXEC", "color": "#20B2AA", "style": "--", "label": "FuXi-ECMWF", "zorder": 55},
    {"name": "HKO_FWEC", "color": "#A6C875", "style": "--", "label": "FengWu-ECMWF", "zorder": 54},
]

MODEL_SOURCES = [
    {"name": "ECMWF", "apihub": "ECMWF", "noaa": "ECMF", "knackwx": "ECMF"},
    {"name": "ECMWF_EPS", "apihub": "ECMWF_EPS", "noaa": "EEMN", "knackwx": "EEMN"},
    {"name": "KIM_3h", "apihub": "KIM_3h", "noaa": None, "knackwx": None},
    {"name": "KIM_6h", "apihub": "KIM_6h", "noaa": None, "knackwx": None},
    {"name": "KIM_EPS", "apihub": "KIM_EPS", "noaa": None, "knackwx": None},
    {"name": "UM", "apihub": "UM", "noaa": None, "knackwx": None},
    {"name": "UM_GFDL_6h", "apihub": "UM_GFDL_6h", "noaa": None, "knackwx": None},
    {"name": "UM_KEPS", "apihub": "UM_KEPS", "noaa": None, "knackwx": None},
    {"name": "UKM", "apihub": None, "noaa": "UKM", "knackwx": "UKM"},
    {"name": "UKMO_EPS", "apihub": None, "noaa": "UEMN", "knackwx": "UEMN"},
    {"name": "GFS", "apihub": "GFS", "noaa": "AVNO", "knackwx": "AVNO"},
    {"name": "GFS_EPS", "apihub": "GFS_EPS", "noaa": "AEMN", "knackwx": "AEMN"},
    {"name": "CMC", "apihub": "CMC", "noaa": None, "knackwx": "CMC"},
    {"name": "CMC_EPS", "apihub": "CMC_EPS", "noaa": "CEMN", "knackwx": "CEMN"},
    {"name": "JGSM", "apihub": "JGSM", "noaa": "JGSM", "knackwx": "JGSM"},
    {"name": "TEPS", "apihub": "TEPS", "noaa": "JENS", "knackwx": "JENS"},
    {"name": "NAVGEM", "apihub": "NAVGEM", "noaa": "NVGM", "knackwx": "NVGM"},
    {"name": "FNMOC_EPS", "apihub": "FNMOC_EPS", "noaa": "NEMN", "knackwx": "NMEN"},
    {"name": "CTCX", "apihub": None, "noaa": "CTCX", "knackwx": "CTCX"},
    {"name": "COAMPS_EPS", "apihub": None, "noaa": "CTMN", "knackwx": "CTMN"},
    {"name": "AFUM", "apihub": None, "noaa": "AFUM", "knackwx": None},
    {"name": "HWRF", "apihub": "HWRF", "noaa": "HWRF", "knackwx": "HWRF"},
    {"name": "HAFS", "apihub": "HAFS", "noaa": "HFSA", "knackwx": "HFSA"},
    {"name": "ECMWF_AIFS", "apihub": "ECMWF_AIFS", "noaa": "AIFS", "knackwx": "AIFS"},
    {"name": "ECMWF_AIFS_EPS", "apihub": None, "noaa": "EAIM", "knackwx": "EAMN"},
    {"name": "AGFS", "apihub": None, "noaa": "AGFS", "knackwx": "AGFS"},
    {"name": "AIGEFS", "apihub": None, "noaa": "AIMN", "knackwx": "AIMN"},
    {"name": "IFEC_AI", "apihub": "IFEC_AI", "noaa": None, "knackwx": None},
    {"name": "IFKM_AI", "apihub": "IFKM_AI", "noaa": None, "knackwx": None},
    {"name": "FNEC_AI", "apihub": "FNEC_AI", "noaa": None, "knackwx": None},
    {"name": "FNKM_AI", "apihub": "FNKM_AI", "noaa": None, "knackwx": None},
    {"name": "FNUM_AI", "apihub": "FNUM_AI", "noaa": None, "knackwx": None},
    {"name": "PGEC_AI", "apihub": "PGEC_AI", "noaa": None, "knackwx": None},
    {"name": "PGKM_AI", "apihub": "PGKM_AI", "noaa": None, "knackwx": None},
    {"name": "PGUM_AI", "apihub": "PGUM_AI", "noaa": None, "knackwx": None},
    {"name": "GCEC_AI", "apihub": "GCEC_AI", "noaa": None, "knackwx": None},
    {"name": "GCKM_AI", "apihub": "GCKM_AI", "noaa": None, "knackwx": None},
    {"name": "GCUM_AI", "apihub": "GCUM_AI", "noaa": None, "knackwx": None},
    {"name": "GENC", "apihub": None, "noaa": None, "knackwx": "GENC", "raw_github": "GENC"},
    {"name": "FNV3", "apihub": None, "noaa": "FGNE", "knackwx": "FNV3", "raw_github": "FNV3"},
    {"name": "HKO_AREC", "apihub": "HKO_AREC", "noaa": None, "knackwx": None},
    {"name": "HKO_FXEC", "apihub": "HKO_FXEC", "noaa": None, "knackwx": None},
    {"name": "HKO_FWEC", "apihub": "HKO_FWEC", "noaa": None, "knackwx": None},
]

MODEL_CATEGORIES = {
    "ECMWF": ("DYNAMICAL", "DETERMINISTIC"),
    "ECMWF_EPS": ("DYNAMICAL", "ENSEMBLE"),
    "KIM_3h": ("DYNAMICAL", "DETERMINISTIC"),
    "KIM_6h": ("DYNAMICAL", "DETERMINISTIC"),
    "KIM_EPS": ("DYNAMICAL", "ENSEMBLE"),
    "UM": ("DYNAMICAL", "DETERMINISTIC"),
    "UM_GFDL_6h": ("DYNAMICAL", "DETERMINISTIC"),
    "UM_KEPS": ("DYNAMICAL", "ENSEMBLE"),
    "UKM": ("DYNAMICAL", "DETERMINISTIC"),
    "UKMO_EPS": ("DYNAMICAL", "ENSEMBLE"),
    "GFS": ("DYNAMICAL", "DETERMINISTIC"),
    "GFS_EPS": ("DYNAMICAL", "ENSEMBLE"),
    "CMC": ("DYNAMICAL", "DETERMINISTIC"),
    "CMC_EPS": ("DYNAMICAL", "ENSEMBLE"),
    "JGSM": ("DYNAMICAL", "DETERMINISTIC"),
    "TEPS": ("DYNAMICAL", "ENSEMBLE"),
    "NAVGEM": ("DYNAMICAL", "DETERMINISTIC"),
    "FNMOC_EPS": ("DYNAMICAL", "ENSEMBLE"),
    "CTCX": ("DYNAMICAL", "DETERMINISTIC"),
    "COAMPS_EPS": ("DYNAMICAL", "ENSEMBLE"),
    "AFUM": ("DYNAMICAL", "DETERMINISTIC"),
    "HWRF": ("DYNAMICAL", "DETERMINISTIC"),
    "HAFS": ("DYNAMICAL", "DETERMINISTIC"),
    "ECMWF_AIFS": ("AI", "DETERMINISTIC"),
    "ECMWF_AIFS_EPS": ("AI", "ENSEMBLE"),
    "AGFS": ("AI", "DETERMINISTIC"),
    "AIGEFS": ("AI", "ENSEMBLE"),
    "IFEC_AI": ("AI", "DETERMINISTIC"),
    "IFKM_AI": ("AI", "DETERMINISTIC"),
    "FNEC_AI": ("AI", "DETERMINISTIC"),
    "FNKM_AI": ("AI", "DETERMINISTIC"),
    "FNUM_AI": ("AI", "DETERMINISTIC"),
    "PGEC_AI": ("AI", "DETERMINISTIC"),
    "PGKM_AI": ("AI", "DETERMINISTIC"),
    "PGUM_AI": ("AI", "DETERMINISTIC"),
    "GCEC_AI": ("AI", "DETERMINISTIC"),
    "GCKM_AI": ("AI", "DETERMINISTIC"),
    "GCUM_AI": ("AI", "DETERMINISTIC"),
    "HKO_AREC": ("AI", "DETERMINISTIC"),
    "HKO_FXEC": ("AI", "DETERMINISTIC"),
    "HKO_FWEC": ("AI", "DETERMINISTIC"),
    "GENC": ("AI", "ENSEMBLE"),
    "FNV3": ("AI", "ENSEMBLE"),
}

MODEL_ACTIVE_WINDOWS = {
    "UM": (None, "202603312359"),
    "UM_GFDL_6h": (None, "202603312359"),
    "UM_KEPS": (None, "202603312359"),
    "FNUM_AI": (None, "202603312359"),
    "PGUM_AI": (None, "202603312359"),
    "GCUM_AI": (None, "202603312359"),
    "UKM": ("202604010000", None),
    "UKMO_EPS": ("202604010000", None),
}

NO_PRESSURE_SUMMARY_MODELS = {"UKMO_EPS"}

PRESSURE_MISSING_COLOR = "#A6A6A6"
PRESSURE_OVER_1000_COLOR = "#222222"
PRESSURE_990_1000_COLOR = "#1595FF"
PRESSURE_970_990_COLOR = "#FFB000"
PRESSURE_950_970_COLOR = "#FF1493"
PRESSURE_930_950_COLOR = "#B00020"
PRESSURE_900_930_COLOR = "#6A00A8"
PRESSURE_UNDER_900_COLOR = "#1F00FF"
MIN_STABLE_240_LON_SPAN = 44.0
MIN_STABLE_240_LAT_SPAN = 28.0
MAX_STABLE_240_LON_SPAN = 100.0
MAX_STABLE_240_LAT_SPAN = 64.0
MAX_DISPLAY_240_LON_SPAN = 112.0
MAX_DISPLAY_240_LAT_SPAN = 70.0
MIN_DISPLAY_240_WEST_LON = 80.0
MAX_DISPLAY_240_EAST_LON = 179.8
MIN_DISPLAY_240_SOUTH_LAT = -22.0
MAX_DISPLAY_240_NORTH_LAT = 74.0
MAX_CAMERA_240_LON_DISTANCE = 92.0
MAX_CAMERA_240_LAT_DISTANCE = 62.0

# 240h output now uses a stable fixed West-Pacific view. Keep the east
# boundary below 180E because the current PlateCarree/Mercator path wraps
# values above 180E into a near-global extent.
FIXED_240_MAP_EXTENT = [100.0, 179.9, 0.0, 51.28]


MODEL_NAMES = {model["name"] for model in MODEL_INFO}

SOURCE_ORDER = ("APIHUB", "NOAA", "RAW.GITHUB", "KNACKWX")
MODEL_SOURCE_PRIORITY_OVERRIDES = {
    "GENC": ("RAW.GITHUB", "APIHUB", "NOAA", "KNACKWX"),
    "FNV3": ("RAW.GITHUB", "APIHUB", "NOAA", "KNACKWX"),
}
SOURCE_DISPLAY_NAMES = {
    "APIHUB": "KMA APIHUB",
    "NOAA": "NOAA ATCF",
    "RAW.GITHUB": "GITHUB",
    "KNACKWX": "KNACKWX ATCF",
}
SOURCE_ALIASES = {
    "APIHUB": "APIHUB",
    "KMAAPIHUB": "APIHUB",
    "NOAA": "NOAA",
    "ATCF": "NOAA",
    "NCEP": "NOAA",
    "NOAAATCF": "NOAA",
    "EMCNCEP": "NOAA",
    "NCEPATCF": "NOAA",
    "EMCNCEPATCF": "NOAA",
    "RAWGITHUB": "RAW.GITHUB",
    "GITHUB": "RAW.GITHUB",
    "GDM": "RAW.GITHUB",
    "KNACKWX": "KNACKWX",
    "KNACKWXATCF": "KNACKWX",
}
SOURCE_IDENTIFIER_COLUMNS = {
    "APIHUB": "apihub",
    "NOAA": "noaa",
    "RAW.GITHUB": "raw_github",
    "KNACKWX": "knackwx",
}
SOURCE_MODEL_IDS = {
    source: {
        row[column]
        for row in MODEL_SOURCES
        if (column := SOURCE_IDENTIFIER_COLUMNS[source]) and row.get(column)
    }
    for source in SOURCE_ORDER
}
MODEL_SOURCE_ALIASES = {
    row[column]: row["name"]
    for row in MODEL_SOURCES
    for column in SOURCE_IDENTIFIER_COLUMNS.values()
    if row.get(column)
}
for row in MODEL_SOURCES:
    for source, column in SOURCE_IDENTIFIER_COLUMNS.items():
        model_id = row.get(column)
        if not model_id:
            continue

        alias_ids = []
        if source == "APIHUB" and model_id == "UM_KEPS":
            alias_ids.append("KEPS")
        if model_id.endswith("_AI"):
            alias_ids.append(model_id[:-3])

        for alias_id in alias_ids:
            MODEL_SOURCE_ALIASES.setdefault(alias_id, row["name"])
            SOURCE_MODEL_IDS[source].add(alias_id)
DATA_SOURCE_COLUMN = "_DATA_SOURCE"
MS_PER_KT = 0.514444
KMA_BASE_URL = "https://apihub-pub.kma.go.kr/api/typ01/url/typ_gts_now.php"
DEFAULT_AUTH_KEY = ""
VALID_FCST_HOURS = (120, 240)
PROJECT_ROOT = Path(__file__).resolve().parent
PLOT_FONT_FAMILY = "DejaVu Sans"
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

ANALYSIS_SOURCE_PRIORITY = {
    "MODEL_0H_MEAN": 1,
    "BDECK": 2,
    "JTWC_BDECK": 2,
    "KMA_OFFICIAL": 3,
    "KMA": 3,
}


@dataclass(frozen=True)
class Settings:
    typ_number: int = 6
    data_typ_number: int | None = None
    typ_name: str = "JANGMI"
    typ_name_ko: str = ""
    linked_td_number: int | None = None
    linked_typ_number: int | None = None
    storm_stage: str = "TYP"
    atcf_id: str = "wp062026"
    extra_atcf_ids: tuple[str, ...] = ()
    data_time: str = "202605301200"
    fcst_hours: int = 120
    fcst_hours_options: tuple[int, ...] = ()
    auto_fcst_hours: bool = False
    margin_lat: float = 25
    margin_lon: float = 25
    manual_kma_lat: float = 7.8
    manual_kma_lon: float = 139.2
    lat_padding: float = 4
    lon_padding: float = 4

    figure_width: float = 16.0
    figure_height: float = 12.0
    figure_dpi: int = 100

    extra_west_lon: float = 3.0
    extra_east_lon: float = 8.0
    output_root: Path = PROJECT_ROOT / "VTG_IMG"
    metadata_path: Path | None = None
    auth_key: str = os.getenv("KMA_APIHUB_AUTH_KEY", DEFAULT_AUTH_KEY)
    base_url: str = KMA_BASE_URL
    source_overrides: tuple[tuple[str, str], ...] = ()
    skip_atcf: bool = False
    analysis_lat: float | None = None
    analysis_lon: float | None = None
    analysis_time: str = ""
    analysis_source: str = ""
    analysis_atcf_id: str = ""
    analysis_match_method: str = ""
    analysis_distance_km: float | None = None
    auto_extent: bool = True
    overwrite_output: bool = False
    show_plot: bool = True


@dataclass(frozen=True)
class AnalysisPoint:
    time_utc: str
    lat: float
    lon: float
    source: str
    atcf_id: str = ""
    match_method: str = ""
    distance_km: float | None = None

# Double ATCF ID lookup for TD-to-typhoon promotion windows.
# python VTG2.py --atcf-id wp062026 --extra-atcf-ids wp992026

# Temporary source override.
# --source-override ECMWF_EPS=NOAA

def alias_key(value: str) -> str:
    return "".join(ch for ch in value.upper() if ch.isalnum())


def normalize_source_name(value: str) -> str:
    source = SOURCE_ALIASES.get(alias_key(value))
    if source is None:
        choices = ", ".join(SOURCE_ORDER)
        raise ValueError(f"unknown source '{value}'. Choose one of: {choices}")
    return source


def normalize_model_name(value: str) -> str:
    stripped = value.strip()
    candidates = [
        stripped,
        stripped.upper(),
        stripped.upper().replace("-", "_").replace(" ", "_"),
    ]
    label_map = {
        alias_key(model.get("label", "")): model["name"]
        for model in MODEL_INFO
        if model.get("label")
    }

    for candidate in candidates:
        model_name = MODEL_SOURCE_ALIASES.get(candidate, candidate)
        if model_name in MODEL_NAMES:
            return model_name

    label_match = label_map.get(alias_key(stripped))
    if label_match:
        return label_match

    raise ValueError(f"unknown model '{value}'")


def parse_source_overrides(values: Iterable[str]) -> tuple[tuple[str, str], ...]:
    overrides = []
    for value in values:
        for item in value.split(","):
            item = item.strip()
            if not item:
                continue
            if "=" not in item:
                raise ValueError(f"source override must be MODEL=SOURCE, got '{item}'")
            model_text, source_text = item.split("=", 1)
            overrides.append((
                normalize_model_name(model_text),
                normalize_source_name(source_text),
            ))
    return tuple(overrides)


def parse_fcst_hours_value(value: str) -> tuple[int, ...]:
    hours: list[int] = []
    for token in str(value or "").replace(",", " ").split():
        try:
            hour = int(token)
        except ValueError as exc:
            raise ValueError("--fcst-hours must be a comma/space separated list of integers.") from exc
        if hour not in VALID_FCST_HOURS:
            allowed = ", ".join(f"{item}h" for item in VALID_FCST_HOURS)
            raise ValueError(f"--fcst-hours only supports {allowed}.")
        if hour not in hours:
            hours.append(hour)
    if not hours:
        raise ValueError("--fcst-hours must include at least one forecast hour.")
    return tuple(hours)


def parse_args() -> Settings:
    parser = argparse.ArgumentParser(description="Plot tropical cyclone track guidance.")
    parser.add_argument("--typ-number", type=int, default=Settings.typ_number)
    parser.add_argument(
        "--data-typ-number",
        type=int,
        default=Settings.data_typ_number,
        help="KMA APIHUB TYP number to query when it differs from the displayed TD/TYP number.",
    )
    parser.add_argument("--typ-name", default=Settings.typ_name)
    parser.add_argument("--typ-name-ko", default=Settings.typ_name_ko)
    parser.add_argument("--linked-td-number", type=int, default=Settings.linked_td_number)
    parser.add_argument("--linked-typ-number", type=int, default=Settings.linked_typ_number)
    parser.add_argument("--storm-stage", choices=("TYP", "TD"), default=Settings.storm_stage)
    parser.add_argument("--atcf-id", default=Settings.atcf_id)
    parser.add_argument(
        "--extra-atcf-ids",
        default="",
        help="Comma-separated extra ATCF IDs to merge as the same storm, e.g. wp992026.",
    )
    parser.add_argument("--data-time", default=Settings.data_time)
    parser.add_argument("--fcst-hours", default=str(Settings.fcst_hours))
    parser.add_argument("--auto-fcst-hours", action="store_true", help="Choose 120 or 240h automatically.")
    parser.add_argument("--margin-lat", type=float, default=Settings.margin_lat)
    parser.add_argument("--margin-lon", type=float, default=Settings.margin_lon)
    parser.add_argument("--manual-kma-lat", type=float, default=Settings.manual_kma_lat)
    parser.add_argument("--manual-kma-lon", type=float, default=Settings.manual_kma_lon)
    parser.add_argument("--lat-padding", type=float, default=Settings.lat_padding)
    parser.add_argument("--lon-padding", type=float, default=Settings.lon_padding)

    parser.add_argument("--figure-width", type=float, default=Settings.figure_width,
                    help="Saved figure width in inches.")
    parser.add_argument("--figure-height", type=float, default=Settings.figure_height,
                        help="Saved figure height in inches.")
    parser.add_argument("--figure-dpi", type=int, default=Settings.figure_dpi,
                        help="Saved figure DPI.")

    parser.add_argument("--extra-west-lon", type=float, default=Settings.extra_west_lon,
                        help="Additional longitude degrees added to the west/left side of the map extent.")
    parser.add_argument("--extra-east-lon", type=float, default=Settings.extra_east_lon,
                        help="Additional longitude degrees added to the east/right side of the map extent.")
    parser.add_argument("--output-root", type=Path, default=Settings.output_root)
    parser.add_argument("--metadata-path", type=Path, default=Settings.metadata_path)
    parser.add_argument("--auth-key", default=os.getenv("KMA_APIHUB_AUTH_KEY", DEFAULT_AUTH_KEY))
    parser.add_argument(
        "--source-override",
        action="append",
        default=[],
        metavar="MODEL=SOURCE",
        help="Prefer a source for this run, e.g. ECMWF_EPS=NOAA. Repeat or comma-separate.",
    )
    parser.add_argument("--skip-atcf", action="store_true", help="Use KMA APIHUB data only.")
    parser.add_argument("--analysis-lat", type=float, default=Settings.analysis_lat)
    parser.add_argument("--analysis-lon", type=float, default=Settings.analysis_lon)
    parser.add_argument("--analysis-time", default=Settings.analysis_time)
    parser.add_argument("--analysis-source", default=Settings.analysis_source)
    parser.add_argument("--analysis-atcf-id", default=Settings.analysis_atcf_id)
    parser.add_argument("--analysis-match-method", default=Settings.analysis_match_method)
    parser.add_argument("--analysis-distance-km", type=float, default=Settings.analysis_distance_km)
    parser.add_argument("--no-auto-extent", action="store_true", help="Use fixed margin/padding map extent.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite the deterministic output PNG.")
    parser.add_argument("--no-show", action="store_true", help="Save the PNG without opening a GUI window.")
    args = parser.parse_args()
    try:
        source_overrides = parse_source_overrides(args.source_override)
        fcst_hours_options = parse_fcst_hours_value(args.fcst_hours)
    except ValueError as exc:
        parser.error(str(exc))

    return Settings(
        typ_number=args.typ_number,
        data_typ_number=args.data_typ_number,
        typ_name=args.typ_name.strip(),
        typ_name_ko=args.typ_name_ko.strip(),
        linked_td_number=args.linked_td_number,
        linked_typ_number=args.linked_typ_number,
        storm_stage=args.storm_stage,
        atcf_id=args.atcf_id.lower(),
        extra_atcf_ids=tuple(
            item.strip().lower()
            for item in args.extra_atcf_ids.split(",")
            if item.strip()
        ),
        data_time=args.data_time,
        fcst_hours=fcst_hours_options[0],
        fcst_hours_options=fcst_hours_options,
        auto_fcst_hours=args.auto_fcst_hours,
        margin_lat=args.margin_lat,
        margin_lon=args.margin_lon,
        manual_kma_lat=args.manual_kma_lat,
        manual_kma_lon=args.manual_kma_lon,
        lat_padding=args.lat_padding,
        lon_padding=args.lon_padding,
        figure_width=args.figure_width,
        figure_height=args.figure_height,
        figure_dpi=args.figure_dpi,
        extra_west_lon=args.extra_west_lon,
        extra_east_lon=args.extra_east_lon,
        output_root=args.output_root,
        metadata_path=args.metadata_path,
        auth_key=args.auth_key,
        source_overrides=source_overrides,
        skip_atcf=args.skip_atcf,
        analysis_lat=args.analysis_lat,
        analysis_lon=args.analysis_lon,
        analysis_time=args.analysis_time.strip(),
        analysis_source=args.analysis_source.strip().upper(),
        analysis_atcf_id=args.analysis_atcf_id.strip().lower(),
        analysis_match_method=args.analysis_match_method.strip(),
        analysis_distance_km=args.analysis_distance_km,
        auto_extent=not args.no_auto_extent,
        overwrite_output=args.overwrite,
        show_plot=not args.no_show,
    )


def configure_plot_fonts() -> None:
    global PLOT_FONT_FAMILY
    font_dirs = [
        str(PROJECT_ROOT / "fonts"),
        "/usr/share/fonts/truetype/nanum",
        str(Path.home() / "AppData/Local/Microsoft/Windows/Fonts"),
        "C:/Windows/Fonts",
    ]
    for font_file in fm.findSystemFonts(fontpaths=[p for p in font_dirs if Path(p).exists()]):
        try:
            fm.fontManager.addfont(font_file)
        except RuntimeError:
            pass
    available = {font.name for font in fm.fontManager.ttflist}
    for candidate in ("NanumSquare", "NanumGothic", "NanumBarunGothic", "Malgun Gothic", "DejaVu Sans"):
        if candidate in available:
            PLOT_FONT_FAMILY = candidate
            break
    print(f"Using plot font: {PLOT_FONT_FAMILY}")
    plt.rcParams["font.family"] = [PLOT_FONT_FAMILY, "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False


def kma_url(settings: Settings, mode: str) -> str:
    params = {
        "src": "",
        "tm": settings.data_time,
        "mode": mode,
        "disp": "1",
        "help": "0",
        "authKey": settings.auth_key,
    }
    return f"{settings.base_url}?{urlencode(params)}"


def fetch_text(
    session: requests.Session,
    url: str,
    *,
    retries: int = 3,
    timeout: float = 8,
    retry_delay: float = 1.0,
    encoding: str | None = None,
) -> str | None:
    for attempt in range(1, retries + 1):
        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            if encoding:
                response.encoding = encoding
            return response.text
        except requests.exceptions.RequestException as exc:
            print(f"[attempt {attempt}/{retries}] request failed: {url} ({exc})")
            if attempt < retries:
                time.sleep(retry_delay)
    return None


def read_kma_csv(text: str | None, settings: Settings, *, forecast_only: bool) -> pd.DataFrame:
    if not text or "NODATA" in text.upper():
        return pd.DataFrame(columns=KMA_COLUMNS)

    try:
        df = pd.read_csv(io.StringIO(text), skiprows=2, header=None)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=KMA_COLUMNS)

    if not df.empty and isinstance(df.iloc[-1, 0], str) and "#7777END" in df.iloc[-1, 0]:
        df = df.iloc[:-1]

    if df.shape[1] != len(KMA_COLUMNS):
        print(f"Warning: KMA column count mismatch. Expected {len(KMA_COLUMNS)}, got {df.shape[1]}.")
        return pd.DataFrame(columns=KMA_COLUMNS)

    df.columns = KMA_COLUMNS
    df["TYP"] = pd.to_numeric(df["TYP"], errors="coerce")
    df["TMD"] = pd.to_numeric(df["TMD"], errors="coerce")
    df["LAT"] = pd.to_numeric(df["LAT"], errors="coerce")
    df["LON"] = pd.to_numeric(df["LON"], errors="coerce")
    df["WS"] = pd.to_numeric(df["WS"], errors="coerce")

    mask = df["TYP"].eq(kma_data_typ_number(settings))
    if forecast_only:
        mask &= df["TMD"].le(settings.fcst_hours)
    else:
        mask &= df["SRC"].eq("KMA")
    df = df.loc[mask].copy()
    if forecast_only:
        df = df[df["SRC"].isin(SOURCE_MODEL_IDS["APIHUB"]) | df["SRC"].eq("KMA")].copy()
        df["SRC"] = df["SRC"].replace(MODEL_SOURCE_ALIASES)
    df[DATA_SOURCE_COLUMN] = "APIHUB"
    return df


def kma_data_typ_number(settings: Settings) -> int:
    return settings.data_typ_number or settings.typ_number


def canonical_model_name(model_name: str) -> str:
    return MODEL_SOURCE_ALIASES.get(model_name, model_name)


def storm_numbers(settings: Settings) -> set[int]:
    ids = (settings.atcf_id, *settings.extra_atcf_ids)
    return {int(atcf_id[2:4]) for atcf_id in ids}


def storm_id_from_atcf_id(atcf_id: str) -> str:
    return f"{atcf_id[2:4].upper()}W"


def knackwx_url(settings: Settings, atcf_id: str) -> str:
    init_time = f"{settings.data_time[8:10]}z"
    params = urlencode({"stormID": storm_id_from_atcf_id(atcf_id), "cycle": "late", "initTime": init_time})
    return f"https://api.knackwx.com/atcf/v1/aid/archive?{params}"


def raw_github_url(settings: Settings, model: str) -> str:
    data_dt = datetime.strptime(settings.data_time, "%Y%m%d%H%M")
    date_path = data_dt.strftime("%Y_%m_%d")
    init_time = data_dt.strftime("%Y_%m_%dT%H_00")
    return (
        "https://raw.githubusercontent.com/SSalKim/GDM/main/"
        f"forecast_files/{date_path}/{model}_{init_time}_atcf_a_deck.txt"
    )


def atcf_urls(settings: Settings) -> list[tuple[str, str, int]]:
    urls = []
    for atcf_id in dict.fromkeys((settings.atcf_id, *settings.extra_atcf_ids)):
        urls.append(("NOAA", f"https://www.emc.ncep.noaa.gov/gc_wmb/vxt/DECKS/a{atcf_id}.dat", 0))
    urls.extend([
        ("RAW.GITHUB", raw_github_url(settings, "GENC"), 6),
        ("RAW.GITHUB", raw_github_url(settings, "FNV3"), 6),
    ])
    for atcf_id in dict.fromkeys((settings.atcf_id, *settings.extra_atcf_ids)):
        urls.append(("KNACKWX", knackwx_url(settings, atcf_id), 0))
    return urls


def parse_atcf_coord(series: pd.Series) -> pd.Series:
    text = series.astype("string").str.strip()
    direction = text.str[-1].str.upper()
    value = pd.to_numeric(text.str[:-1], errors="coerce") / 10
    return value.where(direction.isin(["N", "E"]))


def empty_atcf_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=[*ATCF_COLUMNS, DATA_SOURCE_COLUMN])


def trim_atcf_line_after_field_space(line: str) -> str:
    fields = line.split(",")
    cleaned = []
    for field in fields:
        stripped = field.strip()
        if " " in stripped:
            stripped = stripped.split()[0]
        cleaned.append(stripped)
    return ",".join(cleaned)


def sanitize_atcf_text(text: str, *, source: str) -> str:
    if source != "KNACKWX":
        return text
    lines = []
    for line in text.splitlines():
        if not line.strip():
            continue
        lines.append(trim_atcf_line_after_field_space(line))
    return "\n".join(lines)


def read_atcf_csv(text: str | None, *, source: str, skiprows: int = 0) -> pd.DataFrame:
    empty = empty_atcf_frame()
    if not text or not text.strip():
        return empty
    text = sanitize_atcf_text(text, source=source)

    try:
        df = pd.read_csv(
            io.StringIO(text),
            header=None,
            usecols=[0, 1, 2, 4, 5, 6, 7, 8, 9],
            on_bad_lines="skip",
            skiprows=skiprows,
        )
    except (pd.errors.EmptyDataError, ValueError):
        return empty

    df.columns = ATCF_COLUMNS
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.replace(" ", "", regex=False)

    df["ATCF_NUMBER"] = pd.to_numeric(df["ATCF_NUMBER"], errors="coerce")
    df["TM10"] = pd.to_numeric(df["TM10"], errors="coerce")
    df["FTM"] = pd.to_numeric(df["FTM"], errors="coerce")
    df["WS(KT)"] = pd.to_numeric(df["WS(KT)"], errors="coerce")
    df["SLP"] = pd.to_numeric(df["SLP"], errors="coerce")
    df["LATI"] = parse_atcf_coord(df["LATI"])
    df["LONG"] = parse_atcf_coord(df["LONG"])
    df[DATA_SOURCE_COLUMN] = source
    return df


def fetch_atcf_data(session: requests.Session, settings: Settings) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(fetch_text, session, url, retries=2, timeout=15): (source, url, skiprows)
            for source, url, skiprows in atcf_urls(settings)
        }
        for future in as_completed(futures):
            source, url, skiprows = futures[future]
            try:
                frame = read_atcf_csv(future.result(), source=source, skiprows=skiprows)
                if not frame.empty:
                    frames.append(frame)
            except Exception as exc:
                print(f"Warning: failed to parse ATCF source {url}: {exc}")

    if not frames:
        return empty_atcf_frame()

    raw = pd.concat(frames, ignore_index=True)
    target_storm_nums = storm_numbers(settings)
    data_time_10 = int(settings.data_time[:10])
    source_model_mask = pd.Series(False, index=raw.index)
    for source, model_ids in SOURCE_MODEL_IDS.items():
        if model_ids:
            source_model_mask |= raw[DATA_SOURCE_COLUMN].eq(source) & raw["MODEL"].isin(model_ids)

    mask = (
        source_model_mask
        & raw["FTM"].le(settings.fcst_hours)
        & raw["TM10"].eq(data_time_10)
        & raw["ATCF_NUMBER"].isin(target_storm_nums)
    )
    return raw.loc[mask].copy()


def atcf_to_kma_schema(raw: pd.DataFrame, settings: Settings) -> pd.DataFrame:
    if raw.empty:
        return pd.DataFrame(columns=KMA_COLUMNS)

    raw = raw.copy()
    for col in ["ATCF_NUMBER", "TM10", "FTM", "WS(KT)", "SLP", "LATI", "LONG"]:
        raw[col] = pd.to_numeric(raw[col], errors="coerce")

    base_times = pd.to_datetime(raw["TM10"].astype("Int64").astype(str), format="%Y%m%d%H", errors="coerce")
    ft_times = base_times + pd.to_timedelta(raw["FTM"], unit="h")
    converted = pd.DataFrame({
        "FT": raw["FTM"].gt(0).astype(int),
        "YY": base_times.dt.year,
        "TYP": settings.typ_number,
        "SEQ": raw["FTM"].ne(0).astype(int),
        "TMD": raw["FTM"],
        "TYP_TM(UTC)": base_times.dt.strftime("%Y%m%d%H%M"),
        "FT_TM(UTC)": ft_times.dt.strftime("%Y%m%d%H%M"),
        "LAT": raw["LATI"],
        "LON": raw["LONG"],
        "DIR": "",
        "SP": "",
        "PS": raw["SLP"],
        "WS": (raw["WS(KT)"] * MS_PER_KT).round(),
        "T15": "",
        "T25": "",
        "RAD": "",
        "15D": "",
        "15R": "",
        "SRC": raw["MODEL"].replace(MODEL_SOURCE_ALIASES),
        DATA_SOURCE_COLUMN: raw[DATA_SOURCE_COLUMN],
        "": "",
    })
    return converted.dropna(subset=["FT_TM(UTC)", "LAT", "LON"])


def parse_ft_time(series: pd.Series) -> pd.Series:
    clean = series.astype("string").str.split(".", n=1).str[0]
    return pd.to_datetime(clean, format="%Y%m%d%H%M", errors="coerce")


def normalize_history_time(value: str) -> str:
    text = str(value or "").strip().split(".", 1)[0]
    if len(text) >= 12 and text[:12].isdigit():
        return text[:12]
    if len(text) >= 10 and text[:10].isdigit():
        return f"{text[:10]}00"
    return ""


def analysis_source_priority(source: str) -> int:
    return ANALYSIS_SOURCE_PRIORITY.get(str(source or "").strip().upper(), 0)


def storm_history_keys(settings: Settings) -> list[str]:
    year = storm_year(settings)
    keys: list[str] = []

    def add(key: str) -> None:
        if key and key not in keys:
            keys.append(key)

    stage = settings.storm_stage.upper()
    if stage == "TD":
        add(f"td_{year}_{settings.typ_number:02d}")
        if settings.linked_typ_number:
            add(f"typ_{year}_{settings.linked_typ_number:02d}")
    else:
        if settings.linked_td_number:
            add(f"td_{year}_{settings.linked_td_number:02d}")
        add(f"typ_{year}_{settings.typ_number:02d}")
    return keys


def track_history_paths(settings: Settings) -> list[Path]:
    base = settings.output_root / "metadata" / "track_history" / storm_year(settings)
    return [base / f"{key}.json" for key in storm_history_keys(settings)]


def history_aliases(settings: Settings) -> list[str]:
    aliases = storm_history_keys(settings)
    for atcf_id in (settings.atcf_id, *settings.extra_atcf_ids):
        atcf_id = str(atcf_id or "").strip().lower()
        if atcf_id and not settings.skip_atcf and atcf_id not in aliases:
            aliases.append(atcf_id)
    return aliases


def empty_track_history(settings: Settings) -> dict:
    keys = storm_history_keys(settings)
    return {
        "version": 1,
        "year": storm_year(settings),
        "primary_key": keys[0] if keys else "",
        "aliases": history_aliases(settings),
        "points": [],
    }


def load_track_history(settings: Settings) -> dict:
    history = empty_track_history(settings)
    for path in track_history_paths(settings):
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(payload, dict):
            continue
        for alias in payload.get("aliases", []):
            alias = str(alias or "").strip()
            if alias and alias not in history["aliases"]:
                history["aliases"].append(alias)
        for point in payload.get("points", []):
            if isinstance(point, dict):
                upsert_history_point(history, point)
    return history


def history_point_payload(point: AnalysisPoint) -> dict:
    payload = {
        "time_utc": normalize_history_time(point.time_utc),
        "lat": round(float(point.lat), 4),
        "lon": round(float(point.lon), 4),
        "source": point.source,
    }
    if point.atcf_id:
        payload["atcf_id"] = point.atcf_id
    if point.match_method:
        payload["match_method"] = point.match_method
    if point.distance_km is not None:
        payload["distance_km"] = round(float(point.distance_km), 1)
    return payload


def upsert_history_point(history: dict, point: dict | AnalysisPoint) -> bool:
    payload = history_point_payload(point) if isinstance(point, AnalysisPoint) else dict(point)
    payload["time_utc"] = normalize_history_time(str(payload.get("time_utc") or ""))
    if not payload["time_utc"]:
        return False
    try:
        payload["lat"] = round(float(payload["lat"]), 4)
        payload["lon"] = round(float(payload["lon"]), 4)
    except (KeyError, TypeError, ValueError):
        return False
    payload["source"] = str(payload.get("source") or "MODEL_0H_MEAN").strip().upper()

    points = history.setdefault("points", [])
    for index, existing in enumerate(points):
        if normalize_history_time(str(existing.get("time_utc") or "")) != payload["time_utc"]:
            continue
        existing_priority = analysis_source_priority(str(existing.get("source") or ""))
        payload_priority = analysis_source_priority(payload["source"])
        if payload_priority < existing_priority:
            return False
        if payload_priority == existing_priority and existing == payload:
            return False
        points[index] = payload
        return True

    points.append(payload)
    return True


def save_track_history(settings: Settings, history: dict, *, original: dict) -> None:
    history["aliases"] = sorted(set([*history.get("aliases", []), *history_aliases(settings)]))
    history["points"] = sorted(
        history.get("points", []),
        key=lambda item: normalize_history_time(str(item.get("time_utc") or "")),
    )
    if history == original:
        return
    history["updated_at_utc"] = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    paths = track_history_paths(settings)
    if not paths:
        return
    primary = paths[0]
    primary.parent.mkdir(parents=True, exist_ok=True)
    primary.write_text(
        json.dumps(history, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def cli_analysis_point(settings: Settings) -> AnalysisPoint | None:
    if settings.analysis_lat is None or settings.analysis_lon is None:
        return None
    time_utc = normalize_history_time(settings.analysis_time or settings.data_time)
    if not time_utc or time_utc[:10] != settings.data_time[:10]:
        print(
            "Warning: analysis point time does not match data_time; "
            f"ignoring analysis point ({time_utc} vs {settings.data_time})."
        )
        return None
    return AnalysisPoint(
        time_utc=time_utc,
        lat=float(settings.analysis_lat),
        lon=float(settings.analysis_lon),
        source=settings.analysis_source or "BDECK",
        atcf_id=settings.analysis_atcf_id,
        match_method=settings.analysis_match_method,
        distance_km=settings.analysis_distance_km,
    )


def kma_start_analysis_point(df: pd.DataFrame, settings: Settings) -> AnalysisPoint | None:
    if df.empty:
        return None
    start = df[(df["SRC"] == "KMA") & (pd.to_numeric(df["TMD"], errors="coerce") == 0)].head(1)
    if start.empty:
        return None
    row = start.iloc[0]
    try:
        lat = float(row["LAT"])
        lon = float(row["LON"])
    except (TypeError, ValueError):
        return None
    source = str(row.get(DATA_SOURCE_COLUMN, "") or "").strip().upper()
    if source == "APIHUB":
        source = "KMA_OFFICIAL"
    elif not source:
        source = "MODEL_0H_MEAN"
    return AnalysisPoint(
        time_utc=normalize_history_time(str(row.get("FT_TM(UTC)") or settings.data_time)),
        lat=lat,
        lon=lon,
        source=source,
        atcf_id=settings.analysis_atcf_id or ("" if settings.skip_atcf else settings.atcf_id),
        match_method=settings.analysis_match_method if source == "BDECK" else "",
        distance_km=settings.analysis_distance_km if source == "BDECK" else None,
    )


def official_points_from_past_kma(past_kma: pd.DataFrame) -> list[AnalysisPoint]:
    if past_kma.empty:
        return []
    points: list[AnalysisPoint] = []
    for _, row in past_kma.iterrows():
        try:
            lat = float(row["LAT"])
            lon = float(row["LON"])
        except (TypeError, ValueError):
            continue
        time_utc = normalize_history_time(str(row.get("FT_TM(UTC)") or ""))
        if not time_utc:
            continue
        points.append(AnalysisPoint(time_utc=time_utc, lat=lat, lon=lon, source="KMA_OFFICIAL"))
    return points


def history_to_past_track(history: dict, current_dt: datetime | None) -> pd.DataFrame:
    rows = []
    for point in history.get("points", []):
        time_utc = normalize_history_time(str(point.get("time_utc") or ""))
        if not time_utc:
            continue
        try:
            lat = float(point["lat"])
            lon = float(point["lon"])
        except (KeyError, TypeError, ValueError):
            continue
        rows.append({
            "FT_TM(UTC)": time_utc,
            "LAT": lat,
            "LON": lon,
            "SRC": "KMA",
            DATA_SOURCE_COLUMN: str(point.get("source") or ""),
        })
    if not rows:
        return pd.DataFrame(columns=[*KMA_COLUMNS, "FT_TIME"])
    past = pd.DataFrame(rows)
    past["FT_TIME"] = parse_ft_time(past["FT_TM(UTC)"])
    past = past.dropna(subset=["FT_TIME"]).sort_values("FT_TIME").reset_index(drop=True)
    if current_dt is not None:
        past = past[past["FT_TIME"].le(current_dt + timedelta(minutes=1))].copy()
    if past.empty:
        return past
    gaps = past["FT_TIME"].diff().gt(pd.Timedelta(hours=18))
    if gaps.any():
        past = past.loc[gaps[gaps].index[-1]:].reset_index(drop=True)
    return past


def current_intensity(settings: Settings) -> str:
    return "TD" if settings.storm_stage.upper() == "TD" else "TYP"


def trim_discontinuous_forecast(group: pd.DataFrame, *, gap_factor: float = 2.5) -> pd.DataFrame:
    """Keep the first continuous forecast segment when late-hour outliers appear."""
    clean = group.copy()
    clean["TMD"] = pd.to_numeric(clean["TMD"], errors="coerce")
    leads = sorted(clean["TMD"].dropna().unique())
    if len(leads) < 3:
        return clean

    diffs = [b - a for a, b in zip(leads, leads[1:]) if b > a]
    regular_steps = [diff for diff in diffs if diff > 0]
    if not regular_steps:
        return clean

    expected_step = min(regular_steps)
    max_allowed_gap = max(expected_step * gap_factor, expected_step + 6)

    for previous_lead, next_lead in zip(leads, leads[1:]):
        if next_lead - previous_lead > max_allowed_gap:
            print(
                f"{clean['SRC'].iloc[0]} {clean[DATA_SOURCE_COLUMN].iloc[0]}: "
                f"trimmed after {previous_lead:g}h due to forecast gap to {next_lead:g}h"
            )
            return clean[clean["TMD"].le(previous_lead)].copy()
    return clean


def source_display_name(source: str) -> str:
    return SOURCE_DISPLAY_NAMES.get(source, source)


def source_priority_for_model(model_name: str, settings: Settings) -> tuple[str, ...]:
    priority = list(MODEL_SOURCE_PRIORITY_OVERRIDES.get(model_name, SOURCE_ORDER))
    overrides = dict(settings.source_overrides)
    preferred_source = overrides.get(model_name)
    if preferred_source:
        priority = [preferred_source, *[source for source in priority if source != preferred_source]]
        priority.extend(source for source in SOURCE_ORDER if source not in priority)
    return tuple(priority)


def select_model_sources_by_priority(df: pd.DataFrame, settings: Settings) -> pd.DataFrame:
    """Keep one source per model using fixed provider priority."""
    if df.empty or DATA_SOURCE_COLUMN not in df.columns:
        return df

    selected_frames = []
    for model_name, model_df in df.groupby("SRC", dropna=True):
        source_frames = {}
        for source, source_df in model_df.groupby(DATA_SOURCE_COLUMN, dropna=True):
            source_frames[source] = trim_discontinuous_forecast(source_df)

        if not source_frames:
            continue

        priority = source_priority_for_model(model_name, settings)
        ordered_sources = [source for source in priority if source in source_frames]
        ordered_sources.extend(sorted(source for source in source_frames if source not in priority))
        best_source = ordered_sources[0]
        best_df = source_frames[best_source]
        skipped = ordered_sources[1:]
        requested_source = dict(settings.source_overrides).get(model_name)
        if requested_source and requested_source not in source_frames:
            print(
                f"{model_name}: requested {source_display_name(requested_source)} unavailable; "
                f"using {source_display_name(best_source)}"
            )
        if skipped:
            print(
                f"{model_name}: selected {source_display_name(best_source)} by source priority; "
                f"skipped {', '.join(source_display_name(source) for source in skipped)}"
            )
        selected_frames.append(best_df)

    if not selected_frames:
        return df.iloc[0:0].copy()
    return pd.concat(selected_frames, ignore_index=True)


def normalize_track_data(kma_df: pd.DataFrame, atcf_df: pd.DataFrame, settings: Settings) -> pd.DataFrame:
    df = pd.concat([kma_df, atcf_to_kma_schema(atcf_df, settings)], ignore_index=True)
    if df.empty:
        return df

    df = select_model_sources_by_priority(df, settings)
    df = df.drop_duplicates(subset=["TYP", "SRC", "FT_TM(UTC)"], keep="first")
    df = df[df["SRC"].isin(MODEL_NAMES)].copy()
    for col in ["LAT", "LON", "WS", "TMD", "SEQ"]:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["LAT", "LON"])
    df = apply_common_kma_start(df, settings)
    return trim_dateline_reflected_tracks(df)


def suspected_dateline_reflection_cutoff(track: pd.DataFrame) -> float | None:
    clean = track.dropna(subset=["LAT", "LON", "TMD"]).copy()
    if clean.empty or len(clean) < 5:
        return None

    clean["LAT"] = pd.to_numeric(clean["LAT"], errors="coerce")
    clean["LON"] = pd.to_numeric(clean["LON"], errors="coerce")
    clean["TMD"] = pd.to_numeric(clean["TMD"], errors="coerce")
    clean = clean.dropna(subset=["LAT", "LON", "TMD"]).sort_values(["TMD", "FT_TM(UTC)", "SEQ"])
    forecast = clean[clean["TMD"].ge(0)].reset_index(drop=True)
    if len(forecast) < 5:
        return None

    lons = forecast["LON"].astype(float)
    lats = forecast["LAT"].astype(float)
    if lons.max() < 172.0 or lons.min() < 0 or lons.max() > 180.5:
        return None

    peak_pos = int(lons.idxmax())
    if peak_pos < 2 or peak_pos >= len(forecast) - 2:
        return None

    peak_lon = float(lons.iloc[peak_pos])
    prior_min_lon = float(lons.iloc[:peak_pos + 1].min())
    if peak_lon - prior_min_lon < 7.0:
        return None

    tail = lons.iloc[peak_pos + 1:]
    tail_backtrack = peak_lon - float(tail.min())
    negative_steps = int((lons.diff().iloc[peak_pos + 1:] < -0.8).sum())
    if tail_backtrack < 5.0 or negative_steps < 2:
        return None

    lat_drop = float(lats.iloc[peak_pos] - lats.iloc[peak_pos + 1:].median())
    if lat_drop > 4.0:
        return None

    return float(forecast["TMD"].iloc[peak_pos])


def trim_dateline_reflected_tracks(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or DATA_SOURCE_COLUMN not in df.columns:
        return df

    frames: list[pd.DataFrame] = []
    for (model_name, source_name), track in df.groupby(["SRC", DATA_SOURCE_COLUMN], dropna=False):
        cutoff = None
        if str(source_name) == "APIHUB":
            cutoff = suspected_dateline_reflection_cutoff(track)
        if cutoff is None:
            frames.append(track)
            continue

        tmd = pd.to_numeric(track["TMD"], errors="coerce")
        trimmed = track[tmd.le(cutoff) | tmd.isna()].copy()
        removed = len(track) - len(trimmed)
        print(
            f"{model_name} APIHUB: trimmed {removed} point(s) after {cutoff:g}h "
            "due to suspected dateline-reflected longitude tail"
        )
        frames.append(trimmed)

    return pd.concat(frames, ignore_index=True) if frames else df


def apply_common_kma_start(df: pd.DataFrame, settings: Settings) -> pd.DataFrame:
    kma_start = df[(df["SRC"] == "KMA") & (df["TMD"] == 0)].head(1).copy()
    if kma_start.empty or kma_start[["LAT", "LON"]].isna().any(axis=None):
        override = cli_analysis_point(settings)
        source = "MODEL_0H_MEAN"
        if override:
            lat = override.lat
            lon = override.lon
            time_utc = override.time_utc
            source = override.source
            print(
                "KMA 0h is missing; using "
                f"{source} analysis point: {lat:.2f}N, {lon:.2f}E."
            )
        else:
            model_zero = (
                df[(df["SRC"] != "KMA") & (df["TMD"] == 0)]
                .dropna(subset=["LAT", "LON"])
                .drop_duplicates(subset=["SRC"], keep="first")
            )
            if model_zero.empty:
                print("Warning: KMA 0h is missing and no model 0h points are available.")
                return df.reset_index(drop=True)
            lat = float(model_zero["LAT"].mean())
            lon = float(model_zero["LON"].mean())
            time_utc = settings.data_time
            print(
                "KMA 0h is missing; using the mean of "
                f"{len(model_zero)} model 0h start point(s): {lat:.2f}N, {lon:.2f}E."
            )
        kma_start = pd.DataFrame([{
            "FT": 0,
            "YY": int(settings.data_time[:4]),
            "TYP": settings.typ_number,
            "SEQ": 0,
            "TMD": 0,
            "TYP_TM(UTC)": time_utc,
            "FT_TM(UTC)": time_utc,
            "LAT": lat,
            "LON": lon,
            "WS": 0,
            "SRC": "KMA",
            DATA_SOURCE_COLUMN: source,
        }])

    kma_lat = kma_start.iloc[0]["LAT"]
    kma_lon = kma_start.iloc[0]["LON"]
    kma_tm = str(kma_start.iloc[0]["FT_TM(UTC)"])

    starts = [kma_start]
    model_names = sorted(name for name in df["SRC"].dropna().unique() if name != "KMA")
    for model_name in model_names:
        model_track = df[df["SRC"] == model_name].copy()
        model_start = model_track[model_track["TMD"] == 0].head(1).copy()
        if model_start.empty:
            model_track["TMD"] = pd.to_numeric(model_track["TMD"], errors="coerce")
            model_start = (
                model_track[model_track["TMD"].gt(0)]
                .sort_values(["TMD", "FT_TM(UTC)", "SEQ"])
                .head(1)
                .copy()
            )
        if model_start.empty:
            continue
        model_start.loc[:, "LAT"] = kma_lat
        model_start.loc[:, "LON"] = kma_lon
        model_start.loc[:, "TMD"] = 0
        model_start.loc[:, "SEQ"] = 0
        model_start.loc[:, "FT"] = 0
        model_start.loc[:, "TYP_TM(UTC)"] = kma_tm
        model_start.loc[:, "FT_TM(UTC)"] = kma_tm
        starts.append(model_start)

    future = df[df["TMD"] != 0].copy()
    return (
        pd.concat([future, *starts], ignore_index=True)
        .drop_duplicates(subset=["TYP", "SRC", "FT_TM(UTC)"], keep="first")
        .reset_index(drop=True)
    )


def build_past_kma_track(past_df: pd.DataFrame) -> pd.DataFrame:
    if past_df.empty:
        return past_df

    past = past_df.dropna(subset=["LAT", "LON", "FT_TM(UTC)"]).copy()
    past["FT_TIME"] = parse_ft_time(past["FT_TM(UTC)"])
    past = past.dropna(subset=["FT_TIME"]).sort_values("FT_TIME").reset_index(drop=True)
    if past.empty:
        return past

    gaps = past["FT_TIME"].diff().gt(pd.Timedelta(hours=6))
    if gaps.any():
        past = past.loc[gaps[gaps].index[-1]:].reset_index(drop=True)
    return past


def excluded_models_for(df: pd.DataFrame) -> set[str]:
    grouped = {
        name: group
        for name, group in df.groupby("SRC", dropna=True)
    }

    has_kim_3h = "KIM_3h" in grouped and has_forecast_points(grouped["KIM_3h"])
    has_kim_6h = "KIM_6h" in grouped and has_forecast_points(grouped["KIM_6h"])

    has_um = "UM" in grouped and has_forecast_points(grouped["UM"])
    has_um_gfdl = "UM_GFDL_6h" in grouped and has_forecast_points(grouped["UM_GFDL_6h"])

    excluded = {"KMA"}

    if has_kim_3h or not has_kim_6h:
        excluded.add("KIM_6h")

    if has_um:
        excluded.update({"UM_GFDL_6h", "UKM"})
    elif has_um_gfdl:
        excluded.update({"UM", "UKM"})
    else:
        excluded.add("UM_GFDL_6h")

    return excluded


def active_model_names(settings: Settings) -> set[str]:
    data_dt = datetime.strptime(settings.data_time, "%Y%m%d%H%M")
    active = set()
    for model in MODEL_INFO:
        name = model["name"]
        if name == "KMA":
            continue

        start_str, end_str = MODEL_ACTIVE_WINDOWS.get(name, (None, None))
        if start_str and data_dt < datetime.strptime(start_str, "%Y%m%d%H%M"):
            continue
        if end_str and data_dt > datetime.strptime(end_str, "%Y%m%d%H%M"):
            continue
        active.add(name)
    return active


def active_model_target_count(settings: Settings) -> int:
    active = active_model_names(settings)
    count = len(active)
    if {"KIM_3h", "KIM_6h"}.issubset(active):
        count -= 1
    if {"UM", "UM_GFDL_6h"}.issubset(active):
        count -= 1
    return count


def model_display_label(model_name: str) -> str:
    for model in MODEL_INFO:
        if model["name"] == model_name:
            return model.get("label", model_name).strip()
    return model_name


def plotted_model_labels(df: pd.DataFrame, settings: Settings) -> list[str]:
    labels: list[str] = []
    for model_name in sorted(plotted_model_names(df, settings)):
        label = model_display_label(model_name)
        if label and label not in labels:
            labels.append(label)
    return labels


def has_forecast_points(track: pd.DataFrame, min_hour: float = 3) -> bool:
    if track.empty or "TMD" not in track:
        return False
    leads = pd.to_numeric(track["TMD"], errors="coerce")
    return leads.ge(min_hour).any()


def plotted_model_names(df: pd.DataFrame, settings: Settings) -> set[str]:
    excluded = excluded_models_for(df)
    active = active_model_names(settings)
    names = set()
    for model_name, track in df.groupby("SRC", dropna=True):
        if model_name in active and model_name not in excluded and has_forecast_points(track):
            names.add(model_name)
    return names


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_km = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * radius_km * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1 - a)))


def model_lead_support(df: pd.DataFrame, settings: Settings) -> dict[int, int]:
    support = {}
    names = plotted_model_names(df, settings)
    if not names:
        return {lead: 0 for lead in VALID_FCST_HOURS}
    forecast = df[df["SRC"].isin(names)].copy()
    forecast["TMD"] = pd.to_numeric(forecast["TMD"], errors="coerce")
    max_leads = forecast.groupby("SRC")["TMD"].max()
    for lead in VALID_FCST_HOURS:
        support[lead] = int(max_leads.ge(lead).sum())
    return support


def kma_motion_km_per_day(df: pd.DataFrame) -> float:
    kma = df[df["SRC"].eq("KMA")].copy()
    if kma.empty:
        return 0.0
    kma["TMD"] = pd.to_numeric(kma["TMD"], errors="coerce")
    kma = kma.dropna(subset=["TMD", "LAT", "LON"]).sort_values("TMD")
    if kma.empty:
        return 0.0
    start = kma.iloc[0]
    candidates = kma[kma["TMD"].between(18, 36)]
    if candidates.empty:
        candidates = kma[kma["TMD"].gt(start["TMD"])]
    if candidates.empty:
        return 0.0
    target = candidates.iloc[(candidates["TMD"] - 24).abs().argsort().iloc[0]]
    hours = max(float(target["TMD"] - start["TMD"]), 1.0)
    distance = haversine_km(float(start["LAT"]), float(start["LON"]), float(target["LAT"]), float(target["LON"]))
    return distance / hours * 24


def current_storm_latitude(df: pd.DataFrame) -> float:
    start = df[(df["SRC"].eq("KMA")) & (pd.to_numeric(df["TMD"], errors="coerce").eq(0))]
    if not start.empty:
        return float(pd.to_numeric(start["LAT"], errors="coerce").dropna().iloc[0])
    values = pd.to_numeric(df["LAT"], errors="coerce").dropna()
    return float(values.iloc[0]) if not values.empty else 0.0


def choose_auto_fcst_hours(df: pd.DataFrame, settings: Settings) -> int:
    support = model_lead_support(df, settings)
    model_total = max(len(plotted_model_names(df, settings)), 1)
    min_support = max(5, math.ceil(model_total * 0.35))
    supported = [lead for lead in VALID_FCST_HOURS if support.get(lead, 0) >= min_support]
    base = max(supported) if supported else 120

    lat = current_storm_latitude(df)
    speed = kma_motion_km_per_day(df)

    if lat >= 32 and speed >= 420:
        return min(base, 120)
    return base


def limit_forecast_hours(df: pd.DataFrame, settings: Settings) -> pd.DataFrame:
    limited = df.copy()
    limited["TMD"] = pd.to_numeric(limited["TMD"], errors="coerce")
    return limited[limited["TMD"].le(settings.fcst_hours)].copy()


def track_intensity_summary(track: pd.DataFrame, model_name: str) -> str:
    forecast = track[pd.to_numeric(track["TMD"], errors="coerce").ge(3)].copy()
    if forecast.empty:
        return ""

    forecast["WS"] = pd.to_numeric(forecast["WS"], errors="coerce")
    forecast["PS"] = pd.to_numeric(forecast["PS"], errors="coerce")
    forecast["TMD"] = pd.to_numeric(forecast["TMD"], errors="coerce")
    forecast = forecast.dropna(subset=["TMD"])
    if forecast.empty:
        return ""

    valid_pressure = forecast["PS"].where(forecast["PS"].gt(0))
    has_pressure = (
        model_name not in NO_PRESSURE_SUMMARY_MODELS
        and valid_pressure.notna().any()
    )
    max_lead = int(round(float(forecast["TMD"].max())))

    # If pressure is missing, keep the inactive-style summary.
    if not has_pressure:
        return f"{'----':>4}hPa +----/{max_lead:03d}h"

    # If pressure exists, summarize the model at its minimum pressure time.
    peak = forecast.loc[valid_pressure.idxmin()]

    pressure = peak["PS"]
    pressure_value = str(int(round(float(pressure))))

    pressure_text = f"{pressure_value:>4}hPa"
    lead_text = f"+{int(round(float(peak['TMD']))):03d}/{max_lead:03d}h"
    return f"{pressure_text} {lead_text}"


def split_intensity_summary(metric: str) -> tuple[str, str]:
    if not metric:
        return "", ""
    parts = metric.split()
    if len(parts) >= 2:
        return parts[0], parts[1]
    return metric, ""


def pressure_value_from_text(pressure_text: str) -> int | None:
    digits = "".join(ch for ch in pressure_text if ch.isdigit())
    if not digits:
        return None
    return int(digits)


def pressure_metric_color(pressure_text: str) -> str:
    pressure = pressure_value_from_text(pressure_text)

    if pressure is None:
        return PRESSURE_MISSING_COLOR

    if pressure > 1000:
        return PRESSURE_OVER_1000_COLOR
    if pressure >= 990:
        return PRESSURE_990_1000_COLOR
    if pressure >= 970:
        return PRESSURE_970_990_COLOR
    if pressure >= 950:
        return PRESSURE_950_970_COLOR
    if pressure >= 930:
        return PRESSURE_930_950_COLOR
    if pressure >= 900:
        return PRESSURE_900_930_COLOR
    return PRESSURE_UNDER_900_COLOR


def marker_points_every_24h(track: pd.DataFrame) -> pd.DataFrame:
    if track.empty:
        return track
    base_time = track["FT_TIME"].iloc[0]
    elapsed_hours = (track["FT_TIME"] - base_time).dt.total_seconds() / 3600
    return track[elapsed_hours.mod(24).eq(0)]


def model_visual_style(model_name: str, model: dict) -> dict:
    basis, forecast_type = MODEL_CATEGORIES.get(model_name, ("DYNAMICAL", "DETERMINISTIC"))
    is_ai = basis == "AI"
    is_ensemble = forecast_type == "ENSEMBLE"
    color = model["color"]
    return {
        "color": color,
        "linestyle": "--" if is_ai else "-",
        "linewidth": 1.0 if is_ensemble else 1.7,
        "alpha": 0.78 if is_ensemble else 1.0,
        "marker": "o",
        "markerfacecolor": color,
        "markeredgecolor": color,
        "markeredgewidth": 0.8,
        "markersize": 4.6 if is_ensemble else 5,
        "basis": basis,
        "forecast_type": forecast_type,
    }


def plot_past_track(ax, past_kma: pd.DataFrame, current_dt: datetime | None) -> None:
    if past_kma.empty:
        print("No KMA past track data to plot.")
        return
    if current_dt is None:
        print("Warning: current data_time could not be parsed. Skipping past KMA markers.")
        return

    ax.plot(past_kma["LON"], past_kma["LAT"], color="white", linestyle=":", linewidth=2, zorder=0, transform=ccrs.PlateCarree())
    earliest = past_kma["FT_TIME"].min()
    targets = []
    hours_back = 24
    while current_dt - timedelta(hours=hours_back) >= earliest - timedelta(hours=3):
        targets.append(current_dt - timedelta(hours=hours_back))
        hours_back += 24
        if hours_back > 365 * 24 * 10:
            break

    if not targets:
        return

    markers = []
    for target in targets:
        idx = (past_kma["FT_TIME"] - target).abs().idxmin()
        point = past_kma.loc[idx]
        if abs(point["FT_TIME"] - target) <= timedelta(hours=3):
            markers.append(point)

    if markers:
        marker_df = pd.DataFrame(markers).drop_duplicates(subset=["FT_TIME"])
        ax.plot(marker_df["LON"], marker_df["LAT"], marker="o", color="white", linestyle="None", markersize=5, zorder=0, transform=ccrs.PlateCarree())


def update_and_merge_past_track(
    *,
    df: pd.DataFrame,
    official_past: pd.DataFrame,
    settings: Settings,
) -> pd.DataFrame:
    history = load_track_history(settings)
    original = json.loads(json.dumps(history, ensure_ascii=False))

    for point in official_points_from_past_kma(official_past):
        upsert_history_point(history, point)

    current_point = kma_start_analysis_point(df, settings)
    if current_point:
        upsert_history_point(history, current_point)

    save_track_history(settings, history, original=original)

    current_dt = pd.to_datetime(settings.data_time, format="%Y%m%d%H%M", errors="coerce")
    current_py_dt = None if pd.isna(current_dt) else current_dt.to_pydatetime()
    merged = history_to_past_track(history, current_py_dt)
    if not merged.empty:
        return merged
    return official_past


def tc_id(settings: Settings) -> str:
    year_suffix = int(storm_year(settings)) % 100
    return f"{year_suffix:02d}{settings.typ_number:02d}"


def storm_year(settings: Settings) -> str:
    if len(settings.data_time) >= 4 and settings.data_time[:4].isdigit():
        return settings.data_time[:4]
    if len(settings.atcf_id) >= 8 and settings.atcf_id[4:].isdigit():
        return settings.atcf_id[4:]
    return datetime.utcnow().strftime("%Y")


def storm_number_label(settings: Settings) -> str:
    atcf_id = settings.atcf_id.lower()
    if settings.skip_atcf or len(atcf_id) < 8 or not atcf_id[2:4].isdigit():
        return ""
    basin = atcf_id[:2].upper()
    basin_label = "W" if basin == "WP" else basin
    return f"({atcf_id[2:4]}{basin_label})"


def display_typ_name(settings: Settings) -> str:
    name = str(settings.typ_name or "").strip()
    return "" if name.upper() == "NONAME" else name


def output_path(settings: Settings) -> Path:
    year_str = storm_year(settings)
    cyclone_id = tc_id(settings)
    stage = settings.storm_stage.upper()
    storm_name = settings.typ_name or "NONAME"
    if stage == "TD":
        dir_name = f"TD_{cyclone_id}_{storm_name}"
        file_name = f"TD_{cyclone_id}_{storm_name}_{settings.data_time}_{settings.fcst_hours}h.png"
    else:
        dir_name = f"TYP_{cyclone_id}_{storm_name}"
        file_name = f"TYP_{cyclone_id}_{storm_name}_{settings.data_time}_{settings.fcst_hours}h.png"
    return settings.output_root / year_str / dir_name / file_name


def metadata_path_for_settings(settings: Settings) -> Path | None:
    hours = settings.fcst_hours_options or (settings.fcst_hours,)
    if settings.metadata_path and len(hours) == 1:
        return settings.metadata_path

    year_str = storm_year(settings)
    stage = settings.storm_stage.upper()
    storm_prefix = "td" if stage == "TD" else "typ"
    storm_key = f"{storm_prefix}_{year_str}_{settings.typ_number:02d}"
    return settings.output_root / "metadata" / f"{settings.data_time}_{storm_key}_{settings.fcst_hours}h.json"


def render_signature() -> str:
    try:
        return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    except OSError:
        return ""


def next_available_path(path: Path) -> Path:
    if not path.exists():
        return path

    for index in range(1, 10000):
        candidate = path.with_name(f"{path.stem} ({index}){path.suffix}")
        if not candidate.exists():
            return candidate
    raise FileExistsError(f"Could not find an available filename for {path}")


def write_run_metadata(
    path: Path,
    *,
    target: Path,
    df: pd.DataFrame,
    settings: Settings,
    intensity: str,
) -> None:
    model_names = sorted(plotted_model_names(df, settings))
    model_labels = plotted_model_labels(df, settings)
    image_path = target
    try:
        image_path = target.resolve().relative_to(PROJECT_ROOT.resolve())
    except ValueError:
        pass
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S"),
        "render_signature": render_signature(),
        "image_path": image_path.as_posix(),
        "storm_stage": settings.storm_stage,
        "storm_year": storm_year(settings),
        "typ_number": settings.typ_number,
        "data_typ_number": kma_data_typ_number(settings),
        "typ_name": settings.typ_name,
        "typ_name_ko": settings.typ_name_ko,
        "linked_td_number": settings.linked_td_number,
        "linked_typ_number": settings.linked_typ_number,
        "atcf_id": "" if settings.skip_atcf else settings.atcf_id,
        "extra_atcf_ids": [] if settings.skip_atcf else list(settings.extra_atcf_ids),
        "data_time": settings.data_time,
        "fcst_hours": settings.fcst_hours,
        "intensity": intensity,
        "model_count": len(model_names),
        "target_model_count": active_model_target_count(settings),
        "models": model_names,
        "model_labels": model_labels,
        "skip_atcf": settings.skip_atcf,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def relative_image_path(target: Path) -> str:
    image_path = target
    try:
        image_path = target.resolve().relative_to(PROJECT_ROOT.resolve())
    except ValueError:
        pass
    return image_path.as_posix()


def load_previous_metadata(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def write_preserved_output_metadata(
    path: Path,
    *,
    settings: Settings,
    intensity: str,
    reason: str,
    target: Path,
) -> None:
    previous = load_previous_metadata(path)
    previous_model_count = 0
    try:
        previous_model_count = int(previous.get("model_count") or 0)
    except (TypeError, ValueError):
        previous_model_count = 0
    previous_image_path = str(previous.get("image_path") or "")
    previous_render_signature = str(previous.get("render_signature") or "")
    target_image_path = relative_image_path(target)
    preserved_render_signature = (
        previous_render_signature
        if previous_image_path == target_image_path and not previous.get("no_output")
        else ""
    )

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S"),
        "render_signature": preserved_render_signature,
        "image_path": target_image_path,
        "storm_stage": settings.storm_stage,
        "storm_year": storm_year(settings),
        "typ_number": settings.typ_number,
        "data_typ_number": kma_data_typ_number(settings),
        "typ_name": settings.typ_name,
        "typ_name_ko": settings.typ_name_ko,
        "linked_td_number": settings.linked_td_number,
        "linked_typ_number": settings.linked_typ_number,
        "atcf_id": "" if settings.skip_atcf else settings.atcf_id,
        "extra_atcf_ids": [] if settings.skip_atcf else list(settings.extra_atcf_ids),
        "data_time": settings.data_time,
        "fcst_hours": settings.fcst_hours,
        "intensity": intensity,
        "model_count": max(previous_model_count, 1),
        "target_model_count": active_model_target_count(settings),
        "models": previous.get("models") if isinstance(previous.get("models"), list) else [],
        "model_labels": previous.get("model_labels") if isinstance(previous.get("model_labels"), list) else [],
        "skip_atcf": settings.skip_atcf,
        "preserved_existing_image": True,
        "preserve_reason": reason,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_no_output_metadata(
    path: Path,
    *,
    settings: Settings,
    intensity: str,
    reason: str,
) -> None:
    target = output_path(settings)
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S"),
        "render_signature": render_signature(),
        "image_path": relative_image_path(target),
        "storm_stage": settings.storm_stage,
        "storm_year": storm_year(settings),
        "typ_number": settings.typ_number,
        "data_typ_number": kma_data_typ_number(settings),
        "typ_name": settings.typ_name,
        "typ_name_ko": settings.typ_name_ko,
        "linked_td_number": settings.linked_td_number,
        "linked_typ_number": settings.linked_typ_number,
        "atcf_id": "" if settings.skip_atcf else settings.atcf_id,
        "extra_atcf_ids": [] if settings.skip_atcf else list(settings.extra_atcf_ids),
        "data_time": settings.data_time,
        "fcst_hours": settings.fcst_hours,
        "intensity": intensity,
        "model_count": 0,
        "target_model_count": active_model_target_count(settings),
        "models": [],
        "model_labels": [],
        "skip_atcf": settings.skip_atcf,
        "no_output": True,
        "no_output_reason": reason,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def map_extent(settings: Settings, center_lat: float, center_lon: float) -> list[float]:

    west_margin = settings.margin_lon + settings.extra_west_lon
    east_margin = settings.margin_lon + settings.extra_east_lon
    return [
        center_lon - west_margin,
        center_lon + east_margin,
        center_lat - settings.margin_lat / 1.2,
        center_lat + settings.margin_lat / 1.2,
    ]


def numeric_track_points(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["LAT", "LON", "TMD", "FT_TIME"])
    points = df.copy()
    for column in ["LAT", "LON", "TMD"]:
        if column in points:
            points[column] = pd.to_numeric(points[column], errors="coerce")
    return points.dropna(subset=["LAT", "LON"])


def robust_series_bounds(series: pd.Series) -> tuple[float, float]:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return 0.0, 0.0
    if len(clean) >= 10:
        return float(clean.quantile(0.05)), float(clean.quantile(0.95))
    return float(clean.min()), float(clean.max())


def longitude_delta(a: float, b: float) -> float:
    return ((a - b + 180) % 360) - 180


def anchor_lonlat_from_points(points: pd.DataFrame) -> tuple[float, float] | None:
    if points.empty:
        return None

    if "TMD" in points:
        leads = pd.to_numeric(points["TMD"], errors="coerce")
    else:
        leads = pd.Series(float("nan"), index=points.index)
    for subset in [
        points[leads.between(0, 24)].copy(),
        points[leads.between(0, 120)].copy(),
        points.copy(),
    ]:
        if subset.empty:
            continue
        lons = pd.to_numeric(subset["LON"], errors="coerce").dropna()
        lats = pd.to_numeric(subset["LAT"], errors="coerce").dropna()
        if lons.empty or lats.empty:
            continue
        raw_anchor_lon = float(lons.median())
        normalized_lons = lons.map(lambda lon: raw_anchor_lon + longitude_delta(float(lon), raw_anchor_lon))
        return float(normalized_lons.median()), float(lats.median())
    return None


def normalize_240_camera_longitudes(points: pd.DataFrame, settings: Settings) -> pd.DataFrame:
    if settings.fcst_hours <= 120 or points.empty:
        return points

    normalized = numeric_track_points(points)
    if normalized.empty:
        return points

    anchor = anchor_lonlat_from_points(normalized)
    if anchor is None:
        return normalized

    anchor_lon, _ = anchor
    normalized = normalized.copy()
    normalized["LON"] = normalized["LON"].map(lambda lon: anchor_lon + longitude_delta(float(lon), anchor_lon))
    return normalized


def filter_240_camera_points(points: pd.DataFrame, settings: Settings) -> pd.DataFrame:
    if settings.fcst_hours <= 120 or points.empty:
        return points

    camera_points = normalize_240_camera_longitudes(points, settings)
    if camera_points.empty:
        return points

    lat_values = pd.to_numeric(camera_points["LAT"], errors="coerce")
    camera_points = camera_points[lat_values.between(-12.0, 72.0)].copy()
    if camera_points.empty or "TMD" not in camera_points:
        return points

    anchor = anchor_lonlat_from_points(camera_points)
    if anchor is None:
        return camera_points

    anchor_lon, anchor_lat = anchor
    lon_distance = camera_points["LON"].map(lambda lon: abs(longitude_delta(float(lon), anchor_lon)))
    lat_distance = (camera_points["LAT"] - anchor_lat).abs()
    filtered = camera_points[
        lon_distance.le(MAX_CAMERA_240_LON_DISTANCE)
        & lat_distance.le(MAX_CAMERA_240_LAT_DISTANCE)
    ].copy()

    min_rows = max(5, math.ceil(len(camera_points) * 0.55))
    if len(filtered) < min_rows:
        raw_lon_span = float(camera_points["LON"].max() - camera_points["LON"].min())
        raw_lat_span = float(camera_points["LAT"].max() - camera_points["LAT"].min())
        if len(filtered) >= 5 and (
            raw_lon_span > MAX_DISPLAY_240_LON_SPAN or raw_lat_span > MAX_DISPLAY_240_LAT_SPAN
        ):
            print(
                "240h map extent kept distant-point filter despite sparse retention "
                f"({len(filtered)}/{len(camera_points)} points, "
                f"{raw_lon_span:.1f} lon x {raw_lat_span:.1f} lat raw span)."
            )
            return filtered
        return camera_points

    removed_count = len(camera_points) - len(filtered)
    if removed_count:
        print(f"240h map extent ignored {removed_count} distant camera point(s).")
    return filtered


def extent_points_for_auto_map(df: pd.DataFrame, settings: Settings) -> pd.DataFrame:
    points = numeric_track_points(df)
    if points.empty:
        return points

    if settings.fcst_hours <= 120:
        return points

    points = normalize_240_camera_longitudes(points, settings)
    points = points[pd.to_numeric(points["LAT"], errors="coerce").between(-8, 68)].copy()
    if points.empty or "SRC" not in points:
        return filter_240_camera_points(points, settings)

    centers = (
        points[points["SRC"].ne("KMA")]
        .groupby("SRC", dropna=True)[["LAT", "LON"]]
        .median(numeric_only=True)
        .dropna()
    )
    if len(centers) < 4:
        return filter_240_camera_points(points, settings)

    center_lat = float(centers["LAT"].median())
    center_lon = float(centers["LON"].median())
    keep_models = set()
    for model_name, row in centers.iterrows():
        lon_distance = abs(longitude_delta(float(row["LON"]), center_lon))
        lat_distance = abs(float(row["LAT"]) - center_lat)
        if lon_distance <= 38 and lat_distance <= 24:
            keep_models.add(model_name)

    if len(keep_models) < max(3, math.ceil(len(centers) * 0.45)):
        return filter_240_camera_points(points, settings)

    keep_mask = points["SRC"].eq("KMA") | points["SRC"].isin(keep_models)
    filtered = points[keep_mask].copy()
    removed_models = sorted(set(centers.index) - keep_models)
    if removed_models:
        print(
            "240h map extent ignored distant model cluster(s): "
            + ", ".join(str(name) for name in removed_models)
        )
    return filter_240_camera_points(filtered if not filtered.empty else points, settings)


def robust_bounds(points: pd.DataFrame, column: str, settings: Settings) -> tuple[float, float]:
    clean = pd.to_numeric(points[column], errors="coerce").dropna()
    if clean.empty:
        return 0.0, 0.0
    if settings.fcst_hours > 120 and len(clean) >= 10:
        return float(clean.quantile(0.06)), float(clean.quantile(0.94))
    return robust_series_bounds(clean)


def lead_filtered_points(points: pd.DataFrame, min_hour: float, max_hour: float) -> pd.DataFrame:
    leads = pd.to_numeric(points["TMD"], errors="coerce")
    return points[leads.between(min_hour, max_hour)].copy()


def latest_points_by_source(points: pd.DataFrame, min_hour: float, max_hour: float) -> pd.DataFrame:
    if points.empty or "SRC" not in points:
        return pd.DataFrame(columns=points.columns)
    subset = lead_filtered_points(points, min_hour, max_hour)
    if subset.empty:
        return subset
    subset["TMD"] = pd.to_numeric(subset["TMD"], errors="coerce")
    return subset.dropna(subset=["TMD"]).sort_values("TMD").groupby("SRC", dropna=True).tail(1)


def closest_points_by_source(points: pd.DataFrame, target_hour: float, tolerance: float = 36.0) -> pd.DataFrame:
    if points.empty or "SRC" not in points:
        return pd.DataFrame(columns=points.columns)
    subset = points.copy()
    subset["TMD"] = pd.to_numeric(subset["TMD"], errors="coerce")
    subset = subset.dropna(subset=["TMD"])
    if subset.empty:
        return subset
    subset["_lead_error"] = (subset["TMD"] - target_hour).abs()
    subset = subset[subset["_lead_error"].le(tolerance)]
    if subset.empty:
        return subset.drop(columns=["_lead_error"], errors="ignore")
    closest = subset.sort_values(["SRC", "_lead_error", "TMD"]).groupby("SRC", dropna=True).head(1)
    return closest.drop(columns=["_lead_error"], errors="ignore")


def bounds_from_frames(frames: list[pd.DataFrame], settings: Settings) -> tuple[float, float, float, float] | None:
    available = [frame for frame in frames if frame is not None and not frame.empty]
    if not available:
        return None
    merged = pd.concat(available, ignore_index=True)
    if merged.empty:
        return None
    lat_min, lat_max = robust_bounds(merged, "LAT", settings)
    lon_min, lon_max = robust_bounds(merged, "LON", settings)
    return lon_min, lon_max, lat_min, lat_max


def expand_bounds_with_frame(
    bounds: tuple[float, float, float, float],
    frame: pd.DataFrame,
    *,
    exact: bool = False,
) -> tuple[float, float, float, float]:
    if frame.empty:
        return bounds
    lons = pd.to_numeric(frame["LON"], errors="coerce").dropna()
    lats = pd.to_numeric(frame["LAT"], errors="coerce").dropna()
    if lons.empty or lats.empty:
        return bounds
    lon_min, lon_max, lat_min, lat_max = bounds
    if exact or len(frame) < 10:
        return (
            min(lon_min, float(lons.min())),
            max(lon_max, float(lons.max())),
            min(lat_min, float(lats.min())),
            max(lat_max, float(lats.max())),
        )
    return (
        min(lon_min, float(lons.quantile(0.08))),
        max(lon_max, float(lons.quantile(0.92))),
        min(lat_min, float(lats.quantile(0.08))),
        max(lat_max, float(lats.quantile(0.92))),
    )


def mean_point_frame(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=frame.columns)
    lons = pd.to_numeric(frame["LON"], errors="coerce").dropna()
    lats = pd.to_numeric(frame["LAT"], errors="coerce").dropna()
    if lons.empty or lats.empty:
        return pd.DataFrame(columns=frame.columns)
    return pd.DataFrame({"LAT": [float(lats.mean())], "LON": [float(lons.mean())]})


def quantile_frame_bounds(
    frame: pd.DataFrame,
    *,
    lon_low: float = 0.05,
    lon_high: float = 0.95,
    lat_low: float = 0.05,
    lat_high: float = 0.95,
) -> tuple[float, float, float, float] | None:
    if frame.empty:
        return None
    lons = pd.to_numeric(frame["LON"], errors="coerce").dropna()
    lats = pd.to_numeric(frame["LAT"], errors="coerce").dropna()
    if lons.empty or lats.empty:
        return None
    if len(lons) < 4:
        lon_min = float(lons.min())
        lon_max = float(lons.max())
    else:
        lon_min = float(lons.quantile(lon_low))
        lon_max = float(lons.quantile(lon_high))
    if len(lats) < 4:
        lat_min = float(lats.min())
        lat_max = float(lats.max())
    else:
        lat_min = float(lats.quantile(lat_low))
        lat_max = float(lats.quantile(lat_high))
    return lon_min, lon_max, lat_min, lat_max


def expand_extent_for_screen_bounds(
    extent: list[float],
    bounds: tuple[float, float, float, float],
    *,
    left: float,
    right: float,
    bottom: float,
    top: float,
) -> list[float]:
    lon_min, lon_max, lat_min, lat_max = extent
    data_west, data_east, data_south, data_north = bounds

    for _ in range(2):
        lon_span = lon_max - lon_min
        lat_span = lat_max - lat_min
        if lon_span <= 0 or lat_span <= 0:
            return [lon_min, lon_max, lat_min, lat_max]

        west_x = (data_west - lon_min) / lon_span
        east_x = (data_east - lon_min) / lon_span
        south_y = (data_south - lat_min) / lat_span
        north_y = (data_north - lat_min) / lat_span

        if west_x < left:
            lon_min = (data_west - left * lon_max) / (1.0 - left)
        if east_x > right:
            lon_max = (data_east - right * lon_min) / (1.0 - right)
        if south_y < bottom:
            lat_min = (data_south - bottom * lat_max) / (1.0 - bottom)
        if north_y > top:
            lat_max = (data_north - top * lat_min) / (1.0 - top)

    return [lon_min, lon_max, lat_min, lat_max]


def _mercator_extent_xy(extent: list[float]) -> tuple[float, float, float, float] | None:
    projection = ccrs.Mercator()
    data_crs = ccrs.PlateCarree()
    lon_min, lon_max, lat_min, lat_max = extent
    center_lon = (lon_min + lon_max) / 2
    center_lat = (lat_min + lat_max) / 2

    x0, _ = projection.transform_point(lon_min, center_lat, data_crs)
    x1, _ = projection.transform_point(lon_max, center_lat, data_crs)
    _, y0 = projection.transform_point(center_lon, lat_min, data_crs)
    _, y1 = projection.transform_point(center_lon, lat_max, data_crs)
    if not all(math.isfinite(value) for value in [x0, x1, y0, y1]):
        return None
    if x1 <= x0 or y1 <= y0:
        return None
    return x0, x1, y0, y1


def _extent_from_mercator_xy(
    x0: float,
    x1: float,
    y0: float,
    y1: float,
    reference_extent: list[float],
) -> list[float]:
    projection = ccrs.Mercator()
    data_crs = ccrs.PlateCarree()
    lon_min, lon_max, lat_min, lat_max = reference_extent
    center_x = (x0 + x1) / 2
    center_y = (y0 + y1) / 2

    new_lon_min, _ = data_crs.transform_point(x0, center_y, projection)
    new_lon_max, _ = data_crs.transform_point(x1, center_y, projection)
    _, new_lat_min = data_crs.transform_point(center_x, y0, projection)
    _, new_lat_max = data_crs.transform_point(center_x, y1, projection)

    result = [new_lon_min, new_lon_max, new_lat_min, new_lat_max]
    if not all(math.isfinite(value) for value in result):
        return [lon_min, lon_max, lat_min, lat_max]
    if new_lon_max <= new_lon_min or new_lat_max <= new_lat_min:
        return [lon_min, lon_max, lat_min, lat_max]
    return result


def extent_from_screen_bounds(
    bounds: tuple[float, float, float, float],
    *,
    left: float,
    right: float,
    bottom: float,
    top: float,
) -> list[float] | None:
    data_west, data_east, data_south, data_north = bounds
    x_span = max(right - left, 0.10)
    y_span = max(top - bottom, 0.10)
    data_lon_span = max(data_east - data_west, 1.0)
    data_lat_span = max(data_north - data_south, 1.0)

    lon_span = data_lon_span / x_span
    lat_span = data_lat_span / y_span
    lon_min = data_west - left * lon_span
    lat_min = data_south - bottom * lat_span
    return [lon_min, lon_min + lon_span, lat_min, lat_min + lat_span]


def expand_extent_to_min_span(
    extent: list[float],
    *,
    min_lon_span: float,
    min_lat_span: float,
    east_ratio: float = 0.64,
    north_ratio: float = 0.56,
) -> list[float]:
    lon_min, lon_max, lat_min, lat_max = extent
    lon_span = lon_max - lon_min
    if lon_span < min_lon_span:
        extra = min_lon_span - lon_span
        lon_min -= extra * (1.0 - east_ratio)
        lon_max += extra * east_ratio

    lat_span = lat_max - lat_min
    if lat_span < min_lat_span:
        extra = min_lat_span - lat_span
        lat_min -= extra * (1.0 - north_ratio)
        lat_max += extra * north_ratio

    return [lon_min, lon_max, lat_min, lat_max]


def concat_track_frames(frames: list[pd.DataFrame]) -> pd.DataFrame:
    available = [frame for frame in frames if frame is not None and not frame.empty]
    if not available:
        return pd.DataFrame()
    return pd.concat(available, ignore_index=True)


def build_240_camera_frames(points: pd.DataFrame, settings: Settings) -> dict[str, pd.DataFrame]:
    full = lead_filtered_points(points, 0, settings.fcst_hours)
    early = lead_filtered_points(points, 0, 120)
    late = lead_filtered_points(points, 120, settings.fcst_hours)
    starts = lead_filtered_points(points, 0, 0)
    mid = closest_points_by_source(points, 120, tolerance=42.0)
    late_180 = closest_points_by_source(points, 180, tolerance=48.0)
    late_240 = closest_points_by_source(points, min(settings.fcst_hours, 240), tolerance=54.0)
    endpoints = latest_points_by_source(points, 120, settings.fcst_hours)
    if len(endpoints) < 3:
        endpoints = latest_points_by_source(points, 0, settings.fcst_hours)

    endpoint_cluster = concat_track_frames([late_180, late_240, endpoints])
    return {
        "full": full,
        "early": early,
        "late": late,
        "starts": starts,
        "mid": mid,
        "late_180": late_180,
        "late_240": late_240,
        "endpoints": endpoints,
        "start_mean": mean_point_frame(starts),
        "mid_mean": mean_point_frame(mid),
        "endpoint_mean": mean_point_frame(endpoints),
        "late_mean": mean_point_frame(endpoint_cluster),
    }


def auto_map_extent_long_range_seed(points: pd.DataFrame, past_kma: pd.DataFrame, settings: Settings) -> list[float] | None:
    frames = build_240_camera_frames(points, settings)
    if frames["full"].empty:
        return None

    seed_frame = concat_track_frames([
        frames["full"],
        frames["mid"],
        frames["late_180"],
        frames["late_240"],
        frames["endpoints"],
        frames["start_mean"],
        frames["mid_mean"],
        frames["endpoint_mean"],
        frames["late_mean"],
    ])
    bounds = quantile_frame_bounds(seed_frame, lon_low=0.030, lon_high=0.970, lat_low=0.030, lat_high=0.975)
    if bounds is None:
        bounds = bounds_from_frames([frames["full"]], settings)
    if bounds is None:
        return None

    if not past_kma.empty:
        current_dt = pd.to_datetime(settings.data_time, format="%Y%m%d%H%M", errors="coerce")
        past_points = past_kma.copy()
        if "FT_TIME" in past_points and not pd.isna(current_dt):
            cutoff = current_dt.to_pydatetime() - timedelta(hours=72)
            past_points = past_points[past_points["FT_TIME"].ge(cutoff)].copy()
        past_points = numeric_track_points(past_points)
        if not past_points.empty:
            past_points = normalize_240_camera_longitudes(past_points, settings)
            bounds = expand_bounds_with_frame(bounds, past_points, exact=False)

    extent = extent_from_screen_bounds(
        bounds,
        left=0.045,
        right=0.690,
        bottom=0.055,
        top=0.860,
    )
    if extent is None:
        lon_min, lon_max, lat_min, lat_max = bounds
        extent = [lon_min, lon_max, lat_min, lat_max]
    extent = expand_extent_to_min_span(
        extent,
        min_lon_span=MIN_STABLE_240_LON_SPAN,
        min_lat_span=MIN_STABLE_240_LAT_SPAN,
        east_ratio=0.56,
        north_ratio=0.58,
    )
    return clamp_west_pacific_extent(extent)


def auto_map_extent(df: pd.DataFrame, past_kma: pd.DataFrame, settings: Settings) -> list[float] | None:
    points = extent_points_for_auto_map(df, settings)
    if points.empty:
        return None

    if settings.fcst_hours > 120:
        return auto_map_extent_long_range_seed(points, past_kma, settings)

    lead_hours = pd.to_numeric(points["TMD"], errors="coerce")
    primary = points[lead_hours.between(0, settings.fcst_hours)].copy()
    if primary.empty:
        primary = points.copy()

    lat_min, lat_max = robust_bounds(primary, "LAT", settings)
    lon_min, lon_max = robust_bounds(primary, "LON", settings)
    lat_span = max(lat_max - lat_min, 7.5 if settings.fcst_hours <= 120 else 10.0)
    lon_span = max(lon_max - lon_min, 10.0 if settings.fcst_hours <= 120 else 14.0)

    focus_lat = (lat_min + lat_max) / 2
    focus_lon = (lon_min + lon_max) / 2
    lon_total = max(24.0, lon_span * 1.45 + 7.0)
    lat_total = max(10.5, lat_span * 1.55 + 4.5)
    focus_x = 0.37
    focus_y = 0.37

    lon_min = focus_lon - lon_total * focus_x
    lon_max = lon_min + lon_total
    lat_min = focus_lat - lat_total * focus_y
    lat_max = lat_min + lat_total

    return [
        lon_min,
        lon_max,
        lat_min,
        lat_max,
    ]


def reasonable_display_240_extent(extent: list[float]) -> bool:
    lon_span = extent[1] - extent[0]
    lat_span = extent[3] - extent[2]
    return (
        lon_span > 0
        and lat_span > 0
        and lon_span <= MAX_DISPLAY_240_LON_SPAN
        and lat_span <= MAX_DISPLAY_240_LAT_SPAN
        and extent[0] >= MIN_DISPLAY_240_WEST_LON
        and extent[1] <= MAX_DISPLAY_240_EAST_LON
        and extent[2] >= MIN_DISPLAY_240_SOUTH_LAT
        and extent[3] <= MAX_DISPLAY_240_NORTH_LAT
    )


def broad_display_240_extent(extent: list[float]) -> bool:
    lon_span = extent[1] - extent[0]
    lat_span = extent[3] - extent[2]
    return (
        lon_span > MAX_STABLE_240_LON_SPAN
        or lat_span > MAX_STABLE_240_LAT_SPAN
        or (extent[0] <= MIN_DISPLAY_240_WEST_LON + 0.1 and extent[1] >= MAX_DISPLAY_240_EAST_LON - 0.1)
    )


def expanded_120_anchor_for_240(df: pd.DataFrame, past_kma: pd.DataFrame, settings: Settings) -> list[float] | None:
    anchor_settings = replace(settings, fcst_hours=120, fcst_hours_options=(120,))
    anchor_df = limit_forecast_hours(df, anchor_settings)
    anchor_extent = auto_map_extent(anchor_df, past_kma, anchor_settings)
    if anchor_extent is None:
        return None

    lon_span = max(anchor_extent[1] - anchor_extent[0], 24.0)
    lat_span = max(anchor_extent[3] - anchor_extent[2], 12.0)
    return [
        anchor_extent[0] - lon_span * 0.18,
        anchor_extent[1] + lon_span * 0.48,
        anchor_extent[2] - lat_span * 0.22,
        anchor_extent[3] + lat_span * 0.38,
    ]


def clamp_west_pacific_extent(
    extent: list[float],
    *,
    min_west_lon: float = MIN_DISPLAY_240_WEST_LON,
    max_east_lon: float = MAX_DISPLAY_240_EAST_LON,
) -> list[float]:

    lon_min, lon_max, lat_min, lat_max = extent
    if lon_max <= lon_min or lat_max <= lat_min:
        return extent

    max_lon_span = max_east_lon - min_west_lon
    lon_span = lon_max - lon_min
    if lon_span >= max_lon_span:
        lon_min = min_west_lon
        lon_max = max_east_lon
    else:
        if lon_max > max_east_lon:
            shift = lon_max - max_east_lon
            lon_min -= shift
            lon_max -= shift
        if lon_min < min_west_lon:
            shift = min_west_lon - lon_min
            lon_min += shift
            lon_max += shift

    return [float(lon_min), float(lon_max), float(lat_min), float(lat_max)]


def clamp_240_display_extent(extent: list[float]) -> list[float]:
    lon_min, lon_max, lat_min, lat_max = clamp_west_pacific_extent(extent)
    if lon_max <= lon_min or lat_max <= lat_min:
        return extent

    lon_span = lon_max - lon_min
    max_lon_span = min(MAX_DISPLAY_240_LON_SPAN, MAX_DISPLAY_240_EAST_LON - MIN_DISPLAY_240_WEST_LON)
    if lon_span > max_lon_span:
        center_lon = (lon_min + lon_max) / 2
        lon_min = center_lon - max_lon_span / 2
        lon_max = center_lon + max_lon_span / 2
        lon_min, lon_max, lat_min, lat_max = clamp_west_pacific_extent([lon_min, lon_max, lat_min, lat_max])

    lat_span = lat_max - lat_min
    max_lat_span = min(MAX_DISPLAY_240_LAT_SPAN, MAX_DISPLAY_240_NORTH_LAT - MIN_DISPLAY_240_SOUTH_LAT)
    if lat_span > max_lat_span:
        center_lat = (lat_min + lat_max) / 2
        lat_min = center_lat - max_lat_span / 2
        lat_max = center_lat + max_lat_span / 2

    if lat_max > MAX_DISPLAY_240_NORTH_LAT:
        shift = lat_max - MAX_DISPLAY_240_NORTH_LAT
        lat_min -= shift
        lat_max -= shift
    if lat_min < MIN_DISPLAY_240_SOUTH_LAT:
        shift = MIN_DISPLAY_240_SOUTH_LAT - lat_min
        lat_min += shift
        lat_max += shift

    if lat_max > MAX_DISPLAY_240_NORTH_LAT:
        lat_max = MAX_DISPLAY_240_NORTH_LAT
    if lat_min < MIN_DISPLAY_240_SOUTH_LAT:
        lat_min = MIN_DISPLAY_240_SOUTH_LAT

    return [float(lon_min), float(lon_max), float(lat_min), float(lat_max)]



def current_point_legend_safe_extent(df: pd.DataFrame, extent: list[float], settings: Settings) -> list[float]:
    """Lightweight fallback for manually supplied 240h extents.

    The auto-extent path no longer uses this as a hard post-processor.  It only
    nudges a manual/fallback extent when the current analyzed point is buried
    under the legend area.
    """
    if settings.fcst_hours != 240:
        return extent
    start = df[(df["SRC"] == "KMA") & (pd.to_numeric(df["TMD"], errors="coerce") == 0)].head(1)
    if start.empty:
        return extent
    lon_values = pd.to_numeric(start["LON"], errors="coerce").dropna()
    if lon_values.empty:
        return extent

    lon = float(lon_values.iloc[0])
    lon_min, lon_max, lat_min, lat_max = extent
    lon_span = lon_max - lon_min
    if lon_span <= 0:
        return extent

    current_x = (lon - lon_min) / lon_span
    safe_x = 0.640
    if current_x <= safe_x:
        return extent

    shift = (current_x - safe_x) * lon_span * 0.55
    return [lon_min + shift, lon_max + shift, lat_min, lat_max]


def legend_row_count_for(df: pd.DataFrame, settings: Settings) -> int:
    excluded = excluded_models_for(df)
    active = active_model_names(settings)
    return len([model for model in MODEL_INFO if model["name"] in active and model["name"] not in excluded])




def fixed_240_map_extent(settings: Settings) -> list[float]:
    """Stable 240h West-Pacific view used instead of dynamic 240h camera fitting."""
    return list(FIXED_240_MAP_EXTENT)


def legend_box_for_side(
    row_count: int,
    side: str = "right",
    *,
    padded: bool = False,
) -> tuple[float, float, float, float]:
    """Legend box in axes-fraction coordinates.

    This mirrors draw_model_legend_table().  Do not reference the actual
    legend row list here because this function is also used before the legend
    rows are built, when deciding whether the legend should move left.
    """
    row_count = max(1, int(row_count))
    width = 0.325
    y0 = 0.005
    pad_y = 0.005
    row_h = 0.019

    if side == "left":
        x0, x1 = 0.005, 0.005 + width
    else:
        x0, x1 = 0.670, 0.995

    y1 = y0 + pad_y * 2 + row_h * row_count

    if not padded:
        return x0, x1, y0, y1

    return (
        max(0.0, x0 - 0.014),
        min(1.0, x1 + 0.010),
        0.000,
        min(0.900, y1 + 0.020),
    )


def track_points_for_legend_collision(df: pd.DataFrame, settings: Settings) -> pd.DataFrame:
    points = numeric_track_points(df)
    if points.empty:
        return points
    if "TMD" in points:
        leads = pd.to_numeric(points["TMD"], errors="coerce")
        points = points[leads.between(0, settings.fcst_hours)].copy()
    return points.dropna(subset=["LAT", "LON"])


def legend_collision_score(
    df: pd.DataFrame,
    settings: Settings,
    extent: list[float],
    *,
    side: str,
) -> tuple[float, int, int]:
    row_count = legend_row_count_for(df, settings)
    box = legend_box_for_side(row_count, side, padded=True)
    points = track_points_for_legend_collision(df, settings)
    if points.empty:
        return 0.0, 0, 0
    fractions = point_screen_fractions(extent, points)
    segments = track_screen_segments(extent, points)
    point_hits = count_points_in_box(fractions, box, padding=0.002)
    segment_hits = count_segments_in_box(segments, box, padding=0.004)
    return float(point_hits + segment_hits * 4), point_hits, segment_hits


def choose_legend_side_for_map(df: pd.DataFrame, settings: Settings, extent: list[float]) -> str:
    """Choose legend side for 240h fixed map using point/segment obstacle hits."""
    if settings.fcst_hours != 240:
        return "right"
    right_score, right_points, right_segments = legend_collision_score(df, settings, extent, side="right")
    left_score, left_points, left_segments = legend_collision_score(df, settings, extent, side="left")
    if right_score >= 8.0 and left_score + 2.0 < right_score:
        print(
            "240h legend moved left "
            f"(right obstacle score={right_score:.1f}, points={right_points}, segments={right_segments}; "
            f"left score={left_score:.1f}, points={left_points}, segments={left_segments})."
        )
        return "left"
    print(
        "240h legend kept right "
        f"(right obstacle score={right_score:.1f}, points={right_points}, segments={right_segments}; "
        f"left score={left_score:.1f}, points={left_points}, segments={left_segments})."
    )
    return "right"

def overlay_obstacle_boxes_240(df: pd.DataFrame, settings: Settings) -> dict[str, tuple[float, float, float, float]]:
    """Return map-overlay boxes in axes-fraction coordinates.

    Values mirror draw_header() and draw_model_legend_table().  The scoring
    camera treats these as soft obstacles instead of shrinking the whole usable
    map into one hard rectangle.
    """
    row_count = max(1, legend_row_count_for(df, settings))
    legend_x0, legend_x1 = 0.670, 0.995
    legend_y0 = 0.005
    legend_y1 = legend_y0 + 0.005 * 2 + 0.019 * row_count
    return {
        "header": (0.000, 1.000, 0.905, 1.000),
        "legend": (max(0.0, legend_x0 - 0.012), min(1.0, legend_x1 + 0.006), 0.000, min(0.900, legend_y1 + 0.018)),
        "credit": (0.000, 0.280, 0.000, 0.052),
    }


def normalize_240_render_points(df: pd.DataFrame, settings: Settings) -> pd.DataFrame:
    points = numeric_track_points(df)
    if points.empty:
        return points
    points = normalize_240_camera_longitudes(points, settings)
    if "TMD" in points:
        leads = pd.to_numeric(points["TMD"], errors="coerce")
        points = points[leads.between(0, settings.fcst_hours)].copy()
    lats = pd.to_numeric(points["LAT"], errors="coerce")
    points = points[lats.between(MIN_DISPLAY_240_SOUTH_LAT - 4.0, MAX_DISPLAY_240_NORTH_LAT + 4.0)].copy()
    return points.dropna(subset=["LAT", "LON"])


def protected_240_points(
    df: pd.DataFrame,
    camera_points: pd.DataFrame,
    render_points: pd.DataFrame,
    past_kma: pd.DataFrame,
    settings: Settings,
) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    if not camera_points.empty:
        frames.append(camera_points)
    if not render_points.empty:
        render_frames = build_240_camera_frames(render_points, settings)
        frames.extend([
            render_frames["starts"],
            render_frames["mid"],
            render_frames["late_180"],
            render_frames["late_240"],
            render_frames["endpoints"],
            render_frames["start_mean"],
            render_frames["mid_mean"],
            render_frames["endpoint_mean"],
            render_frames["late_mean"],
        ])
    if not past_kma.empty:
        past_points = past_kma.copy()
        current_dt = pd.to_datetime(settings.data_time, format="%Y%m%d%H%M", errors="coerce")
        if "FT_TIME" in past_points and not pd.isna(current_dt):
            cutoff = current_dt.to_pydatetime() - timedelta(hours=72)
            past_points = past_points[past_points["FT_TIME"].ge(cutoff)].copy()
        past_points = normalize_240_camera_longitudes(numeric_track_points(past_points), settings)
        if not past_points.empty:
            frames.append(past_points)
    protected = concat_track_frames(frames)
    if protected.empty:
        return render_points
    return protected.dropna(subset=["LAT", "LON"])


def point_screen_fractions(extent: list[float], points: pd.DataFrame) -> list[tuple[float, float]]:
    if points.empty:
        return []
    extent_xy = _mercator_extent_xy(extent)
    if extent_xy is None:
        return []
    x0, x1, y0, y1 = extent_xy
    x_span = x1 - x0
    y_span = y1 - y0
    if x_span <= 0 or y_span <= 0:
        return []

    projection = ccrs.Mercator()
    data_crs = ccrs.PlateCarree()
    fractions: list[tuple[float, float]] = []
    for lon, lat in zip(points["LON"], points["LAT"]):
        try:
            x, y = projection.transform_point(float(lon), float(lat), data_crs)
        except (TypeError, ValueError):
            continue
        if math.isfinite(x) and math.isfinite(y):
            fractions.append(((x - x0) / x_span, (y - y0) / y_span))
    return fractions


def count_points_outside_screen(fractions: list[tuple[float, float]], *, margin: float = 0.0) -> int:
    return sum(
        1
        for x, y in fractions
        if x < -margin or x > 1.0 + margin or y < -margin or y > 1.0 + margin
    )


def count_points_in_box(
    fractions: list[tuple[float, float]],
    box: tuple[float, float, float, float],
    *,
    padding: float = 0.0,
) -> int:
    x0, x1, y0, y1 = box
    return sum(
        1
        for x, y in fractions
        if x0 - padding <= x <= x1 + padding and y0 - padding <= y <= y1 + padding
    )




def box_contains_point(
    x: float,
    y: float,
    box: tuple[float, float, float, float],
    *,
    padding: float = 0.0,
) -> bool:
    x0, x1, y0, y1 = box
    return x0 - padding <= x <= x1 + padding and y0 - padding <= y <= y1 + padding


def _orientation(ax: float, ay: float, bx: float, by: float, cx: float, cy: float) -> float:
    return (by - ay) * (cx - bx) - (bx - ax) * (cy - by)


def _on_segment(ax: float, ay: float, bx: float, by: float, cx: float, cy: float) -> bool:
    return min(ax, cx) - 1e-12 <= bx <= max(ax, cx) + 1e-12 and min(ay, cy) - 1e-12 <= by <= max(ay, cy) + 1e-12


def screen_segments_intersect(
    a: tuple[float, float],
    b: tuple[float, float],
    c: tuple[float, float],
    d: tuple[float, float],
) -> bool:
    ax, ay = a
    bx, by = b
    cx, cy = c
    dx, dy = d
    o1 = _orientation(ax, ay, bx, by, cx, cy)
    o2 = _orientation(ax, ay, bx, by, dx, dy)
    o3 = _orientation(cx, cy, dx, dy, ax, ay)
    o4 = _orientation(cx, cy, dx, dy, bx, by)

    if o1 * o2 < 0 and o3 * o4 < 0:
        return True
    if abs(o1) < 1e-12 and _on_segment(ax, ay, cx, cy, bx, by):
        return True
    if abs(o2) < 1e-12 and _on_segment(ax, ay, dx, dy, bx, by):
        return True
    if abs(o3) < 1e-12 and _on_segment(cx, cy, ax, ay, dx, dy):
        return True
    if abs(o4) < 1e-12 and _on_segment(cx, cy, bx, by, dx, dy):
        return True
    return False


def screen_segment_intersects_box(
    segment: tuple[float, float, float, float],
    box: tuple[float, float, float, float],
    *,
    padding: float = 0.0,
) -> bool:
    x0, y0, x1, y1 = segment
    bx0, bx1, by0, by1 = box
    bx0 -= padding
    bx1 += padding
    by0 -= padding
    by1 += padding
    padded_box = (bx0, bx1, by0, by1)

    if box_contains_point(x0, y0, padded_box) or box_contains_point(x1, y1, padded_box):
        return True

    # Quick reject by bounding boxes.
    if max(x0, x1) < bx0 or min(x0, x1) > bx1 or max(y0, y1) < by0 or min(y0, y1) > by1:
        return False

    corners = [(bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1)]
    edges = list(zip(corners, corners[1:] + corners[:1]))
    return any(screen_segments_intersect((x0, y0), (x1, y1), a, b) for a, b in edges)


def track_screen_segments(extent: list[float], points: pd.DataFrame) -> list[tuple[float, float, float, float]]:
    if points.empty:
        return []
    extent_xy = _mercator_extent_xy(extent)
    if extent_xy is None:
        return []
    ex0, ex1, ey0, ey1 = extent_xy
    x_span = ex1 - ex0
    y_span = ey1 - ey0
    if x_span <= 0 or y_span <= 0:
        return []

    projection = ccrs.Mercator()
    data_crs = ccrs.PlateCarree()
    frame = points.dropna(subset=["LON", "LAT"]).copy()
    if frame.empty:
        return []

    source_col = "SRC" if "SRC" in frame.columns else ("MODEL" if "MODEL" in frame.columns else None)
    order_cols = [col for col in ("TMD", "FTM", "FT_TIME") if col in frame.columns]
    if not order_cols:
        order_cols = ["LON", "LAT"]

    segments: list[tuple[float, float, float, float]] = []
    groups = frame.groupby(source_col, sort=False) if source_col else [("__all__", frame)]
    for _, group in groups:
        group = group.sort_values(order_cols)
        previous: tuple[float, float] | None = None
        for lon, lat in zip(group["LON"], group["LAT"]):
            try:
                x, y = projection.transform_point(float(lon), float(lat), data_crs)
            except (TypeError, ValueError):
                previous = None
                continue
            if not (math.isfinite(x) and math.isfinite(y)):
                previous = None
                continue
            current = ((x - ex0) / x_span, (y - ey0) / y_span)
            if previous is not None:
                segments.append((previous[0], previous[1], current[0], current[1]))
            previous = current
    return segments


def count_segments_in_box(
    segments: list[tuple[float, float, float, float]],
    box: tuple[float, float, float, float],
    *,
    padding: float = 0.0,
) -> int:
    return sum(1 for segment in segments if screen_segment_intersects_box(segment, box, padding=padding))


def weighted_screen_centroid(
    weighted_fraction_sets: list[tuple[list[tuple[float, float]], float]],
) -> tuple[float, float] | None:
    total_weight = 0.0
    sx = 0.0
    sy = 0.0
    for fractions, weight in weighted_fraction_sets:
        for x, y in fractions:
            if math.isfinite(x) and math.isfinite(y):
                sx += x * weight
                sy += y * weight
                total_weight += weight
    if total_weight <= 0:
        return None
    return sx / total_weight, sy / total_weight

def screen_bounds_from_fractions(fractions: list[tuple[float, float]]) -> tuple[float, float, float, float] | None:
    if not fractions:
        return None
    xs = [item[0] for item in fractions if math.isfinite(item[0])]
    ys = [item[1] for item in fractions if math.isfinite(item[1])]
    if not xs or not ys:
        return None
    return min(xs), max(xs), min(ys), max(ys)


def quantile_bounds_for_frame(
    frame: pd.DataFrame,
    settings: Settings,
    *,
    lon_low: float = 0.02,
    lon_high: float = 0.98,
    lat_low: float = 0.02,
    lat_high: float = 0.98,
    exact_when_small: int = 6,
) -> tuple[float, float, float, float] | None:
    if frame.empty:
        return None
    lons = pd.to_numeric(frame["LON"], errors="coerce").dropna()
    lats = pd.to_numeric(frame["LAT"], errors="coerce").dropna()
    if lons.empty or lats.empty:
        return None
    if len(frame) <= exact_when_small:
        return float(lons.min()), float(lons.max()), float(lats.min()), float(lats.max())
    return (
        float(lons.quantile(lon_low)),
        float(lons.quantile(lon_high)),
        float(lats.quantile(lat_low)),
        float(lats.quantile(lat_high)),
    )


def candidate_extent_from_240_bounds(
    bounds: tuple[float, float, float, float] | None,
    settings: Settings,
    *,
    left: float,
    right: float,
    bottom: float,
    top: float,
    fig_width: float,
    fig_height: float,
    min_lon_span: float = 42.0,
    min_lat_span: float = 26.0,
) -> list[float] | None:
    if bounds is None:
        return None
    extent = extent_from_screen_bounds(bounds, left=left, right=right, bottom=bottom, top=top)
    if extent is None:
        lon_min, lon_max, lat_min, lat_max = bounds
        extent = [lon_min, lon_max, lat_min, lat_max]
    extent = expand_extent_to_min_span(
        extent,
        min_lon_span=min_lon_span,
        min_lat_span=min_lat_span,
        east_ratio=0.58,
        north_ratio=0.56,
    )
    return normalize_240_candidate_extent(extent, settings, fig_width=fig_width, fig_height=fig_height)


def normalize_240_candidate_extent(
    extent: list[float] | None,
    settings: Settings,
    *,
    fig_width: float,
    fig_height: float,
) -> list[float] | None:
    if extent is None or len(extent) != 4:
        return None
    if extent[1] <= extent[0] or extent[3] <= extent[2]:
        return None
    candidate = aspect_match_and_clamp_extent(extent, settings, fig_width=fig_width, fig_height=fig_height)
    candidate = clamp_240_display_extent(candidate)
    if candidate[1] <= candidate[0] or candidate[3] <= candidate[2]:
        return None
    return [float(value) for value in candidate]


def scale_shift_240_extent(
    extent: list[float],
    settings: Settings,
    *,
    scale: float,
    shift_x: float,
    shift_y: float,
    fig_width: float,
    fig_height: float,
) -> list[float] | None:
    extent_xy = _mercator_extent_xy(extent)
    if extent_xy is None:
        return None
    x0, x1, y0, y1 = extent_xy
    x_span = x1 - x0
    y_span = y1 - y0
    if x_span <= 0 or y_span <= 0:
        return None
    cx = (x0 + x1) / 2 + shift_x * x_span
    cy = (y0 + y1) / 2 + shift_y * y_span
    new_x_span = x_span * scale
    new_y_span = y_span * scale
    candidate = _extent_from_mercator_xy(
        cx - new_x_span / 2,
        cx + new_x_span / 2,
        cy - new_y_span / 2,
        cy + new_y_span / 2,
        extent,
    )
    return normalize_240_candidate_extent(candidate, settings, fig_width=fig_width, fig_height=fig_height)


def dedupe_240_candidates(candidates: list[list[float] | None]) -> list[list[float]]:
    result: list[list[float]] = []
    seen: set[tuple[float, float, float, float]] = set()
    for candidate in candidates:
        if candidate is None:
            continue
        key = tuple(round(float(value), 3) for value in candidate)
        if key in seen:
            continue
        seen.add(key)
        result.append(candidate)
    return result


def build_240_extent_candidates(
    camera_points: pd.DataFrame,
    render_points: pd.DataFrame,
    protected_points: pd.DataFrame,
    settings: Settings,
    seed_extent: list[float],
    anchor_240_extent: list[float] | None,
    *,
    fig_width: float,
    fig_height: float,
) -> list[list[float]]:
    frames = build_240_camera_frames(camera_points, settings) if not camera_points.empty else {}
    render_frames = build_240_camera_frames(render_points, settings) if not render_points.empty else {}
    base_frames = [
        camera_points,
        protected_points,
        render_frames.get("mid", pd.DataFrame()),
        render_frames.get("late_180", pd.DataFrame()),
        render_frames.get("late_240", pd.DataFrame()),
        render_frames.get("endpoints", pd.DataFrame()),
        frames.get("late_mean", pd.DataFrame()) if frames else pd.DataFrame(),
    ]
    base_frame = concat_track_frames(base_frames)
    endpoint_frame = concat_track_frames([
        render_frames.get("late_180", pd.DataFrame()),
        render_frames.get("late_240", pd.DataFrame()),
        render_frames.get("endpoints", pd.DataFrame()),
        render_frames.get("endpoint_mean", pd.DataFrame()),
        render_frames.get("late_mean", pd.DataFrame()),
    ]) if render_frames else pd.DataFrame()
    full_core_frame = concat_track_frames([camera_points, render_points])

    raw_candidates: list[list[float] | None] = [
        seed_extent,
        anchor_240_extent,
    ]

    if settings.fcst_hours <= 120:
        # 120h also uses the collision-scored camera now, but with a tighter
        # profile than 240h.  More east/north shift candidates help keep recurving
        # tracks away from the in-map legend and top title band.
        min_lon_span, min_lat_span = 24.0, 14.5
        scales = (0.86, 0.94, 1.00, 1.10, 1.24, 1.38)
        # Include zoom-in and eastward-camera candidates.  Eastward camera shift
        # pulls the plotted plume left on the canvas, away from the in-map legend.
        shift_xs = (-0.08, 0.0, 0.12, 0.24, 0.38, 0.54)
        shift_ys = (-0.08, 0.0, 0.12, 0.24, 0.36)
        candidate_specs = [
            (quantile_bounds_for_frame(base_frame, settings, lon_low=0.015, lon_high=0.985, lat_low=0.015, lat_high=0.985), 0.095, 0.600, 0.090, 0.800),
            (quantile_bounds_for_frame(base_frame, settings, lon_low=0.030, lon_high=0.970, lat_low=0.030, lat_high=0.975), 0.115, 0.620, 0.100, 0.820),
            (quantile_bounds_for_frame(endpoint_frame, settings, lon_low=0.015, lon_high=0.985, lat_low=0.015, lat_high=0.990), 0.115, 0.585, 0.105, 0.780),
            (quantile_bounds_for_frame(full_core_frame, settings, lon_low=0.035, lon_high=0.965, lat_low=0.035, lat_high=0.975), 0.090, 0.640, 0.085, 0.835),
            (bounds_from_frames([protected_points], settings), 0.105, 0.625, 0.095, 0.815),
        ]
    else:
        min_lon_span, min_lat_span = 38.0, 24.0
        # Include zoom-in candidates.  A long 240h plume can still have no data
        # west of 140E, so forcing only zoom-out candidates leaves empty space.
        scales = (0.80, 0.88, 0.96, 1.04, 1.16, 1.32, 1.50)
        shift_xs = (-0.06, 0.0, 0.12, 0.24, 0.38, 0.54)
        shift_ys = (-0.14, -0.06, 0.0, 0.10, 0.20)
        candidate_specs = [
            (quantile_bounds_for_frame(base_frame, settings, lon_low=0.015, lon_high=0.985, lat_low=0.015, lat_high=0.985), 0.095, 0.610, 0.080, 0.835),
            (quantile_bounds_for_frame(base_frame, settings, lon_low=0.030, lon_high=0.970, lat_low=0.030, lat_high=0.975), 0.110, 0.630, 0.085, 0.850),
            (quantile_bounds_for_frame(endpoint_frame, settings, lon_low=0.015, lon_high=0.985, lat_low=0.015, lat_high=0.990), 0.125, 0.590, 0.095, 0.805),
            (quantile_bounds_for_frame(full_core_frame, settings, lon_low=0.035, lon_high=0.965, lat_low=0.035, lat_high=0.975), 0.085, 0.655, 0.075, 0.860),
            (bounds_from_frames([protected_points], settings), 0.105, 0.640, 0.085, 0.845),
        ]
        # Do not add the broad West-Pacific template to the normal candidate set.
        # It is reserved as a last-resort fallback after the dynamic candidates
        # are scored.

    for bounds, left, right, bottom, top in candidate_specs:
        raw_candidates.append(candidate_extent_from_240_bounds(
            bounds,
            settings,
            left=left,
            right=right,
            bottom=bottom,
            top=top,
            fig_width=fig_width,
            fig_height=fig_height,
            min_lon_span=min_lon_span,
            min_lat_span=min_lat_span,
        ))

    normalized = dedupe_240_candidates([
        normalize_240_candidate_extent(candidate, settings, fig_width=fig_width, fig_height=fig_height)
        for candidate in raw_candidates
    ])

    expanded: list[list[float] | None] = []
    for candidate in normalized:
        for scale in scales:
            for shift_x in shift_xs:
                for shift_y in shift_ys:
                    expanded.append(scale_shift_240_extent(
                        candidate,
                        settings,
                        scale=scale,
                        shift_x=shift_x,
                        shift_y=shift_y,
                        fig_width=fig_width,
                        fig_height=fig_height,
                    ))
    return dedupe_240_candidates(normalized + expanded)


def mercator_extent_canvas_ratio(extent: list[float]) -> float | None:
    extent_xy = _mercator_extent_xy(extent)
    if extent_xy is None:
        return None
    x0, x1, y0, y1 = extent_xy
    x_span = x1 - x0
    y_span = y1 - y0
    if x_span <= 0 or y_span <= 0:
        return None
    return x_span / y_span


def extent_matches_canvas_aspect(
    extent: list[float],
    *,
    fig_width: float,
    fig_height: float,
    tolerance: float = 0.18,
) -> bool:
    ratio = mercator_extent_canvas_ratio(extent)
    if ratio is None:
        return False
    canvas_ratio = fig_width / fig_height
    if canvas_ratio <= 0:
        return False
    return abs(math.log(ratio / canvas_ratio)) <= tolerance


def zoom_out_240_extent_uniform(
    extent: list[float],
    settings: Settings,
    *,
    fig_width: float,
    fig_height: float,
    preferred_scale: float = 1.06,
) -> list[float]:
    """Slightly zoom out while preserving the map/canvas aspect.

    The previous degree-based margin could make the final Mercator extent too
    tall after clamping, which caused Cartopy to shrink the GeoAxes and leave
    large side margins.  This version expands in projected Mercator x/y space
    and rejects candidates whose aspect no longer matches the canvas.
    """
    for scale in (preferred_scale, 1.045, 1.030):
        candidate = scale_shift_240_extent(
            extent,
            settings,
            scale=scale,
            shift_x=0.0,
            shift_y=0.0,
            fig_width=fig_width,
            fig_height=fig_height,
        )
        if candidate is None:
            continue
        if extent_matches_canvas_aspect(candidate, fig_width=fig_width, fig_height=fig_height):
            return candidate

    # Do not risk a malformed final extent.  The collision-scored candidate is
    # known to be layout-safe, so keep it if the extra zoom-out cannot be done
    # without breaking the canvas aspect.
    return extent


def score_240_extent(
    extent: list[float],
    *,
    df: pd.DataFrame,
    camera_points: pd.DataFrame,
    render_points: pd.DataFrame,
    protected_points: pd.DataFrame,
    endpoint_points: pd.DataFrame,
    settings: Settings,
) -> float:
    if not reasonable_display_240_extent(extent):
        return 1_000_000_000.0

    full_fractions = point_screen_fractions(extent, render_points)
    protected_fractions = point_screen_fractions(extent, protected_points)
    endpoint_fractions = point_screen_fractions(extent, endpoint_points)
    if not protected_fractions:
        return 900_000_000.0

    score = 0.0
    full_count = max(1, len(full_fractions))
    protected_count = max(1, len(protected_fractions))
    endpoint_count = max(1, len(endpoint_fractions))

    full_outside = count_points_outside_screen(full_fractions, margin=0.006)
    protected_outside = count_points_outside_screen(protected_fractions, margin=0.003)
    endpoint_outside = count_points_outside_screen(endpoint_fractions, margin=0.003)
    score += full_outside * 350.0
    score += protected_outside * 7_500.0
    score += endpoint_outside * 25_000.0
    score += (full_outside / full_count) * 25_000.0
    score += (protected_outside / protected_count) * 80_000.0
    score += (endpoint_outside / endpoint_count) * 120_000.0

    boxes = overlay_obstacle_boxes_240(df, settings)
    legend_box = boxes["legend"]
    header_box = boxes["header"]
    credit_box = boxes["credit"]

    if settings.fcst_hours <= 120:
        legend_padding = (0.014, 0.020, 0.024)
        legend_weights = (420.0, 2_600.0, 11_000.0)
        header_weights = (1_400.0, 9_500.0)
        east_limit = 0.600
        north_limit = 0.835
        south_limit = 0.085
        west_empty_limit = 0.235
        west_empty_weight = 4_500.0
        centroid_target_x = 0.355
        centroid_target_y = 0.455
        centroid_weight_x = 9_000.0
        centroid_weight_y = 4_500.0
        target_center_x = 0.350
        target_center_y = 0.440
        compact_width = 0.360
        compact_height = 0.440
        span_weight = (1.4, 2.2)
        broad_lon, broad_lat = 58.0, 38.0
    else:
        legend_padding = (0.014, 0.022, 0.028)
        legend_weights = (380.0, 2_500.0, 11_000.0)
        header_weights = (1_100.0, 7_500.0)
        east_limit = 0.615
        north_limit = 0.865
        south_limit = 0.090
        west_empty_limit = 0.235
        west_empty_weight = 5_500.0
        centroid_target_x = 0.360
        centroid_target_y = 0.475
        centroid_weight_x = 10_000.0
        centroid_weight_y = 5_000.0
        target_center_x = 0.350
        target_center_y = 0.465
        compact_width = 0.430
        compact_height = 0.500
        span_weight = (0.9, 1.3)
        broad_lon, broad_lat = 96.0, 60.0

    legend_full = count_points_in_box(full_fractions, legend_box, padding=legend_padding[0])
    legend_protected = count_points_in_box(protected_fractions, legend_box, padding=legend_padding[1])
    legend_endpoint = count_points_in_box(endpoint_fractions, legend_box, padding=legend_padding[2])
    header_full = count_points_in_box(full_fractions, header_box, padding=0.004)
    header_protected = count_points_in_box(protected_fractions, header_box, padding=0.008)
    credit_full = count_points_in_box(full_fractions, credit_box, padding=0.000)
    credit_protected = count_points_in_box(protected_fractions, credit_box, padding=0.002)

    render_segments = track_screen_segments(extent, render_points)
    legend_segments = count_segments_in_box(render_segments, legend_box, padding=legend_padding[1])
    header_segments = count_segments_in_box(render_segments, header_box, padding=0.006)
    credit_segments = count_segments_in_box(render_segments, credit_box, padding=0.002)

    score += legend_full * legend_weights[0]
    score += legend_protected * legend_weights[1]
    score += legend_endpoint * legend_weights[2]
    # Segment-box intersections catch the visually obvious case where no vertex
    # is inside the legend, but a track line still crosses through it.
    score += legend_segments * (4_800.0 if settings.fcst_hours <= 120 else 5_500.0)
    score += header_full * header_weights[0]
    score += header_protected * header_weights[1]
    score += header_segments * (5_500.0 if settings.fcst_hours <= 120 else 5_000.0)
    score += credit_full * 80.0
    score += credit_protected * 450.0
    score += credit_segments * 350.0

    core_bounds = screen_bounds_from_fractions(protected_fractions)
    if core_bounds is not None:
        west_x, east_x, south_y, north_y = core_bounds
        core_width = max(0.0, east_x - west_x)
        core_height = max(0.0, north_y - south_y)

        centroid = weighted_screen_centroid([
            (protected_fractions, 1.0),
            (endpoint_fractions, 2.0 if settings.fcst_hours <= 120 else 2.8),
        ])
        if centroid is not None:
            centroid_x, centroid_y = centroid
            score += abs(centroid_x - centroid_target_x) * centroid_weight_x
            score += abs(centroid_y - centroid_target_y) * centroid_weight_y

        # Prefer a cleaner composition inside the usable viewport, excluding the
        # title band and the in-map legend.  Direct box hits and segment
        # intersections are scored above; these soft limits avoid crowding.
        score += max(0.0, east_x - east_limit) * 6_500.0
        score += max(0.0, north_y - north_limit) * 8_000.0
        score += max(0.0, south_limit - south_y) * 3_500.0
        # Penalize excessive west/left blank space.  In screen coordinates,
        # a high west_x means the left edge of the important plume sits too far
        # to the right, leaving too much empty map on the west side.
        score += max(0.0, west_x - west_empty_limit) * west_empty_weight
        score += max(0.0, south_y - 0.180) * 900.0
        score += max(0.0, (1.0 - north_y) - 0.230) * 700.0
        score += max(0.0, compact_width - core_width) * 1_200.0
        score += max(0.0, compact_height - core_height) * 900.0
        center_x = (west_x + east_x) / 2
        center_y = (south_y + north_y) / 2
        score += abs(center_x - target_center_x) * 900.0
        score += abs(center_y - target_center_y) * 650.0

    lon_span = extent[1] - extent[0]
    lat_span = extent[3] - extent[2]
    score += lon_span * span_weight[0] + lat_span * span_weight[1]
    score += max(0.0, lon_span - broad_lon) * 14.0
    score += max(0.0, lat_span - broad_lat) * 16.0
    if settings.fcst_hours > 120 and broad_display_240_extent(extent):
        score += 180.0

    return score




def broad_west_pacific_fallback_extent(
    settings: Settings,
    *,
    fig_width: float,
    fig_height: float,
) -> list[float] | None:
    if settings.fcst_hours <= 120:
        return None
    # True last-resort view, not a normal candidate.  Keep the final longitude
    # range below 180E because the current PlateCarree set_extent path wraps
    # longitudes greater than 180E into a near-global view.  Dateline-crossing
    # support should be handled separately with a shifted central_longitude map.
    return normalize_240_candidate_extent(
        [100.0, 179.8, 0.0, 50.0],
        settings,
        fig_width=fig_width,
        fig_height=fig_height,
    )


def finalize_240_map_extent(
    df: pd.DataFrame,
    past_kma: pd.DataFrame,
    settings: Settings,
    extent: list[float],
    anchor_240_extent: list[float] | None,
    *,
    fig_width: float,
    fig_height: float,
) -> list[float]:
    camera_points = extent_points_for_auto_map(df, settings)
    render_points = normalize_240_render_points(df, settings)
    if camera_points.empty and render_points.empty:
        fallback = normalize_240_candidate_extent(extent, settings, fig_width=fig_width, fig_height=fig_height)
        return clamp_240_display_extent(fallback or extent)
    if camera_points.empty:
        camera_points = render_points.copy()
    if render_points.empty:
        render_points = camera_points.copy()

    protected_points = protected_240_points(df, camera_points, render_points, past_kma, settings)
    if protected_points.empty:
        protected_points = camera_points.copy()
    render_frames = build_240_camera_frames(render_points, settings)
    endpoint_points = concat_track_frames([
        render_frames["late_180"],
        render_frames["late_240"],
        render_frames["endpoints"],
        render_frames["endpoint_mean"],
        render_frames["late_mean"],
    ])
    if endpoint_points.empty:
        endpoint_points = protected_points.copy()

    candidates = build_240_extent_candidates(
        camera_points,
        render_points,
        protected_points,
        settings,
        extent,
        anchor_240_extent,
        fig_width=fig_width,
        fig_height=fig_height,
    )
    if not candidates:
        fallback = normalize_240_candidate_extent(extent, settings, fig_width=fig_width, fig_height=fig_height)
        return clamp_240_display_extent(fallback or extent)

    scored = [
        (
            score_240_extent(
                candidate,
                df=df,
                camera_points=camera_points,
                render_points=render_points,
                protected_points=protected_points,
                endpoint_points=endpoint_points,
                settings=settings,
            ),
            candidate,
        )
        for candidate in candidates
    ]
    best_score, best_candidate = min(scored, key=lambda item: item[0])

    # Last-resort only.  A broad West-Pacific view is readable but defeats the
    # automatic camera goal, so do not let it beat a merely imperfect dynamic
    # candidate.  Use it only when the dynamic result is catastrophically bad.
    if settings.fcst_hours > 120 and best_score > 180_000.0:
        fallback = broad_west_pacific_fallback_extent(settings, fig_width=fig_width, fig_height=fig_height)
        if fallback is not None:
            fallback_score = score_240_extent(
                fallback,
                df=df,
                camera_points=camera_points,
                render_points=render_points,
                protected_points=protected_points,
                endpoint_points=endpoint_points,
                settings=settings,
            )
            if fallback_score < best_score * 0.75:
                print(
                    f"{settings.fcst_hours}h broad West-Pacific fallback selected "
                    f"(score={fallback_score:.1f} vs dynamic={best_score:.1f})."
                )
                best_score, best_candidate = fallback_score, fallback

    print(
        f"{settings.fcst_hours}h map extent selected by collision scoring "
        f"({len(candidates)} candidates, score={best_score:.1f}, "
        f"span={best_candidate[1] - best_candidate[0]:.1f} lon x {best_candidate[3] - best_candidate[2]:.1f} lat)."
    )
    # Important: no post-selection zoom-out.  Any zoom-in/zoom-out must compete
    # in the scored candidate set; otherwise the final image is not actually the
    # lowest-score layout.
    return best_candidate


def mercator_figure_size(extent: list[float], *, width: float = 11.2) -> tuple[float, float]:
    projection = ccrs.Mercator()
    lon_min, lon_max, lat_min, lat_max = extent
    center_lon = (lon_min + lon_max) / 2
    center_lat = (lat_min + lat_max) / 2
    x0, _ = projection.transform_point(lon_min, center_lat, ccrs.PlateCarree())
    x1, _ = projection.transform_point(lon_max, center_lat, ccrs.PlateCarree())
    _, y0 = projection.transform_point(center_lon, lat_min, ccrs.PlateCarree())
    _, y1 = projection.transform_point(center_lon, lat_max, ccrs.PlateCarree())
    aspect = abs((y1 - y0) / (x1 - x0)) if x1 != x0 else 0.8
    return width, max(7.2, min(10.8, width * aspect))


def match_extent_to_canvas_aspect(
    extent: list[float],
    *,
    fig_width: float,
    fig_height: float,
    east_expand_ratio: float = 0.75,
) -> list[float]:
    """Expand extent to match fixed canvas aspect without distorting the map.

    Keeps the existing right-biased map composition.
    If longitude range must be expanded, add more of the added range to the east/right side.
    """
    projection = ccrs.Mercator()
    data_crs = ccrs.PlateCarree()

    lon_min, lon_max, lat_min, lat_max = extent
    center_lon = (lon_min + lon_max) / 2
    center_lat = (lat_min + lat_max) / 2

    x0, _ = projection.transform_point(lon_min, center_lat, data_crs)
    x1, _ = projection.transform_point(lon_max, center_lat, data_crs)
    _, y0 = projection.transform_point(center_lon, lat_min, data_crs)
    _, y1 = projection.transform_point(center_lon, lat_max, data_crs)

    map_width = abs(x1 - x0)
    map_height = abs(y1 - y0)

    if map_width == 0 or map_height == 0:
        return extent

    map_aspect = map_width / map_height
    canvas_aspect = fig_width / fig_height

    if map_aspect < canvas_aspect:
        scale = canvas_aspect / map_aspect
        old_lon_span = lon_max - lon_min
        new_lon_span = old_lon_span * scale
        extra_lon = new_lon_span - old_lon_span

        west_add = extra_lon * (1.0 - east_expand_ratio)
        east_add = extra_lon * east_expand_ratio

        return [
            lon_min - west_add,
            lon_max + east_add,
            lat_min,
            lat_max,
        ]

    if map_aspect > canvas_aspect:
        scale = map_aspect / canvas_aspect
        y_center = (y0 + y1) / 2
        y_half = map_height / 2 * scale

        _, new_lat_min = data_crs.transform_point(center_lon, y_center - y_half, projection)
        _, new_lat_max = data_crs.transform_point(center_lon, y_center + y_half, projection)

        return [
            lon_min,
            lon_max,
            new_lat_min,
            new_lat_max,
        ]

    return extent


def canvas_east_expand_ratio(settings: Settings) -> float:
    if not settings.auto_extent:
        return 0.75
    if settings.fcst_hours == 240:
        return 0.62
    return 0.68


def aspect_match_and_clamp_extent(
    extent: list[float],
    settings: Settings,
    *,
    fig_width: float,
    fig_height: float,
) -> list[float]:
    extent = match_extent_to_canvas_aspect(
        extent,
        fig_width=fig_width,
        fig_height=fig_height,
        east_expand_ratio=canvas_east_expand_ratio(settings),
    )
    return clamp_west_pacific_extent(extent)


def finalize_map_extent(
    df: pd.DataFrame,
    past_kma: pd.DataFrame,
    settings: Settings,
    extent: list[float],
    anchor_240_extent: list[float] | None,
    *,
    fig_width: float,
    fig_height: float,
) -> list[float]:
    """Finalize map extent.

    240h intentionally uses a fixed West-Pacific view for stability. The old
    dynamic 240h camera path is no longer invoked. 120h keeps the existing
    automatic collision-scored camera for now.
    """
    if settings.fcst_hours == 240:
        return fixed_240_map_extent(settings)

    if settings.auto_extent and settings.fcst_hours == 120:
        return finalize_240_map_extent(
            df,
            past_kma,
            settings,
            extent,
            anchor_240_extent,
            fig_width=fig_width,
            fig_height=fig_height,
        )

    extent = aspect_match_and_clamp_extent(extent, settings, fig_width=fig_width, fig_height=fig_height)
    return extent


def plot_guidance(df: pd.DataFrame, past_kma: pd.DataFrame, settings: Settings, intensity: str) -> Path:
    df = df.copy()
    df["FT_TIME"] = parse_ft_time(df["FT_TM(UTC)"])
    current_dt = pd.to_datetime(settings.data_time, format="%Y%m%d%H%M", errors="coerce")
    current_dt = None if pd.isna(current_dt) else current_dt.to_pydatetime()

    if settings.fcst_hours == 240:
        # 240h uses a fixed view; skip the old dynamic camera seed/anchor work.
        extent = fixed_240_map_extent(settings)
        anchor_240_extent = None
    else:
        if settings.auto_extent:
            extent = auto_map_extent(df, past_kma, settings)
        else:
            extent = None
        anchor_240_extent = None
        if extent is None:
            center_lat = df["LAT"].mean() + settings.lat_padding if not df.empty else 25
            center_lon = df["LON"].mean() + settings.lon_padding if not df.empty else 135
            extent = map_extent(settings, center_lat, center_lon)
        extent = clamp_west_pacific_extent(extent)

    fig_width = settings.figure_width
    fig_height = settings.figure_height

    extent = finalize_map_extent(
        df,
        past_kma,
        settings,
        extent,
        anchor_240_extent,
        fig_width=fig_width,
        fig_height=fig_height,
    )

    data_crs = ccrs.PlateCarree()
    map_crs = ccrs.Mercator()

    fig = plt.figure(figsize=(fig_width, fig_height), dpi=settings.figure_dpi, frameon=False)
    fig.patch.set_facecolor("#262626")
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

    ax = fig.add_axes([0, 0, 1, 1], projection=map_crs)
    ax.set_facecolor("#262626")
    ax.set_extent(extent, crs=data_crs)
    ax.set_position([0, 0, 1, 1])

    ax.add_feature(cfeature.OCEAN.with_scale("10m"), zorder=0, facecolor="#262626", edgecolor="none")
    ax.add_feature(cfeature.LAND.with_scale("10m"), zorder=0, facecolor="#656565")
    ax.add_feature(cfeature.BORDERS.with_scale("10m"), edgecolor="gray", linestyle="-", linewidth=1)

    gl = ax.gridlines(draw_labels=True, color="gray", alpha=0.3)
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {"size": 10, "color": "gray", "va": "top"}
    gl.ylabel_style = {"size": 10, "color": "gray", "ha": "right"}
    gl.xpadding = -5
    gl.ypadding = -5
    gl.xlocator = mticker.MultipleLocator(5)
    gl.ylocator = mticker.MultipleLocator(5)

    legend_side = choose_legend_side_for_map(df, settings, extent)

    plot_past_track(ax, past_kma, current_dt)
    draw_header(ax, fig, df, settings, intensity, legend_side=legend_side)
    draw_model_tracks(ax, df, settings, legend_side=legend_side)

    kma_start = df[(df["SRC"] == "KMA") & (df["TMD"] == 0)].head(1)
    if not kma_start.empty:
        ax.plot(kma_start.iloc[0]["LON"], kma_start.iloc[0]["LAT"], marker="o", markersize=5, color="white", linestyle="None", zorder=100, transform=ccrs.PlateCarree())

    target = output_path(settings)
    if not settings.overwrite_output:
        target = next_available_path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        target,
        dpi=settings.figure_dpi,
        facecolor="#262626",
        edgecolor="none",
        transparent=False,
        bbox_inches=None,
        pad_inches=0,
    )
    if settings.show_plot:
        plt.show()
    else:
        plt.close(fig)
    return target


def draw_header(ax, fig, df: pd.DataFrame, settings: Settings, intensity: str, *, legend_side: str = "right") -> None:
    ax.add_patch(mpatches.FancyBboxPatch(
        (0.03, 0.915),
        1.0 - 0.03 - 0.024,
        1.0 - 0.915 - 0.022,
        transform=ax.transAxes,
        boxstyle="square,pad=0.03",
        linewidth=0,
        edgecolor="none",
        facecolor="black",
        alpha=0.8,
        zorder=100,
    ))

    cyclone_id = tc_id(settings)
    storm_number = storm_number_label(settings)
    display_name = display_typ_name(settings)
    title = f"{intensity} {cyclone_id} {display_name}".strip()
    title_text = ax.text(
        0.022,
        0.980,
        title,
        transform=ax.transAxes,
        fontsize=38,
        color="#AAF7F4",
        fontweight="1000",
        fontfamily=PLOT_FONT_FAMILY,
        verticalalignment="top",
        zorder=100,
    )

    fig.canvas.draw()
    bbox = title_text.get_window_extent().transformed(ax.transAxes.inverted())
    storm_x = bbox.x1 + 0.004

    if storm_number:
        ax.text(storm_x, 0.966, storm_number, transform=ax.transAxes, fontsize=17.5 if not display_name else 16.5,
                color="#AAF7F4", fontweight="700", fontfamily=PLOT_FONT_FAMILY, verticalalignment="top",
                horizontalalignment="left", zorder=100)

    start = df.loc[(df["SRC"] == "KMA") & (df["TMD"] == 0), "TYP_TM(UTC)"].dropna()
    start_time = str(start.iloc[0]).split(".")[0] if not start.empty else settings.data_time
    start_date = f"{start_time[:4]}-{start_time[4:6]}-{start_time[6:8]}"
    start_hour = start_time[8:10]

    model_nums = len(plotted_model_names(df, settings))
    ax.text(0.978, 0.978, f"{start_date} {start_hour}UTC", transform=ax.transAxes,
            fontsize=34, color="white", fontweight="1000", fontfamily=PLOT_FONT_FAMILY,
            verticalalignment="top", horizontalalignment="right", zorder=100,
            bbox=dict(boxstyle="square,pad=0.5", facecolor="none", linewidth=0))
    ax.text(0.024, 0.932, "VORTEX TRACK GUIDANCE", transform=ax.transAxes,
            fontsize=22.5, color="white", fontweight="800", fontfamily=PLOT_FONT_FAMILY,
            verticalalignment="top", zorder=100,
            bbox=dict(boxstyle="square,pad=0.3", facecolor="none", alpha=0.8, linewidth=0))
    fig.canvas.draw()
    guidance_probe = ax.text(0.024, 0.932, "VORTEX TRACK GUIDANCE", transform=ax.transAxes,
                             fontsize=22.5, fontweight="800", fontfamily=PLOT_FONT_FAMILY, alpha=0)
    fig.canvas.draw()
    guidance_bbox = guidance_probe.get_window_extent().transformed(ax.transAxes.inverted())
    guidance_probe.remove()
    ax.text(guidance_bbox.x1 + 0.006, 0.932, "+", transform=ax.transAxes,
            fontsize=22.5, color="white", fontweight="800", fontfamily=PLOT_FONT_FAMILY,
            verticalalignment="top", zorder=100,
            bbox=dict(boxstyle="square,pad=0.3", facecolor="none", alpha=0.8, linewidth=0))
    ax.text(0.978, 0.932, f"{model_nums} MODELS @ {settings.fcst_hours} HOURS", transform=ax.transAxes,
            fontsize=22.5, color="#DCB0E1", fontweight="800", fontfamily=PLOT_FONT_FAMILY,
            verticalalignment="top", horizontalalignment="right", zorder=100,
            bbox=dict(boxstyle="square,pad=0.3", facecolor="none", alpha=0.8, linewidth=0))
    credit_x = 0.995 if legend_side == "left" else 0.005
    credit_ha = "right" if legend_side == "left" else "left"
    ax.text(credit_x, 0.006, "Plotted by WooJin Kim\nData sourced from KMA APIHUB & NRL ATCF", transform=ax.transAxes,
            fontsize=12, color="aliceblue", fontweight="800", fontfamily=PLOT_FONT_FAMILY,
            verticalalignment="bottom", horizontalalignment=credit_ha, zorder=100,
            bbox=dict(boxstyle="square,pad=0.3", facecolor="none", alpha=0.8, linewidth=0))


def draw_model_tracks(ax, df: pd.DataFrame, settings: Settings, *, legend_side: str = "right") -> None:
    excluded = excluded_models_for(df)
    active = active_model_names(settings)
    legend_rows = []
    grouped = {name: group for name, group in df.dropna(subset=["FT_TIME", "LAT", "LON"]).groupby("SRC")}
    active_legend_models = [model for model in MODEL_INFO if model["name"] in active and model["name"] not in excluded]

    for model in active_legend_models:
        name = model["name"]
        label = model.get("label", name).strip()
        zorder = model.get("zorder", 2)
        style = model_visual_style(name, model)
        has_plot_data = name in grouped
        track = pd.DataFrame()
        metric = ""
        if has_plot_data:
            track = grouped[name].sort_values(["FT_TIME", "SEQ", "TMD"]).drop_duplicates(subset=["FT_TIME"], keep="first")
            has_plot_data = has_forecast_points(track)
            if has_plot_data:
                metric = track_intensity_summary(track, name)

        if has_plot_data:
            ax.plot(
                track["LON"],
                track["LAT"],
                color=style["color"],
                linestyle=style["linestyle"],
                linewidth=style["linewidth"],
                alpha=style["alpha"],
                zorder=zorder,
                transform=ccrs.PlateCarree(),
            )
            markers = marker_points_every_24h(track)
            if not markers.empty:
                ax.plot(
                    markers["LON"],
                    markers["LAT"],
                    linestyle="None",
                    marker=style["marker"],
                    color=style["color"],
                    markerfacecolor=style["markerfacecolor"],
                    markeredgecolor=style["markeredgecolor"],
                    markeredgewidth=style["markeredgewidth"],
                    markersize=style["markersize"],
                    alpha=style["alpha"],
                    zorder=zorder,
                    transform=ccrs.PlateCarree(),
                )

        legend_color = style["color"] if has_plot_data else "#B5B5B5"
        text_color = "black" if has_plot_data else "#A6A6A6"
        legend_rows.append({
            "label": label,
            "metric": metric,
            "color": legend_color,
            "text_color": text_color,
            "linestyle": style["linestyle"],
            "marker": style["marker"],
            "markeredgewidth": style["markeredgewidth"],
            "markersize": style["markersize"],
        })

    draw_model_legend_table(ax, legend_rows, side=legend_side)


def draw_model_legend_table(ax, rows: list[dict], *, side: str = "right") -> None:
    if not rows:
        return

    if side == "left":
        x0, x1 = 0.005, 0.330
    else:
        x0, x1 = 0.670, 0.995
    y0 = 0.005
    pad_x = 0.008
    pad_y = 0.005
    row_h = 0.019
    y1 = y0 + pad_y * 2 + row_h * len(rows)
    font_size = 14
    handle_y_offset = row_h * 0.07

    box = mpatches.FancyBboxPatch(
        (x0, y0),
        x1 - x0,
        y1 - y0,
        transform=ax.transAxes,
        boxstyle="round,pad=0.002,rounding_size=0.006",
        linewidth=0.8,
        edgecolor="#DDDDDD",
        facecolor="white",
        alpha=0.88,
        zorder=100,
    )
    ax.add_patch(box)

    handle_x0 = x0 + pad_x
    handle_x1 = x0 + pad_x + 0.024
    handle_mid = (handle_x0 + handle_x1) / 2
    label_x = x0 + pad_x + 0.030
    pressure_x = x1 - pad_x - 0.069
    lead_x = x1 - pad_x + 0.003
    label_font_family = PLOT_FONT_FAMILY
    label_font_weight = "700"

    for idx, row in enumerate(rows):
        y = y1 - pad_y - row_h * (idx + 0.5)
        handle_y = y + handle_y_offset
        color = row["color"]
        line = mlines.Line2D(
            [handle_x0, handle_x1],
            [handle_y, handle_y],
            transform=ax.transAxes,
            color=color,
            linestyle=row["linestyle"],
            linewidth=2.0,
            zorder=101,
            clip_on=False,
        )
        marker = mlines.Line2D(
            [handle_mid],
            [handle_y],
            transform=ax.transAxes,
            linestyle="None",
            marker=row["marker"],
            markersize=row["markersize"] + 2.5,
            markerfacecolor=color,
            markeredgecolor=color,
            markeredgewidth=row["markeredgewidth"],
            zorder=102,
            clip_on=False,
        )
        ax.add_line(line)
        ax.add_line(marker)
        ax.text(
            label_x,
            y,
            row["label"],
            transform=ax.transAxes,
            fontfamily=label_font_family,
            fontsize=font_size,
            fontweight=label_font_weight,
            color=row["text_color"],
            ha="left",
            va="center",
            zorder=102,
        )
        pressure_text, lead_text = split_intensity_summary(row["metric"])
        metric_text_color = pressure_metric_color(pressure_text)

        ax.text(
            pressure_x,
            y,
            pressure_text,
            transform=ax.transAxes,
            fontfamily=PLOT_FONT_FAMILY,
            fontsize=font_size,
            fontweight="700",
            color=metric_text_color,
            ha="right",
            va="center",
            zorder=102,
        )
        ax.text(
            lead_x,
            y,
            lead_text,
            transform=ax.transAxes,
            fontfamily=PLOT_FONT_FAMILY,
            fontsize=font_size,
            fontweight="700",
            color=metric_text_color,
            ha="right",
            va="center",
            zorder=102,
        )


def main() -> None:
    settings = parse_args()
    if not settings.auth_key:
        raise SystemExit("KMA_APIHUB_AUTH_KEY or --auth-key is required.")

    configure_plot_fonts()
    requested_hours = settings.fcst_hours_options or (settings.fcst_hours,)
    fetch_hour = max(settings.fcst_hours, 240) if settings.auto_fcst_hours else max(requested_hours)
    fetch_settings = replace(settings, fcst_hours=fetch_hour)

    with requests.Session() as session:
        session.headers.update(REQUEST_HEADERS)
        kma_forecast_text = fetch_text(
            session,
            kma_url(fetch_settings, "2"),
            retries=5,
            timeout=8,
            retry_delay=3,
            encoding="cp949",
        )
        kma_df = read_kma_csv(kma_forecast_text, fetch_settings, forecast_only=True)
        atcf_df = empty_atcf_frame() if fetch_settings.skip_atcf else fetch_atcf_data(session, fetch_settings)
        df = normalize_track_data(kma_df, atcf_df, fetch_settings)

        kma_past_text = fetch_text(
            session,
            kma_url(fetch_settings, "0"),
            retries=3,
            timeout=10,
            retry_delay=3,
            encoding="cp949",
        )
        past_kma = build_past_kma_track(read_kma_csv(kma_past_text, fetch_settings, forecast_only=False))

    past_kma = update_and_merge_past_track(
        df=df,
        official_past=past_kma,
        settings=fetch_settings,
    )

    if df.empty:
        reason = "No forecast data matched the requested storm/time/model configuration."
        for fcst_hours in requested_hours:
            metadata_path = settings.metadata_path if len(requested_hours) == 1 else None
            hour_settings = replace(
                settings,
                fcst_hours=fcst_hours,
                fcst_hours_options=(fcst_hours,),
                metadata_path=metadata_path,
            )
            metadata_path = metadata_path_for_settings(hour_settings)
            if metadata_path:
                write_no_output_metadata(
                    metadata_path,
                    settings=hour_settings,
                    intensity=current_intensity(hour_settings),
                    reason=reason,
                )
            print(f"{fcst_hours}h: {reason}")
        return

    if settings.auto_fcst_hours:
        requested_hours = (choose_auto_fcst_hours(df, fetch_settings),)

    for fcst_hours in requested_hours:
        metadata_path = settings.metadata_path if len(requested_hours) == 1 else None
        hour_settings = replace(
            settings,
            fcst_hours=fcst_hours,
            fcst_hours_options=(fcst_hours,),
            metadata_path=metadata_path,
        )
        hour_df = limit_forecast_hours(df, hour_settings)
        intensity = current_intensity(hour_settings)
        metadata_path = metadata_path_for_settings(hour_settings)

        if not plotted_model_names(hour_df, hour_settings):
            reason = "No available model forecast points for this storm/time."
            if metadata_path:
                write_no_output_metadata(
                    metadata_path,
                    settings=hour_settings,
                    intensity=intensity,
                    reason=reason,
                )
            print(f"{fcst_hours}h: {reason}")
            continue

        target = plot_guidance(hour_df, past_kma, hour_settings, intensity)
        if metadata_path:
            write_run_metadata(
                metadata_path,
                target=target,
                df=hour_df,
                settings=hour_settings,
                intensity=intensity,
            )
        print(f"Saved: {target}")


if __name__ == "__main__":
    main()
