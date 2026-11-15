"""Render one ready lead, publishing completed products without waiting for rain."""
from pathlib import Path

import numpy as np
from PIL import Image

from . import policy
from .chart_style import PUBLIC_PROFILE, PUBLIC_IMAGE_SIZES
from .diagnostics import interpolate
from .extended_sources import ExtraFields, winter_fields
from .plotter import render
from .quality import closed_contour_predicate
from .sources import MODELS, collect, accumulation_hours, NotReady


def crop(arrays, domain):
    if domain == "asia":
        return arrays
    latitude, longitude = arrays["latitude"], arrays["longitude"]
    rows = np.flatnonzero((latitude >= 29) & (latitude <= 45))
    cols = np.flatnonzero((longitude >= 115) & (longitude <= 138))
    selected = {key: value[rows] if key == "latitude" else value[cols] if key == "longitude"
                else value[np.ix_(rows, cols)] for key, value in arrays.items()
                if key not in {"precipitation", "precipitation_latitude", "precipitation_longitude"}}
    if "precipitation" in arrays:
        rain_lat = arrays.get("precipitation_latitude", latitude)
        rain_lon = arrays.get("precipitation_longitude", longitude)
        yi = np.flatnonzero((rain_lat >= 29) & (rain_lat <= 45))
        xi = np.flatnonzero((rain_lon >= 115) & (rain_lon <= 138))
        selected["precipitation"] = arrays["precipitation"][np.ix_(yi, xi)]
        if "precipitation_latitude" in arrays:
            selected.update(precipitation_latitude=rain_lat[yi], precipitation_longitude=rain_lon[xi])
    return selected


def compose(frames, vertical):
    width, height = frames[0].size
    if any(frame.size != (width, height) for frame in frames):
        raise ValueError("Winter panel sizes differ")
    result = Image.new("RGB", (width, height * len(frames)) if vertical else (width * len(frames), height), "white")
    for index, frame in enumerate(frames):
        result.paste(frame, (0, index * height) if vertical else (index * width, 0))
    return result


def encode(frame, path):
    """One final lossless encode; no intermediate PNG and no second map render."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    frame.save(temporary, format="WEBP", lossless=True, quality=80, method=4)
    with Image.open(temporary) as saved:
        saved.load()
        if saved.format != "WEBP" or saved.size != frame.size:
            raise ValueError("Invalid encoded chart")
        if np.asarray(saved.convert("RGB")).std() < 10:
            raise ValueError("Encoded chart is blank")
    temporary.replace(path)


def produce_lead(model, cycle, hour, root, existing, publish, *, force=False):
    """publish(product, domain, path, alias_of=None) commits one verified image."""
    root = Path(root)
    completed = set(existing)
    interval = accumulation_hours(model, hour) or 0

    def done(product, domain):
        return not force and policy.key(model, cycle, hour, product, domain) in completed

    def emit(product, domain, frame=None, alias_of=None):
        if done(product, domain):
            return
        path = root / "images" / model / f"{cycle}_{hour:03}_{product}_{domain}.webp"
        if frame is not None:
            encode(frame, path)
        publish(product, domain, path if frame is not None else None, alias_of=alias_of)
        completed.add(policy.key(model, cycle, hour, product, domain))
        if path.exists():
            path.unlink()

    def draw(arrays, product, domain, *, accumulation=None, pressure_only=False):
        return render(arrays, cycle, hour, product, domain, None, accumulation,
                      model_name=MODELS[model]["name"], precipitation_hours=interval,
                      precipitation_field="precipitation", source_note=MODELS[model]["attribution"],
                      pressure_only=pressure_only, upper_level_override=200 if product == "gph200" else None,
                      physical_barb_spacing=True, profile=PUBLIC_PROFILE, model_id=model,
                      contour_filter=closed_contour_predicate(arrays), diagnostic_snowfall=model == "gfs",
                      return_frame=True)

    base, _, _ = collect(model, cycle, hour, root, include_precipitation=False)
    for domain in ("asia", "hkor"):
        selected = crop(base, domain)
        for product in policy.products(cycle):
            if not done(product, domain):
                emit(product, domain, draw(selected, product, domain))
    if hour == 0:
        base = {**base, "precipitation": np.zeros_like(base["pressure_msl"], dtype=np.float64)}

    try:
        if hour:
            base, _, _ = collect(model, cycle, hour, root)
        if not done("surfce", "asia"):
            emit("surfce", "asia", draw(base, "surfce", "asia"))
        extra = ExtraFields(root, model, cycle)
        selected = crop(base, "hkor")
        total = None if not hour or done("acrain", "hkor") and done("acrain1", "hkor") else extra.total_rain(hour)
        if policy.winter(model, cycle):
            required = ("acptot", "acptot1", "acrain", "acrain1") if hour else ("acptot", "acptot1")
            if all(done(name, "hkor") for name in required):
                emit("surfce", "hkor", alias_of=("acptot", "hkor"))
                return {"complete": policy.expected_keys(model, cycle, hour) <= completed}
            selected, _ = winter_fields(extra, base, hour, interval)
            amount = interpolate(total, selected["latitude"], selected["longitude"]) if total is not None else None
            for name, components in (("acptot", ("acptot", "acptot_snow", "acptot_snowdepth")),
                                     ("acrain", ("acrain", "acrain_snow", "acrain_snowdepth"))):
                if name == "acrain" and not hour:
                    continue
                if done(name, "hkor") and done(name + "1", "hkor"):
                    continue
                panels = [draw(selected, product, "hkor", accumulation=amount if product == "acrain" else None)
                          for product in components]
                for suffix, vertical in (("", False), ("1", True)):
                    if not done(name + suffix, "hkor"):
                        emit(name + suffix, "hkor", compose(panels, vertical))
            emit("surfce", "hkor", alias_of=("acptot", "hkor"))
        else:
            if not done("surfce", "hkor"):
                emit("surfce", "hkor", draw(selected, "surfce", "hkor"))
            for name in ("acptot", "acptot1"):
                emit(name, "hkor", alias_of=("surfce", "hkor"))
            if hour and not done("acrain", "hkor"):
                emit("acrain", "hkor", draw(selected, "acrain", "hkor",
                                            accumulation=interpolate(total, selected["latitude"], selected["longitude"])))
            if hour:
                emit("acrain1", "hkor", alias_of=("acrain", "hkor"))
    except NotReady as error:
        return {"complete": False, "pending": str(error)}
    return {"complete": policy.expected_keys(model, cycle, hour) <= completed}
