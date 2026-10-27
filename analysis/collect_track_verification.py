"""Read-only, exact-cycle historical track verification data collection.

No production manifests/images are written. Credentials are never persisted.
Raw forecasts are retained without motion/intensity QC to avoid skill selection bias.
"""

import argparse
import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path
import sys
import time
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from windborne import NoRedirects, WindborneError, parse_coord

STORMS = {
    "BAVI": dict(number=9, atcf="WP092026", start="2026070200", end="2026071306"),
    "CHAMPI": dict(number=30, atcf="WP292026", start="2026101506", end="2026102518"),
}
LEADS = (24, 48, 72, 120, 240)
MODELS = {
    "ECMWF": ("ECMWF", "ECMWF_TIGGE", "ECM_SPR_D"),
    "ECMWF_EPS": ("ECMWF_EPS", "ECM_SPR_E"),
    "KIM": ("KIM_3h", "KIM_6h"), "KIM_EPS": ("KIM_EPS",),
    "GFS": ("GFS", "GFS_TIGGE", "NCEP_TIGGE"), "GFS_EPS": ("GFS_EPS",),
    "CMC": ("CMC", "CMSC"), "CMC_EPS": ("CMC_EPS", "CMSC_EPS"),
    "ECMWF_AIFS": ("ECMWF_AIFS", "ECMF_AIFS"),
    "IFEC_AI": ("IFEC_AI", "IFEC"),
    "FNEC_AI": ("FNEC_AI", "FNEC"), "FNKM_AI": ("FNKM_AI", "FNKM"),
    "PGEC_AI": ("PGEC_AI", "PGEC"), "PGKM_AI": ("PGKM_AI", "PGKM"),
    "GCEC_AI": ("GCEC_AI", "GCEC", "GPEC"),
    "GCKM_AI": ("GCKM_AI", "GCKM", "GPKM"),
    "HKO_AREC": ("HKO_AREC",), "HKO_FXEC": ("HKO_FXEC",),
    "HKO_FWEC": ("HKO_FWEC",),
}
FIELDS = ("storm", "model", "source", "cycle", "lead", "valid_time", "lat", "lon",
          "raw_model", "storm_id", "reference", "sha256")


def dt(value):
    return datetime.strptime(str(value)[:10], "%Y%m%d%H").replace(tzinfo=timezone.utc)


def stamp(value):
    return value.strftime("%Y%m%d%H")


def cycles(spec):
    current = dt(spec["start"])
    # Later initializations cannot verify even the shortest requested lead.
    while current <= dt(spec["end"]) - timedelta(hours=min(LEADS)):
        yield stamp(current)
        current += timedelta(hours=6)


def valid_position(lat, lon):
    return all(math.isfinite(v) for v in (lat, lon)) and -90 <= lat <= 90 and -180 <= lon <= 180 and (lat, lon) != (0, 0)


def record(storm, model, source, cycle, lead, lat, lon, raw_model, storm_id, reference, digest):
    return dict(zip(FIELDS, (storm, model, source, cycle, lead,
        stamp(dt(cycle) + timedelta(hours=lead)), lat, lon, raw_model, storm_id, reference, digest)))


def parse_kma(text, storm, cycle, numbers, reference="", digest=""):
    selected = {}
    conflicts = set()
    aliases = {alias: (model, rank) for model, names in MODELS.items() for rank, alias in enumerate(names)}
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        row = [x.strip() for x in next(csv.reader([line]))] if "," in line else line.split()
        if len(row) < 19 or row[0] not in ("0", "1") or row[18] not in aliases:
            continue
        try:
            number, year, lead = int(row[2]), int(row[1]), int(row[4])
            if number not in numbers or year != int(cycle[:4]) or row[5] != cycle + "00":
                continue
            if not 0 <= lead <= 240 or row[6] != stamp(dt(cycle) + timedelta(hours=lead)) + "00":
                continue
            lat, lon = float(row[7]), float(row[8])
            if not valid_position(lat, lon):
                continue
        except (ValueError, OverflowError):
            continue
        model, alias_rank = aliases[row[18]]
        rank = (numbers.index(number), alias_rank)
        key = (model, lead)
        item = record(storm, model, "APIHUB", cycle, lead, lat, lon, row[18], number, reference, digest)
        previous = selected.get(key)
        if previous is None or rank < previous[0]:
            selected[key] = (rank, item)
            conflicts.discard(key)
        elif rank == previous[0] and (lat, lon) != (previous[1]["lat"], previous[1]["lon"]):
            conflicts.add(key)
    return [item for key, (_, item) in selected.items() if key not in conflicts], len(conflicts)


def parse_deck(text, storm, cycle, model, atcf, source, reference="", digest=""):
    selected, conflicts = {}, set()
    for row in csv.reader(io.StringIO(text)):
        row = [value.strip() for value in row]
        if len(row) < 10 or row[0] != atcf[:2] or row[1] != atcf[2:4] or row[2] != cycle or row[4] != model:
            continue
        try:
            lead = int(row[5])
            lat, lon = parse_coord(row[6], True), parse_coord(row[7], False)
            if not 0 <= lead <= 240 or not valid_position(lat, lon):
                continue
        except (ValueError, WindborneError):
            continue
        item = record(storm, model, source, cycle, lead, lat, lon, model, atcf, reference, digest)
        if lead in selected and (lat, lon) != (selected[lead]["lat"], selected[lead]["lon"]):
            conflicts.add(lead)
        selected[lead] = item
    return [item for lead, item in selected.items() if lead not in conflicts], len(conflicts)


def digest_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fetch(url, secrets=()):
    opener = build_opener(NoRedirects())
    try:
        with opener.open(Request(url, headers={"User-Agent": "CDS-historical-track-verification/1.0"}), timeout=30) as response:
            raw = response.read(20 * 1024 * 1024 + 1)
        if len(raw) > 20 * 1024 * 1024:
            return None, "size_limit"
        text = raw.decode("utf-8-sig")
        if any(key and key in text for key in secrets):
            return None, "credential_echo_rejected"
        if "<html" in text[:1000].lower() or "<!doctype" in text[:1000].lower():
            return None, "html_rejected"
        return text, "ok"
    except HTTPError as error:
        error.close()
        return None, f"HTTP_{error.code}"
    except (URLError, TimeoutError, OSError, UnicodeError):
        return None, "network_or_encoding_error"


def collect(storm, output):
    spec = STORMS[storm]
    folder = ROOT / "data" / "2026" / f"TYP_26{spec['number']:02d}_{storm}"
    output.mkdir(parents=True, exist_ok=True)
    raw_dir = output / "raw"
    raw_dir.mkdir(exist_ok=True)
    history = json.loads((folder / "metadata/track_history.json").read_text(encoding="utf-8"))
    observations = [p for p in history["points"] if spec["start"] <= p["time_utc"][:10] <= spec["end"]]
    (output / "observations.json").write_text(json.dumps(observations, indent=2), encoding="utf-8")
    keys = [os.getenv("KMA_APIHUB_AUTH_KEY", "").strip(), os.getenv("KMA_APIHUB_FALLBACK_AUTH_KEY", "").strip()]
    hosts = ["apihub-pub.kma.go.kr", "apihub.kma.go.kr"]
    audit, points = [], []
    for cycle in cycles(spec):
        numbers = [spec["number"]]
        meta_path = folder / "metadata/runs" / (cycle + "00_240h.json")
        if meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            number = meta.get("data_typ_number")
            if number and number not in numbers and meta.get("canonical_typ_number") == spec["number"]:
                numbers.append(number)
        kma_rows = []
        for host, key in zip(hosts, keys):
            if not key:
                audit.append(dict(storm=storm, cycle=cycle, source="APIHUB", endpoint=host, status="key_missing"))
                continue
            params = dict(src="", tm=cycle + "00", mode="2", disp="1", help="0", authKey=key)
            text, status = fetch(f"https://{host}/api/typ01/url/typ_gts_now.php?" + urlencode(params), keys)
            ref = f"raw/apihub_{cycle}.txt"
            if text is not None:
                rows, conflict = parse_kma(text, storm, cycle, numbers, ref, digest_text(text))
                if rows:
                    (output / ref).write_text(text, encoding="utf-8")
                    kma_rows = rows
                else:
                    status = "no_exact_storm_cycle_rows"
                audit.append(dict(storm=storm, cycle=cycle, source="APIHUB", endpoint=host, status=status,
                                  points=len(rows), conflicts=conflict, numbers=numbers))
            else:
                audit.append(dict(storm=storm, cycle=cycle, source="APIHUB", endpoint=host, status=status))
            time.sleep(0.5)
            if kma_rows:
                break
        points.extend(kma_rows)

        dmdw_count = 0
        dmdw_models = []
        candidates = [ROOT / "data/dmdw/2026" / cycle / f"typ_2026_{spec['number']:02d}.json"]
        for number in numbers[1:]:
            candidates += [ROOT / "data/dmdw/2026" / cycle / f"{stage}_2026_{number:02d}.json" for stage in ("td", "typ")]
        for path in candidates:
            if not path.exists():
                continue
            raw = path.read_text(encoding="utf-8")
            payload = json.loads(raw)
            if payload.get("source") != "DMDW" or payload.get("schema_version") != 2 or str(payload.get("cycle_utc")) != cycle + "00":
                continue
            models = payload.get("models", [])
            rows = []
            for point in payload.get("points", []):
                p = dict(zip(payload["point_columns"], point))
                m = models[p["model_index"]]
                if m.get("model_id") != "ECMWF_AIFS_EPS" or m.get("member_id") not in (None, "", "MEAN"):
                    continue
                lead = p["lead_hour"]
                if not 0 <= lead <= 240 or p["valid_time"] != stamp(dt(cycle) + timedelta(hours=lead)) + "00":
                    continue
                if not valid_position(float(p["lat"]), float(p["lon"])):
                    continue
                rows.append(record(storm, "ECMWF_AIFS_EPS", "DMDW", cycle, lead, p["lat"], p["lon"],
                    m["raw_model_id"], spec["number"], path.relative_to(ROOT).as_posix(), digest_text(raw)))
                if m not in dmdw_models:
                    dmdw_models.append(m)
            if rows:
                points.extend(rows)
                dmdw_count = len(rows)
                break
        audit.append(dict(storm=storm, cycle=cycle, source="DMDW", status="ok" if dmdw_count else "mean_unavailable",
                          points=dmdw_count, models=dmdw_models))

        for model in ("GENC", "FNV3", "WNV3"):
            date = dt(cycle)
            filename = f"{model}_{date:%Y_%m_%dT%H_00}_atcf_a_deck.txt"
            layouts = [f"{date:%Y/%m/%d}"] + ([f"{date:%Y_%m_%d}"] if model != "WNV3" else [])
            for layout in layouts:
                url = f"https://raw.githubusercontent.com/SSalKim/GDM/main/forecast_files/{layout}/{filename}"
                text, status = fetch(url)
                rows, conflicts = parse_deck(text, storm, cycle, model, spec["atcf"], "RAW.GITHUB", url, digest_text(text)) if text else ([], 0)
                audit.append(dict(storm=storm, cycle=cycle, source="RAW.GITHUB", model=model, reference=url,
                                  status=status if rows or text is None else "no_exact_storm_cycle_rows", points=len(rows), conflicts=conflicts))
                if rows:
                    (raw_dir / filename).write_text(text, encoding="utf-8")
                    points.extend(rows)
                    break
                time.sleep(0.1)

        (output / "audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
        with (output / "forecasts.csv").open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(points)
        print(f"{storm} {cycle}: APIHUB={len(kma_rows)} DMDW={dmdw_count}; total_points={len(points)}", flush=True)
    manifest = dict(storm=storm, spec=spec, leads=LEADS, collected_at=datetime.now(timezone.utc).isoformat(),
                    commit=os.getenv("GITHUB_SHA"), observation_history_sha256=hashlib.sha256((folder / "metadata/track_history.json").read_bytes()).hexdigest(),
                    cycles=list(cycles(spec)), forecast_points=len(points), observation_points=len(observations))
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--storm", choices=STORMS, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    collect(args.storm, args.output)
