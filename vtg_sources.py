"""Shared VTG model/source registry; no rendering or network dependencies."""

import hashlib
from pathlib import Path


SOURCE_ORDER = ("APIHUB", "DMDW", "RAW.GITHUB", "POLARWX", "SMCA.FUN", "RAL.UCAR", "KNACKWX")
MODEL_SOURCE_PRIORITY_OVERRIDES: dict[str, tuple[str, ...]] = {}
PRESSURE_PREFERRED_MODELS = frozenset(("UKMO_EPS",))

# None disables a source. DMDW is a support flag: its layer IDs are mapped below.
# NOAA IDs are legacy aliases only; NOAA is not an active source in SOURCE_ORDER.
_MODEL_SOURCE_COLUMNS = ("name", "apihub", "dmdw", "raw_github", "polarwx", "smca", "ral_ucar", "knackwx", "noaa")
MODEL_SOURCES = [
    dict(zip(_MODEL_SOURCE_COLUMNS, row, strict=True))
    for row in (
        # name              apihub         dmdw   raw_github  polarwx          smca       ral_ucar  knackwx  noaa
        ("ECMWF",          "ECMWF",       True,  None,       "ecm",           "ECMWF",   None,     "ECMF",  "ECMF"),
        ("ECMWF_EPS",      "ECMWF_EPS",   True,  None,       "eps_mean",      "ECMWFM",  None,     "EEMN",  "EEMN"),
        ("KIM_3h",         "KIM_3h",      True,  None,       None,            None,      None,     None,    None),
        ("KIM_6h",         "KIM_6h",      True,  None,       None,            None,      None,     None,    None),
        ("KIM_GFDL_6h",    "KIM_GFDL_6h", False, None,       None,            None,      None,     None,    None),
        ("KIM_EPS",        "KIM_EPS",     True,  None,       None,            None,      None,     None,    None),
        ("UM",             "UM",          False, None,       None,            None,      None,     None,    None),
        ("UM_GFDL_6h",     "UM_GFDL_6h",  False, None,       None,            None,      None,     None,    None),
        ("UM_KEPS",        "UM_KEPS",     False, None,       None,            None,      None,     None,    None),
        ("UKM",            "UKX",         True,  None,       "ukmet",         None,      "UKM",    "UKM",   "UKM"),
        ("UKMO_EPS",       "EGRR_EPS",    False, None,       "ukmet_mean",    None,      "UEMN",   "UEMN",  "UEMN"),
        ("GFS",            "GFS",         True,  None,       "gfs",           "GFS",     "AVNO",   "AVNO",  "AVNO"),
        ("GFS_EPS",        "GFS_EPS",     True,  None,       "gefs_mean",     "GEFSM",   "AEMN",   "AEMN",  "AEMN"),
        ("CMC",            "CMC",         True,  None,       "cmc",           None,      "CMC",    "CMC",   "CMC"),
        ("CMC_EPS",        "CMC_EPS",     True,  None,       "cmc_mean",      None,      "CEMN",   "CEMN",  "CEMN"),
        ("JGSM",           "JGSM",        True,  None,       None,            None,      "JGSM",   "JGSM",  "JGSM"),
        ("TEPS",           "TEPS",        True,  None,       None,            None,      "JENS",   "JENS",  "JENS"),
        ("NAVGEM",         "NAVGEM",      True,  None,       None,            None,      "NVGM",   "NVGM",  "NVGM"),
        ("FNMOC_EPS",      "FNMOC_EPS",   True,  None,       None,            None,      "NEMN",   "NEMN",  "NEMN"),
        ("ICON",           None,          False, None,       "icon",          None,      None,     None,    None),
        ("ICON_EPS",       None,          False, None,       "icon_ens_mean", None,      None,     None,    None),
        ("CTCX",           None,          False, None,       None,            None,      "CTCX",   "CTCX",  "CTCX"),
        ("COAMPS_EPS",     None,          False, None,       None,            None,      "CTMN",   "CTMN",  "CTMN"),
        ("AFUM",           None,          False, None,       None,            None,      None,     None,    "AFUM"),
        ("HWRF",           "HWRF",        True,  None,       "hwrf",          None,      "HWRF",   "HWRF",  "HWRF"),
        ("HAFS",           "HAFS",        True,  None,       "hafsa",         None,      "HFSA",   "HFSA",  "HFSA"),
        ("ECMWF_AIFS",     "ECMWF_AIFS",  True,  None,       "aifs",          "AIFS",    None,     "AIFS",  "AIFS"),
        ("ECMWF_AIFS_EPS", None,          True,  None,       "aifs_ens_mean", "AIFSM",   None,     "EAIM",  "EAIM"),
        ("AGFS",           None,          False, None,       "aigfs",         "AIGFS",   None,     "AGFS",  "AGFS"),
        ("AIGEFS",         None,          False, None,       None,            "AIGEFSM", None,     "AIMN",  "AIMN"),
        ("AICON",          None,          False, None,       None,            "AICON",   None,     None,    None),
        ("IFEC_AI",        "IFEC_AI",     False, None,       None,            None,      None,     None,    None),
        ("IFKM_AI",        "IFKM_AI",     False, None,       None,            None,      None,     None,    None),
        ("FNEC_AI",        "FNEC_AI",     False, None,       None,            None,      None,     None,    None),
        ("FNKM_AI",        "FNKM_AI",     False, None,       None,            None,      None,     None,    None),
        ("FNUM_AI",        "FNUM_AI",     False, None,       None,            None,      None,     None,    None),
        ("PGEC_AI",        "PGEC_AI",     False, None,       None,            None,      None,     None,    None),
        ("PGKM_AI",        "PGKM_AI",     False, None,       None,            None,      None,     None,    None),
        ("PGUM_AI",        "PGUM_AI",     False, None,       None,            None,      None,     None,    None),
        ("GCEC_AI",        "GCEC_AI",     False, None,       None,            None,      None,     None,    None),
        ("GCKM_AI",        "GCKM_AI",     False, None,       None,            None,      None,     None,    None),
        ("GCUM_AI",        "GCUM_AI",     False, None,       None,            None,      None,     None,    None),
        ("GENC",           None,          False, "GENC",     "gencast",       None,      None,     "GENC",  None),
        ("WNC",            None,          False, "FNV3",     "deepmind",      "WN2C",    None,     "FNV3",  "FGNE"),
        ("WNV3",           None,          False, "WNV3",     None,            "WN3C",    None,     "WNV3",  None),
        ("HKO_AREC",       "HKO_AREC",    False, None,       None,            None,      None,     None,    None),
        ("HKO_FXEC",       "HKO_FXEC",    False, None,       None,            None,      None,     None,    None),
        ("HKO_FWEC",       "HKO_FWEC",    False, None,       None,            None,      None,     None,    None),
    )
]
_MODEL_SOURCES_BY_NAME = {row["name"]: row for row in MODEL_SOURCES}
DMDW_ENABLED_MODEL_IDS = frozenset(row["name"] for row in MODEL_SOURCES if row["dmdw"])

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

# Alias order also determines preference within the same source.
_SOURCE_MODEL_EXTRA_ALIASES = {
    ("APIHUB", "ECMWF"): ("ECMWF_TIGGE", "ECM_SPR_D"),
    ("APIHUB", "ECMWF_EPS"): ("ECM_SPR_E",),
    ("APIHUB", "UM_KEPS"): ("KEPS",),
    ("NOAA", "UKM"): ("EGRR",),
    ("APIHUB", "GFS"): ("GFS_TIGGE", "NCEP_TIGGE"),
    ("APIHUB", "CMC"): ("CMSC",),
    ("APIHUB", "CMC_EPS"): ("CMSC_EPS",),
    ("APIHUB", "NAVGEM"): ("NOGAPS",),
    ("APIHUB", "GCEC_AI"): ("GPEC",),
    ("APIHUB", "GCKM_AI"): ("GPKM",),
    ("APIHUB", "GCUM_AI"): ("GPUM",),
    ("APIHUB", "ECMWF_AIFS"): ("ECMF_AIFS",),
}
_RAW_SOURCE_COLUMNS = {
    source: column for source, column in SOURCE_IDENTIFIER_COLUMNS.items()
    if source != "DMDW"
}
SOURCE_MODEL_IDS = {
    source: {
        row[column] for row in MODEL_SOURCES
        if (column := _RAW_SOURCE_COLUMNS.get(source)) and row.get(column)
    }
    for source in SOURCE_ORDER
}
MODEL_SOURCE_ALIASES = {
    row[column]: row["name"]
    for row in MODEL_SOURCES
    for column in _RAW_SOURCE_COLUMNS.values()
    if row.get(column)
}
MODEL_ALIAS_PRIORITIES: dict[str, int] = {}
for row in MODEL_SOURCES:
    for source, column in _RAW_SOURCE_COLUMNS.items():
        model_id = row.get(column)
        if not model_id:
            continue
        MODEL_ALIAS_PRIORITIES.setdefault(model_id, 0)
        alias_ids = [model_id[:-3]] if model_id.endswith("_AI") else []
        alias_ids.extend(_SOURCE_MODEL_EXTRA_ALIASES.get((source, model_id), ()))
        for priority, alias_id in enumerate(alias_ids, start=1):
            MODEL_SOURCE_ALIASES.setdefault(alias_id, row["name"])
            if source in SOURCE_MODEL_IDS:
                SOURCE_MODEL_IDS[source].add(alias_id)
            MODEL_ALIAS_PRIORITIES.setdefault(alias_id, priority)

RAW_GITHUB_MODELS = tuple(row["raw_github"] for row in MODEL_SOURCES if row["raw_github"])
_POLARWX_KEYS = {
    row["polarwx"].strip().lower(): row["name"] for row in MODEL_SOURCES if row["polarwx"]
}
_SMCA_KEYS = {
    row["smca"].strip().upper(): row["name"] for row in MODEL_SOURCES if row["smca"]
}
SMCA_PERSISTED_MODEL_IDS = ("AICON", "AIFSM", "AIGFS")
SMCA_SNAPSHOT_KEYS = {
    raw_model: f"smca_{raw_model.lower()}_snapshot_path"
    for raw_model in SMCA_PERSISTED_MODEL_IDS
}

DMDW_MODEL_MAP = {
    "CMC": "CMC",
    "CMC_EPS": "CMC_EPS",
    "EC_AIFS": "ECMWF_AIFS",
    "EC_AIFS_SINGLE": "ECMWF_AIFS",
    "ECMWF": "ECMWF",
    "ECMWF_AIFS": "ECMWF_AIFS",
    "ECMWF_EPS": "ECMWF_EPS",
    "ECMWF_HRES": "ECMWF",
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

DMDW_ENSEMBLE_MODELS = {
    "EC_AIFS": "ECMWF_AIFS_EPS",
    "ECMWF": "ECMWF_EPS",
    "CMC": "CMC_EPS",
    "GFS": "GFS_EPS",
    "KIM": "KIM_EPS",
    "FNMOC": "FNMOC_EPS",
}
ENSEMBLE_MEAN_MODEL_IDS = set(DMDW_ENSEMBLE_MODELS.values())


def polarwx_keys() -> dict[str, str]:
    return _POLARWX_KEYS.copy()


def smca_keys() -> dict[str, str]:
    return _SMCA_KEYS.copy()


def expected_raw_model_id(model_name: str, source_name: str) -> str:
    column = _RAW_SOURCE_COLUMNS.get(source_name)
    row = _MODEL_SOURCES_BY_NAME.get(model_name, {})
    return str(row.get(column) or "").strip()


def render_code_signature(project_root: Path) -> str:
    # Source-only edits must invalidate completed renders as they did in VTG.py.
    digest = hashlib.sha256()
    try:
        for filename in ("VTG.py", "vtg_sources.py", "polarwx_browser.py"):
            digest.update(filename.encode("utf-8") + b"\0")
            digest.update((project_root / filename).read_bytes())
        return digest.hexdigest()
    except OSError:
        return ""
