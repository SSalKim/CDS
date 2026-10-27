"""Read-only WeatherMesh API checks, separate from VTG production ingestion."""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.request import build_opener

from windborne import (
    WindborneError as ProbeError, NoRedirects, parse_cycle, parse_time,
    parse_coord, request_text, request_json, summarize_deck,
)


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
        started = time.monotonic()
        try:
            result = probe_cycle(opener, key, storm_id, cycle, args.output_dir)
        except ProbeError as error:
            result = {"requested_cycle": cycle, "status": "error", "error": str(error)}
        result["elapsed_seconds"] = round(time.monotonic() - started, 3)
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
