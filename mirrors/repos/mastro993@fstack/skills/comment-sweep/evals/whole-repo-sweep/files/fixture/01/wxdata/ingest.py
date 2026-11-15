"""Pull a day's readings from SkyFeed, clean them, and store them."""

from __future__ import annotations

import logging
from collections.abc import Iterable
from dataclasses import dataclass, replace
from datetime import date, datetime

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from wxdata import config
from wxdata.client import RawReading, SkyFeedClient
from wxdata.models import Reading
from wxdata.units import pressure_to_hpa, to_celsius

log = logging.getLogger(__name__)


@dataclass
class IngestResult:
    fetched: int = 0
    stored: int = 0
    duplicates: int = 0
    outliers: int = 0


def ingest_day(
    client: SkyFeedClient, session: Session, station_ids: Iterable[str], day: date
) -> IngestResult:
    result = IngestResult()
    # Loop over the stations
    for station_id in station_ids:
        raw = list(client.get_readings(station_id, day))
        # raw = [r for r in raw if r.temperature is not None]
        result.fetched += len(raw)

        # IMPORTANT: normalize_units must run before dedupe_readings. SkyFeed sends some
        # stations' readings twice, once in °F and once in °C, and dedupe keys on the
        # temperature value, so deduping first keeps both copies.
        cleaned = normalize_units(raw)
        unique = dedupe_readings(cleaned)
        result.duplicates += len(cleaned) - len(unique)

        kept = drop_outliers(unique)
        result.outliers += len(unique) - len(kept)

        result.stored += store(session, kept)
        log.info("station %s: %d fetched, %d stored", station_id, len(raw), len(kept))
    return result


def normalize_units(readings: list[RawReading]) -> list[RawReading]:
    out = []
    for r in readings:
        temperature = r.temperature
        if temperature is not None:
            unit = r.temperature_unit
            temperature = round(to_celsius(temperature, unit), 2)  # type: ignore[arg-type]
        pressure = r.pressure
        if pressure is not None:
            pressure = round(pressure_to_hpa(pressure, r.pressure_unit), 1)
        out.append(
            replace(
                r,
                temperature=temperature,
                temperature_unit="C",
                pressure=pressure,
                pressure_unit="hPa",
            )
        )
    return out


def dedupe_readings(readings: list[RawReading]) -> list[RawReading]:
    seen: set[tuple[str, str, float | None]] = set()
    out = []
    for r in readings:
        temperature = None if r.temperature is None else round(r.temperature, 1)
        key = (r.station_id, r.observed_at, temperature)
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def drop_outliers(readings: list[RawReading]) -> list[RawReading]:
    low, high = config.OUTLIER_LIMITS_C
    return [r for r in readings if r.temperature is None or low <= r.temperature <= high]


# ---------- Helpers ----------


def store(session: Session, readings: list[RawReading]) -> int:
    if not readings:
        return 0
    rows = [
        {
            "station_id": r.station_id,
            "observed_at": datetime.fromisoformat(r.observed_at),
            "temperature_c": r.temperature,
            "pressure_hpa": r.pressure,
            "humidity_pct": r.humidity,
        }
        for r in readings
    ]
    stmt = insert(Reading).values(rows)
    stmt = stmt.on_conflict_do_nothing(constraint="uq_readings_station_time")
    return session.execute(stmt).rowcount or 0
