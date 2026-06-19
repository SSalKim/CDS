from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from vtg_auto import (
    CycleWindow,
    load_json,
    root_manifest_payload,
    split_manifest_inventory_count,
    write_json,
    write_split_manifest_files,
)


PROJECT_ROOT = Path(__file__).resolve().parent


def option_value(tokens: list[str], names: tuple[str, ...], default: str | None = None) -> str | None:
    for index, token in enumerate(tokens):
        for name in names:
            if token == name and index + 1 < len(tokens):
                return tokens[index + 1]
            if token.startswith(f"{name}="):
                return token.split("=", 1)[1]
    return default


def has_option(tokens: list[str], names: tuple[str, ...]) -> bool:
    return any(token == name or token.startswith(f"{name}=") for token in tokens for name in names)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one manual VTG command from GitHub workflow_dispatch.")
    parser.add_argument("--vtg-args", required=True, help="Arguments to pass to VTG.py, e.g. --typ-number 6 --typ-name JANGMI.")
    parser.add_argument("--auth-key", default=os.getenv("KMA_APIHUB_AUTH_KEY", ""))
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--output-root", type=Path, default=PROJECT_ROOT / "VTG_IMG")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.auth_key:
        raise SystemExit("KMA_APIHUB_AUTH_KEY is required.")

    tokens = shlex.split(args.vtg_args)
    data_time = option_value(tokens, ("--data-time",), "")
    if not data_time:
        raise SystemExit("manual VTG args must include --data-time YYYYmmddHHMM.")

    typ_number = int(option_value(tokens, ("--typ-number",), "0") or 0)
    storm_stage = (option_value(tokens, ("--storm-stage",), "TYP") or "TYP").upper()
    fcst_hours = int(option_value(tokens, ("--fcst-hours",), "120") or 120)
    year = data_time[:4]
    metadata_name = f"{data_time}_{storm_stage.lower()}_{year}_{typ_number:02d}_{fcst_hours}h.json"
    metadata_path = args.output_root / "metadata" / metadata_name

    command = [args.python, str(PROJECT_ROOT / "VTG.py"), *tokens]
    if not has_option(tokens, ("--output-root",)):
        command.extend(["--output-root", str(args.output_root)])
    if not has_option(tokens, ("--metadata-path",)):
        command.extend(["--metadata-path", str(metadata_path)])
    if not has_option(tokens, ("--auth-key",)):
        command.extend(["--auth-key", args.auth_key])
    if not has_option(tokens, ("--overwrite",)):
        command.append("--overwrite")
    if not has_option(tokens, ("--no-show",)):
        command.append("--no-show")

    completed = subprocess.run(command, cwd=PROJECT_ROOT, text=True, capture_output=True, check=False)
    print(completed.stdout)
    print(completed.stderr, file=sys.stderr)
    if completed.returncode:
        return completed.returncode

    metadata = load_json(metadata_path, {})
    updated_at_utc = datetime.now(timezone.utc).strftime("%Y%m%d%H%M")
    run_entries = [
        {
            "job": {
                "stage": metadata.get("storm_stage", storm_stage),
                "year": int(metadata.get("storm_year") or year),
                "data_time": metadata.get("data_time", data_time),
                "td_number": metadata.get("typ_number") if metadata.get("storm_stage") == "TD" else None,
                "linked_td_number": metadata.get("linked_td_number"),
                "typ_number": metadata.get("typ_number", typ_number),
                "typ_name_ko": metadata.get("typ_name_ko", ""),
                "typ_name": metadata.get("typ_name", ""),
                "typ_en": metadata.get("typ_name", ""),
                "atcf_id": metadata.get("atcf_id"),
                "fcst_hours": metadata.get("fcst_hours", fcst_hours),
                "skip_atcf": bool(metadata.get("skip_atcf")),
            },
            "window": {"data_time": metadata.get("data_time", data_time)},
            "result": {"status": "manual", "metadata": metadata},
        }
    ]
    write_split_manifest_files(args.output_root, run_entries, updated_at_utc=updated_at_utc)
    data_time_text = str(metadata.get("data_time") or data_time)
    window = CycleWindow(
        data_time=data_time_text,
        cycle_time_utc=data_time_text,
        start_utc=data_time_text,
        end_utc=data_time_text,
    )
    manifest = root_manifest_payload(
        updated_at_utc=updated_at_utc,
        windows=[window],
        complete_model_count=0,
        final_check_before_window_end_minutes=0,
        runs=run_entries,
        output_root=args.output_root,
        inventory_count=split_manifest_inventory_count(args.output_root),
    )
    manifest["manual"] = True
    manifest["manual_args"] = args.vtg_args
    write_json(args.output_root / "manifest.json", manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
