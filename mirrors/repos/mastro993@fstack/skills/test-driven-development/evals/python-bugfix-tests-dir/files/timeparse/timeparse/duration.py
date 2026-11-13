import re

UNITS = {"h": 3600, "m": 60, "s": 1}
PART = re.compile(r"(\d+)([hms])")


def parse_duration(text: str) -> int:
    """Return the number of seconds in a duration such as '1h30m' or '45s'."""
    cleaned = text.strip().lower()
    parts = PART.findall(cleaned)
    if not parts or PART.sub("", cleaned):
        raise ValueError(f"not a duration: {text!r}")
    total = 0
    for value, unit in parts:
        total = int(value) * UNITS[unit]
    return total
