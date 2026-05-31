# === VORTEX TRACK GUIDANCE with AI Models ===
# ====== Created by WooJin.Kim 20250613 ======
# Refactored 20260527

from __future__ import annotations

import argparse
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
    {"name": "UM_KEPS", "color": "#B8CE9E", "style": "-", "label": "UM KEPS", "zorder": 84},
    {"name": "UKM", "color": "#FFF200", "style": "-", "label": "UKMO", "zorder": 85},
    {"name": "UKMO_EPS", "color": "#B8CE9E", "style": "-", "label": "UKMO EPS", "zorder": 84},
    {"name": "GFS", "color": "#03C04A", "style": "-", "label": "GFS", "zorder": 83},
    {"name": "GFS_EPS", "color": "#7DDBA7", "style": "-", "label": "GFS GEFS", "zorder": 82},
    {"name": "CMC", "color": "#0CCBF0", "style": "-", "label": "CMC", "zorder": 81},
    {"name": "CMC_EPS", "color": "#AAF7F4", "style": "-", "label": "CMC GEPS", "zorder": 80},
    {"name": "NAVGEM", "color": "#4470AD", "style": "-", "label": "NAVGEM", "zorder": 79},
    {"name": "FNMOC_EPS", "color": "#99AFD7", "style": "-", "label": "NAVGEM EPS", "zorder": 78},
    {"name": "JGSM", "color": "#997950", "style": "-", "label": "JGSM", "zorder": 77},
    {"name": "TEPS", "color": "#654321", "style": "-", "label": "JGSM TEPS", "zorder": 76},
    {"name": "CTCX", "color": "#78081C", "style": "-", "label": "COAMPS-TC ", "zorder": 75},
    {"name": "COAMPS_EPS", "color": "#A13B4E", "style": "-", "label": "COAMPS-TC EPS", "zorder": 74},
    {"name": "AFUM", "color": "#4F746C", "style": "-", "label": "GALWEM", "zorder": 73},
    {"name": "HAFS", "color": "#9D5E5C", "style": "-", "label": "HAFS", "zorder": 72},
    {"name": "HWRF", "color": "#9E9E9E", "style": "-", "label": "HWRF", "zorder": 71},
    {"name": "ECMWF_AIFS", "color": "#C71585", "style": "--", "label": "ECMWF AIFS", "zorder": 96},
    {"name": "ECMWF_AIFS_EPS", "color": "#E34FA5", "style": "--", "label": "ECMWF AIFS EPS", "zorder": 95},
    {"name": "IFEC_AI", "color": "#C8A3D3", "style": "--", "label": "KMA AIFS-ECMWF", "zorder": 98},
    {"name": "IFKM_AI", "color": "#D8BF8A", "style": "--", "label": "KMA AIFS-KIM", "zorder": 97},
    {"name": "AGFS", "color": "#E0FF78", "style": "--", "label": "AIGFS", "zorder": 61},
    {"name": "AIGEFS", "color": "#78FF8F", "style": "--", "label": "AIGEFS", "zorder": 60},
    {"name": "FNEC_AI", "color": "#004B1C", "style": "--", "label": "FourCastNet-ECMWF", "zorder": 63},
    {"name": "FNKM_AI", "color": "#388E3C", "style": "--", "label": "FourCastNet-KIM", "zorder": 62},
    {"name": "PGEC_AI", "color": "#3944BC", "style": "--", "label": "Pangu-Weather-ECMWF", "zorder": 65},
    {"name": "PGKM_AI", "color": "#727EF2", "style": "--", "label": "Pangu-Weather-KIM", "zorder": 64},
    {"name": "GCEC_AI", "color": "#4D248D", "style": "--", "label": "GraphCast-ECMWF", "zorder": 68},
    {"name": "GCKM_AI", "color": "#6C33C6", "style": "--", "label": "GraphCast-KIM", "zorder": 67},
    {"name": "GENC", "color": "#9866C7", "style": "--", "label": "GenCast", "zorder": 69},
    {"name": "FNV3", "color": "#DA70D6", "style": "--", "label": "FNV3", "zorder": 99},
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
    {"name": "PGEC_AI", "apihub": "PGEC_AI", "noaa": None, "knackwx": None},
    {"name": "PGKM_AI", "apihub": "PGKM_AI", "noaa": None, "knackwx": None},
    {"name": "GCEC_AI", "apihub": "GCEC_AI", "noaa": None, "knackwx": None},
    {"name": "GCKM_AI", "apihub": "GCKM_AI", "noaa": None, "knackwx": None},
    {"name": "GENC", "apihub": None, "noaa": None, "knackwx": "GENC", "raw_github": "GENC"},
    {"name": "FNV3", "apihub": None, "noaa": "FGNE", "knackwx": "FNV3", "raw_github": "FNV3"},
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
    "PGEC_AI": ("AI", "DETERMINISTIC"),
    "PGKM_AI": ("AI", "DETERMINISTIC"),
    "GCEC_AI": ("AI", "DETERMINISTIC"),
    "GCKM_AI": ("AI", "DETERMINISTIC"),
    "GENC": ("AI", "ENSEMBLE"),
    "FNV3": ("AI", "ENSEMBLE"),
}

MODEL_ACTIVE_WINDOWS = {
    "UM": (None, "202603312359"),
    "UM_GFDL_6h": (None, "202603312359"),
    "UM_KEPS": (None, "202603312359"),
    "UKM": ("202604010000", None),
    "UKMO_EPS": ("202604010000", None),
}

NO_WIND_SUMMARY_MODELS = {"KIM_EPS", "UKMO_EPS"}
NO_PRESSURE_SUMMARY_MODELS = {"UKMO_EPS"}

PRESSURE_MISSING_COLOR = "#A6A6A6"
PRESSURE_OVER_1000_COLOR = "#222222"
PRESSURE_990_1000_COLOR = "#1595FF"
PRESSURE_970_990_COLOR = "#FFB000"
PRESSURE_950_970_COLOR = "#FF1493"
PRESSURE_930_950_COLOR = "#B00020"
PRESSURE_900_930_COLOR = "#6A00A8"
PRESSURE_UNDER_900_COLOR = "#1F00FF"

MODEL_NAMES = {model["name"] for model in MODEL_INFO}

SOURCE_ORDER = ("APIHUB", "NOAA", "KNACKWX", "RAW.GITHUB")
MODEL_SOURCE_PRIORITY_OVERRIDES = {
    "GENC": ("RAW.GITHUB", "APIHUB", "NOAA", "KNACKWX"),
    "FNV3": ("RAW.GITHUB", "APIHUB", "NOAA", "KNACKWX"),
}
SOURCE_DISPLAY_NAMES = {
    "APIHUB": "KMA APIHUB",
    "NOAA": "NOAA ATCF",
    "KNACKWX": "KNACKWX ATCF",
    "RAW.GITHUB": "GITHUB",
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
    "KNACKWX": "KNACKWX",
    "KNACKWXATCF": "KNACKWX",
    "RAWGITHUB": "RAW.GITHUB",
    "GITHUB": "RAW.GITHUB",
    "GDM": "RAW.GITHUB",
}
SOURCE_IDENTIFIER_COLUMNS = {
    "APIHUB": "apihub",
    "NOAA": "noaa",
    "KNACKWX": "knackwx",
    "RAW.GITHUB": "raw_github",
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
MODEL_SOURCE_ALIASES.update({"KEPS": "UM_KEPS", "IFEC": "IFEC_AI", "IFKM": "IFKM_AI"})
DATA_SOURCE_COLUMN = "_DATA_SOURCE"
MS_PER_KT = 0.514444
KMA_BASE_URL = "https://apihub-pub.kma.go.kr/api/typ01/url/typ_gts_now.php"
DEFAULT_AUTH_KEY = ""
PROJECT_ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Settings:
    typ_number: int = 6
    typ_name: str = "JANGMI"
    typ_name_ko: str = ""
    linked_td_number: int | None = None
    storm_stage: str = "TYP"
    atcf_id: str = "wp062026"
    extra_atcf_ids: tuple[str, ...] = ()
    data_time: str = "202605301200"
    fcst_hours: int = 120
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
    auto_extent: bool = True
    overwrite_output: bool = False
    show_plot: bool = True

# DB→TD 승격 시간대 이중 ATCF ID 조회
# python VTG2.py --atcf-id wp062026 --extra-atcf-ids wp992026

# Source 임시 변경
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


def parse_args() -> Settings:
    parser = argparse.ArgumentParser(description="Plot tropical cyclone track guidance.")
    parser.add_argument("--typ-number", type=int, default=Settings.typ_number)
    parser.add_argument("--typ-name", default=Settings.typ_name)
    parser.add_argument("--typ-name-ko", default=Settings.typ_name_ko)
    parser.add_argument("--linked-td-number", type=int, default=Settings.linked_td_number)
    parser.add_argument("--storm-stage", choices=("TYP", "TD"), default=Settings.storm_stage)
    parser.add_argument("--atcf-id", default=Settings.atcf_id)
    parser.add_argument(
        "--extra-atcf-ids",
        default="",
        help="Comma-separated extra ATCF IDs to merge as the same storm, e.g. wp992026.",
    )
    parser.add_argument("--data-time", default=Settings.data_time)
    parser.add_argument("--fcst-hours", type=int, default=Settings.fcst_hours)
    parser.add_argument("--auto-fcst-hours", action="store_true", help="Choose 72, 120, 180, or 240h automatically.")
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
    parser.add_argument("--no-auto-extent", action="store_true", help="Use fixed margin/padding map extent.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite the deterministic output PNG.")
    parser.add_argument("--no-show", action="store_true", help="Save the PNG without opening a GUI window.")
    args = parser.parse_args()
    try:
        source_overrides = parse_source_overrides(args.source_override)
    except ValueError as exc:
        parser.error(str(exc))

    return Settings(
        typ_number=args.typ_number,
        typ_name=args.typ_name.strip(),
        typ_name_ko=args.typ_name_ko.strip(),
        linked_td_number=args.linked_td_number,
        storm_stage=args.storm_stage,
        atcf_id=args.atcf_id.lower(),
        extra_atcf_ids=tuple(
            item.strip().lower()
            for item in args.extra_atcf_ids.split(",")
            if item.strip()
        ),
        data_time=args.data_time,
        fcst_hours=args.fcst_hours,
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
        auto_extent=not args.no_auto_extent,
        overwrite_output=args.overwrite,
        show_plot=not args.no_show,
    )


def configure_plot_fonts() -> None:
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
    plt.rcParams["font.family"] = ["NanumSquare", "Malgun Gothic", "DejaVu Sans"]
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
                time.sleep(1)
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

    mask = df["TYP"].eq(settings.typ_number)
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


def canonical_model_name(model_name: str) -> str:
    return MODEL_SOURCE_ALIASES.get(model_name, model_name)


def storm_id_from_atcf_id(atcf_id: str) -> str:
    return f"{atcf_id[2:4].upper()}W"


def storm_numbers(settings: Settings) -> set[int]:
    ids = (settings.atcf_id, *settings.extra_atcf_ids)
    return {int(atcf_id[2:4]) for atcf_id in ids}


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
        urls.extend([
            ("NOAA", f"https://www.emc.ncep.noaa.gov/gc_wmb/vxt/DECKS/a{atcf_id}.dat", 0),
            ("KNACKWX", knackwx_url(settings, atcf_id), 0),
        ])
    urls.extend([
        ("RAW.GITHUB", raw_github_url(settings, "GENC"), 6),
        ("RAW.GITHUB", raw_github_url(settings, "FNV3"), 6),
    ])
    return urls


def parse_atcf_coord(series: pd.Series) -> pd.Series:
    text = series.astype("string").str.strip()
    direction = text.str[-1].str.upper()
    value = pd.to_numeric(text.str[:-1], errors="coerce") / 10
    return value.where(direction.isin(["N", "E"]))


def empty_atcf_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=[*ATCF_COLUMNS, DATA_SOURCE_COLUMN])


def read_atcf_csv(text: str | None, *, source: str, skiprows: int = 0) -> pd.DataFrame:
    empty = empty_atcf_frame()
    if not text or not text.strip():
        return empty

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
            executor.submit(fetch_text, session, url, retries=2, timeout=8): (source, url, skiprows)
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


def current_intensity(df: pd.DataFrame) -> str:
    current = df.loc[(df["SRC"] == "KMA") & (df["TMD"] == 0), "WS"]
    if current.empty or pd.isna(current.iloc[0]):
        return "TD"
    ws_10m = float(current.iloc[0])
    if 17 <= ws_10m < 25:
        return "TS"
    if 25 <= ws_10m < 33:
        return "STS"
    if ws_10m >= 33:
        return "TY"
    return "TD"


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
    return apply_common_kma_start(df, settings)


def apply_common_kma_start(df: pd.DataFrame, settings: Settings) -> pd.DataFrame:
    kma_start = df[(df["SRC"] == "KMA") & (df["TMD"] == 0)].head(1).copy()
    if kma_start.empty or kma_start[["LAT", "LON"]].isna().any(axis=None):
        kma_start = pd.DataFrame([{
            "FT": 0,
            "YY": int(settings.data_time[:4]),
            "TYP": settings.typ_number,
            "SEQ": 0,
            "TMD": 0,
            "TYP_TM(UTC)": settings.data_time,
            "FT_TM(UTC)": settings.data_time,
            "LAT": settings.manual_kma_lat,
            "LON": settings.manual_kma_lon,
            "WS": 0,
            "SRC": "KMA",
        }])

    kma_lat = kma_start.iloc[0]["LAT"]
    kma_lon = kma_start.iloc[0]["LON"]
    kma_tm = str(kma_start.iloc[0]["FT_TM(UTC)"])

    starts = [kma_start]
    for model_name in sorted(name for name in df["SRC"].dropna().unique() if name != "KMA"):
        model_start = df[(df["SRC"] == model_name) & (df["TMD"] == 0)].head(1).copy()
        if model_start.empty:
            continue
        model_start.loc[:, "LAT"] = kma_lat
        model_start.loc[:, "LON"] = kma_lon
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
        excluded.add("UKM")

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
        return {lead: 0 for lead in (72, 120, 180, 240)}
    forecast = df[df["SRC"].isin(names)].copy()
    forecast["TMD"] = pd.to_numeric(forecast["TMD"], errors="coerce")
    max_leads = forecast.groupby("SRC")["TMD"].max()
    for lead in (72, 120, 180, 240):
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
    supported = [lead for lead in (72, 120, 180, 240) if support.get(lead, 0) >= min_support]
    base = max(supported) if supported else 72

    lat = current_storm_latitude(df)
    speed = kma_motion_km_per_day(df)

    if lat >= 36 and speed >= 520:
        return min(base, 72)
    if lat >= 32 and speed >= 420:
        return min(base, 120)
    if lat >= 28 and speed >= 360:
        return min(base, 180)
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
    has_wind = (
        model_name not in NO_WIND_SUMMARY_MODELS
        and forecast["WS"].notna().any()
    )

    # 기압이 없으면 대표 시각을 잡지 않는다.
    # 비활성화 값처럼 ----hPa ---KT +000h로 고정한다.
    if not has_pressure:
        return f"{'----':>4}hPa {'---':>3}KT +000h"

    # 기압이 있으면 무조건 해당 모델의 최저기압 시점을 대표값으로 사용한다.
    peak = forecast.loc[valid_pressure.idxmin()]

    pressure = peak["PS"]
    pressure_value = str(int(round(float(pressure))))

    wind_value = "---"
    if has_wind and pd.notna(peak["WS"]):
        wind_value = str(int(round(float(peak["WS"]) / MS_PER_KT)))

    pressure_text = f"{pressure_value:>4}hPa"
    wind_text = f"{wind_value:>3}KT"
    lead_text = f"+{int(round(float(peak['TMD']))):03d}h"
    return f"{pressure_text} {wind_text} {lead_text}"


def split_intensity_summary(metric: str) -> tuple[str, str, str]:
    if not metric:
        return "", "", ""
    parts = metric.split()
    if len(parts) >= 3:
        return parts[0], parts[1], parts[2]
    return metric, "", ""


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


def output_path(settings: Settings) -> Path:
    year_str = storm_year(settings)
    cyclone_id = tc_id(settings)
    stage = settings.storm_stage.upper()
    storm_name = settings.typ_name or "NAMELESS"
    if stage == "TD":
        dir_name = f"TD_{cyclone_id}_{storm_name}"
        file_name = f"TD_{cyclone_id}_{storm_name}_{settings.data_time}_{settings.fcst_hours}h.png"
    else:
        dir_name = f"TYP_{cyclone_id}_{storm_name}"
        file_name = f"TYP_{cyclone_id}_{storm_name}_{settings.data_time}_{settings.fcst_hours}h.png"
    return settings.output_root / year_str / dir_name / file_name


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
        "image_path": image_path.as_posix(),
        "storm_stage": settings.storm_stage,
        "storm_year": storm_year(settings),
        "typ_number": settings.typ_number,
        "typ_name": settings.typ_name,
        "typ_name_ko": settings.typ_name_ko,
        "linked_td_number": settings.linked_td_number,
        "atcf_id": settings.atcf_id,
        "extra_atcf_ids": list(settings.extra_atcf_ids),
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
        return float(clean.quantile(0.08)), float(clean.quantile(0.92))
    return float(clean.min()), float(clean.max())


def auto_map_extent(df: pd.DataFrame, past_kma: pd.DataFrame, settings: Settings) -> list[float] | None:
    points = numeric_track_points(df)
    if points.empty:
        return None

    primary_limit = min(settings.fcst_hours, 120)
    primary = points[pd.to_numeric(points["TMD"], errors="coerce").between(0, primary_limit)].copy()
    if primary.empty:
        primary = points.copy()

    current_dt = pd.to_datetime(settings.data_time, format="%Y%m%d%H%M", errors="coerce")
    if not pd.isna(current_dt) and not past_kma.empty and "FT_TIME" in past_kma:
        past = numeric_track_points(past_kma)
        if not past.empty:
            start = current_dt.to_pydatetime() - timedelta(hours=48)
            end = current_dt.to_pydatetime()
            past = past[past["FT_TIME"].between(start, end)]
            if not past.empty:
                primary = pd.concat([primary, past[["LAT", "LON", "TMD"]]], ignore_index=True)

    lat_min, lat_max = robust_series_bounds(primary["LAT"])
    lon_min, lon_max = robust_series_bounds(primary["LON"])
    lat_span = max(lat_max - lat_min, 7.0)
    lon_span = max(lon_max - lon_min, 9.0)

    center_lat = (lat_min + lat_max) / 2 + max(-1.0, min(2.5, lat_span * 0.06))
    center_lon = (lon_min + lon_max) / 2 + max(2.0, min(7.0, lon_span * 0.22))

    west_margin = lon_span * 0.68 + max(2.0, min(5.0, settings.margin_lon * 0.12))
    east_margin = lon_span * 0.95 + max(6.0, min(10.0, settings.extra_east_lon))
    lat_margin = lat_span * 0.72 + max(2.5, min(5.5, settings.margin_lat * 0.14))

    return [
        center_lon - west_margin,
        center_lon + east_margin,
        center_lat - lat_margin,
        center_lat + lat_margin,
    ]


def clamp_west_pacific_extent(
    extent: list[float],
    *,
    max_east_lon: float = 179.8,
) -> list[float]:

    lon_min, lon_max, lat_min, lat_max = extent

    if lon_max > max_east_lon:
        over = lon_max - max_east_lon
        lon_min -= over
        lon_max = max_east_lon

    return [lon_min, lon_max, lat_min, lat_max]


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


def plot_guidance(df: pd.DataFrame, past_kma: pd.DataFrame, settings: Settings, intensity: str) -> Path:
    df = df.copy()
    df["FT_TIME"] = parse_ft_time(df["FT_TM(UTC)"])
    current_dt = pd.to_datetime(settings.data_time, format="%Y%m%d%H%M", errors="coerce")
    current_dt = None if pd.isna(current_dt) else current_dt.to_pydatetime()

    if settings.auto_extent:
        extent = auto_map_extent(df, past_kma, settings)
    else:
        extent = None
    if extent is None:
        center_lat = df["LAT"].mean() + settings.lat_padding if not df.empty else 25
        center_lon = df["LON"].mean() + settings.lon_padding if not df.empty else 135
        extent = map_extent(settings, center_lat, center_lon)
    extent = clamp_west_pacific_extent(extent)

    fig_width = settings.figure_width
    fig_height = settings.figure_height

    extent = match_extent_to_canvas_aspect(
        extent,
        fig_width=fig_width,
        fig_height=fig_height,
    )

    extent = clamp_west_pacific_extent(extent)

    data_crs = ccrs.PlateCarree()
    map_crs = ccrs.Mercator()

    fig = plt.figure(figsize=(fig_width, fig_height), dpi=settings.figure_dpi)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

    ax = fig.add_axes([0, 0, 1, 1], projection=map_crs)
    ax.set_extent(extent, crs=data_crs)

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

    plot_past_track(ax, past_kma, current_dt)
    draw_header(ax, fig, df, settings, intensity)
    draw_model_tracks(ax, df, settings)

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
        facecolor="#ffffff",
        transparent=False,
    )
    if settings.show_plot:
        plt.show()
    else:
        plt.close(fig)
    return target


def draw_header(ax, fig, df: pd.DataFrame, settings: Settings, intensity: str) -> None:
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
    title = f"{intensity} {cyclone_id} {settings.typ_name}".strip()
    title_text = ax.text(
        0.022,
        0.982 if settings.typ_name else 0.980,
        title,
        transform=ax.transAxes,
        fontsize=38,
        color="#AAF7F4",
        fontweight="1000",
        fontfamily="NanumSquare",
        verticalalignment="top",
        zorder=100,
    )

    if settings.typ_name:
        fig.canvas.draw()
        bbox = title_text.get_window_extent().transformed(ax.transAxes.inverted())
        storm_x = bbox.x1 + 0.005
    else:
        storm_x = 0.185

    if storm_number:
        ax.text(storm_x, 0.966, storm_number, transform=ax.transAxes, fontsize=17.5 if not settings.typ_name else 16.5,
                color="#AAF7F4", fontweight="700", fontfamily="NanumSquare", verticalalignment="top",
                horizontalalignment="left", zorder=100)

    start = df.loc[(df["SRC"] == "KMA") & (df["TMD"] == 0), "TYP_TM(UTC)"].dropna()
    start_time = str(start.iloc[0]).split(".")[0] if not start.empty else settings.data_time
    start_date = f"{start_time[:4]}-{start_time[4:6]}-{start_time[6:8]}"
    start_hour = start_time[8:10]

    model_nums = len(plotted_model_names(df, settings))
    ax.text(0.978, 0.978, f"{start_date} {start_hour}UTC", transform=ax.transAxes,
            fontsize=34, color="white", fontweight="1000", fontfamily="NanumSquare",
            verticalalignment="top", horizontalalignment="right", zorder=100,
            bbox=dict(boxstyle="square,pad=0.5", facecolor="none", linewidth=0))
    ax.text(0.022, 0.932, "VORTEX TRACK GUIDANCE", transform=ax.transAxes,
            fontsize=22.5, color="white", fontweight="800", fontfamily="NanumSquare",
            verticalalignment="top", zorder=100,
            bbox=dict(boxstyle="square,pad=0.3", facecolor="none", alpha=0.8, linewidth=0))
    fig.canvas.draw()
    guidance_probe = ax.text(0.022, 0.932, "VORTEX TRACK GUIDANCE", transform=ax.transAxes,
                             fontsize=22.5, fontweight="800", fontfamily="NanumSquare", alpha=0)
    fig.canvas.draw()
    guidance_bbox = guidance_probe.get_window_extent().transformed(ax.transAxes.inverted())
    guidance_probe.remove()
    ax.text(guidance_bbox.x1 + 0.006, 0.932, "+", transform=ax.transAxes,
            fontsize=22.5, color="white", fontweight="800", fontfamily="NanumSquare",
            verticalalignment="top", zorder=100,
            bbox=dict(boxstyle="square,pad=0.3", facecolor="none", alpha=0.8, linewidth=0))
    ax.text(0.978, 0.932, f"{model_nums} MODELS @ {settings.fcst_hours} HOURS", transform=ax.transAxes,
            fontsize=22.5, color="#DCB0E1", fontweight="800", fontfamily="NanumSquare",
            verticalalignment="top", horizontalalignment="right", zorder=100,
            bbox=dict(boxstyle="square,pad=0.3", facecolor="none", alpha=0.8, linewidth=0))
    ax.text(0.005, 0.006, "Plotted by WooJin Kim\nUsing KMA APIHUB & NRL ATCF", transform=ax.transAxes,
            fontsize=11, color="aliceblue", fontweight="800", fontfamily="NanumSquare",
            verticalalignment="bottom", horizontalalignment="left", zorder=100,
            bbox=dict(boxstyle="square,pad=0.3", facecolor="none", alpha=0.8, linewidth=0))


def draw_model_tracks(ax, df: pd.DataFrame, settings: Settings) -> None:
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

    draw_model_legend_table(ax, legend_rows)


def draw_model_legend_table(ax, rows: list[dict]) -> None:
    if not rows:
        return

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
    pressure_x = x1 - pad_x - 0.080
    wind_x = x1 - pad_x - 0.040
    lead_x = x1 - pad_x
    label_font_family = "NanumSquare"
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
        pressure_text, wind_text, lead_text = split_intensity_summary(row["metric"])
        metric_text_color = pressure_metric_color(pressure_text)

        ax.text(
            pressure_x,
            y,
            pressure_text,
            transform=ax.transAxes,
            fontfamily="NanumSquare",
            fontsize=font_size,
            fontweight="700",
            color=metric_text_color,
            ha="right",
            va="center",
            zorder=102,
        )
        ax.text(
            wind_x,
            y,
            wind_text,
            transform=ax.transAxes,
            fontfamily="NanumSquare",
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
            fontfamily="NanumSquare",
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
    fetch_settings = replace(settings, fcst_hours=max(settings.fcst_hours, 240)) if settings.auto_fcst_hours else settings

    with requests.Session() as session:
        kma_forecast_text = fetch_text(session, kma_url(fetch_settings, "2"), retries=10, timeout=3, encoding="cp949")
        kma_df = read_kma_csv(kma_forecast_text, fetch_settings, forecast_only=True)
        atcf_df = empty_atcf_frame() if fetch_settings.skip_atcf else fetch_atcf_data(session, fetch_settings)
        df = normalize_track_data(kma_df, atcf_df, fetch_settings)

        kma_past_text = fetch_text(session, kma_url(fetch_settings, "0"), retries=3, timeout=10, encoding="cp949")
        past_kma = build_past_kma_track(read_kma_csv(kma_past_text, fetch_settings, forecast_only=False))

    if df.empty:
        raise SystemExit("No forecast data matched the requested storm/time/model configuration.")

    if settings.auto_fcst_hours:
        settings = replace(settings, fcst_hours=choose_auto_fcst_hours(df, fetch_settings))
        df = limit_forecast_hours(df, settings)

    intensity = current_intensity(df)
    target = plot_guidance(df, past_kma, settings, intensity)
    if settings.metadata_path:
        write_run_metadata(
            settings.metadata_path,
            target=target,
            df=df,
            settings=settings,
            intensity=intensity,
        )
    print(f"Saved: {target}")


if __name__ == "__main__":
    main()
