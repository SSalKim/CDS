"""Read-only WeatherMesh API checks, separate from VTG production ingestion."""

import argparse
import csv
import hashlib
import io
import json
import math
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener


BASE_URL = "https://api.windbornesystems.com/forecasts/v1/wm-6/tropical_cyclones"
MAX_RESPONSE_BYTES = 20 * 1024 * 1024


class ProbeError(Exception):
    pass


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Never forward the provider's Authorization header to a redirect target.
        return None


def parse_cycle(value):
    if not re.fullmatch(r"\d{10}", value):
        raise ValueError("Expected UTC cycle YYYYmmddHH")
    return datetime.strptime(value, "%Y%m%d%H").replace(tzinfo=timezone.utc)


def parse_time(value):
    if not isinstance(value, str):
        raise ProbeError("Invalid API timestamp")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ProbeError("Invalid API timestamp") from None
    if result.tzinfo is None:
        raise ProbeError("API timestamp has no timezone")
    return result.astimezone(timezone.utc)


def request_text(opener, key, path, params=None):
    url = BASE_URL + path
    if params:
        url += "?" + urlencode(params)
    request = Request(url, headers={
        "Authorization": "Bearer " + key,
        "User-Agent": "CDS-WeatherMesh-Probe/1.0",
    })
    try:
        with opener.open(request, timeout=60) as response:
            if response.status != 200:
                raise ProbeError(f"HTTP {response.status}")
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except HTTPError as error:
        error.close()
        raise ProbeError(f"HTTP {error.code}") from None
    except (URLError, TimeoutError, OSError):
        raise ProbeError("Network or TLS request failed") from None
    if len(raw) > MAX_RESPONSE_BYTES:
        raise ProbeError("Response exceeds size limit")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeError:
        raise ProbeError("Response is not UTF-8 text") from None
    if key in text:
        raise ProbeError("Response unexpectedly contains credential material")
    return text


def request_json(opener, key, path, params=None):
    try:
        result = json.loads(request_text(opener, key, path, params))
    except ValueError:
        raise ProbeError("Response is not valid JSON") from None
    if not isinstance(result, dict):
        raise ProbeError("Response is not a JSON object")
    return result


def parse_coord(value, latitude):
    match = re.fullmatch(r"(\d+)([NS])" if latitude else r"(\d+)([EW])", value)
    if not match:
        raise ProbeError("Invalid ATCF coordinate")
    coordinate = int(match[1]) / 10
    if coordinate > (90 if latitude else 180):
        raise ProbeError("ATCF coordinate outside valid range")
    return -coordinate if match[2] in "SW" else coordinate


def summarize_deck(text, storm_id, cycle):
    mean = {}
    models = set()
    row_count = 0
    for row in csv.reader(io.StringIO(text)):
        if not row or not any(field.strip() for field in row):
            continue
        if len(row) < 10:
            raise ProbeError("Response is not an ATCF A-deck")
        row = [field.strip() for field in row]
        if row[0] != storm_id[:2] or row[1] != storm_id[2:4]:
            raise ProbeError("ATCF storm does not match requested storm")
        if row[2] != cycle:
            raise ProbeError("ATCF cycle does not match requested cycle")
        model = row[4]
        if not re.fullmatch(r"WMSH|W\d{3}", model):
            raise ProbeError("Unexpected WeatherMesh model code")
        lat = parse_coord(row[6], True)
        lon = parse_coord(row[7], False)
        try:
            lead = int(row[5])
            wind = float(row[8])
            pressure = float(row[9])
        except ValueError:
            raise ProbeError("Invalid ATCF numeric fields") from None
        if lead < 0 or not all(math.isfinite(value) for value in (wind, pressure)):
            raise ProbeError("Invalid ATCF lead or intensity")
        models.add(model)
        row_count += 1
        if model == "WMSH":
            point = (lat, lon, wind, pressure)
            if lead in mean and mean[lead] != point:
                raise ProbeError("Conflicting WMSH points at the same lead")
            mean[lead] = point
    if not row_count:
        raise ProbeError("Empty ATCF response")
    hours = sorted(mean)
    pressures = [point[3] for point in mean.values() if point[3] > 0]
    winds = [point[2] for point in mean.values() if point[2] >= 0]
    return {
        "atcf_cycle": cycle,
        "rows": row_count,
        "member_count": len(models - {"WMSH"}),
        "mean_points": len(hours),
        "mean_first_hour": hours[0] if hours else None,
        "mean_last_hour": hours[-1] if hours else None,
        "mean_step_hours": sorted({b - a for a, b in zip(hours, hours[1:])}),
        "mean_min_pressure_hpa": min(pressures) if pressures else None,
        "mean_max_wind_kt": max(winds) if winds else None,
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    }


def probe_cycle(opener, key, storm_id, cycle, output_dir):
    requested = parse_cycle(cycle)
    params = {"initialization_time": cycle, "format": "json"}
    detail = request_json(opener, key, "/" + storm_id, params)
    if detail.get("tropical_cyclone_id") != storm_id:
        raise ProbeError("JSON storm does not match requested storm")
    initialization = parse_time(detail.get("initialization_time"))
    forecast_zero = parse_time(detail.get("forecast_zero"))
    if initialization != requested:
        raise ProbeError("API returned a different initialization time")
    # These probes use exact 00/06/12/18 UTC cycles, not later hourly flavors.
    if forecast_zero != requested:
        raise ProbeError("API forecast zero differs from requested cycle")
    params["format"] = "deck"
    deck = request_text(opener, key, "/" + storm_id, params)
    summary = summarize_deck(deck, storm_id, cycle)
    if not summary["mean_points"]:
        raise ProbeError("No WMSH ensemble-mean points in A-deck")
    filename = f"{storm_id}_{cycle}.atcf"
    (output_dir / filename).write_text(deck, encoding="utf-8", newline="")
    return {
        "status": "ok",
        "requested_cycle": cycle,
        "initialization_time": initialization.isoformat(),
        "forecast_zero": forecast_zero.isoformat(),
        "file": filename,
        **summary,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--storm-id", default="WP302026")
    parser.add_argument("--cycles", default="2026102612,2026102618,2026102700")
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    storm_id = args.storm_id.strip().upper()
    cycles = list(dict.fromkeys(value.strip() for value in args.cycles.split(",")))
    if not re.fullmatch(r"(?:WP|EP|CP|AL|IO|SH)\d{6}", storm_id):
        parser.error("Invalid operational ATCF ID")
    if not 1 <= len(cycles) <= 8:
        parser.error("Provide between one and eight cycles")
    try:
        for cycle in cycles:
            parse_cycle(cycle)
            if cycle[-2:] not in {"00", "06", "12", "18"}:
                raise ValueError("Only standard 6-hour UTC cycles are supported")
    except ValueError as error:
        parser.error(str(error))
    key = os.environ.get("WB_API_KEY", "").strip()
    if not key:
        print("WB_API_KEY is not configured", file=sys.stderr)
        return 1
    args.output_dir.mkdir(parents=True, exist_ok=True)
    opener = build_opener(NoRedirects())
    report = {"storm_id": storm_id, "results": []}
    try:
        times = request_json(opener, key, f"/{storm_id}/init_times")
        if times.get("tropical_cyclone_id") != storm_id:
            raise ProbeError("Initialization index storm mismatch")
        report["latest_available_initialization"] = parse_time(times.get("latest")).isoformat()
        available_values = times.get("available")
        if not isinstance(available_values, list):
            raise ProbeError("Invalid initialization index")
        available = {parse_time(value) for value in available_values}
        report["listed_cycles"] = [cycle for cycle in cycles if parse_cycle(cycle) in available]
    except ProbeError as error:
        report["availability_error"] = str(error)
    for cycle in cycles:
        try:
            result = probe_cycle(opener, key, storm_id, cycle, args.output_dir)
        except ProbeError as error:
            result = {"requested_cycle": cycle, "status": "error", "error": str(error)}
        report["results"].append(result)
        print(json.dumps(result, sort_keys=True), flush=True)
    content = json.dumps(report, indent=2, sort_keys=True) + "\n"
    (args.output_dir / "report.json").write_text(content, encoding="utf-8")
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as stream:
            stream.write("## WeatherMesh exact-cycle probe\n\n```json\n" + content + "```\n")
    return 0 if all(item["status"] == "ok" for item in report["results"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
