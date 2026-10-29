"""Exact-cycle WeatherMesh transport and validated ensemble-mean A-decks."""

import csv
import hashlib
import io
import json
import math
import re
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener


BASE_URL = "https://api.windbornesystems.com/forecasts/v1/wm-6/tropical_cyclones"
MAX_RESPONSE_BYTES = 20 * 1024 * 1024


class WindborneError(Exception):
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
        raise WindborneError("Invalid API timestamp")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise WindborneError("Invalid API timestamp") from None
    if result.tzinfo is None:
        raise WindborneError("API timestamp has no timezone")
    return result.astimezone(timezone.utc)


def request_text(opener, key, path, params=None, *, timeout=60):
    url = BASE_URL + path
    if params:
        url += "?" + urlencode(params)
    request = Request(url, headers={
        "Authorization": "Bearer " + key,
        "User-Agent": "CDS-VTG-WeatherMesh/1.0",
    })
    try:
        with opener.open(request, timeout=timeout) as response:
            if response.status != 200:
                raise WindborneError(f"HTTP {response.status}")
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except HTTPError as error:
        error.close()
        raise WindborneError(f"HTTP {error.code}") from None
    except (URLError, TimeoutError, OSError):
        raise WindborneError("Network or TLS request failed") from None
    if len(raw) > MAX_RESPONSE_BYTES:
        raise WindborneError("Response exceeds size limit")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeError:
        raise WindborneError("Response is not UTF-8 text") from None
    if key in text:
        raise WindborneError("Response unexpectedly contains credential material")
    return text


def request_json(opener, key, path, params=None, *, timeout=60):
    try:
        result = json.loads(request_text(opener, key, path, params, timeout=timeout))
    except ValueError:
        raise WindborneError("Response is not valid JSON") from None
    if not isinstance(result, dict):
        raise WindborneError("Response is not a JSON object")
    return result


def parse_coord(value, latitude):
    match = re.fullmatch(r"(\d+)([NS])" if latitude else r"(\d+)([EW])", value)
    if not match:
        raise WindborneError("Invalid ATCF coordinate")
    coordinate = int(match[1]) / 10
    if coordinate > (90 if latitude else 180):
        raise WindborneError("ATCF coordinate outside valid range")
    return -coordinate if match[2] in "SW" else coordinate


def summarize_deck(text, storm_id, cycle):
    mean = {}
    models = set()
    row_count = 0
    for row in csv.reader(io.StringIO(text)):
        if not row or not any(field.strip() for field in row):
            continue
        if len(row) < 10:
            raise WindborneError("Response is not an ATCF A-deck")
        row = [field.strip() for field in row]
        if row[0] != storm_id[:2] or row[1] != storm_id[2:4]:
            raise WindborneError("ATCF storm does not match requested storm")
        if row[2] != cycle:
            raise WindborneError("ATCF cycle does not match requested cycle")
        model = row[4]
        if not re.fullmatch(r"WMSH|W\d{3}", model):
            raise WindborneError("Unexpected WeatherMesh model code")
        lat = parse_coord(row[6], True)
        lon = parse_coord(row[7], False)
        try:
            lead = int(row[5])
            wind = float(row[8])
            pressure = float(row[9])
        except ValueError:
            raise WindborneError("Invalid ATCF numeric fields") from None
        if lead < 0 or not all(math.isfinite(value) for value in (wind, pressure)):
            raise WindborneError("Invalid ATCF lead or intensity")
        models.add(model)
        row_count += 1
        if model == "WMSH":
            point = (lat, lon, wind, pressure)
            if lead in mean and mean[lead] != point:
                raise WindborneError("Conflicting WMSH points at the same lead")
            mean[lead] = point
    if not row_count:
        raise WindborneError("Empty ATCF response")
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


def reusable_mean_deck(text, storm_id, cycle):
    """Freeze only mean-only decks with analysis and uninterrupted 3-hour forecasts.

    A naturally short forecast is valid; this is local validation, not a claim
    that the provider exposes a final-publication flag.
    """
    if not isinstance(text, str):
        return False
    try:
        summary = summarize_deck(text, storm_id, cycle)
    except WindborneError:
        return False
    return (summary["member_count"] == 0 and summary["mean_first_hour"] == 0
            and summary["mean_points"] >= 2 and summary["mean_step_hours"] == [3])


def fetch_mean_deck(storm_id, cycle, key):
    """Return only WMSH for this identity/cycle, without latest-cycle fallback."""
    storm_id = storm_id.strip().upper()
    if not re.fullmatch(r"(?:WP|EP|CP|AL|IO|SH)\d{6}", storm_id):
        raise WindborneError("Invalid operational ATCF ID")
    try:
        requested = parse_cycle(cycle)
    except ValueError:
        raise WindborneError("Invalid UTC initialization") from None
    if cycle[-2:] not in {"00", "06", "12", "18"}:
        raise WindborneError("Only standard 6-hour UTC cycles are supported")
    if not key.strip():
        raise WindborneError("WB_API_KEY is not configured")
    opener = build_opener(NoRedirects())
    params = {"initialization_time": cycle, "format": "json"}
    detail = request_json(opener, key, "/" + storm_id, params, timeout=20)
    if detail.get("tropical_cyclone_id") != storm_id:
        raise WindborneError("JSON storm does not match requested storm")
    if parse_time(detail.get("initialization_time")) != requested:
        raise WindborneError("API returned a different initialization time")
    if parse_time(detail.get("forecast_zero")) != requested:
        raise WindborneError("API forecast zero differs from requested cycle")
    params["format"] = "deck"
    deck = request_text(opener, key, "/" + storm_id, params, timeout=20)
    summary = summarize_deck(deck, storm_id, cycle)
    if not summary["mean_points"]:
        raise WindborneError("No WMSH ensemble-mean points in A-deck")
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    for row in csv.reader(io.StringIO(deck)):
        if len(row) >= 10 and row[4].strip() == "WMSH":
            writer.writerow(row)
    return output.getvalue()
