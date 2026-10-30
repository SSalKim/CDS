"""Offline, fixed-input pixel parity checks for the two production VTG runners."""

import argparse
import hashlib
import json
import math
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

import VTG
from vtg_render_runtime import check_runtime, runtime_report


def fixture():
    cycle = datetime(2026, 10, 30, 12)
    settings = VTG.Settings(data_time="202610301200", typ_number=31, typ_name="IN-FA",
                            typ_name_ko="인파", storm_year="2026", atcf_id="wp302026")
    names = [model["name"] for model in VTG.MODEL_INFO if model["name"] in VTG.active_model_names(settings)
             and model["name"] not in {"KIM_6h", "KIM_GFDL_6h"}]
    rows = []
    for index, name in enumerate(["KMA", *names]):
        for hour in range(0, 241 - index % 4 * 6, 6):
            fraction = hour / 240
            rows.append({
                "FT": int(hour > 0), "YY": 2026, "TYP": 31, "SEQ": 0, "TMD": hour,
                "TYP_TM(UTC)": "202610301200",
                "FT_TM(UTC)": (cycle + timedelta(hours=hour)).strftime("%Y%m%d%H%M"),
                "LAT": round(22 + hour * 0.11 + (index % 7 - 3) * 5 * fraction ** 2, 4),
                "LON": round(140 - 18 * math.sin(fraction * 2.5) + hour * 0.13
                             + (index % 5 - 2) * 3 * fraction ** 2, 4),
                "PS": 970 - index % 20 + hour // 24, "WS": 35,
                "SRC": name, VTG.DATA_SOURCE_COLUMN: "APIHUB",
            })
    past = [{"LON": round(140 + h / 10, 4), "LAT": round(22 - h / 12, 4),
             "FT_TIME": (cycle - timedelta(hours=h)).isoformat()} for h in range(72, -1, -6)]
    return rows, past


def image_signature(path):
    with Image.open(path) as im:
        rgba = np.asarray(im.convert("RGBA"))
        return {"size": list(im.size), "pixel_sha256": hashlib.sha256(rgba.tobytes()).hexdigest(),
                "file_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "min_alpha": int(rgba[:, :, 3].min())}


def render_fixture(output):
    errors = check_runtime()
    if errors:
        raise RuntimeError("; ".join(errors))
    output.mkdir(parents=True, exist_ok=True)
    rows, past_rows = fixture()
    inputs = json.dumps({"rows": rows, "past": past_rows}, sort_keys=True, separators=(",", ":")).encode()
    (output / "fixture.json").write_bytes(inputs)
    frame = pd.DataFrame(rows)
    past = pd.DataFrame(past_rows)
    past["FT_TIME"] = pd.to_datetime(past.FT_TIME)
    VTG.configure_plot_fonts()
    images = {}
    for horizon in (120, 240):
        settings = VTG.Settings(data_time="202610301200", typ_number=31, typ_name="IN-FA",
                                typ_name_ko="인파", storm_year="2026", atcf_id="wp302026",
                                fcst_hours=horizon, output_root=output, show_plot=False, overwrite_output=True)
        path = VTG.plot_guidance(frame[frame.TMD.le(horizon)], past, settings, "TYP")
        target = output / f"{horizon}h.png"
        path.replace(target)
        images[target.name] = image_signature(target)
        if images[target.name]["min_alpha"] != 255:
            raise RuntimeError("Rendered PNG has transparent pixels")
    maps = Path(VTG.cartopy_config["data_dir"])
    assets = {p.relative_to(maps).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted((maps / "shapefiles").rglob("*"))
              if p.suffix in {".shp", ".shx", ".dbf", ".prj", ".cpg"}}
    report = {"runtime": runtime_report(), "input_sha256": hashlib.sha256(inputs).hexdigest(),
              "map_assets": assets, "images": images}
    (output / "report.json").write_text(json.dumps(report, sort_keys=True, indent=2))
    print(json.dumps(report, sort_keys=True))


def compare(left, right):
    reports = [json.loads((p / "report.json").read_text()) for p in (left, right)]
    for key in ("runtime", "input_sha256", "map_assets"):
        if reports[0][key] != reports[1][key]:
            raise RuntimeError(f"Runner parity mismatch: {key}")
    for name in ("120h.png", "240h.png"):
        a, b = (reports[i]["images"][name] for i in (0, 1))
        if a["size"] != b["size"] or a["pixel_sha256"] != b["pixel_sha256"]:
            raise RuntimeError(f"Runner pixel mismatch: {name}")
        print(f"IDENTICAL {name}: {a['size']}, {a['pixel_sha256']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--compare", nargs=2, type=Path)
    args = parser.parse_args()
    if args.compare:
        compare(*args.compare)
    elif args.output:
        render_fixture(args.output)
    else:
        parser.error("--output or --compare is required")


if __name__ == "__main__":
    main()
