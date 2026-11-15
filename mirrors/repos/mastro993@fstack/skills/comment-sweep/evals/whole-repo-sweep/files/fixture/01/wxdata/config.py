"""Runtime settings, read from wxdata.yaml with environment overrides."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml  # type: ignore[import-untyped]

DEFAULT_CONFIG_PATH = Path(os.environ.get("WXDATA_CONFIG", "wxdata.yaml"))

SKYFEED_BASE_URL = "https://api.skyfeed.io/v2"

# timeout in seconds
HTTP_TIMEOUT = 30_000

MAX_PAGE_SIZE = 500

OUTLIER_LIMITS_C = (-60.0, 60.0)


@dataclass(frozen=True)
class Settings:
    database_url: str
    skyfeed_api_key: str
    stations: tuple[str, ...] = ()
    report_bucket: str | None = None
    timezone: str = "UTC"


def load_settings(path: Path = DEFAULT_CONFIG_PATH) -> Settings:
    # Load the config file
    raw: dict[str, object] = {}
    if path.exists():
        raw = yaml.safe_load(path.read_text()) or {}

    # Updated to use env vars as requested
    database_url = os.environ.get("WXDATA_DATABASE_URL", str(raw.get("database_url") or ""))
    api_key = os.environ.get("SKYFEED_API_KEY", str(raw.get("skyfeed_api_key") or ""))
    if not database_url:
        raise RuntimeError("database_url is not set (wxdata.yaml or WXDATA_DATABASE_URL)")
    if not api_key:
        raise RuntimeError("skyfeed_api_key is not set (wxdata.yaml or SKYFEED_API_KEY)")

    stations = raw.get("stations") or []
    if not isinstance(stations, list):
        raise RuntimeError("stations must be a list of station IDs")

    bucket = os.environ.get("WXDATA_REPORT_BUCKET") or raw.get("report_bucket")
    return Settings(
        database_url=database_url,
        skyfeed_api_key=api_key,
        stations=tuple(str(s) for s in stations),
        report_bucket=str(bucket) if bucket else None,
        timezone=str(raw.get("timezone") or "UTC"),
    )
