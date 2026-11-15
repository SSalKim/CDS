"""Native public GRIB grids, with explicit cycles, units and accumulation windows."""
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import time

import eccodes as ec
import numpy as np
import requests
from urllib3.util.retry import Retry

GRAVITY = 9.80665
LEVELS = (200, 300, 500, 700, 850, 925)
BOUNDS = (-5, 85, 20, 220)
MODELS = {
    "aifs": {"name": "ECMWF AIFS-Single (N320)", "grid": .25, "interval": 6, "rain": 6,
             "attribution":"Data Sourced from ECMWF (CC BY 4.0)"},
    "gfs": {"name": "NCEP GFS (C768 L127)", "grid": .25, "interval": 3, "rain": 3,
            "attribution":"Data Sourced from NOAA NCEP","thermal_merge_version":3,"precipitation_source":"sflux"},
    "aigfs": {"name": "NCEP AIGFS (0.25\u00b0)", "grid": .25, "interval": 6, "rain": 6,
              "attribution":"Data Sourced from NOAA NCEP","thermal_merge_version":3},
    "cmc": {"name": "CMC GDPS (GEM 0.135\u02da L84)", "grid": .15, "interval": 3, "rain": 3,
            "attribution":"Data Sourced from ECCC MSC"},
}
FAMILIES = {"z": "geopotential", "gh": "geopotential", "HGT": "geopotential",
            "t": "temperature", "TMP": "temperature", "u": "wind_u", "UGRD": "wind_u",
            "v": "wind_v", "VGRD": "wind_v", "q": "specific_humidity", "SPFH": "specific_humidity",
            "w":"vertical_velocity","VVEL":"vertical_velocity"}


class NotReady(RuntimeError):
    """A missing file or required variable can be retried by the next polling pass."""


def forecast_hours(model):
    interval = MODELS[model]["interval"]
    return tuple(range(0, 85, interval)) + (90, 96) + tuple(range(108, 241, 12))


def accumulation_hours(model,hour):
    hours=forecast_hours(model)
    index=hours.index(hour)
    return hour-hours[index-1] if index else None


def required_fields(model=None):
    result = {f"{family}_{level}" for level in LEVELS
              for family in ("geopotential", "temperature", "wind_u", "wind_v")}
    result |= {f"specific_humidity_{level}" for level in (700, 850, 925)}
    result |= {"pressure_msl"}
    if model is not None:
        result.add("terrain_height")
        if model != "aigfs":
            result.add("surface_pressure")
    return result


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


class HttpCache:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "CDS-public-grid-test/1.0"
        self.requests = 0
        self.bytes = 0
        self.hits = 0
        self.records = []

    def get(self, url, byte_range=None, *, cache=True):
        key = hashlib.sha256(f"{url}|{byte_range}".encode()).hexdigest()
        path = self.root / (key + ".bin")
        meta = path.with_suffix(".json")
        def valid_payload(value):
            if byte_range is None and not url.endswith(".grib2"):
                return True
            return (len(value)>=20 and value.startswith(b"GRIB") and value.endswith(b"7777")
                    and int.from_bytes(value[8:16],"big")==len(value))

        if cache and path.exists() and meta.exists():
            record = json.loads(meta.read_text(encoding="utf-8"))
            value = path.read_bytes()
            if len(value) == record["bytes"] and hashlib.sha256(value).hexdigest() == record["sha256"] and valid_payload(value):
                self.hits += 1
                self.records.append(record)
                return value
        headers = {} if byte_range is None else {"Range": f"bytes={byte_range[0]}-{byte_range[1]}"}
        for attempt in range(3):
            try:
                response = self.session.get(url, headers=headers, timeout=(15, 120))
                self.requests += 1
                if response.status_code in (404, 410):
                    raise NotReady(f"HTTP {response.status_code}: {url}")
                if response.status_code in (429, 500, 502, 503, 504) and attempt < 2:
                    time.sleep(min(30,max(2,Retry().get_retry_after(response) or 3)))
                    continue
                response.raise_for_status()
                break
            except (requests.ConnectionError, requests.Timeout):
                if attempt == 2:
                    raise
                time.sleep(2 ** attempt)
        value = response.content
        self.bytes += len(value)
        if byte_range is not None:
            first, last = byte_range
            if response.status_code != 206 or len(value) != last-first+1:
                raise ValueError(f"Invalid byte-range response: {url}")
            if not response.headers.get("Content-Range", "").startswith(f"bytes {first}-{last}/"):
                raise ValueError(f"Incorrect Content-Range: {url}")
        if not valid_payload(value):
            raise NotReady(f"GRIB message is not fully published yet: {url}")
        record = {"url": url, "range": byte_range, "bytes": len(value),
                  "last_modified": response.headers.get("Last-Modified"), "etag": response.headers.get("ETag"),
                  "observed_at": datetime.now(timezone.utc).isoformat(),
                  "sha256": hashlib.sha256(value).hexdigest()}
        self.records.append(record)
        if cache:
            temporary = path.with_suffix(".tmp")
            temporary.write_bytes(value)
            temporary.replace(path)
            atomic_json(meta, record)
        return value


def ncep_index(text):
    entries = []
    for line in text.splitlines():
        parts = line.split(":")
        if len(parts) < 6 or not parts[0].isdigit():
            continue
        entries.append({"offset": int(parts[1]), "parameter": parts[3], "level": parts[4],
                        "description": parts[5]})
    for current, following in zip(entries, entries[1:]):
        current["length"] = following["offset"] - current["offset"]
    return entries


def ncep_field(entry):
    name, level = entry["parameter"], entry["level"]
    near={("TMP","2 m above ground"):"temperature_2m",("SPFH","2 m above ground"):"specific_humidity_2m",
          ("RH","2 m above ground"):"relative_humidity_2m",("DPT","2 m above ground"):"dewpoint_2m",
          ("UGRD","10 m above ground"):"wind_u_10m",("VGRD","10 m above ground"):"wind_v_10m",
          ("CSNOW","surface"):"categorical_snow",("CRAIN","surface"):"categorical_rain",
          ("CICEP","surface"):"categorical_ice_pellets",("CFRZR","surface"):"categorical_freezing_rain"}
    if (name,level) in near:
        return near[name,level] if "ave" not in entry["description"] else None
    if name == "PRMSL" and level == "mean sea level":
        return "pressure_msl"
    if name == "APCP" and level == "surface":
        return "precipitation"
    if name == "HGT" and level == "surface":
        return "terrain_height"
    if name == "PRES" and level == "surface":
        return "surface_pressure"
    match = re.fullmatch(r"(\d+) mb", level)
    if match and name in FAMILIES:
        return f"{FAMILIES[name]}_{match[1]}"
    return None


def choose_ncep(entries, wanted):
    selected = {}
    for entry in entries:
        key = ncep_field(entry)
        if key not in wanted:
            continue
        if key == "precipitation" and key in selected:
            # Prefer the shortest published accumulation over a run-total field.
            if accumulation_start(entry["description"]) <= accumulation_start(selected[key]["description"]):
                continue
        selected[key] = entry
    missing = wanted - selected.keys()
    if missing:
        raise NotReady(f"NCEP inventory lacks {sorted(missing)}")
    return selected


def accumulation_start(description):
    match = re.match(r"(\d+)-(\d+) (hour|day)", description)
    return int(match[1]) * (24 if match[3] == "day" else 1) if match else 0


@dataclass
class Decoded:
    values: np.ndarray
    latitude: np.ndarray
    longitude: np.ndarray
    metadata: dict


def decode(message, cycle, hour, key):
    handle = ec.codes_new_from_message(message)
    try:
        def get(name, default=None):
            try:
                return ec.codes_get(handle, name)
            except ec.CodesInternalError:
                return default
        meta = {name: get(name) for name in ("dataDate", "dataTime", "endStep", "startStep", "stepType",
                                             "stepUnits", "units", "shortName", "typeOfLevel", "level",
                                             "Ni", "Nj", "N", "gridType", "uvRelativeToGrid", "discipline",
                                             "parameterCategory", "parameterNumber", "tablesVersion", "numberOfMissing")}
        if str(meta["dataDate"]) != cycle[:8] or int(meta["dataTime"] or 0) != int(cycle[8:]) * 100:
            raise ValueError(f"Wrong cycle in {key}: {meta}")
        if int(meta["endStep"]) != hour or meta["stepUnits"] not in (1, "h"):
            raise ValueError(f"Wrong forecast step in {key}: {meta}")
        gaussian_keys={"precipitation_rate","temperature_2m","specific_humidity_2m","surface_pressure","wind_u_10m","wind_v_10m"}
        if meta["gridType"] != "regular_ll" and not (key in gaussian_keys and meta["gridType"]=="regular_gg"):
            raise ValueError(f"Unsupported source grid: {meta}")
        if key.startswith("wind_") and meta["uvRelativeToGrid"] not in (0, None):
            raise ValueError("Earth-relative wind components are required")
        if "_" in key and key.rsplit("_", 1)[1].isdigit():
            if meta["typeOfLevel"] != "isobaricInhPa" or int(meta["level"]) != int(key.rsplit("_", 1)[1]):
                raise ValueError(f"Wrong pressure level in {key}: {meta}")
        shape = int(meta["Nj"]), int(meta["Ni"])
        lat = np.asarray(ec.codes_get_array(handle, "latitudes")).reshape(shape)[:, 0]
        lon = np.asarray(ec.codes_get_array(handle, "longitudes")).reshape(shape)[0, :] % 360
        values = np.asarray(ec.codes_get_values(handle)).reshape(shape)
        south, north, west, east = BOUNDS
        yi = np.flatnonzero((lat >= south-.001) & (lat <= north+.001))
        xi = np.flatnonzero((lon >= west-.001) & (lon <= east+.001))
        yi, xi = yi[np.argsort(lat[yi])], xi[np.argsort(lon[xi])]
        values = values[np.ix_(yi, xi)].astype(np.float32)
        unit = str(meta["units"])
        if key == "terrain_height":
            if unit in ("m**2 s**-2", "m2 s-2"):
                values /= GRAVITY
            elif unit not in ("m", "gpm"):
                raise ValueError(f"Unknown terrain-height unit: {unit}")
        elif key.startswith("geopotential"):
            if unit in ("gpm", "m"):
                values *= GRAVITY
            elif unit not in ("m**2 s**-2", "m2 s-2"):
                raise ValueError(f"Unknown geopotential unit: {unit}")
        elif key.startswith("temperature") and unit != "K":
            raise ValueError(f"Unknown temperature unit: {unit}")
        elif key.startswith("wind_") and unit not in ("m s**-1", "m s-1"):
            raise ValueError(f"Unknown wind unit: {unit}")
        elif key.startswith("specific_humidity") and unit not in ("kg kg**-1", "kg kg-1", "kg/kg"):
            raise ValueError(f"Unknown humidity unit: {unit}")
        elif key=="dewpoint_2m" and unit!="K":
            raise ValueError(f"Unknown dewpoint unit: {unit}")
        elif key=="relative_humidity_2m" and unit!="%":
            raise ValueError(f"Unknown relative humidity unit: {unit}")
        elif key.startswith("vertical_velocity") and unit not in ("Pa s**-1","Pa s-1"):
            raise ValueError(f"Expected pressure vertical velocity, not geometric wind: {unit}")
        elif key in ("pressure_msl","surface_pressure") and unit != "Pa":
            raise ValueError(f"Unknown MSLP unit: {unit}")
        elif key == "precipitation_rate":
            if unit not in ("kg m**-2 s**-1", "kg m-2 s-1") or meta["stepType"]!="avg":
                raise ValueError(f"Expected a time-averaged precipitation mass flux: {meta}")
        elif key in ("precipitation","snowfall_water_equivalent"):
            # CMC's older WMO table 4 encodes 0/1/8 (total precipitation, kg/m2),
            # which recent ecCodes versions sometimes expose as an unknown name.
            if unit == "unknown" and (meta["discipline"], meta["parameterCategory"], meta["parameterNumber"]) == (0, 1, 8):
                unit = "kg m**-2"
                meta["units_resolved_from_wmo_4_2"] = unit
            if unit == "m":
                values *= 1000
            elif unit not in ("kg m**-2", "mm", "kg m-2"):
                raise ValueError(f"Unknown precipitation unit: {unit}")
            if meta["stepType"] != "accum":
                raise ValueError(f"Precipitation is not an accumulation: {meta}")
        if meta["numberOfMissing"] or not np.isfinite(values).all() or np.any(np.abs(values) >= 1e15):
            raise ValueError(f"Missing or invalid data in {key}")
        return Decoded(values, lat[yi], lon[xi], meta)
    finally:
        ec.codes_release(handle)


class Provider:
    def __init__(self, model, client):
        self.model, self.client = model, client

    def fetch(self, cycle, hour, wanted):
        if self.model == "aifs":
            return self.aifs(cycle, hour, wanted)
        if self.model in ("gfs", "aigfs"):
            return self.noaa(cycle, hour, wanted)
        return self.canada(cycle, hour, wanted)

    def aifs(self, cycle, hour, wanted):
        url = (f"https://data.ecmwf.int/forecasts/{cycle[:8]}/{cycle[8:]}z/aifs-single/0p25/oper/"
               f"{cycle}0000-{hour}h-oper-fc.grib2")
        entries = [json.loads(line) for line in self.client.get(url.replace(".grib2", ".index"),cache=False).decode().splitlines() if line.strip()]
        result = {}
        for item in entries:
            parameter = item.get("param")
            key = {"msl": "pressure_msl", "tp": "precipitation","sp":"surface_pressure",
                   "2t":"temperature_2m","2d":"dewpoint_2m","10u":"wind_u_10m","10v":"wind_v_10m",
                   "sf":"snowfall_water_equivalent"}.get(parameter)
            if parameter=="z" and item.get("levtype")=="sfc":
                key="terrain_height"
            if item.get("levtype") == "pl" and parameter in FAMILIES:
                key = f"{FAMILIES[parameter]}_{item.get('levelist')}"
            if key not in wanted:
                continue
            offset, length = int(item["_offset"]), int(item["_length"])
            result[key] = decode(self.client.get(url, (offset, offset+length-1)), cycle, hour, key)
        if wanted - result.keys():
            raise NotReady(f"AIFS inventory lacks {sorted(wanted-result.keys())}")
        return result

    def noaa(self, cycle, hour, wanted):
        if self.model == "gfs":
            urls = [f"https://noaa-gfs-bdp-pds.s3.amazonaws.com/gfs.{cycle[:8]}/{cycle[8:]}/atmos/"
                    f"gfs.t{cycle[8:]}z.pgrb2.0p25.f{hour:03}"]
        else:
            base = (f"https://noaa-nws-graphcastgfs-pds.s3.amazonaws.com/aigfs.{cycle[:8]}/"
                    f"{cycle[8:]}/model/atmos/grib2/")
            urls = [base+f"aigfs.t{cycle[8:]}z.{kind}.f{hour:03}.grib2" for kind in ("pres", "sfc")]
        result = {}
        for url in urls:
            subset = {key for key in wanted if (key.startswith(("pressure_", "precip")) or key.endswith(("_2m","_10m"))) == (".sfc." in url)} if self.model == "aigfs" else wanted
            if not subset:
                continue
            if self.model=="aigfs":
                try:
                    inventory=self.client.get(url+".idx",cache=False)
                except (NotReady,requests.RequestException):
                    url=url.replace("https://noaa-nws-graphcastgfs-pds.s3.amazonaws.com/",
                                    "https://nomads.ncep.noaa.gov/pub/data/nccf/com/aigfs/prod/")
                    inventory=self.client.get(url+".idx",cache=False)
            else:
                inventory=self.client.get(url+".idx",cache=False)
            entries = ncep_index(inventory.decode())
            selected = choose_ncep(entries, subset)
            for key, item in selected.items():
                if "length" not in item:
                    response = self.client.session.head(url, timeout=30)
                    response.raise_for_status()
                    item["length"] = int(response.headers["Content-Length"])-item["offset"]
                first, length = item["offset"], item["length"]
                result[key] = decode(self.client.get(url, (first, first+length-1)), cycle, hour, key)
        return result

    def sflux(self, cycle, hour):
        if self.model!="gfs":
            raise ValueError("Only GFS provides this surface-flux source")
        url=(f"https://noaa-gfs-bdp-pds.s3.amazonaws.com/gfs.{cycle[:8]}/{cycle[8:]}/atmos/"
             f"gfs.t{cycle[8:]}z.sfluxgrbf{hour:03}.grib2")
        entries=ncep_index(self.client.get(url+".idx",cache=False).decode())
        choices=[item for item in entries if item["parameter"]=="PRATE" and item["level"]=="surface"]
        if not choices:
            raise NotReady("GFS sflux inventory lacks surface PRATE")
        item=max(choices,key=lambda entry:accumulation_start(entry["description"]))
        if "length" not in item:
            raise NotReady("GFS sflux PRATE range is not fully indexed")
        first,length=item["offset"],item["length"]
        return decode(self.client.get(url,(first,first+length-1)),cycle,hour,"precipitation_rate")

    def sflux_surface(self,cycle,hour,wanted):
        if self.model!="gfs":
            raise ValueError("GFS surface flux cannot replace another model's fields")
        url=(f"https://noaa-gfs-bdp-pds.s3.amazonaws.com/gfs.{cycle[:8]}/{cycle[8:]}/atmos/"
             f"gfs.t{cycle[8:]}z.sfluxgrbf{hour:03}.grib2")
        selected=choose_ncep(ncep_index(self.client.get(url+".idx",cache=False).decode()),wanted)
        result={}
        for key,item in selected.items():
            if "length" not in item:
                raise NotReady(f"Incomplete sflux index for {key}")
            first,length=item["offset"],item["length"]
            result[key]=decode(self.client.get(url,(first,first+length-1)),cycle,hour,key)
        return result

    def canada(self, cycle, hour, wanted, *, total_precipitation=False):
        geml = self.model == "geml"
        model, resolution = ("GDPS-GEML", "0.25") if geml else ("GDPS", "0.15")
        root = "model_gdps-geml/25km" if geml else "model_gdps/15km"
        base = f"https://dd.weather.gc.ca/today/{root}/{cycle[8:]}/{hour:03}/"
        variables = {"geopotential": "Geopotential" if geml else "GeopotentialHeight",
                     "temperature": "AirTemp", "specific_humidity": "SpecificHumidity",
                     "wind_u": "WindU", "wind_v": "WindV"}
        result = {}
        for key in sorted(wanted):
            if key == "pressure_msl":
                part = "Pressure_MSL"
            elif key == "surface_pressure":
                part = "Pressure_Sfc"
            elif key == "terrain_height":
                part = "GeopotentialHeight_Sfc"
            elif key == "precipitation":
                part = "Precip-Accum_Sfc" if total_precipitation else "Precip-Accum3h_Sfc"
            elif key=="snowfall_water_equivalent":
                part="Snow-Accum_Sfc"
            elif key in ("temperature_2m","relative_humidity_2m","dewpoint_2m"):
                part={"temperature_2m":"AirTemp","relative_humidity_2m":"RelativeHumidity","dewpoint_2m":"DewPoint"}[key]+"_AGL-2m"
            elif key in ("wind_u_10m","wind_v_10m"):
                part={"wind_u_10m":"WindU","wind_v_10m":"WindV"}[key]+"_AGL-10m"
            else:
                family, level = key.rsplit("_", 1)
                if family=="vertical_velocity":
                    variables[family]="VerticalVelocity"
                part = f"{variables[family]}_IsbL-{int(level):04}"
            name = f"{cycle[:8]}T{cycle[8:]}Z_MSC_{model}_{part}_LatLon{resolution}_PT{hour:03}H.grib2"
            try:
                value = self.client.get(base+name)
            except NotReady:
                if key != "precipitation" or geml:
                    raise
                # Long GDPS leads omit the standalone 3h field but retain run totals.
                name = name.replace("Precip-Accum3h_Sfc", "Precip-Accum_Sfc")
                value = self.client.get(base+name)
            result[key] = decode(value, cycle, hour, key)
        return result


def rainfall_interval(current, previous, hour, interval):
    end, start = int(current.metadata["endStep"]), int(current.metadata["startStep"])
    if end != hour:
        raise ValueError("Wrong rainfall valid time")
    if start == hour-interval:
        return current.values
    if previous is None or int(previous.metadata["endStep"]) != hour-interval:
        raise NotReady("Rainfall needs its exact earlier forecast step")
    if int(previous.metadata["startStep"]) != start:
        raise ValueError("Cannot subtract accumulations with different start times")
    if not np.array_equal(current.latitude, previous.latitude) or not np.array_equal(current.longitude, previous.longitude):
        raise ValueError("Rainfall dependency grid differs")
    difference = current.values-previous.values
    if float(np.nanmin(difference)) < -.1:
        raise ValueError("Negative accumulated-rainfall difference")
    return np.maximum(difference, 0)


def rainfall_from_rate(current, previous, hour, interval):
    """Integrate mean mass flux, subtracting only an exactly matching earlier window."""
    def integrated(field):
        start,end=int(field.metadata["startStep"]),int(field.metadata["endStep"])
        if field.metadata.get("stepType")!="avg" or start>=end or np.any(field.values<0):
            raise ValueError("Expected a nonempty mean rainfall-rate interval")
        return Decoded(field.values.astype(np.float64)*(end-start)*3600,
                       field.latitude,field.longitude,field.metadata)
    return rainfall_interval(integrated(current),None if previous is None else integrated(previous),hour,interval).astype(np.float32)


def collect_rainfall(provider,cycle,hour,interval):
    """Cover the display interval exactly with available source accumulation windows."""
    start,end=hour-interval,hour
    pieces,components=[],[]
    reference=None
    sflux=provider.model=="gfs"
    while end>start:
        current=provider.sflux(cycle,end) if sflux else provider.fetch(cycle,end,{"precipitation"})["precipitation"]
        source_start=int(current.metadata["startStep"])
        if int(current.metadata["endStep"])!=end or source_start>=end:
            raise ValueError("Rainfall window does not advance towards the requested start")
        piece_start=max(start,source_start)
        previous=None
        if source_start<piece_start:
            if sflux:
                previous=provider.sflux(cycle,piece_start)
            elif provider.model=="cmc" and source_start==0:
                previous=provider.canada(cycle,piece_start,{"precipitation"},total_precipitation=True)["precipitation"]
            else:
                previous=provider.fetch(cycle,piece_start,{"precipitation"})["precipitation"]
        piece=(rainfall_from_rate if sflux else rainfall_interval)(current,previous,end,end-piece_start)
        if reference is not None and (not np.array_equal(reference.latitude,current.latitude) or
                                      not np.array_equal(reference.longitude,current.longitude)):
            raise ValueError("Rainfall component grids differ")
        reference=current
        pieces.append(piece.astype(np.float64))
        components.append({"start_hour":piece_start,"end_hour":end,"current":current.metadata,
                           "previous":None if previous is None else previous.metadata})
        end=piece_start
    return np.sum(pieces,axis=0).astype(np.float32),reference,components


def collect(model, cycle, hour, root, *, include_precipitation=True):
    directory = Path(root) / "fields" / cycle / model / f"{hour:03}"
    directory.mkdir(parents=True, exist_ok=True)
    path, meta_path = directory/"fields.npz", directory/"metadata.json"
    arrays,meta={},{}
    rain = accumulation_hours(model,hour) if include_precipitation else None
    sflux_rain = model=="gfs" and rain is not None
    collector_version=4
    expected=required_fields(model)|({"precipitation"} if rain else set())
    if sflux_rain:
        expected|={"precipitation_latitude","precipitation_longitude"}
    if path.exists() and meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if (meta.get("model"),meta.get("cycle"),meta.get("hour")) == (model,cycle,hour):
            with np.load(path, allow_pickle=False) as archive:
                arrays = {key: archive[key] for key in archive.files}
            if not all(np.isfinite(a).all() for a in arrays.values()):
                arrays,meta={},{}
            if meta.get("collector_version")==collector_version and expected<=arrays.keys():
                return arrays, meta, {"requests": 0, "bytes": 0, "cached": True}
        else:
            meta={}
    client = HttpCache(Path(root)/"grib-cache")
    provider = Provider(model, client)
    wanted=required_fields()-arrays.keys()
    started = time.perf_counter()
    fields = provider.fetch(cycle, hour, wanted) if wanted else {}
    if "terrain_height" not in arrays:
        terrain_provider=Provider("gfs" if model=="aigfs" else model,client)
        fields.update(terrain_provider.fetch(cycle,0,{"terrain_height"}))
    if model!="aigfs" and "surface_pressure" not in arrays:
        fields.update(provider.fetch(cycle,hour,{"surface_pressure"}))
    if not arrays:
        reference=fields["pressure_msl"]
        arrays={"latitude":reference.latitude,"longitude":reference.longitude}
    for key, field in fields.items():
        if not np.array_equal(field.latitude, arrays["latitude"]) or not np.array_equal(field.longitude, arrays["longitude"]):
            raise ValueError(f"Inconsistent grid for {key}")
        arrays[key] = field.values
    rain_metadata={}
    rain_grid=meta.get("precipitation_grid")
    if rain:
        arrays["precipitation"],current,components=collect_rainfall(provider,cycle,hour,rain)
        rain_metadata={"precipitation":{"startStep":hour-rain,"endStep":hour,"stepType":"accum","units":"mm",
                                        "derived_from":"PRATE" if sflux_rain else "source accumulations",
                                        "gridType":current.metadata["gridType"]}}
        rain_grid={"source":"GFS sflux PRATE" if sflux_rain else model,"grid_type":current.metadata["gridType"],
                   "interpolated":False,"start_hour":hour-rain,"end_hour":hour,"units":"mm","components":components}
    if sflux_rain:
        arrays["precipitation_latitude"]=current.latitude
        arrays["precipitation_longitude"]=current.longitude
        rain_grid.update(global_shape=[current.metadata["Nj"],current.metadata["Ni"]],
                         gaussian_order=current.metadata["N"],method="integrated mean mass flux; exact nonoverlapping components")
    previous_fields=meta.get("fields",{})
    previous_sources=meta.get("sources",[])
    meta = {"collector_version": collector_version, "model": model, "cycle": cycle, "hour": hour,
            "precipitation_hours": rain, "grid_degrees": MODELS[model]["grid"],
            "precipitation_grid":rain_grid,
            "terrain_qc":{"terrain_source_model":"gfs" if model=="aigfs" else model,
                          "uses_reference_terrain":model=="aigfs","has_forecast_surface_pressure":model!="aigfs"},
            "fields": {**previous_fields,**{key: value.metadata for key, value in fields.items()},**rain_metadata},
            "sources": previous_sources+client.records, "statistics": {"requests": client.requests, "bytes": client.bytes,
                                                      "cache_hits": client.hits, "seconds": round(time.perf_counter()-started, 2)}}
    temporary = path.with_suffix(".tmp")
    with temporary.open("wb") as handle:
        np.savez_compressed(handle, **arrays)
    temporary.replace(path)
    atomic_json(meta_path, meta)
    return arrays, meta, meta["statistics"]
