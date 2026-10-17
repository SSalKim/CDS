"""Reversible TD-to-TYP links while the official TD list is delayed."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path


LINKS_FILENAME = "td_typ_links.json"
ACTIVE_STATES = {"provisional", "confirmed"}


def stamp(value) -> datetime | None:
    text = str(value or "")
    if not re.fullmatch(r"\d{12}", text):
        return None
    try:
        return datetime.strptime(text, "%Y%m%d%H%M").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def valid_link(link: dict) -> bool:
    if not isinstance(link, dict):
        return False
    try:
        year, td, typ = int(link["year"]), int(link["td_number"]), int(link["typ_number"])
    except (KeyError, TypeError, ValueError):
        return False
    effective = stamp(link.get("effective_time_utc"))
    identity = str(link.get("atcf_id") or "")
    return bool(
        1900 <= year <= 2200 and 1 <= td <= 99 and 1 <= typ <= 99
        and effective and effective.year == year
        and re.fullmatch(r"(?:wp|cp|ep)(?:0[1-9]|[1-8]\d)" + str(year), identity)
        and link.get("state") in {*ACTIVE_STATES, "conflict"}
    )


def load_links(cache_dir: Path) -> dict:
    try:
        path = cache_dir / LINKS_FILENAME
        if path.stat().st_size > 2 * 1024 * 1024:
            return {"version": 1, "links": []}
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("version") == 1 and isinstance(payload.get("links"), list):
            return {"version": 1, "links": [dict(link) for link in payload["links"] if valid_link(link)]}
    except (OSError, ValueError, TypeError, AttributeError):
        pass
    return {"version": 1, "links": []}


def reconcile_links(payload: dict, td_rows: list[dict], typ_rows: list[dict]) -> dict:
    """Explicit official conflicts disable a provisional link; missing rows do not."""
    result = {"version": 1, "links": []}
    for stored in payload.get("links", []):
        if not valid_link(stored):
            continue
        link = dict(stored)
        year, td, typ = int(link["year"]), int(link["td_number"]), int(link["typ_number"])
        td_matches = [row for row in td_rows if str(row.get("YY")) == str(year) and str(row.get("TD")) == str(td)]
        typ_matches = [row for row in typ_rows if str(row.get("YY")) == str(year) and str(row.get("SEQ")) == str(typ)]
        official_numbers = {str(row.get("TYP") or "0") for row in td_matches} - {"0", ""}
        if official_numbers - {str(typ)}:
            link.update(state="conflict", conflict_reason="Official TD link identifies another TYP.")
        elif any(stamp(row.get("TM_ST")) and stamp(row["TM_ST"]) >= stamp(link["effective_time_utc"]) for row in td_matches):
            link.update(state="conflict", conflict_reason="TD episode starts after the proposed promotion.")
        elif typ_matches and any(str(row.get("TM_ST")) != link["effective_time_utc"] for row in typ_matches):
            link.update(state="conflict", conflict_reason="Official TYP start time changed.")
        elif official_numbers == {str(typ)} and link["state"] != "conflict":
            link["state"] = "confirmed"
        result["links"].append(link)
    return result


def active_links(payload: dict) -> list[dict]:
    links = [link for link in payload.get("links", []) if valid_link(link) and link["state"] in ACTIVE_STATES]
    # Neither a TD nor a TYP may acquire multiple competing predecessors.
    return [link for link in links if sum(
        int(other["year"]) == int(link["year"]) and (
            int(other["td_number"]) == int(link["td_number"]) or int(other["typ_number"]) == int(link["typ_number"])
        ) for other in links
    ) == 1]


def effective_td_rows(td_rows: list[dict], typ_rows: list[dict], payload: dict) -> list[dict]:
    links = {(int(link["year"]), int(link["td_number"])): link
             for link in active_links(reconcile_links(payload, td_rows, typ_rows))}
    result = []
    for row in td_rows:
        updated = dict(row)
        try:
            link = links.get((int(row["YY"]), int(row["TD"])))
            official_number = int(row.get("TYP") or 0)
        except (KeyError, TypeError, ValueError):
            link = None
            official_number = 0
        if link and official_number in (0, int(link["typ_number"])):
            start, effective = stamp(row.get("TM_ST")), stamp(link["effective_time_utc"])
            if start and start < effective:
                updated["TYP"] = str(link["typ_number"])
                end = stamp(row.get("TM_ED"))
                updated["TM_ED"] = min(end, effective).strftime("%Y%m%d%H%M") if end else link["effective_time_utc"]
        # An explicitly linked pre-TYP episode cannot continue past first naming.
        # A later weakening TD episode starts after naming and must remain active.
        if official_number > 0:
            typ_row = next((item for item in typ_rows if str(item.get("YY")) == str(row.get("YY"))
                            and str(item.get("SEQ")) == str(official_number)), None)
            typ_start = stamp((typ_row or {}).get("TM_ST"))
            td_start, td_end = stamp(row.get("TM_ST")), stamp(row.get("TM_ED"))
            if td_start and typ_start and td_start < typ_start and (td_end is None or typ_start < td_end):
                updated["TM_ED"] = typ_start.strftime("%Y%m%d%H%M")
        result.append(updated)
    return result
