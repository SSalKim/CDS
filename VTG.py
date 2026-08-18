# === VORTEX TRACK GUIDANCE with AI Models ===
# ====== Created by WooJin.Kim 20250613 ======
# Refactored 20260527

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from typing import Iterable
from urllib.parse import urlencode

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io import shapereader
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
    {"name": "KIM_GFDL_6h", "color": "#FA8128", "style": "-", "label": "KIM", "zorder": 87},
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
    {"name": "ICON", "color": "#B85CFF", "style": "-", "label": "ICON", "zorder": 77.8},
    {"name": "ICON_EPS", "color": "#E0B3FF", "style": "-", "label": "ICON EPS", "zorder": 77.7},
    {"name": "JGSM", "color": "#997950", "style": "-", "label": "JGSM", "zorder": 77},
    {"name": "TEPS", "color": "#654321", "style": "-", "label": "JGSM EPS", "zorder": 76},
    {"name": "CTCX", "color": "#78081C", "style": "-", "label": "COAMPS-TC ", "zorder": 75},
    {"name": "COAMPS_EPS", "color": "#A13B4E", "style": "-", "label": "COAMPS-TC EPS", "zorder": 74},
    {"name": "AFUM", "color": "#4F746C", "style": "-", "label": "GALWEM", "zorder": 73},
    {"name": "HAFS", "color": "#9D5E5C", "style": "-", "label": "HAFS", "zorder": 72},
    {"name": "HWRF", "color": "#9E9E9E", "style": "-", "label": "HWRF", "zorder": 71},
    {"name": "ECMWF_AIFS", "color": "#C71585", "style": "--", "label": "ECMWF AIFS", "zorder": 96},
    {"name": "ECMWF_AIFS_EPS", "color": "#E34FA5", "style": "--", "label": "ECMWF AIFS EPS", "zorder": 95},
    {"name": "IFEC_AI", "color": "#1B2AFA", "style": "--", "label": "KMA AIFS-ECMWF", "zorder": 98},
    {"name": "IFKM_AI", "color": "#DDA520", "style": "--", "label": "KMA AIFS-KIM", "zorder": 97},
    {"name": "AGFS", "color": "#E0FF78", "style": "--", "label": "AIGFS", "zorder": 59},
    {"name": "AIGEFS", "color": "#78FF8F", "style": "--", "label": "AIGFS EPS", "zorder": 58},
    {"name": "AICON", "color": "#C8A3D3", "style": "--", "label": "AICON", "zorder": 57.5},
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
    {"name": "WNC", "color": "#DA70D6", "style": "--", "label": "WeatherNext2C", "zorder": 99},
    {"name": "HKO_AREC", "color": "#1E90FF", "style": "--", "label": "Aurora-ECMWF", "zorder": 56},
    {"name": "HKO_FXEC", "color": "#20B2AA", "style": "--", "label": "FuXi-ECMWF", "zorder": 55},
    {"name": "HKO_FWEC", "color": "#A6C875", "style": "--", "label": "FengWu-ECMWF", "zorder": 54},
]

MODEL_SOURCES = [
    {"name": "ECMWF", "apihub": "ECMWF", "noaa": "ECMF", "ral_ucar": "ECMF", "knackwx": "ECMF", "polarwx": "ecm"},
    {"name": "ECMWF_EPS", "apihub": "ECMWF_EPS", "noaa": "EEMN", "ral_ucar": "EEMN", "knackwx": "EEMN", "polarwx": "eps_mean"},
    {"name": "KIM_3h", "apihub": "KIM_3h", "noaa": None},
    {"name": "KIM_6h", "apihub": "KIM_6h", "noaa": None},
    {"name": "KIM_GFDL_6h", "apihub": "KIM_GFDL_6h", "noaa": None},
    {"name": "KIM_EPS", "apihub": "KIM_EPS", "noaa": None},
    {"name": "UM", "apihub": "UM", "noaa": None},
    {"name": "UM_GFDL_6h", "apihub": "UM_GFDL_6h", "noaa": None},
    {"name": "UM_KEPS", "apihub": "UM_KEPS", "noaa": None},
    {"name": "UKM", "apihub": "UKX", "noaa": "UKM", "ral_ucar": "UKM", "knackwx": "UKM", "polarwx": "ukmet"},
    {"name": "UKMO_EPS", "apihub": "EGRR_EPS", "noaa": "UEMN", "ral_ucar": "UEMN", "knackwx": "UEMN"},
    {"name": "GFS", "apihub": "GFS", "noaa": "AVNO", "ral_ucar": "AVNO", "knackwx": "AVNO", "polarwx": "gfs"},
    {"name": "GFS_EPS", "apihub": "GFS_EPS", "noaa": "AEMN", "ral_ucar": "AEMN", "knackwx": "AEMN", "polarwx": "gefs_mean"},
    {"name": "CMC", "apihub": "CMC", "noaa": "CMC", "ral_ucar": "CMC", "knackwx": "CMC", "polarwx": "cmc"},
    {"name": "CMC_EPS", "apihub": "CMC_EPS", "noaa": "CEMN", "ral_ucar": "CEMN", "knackwx": "CEMN", "polarwx": "cmc_mean"},
    {"name": "JGSM", "apihub": "JGSM", "noaa": "JGSM", "ral_ucar": "JGSM", "knackwx": "JGSM"},
    {"name": "TEPS", "apihub": "TEPS", "noaa": "JENS", "ral_ucar": "JENS", "knackwx": "JENS"},
    {"name": "NAVGEM", "apihub": "NAVGEM", "noaa": "NVGM", "ral_ucar": "NVGM", "knackwx": "NVGM"},
    {"name": "FNMOC_EPS", "apihub": "FNMOC_EPS", "noaa": "NEMN", "ral_ucar": "NEMN", "knackwx": "NEMN"},
    {"name": "ICON", "apihub": None, "polarwx": "icon"},
    {"name": "ICON_EPS", "apihub": None, "polarwx": "icon_ens_mean"},
    {"name": "CTCX", "apihub": None, "noaa": "CTCX", "ral_ucar": "CTCX", "knackwx": "CTCX"},
    {"name": "COAMPS_EPS", "apihub": None, "noaa": "CTMN", "ral_ucar": "CTMN", "knackwx": "CTMN"},
    {"name": "AFUM", "apihub": None, "noaa": "AFUM", "ral_ucar": "AFUM"},
    {"name": "HWRF", "apihub": "HWRF", "noaa": "HWRF", "ral_ucar": "HWRF", "knackwx": "HWRF", "polarwx": "hwrf"},
    {"name": "HAFS", "apihub": "HAFS", "noaa": "HFSA", "ral_ucar": "HFSA", "knackwx": "HFSA", "polarwx": "hafsa"},
    {"name": "ECMWF_AIFS", "apihub": "ECMWF_AIFS", "noaa": "AIFS", "ral_ucar": "AIFS", "knackwx": "AIFS", "polarwx": "aifs"},
    {"name": "ECMWF_AIFS_EPS", "apihub": None, "noaa": "EAIM", "ral_ucar": "EAMN", "knackwx": "EAMN", "polarwx": "aifs_ens_mean"},
    {"name": "AGFS", "apihub": None, "noaa": "AGFS", "ral_ucar": "AGFS", "knackwx": "AGFS"},
    {"name": "AIGEFS", "apihub": None, "noaa": "AIMN", "ral_ucar": "AIMN", "knackwx": "AIMN", "smca": "AIGEFSM"},
    {"name": "AICON", "apihub": None, "smca": "AICON"},
    {"name": "IFEC_AI", "apihub": "IFEC_AI", "noaa": None},
    {"name": "IFKM_AI", "apihub": "IFKM_AI", "noaa": None},
    {"name": "FNEC_AI", "apihub": "FNEC_AI", "noaa": None},
    {"name": "FNKM_AI", "apihub": "FNKM_AI", "noaa": None},
    {"name": "FNUM_AI", "apihub": "FNUM_AI", "noaa": None},
    {"name": "PGEC_AI", "apihub": "PGEC_AI", "noaa": None},
    {"name": "PGKM_AI", "apihub": "PGKM_AI", "noaa": None},
    {"name": "PGUM_AI", "apihub": "PGUM_AI", "noaa": None},
    {"name": "GCEC_AI", "apihub": "GCEC_AI", "noaa": None},
    {"name": "GCKM_AI", "apihub": "GCKM_AI", "noaa": None},
    {"name": "GCUM_AI", "apihub": "GCUM_AI", "noaa": None},
    {"name": "GENC", "apihub": None, "noaa": None, "knackwx": "GENC", "raw_github": "GENC", "polarwx": "gencast"},
    {"name": "WNC", "apihub": None, "noaa": "FGNE", "ral_ucar": "FGNE", "knackwx": "FNV3", "raw_github": "FNV3", "polarwx": "deepmind"},
    {"name": "HKO_AREC", "apihub": "HKO_AREC", "noaa": None},
    {"name": "HKO_FXEC", "apihub": "HKO_FXEC", "noaa": None},
    {"name": "HKO_FWEC", "apihub": "HKO_FWEC", "noaa": None},
]

MODEL_CATEGORIES = {
    "ECMWF": ("DYNAMICAL", "DETERMINISTIC"),
    "ECMWF_EPS": ("DYNAMICAL", "ENSEMBLE"),
    "KIM_3h": ("DYNAMICAL", "DETERMINISTIC"),
    "KIM_6h": ("DYNAMICAL", "DETERMINISTIC"),
    "KIM_GFDL_6h": ("DYNAMICAL", "DETERMINISTIC"),
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
    "ICON": ("DYNAMICAL", "DETERMINISTIC"),
    "ICON_EPS": ("DYNAMICAL", "ENSEMBLE"),
    "CTCX": ("DYNAMICAL", "DETERMINISTIC"),
    "COAMPS_EPS": ("DYNAMICAL", "ENSEMBLE"),
    "AFUM": ("DYNAMICAL", "DETERMINISTIC"),
    "HWRF": ("DYNAMICAL", "DETERMINISTIC"),
    "HAFS": ("DYNAMICAL", "DETERMINISTIC"),
    "ECMWF_AIFS": ("AI", "DETERMINISTIC"),
    "ECMWF_AIFS_EPS": ("AI", "ENSEMBLE"),
    "AGFS": ("AI", "DETERMINISTIC"),
    "AIGEFS": ("AI", "ENSEMBLE"),
    "AICON": ("AI", "DETERMINISTIC"),
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
    "WNC": ("AI", "ENSEMBLE"),
}

MODEL_ACTIVE_WINDOWS = {
    "HAFS": ("202301010000", None),                 # HAFS 예측자료 신규 추가(2023.1.1.~)

    "ECMWF_AIFS": ("202408010000", None),           # ECMWF AIFS 예측자료 신규 추가(2024.8.19.~)

    "FNEC_AI": ("202405150000", None),              # 기상청(KMA) AI 예측자료 신규 추가(2025.3.17.~)
    "FNKM_AI": ("202405150000", None),              # 기상청(KMA) AI 예측자료 신규 추가(2025.3.17.~)  
    "PGEC_AI": ("202405150000", None),              # 기상청(KMA) AI 예측자료 신규 추가(2025.3.17.~)
    "PGKM_AI": ("202405150000", None),              # 기상청(KMA) AI 예측자료 신규 추가(2025.3.17.~)
    "GCEC_AI": ("202405150000", None),              # 기상청(KMA) AI 예측자료 신규 추가(2025.3.17.~)
    "GCKM_AI": ("202405150000", None),              # 기상청(KMA) AI 예측자료 신규 추가(2025.3.17.~)

    "GENC": ("202506010000", None),                 # Google DeeepMind Ensemble 예측자료 신규 추가(2025.6.1.~)
    "WNC": ("202506010000", None),                  # Google DeepMind WeatherNext2 Cyclones(구 FNV3)

    "HKO_AREC": ("202507210000", None),             # 홍콩기상청(HKO) AI 예측자료 신규 추가(2025.8.12.~)
    "HKO_FXEC": ("202507210000", None),             # 홍콩기상청(HKO) AI 예측자료 신규 추가(2025.8.12.~)
    "HKO_FWEC": ("202507210000", None),             # 홍콩기상청(HKO) AI 예측자료 신규 추가(2025.8.12.~)

    "UM": (None, "202603312359"),                   # 기상청(KMA) UM 기반 수치예보시스템 종료(2026.3.31.),
    "UM_GFDL_6h": (None, "202603312359"),           # 기상청(KMA) UM 기반 수치예보시스템 종료(2026.3.31.),
    "UM_KEPS": (None, "202603312359"),              # 기상청(KMA) UM 기반 수치예보시스템 종료(2026.3.31.),
    "FNUM_AI": ("202405150000", "202603312359"),    # 기상청(KMA) UM 기반 수치예보시스템 종료(2026.3.31.),
    "PGUM_AI": ("202405150000", "202603312359"),    # 기상청(KMA) UM 기반 수치예보시스템 종료(2026.3.31.),
    "GCUM_AI": ("202405150000", "202603312359"),    # 기상청(KMA) UM 기반 수치예보시스템 종료(2026.3.31.),

    "UKM": ("202604010000", None),                  # 영국기상청(UKMO) UM 예측자료 신규 추가(2026.4.1.~)
    "UKMO_EPS": ("202604010000", None),             # 영국기상청(UKMO) UM 예측자료 신규 추가(2026.4.1.~)

    "AGFS": ("202601010000", None),                # 미해양대기청(NOAA) AI 예측자료 신규 추가(2026.4.1.~)
    "AIGEFS": ("202601010000", None),               # 미해양대기청(NOAA) AI 예측자료 신규 추가(2026.4.1.~)

    "IFEC_AI": ("202601010000", None),              # 기상청(KMA) AIFS 예측자료 신규 추가(2026.4.28.~)
    "IFKM_AI": ("202601010000", None),              # 기상청(KMA) AIFS 예측자료 신규 추가(2026.4.28.~)

    "ECMWF_AIFS_EPS": ("202605150000", None),       # ECMWF AIFS-ENS 예측자료 신규 추가(2026.5.26.~)
    "ICON": ("202608010000", None),                 # POLARWX ICON 예측자료 신규 추가(2026.8.~)
    "ICON_EPS": ("202608010000", None),             # POLARWX ICON-EPS 예측자료 신규 추가(2026.8.~)
    "AICON": ("202608010000", None),                # SMCA.FUN AI-ICON 예측자료 신규 추가(2026.8.~)
}

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
MAX_DISPLAY_240_EAST_LON = 179.9
MIN_DISPLAY_240_SOUTH_LAT = -22.0
MAX_DISPLAY_240_NORTH_LAT = 74.0
MAX_CAMERA_240_LON_DISTANCE = 92.0
MAX_CAMERA_240_LAT_DISTANCE = 62.0

FIXED_240_MAP_EXTENT = [100.0, 179.9, 0.0, 51.45]

DISPLAY_120_LON_MIN = 100.0
DISPLAY_120_LON_MAX = 179.9
DISPLAY_120_LAT_MIN = 0.0
DISPLAY_120_LAT_MAX = 50.0
APIHUB_MODEL_START_MAX_DISTANCE_KM = float(os.getenv("VTG_APIHUB_START_MAX_DISTANCE_KM", "850"))
MODEL_TRACK_MAX_SPEED_KMH = float(os.getenv("VTG_MODEL_TRACK_MAX_SPEED_KMH", "100"))
KNACKWX_MAX_LEAD_GAP_HOURS = float(os.getenv("VTG_KNACKWX_MAX_LEAD_GAP_HOURS", "12"))


MODEL_NAMES = {model["name"] for model in MODEL_INFO}

SOURCE_ORDER = ("APIHUB", "DMDW", "RAW.GITHUB", "POLARWX", "SMCA.FUN", "RAL.UCAR", "KNACKWX")
MODEL_SOURCE_PRIORITY_OVERRIDES: dict[str, tuple[str, ...]] = {}
SOURCE_DISPLAY_NAMES = {
    "APIHUB": "KMA APIHUB",
    "DMDW": "KMA DMDW",
    "NOAA": "NOAA ATCF",
    "POLARWX": "POLARWX",
    "SMCA.FUN": "SMCA.FUN",
    "RAL.UCAR": "RAL UCAR ATCF",
    "KNACKWX": "KNACKWX ATCF",
    "RAW.GITHUB": "GITHUB",
}
SOURCE_ALIASES = {
    "APIHUB": "APIHUB",
    "KMAAPIHUB": "APIHUB",
    "DMDW": "DMDW",
    "KMADMDW": "DMDW",
    "NOAA": "NOAA",
    "ATCF": "NOAA",
    "NCEP": "NOAA",
    "NOAAATCF": "NOAA",
    "POLARWX": "POLARWX",
    "POLAR": "POLARWX",
    "SMCAFUN": "SMCA.FUN",
    "SMCA": "SMCA.FUN",
    "RALUCAR": "RAL.UCAR",
    "UCAR": "RAL.UCAR",
    "RAL": "RAL.UCAR",
    "KNACKWX": "KNACKWX",
    "KNACK": "KNACKWX",
    "APIKNACKWX": "KNACKWX",
    "EMCNCEP": "NOAA",
    "NCEPATCF": "NOAA",
    "EMCNCEPATCF": "NOAA",
    "RAWGITHUB": "RAW.GITHUB",
    "GITHUB": "RAW.GITHUB",
    "GDM": "RAW.GITHUB",
}
SOURCE_IDENTIFIER_COLUMNS = {
    "APIHUB": "apihub",
    "DMDW": "dmdw",
    "NOAA": "noaa",
    "POLARWX": "polarwx",
    "SMCA.FUN": "smca",
    "RAL.UCAR": "ral_ucar",
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
MODEL_ALIAS_PRIORITIES: dict[str, int] = {}
for row in MODEL_SOURCES:
    for source, column in SOURCE_IDENTIFIER_COLUMNS.items():
        model_id = row.get(column)
        if not model_id:
            continue

        MODEL_ALIAS_PRIORITIES.setdefault(model_id, 0)

        alias_ids = []
        if source == "APIHUB" and model_id == "ECMWF":
            alias_ids.extend(["ECMWF_TIGGE", "ECM_SPR_D"])
        if source == "NOAA" and model_id == "ECMWF":
            alias_ids.extend(["ECMO", "EMX"])
        if source == "APIHUB" and model_id == "ECMWF_EPS":
            alias_ids.extend(["ECM_SPR_E"])
        if source == "APIHUB" and model_id == "UM_KEPS":
            alias_ids.extend(["KEPS"])
        if source == "NOAA" and model_id == "UKM":
            alias_ids.extend(["EGRR"])
        if source == "APIHUB" and model_id == "GFS":
            alias_ids.extend(["GFS_TIGGE", "NCEP_TIGGE"])
        if source == "APIHUB" and model_id == "CMC":
            alias_ids.extend(["CMSC"])
        if source == "APIHUB" and model_id == "CMC_EPS":
            alias_ids.extend(["CMSC_EPS"])
        if source == "APIHUB" and model_id == "NAVGEM":
            alias_ids.extend(["NOGAPS"])

        if model_id.endswith("_AI"):
            alias_ids.append(model_id[:-3])
        if source == "APIHUB" and model_id == "GCEC_AI":
            alias_ids.extend(["GPEC"])
        if source == "APIHUB" and model_id == "GCKM_AI":
            alias_ids.extend(["GPKM"])
        if source == "APIHUB" and model_id == "GCUM_AI":
            alias_ids.extend(["GPUM"])

        if source == "APIHUB" and model_id == "ECMWF_AIFS":
            alias_ids.extend(["ECMF_AIFS"])


        for alias_priority, alias_id in enumerate(alias_ids, start=1):
            MODEL_SOURCE_ALIASES.setdefault(alias_id, row["name"])
            if source in SOURCE_MODEL_IDS:
                SOURCE_MODEL_IDS[source].add(alias_id)
            MODEL_ALIAS_PRIORITIES.setdefault(alias_id, alias_priority)

DATA_SOURCE_COLUMN = "_DATA_SOURCE"
RAW_MODEL_COLUMN = "_RAW_MODEL"
MODEL_ALIAS_PRIORITY_COLUMN = "_MODEL_ALIAS_PRIORITY"
MS_PER_KT = 0.514444
KMA_URL_BASE = (os.getenv("KMA_APIHUB_BASE_URL") or "https://apihub-pub.kma.go.kr/api/typ01/url").rstrip("/")
KMA_FALLBACK_URL_BASE = (os.getenv("KMA_APIHUB_FALLBACK_BASE_URL") or "https://apihub.kma.go.kr/api/typ01/url").rstrip("/")
SMCA_TYPHOON_API_BASE = (os.getenv("SMCA_TYPHOON_API_BASE_URL") or "https://smca.fun/api/typhoon_msg/").rstrip("/")
KMA_BASE_URL = f"{KMA_URL_BASE}/typ_gts_now.php"
KMA_TYP_NOW_URL = f"{KMA_URL_BASE}/typ_now.php"
KMA_TD_NOW_URL = f"{KMA_URL_BASE}/td_now.php"
DEFAULT_AUTH_KEY = ""
DEFAULT_FALLBACK_AUTH_KEY = os.getenv("KMA_APIHUB_FALLBACK_AUTH_KEY", "").strip()
VALID_FCST_HOURS = (120, 240)
CLI_FCST_HOURS = (*VALID_FCST_HOURS, 360)
TRACK_HISTORY_MAX_LOOKBACK_DAYS = 45
PROJECT_ROOT = Path(__file__).resolve().parent
PLOT_FONT_FAMILY = "DejaVu Sans"
PREFERRED_PLOT_FONT_FILE = PROJECT_ROOT / "fonts" / "NanumSquareB.ttf"
MAP_FEATURE_SCALE = os.getenv("VTG_MAP_FEATURE_SCALE", "10m").strip().lower()
if MAP_FEATURE_SCALE not in {"10m", "50m", "110m"}:
    MAP_FEATURE_SCALE = "10m"
ATCF_RECENT_RANGE_BYTES = 2 * 1024 * 1024
HOKKAIDO_EAST_BORDER_MASK = (145.0, 42.8, 146.2, 45.0)
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json,text/csv,text/plain,*/*",
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
    canonical_storm_stage: str = ""
    canonical_typ_number: int | None = None
    canonical_typ_name: str = ""
    canonical_typ_name_ko: str = ""
    storm_stage: str = "TYP"
    atcf_id: str = "wp062026"
    extra_atcf_ids: tuple[str, ...] = ()
    data_time: str = "202605301200"
    storm_year: str = ""
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
    output_root: Path = PROJECT_ROOT / "data"
    metadata_path: Path | None = None
    auth_key: str = os.getenv("KMA_APIHUB_AUTH_KEY", DEFAULT_AUTH_KEY)
    fallback_auth_key: str = DEFAULT_FALLBACK_AUTH_KEY
    fallback_url_base: str = KMA_FALLBACK_URL_BASE
    base_url: str = KMA_BASE_URL
    kma_forecast_text_path: Path | None = None
    kma_past_text_path: Path | None = None
    http_cache_dir: Path | None = None
    http_cache_ttl_seconds: int = 6 * 3600
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
        if hour not in CLI_FCST_HOURS:
            allowed = ", ".join(f"{item}h" for item in CLI_FCST_HOURS)
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
    parser.add_argument("--canonical-storm-stage", choices=("", "TYP", "TD"), default=Settings.canonical_storm_stage)
    parser.add_argument("--canonical-typ-number", type=int, default=Settings.canonical_typ_number)
    parser.add_argument("--canonical-typ-name", default=Settings.canonical_typ_name)
    parser.add_argument("--canonical-typ-name-ko", default=Settings.canonical_typ_name_ko)
    parser.add_argument("--storm-stage", choices=("TYP", "TD"), default=Settings.storm_stage)
    parser.add_argument("--atcf-id", default=Settings.atcf_id)
    parser.add_argument(
        "--extra-atcf-ids",
        default="",
        help="Comma-separated extra ATCF IDs to merge as the same storm, e.g. wp992026.",
    )
    parser.add_argument("--data-time", default=Settings.data_time)
    parser.add_argument("--storm-year", default=Settings.storm_year, help="Storm season year used for output folders and TC IDs.")
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
        "--fallback-auth-key",
        default=os.getenv("KMA_APIHUB_FALLBACK_AUTH_KEY", DEFAULT_FALLBACK_AUTH_KEY),
        help="Optional fallback KMA APIHUB auth key for apihub.kma.go.kr.",
    )
    parser.add_argument(
        "--kma-forecast-text-path",
        type=Path,
        default=Settings.kma_forecast_text_path,
        help="Read pre-fetched KMA APIHUB mode=2 typ_gts_now text from this file.",
    )
    parser.add_argument(
        "--kma-past-text-path",
        type=Path,
        default=Settings.kma_past_text_path,
        help="Read pre-fetched KMA APIHUB mode=0 typ_gts_now text from this file.",
    )
    parser.add_argument(
        "--http-cache-dir",
        type=Path,
        default=Settings.http_cache_dir,
        help="Directory for reusable per-URL HTTP response cache during a workflow run.",
    )
    parser.add_argument(
        "--http-cache-ttl-seconds",
        type=int,
        default=Settings.http_cache_ttl_seconds,
        help="Maximum age for --http-cache-dir entries.",
    )
    parser.add_argument(
        "--source-override",
        action="append",
        default=[],
        metavar="MODEL=SOURCE",
        help="Prefer a source for this run, e.g. ECMWF_EPS=NOAA. Repeat or comma-separate.",
    )
    parser.add_argument("--skip-atcf", action="store_true", help="Skip ATCF fallback sources.")
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
        canonical_storm_stage=args.canonical_storm_stage.strip(),
        canonical_typ_number=args.canonical_typ_number,
        canonical_typ_name=args.canonical_typ_name.strip(),
        canonical_typ_name_ko=args.canonical_typ_name_ko.strip(),
        storm_stage=args.storm_stage,
        atcf_id=args.atcf_id.lower(),
        extra_atcf_ids=tuple(
            item.strip().lower()
            for item in args.extra_atcf_ids.split(",")
            if item.strip()
        ),
        data_time=args.data_time,
        storm_year=args.storm_year.strip(),
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
        fallback_auth_key=args.fallback_auth_key.strip(),
        fallback_url_base=KMA_FALLBACK_URL_BASE,
        kma_forecast_text_path=args.kma_forecast_text_path,
        kma_past_text_path=args.kma_past_text_path,
        http_cache_dir=args.http_cache_dir,
        http_cache_ttl_seconds=max(0, int(args.http_cache_ttl_seconds)),
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

    preferred_font = PREFERRED_PLOT_FONT_FILE
    if preferred_font.exists():
        try:
            fm.fontManager.addfont(str(preferred_font))
            PLOT_FONT_FAMILY = fm.FontProperties(fname=str(preferred_font)).get_name()
            plt.rcParams["font.family"] = [PLOT_FONT_FAMILY]
            plt.rcParams["font.sans-serif"] = [PLOT_FONT_FAMILY]
            plt.rcParams["axes.unicode_minus"] = False
            print(f"Using plot font: {PLOT_FONT_FAMILY} ({preferred_font})")
            return
        except RuntimeError as exc:
            print(f"Preferred font could not be loaded: {preferred_font} ({exc})")

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
    plt.rcParams["font.sans-serif"] = [PLOT_FONT_FAMILY, "DejaVu Sans"]
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


def kma_now_url(settings: Settings, endpoint_url: str, typ_number: int | None) -> str:
    params = {
        "src": "",
        "typ": "" if typ_number is None else str(int(typ_number)),
        "tm": settings.data_time,
        "mode": "0",
        "disp": "1",
        "help": "0",
        "authKey": settings.auth_key,
    }
    return f"{endpoint_url}?{urlencode(params)}"


def kma_fallback_endpoint_url(settings: Settings, endpoint_url: str) -> str:
    if not settings.fallback_auth_key:
        return ""
    endpoint_name = endpoint_url.rsplit("/", 1)[-1]
    return f"{settings.fallback_url_base.rstrip('/')}/{endpoint_name}"


def kma_fallback_url(settings: Settings, mode: str) -> str:
    endpoint_url = kma_fallback_endpoint_url(settings, settings.base_url)
    if not endpoint_url:
        return ""
    params = {
        "src": "",
        "tm": settings.data_time,
        "mode": mode,
        "disp": "1",
        "help": "0",
        "authKey": settings.fallback_auth_key,
    }
    return f"{endpoint_url}?{urlencode(params)}"


def kma_now_fallback_url(settings: Settings, endpoint_url: str, typ_number: int | None) -> str:
    fallback_endpoint_url = kma_fallback_endpoint_url(settings, endpoint_url)
    if not fallback_endpoint_url:
        return ""
    params = {
        "src": "",
        "typ": "" if typ_number is None else str(int(typ_number)),
        "tm": settings.data_time,
        "mode": "0",
        "disp": "1",
        "help": "0",
        "authKey": settings.fallback_auth_key,
    }
    return f"{fallback_endpoint_url}?{urlencode(params)}"


def normalize_utc_stamp(value: str) -> str:
    text = str(value or "").strip().split(".", 1)[0]
    if len(text) >= 12 and text[:12].isdigit():
        return text[:12]
    if len(text) >= 10 and text[:10].isdigit():
        return f"{text[:10]}00"
    return ""


def kma_now_row_numbers(row: list[str]) -> set[int]:
    numbers: set[int] = set()
    for value in row[:6]:
        text = str(value or "").strip().split(".", 1)[0]
        if not text.isdigit():
            continue
        number = int(text)
        if 1 <= number <= 99:
            numbers.add(number)
    return numbers


def kma_now_row_time(row: list[str], data_time: str) -> str:
    target = normalize_utc_stamp(data_time)
    for value in row:
        time_text = normalize_utc_stamp(value)
        if time_text and time_text[:10] == target[:10]:
            return time_text
    return ""


def safe_float_value(value) -> float | None:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def kma_now_row_lat_lon(row: list[str]) -> tuple[float, float] | None:
    pairs = [(7, 8), (5, 6), (4, 5), (6, 7), (8, 9)]
    pairs.extend((index, index + 1) for index in range(max(0, len(row) - 1)))
    seen: set[tuple[int, int]] = set()
    for lat_index, lon_index in pairs:
        if (lat_index, lon_index) in seen or lon_index >= len(row):
            continue
        seen.add((lat_index, lon_index))
        lat = safe_float_value(row[lat_index])
        lon = safe_float_value(row[lon_index])
        if lat is None or lon is None:
            continue
        if -90.0 <= lat <= 90.0 and 0.0 <= lon <= 360.0:
            return lat, lon
    return None


def kma_now_point_from_text(
    text: str | None,
    *,
    settings: Settings,
    typ_number: int | None,
    require_number_match: bool,
) -> AnalysisPoint | None:
    if not text or "NODATA" in text.upper():
        return None
    target_number = int(typ_number) if typ_number else None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            row = [item.strip() for item in next(csv.reader([line]))]
        except csv.Error:
            continue
        if row and row[-1] == "=":
            row = row[:-1]
        time_utc = kma_now_row_time(row, settings.data_time)
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
        return AnalysisPoint(
            time_utc=time_utc,
            lat=lat,
            lon=lon,
            source="KMA_OFFICIAL",
            atcf_id="" if settings.skip_atcf else settings.atcf_id,
            match_method="kma_now_fallback",
        )
    return None


def kma_now_endpoint_candidates(settings: Settings) -> list[tuple[str, str, int | None, int | None]]:
    candidates: list[tuple[str, str, int | None, int | None]] = []
    seen: set[tuple[str, int | None, int | None]] = set()

    def add(label: str, endpoint: str, query_number: int | None, filter_number: int | None = None) -> None:
        query_value = int(query_number) if query_number else None
        filter_value = int(filter_number) if filter_number else query_value
        if query_value is None and filter_value is None:
            return
        key = (endpoint, query_value, filter_value)
        if key not in seen:
            seen.add(key)
            candidates.append((label, endpoint, query_value, filter_value))

    data_typ_number = kma_data_typ_number(settings)
    stage = settings.storm_stage.upper()
    if stage == "TD":
        add("td_now", KMA_TD_NOW_URL, settings.typ_number)
        if settings.linked_typ_number:
            add("typ_now", KMA_TYP_NOW_URL, settings.linked_typ_number)
        add("typ_now", KMA_TYP_NOW_URL, data_typ_number)
    else:
        add("typ_now", KMA_TYP_NOW_URL, data_typ_number)
        if settings.linked_td_number:
            add("td_now", KMA_TD_NOW_URL, settings.linked_td_number)
    add("typ_now", KMA_TYP_NOW_URL, None, data_typ_number)
    add("td_now", KMA_TD_NOW_URL, None, settings.typ_number if stage == "TD" else settings.linked_td_number)
    return candidates


def fetch_kma_now_analysis_point(session: requests.Session, settings: Settings) -> AnalysisPoint | None:
    for label, endpoint, query_number, filter_number in kma_now_endpoint_candidates(settings):
        url = kma_now_url(settings, endpoint, query_number)
        text = fetch_kma_text(
            session,
            url,
            kma_now_fallback_url(settings, endpoint, query_number),
            label=label,
            retries=2,
            timeout=10,
            retry_delay=2,
            encoding="cp949",
            cache_dir=settings.http_cache_dir,
            cache_ttl_seconds=settings.http_cache_ttl_seconds,
        )
        point = kma_now_point_from_text(
            text,
            settings=settings,
            typ_number=filter_number,
            require_number_match=query_number is None,
        )
        if point is None:
            continue
        number_label = "all" if query_number is None else f"{query_number:02d}"
        print(
            "KMA 0h is missing from typ_gts_now; using "
            f"{label} mode=0 analysis point ({number_label}) "
            f"{point.lat:.2f}N, {point.lon:.2f}E."
        )
        return point
    return None



def http_cache_path(cache_dir: Path | None, url: str) -> Path | None:
    if cache_dir is None:
        return None
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
    return cache_dir / "http" / f"{digest}.txt"


def read_cached_text(cache_path: Path | None, *, ttl_seconds: int) -> str | None:
    if cache_path is None or not cache_path.exists():
        return None
    try:
        if ttl_seconds > 0 and time.time() - cache_path.stat().st_mtime > ttl_seconds:
            return None
        return cache_path.read_text(encoding="utf-8")
    except OSError:
        return None


def write_cached_text(cache_path: Path | None, text: str) -> None:
    if cache_path is None:
        return
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = cache_path.with_name(f".{cache_path.name}.{os.getpid()}.tmp")
        tmp_path.write_text(text, encoding="utf-8")
        tmp_path.replace(cache_path)
    except OSError as exc:
        print(f"Warning: failed to write HTTP cache {cache_path}: {exc}")


def read_text_file(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Warning: failed to read pre-fetched text {path}: {exc}")
        return None


def log_timing(label: str, started_at: float, **details) -> None:
    suffix = " ".join(f"{key}={value}" for key, value in details.items())
    print(f"[timing] {label}: {time.monotonic() - started_at:.1f}s{(' ' + suffix) if suffix else ''}")


def fetch_text(
    session: requests.Session,
    url: str,
    *,
    retries: int = 3,
    timeout: float = 8,
    retry_delay: float = 1.0,
    encoding: str | None = None,
    cache_dir: Path | None = None,
    cache_ttl_seconds: int = 6 * 3600,
) -> str | None:
    cache_path = http_cache_path(cache_dir, url)
    cached = read_cached_text(cache_path, ttl_seconds=cache_ttl_seconds)
    if cached is not None:
        print(f"Using cached HTTP response: {url}")
        return cached

    for attempt in range(1, retries + 1):
        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            if encoding:
                response.encoding = encoding
            text = response.text
            write_cached_text(cache_path, text)
            return text
        except requests.exceptions.HTTPError as exc:
            print(f"[attempt {attempt}/{retries}] request failed: {url} ({exc})")
            status_code = exc.response.status_code if exc.response is not None else None
            if status_code is not None and 400 <= status_code < 500 and status_code not in {408, 429}:
                break
            if attempt < retries:
                time.sleep(retry_delay)
        except requests.exceptions.RequestException as exc:
            print(f"[attempt {attempt}/{retries}] request failed: {url} ({exc})")
            if attempt < retries:
                time.sleep(retry_delay)
    return None


def fetch_kma_text(
    session: requests.Session,
    primary_url: str,
    fallback_url: str,
    *,
    label: str,
    retries: int = 3,
    timeout: float = 8,
    retry_delay: float = 1.0,
    encoding: str | None = None,
    cache_dir: Path | None = None,
    cache_ttl_seconds: int = 6 * 3600,
) -> str | None:
    text = fetch_text(
        session,
        primary_url,
        retries=retries,
        timeout=timeout,
        retry_delay=retry_delay,
        encoding=encoding,
        cache_dir=cache_dir,
        cache_ttl_seconds=cache_ttl_seconds,
    )
    if text is not None or not fallback_url:
        return text
    print(f"KMA APIHUB {label} primary endpoint unavailable; trying fallback endpoint.")
    return fetch_text(
        session,
        fallback_url,
        retries=retries,
        timeout=timeout,
        retry_delay=retry_delay,
        encoding=encoding,
        cache_dir=cache_dir,
        cache_ttl_seconds=cache_ttl_seconds,
    )


def atcf_cycle_from_line(line: str) -> str:
    parts = line.split(",", 3)
    return parts[2].strip() if len(parts) >= 3 else ""


def filter_atcf_cycle_text(text: str, target_cycle: str) -> tuple[str, list[str]]:
    lines = text.splitlines()
    cycles = [cycle for line in lines if (cycle := atcf_cycle_from_line(line)).isdigit() and len(cycle) == 10]
    selected = [line for line in lines if atcf_cycle_from_line(line) == target_cycle]
    return ("\n".join(selected) + ("\n" if selected else "")), cycles


def fetch_recent_atcf_cycle_text(
    session: requests.Session,
    url: str,
    target_cycle: str,
    *,
    cache_dir: Path | None,
    cache_ttl_seconds: int,
    timeout: float = 15,
) -> str | None:
    cycle_cache_path = http_cache_path(cache_dir, f"{url}#cycle={target_cycle}")
    cached = read_cached_text(cycle_cache_path, ttl_seconds=cache_ttl_seconds)
    if cached is not None:
        return cached

    try:
        head = session.head(url, timeout=timeout, allow_redirects=True)
        head.raise_for_status()
        content_length = int(head.headers.get("Content-Length") or 0)
        supports_ranges = "bytes" in str(head.headers.get("Accept-Ranges") or "").lower()
    except (requests.exceptions.RequestException, TypeError, ValueError):
        return None

    if not supports_ranges or content_length <= ATCF_RECENT_RANGE_BYTES:
        return None

    range_start = max(0, content_length - ATCF_RECENT_RANGE_BYTES)
    try:
        response = session.get(
            url,
            headers={"Range": f"bytes={range_start}-{content_length - 1}"},
            timeout=timeout,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return None
    if response.status_code != 206:
        return None

    selected_text, cycles = filter_atcf_cycle_text(response.content.decode("utf-8", errors="replace"), target_cycle)
    if not cycles:
        return None
    minimum_cycle = min(cycles)
    maximum_cycle = max(cycles)
    has_complete_lower_boundary = range_start == 0 or minimum_cycle < target_cycle
    has_complete_upper_boundary = (
        maximum_cycle > target_cycle
        or response.headers.get("Content-Range", "").endswith(f"/{content_length}")
    )
    if selected_text:
        if has_complete_lower_boundary and has_complete_upper_boundary:
            write_cached_text(cycle_cache_path, selected_text)
            return selected_text
        return None
    if minimum_cycle <= target_cycle <= maximum_cycle or target_cycle > maximum_cycle:
        write_cached_text(cycle_cache_path, "")
        return ""
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
        df[MODEL_ALIAS_PRIORITY_COLUMN] = (
            df["SRC"].map(MODEL_ALIAS_PRIORITIES).fillna(0).astype(int)
        )
        df["SRC"] = df["SRC"].replace(MODEL_SOURCE_ALIASES)
    else:
        df[MODEL_ALIAS_PRIORITY_COLUMN] = 0

    df[DATA_SOURCE_COLUMN] = "APIHUB"
    return df


def kma_data_typ_number(settings: Settings) -> int:
    return settings.data_typ_number or settings.typ_number


def dmdw_data_root() -> Path:
    return PROJECT_ROOT / "data" / "dmdw"


def dmdw_cycle_key(settings: Settings) -> str:
    return settings.data_time[:10]


def dmdw_storm_key_aliases(settings: Settings) -> set[str]:
    year = storm_year(settings)
    aliases = {key.lower() for key in storm_history_keys(settings) if key}
    aliases.add(f"{settings.storm_stage.lower()}_{year}_{settings.typ_number:02d}")
    aliases.add(f"typ_{year}_{kma_data_typ_number(settings):02d}")
    if settings.linked_typ_number:
        aliases.add(f"typ_{year}_{settings.linked_typ_number:02d}")
    if settings.linked_td_number:
        aliases.add(f"td_{year}_{settings.linked_td_number:02d}")
    return aliases


def dmdw_candidate_paths(settings: Settings) -> list[Path]:
    root = dmdw_data_root()
    year = settings.data_time[:4]
    cycle = dmdw_cycle_key(settings)
    cycle_dir = root / year / cycle
    aliases = dmdw_storm_key_aliases(settings)

    direct_paths = [
        cycle_dir / f"{alias}.json"
        for alias in sorted(aliases)
        if alias.startswith(("typ_", "td_"))
    ]
    existing = [path for path in direct_paths if path.exists()]
    if existing:
        return existing

    index_path = root / "index.json"
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    rels = index.get("cycles", {}).get(f"{year}/{cycle}", [])
    paths: list[Path] = []
    for rel in rels if isinstance(rels, list) else []:
        path = root / str(rel)
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        storm_key = str((payload.get("storm") or {}).get("storm_key") or "").lower()
        if storm_key in aliases:
            paths.append(path)
    return paths


def dmdw_value(row: list, column_index: dict[str, int], column: str):
    index = column_index.get(column)
    if index is None or index >= len(row):
        return None
    return row[index]


def read_dmdw_json(path: Path, settings: Settings) -> pd.DataFrame:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Warning: failed to read DMDW source {path}: {exc}")
        return pd.DataFrame(columns=[*KMA_COLUMNS, DATA_SOURCE_COLUMN])

    if payload.get("schema_version") != 2 or payload.get("source") != "DMDW":
        print(f"Warning: unsupported DMDW schema in {path}")
        return pd.DataFrame(columns=[*KMA_COLUMNS, DATA_SOURCE_COLUMN])

    cycle_utc = str(payload.get("cycle_utc") or settings.data_time)
    point_columns = payload.get("point_columns") or []
    points = payload.get("points") or []
    models = payload.get("models") or []
    if not isinstance(point_columns, list) or not isinstance(points, list) or not isinstance(models, list):
        return pd.DataFrame(columns=[*KMA_COLUMNS, DATA_SOURCE_COLUMN])

    column_index = {str(column): idx for idx, column in enumerate(point_columns)}
    rows: list[dict] = []
    for point in points:
        if not isinstance(point, list):
            continue
        model_index = dmdw_value(point, column_index, "model_index")
        if not isinstance(model_index, int) or not (0 <= model_index < len(models)):
            continue
        model = models[model_index] if isinstance(models[model_index], dict) else {}
        member_id = model.get("member_id")
        if member_id not in (None, "", "MEAN"):
            continue

        raw_model_id = str(model.get("model_id") or "").strip()
        model_id = MODEL_SOURCE_ALIASES.get(raw_model_id, raw_model_id)
        if model_id not in MODEL_NAMES:
            continue
        lead_hour = dmdw_value(point, column_index, "lead_hour")
        if not isinstance(lead_hour, int) or lead_hour < 0 or lead_hour > settings.fcst_hours:
            continue
        valid_time = str(dmdw_value(point, column_index, "valid_time") or "")
        rows.append({
            "FT": 1 if lead_hour > 0 else 0,
            "YY": int(settings.data_time[:4]),
            "TYP": kma_data_typ_number(settings),
            "SEQ": lead_hour,
            "TMD": lead_hour,
            "TYP_TM(UTC)": cycle_utc,
            "FT_TM(UTC)": valid_time,
            "LAT": dmdw_value(point, column_index, "lat"),
            "LON": dmdw_value(point, column_index, "lon"),
            "DIR": dmdw_value(point, column_index, "direction"),
            "SP": dmdw_value(point, column_index, "speed"),
            "PS": dmdw_value(point, column_index, "pressure_hpa"),
            "WS": dmdw_value(point, column_index, "wind"),
            "T15": dmdw_value(point, column_index, "radius_15"),
            "T25": "",
            "RAD": "",
            "15D": "",
            "15R": "",
            "SRC": model_id,
            RAW_MODEL_COLUMN: str(model.get("raw_model_id") or model_id),
            DATA_SOURCE_COLUMN: "DMDW",
            MODEL_ALIAS_PRIORITY_COLUMN: 0,
            "": "",
        })

    if not rows:
        return pd.DataFrame(columns=[*KMA_COLUMNS, RAW_MODEL_COLUMN, DATA_SOURCE_COLUMN, MODEL_ALIAS_PRIORITY_COLUMN])

    df = pd.DataFrame(rows)
    for column in ("TMD", "LAT", "LON", "DIR", "SP", "PS", "WS", "T15", "SEQ"):
        if column in df:
            df[column] = pd.to_numeric(df[column], errors="coerce")
    df = df.dropna(subset=["TMD", "FT_TM(UTC)", "LAT", "LON"])
    return df


def read_dmdw_data(settings: Settings) -> pd.DataFrame:
    frames = []
    for path in dmdw_candidate_paths(settings):
        frame = read_dmdw_json(path, settings)
        if not frame.empty:
            print(f"Loaded DMDW source data: {relative_project_path(path)} rows={len(frame)}")
            frames.append(frame)
    if not frames:
        return pd.DataFrame(columns=[*KMA_COLUMNS, RAW_MODEL_COLUMN, DATA_SOURCE_COLUMN, MODEL_ALIAS_PRIORITY_COLUMN])
    return pd.concat(frames, ignore_index=True, sort=False)


def storm_numbers(settings: Settings) -> set[int]:
    ids = (settings.atcf_id, *settings.extra_atcf_ids)
    return {int(atcf_id[2:4]) for atcf_id in ids}


def raw_github_url(settings: Settings, model: str) -> str:
    data_dt = datetime.strptime(settings.data_time, "%Y%m%d%H%M")
    date_path = data_dt.strftime("%Y_%m_%d")
    init_time = data_dt.strftime("%Y_%m_%dT%H_00")
    return (
        "https://raw.githubusercontent.com/SSalKim/GDM/main/"
        f"forecast_files/{date_path}/{model}_{init_time}_atcf_a_deck.txt"
    )


def polarwx_url(atcf_id: str, data_time: str) -> str:
    atcf_id = str(atcf_id or "").strip().lower()
    cycle = normalize_utc_stamp(data_time)[:10]
    return f"https://polarwx.com/data/tropical/storms/{atcf_id}/ensembles/{cycle}.json"


def polarwx_keys() -> dict[str, str]:
    return {
        str(row.get("polarwx") or "").strip().lower(): row["name"]
        for row in MODEL_SOURCES
        if str(row.get("polarwx") or "").strip()
    }


def empty_polarwx_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=[*KMA_COLUMNS, RAW_MODEL_COLUMN, DATA_SOURCE_COLUMN, MODEL_ALIAS_PRIORITY_COLUMN])


def polarwx_value(values, index: int):
    if isinstance(values, list) and 0 <= index < len(values):
        return values[index]
    return None


def read_polarwx_json(text: str | None, settings: Settings, *, atcf_id: str = "") -> pd.DataFrame:
    if not text or not text.strip():
        return empty_polarwx_frame()
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        print(f"Warning: failed to parse POLARWX JSON for {atcf_id or settings.atcf_id}: {exc}")
        return empty_polarwx_frame()
    if not isinstance(payload, dict):
        return empty_polarwx_frame()

    lookup = {str(key).strip().lower(): value for key, value in payload.items()}
    rows: list[dict] = []
    cycle_utc = normalize_utc_stamp(settings.data_time)
    for source_key, model_name in polarwx_keys().items():
        model = lookup.get(source_key)
        if not isinstance(model, dict):
            continue
        fhrs = model.get("fhr")
        lats = model.get("lat")
        lons = model.get("lon")
        if not all(isinstance(values, list) for values in (fhrs, lats, lons)):
            continue
        count = min(len(fhrs), len(lats), len(lons))
        for index in range(count):
            lead_hour = pd.to_numeric(polarwx_value(fhrs, index), errors="coerce")
            lat = pd.to_numeric(polarwx_value(lats, index), errors="coerce")
            lon = pd.to_numeric(polarwx_value(lons, index), errors="coerce")
            if pd.isna(lead_hour) or pd.isna(lat) or pd.isna(lon):
                continue
            lead_hour = float(lead_hour)
            if lead_hour < 0 or lead_hour > settings.fcst_hours:
                continue
            valid_time = normalize_utc_stamp(str(polarwx_value(model.get("time"), index) or ""))
            if not valid_time and cycle_utc:
                valid_dt = datetime.strptime(cycle_utc, "%Y%m%d%H%M") + timedelta(hours=lead_hour)
                valid_time = valid_dt.strftime("%Y%m%d%H%M")
            pressure = pd.to_numeric(polarwx_value(model.get("mslp"), index), errors="coerce")
            wind_kt = pd.to_numeric(polarwx_value(model.get("vmax"), index), errors="coerce")
            rows.append({
                "FT": 1 if lead_hour > 0 else 0,
                "YY": int(settings.data_time[:4]),
                "TYP": settings.typ_number,
                "SEQ": lead_hour,
                "TMD": lead_hour,
                "TYP_TM(UTC)": cycle_utc,
                "FT_TM(UTC)": valid_time,
                "LAT": float(lat),
                "LON": float(lon),
                "DIR": "",
                "SP": "",
                "PS": None if pd.isna(pressure) else float(pressure),
                "WS": None if pd.isna(wind_kt) else round(float(wind_kt) * MS_PER_KT),
                "T15": "",
                "T25": "",
                "RAD": "",
                "15D": "",
                "15R": "",
                "SRC": model_name,
                RAW_MODEL_COLUMN: source_key.upper(),
                DATA_SOURCE_COLUMN: "POLARWX",
                MODEL_ALIAS_PRIORITY_COLUMN: 0,
                "": "",
            })

    if not rows:
        return empty_polarwx_frame()
    df = pd.DataFrame(rows)
    for column in ("TMD", "LAT", "LON", "PS", "WS", "SEQ"):
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df = df.dropna(subset=["TMD", "FT_TM(UTC)", "LAT", "LON"])
    df = df.drop_duplicates(subset=["SRC", "TMD", "FT_TM(UTC)", "LAT", "LON"], keep="first")
    return df.reset_index(drop=True)


def fetch_polarwx_data(session: requests.Session, settings: Settings) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for atcf_id in dict.fromkeys((settings.atcf_id, *settings.extra_atcf_ids)):
        if not atcf_id:
            continue
        url = polarwx_url(atcf_id, settings.data_time)
        text = fetch_text(
            session,
            url,
            retries=1,
            timeout=10,
            cache_dir=settings.http_cache_dir,
            cache_ttl_seconds=settings.http_cache_ttl_seconds,
        )
        frame = read_polarwx_json(text, settings, atcf_id=atcf_id)
        if not frame.empty:
            print(f"Loaded POLARWX source data: {atcf_id} rows={len(frame)}")
            frames.append(frame)
    if not frames:
        return empty_polarwx_frame()
    return pd.concat(frames, ignore_index=True, sort=False).drop_duplicates(
        subset=["SRC", "TMD", "FT_TM(UTC)", "LAT", "LON"],
        keep="first",
    )


def smca_typhoon_id(settings: Settings) -> str:
    if canonical_storm_stage(settings) != "TYP":
        return ""
    return f"{storm_year(settings)}{canonical_typ_number(settings):02d}"


def smca_url(settings: Settings) -> str:
    typhoon_id = smca_typhoon_id(settings)
    return f"{SMCA_TYPHOON_API_BASE}/?{urlencode({'typhoonId': typhoon_id})}" if typhoon_id else ""


def smca_keys() -> dict[str, str]:
    return {
        str(row.get("smca") or "").strip().upper(): row["name"]
        for row in MODEL_SOURCES
        if str(row.get("smca") or "").strip()
    }


def empty_smca_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=[*KMA_COLUMNS, RAW_MODEL_COLUMN, DATA_SOURCE_COLUMN, MODEL_ALIAS_PRIORITY_COLUMN])


def iso_datetime_stamp(value) -> str:
    timestamp = pd.to_datetime(value, errors="coerce")
    if pd.isna(timestamp):
        return ""
    if timestamp.tzinfo is not None:
        timestamp = timestamp.tz_convert("UTC").tz_localize(None)
    return timestamp.strftime("%Y%m%d%H%M")


def smca_forecast_cycle(forecast: dict) -> str:
    cycle = iso_datetime_stamp(forecast.get("init_time_utc"))
    if cycle:
        return cycle
    bjt = pd.to_datetime(forecast.get("init_time_bjt"), errors="coerce")
    if pd.isna(bjt):
        return ""
    return (bjt - pd.Timedelta(hours=8)).strftime("%Y%m%d%H%M")


def read_smca_json(text: str | None, settings: Settings, *, typhoon_id: str = "") -> pd.DataFrame:
    if not text or not text.strip():
        return empty_smca_frame()
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        print(f"Warning: failed to parse SMCA.FUN JSON for {typhoon_id}: {exc}")
        return empty_smca_frame()
    if not isinstance(payload, dict) or str(payload.get("code")) != "200":
        return empty_smca_frame()

    data = payload.get("data")
    if not isinstance(data, dict):
        return empty_smca_frame()
    response_id = str(data.get("ident") or data.get("tfbh") or "").strip()
    if typhoon_id and response_id != typhoon_id:
        print(f"Warning: SMCA.FUN storm mismatch: requested {typhoon_id}, received {response_id or 'unknown'}")
        return empty_smca_frame()

    target_cycle = normalize_utc_stamp(settings.data_time)
    model_lookup = smca_keys()
    rows: list[dict] = []
    matched_forecasts = 0
    for analysis_point in data.get("points") or []:
        if not isinstance(analysis_point, dict):
            continue
        for forecast in analysis_point.get("forecast") or []:
            if not isinstance(forecast, dict):
                continue
            raw_model = str(forecast.get("sets") or "").strip().upper()
            model_name = model_lookup.get(raw_model)
            if not model_name or smca_forecast_cycle(forecast) != target_cycle:
                continue
            matched_forecasts += 1
            for point in forecast.get("points") or []:
                if not isinstance(point, dict):
                    continue
                lead_hour = pd.to_numeric(point.get("forecastTime"), errors="coerce")
                lat = pd.to_numeric(point.get("lat"), errors="coerce")
                lon = pd.to_numeric(point.get("lng"), errors="coerce")
                if pd.isna(lead_hour) or pd.isna(lat) or pd.isna(lon):
                    continue
                lead_hour = float(lead_hour)
                if lead_hour < 0 or lead_hour > settings.fcst_hours:
                    continue
                valid_dt = datetime.strptime(target_cycle, "%Y%m%d%H%M") + timedelta(hours=lead_hour)
                pressure = pd.to_numeric(point.get("pressure"), errors="coerce")
                wind_ms = pd.to_numeric(point.get("speed"), errors="coerce")
                rows.append({
                    "FT": 1 if lead_hour > 0 else 0,
                    "YY": int(target_cycle[:4]),
                    "TYP": canonical_typ_number(settings),
                    "SEQ": lead_hour,
                    "TMD": lead_hour,
                    "TYP_TM(UTC)": target_cycle,
                    "FT_TM(UTC)": valid_dt.strftime("%Y%m%d%H%M"),
                    "LAT": float(lat),
                    "LON": float(lon),
                    "DIR": "",
                    "SP": "",
                    "PS": None if pd.isna(pressure) else float(pressure),
                    "WS": None if pd.isna(wind_ms) else float(wind_ms),
                    "T15": "",
                    "T25": "",
                    "RAD": "",
                    "15D": "",
                    "15R": "",
                    "SRC": model_name,
                    RAW_MODEL_COLUMN: raw_model,
                    DATA_SOURCE_COLUMN: "SMCA.FUN",
                    MODEL_ALIAS_PRIORITY_COLUMN: 0,
                    "": "",
                })

    if not rows:
        if matched_forecasts == 0:
            print(f"SMCA.FUN has no AIGEFSM/AICON forecast initialized at {target_cycle} for {typhoon_id}")
        return empty_smca_frame()
    frame = pd.DataFrame(rows)
    for column in ("TMD", "LAT", "LON", "PS", "WS", "SEQ"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame = frame.dropna(subset=["TMD", "FT_TM(UTC)", "LAT", "LON"])
    return frame.drop_duplicates(subset=["SRC", "TMD", "LAT", "LON"], keep="first").reset_index(drop=True)


def fetch_smca_data(session: requests.Session, settings: Settings) -> pd.DataFrame:
    typhoon_id = smca_typhoon_id(settings)
    url = smca_url(settings)
    if not typhoon_id or not url:
        return empty_smca_frame()
    text = fetch_text(
        session,
        url,
        retries=1,
        timeout=10,
        cache_dir=settings.http_cache_dir,
        cache_ttl_seconds=settings.http_cache_ttl_seconds,
    )
    frame = read_smca_json(text, settings, typhoon_id=typhoon_id)
    if not frame.empty:
        print(f"Loaded SMCA.FUN source data: {typhoon_id} rows={len(frame)}")
    return frame


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


def ral_ucar_url(atcf_id: str) -> str:
    atcf_id = str(atcf_id or "").strip().lower()
    year = atcf_id[-4:]
    return (
        "https://hurricanes.ral.ucar.edu/realtime/plots/"
        f"{ral_ucar_basin_dir(atcf_id)}/{year}/{atcf_id}/a{atcf_id}.dat"
    )


def knackwx_storm_id(atcf_id: str) -> str:
    atcf_id = str(atcf_id or "").strip().lower()
    basin_suffixes = {
        "wp": "W",
        "al": "L",
        "ep": "E",
        "cp": "C",
        "io": "A",
        "sh": "S",
    }
    if len(atcf_id) < 4 or atcf_id[:2] not in basin_suffixes or not atcf_id[2:4].isdigit():
        return ""
    return f"{atcf_id[2:4]}{basin_suffixes[atcf_id[:2]]}"


def knackwx_url(atcf_id: str, data_time: str) -> str:
    storm_id = knackwx_storm_id(atcf_id)
    if not storm_id:
        return ""
    query = urlencode({
        "stormID": storm_id,
        "cycle": "late",
        "initTime": f"{data_time[8:10]}z",
    })
    return f"https://api.knackwx.com/atcf/v2/aid/archive?{query}"


def bdeck_url(atcf_id: str) -> str:
    atcf_id = str(atcf_id or "").strip().lower()
    return f"https://www.emc.ncep.noaa.gov/gc_wmb/vxt/DECKS/b{atcf_id}.dat"


def ral_ucar_bdeck_url(atcf_id: str) -> str:
    atcf_id = str(atcf_id or "").strip().lower()
    year = atcf_id[-4:]
    return (
        "https://hurricanes.ral.ucar.edu/realtime/plots/"
        f"{ral_ucar_basin_dir(atcf_id)}/{year}/{atcf_id}/b{atcf_id}.dat"
    )


def natyphoon_bdeck_url(atcf_id: str) -> str:
    atcf_id = str(atcf_id or "").strip().lower()
    return f"https://www.natyphoon.top/atcf/temp/b{atcf_id}.dat"


def atcf_urls(settings: Settings) -> list[tuple[str, str, int]]:
    urls = []
    for atcf_id in dict.fromkeys((settings.atcf_id, *settings.extra_atcf_ids)):
        urls.append(("RAL.UCAR", ral_ucar_url(atcf_id), 0))
    for atcf_id in dict.fromkeys((settings.atcf_id, *settings.extra_atcf_ids)):
        if url := knackwx_url(atcf_id, settings.data_time):
            urls.append(("KNACKWX", url, 0))
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


def trim_knackwx_dateline_crossings(df: pd.DataFrame) -> pd.DataFrame:
    """Trim a KNACKWX model track before it crosses from 170E+ to 170W+."""
    if df.empty or "LONG" not in df or "FTM" not in df:
        return df

    longitude = df["LONG"].astype("string").str.strip().str.upper()
    hemisphere = longitude.str[-1]
    magnitude = pd.to_numeric(longitude.str[:-1], errors="coerce") / 10
    work = df.assign(_LON_HEMISPHERE=hemisphere, _LON_MAGNITUDE=magnitude)
    keep = pd.Series(True, index=df.index, dtype=bool)
    group_columns = ["ATCF_BASIN", "ATCF_NUMBER", "TM10", "MODEL"]

    for _, group in work.groupby(group_columns, dropna=False, sort=False):
        leads = pd.to_numeric(group["FTM"], errors="coerce")
        east_leads = leads[
            group["_LON_HEMISPHERE"].eq("E")
            & group["_LON_MAGNITUDE"].ge(170)
        ].dropna()
        west_leads = leads[
            group["_LON_HEMISPHERE"].eq("W")
            & group["_LON_MAGNITUDE"].ge(170)
        ].dropna()
        if east_leads.empty or west_leads.empty:
            continue

        crossing_leads = [
            float(west_lead)
            for west_lead in west_leads.unique()
            if east_leads.lt(west_lead).any()
        ]
        if not crossing_leads:
            continue

        crossing_lead = min(crossing_leads)
        previous_lead = float(east_leads[east_leads.lt(crossing_lead)].max())
        keep.loc[group.index[leads.ge(crossing_lead)]] = False
        print(
            f"{group['MODEL'].iloc[0]} KNACKWX: trimmed after {previous_lead:g}h "
            f"before dateline crossing at {crossing_lead:g}h."
        )

    return df.loc[keep].copy()


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
    if source == "KNACKWX":
        df = trim_knackwx_dateline_crossings(df)
    df["LATI"] = parse_atcf_coord(df["LATI"])
    df["LONG"] = parse_atcf_coord(df["LONG"])
    df[DATA_SOURCE_COLUMN] = source
    valid = (
        df["ATCF_NUMBER"].between(1, 99)
        & df["TM10"].between(1900010100, 2200010100)
        & df["FTM"].between(0, max(CLI_FCST_HOURS))
        & df["LATI"].between(-90, 90)
        & df["LONG"].between(-180, 180)
        & df["MODEL"].astype(str).str.strip().ne("")
    )
    return (
        df.loc[valid]
        .drop_duplicates(
            subset=["ATCF_BASIN", "ATCF_NUMBER", "TM10", "MODEL", "FTM", "LATI", "LONG"],
            keep="first",
        )
        .reset_index(drop=True)
    )


def fetch_atcf_data(session: requests.Session, settings: Settings) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    url_specs = atcf_urls(settings)
    target_cycle = settings.data_time[:10]

    def fetch_source(source: str, url: str) -> str | None:
        if source in {"NOAA", "RAL.UCAR"}:
            recent_text = fetch_recent_atcf_cycle_text(
                session,
                url,
                target_cycle,
                cache_dir=settings.http_cache_dir,
                cache_ttl_seconds=settings.http_cache_ttl_seconds,
            )
            if recent_text is not None:
                return recent_text
        is_knackwx = source == "KNACKWX"
        return fetch_text(
            session,
            url,
            retries=1 if is_knackwx else 2,
            timeout=15,
            # This endpoint has no date in its URL and replaces same-hour data
            # daily, so a persistent cache could replay yesterday's cycle.
            cache_dir=None if is_knackwx else settings.http_cache_dir,
            cache_ttl_seconds=settings.http_cache_ttl_seconds,
        )

    with ThreadPoolExecutor(max_workers=min(8, len(url_specs))) as executor:
        futures = {
            executor.submit(fetch_source, source, url): (source, url, skiprows, time.monotonic())
            for source, url, skiprows in url_specs
        }
        for future in as_completed(futures):
            source, url, skiprows, started_at = futures[future]
            try:
                frame = read_atcf_csv(future.result(), source=source, skiprows=skiprows)
                log_timing(
                    f"ATCF source {source}",
                    started_at,
                    rows=len(frame),
                    file=url.rsplit("/", 1)[-1],
                )
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


def kma_has_current_track_point(kma_df: pd.DataFrame) -> bool:
    if kma_df.empty:
        return False
    if "SRC" not in kma_df or "TMD" not in kma_df:
        return False
    start = kma_df[(kma_df["SRC"].eq("KMA")) & (pd.to_numeric(kma_df["TMD"], errors="coerce").eq(0))]
    return not start.dropna(subset=["LAT", "LON"]).empty


def bdeck_analysis_candidates(text: str | None, settings: Settings, *, max_offset_hours: int = 12) -> pd.DataFrame:
    raw = read_atcf_csv(text, source="BDECK")
    if raw.empty:
        return raw

    for col in ["ATCF_NUMBER", "TM10", "FTM", "LATI", "LONG"]:
        raw[col] = pd.to_numeric(raw[col], errors="coerce")
    target_numbers = storm_numbers(settings)
    target_dt = datetime.strptime(settings.data_time[:10], "%Y%m%d%H").replace(tzinfo=timezone.utc)
    raw = raw[
        raw["ATCF_NUMBER"].isin(target_numbers)
        & raw["FTM"].eq(0)
        & raw["LATI"].notna()
        & raw["LONG"].notna()
    ].copy()
    if raw.empty:
        return raw

    raw["_time"] = pd.to_datetime(raw["TM10"].astype("Int64").astype(str), format="%Y%m%d%H", errors="coerce", utc=True)
    raw = raw.dropna(subset=["_time"])
    if raw.empty:
        return raw
    raw["_offset_hours"] = (raw["_time"] - target_dt).abs().dt.total_seconds() / 3600.0
    raw = raw[raw["_offset_hours"].le(max_offset_hours)].sort_values("_offset_hours")
    return raw


def fetch_bdeck_analysis_candidates(
    session: requests.Session,
    settings: Settings,
    *,
    url: str,
    max_offset_hours: int,
) -> pd.DataFrame:
    text = fetch_text(
        session,
        url,
        retries=2,
        timeout=12,
        retry_delay=2,
        cache_dir=settings.http_cache_dir,
        cache_ttl_seconds=settings.http_cache_ttl_seconds,
    )
    return bdeck_analysis_candidates(text, settings, max_offset_hours=max_offset_hours)


def exact_bdeck_rows(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty or "_offset_hours" not in frame:
        return frame.iloc[0:0].copy()
    return frame[frame["_offset_hours"].le(0)].copy()


def select_bdeck_analysis_row(
    session: requests.Session,
    settings: Settings,
    *,
    max_offset_hours: int,
) -> tuple[pd.Series, str] | None:
    nearest_fallback: tuple[pd.Series, str] | None = None
    for source_name, url in (
        ("RAL.UCAR", ral_ucar_bdeck_url(settings.atcf_id)),
        ("NATYPHOON", natyphoon_bdeck_url(settings.atcf_id)),
    ):
        frame = fetch_bdeck_analysis_candidates(
            session,
            settings,
            url=url,
            max_offset_hours=max_offset_hours,
        )
        exact = exact_bdeck_rows(frame)
        if not exact.empty:
            return exact.iloc[0], source_name
        if nearest_fallback is None and not frame.empty:
            nearest_fallback = (frame.iloc[0], source_name)
    if nearest_fallback is not None:
        return nearest_fallback
    return None


def fetch_bdeck_analysis_point(session: requests.Session, settings: Settings, *, max_offset_hours: int = 12) -> AnalysisPoint | None:
    if settings.skip_atcf or not settings.atcf_id:
        return None

    selected = select_bdeck_analysis_row(session, settings, max_offset_hours=max_offset_hours)
    if selected is None:
        return None
    row, source_name = selected
    time_utc = row["_time"].strftime("%Y%m%d%H%M")
    if row["_offset_hours"] > 0:
        print(
            f"KMA current track is missing; using nearest {source_name} BDECK/bwp analysis point "
            f"{time_utc} for {settings.atcf_id} at {settings.data_time}."
        )
    else:
        print(
            f"KMA current track is missing; using {source_name} BDECK/bwp analysis point "
            f"for {settings.atcf_id} at {settings.data_time}."
        )
    return AnalysisPoint(
        time_utc=time_utc,
        lat=float(row["LATI"]),
        lon=float(row["LONG"]),
        source="BDECK",
        atcf_id=settings.atcf_id,
        match_method=f"{source_name.lower().replace('.', '_')}_bdeck_fallback",
        distance_km=None,
    )


def settings_with_bdeck_analysis_if_needed(session: requests.Session, settings: Settings, kma_df: pd.DataFrame) -> Settings:
    if cli_analysis_point(settings) is not None:
        return settings
    if kma_has_current_track_point(kma_df):
        return settings
    kma_now_point = fetch_kma_now_analysis_point(session, settings)
    if kma_now_point is not None:
        return replace(
            settings,
            analysis_lat=kma_now_point.lat,
            analysis_lon=kma_now_point.lon,
            analysis_time=kma_now_point.time_utc,
            analysis_source=kma_now_point.source,
            analysis_atcf_id=kma_now_point.atcf_id,
            analysis_match_method=kma_now_point.match_method,
            analysis_distance_km=kma_now_point.distance_km,
        )
    analysis = fetch_bdeck_analysis_point(session, settings)
    if analysis is None:
        return settings
    return replace(
        settings,
        analysis_lat=analysis.lat,
        analysis_lon=analysis.lon,
        analysis_time=analysis.time_utc,
        analysis_source=analysis.source,
        analysis_atcf_id=analysis.atcf_id,
        analysis_match_method=analysis.match_method,
        analysis_distance_km=analysis.distance_km,
    )


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
        RAW_MODEL_COLUMN: raw["MODEL"].astype(str),
        DATA_SOURCE_COLUMN: raw[DATA_SOURCE_COLUMN],
        "": "",
    })
    return converted.dropna(subset=["FT_TM(UTC)", "LAT", "LON"])


def parse_ft_time(series: pd.Series) -> pd.Series:
    clean = series.astype("string").str.split(".", n=1).str[0]
    return pd.to_datetime(clean, format="%Y%m%d%H%M", errors="coerce")


def history_time_to_datetime(value: str) -> datetime | None:
    text = normalize_utc_stamp(value)
    if not text:
        return None
    try:
        return datetime.strptime(text, "%Y%m%d%H%M").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def clean_history_alias(alias: str) -> str:
    text = str(alias or "").strip().lower()
    if not text or text == "track_history":
        return ""
    return text


def analysis_source_priority(source: str) -> int:
    return ANALYSIS_SOURCE_PRIORITY.get(str(source or "").strip().upper(), 0)


def storm_history_keys(settings: Settings) -> list[str]:
    year = storm_year(settings)
    keys: list[str] = []

    def add(key: str) -> None:
        if key and key not in keys:
            keys.append(key)

    add(canonical_storm_key(settings))
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
    return [system_metadata_dir(settings) / "track_history.json"]


def history_aliases(settings: Settings) -> list[str]:
    aliases: list[str] = []
    for key in storm_history_keys(settings):
        alias = clean_history_alias(key)
        if alias and alias not in aliases:
            aliases.append(alias)
    for atcf_id in (settings.atcf_id, *settings.extra_atcf_ids):
        atcf_id = clean_history_alias(atcf_id)
        if atcf_id and not settings.skip_atcf and atcf_id not in aliases:
            aliases.append(atcf_id)
    return aliases


def empty_track_history(settings: Settings) -> dict:
    keys = storm_history_keys(settings)
    return {
        "version": 1,
        "year": storm_year(settings),
        "primary_key": canonical_storm_key(settings),
        "aliases": history_aliases(settings),
        "points": [],
    }


def load_track_history(settings: Settings) -> dict:
    history = empty_track_history(settings)
    requested_aliases = set(history_aliases(settings))
    loaded_paths: set[Path] = set()

    def merge_payload(path: Path, *, require_alias_match: bool) -> None:
        if path in loaded_paths or not path.exists():
            return
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        if not isinstance(payload, dict):
            return

        payload_aliases: set[str] = set()
        primary_key = str(payload.get("primary_key") or "").strip()
        primary_key = clean_history_alias(primary_key)
        if primary_key:
            payload_aliases.add(primary_key)
        for alias in payload.get("aliases", []):
            alias = clean_history_alias(alias)
            if alias:
                payload_aliases.add(alias)

        if require_alias_match and not (requested_aliases & payload_aliases):
            return

        loaded_paths.add(path)
        for alias in payload_aliases:
            if alias and alias not in history["aliases"]:
                history["aliases"].append(alias)
        for point in payload.get("points", []):
            if isinstance(point, dict):
                upsert_history_point(history, point)

    for path in track_history_paths(settings):
        merge_payload(path, require_alias_match=False)

    # Backward compatibility: older runs wrote linked TYP history only to the
    # linked TD file, or vice versa. Scan sibling history files by alias so a
    # TYP -> TD or TD -> TYP phase transition keeps the old past track.
    base = settings.output_root / storm_year(settings)
    if base.exists():
        for path in sorted(base.glob("*/metadata/track_history.json")):
            merge_payload(path, require_alias_match=True)

    return history


def history_point_payload(point: AnalysisPoint) -> dict:
    payload = {
        "time_utc": normalize_utc_stamp(point.time_utc),
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
    payload["time_utc"] = normalize_utc_stamp(str(payload.get("time_utc") or ""))
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
        if normalize_utc_stamp(str(existing.get("time_utc") or "")) != payload["time_utc"]:
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


def filter_history_points_for_settings(settings: Settings, points: list[dict]) -> list[dict]:
    current_dt = history_time_to_datetime(settings.data_time)
    if current_dt is None:
        return points
    min_dt = current_dt - timedelta(days=TRACK_HISTORY_MAX_LOOKBACK_DAYS)
    max_dt = current_dt + timedelta(hours=6)
    filtered: list[dict] = []
    for point in points:
        point_dt = history_time_to_datetime(str(point.get("time_utc") or ""))
        if point_dt is None:
            continue
        if min_dt <= point_dt <= max_dt:
            filtered.append(point)
    return filtered


def save_track_history(settings: Settings, history: dict, *, original: dict) -> None:
    aliases = {
        alias
        for alias in (
            clean_history_alias(item)
            for item in [*history.get("aliases", []), *history_aliases(settings)]
        )
        if alias
    }
    history["aliases"] = sorted(aliases)
    history["points"] = sorted(
        filter_history_points_for_settings(settings, history.get("points", [])),
        key=lambda item: normalize_utc_stamp(str(item.get("time_utc") or "")),
    )
    if history == original:
        return
    history["updated_at_utc"] = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    payload = json.dumps(history, ensure_ascii=False, indent=2) + "\n"
    paths = track_history_paths(settings)
    if not paths:
        return
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload, encoding="utf-8")


def cli_analysis_point(settings: Settings) -> AnalysisPoint | None:
    if settings.analysis_lat is None or settings.analysis_lon is None:
        return None
    time_utc = normalize_utc_stamp(settings.analysis_time or settings.data_time)
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
        time_utc=normalize_utc_stamp(str(row.get("FT_TM(UTC)") or settings.data_time)),
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
        time_utc = normalize_utc_stamp(str(row.get("FT_TM(UTC)") or ""))
        if not time_utc:
            continue
        points.append(AnalysisPoint(time_utc=time_utc, lat=lat, lon=lon, source="KMA_OFFICIAL"))
    return points


def history_to_past_track(history: dict, current_dt: datetime | None) -> pd.DataFrame:
    rows = []
    for point in history.get("points", []):
        time_utc = normalize_utc_stamp(str(point.get("time_utc") or ""))
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


def trim_knackwx_forecast_gaps(group: pd.DataFrame, *, max_gap_hours: float = KNACKWX_MAX_LEAD_GAP_HOURS) -> pd.DataFrame:
    """Drop the tail after KNACKWX skips more than the allowed lead interval."""
    clean = group.copy()
    clean["TMD"] = pd.to_numeric(clean["TMD"], errors="coerce")
    leads = sorted(clean["TMD"].dropna().unique())
    if leads and leads[0] > max_gap_hours:
        print(
            f"{clean['SRC'].iloc[0]} KNACKWX: "
            f"dropped because first forecast lead is {leads[0]:g}h "
            f"(>{max_gap_hours:g}h)."
        )
        return clean.iloc[0:0].copy()
    if len(leads) < 2:
        return clean

    for previous_lead, next_lead in zip(leads, leads[1:]):
        gap = next_lead - previous_lead
        if gap > max_gap_hours:
            print(
                f"{clean['SRC'].iloc[0]} KNACKWX: "
                f"trimmed after {previous_lead:g}h due to forecast gap to {next_lead:g}h "
                f"(>{max_gap_hours:g}h)."
            )
            return clean[clean["TMD"].le(previous_lead)].copy()
    return clean


def trim_discontinuous_forecast(group: pd.DataFrame, *, gap_factor: float = 2.5) -> pd.DataFrame:
    """Keep the first continuous forecast segment when late-hour outliers appear."""
    clean = group.copy()
    clean["TMD"] = pd.to_numeric(clean["TMD"], errors="coerce")
    if DATA_SOURCE_COLUMN in clean and clean[DATA_SOURCE_COLUMN].eq("KNACKWX").any():
        return trim_knackwx_forecast_gaps(clean)
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


def expected_raw_model_id(model_name: str, source_name: str) -> str:
    if source_name == "DMDW":
        return ""
    source_column = SOURCE_IDENTIFIER_COLUMNS.get(source_name)
    if not source_column:
        return ""
    for row in MODEL_SOURCES:
        if row.get("name") == model_name:
            return str(row.get(source_column) or "").strip()
    return ""


def normalized_raw_model_ids(model_name: str, source_name: str, observed_ids: Iterable[str]) -> list[str]:
    cleaned = sorted({
        str(value).strip()
        for value in observed_ids
        if str(value or "").strip()
    })
    expected = expected_raw_model_id(model_name, source_name)
    if expected and (not cleaned or cleaned == [model_name]):
        return [expected]
    return cleaned


def source_availability_point_count(group: pd.DataFrame) -> int:
    required_columns = ("TMD", "LAT", "LON")
    if group.empty:
        return 0
    if any(column not in group for column in required_columns):
        return int(len(group))
    point_frame = pd.DataFrame({
        "TMD": pd.to_numeric(group["TMD"], errors="coerce").round(3),
        "LAT": pd.to_numeric(group["LAT"], errors="coerce").round(4),
        "LON": pd.to_numeric(group["LON"], errors="coerce").round(4),
    }).dropna()
    if point_frame.empty:
        return int(len(group))
    return int(point_frame.drop_duplicates().shape[0])


def source_priority_for_model(model_name: str, settings: Settings) -> tuple[str, ...]:
    priority = list(MODEL_SOURCE_PRIORITY_OVERRIDES.get(model_name, SOURCE_ORDER))
    overrides = dict(settings.source_overrides)
    preferred_source = overrides.get(model_name)
    if preferred_source:
        priority = [preferred_source, *[source for source in priority if source != preferred_source]]
        priority.extend(source for source in SOURCE_ORDER if source not in priority)
    return tuple(priority)



def row_inside_120_domain(row: pd.Series) -> bool:
    try:
        lon = float(row["LON"])
        lat = float(row["LAT"])
    except (KeyError, TypeError, ValueError):
        return False
    return (
        DISPLAY_120_LON_MIN <= lon <= DISPLAY_120_LON_MAX
        and DISPLAY_120_LAT_MIN <= lat <= DISPLAY_120_LAT_MAX
    )


def clip_track_to_120_domain(track: pd.DataFrame) -> pd.DataFrame:
    if track.empty:
        return track
    clean = track.copy()
    clean["TMD"] = pd.to_numeric(clean["TMD"], errors="coerce")
    clean = clean.sort_values(["TMD", "FT_TM(UTC)", "SEQ"], kind="stable")
    keep_indices: list[int] = []
    has_inside = False
    crossed_out = False
    for idx, row in clean.iterrows():
        inside = row_inside_120_domain(row)
        if inside:
            if not crossed_out:
                keep_indices.append(idx)
                has_inside = True
            continue
        if has_inside and not crossed_out:
            # Keep the first point outside the display domain to draw the final
            # line segment to the boundary/outflow direction, then drop the tail.
            keep_indices.append(idx)
            crossed_out = True
            continue
        if not has_inside and not keep_indices:
            keep_indices.append(idx)
            crossed_out = True
    return clean.loc[keep_indices].copy() if keep_indices else clean.iloc[0:0].copy()


def clip_120_domain_tracks(df: pd.DataFrame, settings: Settings) -> pd.DataFrame:
    if df.empty or settings.fcst_hours != 120:
        return df
    frames: list[pd.DataFrame] = []
    for (model_name, source_name), track in df.groupby(["SRC", DATA_SOURCE_COLUMN], dropna=False):
        clipped = clip_track_to_120_domain(track)
        removed = len(track) - len(clipped)
        if removed > 0:
            print(
                f"{model_name} {source_display_name(str(source_name))}: "
                f"clipped {removed} point(s) outside 120h display domain "
                f"({DISPLAY_120_LON_MIN:g}-{DISPLAY_120_LON_MAX:g}E, "
                f"{DISPLAY_120_LAT_MIN:g}-{DISPLAY_120_LAT_MAX:g}N)."
            )
        if not clipped.empty:
            frames.append(clipped)
    return pd.concat(frames, ignore_index=True) if frames else df.iloc[0:0].copy()


def analysis_reference_point_from_df(df: pd.DataFrame, settings: Settings) -> tuple[float, float, str] | None:
    override = cli_analysis_point(settings)
    if override is not None:
        return override.lat, override.lon, override.source
    if df.empty:
        return None
    kma = df[(df["SRC"].eq("KMA")) & (pd.to_numeric(df["TMD"], errors="coerce").eq(0))]
    kma = kma.dropna(subset=["LAT", "LON"])
    if not kma.empty:
        row = kma.iloc[0]
        return float(row["LAT"]), float(row["LON"]), "KMA"
    return None


def filter_suspicious_apihub_model_starts(df: pd.DataFrame, settings: Settings) -> pd.DataFrame:
    if df.empty or DATA_SOURCE_COLUMN not in df.columns:
        return df
    reference = analysis_reference_point_from_df(df, settings)
    if reference is None:
        return df
    ref_lat, ref_lon, ref_source = reference
    keep_mask = pd.Series(True, index=df.index)
    removed: list[str] = []
    for model_name, model_df in df[df[DATA_SOURCE_COLUMN].eq("APIHUB")].groupby("SRC", dropna=True):
        if model_name == "KMA":
            continue
        clean = model_df.copy()
        clean["TMD"] = pd.to_numeric(clean["TMD"], errors="coerce")
        start = clean[clean["TMD"].eq(0)].dropna(subset=["LAT", "LON"]).head(1)
        if start.empty:
            start = clean[clean["TMD"].gt(0)].dropna(subset=["LAT", "LON"]).sort_values(["TMD", "FT_TM(UTC)", "SEQ"]).head(1)
        if start.empty:
            continue
        row = start.iloc[0]
        distance = haversine_km(ref_lat, ref_lon, float(row["LAT"]), float(row["LON"]))
        if distance <= APIHUB_MODEL_START_MAX_DISTANCE_KM:
            continue
        keep_mask.loc[model_df.index] = False
        removed.append(f"{model_name} ({distance:.0f} km from {ref_source})")
    if removed:
        print(
            "Dropped suspicious KMA APIHUB model source(s) due to excessive start-position distance; "
            "falling back to lower-priority ATCF source when available: " + ", ".join(removed)
        )
    return df.loc[keep_mask].copy()

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


def normalize_track_data(
    kma_df: pd.DataFrame,
    dmdw_df: pd.DataFrame,
    polarwx_df: pd.DataFrame,
    smca_df: pd.DataFrame,
    atcf_df: pd.DataFrame,
    settings: Settings,
) -> pd.DataFrame:
    df = pd.concat([kma_df, dmdw_df, polarwx_df, smca_df, atcf_to_kma_schema(atcf_df, settings)], ignore_index=True)
    if df.empty:
        return df

    df = filter_suspicious_apihub_model_starts(df, settings)
    df = select_model_sources_by_priority(df, settings)

    if MODEL_ALIAS_PRIORITY_COLUMN not in df.columns:
        df[MODEL_ALIAS_PRIORITY_COLUMN] = 0
    df[MODEL_ALIAS_PRIORITY_COLUMN] = (
        pd.to_numeric(df[MODEL_ALIAS_PRIORITY_COLUMN], errors="coerce")
        .fillna(0)
        .astype(int)
    )

    df = df.sort_values(
        ["TYP", "SRC", "FT_TM(UTC)", MODEL_ALIAS_PRIORITY_COLUMN],
        kind="stable",
    )
    df = df.drop_duplicates(subset=["TYP", "SRC", "FT_TM(UTC)"], keep="first")
    df = df[df["SRC"].isin(MODEL_NAMES)].copy()
    for col in ["LAT", "LON", "WS", "TMD", "SEQ"]:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["LAT", "LON"])
    df = apply_common_kma_start(df, settings)
    df = trim_dateline_reflected_tracks(df)
    df = trim_excessive_motion_tracks(df)
    return clip_120_domain_tracks(df, settings)


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


def signed_dateline_crossing_cutoff(track: pd.DataFrame) -> tuple[float, float] | None:
    """Return (crossing lead, previous lead) for a signed 170E/170W transition."""
    clean = track.dropna(subset=["LON", "TMD"]).copy()
    if len(clean) < 2:
        return None
    clean["LON"] = pd.to_numeric(clean["LON"], errors="coerce")
    clean["TMD"] = pd.to_numeric(clean["TMD"], errors="coerce")
    clean = (
        clean.dropna(subset=["LON", "TMD"])
        .sort_values(["TMD", "FT_TM(UTC)", "SEQ"], kind="stable")
        .drop_duplicates(subset=["TMD"], keep="first")
    )
    forecast = clean[clean["TMD"].ge(0)].reset_index(drop=True)
    if len(forecast) < 2:
        return None

    previous = forecast.iloc[0]
    for _, current in forecast.iloc[1:].iterrows():
        previous_lon = float(previous["LON"])
        current_lon = float(current["LON"])
        crosses_dateline = (
            abs(previous_lon) >= 170
            and abs(current_lon) >= 170
            and previous_lon * current_lon < 0
            and abs(current_lon - previous_lon) > 180
        )
        if crosses_dateline:
            return float(current["TMD"]), float(previous["TMD"])
        previous = current
    return None


def trim_dateline_reflected_tracks(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or DATA_SOURCE_COLUMN not in df.columns:
        return df

    frames: list[pd.DataFrame] = []
    for (model_name, source_name), track in df.groupby(["SRC", DATA_SOURCE_COLUMN], dropna=False):
        crossing = signed_dateline_crossing_cutoff(track)
        if crossing is not None:
            crossing_lead, previous_lead = crossing
            tmd = pd.to_numeric(track["TMD"], errors="coerce")
            trimmed = track[tmd.lt(crossing_lead) | tmd.isna()].copy()
            removed = len(track) - len(trimmed)
            print(
                f"{model_name} {source_display_name(str(source_name))}: "
                f"trimmed {removed} point(s) after {previous_lead:g}h "
                f"before dateline crossing at {crossing_lead:g}h"
            )
            frames.append(trimmed)
            continue

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


def excessive_motion_cutoff(track: pd.DataFrame, *, max_speed_kmh: float = MODEL_TRACK_MAX_SPEED_KMH) -> tuple[float, float] | None:
    if track.empty or len(track) < 2 or max_speed_kmh <= 0:
        return None
    clean = track.dropna(subset=["LAT", "LON", "TMD"]).copy()
    if len(clean) < 2:
        return None
    clean["LAT"] = pd.to_numeric(clean["LAT"], errors="coerce")
    clean["LON"] = pd.to_numeric(clean["LON"], errors="coerce")
    clean["TMD"] = pd.to_numeric(clean["TMD"], errors="coerce")
    clean = (
        clean.dropna(subset=["LAT", "LON", "TMD"])
        .sort_values(["TMD", "FT_TM(UTC)", "SEQ"], kind="stable")
        .drop_duplicates(subset=["TMD"], keep="first")
        .reset_index(drop=True)
    )
    forecast = clean[clean["TMD"].ge(0)].reset_index(drop=True)
    if len(forecast) < 2:
        return None
    previous = forecast.iloc[0]
    for _, current in forecast.iloc[1:].iterrows():
        hours = float(current["TMD"]) - float(previous["TMD"])
        if hours <= 0:
            previous = current
            continue
        distance = haversine_km(
            float(previous["LAT"]),
            float(previous["LON"]),
            float(current["LAT"]),
            float(current["LON"]),
        )
        speed = distance / hours
        if speed >= max_speed_kmh:
            return float(current["TMD"]), float(speed)
        previous = current
    return None


def trim_excessive_motion_tracks(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or DATA_SOURCE_COLUMN not in df.columns:
        return df

    frames: list[pd.DataFrame] = []
    for (model_name, source_name), track in df.groupby(["SRC", DATA_SOURCE_COLUMN], dropna=False):
        if str(model_name) == "KMA":
            frames.append(track)
            continue
        cutoff = excessive_motion_cutoff(track)
        if cutoff is None:
            frames.append(track)
            continue
        cutoff_lead, speed = cutoff
        tmd = pd.to_numeric(track["TMD"], errors="coerce")
        trimmed = track[tmd.lt(cutoff_lead) | tmd.isna()].copy()
        removed = len(track) - len(trimmed)
        print(
            f"{model_name} {source_display_name(str(source_name))}: "
            f"trimmed {removed} point(s) from {cutoff_lead:g}h onward "
            f"due to excessive forecast motion ({speed:.0f} km/h >= {MODEL_TRACK_MAX_SPEED_KMH:g} km/h)."
        )
        if not trimmed.empty:
            frames.append(trimmed)

    return pd.concat(frames, ignore_index=True) if frames else df.iloc[0:0].copy()


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
            source_names = {
                str(source).strip().upper()
                for source in model_track.get(DATA_SOURCE_COLUMN, pd.Series(dtype=str)).dropna().unique()
            }
            if "KNACKWX" in source_names:
                first_lead = model_track["TMD"].dropna().min()
                print(
                    f"{model_name} KNACKWX starts at {first_lead:g}h; "
                    "keeping the track unanchored from KMA 0h."
                )
                continue
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
    has_kim_gfdl = "KIM_GFDL_6h" in grouped and has_forecast_points(grouped["KIM_GFDL_6h"])

    has_um = "UM" in grouped and has_forecast_points(grouped["UM"])
    has_um_gfdl = "UM_GFDL_6h" in grouped and has_forecast_points(grouped["UM_GFDL_6h"])

    excluded = {"KMA"}

    if has_kim_3h:
        excluded.update({"KIM_6h", "KIM_GFDL_6h"})
    elif has_kim_6h:
        excluded.update({"KIM_3h", "KIM_GFDL_6h"})
    elif has_kim_gfdl:
        excluded.update({"KIM_3h", "KIM_6h"})
    else:
        excluded.update({"KIM_6h", "KIM_GFDL_6h"})

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
    kim_active_count = len({"KIM_3h", "KIM_6h", "KIM_GFDL_6h"} & active)
    if kim_active_count > 1:
        count -= kim_active_count - 1
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


def canonical_storm_stage(settings: Settings) -> str:
    explicit = str(settings.canonical_storm_stage or "").strip().upper()
    if explicit in {"TD", "TYP"}:
        return explicit
    if settings.storm_stage.upper() == "TD" and settings.linked_typ_number and settings.canonical_typ_number:
        return "TYP"
    return "TD" if settings.storm_stage.upper() == "TD" else "TYP"


def canonical_typ_number(settings: Settings) -> int:
    if settings.canonical_typ_number:
        return int(settings.canonical_typ_number)
    if canonical_storm_stage(settings) == "TYP" and settings.storm_stage.upper() == "TD" and settings.linked_typ_number:
        return int(settings.linked_typ_number)
    return int(settings.typ_number)


def canonical_typ_name(settings: Settings) -> str:
    name = str(settings.canonical_typ_name or "").strip()
    if name:
        return name
    if canonical_storm_stage(settings) == "TYP":
        return str(settings.typ_name or "NONAME").strip() or "NONAME"
    return str(settings.typ_name or "NONAME").strip() or "NONAME"


def canonical_typ_name_ko(settings: Settings) -> str:
    return str(settings.canonical_typ_name_ko or settings.typ_name_ko or "").strip()


def canonical_storm_key(settings: Settings) -> str:
    prefix = "td" if canonical_storm_stage(settings) == "TD" else "typ"
    return f"{prefix}_{storm_year(settings)}_{canonical_typ_number(settings):02d}"


def canonical_metadata_fields(settings: Settings) -> dict:
    return {
        "canonical_storm_key": canonical_storm_key(settings),
        "canonical_storm_stage": canonical_storm_stage(settings),
        "canonical_typ_number": canonical_typ_number(settings),
        "canonical_typ_name": canonical_typ_name(settings),
        "canonical_typ_name_ko": canonical_typ_name_ko(settings),
    }


def source_availability_storm_key(settings: Settings) -> str:
    return canonical_storm_key(settings)


def source_availability_base_dir(settings: Settings) -> Path:
    return system_output_dir(settings) / "metadata" / "source_availability"


def source_availability_latest_path(settings: Settings) -> Path:
    return source_availability_base_dir(settings) / f"{settings.data_time}.json"


def source_availability_summary_path(settings: Settings) -> Path:
    return source_availability_base_dir(settings) / "summary.json"


def relative_project_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def source_availability_metadata_paths(
    settings: Settings,
    observed_at_utc: str | None = None,
    *,
    existing_only: bool = True,
) -> dict[str, str]:
    latest_path = source_availability_latest_path(settings)
    paths: dict[str, str] = {}
    if not existing_only or latest_path.exists():
        paths["source_availability_path"] = relative_project_path(latest_path)
    return paths


def availability_load_json(path: Path, fallback):
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return fallback


def availability_write_json(path: Path, payload) -> None:
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


def source_availability_frame(
    kma_df: pd.DataFrame,
    dmdw_df: pd.DataFrame,
    polarwx_df: pd.DataFrame,
    smca_df: pd.DataFrame,
    atcf_df: pd.DataFrame,
    settings: Settings,
) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    if not kma_df.empty:
        frames.append(kma_df.copy())
    if not dmdw_df.empty:
        frames.append(dmdw_df.copy())
    if not polarwx_df.empty:
        frames.append(polarwx_df.copy())
    if not smca_df.empty:
        frames.append(smca_df.copy())
    if not atcf_df.empty:
        frames.append(atcf_to_kma_schema(atcf_df, settings))
    if not frames:
        return pd.DataFrame(columns=[*KMA_COLUMNS, DATA_SOURCE_COLUMN])

    raw = pd.concat(frames, ignore_index=True, sort=False)
    if DATA_SOURCE_COLUMN not in raw:
        raw[DATA_SOURCE_COLUMN] = ""
    if "SRC" not in raw or "TMD" not in raw:
        return pd.DataFrame(columns=[*KMA_COLUMNS, DATA_SOURCE_COLUMN])
    if RAW_MODEL_COLUMN not in raw:
        raw[RAW_MODEL_COLUMN] = raw["SRC"].astype(str)
    else:
        raw[RAW_MODEL_COLUMN] = raw[RAW_MODEL_COLUMN].where(
            raw[RAW_MODEL_COLUMN].notna() & raw[RAW_MODEL_COLUMN].astype(str).str.strip().ne(""),
            raw["SRC"],
        ).astype(str)
    raw["SRC"] = raw["SRC"].replace(MODEL_SOURCE_ALIASES)
    raw["TMD"] = pd.to_numeric(raw["TMD"], errors="coerce")
    for column in ("LAT", "LON", "WS", "PS"):
        if column in raw:
            raw[column] = pd.to_numeric(raw[column], errors="coerce")
    raw = raw[raw["SRC"].isin(MODEL_NAMES)].copy()
    raw = raw.dropna(subset=["TMD"])
    return raw


def source_availability_entries(
    raw_df: pd.DataFrame,
    selected_df: pd.DataFrame,
    settings: Settings,
) -> tuple[list[dict], dict[str, dict]]:
    if raw_df.empty:
        return [], {}

    selected_pairs: set[tuple[str, str]] = set()
    selected_models: dict[str, dict] = {}
    if not selected_df.empty and DATA_SOURCE_COLUMN in selected_df and "SRC" in selected_df:
        selected_work = selected_df.copy()
        selected_work["TMD"] = pd.to_numeric(selected_work["TMD"], errors="coerce")
        for (model_name, source_name), group in selected_work.groupby(["SRC", DATA_SOURCE_COLUMN], dropna=True):
            model_name = str(model_name or "").strip()
            source_name = str(source_name or "").strip().upper()
            if not model_name or not source_name:
                continue
            selected_pairs.add((model_name, source_name))
            leads = sorted({int(round(float(value))) for value in group["TMD"].dropna()})
            selected_models[model_name] = {
                "selected_source": source_name,
                "selected_source_label": source_display_name(source_name),
                "max_lead_hour": max(leads) if leads else None,
                "point_count": source_availability_point_count(group),
            }

    entries: list[dict] = []
    for (source_name, model_name), group in raw_df.groupby([DATA_SOURCE_COLUMN, "SRC"], dropna=True):
        source_name = str(source_name or "").strip().upper()
        model_name = str(model_name or "").strip()
        if not source_name or not model_name:
            continue
        leads = sorted({int(round(float(value))) for value in pd.to_numeric(group["TMD"], errors="coerce").dropna()})
        if not leads:
            continue
        ws_values = pd.to_numeric(group.get("WS", pd.Series(dtype=float)), errors="coerce")
        ps_values = pd.to_numeric(group.get("PS", pd.Series(dtype=float)), errors="coerce")
        observed_raw_model_ids = sorted({
            str(value).strip()
            for value in group.get(RAW_MODEL_COLUMN, pd.Series(dtype=str)).dropna()
            if str(value).strip()
        })
        raw_model_ids = normalized_raw_model_ids(model_name, source_name, observed_raw_model_ids)
        entry = {
            "model_id": model_name,
            "model_label": model_display_label(model_name),
            "raw_model_ids": raw_model_ids,
            "source": source_name,
            "source_label": source_display_name(source_name),
            "selected": (model_name, source_name) in selected_pairs,
            "point_count": source_availability_point_count(group),
            "max_lead_hour": max(leads),
            "has_pressure": bool(ps_values.gt(0).any()) if not ps_values.empty else False,
            "has_wind": bool(ws_values.gt(0).any()) if not ws_values.empty else False,
            "is_official": model_name == "KMA",
        }
        entries.append(entry)

    entries.sort(key=lambda item: (item["model_label"], item["model_id"], item["source"]))
    selected_models = dict(sorted(selected_models.items(), key=lambda item: item[0]))
    return entries, selected_models


def availability_parse_utc_stamp(value: str) -> datetime | None:
    text = str(value or "").strip()
    for size, fmt in ((14, "%Y%m%d%H%M%S"), (12, "%Y%m%d%H%M"), (10, "%Y%m%d%H")):
        candidate = text[:size]
        if len(candidate) == size and candidate.isdigit():
            try:
                return datetime.strptime(candidate, fmt).replace(tzinfo=timezone.utc)
            except ValueError:
                return None
    return None


def availability_kst_label(value: str) -> str:
    parsed = availability_parse_utc_stamp(value)
    if parsed is None:
        return ""
    return (parsed + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M KST")


def availability_cycle_label(value: str) -> str:
    parsed = availability_parse_utc_stamp(value)
    if parsed is None:
        return str(value or "")
    return parsed.strftime("%Y-%m-%d %HUTC")


def previous_availability_source_records(path: Path) -> dict[str, dict]:
    payload = availability_load_json(path, {})
    if not isinstance(payload, dict):
        return {}
    records: dict[str, dict] = {}
    for entry in payload.get("model_sources", []):
        if not isinstance(entry, dict):
            continue
        key = source_model_key(entry)
        if key != "|":
            records[key] = entry
    return records


def annotate_source_first_seen(entries: list[dict], latest_path: Path, observed_at_utc: str) -> list[dict]:
    previous_records = previous_availability_source_records(latest_path)
    annotated: list[dict] = []
    for entry in entries:
        key = source_model_key(entry)
        previous = previous_records.get(key, {})
        first_seen = str(previous.get("first_seen_utc") or observed_at_utc)
        updated = dict(entry)
        updated["first_seen_utc"] = first_seen
        updated["first_seen_kst"] = availability_kst_label(first_seen)
        annotated.append(updated)
    return sorted(
        annotated,
        key=lambda item: (
            str(item.get("model_label") or ""),
            str(item.get("model_id") or ""),
            str(item.get("first_seen_utc") or ""),
            0 if item.get("selected") else 1,
            str(item.get("source") or ""),
        ),
    )


def source_availability_snapshot(
    raw_df: pd.DataFrame,
    selected_df: pd.DataFrame,
    settings: Settings,
    *,
    fetch_hours: int,
    requested_hours: tuple[int, ...],
    observed_at_utc: str,
) -> dict:
    entries, selected_models = source_availability_entries(raw_df, selected_df, settings)
    entries = annotate_source_first_seen(entries, source_availability_latest_path(settings), observed_at_utc)
    selected_model_count = len([name for name in selected_models if name != "KMA"])

    return {
        "version": 2,
        "schema": "cycle_model_source_first_seen",
        "generated_at_utc": observed_at_utc,
        "generated_at_kst": availability_kst_label(observed_at_utc),
        "storm_year": storm_year(settings),
        "storm_key": source_availability_storm_key(settings),
        "storm_stage": settings.storm_stage,
        "typ_number": settings.typ_number,
        "data_typ_number": kma_data_typ_number(settings),
        "typ_name": settings.typ_name,
        "typ_name_ko": settings.typ_name_ko,
        **canonical_metadata_fields(settings),
        "linked_td_number": settings.linked_td_number,
        "linked_typ_number": settings.linked_typ_number,
        "atcf_id": "" if settings.skip_atcf else settings.atcf_id,
        "extra_atcf_ids": [] if settings.skip_atcf else list(settings.extra_atcf_ids),
        "data_time": settings.data_time,
        "cycle_time_utc": settings.data_time,
        "cycle_label_utc": availability_cycle_label(settings.data_time),
        "fetch_hours": int(fetch_hours),
        "requested_hours": list(requested_hours),
        "model_source_count": len(entries),
        "selected_model_count": selected_model_count,
        "active_target_model_count": active_model_target_count(settings),
        "model_sources": entries,
        **source_availability_metadata_paths(settings, observed_at_utc, existing_only=False),
    }


def source_model_key(entry: dict) -> str:
    return f"{entry.get('model_id', '')}|{entry.get('source', '')}"


def write_source_availability_outputs(
    *,
    raw_df: pd.DataFrame,
    selected_df: pd.DataFrame,
    settings: Settings,
    fetch_hours: int,
    requested_hours: tuple[int, ...],
) -> dict[str, str]:
    observed_at_utc = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    latest_path = source_availability_latest_path(settings)
    summary_path = source_availability_summary_path(settings)

    snapshot = source_availability_snapshot(
        raw_df,
        selected_df,
        settings,
        fetch_hours=fetch_hours,
        requested_hours=requested_hours,
        observed_at_utc=observed_at_utc,
    )
    snapshot["source_availability_path"] = relative_project_path(latest_path)

    availability_write_json(latest_path, snapshot)
    try:
        summary_path.unlink()
    except FileNotFoundError:
        pass
    print(
        "Wrote source availability metadata: "
        f"{relative_project_path(latest_path)} "
        f"(model_sources={len(snapshot.get('model_sources', []))})"
    )
    return source_availability_metadata_paths(settings, observed_at_utc)

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
    has_pressure = valid_pressure.notna().any()
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
    if DATA_SOURCE_COLUMN in track:
        sources = track[DATA_SOURCE_COLUMN].fillna("").astype(str).str.upper()
        if sources.eq("KNACKWX").any():
            clean = track.copy()
            clean["TMD"] = pd.to_numeric(clean["TMD"], errors="coerce")
            clean = clean.dropna(subset=["TMD"]).sort_values(["TMD", "FT_TIME", "SEQ"])
            clean = clean.drop_duplicates(subset=["TMD"], keep="first")
            if clean.empty:
                return clean

            selected_indices = {clean.index[0]}
            min_lead = float(clean["TMD"].min())
            max_lead = float(clean["TMD"].max())
            target = max(24.0, math.ceil(min_lead / 24.0) * 24.0)

            while target <= max_lead:
                candidates = clean.loc[~clean.index.isin(selected_indices)].copy()
                candidates["_MARKER_DISTANCE"] = (candidates["TMD"] - target).abs()
                candidates = candidates[candidates["_MARKER_DISTANCE"].le(12.0)]
                if not candidates.empty:
                    nearest = candidates.sort_values(
                        ["_MARKER_DISTANCE", "TMD", "FT_TIME"],
                        ascending=[True, True, True],
                    ).iloc[0]
                    selected_indices.add(nearest.name)
                target += 24.0

            return clean.loc[sorted(selected_indices, key=lambda index: clean.at[index, "TMD"])]
    base_time = track["FT_TIME"].iloc[0]
    elapsed_hours = (track["FT_TIME"] - base_time).dt.total_seconds() / 3600
    return track[elapsed_hours.mod(24).eq(0)]


def split_knackwx_track_segments(track: pd.DataFrame, *, max_gap_hours: float = KNACKWX_MAX_LEAD_GAP_HOURS) -> list[pd.DataFrame]:
    """Do not draw lines across forecast hours missing from the temporary KNACKWX feed."""
    if track.empty or DATA_SOURCE_COLUMN not in track:
        return [track]
    sources = track[DATA_SOURCE_COLUMN].fillna("").astype(str).str.upper()
    if not sources.eq("KNACKWX").any():
        return [track]

    ordered = track.copy()
    ordered["TMD"] = pd.to_numeric(ordered["TMD"], errors="coerce")
    ordered = ordered.sort_values(["TMD", "FT_TIME", "SEQ"], na_position="last")
    gap_starts = ordered["TMD"].diff().gt(max_gap_hours).fillna(False)
    segment_ids = gap_starts.cumsum()
    segments = [segment.copy() for _, segment in ordered.groupby(segment_ids, sort=True) if not segment.empty]

    if len(segments) > 1:
        boundaries = [
            (float(segments[index - 1]["TMD"].max()), float(segments[index]["TMD"].min()))
            for index in range(1, len(segments))
        ]
        print(f"KNACKWX track split across missing lead interval(s): {boundaries}")
    return segments or [ordered]


def model_visual_style(model_name: str, model: dict) -> dict:
    basis, forecast_type = MODEL_CATEGORIES.get(model_name, ("DYNAMICAL", "DETERMINISTIC"))
    is_ai = basis == "AI"
    is_ensemble = forecast_type == "ENSEMBLE"
    color = model["color"]
    return {
        "color": color,
        "linestyle": "--" if is_ai else "-",
        "linewidth": 1.7,
        "alpha": 1.0,
        "marker": "o",
        "markerfacecolor": color,
        "markeredgecolor": color,
        "markeredgewidth": 0.8,
        "markersize": 5,
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
    explicit_year = str(getattr(settings, "storm_year", "") or "").strip()
    if len(explicit_year) == 4 and explicit_year.isdigit():
        return explicit_year
    if len(settings.atcf_id) >= 8 and settings.atcf_id[4:].isdigit():
        return settings.atcf_id[4:]
    if len(settings.data_time) >= 4 and settings.data_time[:4].isdigit():
        return settings.data_time[:4]
    return datetime.utcnow().strftime("%Y")


def storm_number_label(settings: Settings) -> str:
    atcf_id = settings.atcf_id.lower()
    if settings.skip_atcf or len(atcf_id) < 8 or not atcf_id[2:4].isdigit():
        return ""
    basin = atcf_id[:2].upper()
    basin_label = {
        "WP": "W",
        "EP": "E",
        "CP": "C",
        "AL": "L",
    }.get(basin, basin)
    return f"({atcf_id[2:4]}{basin_label})"


def display_typ_name(settings: Settings) -> str:
    name = str(settings.typ_name or "").strip()
    return "" if name.upper() == "NONAME" else name


def system_dir_name_for_parts(year: str | int, stage: str, number: int, name: str = "NONAME") -> str:
    year_text = str(year or "").strip()
    try:
        year_suffix = int(year_text) % 100
    except (TypeError, ValueError):
        year_suffix = 0
    try:
        storm_number = int(number)
    except (TypeError, ValueError):
        storm_number = 0
    stage_label = "TD" if str(stage or "").upper().startswith("TD") else "TYP"
    storm_name = str(name or "NONAME").strip() or "NONAME"
    return f"{stage_label}_{year_suffix:02d}{storm_number:02d}_{storm_name}"


def system_dir_name(settings: Settings) -> str:
    return system_dir_name_for_parts(
        storm_year(settings),
        canonical_storm_stage(settings),
        canonical_typ_number(settings),
        canonical_typ_name(settings),
    )


def system_output_dir(settings: Settings) -> Path:
    return settings.output_root / storm_year(settings) / system_dir_name(settings)


def system_metadata_dir(settings: Settings) -> Path:
    return system_output_dir(settings) / "metadata"


def output_path(settings: Settings) -> Path:
    cyclone_id = tc_id(settings)
    stage = settings.storm_stage.upper()
    storm_name = settings.typ_name or "NONAME"
    if stage == "TD":
        dir_name = f"TD_{cyclone_id}_{storm_name}"
        file_name = f"TD_{cyclone_id}_{storm_name}_{settings.data_time}_{settings.fcst_hours}h.png"
    else:
        dir_name = f"TYP_{cyclone_id}_{storm_name}"
        file_name = f"TYP_{cyclone_id}_{storm_name}_{settings.data_time}_{settings.fcst_hours}h.png"
    return system_output_dir(settings) / "images" / file_name


def metadata_path_for_settings(settings: Settings) -> Path | None:
    hours = settings.fcst_hours_options or (settings.fcst_hours,)
    if settings.metadata_path and len(hours) == 1:
        return settings.metadata_path

    return system_metadata_dir(settings) / "runs" / f"{settings.data_time}_{settings.fcst_hours}h.json"


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
        **canonical_metadata_fields(settings),
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
        **source_availability_metadata_paths(settings),
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
        **canonical_metadata_fields(settings),
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
        **source_availability_metadata_paths(settings),
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


def auto_120_map_extent(df: pd.DataFrame, settings: Settings) -> list[float] | None:
    points = extent_points_for_auto_map(df, settings)
    if points.empty:
        return None

    # For 120h, the old KMA past track no longer needs to drive the camera.
    # Use the forecast spread plus the current KMA position only.
    lead_hours = pd.to_numeric(points["TMD"], errors="coerce")
    forecast_points = points[lead_hours.between(0, settings.fcst_hours)].copy()
    if forecast_points.empty:
        forecast_points = points.copy()

    current_kma = points[points["SRC"].eq("KMA") & lead_hours.eq(0)].copy()
    non_kma_forecast = forecast_points[forecast_points["SRC"].ne("KMA")].copy()
    primary = pd.concat([non_kma_forecast, current_kma], ignore_index=True)
    if primary.empty:
        primary = forecast_points.copy()

    lat_min, lat_max = robust_bounds(primary, "LAT", settings)
    lon_min, lon_max = robust_bounds(primary, "LON", settings)
    lat_span = max(lat_max - lat_min, 7.0)
    lon_span = max(lon_max - lon_min, 9.0)

    focus_lat = (lat_min + lat_max) / 2
    focus_lon = (lon_min + lon_max) / 2
    lon_total = max(21.0, lon_span * 1.18 + 4.2)
    lat_total = max(9.2, lat_span * 1.28 + 3.0)

    # Mild westward framing bias so the forecast fan appears closer to center.
    focus_x = 0.57
    focus_y = 0.40

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




def legend_row_count_for(df: pd.DataFrame, settings: Settings) -> int:
    excluded = excluded_models_for(df)
    active = active_model_names(settings)
    return len([model for model in MODEL_INFO if model["name"] in active and model["name"] not in excluded])




def fixed_240_map_extent(settings: Settings) -> list[float]:
    """Stable long-range West-Pacific view used instead of dynamic camera fitting."""
    return list(FIXED_240_MAP_EXTENT)


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
    
    x_center = (x0 + x1) / 2

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

        _, new_lat_min = data_crs.transform_point(x_center, y_center - y_half, projection)
        _, new_lat_max = data_crs.transform_point(x_center, y_center + y_half, projection)

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
    if settings.fcst_hours >= 240:
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


def extent_exceeds_120_display_bounds(extent: list[float]) -> bool:
    lon_min, lon_max, lat_min, lat_max = [float(value) for value in extent]
    return (
        lon_min < DISPLAY_120_LON_MIN
        or lon_max > DISPLAY_120_LON_MAX
        or lat_min < DISPLAY_120_LAT_MIN
        or lat_max > DISPLAY_120_LAT_MAX
    )


def crop_legacy_120_extent_to_hard_domain(
    legacy_extent: list[float],
    *,
    fig_width: float,
    fig_height: float,
    start_point: tuple[float, float] | None = None,
) -> list[float]:
    """Crop the original 120h camera without redesigning its composition.

    The pre-hard-domain camera is treated as the source viewport.  Intersect it
    with the 100E-179.9E / 0N-50N display domain, then choose the largest exact
    Mercator-aspect rectangle inside that intersection.  No opposite-side fill,
    terminal-anchor expansion, or secondary camera fit is applied.

    When one dimension must be trimmed, preserve the current 0h point's
    relative position from the original viewport as far as the hard boundary
    allows.  This retains the legacy left/bottom breathing room and keeps a
    short section of the past track visible.
    """
    if fig_width <= 0 or fig_height <= 0:
        return legacy_extent

    projection = ccrs.Mercator()
    data_crs = ccrs.PlateCarree()
    lon_min, lon_max, lat_min, lat_max = [float(value) for value in legacy_extent]
    center_lon = (lon_min + lon_max) / 2.0
    center_lat = (lat_min + lat_max) / 2.0

    legacy_x0, _ = projection.transform_point(lon_min, center_lat, data_crs)
    legacy_x1, _ = projection.transform_point(lon_max, center_lat, data_crs)
    _, legacy_y0 = projection.transform_point(center_lon, lat_min, data_crs)
    _, legacy_y1 = projection.transform_point(center_lon, lat_max, data_crs)

    hard_x0, _ = projection.transform_point(DISPLAY_120_LON_MIN, center_lat, data_crs)
    hard_x1, _ = projection.transform_point(DISPLAY_120_LON_MAX, center_lat, data_crs)
    _, hard_y0 = projection.transform_point(center_lon, DISPLAY_120_LAT_MIN, data_crs)
    _, hard_y1 = projection.transform_point(center_lon, DISPLAY_120_LAT_MAX, data_crs)

    crop_x0 = max(legacy_x0, hard_x0)
    crop_x1 = min(legacy_x1, hard_x1)
    crop_y0 = max(legacy_y0, hard_y0)
    crop_y1 = min(legacy_y1, hard_y1)
    if crop_x1 <= crop_x0 or crop_y1 <= crop_y0:
        return [
            max(DISPLAY_120_LON_MIN, min(DISPLAY_120_LON_MAX, lon_min)),
            max(DISPLAY_120_LON_MIN, min(DISPLAY_120_LON_MAX, lon_max)),
            max(DISPLAY_120_LAT_MIN, min(DISPLAY_120_LAT_MAX, lat_min)),
            max(DISPLAY_120_LAT_MIN, min(DISPLAY_120_LAT_MAX, lat_max)),
        ]

    target_aspect = fig_width / fig_height
    crop_width = crop_x1 - crop_x0
    crop_height = crop_y1 - crop_y0
    crop_aspect = crop_width / crop_height

    # Preserve where the 0h point sat in the legacy camera.  The ratios are
    # bounded only to guarantee a small visible margin if hard clipping pushes
    # the point close to an edge.
    anchor_x = (legacy_x0 + legacy_x1) / 2.0
    anchor_y = (legacy_y0 + legacy_y1) / 2.0
    ratio_x = 0.5
    ratio_y = 0.5
    if start_point is not None:
        start_lon, start_lat = [float(value) for value in start_point]
        if all(math.isfinite(value) for value in (start_lon, start_lat)):
            anchor_x, anchor_y = projection.transform_point(start_lon, start_lat, data_crs)
            legacy_width = legacy_x1 - legacy_x0
            legacy_height = legacy_y1 - legacy_y0
            if legacy_width > 0:
                ratio_x = (anchor_x - legacy_x0) / legacy_width
            if legacy_height > 0:
                ratio_y = (anchor_y - legacy_y0) / legacy_height
    ratio_x = min(0.92, max(0.08, ratio_x))
    ratio_y = min(0.92, max(0.08, ratio_y))

    if crop_aspect > target_aspect:
        # Hard clipping made the viewport too wide: trim only longitude.
        final_height = crop_height
        final_width = final_height * target_aspect
        preferred_x0 = anchor_x - ratio_x * final_width
        final_x0 = min(max(preferred_x0, crop_x0), crop_x1 - final_width)
        final_x1 = final_x0 + final_width
        final_y0, final_y1 = crop_y0, crop_y1
    elif crop_aspect < target_aspect:
        # Hard clipping made the viewport too tall: trim only latitude.
        final_width = crop_width
        final_height = final_width / target_aspect
        preferred_y0 = anchor_y - ratio_y * final_height
        final_y0 = min(max(preferred_y0, crop_y0), crop_y1 - final_height)
        final_y1 = final_y0 + final_height
        final_x0, final_x1 = crop_x0, crop_x1
    else:
        final_x0, final_x1 = crop_x0, crop_x1
        final_y0, final_y1 = crop_y0, crop_y1

    projected_y = (final_y0 + final_y1) / 2.0
    projected_x = (final_x0 + final_x1) / 2.0
    final_lon_min, _ = data_crs.transform_point(final_x0, projected_y, projection)
    final_lon_max, _ = data_crs.transform_point(final_x1, projected_y, projection)
    _, final_lat_min = data_crs.transform_point(projected_x, final_y0, projection)
    _, final_lat_max = data_crs.transform_point(projected_x, final_y1, projection)

    return [
        max(DISPLAY_120_LON_MIN, float(final_lon_min)),
        min(DISPLAY_120_LON_MAX, float(final_lon_max)),
        max(DISPLAY_120_LAT_MIN, float(final_lat_min)),
        min(DISPLAY_120_LAT_MAX, float(final_lat_max)),
    ]


def finalize_map_extent(
    settings: Settings,
    extent: list[float],
    *,
    fig_width: float,
    fig_height: float,
    start_point: tuple[float, float] | None = None,
) -> list[float]:
    """Finalize the viewport with one explicit camera priority.

    240h and longer forecasts keep their fixed domain. Every other case first uses the original
    pre-hard-domain camera.  Only an automatic 120h viewport that crosses the
    hard domain receives one final crop-and-zoom pass.
    """
    if settings.fcst_hours >= 240:
        return fixed_240_map_extent(settings)

    legacy_extent = aspect_match_and_clamp_extent(
        [float(value) for value in extent],
        settings,
        fig_width=fig_width,
        fig_height=fig_height,
    )

    if (
        settings.fcst_hours == 120
        and settings.auto_extent
        and extent_exceeds_120_display_bounds(legacy_extent)
    ):
        return crop_legacy_120_extent_to_hard_domain(
            legacy_extent,
            fig_width=fig_width,
            fig_height=fig_height,
            start_point=start_point,
        )

    return legacy_extent


def bounds_intersect(left: tuple[float, float, float, float], right: tuple[float, float, float, float]) -> bool:
    left_min_x, left_min_y, left_max_x, left_max_y = left
    right_min_x, right_min_y, right_max_x, right_max_y = right
    return not (
        left_max_x < right_min_x
        or left_min_x > right_max_x
        or left_max_y < right_min_y
        or left_min_y > right_max_y
    )


def hide_hokkaido_east_border_record(record) -> bool:
    attributes = record.attributes
    if attributes.get("FEATURECLA") != "Disputed (please verify)":
        return False
    if attributes.get("TYPE") != "Water Indicator":
        return False
    geometry = record.geometry
    return geometry is not None and bounds_intersect(geometry.bounds, HOKKAIDO_EAST_BORDER_MASK)


@lru_cache(maxsize=3)
def filtered_country_borders(scale: str) -> cfeature.ShapelyFeature:
    path = shapereader.natural_earth(
        resolution=scale,
        category="cultural",
        name="admin_0_boundary_lines_land",
    )
    geometries = tuple(
        record.geometry
        for record in shapereader.Reader(path).records()
        if record.geometry is not None and not hide_hokkaido_east_border_record(record)
    )
    return cfeature.ShapelyFeature(geometries, ccrs.PlateCarree(), facecolor="none")


def plot_guidance(df: pd.DataFrame, past_kma: pd.DataFrame, settings: Settings, intensity: str) -> Path:
    df = df.copy()
    df["FT_TIME"] = parse_ft_time(df["FT_TM(UTC)"])
    current_dt = pd.to_datetime(settings.data_time, format="%Y%m%d%H%M", errors="coerce")
    current_dt = None if pd.isna(current_dt) else current_dt.to_pydatetime()

    if settings.fcst_hours >= 240:
        extent = fixed_240_map_extent(settings)
    else:
        if settings.auto_extent:
            extent = auto_120_map_extent(df, settings)
        else:
            extent = None
        if extent is None:
            center_lat = df["LAT"].mean() + settings.lat_padding if not df.empty else 25
            center_lon = df["LON"].mean() + settings.lon_padding if not df.empty else 135
            extent = map_extent(settings, center_lat, center_lon)

    fig_width = settings.figure_width
    fig_height = settings.figure_height

    start_point = None
    if settings.fcst_hours == 120:
        kma_start_for_extent = df[
            df["SRC"].eq("KMA")
            & pd.to_numeric(df["TMD"], errors="coerce").eq(0)
        ].dropna(subset=["LON", "LAT"]).head(1)
        if not kma_start_for_extent.empty:
            start_point = (
                float(kma_start_for_extent.iloc[0]["LON"]),
                float(kma_start_for_extent.iloc[0]["LAT"]),
            )

    extent = finalize_map_extent(
        settings,
        extent,
        fig_width=fig_width,
        fig_height=fig_height,
        start_point=start_point,
    )

    data_crs = ccrs.PlateCarree()
    map_crs = ccrs.Mercator()

    legend_ax = None
    header_ax = None

    # Put the model legend outside the map for both 120h and 240h.
    # Keep the map panel itself at the original figure aspect so the existing
    # automatic 120h camera logic and the fixed 240h extent are not distorted.
    legend_extra_width_ratio = 0.325
    total_fig_width = fig_width * (1.0 + legend_extra_width_ratio)
    map_panel_frac = fig_width / total_fig_width
    fig = plt.figure(figsize=(total_fig_width, fig_height), dpi=settings.figure_dpi, frameon=False)
    fig.patch.set_facecolor("#262626")
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

    ax = fig.add_axes([0, 0, map_panel_frac, 1], projection=map_crs)
    ax.set_facecolor("#262626")
    ax.set_extent(extent, crs=data_crs)
    ax.set_position([0, 0, map_panel_frac, 1])

    legend_ax = fig.add_axes([map_panel_frac, 0, 1 - map_panel_frac, 1], frameon=False)
    legend_ax.set_axis_off()
    legend_ax.set_facecolor("none")

    header_ax = fig.add_axes([0, 0, 1, 1], frameon=False)
    header_ax.set_axis_off()
    header_ax.set_facecolor("none")

    ax.add_feature(cfeature.OCEAN.with_scale(MAP_FEATURE_SCALE), zorder=0, facecolor="#262626", edgecolor="none")
    ax.add_feature(cfeature.LAND.with_scale(MAP_FEATURE_SCALE), zorder=0, facecolor="#656565")
    ax.add_feature(filtered_country_borders(MAP_FEATURE_SCALE), edgecolor="gray", linestyle="-", linewidth=1)

    gl = ax.gridlines(draw_labels=True, color="gray", alpha=0.3)
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {"size": 10, "color": "gray", "va": "top"}
    gl.ylabel_style = {"size": 10, "color": "gray", "ha": "right"}
    gl.xpadding = -5
    gl.ypadding = -5
    gl.xlocator = mticker.MultipleLocator(5)
    gl.ylocator = mticker.MultipleLocator(5)

    legend_side = "panel"

    plot_past_track(ax, past_kma, current_dt)
    draw_header(header_ax, fig, df, settings, intensity, legend_side=legend_side, panel_left=map_panel_frac)
    draw_model_tracks(ax, df, settings, legend_side=legend_side, legend_ax=legend_ax)

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


def draw_header(
    ax,
    fig,
    df: pd.DataFrame,
    settings: Settings,
    intensity: str,
    *,
    legend_side: str = "right",
    panel_left: float | None = None,
) -> None:
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

    start = df.loc[(df["SRC"] == "KMA") & (df["TMD"] == 0), "TYP_TM(UTC)"].dropna()
    start_time = str(start.iloc[0]).split(".")[0] if not start.empty else settings.data_time
    start_date = f"{start_time[:4]}-{start_time[4:6]}-{start_time[6:8]}"
    start_hour = start_time[8:10]

    model_nums = len(plotted_model_names(df, settings))
    total_model_nums = legend_row_count_for(df, settings)
    model_count_text = f"{model_nums} / {total_model_nums} MODELS @ {settings.fcst_hours} HOURS"

    right_header_x = 0.978
    right_header_ha = "right"
    if legend_side == "panel" and panel_left is not None:
        right_header_x = panel_left + (1.0 - panel_left) / 2.0
        right_header_ha = "center"

    ax.text(right_header_x, 0.978, f"{start_date} {start_hour}UTC", transform=ax.transAxes,
            fontsize=34, color="white", fontweight="1000", fontfamily=PLOT_FONT_FAMILY,
            verticalalignment="top", horizontalalignment=right_header_ha, zorder=100,
            bbox=dict(boxstyle="square,pad=0.5", facecolor="none", linewidth=0))
    guidance_text = ax.text(
        0.024,
        0.932,
        "VORTEX TRACK GUIDANCE",
        transform=ax.transAxes,
        fontsize=22.5,
        color="white",
        fontweight="800",
        fontfamily=PLOT_FONT_FAMILY,
        verticalalignment="top",
        zorder=100,
        bbox=dict(boxstyle="square,pad=0.3", facecolor="none", alpha=0.8, linewidth=0),
    )

    # Measure text directly through the backend renderer. Calling canvas.draw()
    # here would render the full Cartopy map before savefig renders it again.
    get_renderer = getattr(fig.canvas, "get_renderer", None)
    if get_renderer is None:
        fig.canvas.draw()
        renderer = None
    else:
        renderer = get_renderer()
    title_bbox = title_text.get_window_extent(renderer=renderer).transformed(ax.transAxes.inverted())
    guidance_bbox = guidance_text.get_window_extent(renderer=renderer).transformed(ax.transAxes.inverted())
    if storm_number:
        ax.text(title_bbox.x1 + 0.004, 0.966, storm_number, transform=ax.transAxes,
                fontsize=17.5 if not display_name else 16.5, color="#AAF7F4", fontweight="700",
                fontfamily=PLOT_FONT_FAMILY, verticalalignment="top", horizontalalignment="left", zorder=100)
    ax.text(guidance_bbox.x1 + 0.006, 0.932, "+", transform=ax.transAxes,
            fontsize=22.5, color="white", fontweight="800", fontfamily=PLOT_FONT_FAMILY,
            verticalalignment="top", zorder=100,
            bbox=dict(boxstyle="square,pad=0.3", facecolor="none", alpha=0.8, linewidth=0))
    ax.text(right_header_x, 0.932, model_count_text, transform=ax.transAxes,
            fontsize=22.5, color="#DCB0E1", fontweight="800", fontfamily=PLOT_FONT_FAMILY,
            verticalalignment="top", horizontalalignment=right_header_ha, zorder=100,
            bbox=dict(boxstyle="square,pad=0.3", facecolor="none", alpha=0.8, linewidth=0))
    credit_x = 0.995 if legend_side == "left" else 0.005
    credit_ha = "right" if legend_side == "left" else "left"
    ax.text(credit_x, 0.006, "Plotted by WooJin Kim\nData sourced from KMA APIHUB & NRL ATCF", transform=ax.transAxes,
            fontsize=12, color="aliceblue", fontweight="800", fontfamily=PLOT_FONT_FAMILY,
            verticalalignment="bottom", horizontalalignment=credit_ha, zorder=100,
            bbox=dict(boxstyle="square,pad=0.3", facecolor="none", alpha=0.8, linewidth=0))


def draw_model_tracks(ax, df: pd.DataFrame, settings: Settings, *, legend_side: str = "right", legend_ax=None) -> None:
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
            for segment in split_knackwx_track_segments(track):
                ax.plot(
                    segment["LON"],
                    segment["LAT"],
                    color=style["color"],
                    linestyle=style["linestyle"],
                    linewidth=style["linewidth"],
                    alpha=style["alpha"],
                    zorder=zorder,
                    transform=ccrs.PlateCarree(),
                )
                markers = marker_points_every_24h(segment)
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

    draw_model_legend_table(legend_ax if legend_ax is not None else ax, legend_rows, side=legend_side)


def snap_axes_point_to_pixel(ax, x: float, y: float) -> tuple[float, float]:
    """Snap an axes-coordinate anchor to the display pixel grid.

    This is mainly for small legend text: when repeated rows land on
    slightly different sub-pixel baselines, glyph antialiasing can make
    identical labels look uneven.
    """
    px, py = ax.transAxes.transform((x, y))
    px = round(px) + 0.5
    py = round(py) + 0.5
    return tuple(ax.transAxes.inverted().transform((px, py)))


def draw_model_legend_table(ax, rows: list[dict], *, side: str = "right") -> None:
    if not rows:
        return

    if side == "panel":
        bg = mpatches.Rectangle(
            (0, 0),
            1,
            1,
            transform=ax.transAxes,
            facecolor="#E6E6E6",
            edgecolor="none",
            zorder=0,
        )
        ax.add_patch(bg)

    if side == "left":
        x0, x1 = 0.005, 0.330
        pad_x = 0.008
        pad_y = 0.005
        row_h = 0.019
        font_size = 14
        handle_len = 0.024
        label_gap = 0.030
        pressure_x = x1 - pad_x - 0.069
        lead_x = x1 - pad_x + 0.003
    elif side == "panel":
        x0, x1 = 0.022, 0.978
        pad_x = 0.016
        pad_y = 0.004
        row_h = 0.0215
        font_size = 14.2
        handle_len = 0.092
        label_gap = 0.106
        width = x1 - x0
        pressure_x = x0 + width * 0.760
        lead_x = x0 + width * 0.986
    else:
        x0, x1 = 0.670, 0.995
        pad_x = 0.008
        pad_y = 0.005
        row_h = 0.019
        font_size = 14
        handle_len = 0.024
        label_gap = 0.030
        pressure_x = x1 - pad_x - 0.069
        lead_x = x1 - pad_x + 0.003

    box_h = pad_y * 2 + row_h * len(rows)
    if side == "panel":
        panel_top = 0.895
        y1 = panel_top - x0
        y0 = max(0.012, y1 - box_h)
    else:
        y0 = 0.005
        y1 = y0 + box_h
    handle_y_offset = row_h * 0.07

    box = mpatches.FancyBboxPatch(
        (x0, y0),
        x1 - x0,
        y1 - y0,
        transform=ax.transAxes,
        boxstyle="round,pad=0.004,rounding_size=0.014",
        linewidth=0.8,
        edgecolor="#DDDDDD",
        facecolor="white",
        alpha=1.0,
        zorder=100,
    )
    ax.add_patch(box)

    handle_x0 = x0 + pad_x
    handle_x1 = x0 + pad_x + handle_len
    handle_mid = (handle_x0 + handle_x1) / 2
    label_x = x0 + pad_x + label_gap
    label_font_family = PLOT_FONT_FAMILY
    label_font_weight = "semibold"

    for idx, row in enumerate(rows):
        y = y1 - pad_y - row_h * (idx + 0.5)
        handle_y = y + handle_y_offset
        color = row["color"]
        gap = 0.011 if side == "panel" else 0.006
        handle_segments = []
        if side == "panel" and row["linestyle"] in {"--", "dashed"}:
            marker_gap = 0.012
            dash_len = 0.014
            dash_gap = 0.004
            left_inner_end = handle_mid - marker_gap
            left_inner_start = left_inner_end - dash_len
            left_outer_end = left_inner_start - dash_gap
            left_outer_start = left_outer_end - dash_len
            right_inner_start = handle_mid + marker_gap
            right_inner_end = right_inner_start + dash_len
            right_outer_start = right_inner_end + dash_gap
            right_outer_end = right_outer_start + dash_len
            handle_segments = [
                (left_outer_start, left_outer_end, "-"),
                (left_inner_start, left_inner_end, "-"),
                (right_inner_start, right_inner_end, "-"),
                (right_outer_start, right_outer_end, "-"),
            ]
        else:
            handle_segments = [
                (handle_x0, handle_mid - gap, row["linestyle"]),
                (handle_mid + gap, handle_x1, row["linestyle"]),
            ]
        for segment_x0, segment_x1, segment_style in handle_segments:
            ax.add_line(
                mlines.Line2D(
                    [segment_x0, segment_x1],
                    [handle_y, handle_y],
                    transform=ax.transAxes,
                    color=color,
                    linestyle=segment_style,
                    linewidth=2.0,
                    solid_capstyle="butt",
                    dash_capstyle="butt",
                    zorder=101,
                    clip_on=False,
                )
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
        ax.add_line(marker)
        label_text_x, label_text_y = snap_axes_point_to_pixel(ax, label_x, y)
        ax.text(
            label_text_x,
            label_text_y,
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

        pressure_text_x, pressure_text_y = snap_axes_point_to_pixel(ax, pressure_x, y)
        lead_text_x, lead_text_y = snap_axes_point_to_pixel(ax, lead_x, y)
        ax.text(
            pressure_text_x,
            pressure_text_y,
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
            lead_text_x,
            lead_text_y,
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
    main_started_at = time.monotonic()
    settings = parse_args()
    if not settings.auth_key:
        raise SystemExit("KMA_APIHUB_AUTH_KEY or --auth-key is required.")

    stage_started_at = time.monotonic()
    configure_plot_fonts()
    log_timing("configure plot fonts", stage_started_at, scale=MAP_FEATURE_SCALE)
    requested_hours = settings.fcst_hours_options or (settings.fcst_hours,)
    fetch_hour = max(settings.fcst_hours, 240) if settings.auto_fcst_hours else max(requested_hours)
    fetch_settings = replace(settings, fcst_hours=fetch_hour)

    with requests.Session() as session:
        session.headers.update(REQUEST_HEADERS)
        stage_started_at = time.monotonic()
        kma_forecast_text = read_text_file(fetch_settings.kma_forecast_text_path)
        if kma_forecast_text is None:
            kma_forecast_text = fetch_kma_text(
                session,
                kma_url(fetch_settings, "2"),
                kma_fallback_url(fetch_settings, "2"),
                label="typ_gts_now mode=2",
                retries=5,
                timeout=8,
                retry_delay=3,
                encoding="cp949",
                cache_dir=fetch_settings.http_cache_dir,
                cache_ttl_seconds=fetch_settings.http_cache_ttl_seconds,
            )
        kma_df = read_kma_csv(kma_forecast_text, fetch_settings, forecast_only=True)
        log_timing("load KMA forecast", stage_started_at, rows=len(kma_df))

        stage_started_at = time.monotonic()
        fetch_settings = settings_with_bdeck_analysis_if_needed(session, fetch_settings, kma_df)
        log_timing("resolve analysis point", stage_started_at)
        if kma_df.empty and not fetch_settings.skip_atcf:
            print(
                "KMA APIHUB has no forecast model rows for this storm/time; "
                "trying DMDW/ATCF guidance sources."
            )
        stage_started_at = time.monotonic()
        dmdw_df = read_dmdw_data(fetch_settings)
        log_timing("load DMDW guidance", stage_started_at, rows=len(dmdw_df))

        stage_started_at = time.monotonic()
        polarwx_df = empty_polarwx_frame() if fetch_settings.skip_atcf else fetch_polarwx_data(session, fetch_settings)
        log_timing("load POLARWX guidance", stage_started_at, rows=len(polarwx_df))

        stage_started_at = time.monotonic()
        smca_df = empty_smca_frame() if fetch_settings.skip_atcf else fetch_smca_data(session, fetch_settings)
        log_timing("load SMCA.FUN guidance", stage_started_at, rows=len(smca_df))

        stage_started_at = time.monotonic()
        atcf_df = empty_atcf_frame() if fetch_settings.skip_atcf else fetch_atcf_data(session, fetch_settings)
        log_timing("load ATCF guidance", stage_started_at, rows=len(atcf_df))

        stage_started_at = time.monotonic()
        source_availability_raw_df = source_availability_frame(kma_df, dmdw_df, polarwx_df, smca_df, atcf_df, fetch_settings)
        df = normalize_track_data(kma_df, dmdw_df, polarwx_df, smca_df, atcf_df, fetch_settings)
        log_timing("normalize guidance", stage_started_at, rows=len(df))

        stage_started_at = time.monotonic()
        try:
            write_source_availability_outputs(
                raw_df=source_availability_raw_df,
                selected_df=df,
                settings=fetch_settings,
                fetch_hours=fetch_hour,
                requested_hours=tuple(requested_hours),
            )
        except Exception as exc:
            print(f"Warning: failed to write source availability metadata: {exc}")
        log_timing("write source availability", stage_started_at)

        stage_started_at = time.monotonic()
        kma_past_text = read_text_file(fetch_settings.kma_past_text_path)
        if kma_past_text is None:
            kma_past_text = fetch_kma_text(
                session,
                kma_url(fetch_settings, "0"),
                kma_fallback_url(fetch_settings, "0"),
                label="typ_gts_now mode=0",
                retries=3,
                timeout=10,
                retry_delay=3,
                encoding="cp949",
                cache_dir=fetch_settings.http_cache_dir,
                cache_ttl_seconds=fetch_settings.http_cache_ttl_seconds,
            )
        past_kma = build_past_kma_track(read_kma_csv(kma_past_text, fetch_settings, forecast_only=False))
        log_timing("load KMA past track", stage_started_at, rows=len(past_kma))

    stage_started_at = time.monotonic()
    past_kma = update_and_merge_past_track(
        df=df,
        official_past=past_kma,
        settings=fetch_settings,
    )
    log_timing("update track history", stage_started_at, rows=len(past_kma))

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
        log_timing("VTG.py total", main_started_at)
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

        stage_started_at = time.monotonic()
        target = plot_guidance(hour_df, past_kma, hour_settings, intensity)
        log_timing(
            f"render {fcst_hours}h image",
            stage_started_at,
            models=len(plotted_model_names(hour_df, hour_settings)),
        )
        if metadata_path:
            stage_started_at = time.monotonic()
            write_run_metadata(
                metadata_path,
                target=target,
                df=hour_df,
                settings=hour_settings,
                intensity=intensity,
            )
            log_timing(f"write {fcst_hours}h metadata", stage_started_at)
        print(f"Saved: {target}")

    log_timing("VTG.py total", main_started_at)


if __name__ == "__main__":
    main()
