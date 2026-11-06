"""Read-only, bounded WeatherMesh gridded sample; never publishes CDS products."""
import argparse
import base64
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import resource
import sys
import time
import re
import zipfile
from urllib.error import HTTPError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener, urlopen

import numpy as np
import xarray as xr
from zarr.storage import ZipStore

API = "https://api.windbornesystems.com/models/v1/wm-6/gridded"
FIELDS = ("total_precipitation_3h", "geopotential", "temperature", "wind_u", "wind_v", "pressure_msl")
MAX_DOWNLOAD = 768 * 1024 * 1024


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def download(key, cycle, hour, target, metrics):
    params = {"variable": "all", "initialization_time": cycle.isoformat(),
              "forecast_hour": hour, "format": "zarr", "as_url": "true",
              "include_members": "false", "include_distribution": "false",
              "include_deterministic": "false"}
    request = Request(API + "?" + urlencode(params), headers={
        "Authorization": "Bearer " + key, "User-Agent": "CDS-WM6-Grid-Sample/1.0"})
    opener = build_opener(NoRedirect())
    metrics["authenticated_api_requests"] += 1
    try:
        with opener.open(request, timeout=90) as response:
            raw = response.read(1024 * 1024)
            metrics["api_response_bytes"] = len(raw)
            metadata = json.loads(raw)
    except HTTPError as error:
        status = error.code
        error.close()
        metrics["api_http_status"] = status
        raise RuntimeError(f"Gridded API HTTP {status}; no automatic retry") from None
    metrics["api_http_status"] = 200
    link = metadata.get("url")
    if not isinstance(link, str) or urlsplit(link).scheme != "https":
        raise RuntimeError("No HTTPS download URL returned")
    parts = metadata.get("parts")
    if isinstance(parts, list) and parts:
        safe_metadata = {k: v for k, v in metadata.items() if k not in {"url", "url_expires_at"}}
        (target.parent / "selection_manifest.json").write_text(json.dumps(safe_metadata, indent=2), encoding="utf-8")
        selected = [part for part in parts if needed_part(part["path"])]
        metrics["archive_entries"] = len(parts)
        metrics["selected_entries"] = len(selected)
        metrics["provider_subset_bytes"] = metadata.get("subset_bytes")
        with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_STORED) as output:
            for part in selected:
                path = part["path"]
                if path.startswith("/") or ".." in path.split("/") or "\\" in path:
                    raise RuntimeError("Unsafe Zarr entry path")
                if "inline" in part:
                    raw = base64.b64decode(part["inline"], validate=True)
                else:
                    start, end = part["range"]
                    expected = end - start + 1
                    if expected < 0 or metrics["download_bytes"] + expected > MAX_DOWNLOAD:
                        raise RuntimeError("Selected fields exceed 768 MiB sample budget")
                    metrics["storage_download_requests"] += 1
                    request = Request(link, headers={"Range": f"bytes={start}-{end}",
                                                    "User-Agent": "CDS-WM6-Grid-Sample/1.0"})
                    with urlopen(request, timeout=120) as response:
                        if response.status != 206:
                            raise RuntimeError("Storage did not honor byte-range selection")
                        raw = response.read(expected + 1)
                    metrics["download_bytes"] += len(raw)
                    if len(raw) != expected:
                        raise RuntimeError("Incorrect storage range length")
                output.writestr(path, raw)
        metrics["archive_bytes"] = target.stat().st_size
        return
    # Use a new, unauthenticated request; do not forward the API key to storage.
    metrics["storage_download_requests"] += 1
    with urlopen(Request(link, headers={"User-Agent": "CDS-WM6-Grid-Sample/1.0"}), timeout=180) as response:
        declared = int(response.headers.get("Content-Length", 0))
        metrics["declared_archive_bytes"] = declared
        if declared > MAX_DOWNLOAD:
            raise RuntimeError("Archive exceeds 768 MiB sample budget")
        with target.open("wb") as output:
            while chunk := response.read(1024 * 1024):
                metrics["download_bytes"] += len(chunk)
                if metrics["download_bytes"] > MAX_DOWNLOAD:
                    raise RuntimeError("Download exceeds 768 MiB sample budget")
                output.write(chunk)
    metrics["archive_bytes"] = target.stat().st_size


def needed_part(path):
    """Keep shared metadata/coordinates and requested fields, not other variables."""
    lower = path.lower()
    if lower.split("/")[-1].startswith(".") or lower.endswith("zarr.json"):
        return True
    if any(name in lower for name in FIELDS):
        return True
    return any(token in lower.split("/") for token in (
        "latitude", "longitude", "lat", "lon", "level", "levels", "pressure",
        "pressure_level", "time", "initialization_time", "forecast_hour"))


def find_coord(dataset, names):
    for name in names:
        if name in dataset.coords or name in dataset.variables:
            return name
    raise ValueError("Missing coordinate " + "/".join(names))


def select_field(dataset, name, lat_name, lon_name):
    candidates = [name, name + "_mean", "mean_" + name]
    variable = next((n for n in candidates if n in dataset.data_vars), None)
    if variable is None:
        raise ValueError("Missing ensemble-mean variable: " + name)
    field = dataset[variable]
    for dim in list(field.dims):
        if dim in (lat_name, lon_name):
            continue
        if dim.lower() in {"level", "pressure", "pressure_level", "isobaricinhpa", "isobaric", "plev"}:
            levels = np.asarray(field[dim].values, dtype=float)
            # Some containers use Pa rather than hPa for the vertical coordinate.
            target = 50000 if np.nanmax(levels) > 2000 else 500
            matches = np.flatnonzero(np.isclose(levels, target))
            if len(matches) != 1:
                raise ValueError("Exactly one 500 hPa level required")
            field = field.isel({dim: int(matches[0])})
        elif field.sizes[dim] == 1:
            field = field.isel({dim: 0})
        else:
            raise ValueError("Unexpected non-singleton dimension: " + dim)
    return field.transpose(lat_name, lon_name)


def extract(archive, output, cycle, hour, metrics):
    store = ZipStore(archive, mode="r")
    try:
        dataset = xr.open_zarr(store, consolidated=None, chunks=None)
        schema = {"dimensions": dict(dataset.sizes),
                  "coordinates": {n: {"shape": list(v.shape), "attrs": dict(v.attrs)}
                                  for n, v in dataset.coords.items()},
                  "variables": {n: {"dims": list(v.dims), "attrs": dict(v.attrs)}
                                for n, v in dataset.data_vars.items()},
                  "attrs": dict(dataset.attrs)}
        (output / "schema.json").write_text(json.dumps(schema, indent=2, default=str), encoding="utf-8")
        lat_name = find_coord(dataset, ("latitude", "lat"))
        lon_name = find_coord(dataset, ("longitude", "lon"))
        lat = np.asarray(dataset[lat_name].values, dtype=float)
        lon = np.asarray(dataset[lon_name].values, dtype=float) % 360
        if lat.ndim != 1 or lon.ndim != 1:
            raise ValueError("Expected rectilinear latitude/longitude grid")
        yi = np.flatnonzero((lat >= -5) & (lat <= 70))
        xi = np.flatnonzero((lon >= 45) & (lon <= 185))
        if len(yi) < 100 or len(xi) < 100:
            raise ValueError("Asia grid unexpectedly small")
        yi = yi[np.argsort(lat[yi])]
        xi = xi[np.argsort(lon[xi])]
        arrays = {"latitude": lat[yi], "longitude": lon[xi]}
        stats = {}
        for name in FIELDS:
            field = select_field(dataset, name, lat_name, lon_name)
            values = np.asarray(field.isel({lat_name: yi, lon_name: xi}).values, dtype=np.float32)
            if not np.isfinite(values).all():
                raise ValueError("Nonfinite grid values: " + name)
            arrays[name] = values
            stats[name] = {"min": float(values.min()), "max": float(values.max()),
                           "unit": str(field.attrs.get("units", field.attrs.get("unit", "")))}
        valid = cycle + timedelta(hours=hour)
        arrays["initialization_time"] = np.array(cycle.isoformat())
        arrays["valid_time"] = np.array(valid.isoformat())
        arrays["forecast_hour"] = np.array(hour)
        np.savez_compressed(output / "asia_fields.npz", **arrays)
        metrics["grid_shape"] = [len(yi), len(xi)]
        metrics["grid_statistics"] = stats
        metrics["regional_arrays_bytes"] = sum(a.nbytes for a in arrays.values())
        metrics["regional_npz_bytes"] = (output / "asia_fields.npz").stat().st_size
        dataset.close()
    finally:
        store.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cycle", required=True)
    parser.add_argument("--forecast-hour", type=int, default=24)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    cycle = datetime.strptime(args.cycle, "%Y%m%d%H").replace(tzinfo=timezone.utc)
    if not 3 <= args.forecast_hour <= 360 or args.forecast_hour % 3:
        parser.error("Use a 3-hour forecast step between +3 and +360")
    key = os.environ.get("WB_API_KEY", "").strip()
    if not key:
        parser.error("WB_API_KEY is not configured")
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    started, cpu = time.perf_counter(), time.process_time()
    metrics = {"model": "WeatherMesh-6", "statistic": "ensemble mean",
               "cycle": args.cycle, "forecast_hour": args.forecast_hour,
               "valid_time": (cycle + timedelta(hours=args.forecast_hour)).isoformat(),
               "authenticated_api_requests": 0, "storage_download_requests": 0,
               "download_bytes": 0, "status": "started",
               "billing_note": "HTTP counts are measured; provider quota debits and remaining quota are not exposed or inferred."}
    archive = output / "forecast.zarr.zip"
    try:
        before = time.perf_counter()
        download(key, cycle, args.forecast_hour, archive, metrics)
        metrics["fetch_seconds"] = round(time.perf_counter() - before, 3)
        print("Downloaded bytes:", metrics["download_bytes"], flush=True)
        before = time.perf_counter()
        extract(archive, output, cycle, args.forecast_hour, metrics)
        metrics["extract_seconds"] = round(time.perf_counter() - before, 3)
        metrics["status"] = "ok"
    except Exception as error:
        # Do not include URLs or exception payloads: signed storage links are secret.
        message = str(error)
        metrics["error"] = (message if isinstance(error, (ValueError, RuntimeError)) and "http" not in message.lower()
                            else type(error).__name__)
        print("Sample failed:", metrics["error"], flush=True)
        metrics["status"] = "error"
    finally:
        metrics["elapsed_seconds"] = round(time.perf_counter() - started, 3)
        metrics["cpu_seconds"] = round(time.process_time() - cpu, 3)
        metrics["peak_rss_bytes"] = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024)
        (output / "resource_usage.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        print(json.dumps(metrics, indent=2), flush=True)
    return 0 if metrics["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
