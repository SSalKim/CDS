"""Collect requested Polarwx cycles outside the image-generation job."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import VTG
from polarwx_browser import capture_cycle, request_identity
from polarwx_cache import DEFAULT_ROOT, load_snapshot, save_snapshot, snapshot_is_fresh, write_json


def collect_requests(requests: list[tuple[str, str]], root: Path) -> dict:
    result = {"collected": [], "skipped": [], "failed": []}
    for storm, cycle in sorted(set(requests)):
        if snapshot_is_fresh(load_snapshot(root, storm, cycle), datetime.now(timezone.utc)):
            result["skipped"].append({"atcf_id": storm, "cycle": cycle, "reason": "fresh snapshot"})
            continue
        report = {}
        try:
            text = capture_cycle(storm, cycle, report=report)
            settings = VTG.Settings(atcf_id=storm, data_time=cycle + "00", fcst_hours=240)
            frame = VTG.read_polarwx_json(text, settings, atcf_id=storm)
            if not VTG.has_forecast_points(frame):
                raise ValueError("No usable exact-cycle Raw forecast in the page response")
            valid_models = {name for name, track in frame.groupby("SRC") if VTG.has_forecast_points(track)}
            valid_keys = {key for key, name in VTG.polarwx_keys().items() if name in valid_models}
            path = save_snapshot(root, storm, cycle, text, valid_model_keys=valid_keys)
            saved = load_snapshot(root, storm, cycle)
            report.update(path=str(path), models=int(frame["SRC"].nunique()), points=len(frame),
                          pressure_points=int(frame["PS"].gt(0).sum()), retained_models=saved["retained_models"])
            result["collected"].append(report)
        except Exception as exc:
            result["failed"].append({"atcf_id": storm, "cycle": cycle, "error": str(exc)})
            print(f"POLARWX prefetch failed for {storm} {cycle}: {exc}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--requests-dir", type=Path)
    parser.add_argument("--atcf-id")
    parser.add_argument("--cycle")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    requests = []
    if args.atcf_id or args.cycle:
        requests.append(request_identity(args.atcf_id or "", args.cycle or ""))
    elif args.requests_dir:
        for path in sorted(args.requests_dir.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            requests.append(request_identity(payload["atcf_id"], payload["cycle"]))
    if len(requests) > 24:
        raise SystemExit("Too many browser requests in one collection job")
    result = collect_requests(requests, args.output_root)
    write_json(args.report, result)
    print(json.dumps(result, indent=2))
    if result["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
