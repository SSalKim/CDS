"""Pure scheduling, product, and retention policy for the public chart pipeline."""
from datetime import datetime, timedelta, timezone
import re

from .dates import parse_cycle

RETENTION = {"aifs": 9, "gfs": 9, "aigfs": 9, "cmc": 5}
CYCLE_STEP = {"aifs": 6, "gfs": 6, "aigfs": 6, "cmc": 12}
TITLES = {"aifs": "ECMWF AIFS-Single (N320)", "gfs": "NCEP GFS (C768 L127)",
          "aigfs": "NCEP AIGFS (0.25\u00b0)", "cmc": "CMC GDPS (GEM 0.135\u02da L84)"}
MAX_IMAGE_BYTES = 12_000_000_000
PIPELINE_VERSION = 2
KEY_PATTERN = re.compile(r"(aifs|gfs|aigfs|cmc)/(\d{10})/(\d{3})/([a-z0-9_]+)/(asia|hkor)")


def hours(model):
    step = 6 if model in {"aifs", "aigfs"} else 3
    if model not in RETENTION:
        raise ValueError("Unknown model")
    return tuple(range(0, 85, step)) + (90, 96) + tuple(range(108, 241, 12))


def cycle_candidates(model, now=None, depth=2):
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("Timezone-aware time required")
    now = now.astimezone(timezone.utc)
    step = CYCLE_STEP[model]
    latest = now.replace(hour=now.hour // step * step, minute=0, second=0, microsecond=0)
    return [(latest - timedelta(hours=step * n)).strftime("%Y%m%d%H") for n in range(depth)]


def products(cycle):
    upper = "gph300" if int(cycle[4:6]) in (11, 12, 1, 2, 3, 4) else "gph200"
    return (upper, "gph500", "gph700", "ept850", "ept925", "wnd850", "wnd925")


def winter(model, cycle):
    return model != "aigfs" and int(cycle[4:6]) in (10, 11, 12, 1, 2, 3, 4)


def key(model, cycle, hour, product, domain):
    value = f"{model}/{cycle}/{hour:03}/{product}/{domain}"
    if not KEY_PATTERN.fullmatch(value) or hour not in hours(model):
        raise ValueError("Invalid chart identity")
    if product not in set(products(cycle)) | {"surfce", "acptot", "acptot1", "acrain", "acrain1"}:
        raise ValueError("Product is outside the active nine-product catalog")
    if parse_cycle(cycle).hour % CYCLE_STEP[model]:
        raise ValueError("Invalid model cycle")
    return value


def expected_keys(model, cycle, hour):
    keys = {key(model, cycle, hour, product, domain)
            for product in products(cycle) for domain in ("asia", "hkor")}
    keys.add(key(model, cycle, hour, "surfce", "asia"))
    # Korea's rain-only aliases share one physical file. +000h is MSLP only.
    for product in ("surfce", "acptot", "acptot1"):
        keys.add(key(model, cycle, hour, product, "hkor"))
    if hour:
        for product in ("acrain", "acrain1"):
            keys.add(key(model, cycle, hour, product, "hkor"))
    return keys


def row_key(row):
    return key(row["model"], row["cycle"], int(row["hour"]), row["product"], row["domain"])


def unique_bytes(rows):
    files = {}
    for row in rows:
        file_id = str(row["file_id"])
        size = int(row["size"])
        if size < 1 or file_id in files and files[file_id] != size:
            raise ValueError("Inconsistent Drive image size")
        files[file_id] = size
    return sum(files.values())


def retain(rows, max_bytes=MAX_IMAGE_BYTES):
    """Evict whole old cycles, deduplicating aliases and preserving latest per model."""
    by_key = {row_key(row): dict(row) for row in rows}
    cycles = {model: sorted({row["cycle"] for row in by_key.values() if row["model"] == model}, reverse=True)
              for model in RETENTION}
    selected = {(model, cycle) for model, values in cycles.items() for cycle in values[:RETENTION[model]]}

    def selected_rows():
        return [row for row in by_key.values() if (row["model"], row["cycle"]) in selected]

    while unique_bytes(selected_rows()) > max_bytes:
        removable = [(cycle, model) for model, cycle in selected
                     if sum(m == model for m, _ in selected) > 1]
        if not removable:
            raise ValueError("Latest cycles alone exceed the image budget; cleanup refused")
        cycle, model = min(removable)
        selected.remove((model, cycle))
    kept = sorted(selected_rows(), key=lambda row: row_key(row))
    retained_ids = {row["file_id"] for row in kept}
    delete_ids = sorted({row["file_id"] for row in by_key.values()} - retained_ids)
    return kept, delete_ids


def public_manifest(rows):
    rows = list(rows)
    public = [{k: row[k] for k in ("model", "cycle", "hour", "product", "domain", "url", "size", "sha256", "file_id")}
              for row in rows]
    for source, target in zip(rows, public):
        target["render_version"] = source.get("render_version", 0)
    return {"schema_version": 1, "pipeline_version": PIPELINE_VERSION,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "models": {model: {"title": TITLES[model], "published": any(r["model"] == model for r in public),
                                "retention_cycles": RETENTION[model]}
                       for model in RETENTION}, "charts": public}
