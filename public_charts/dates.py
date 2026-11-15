from datetime import datetime, timezone
import re


def parse_cycle(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{10}", value):
        raise ValueError("Cycle must be YYYYMMDDHH in UTC")
    return datetime.strptime(value, "%Y%m%d%H").replace(tzinfo=timezone.utc)
