from __future__ import annotations

from datetime import UTC, date, datetime

import pytest

from wxdata.aggregate import DailyStats
from wxdata.client import RawReading
from wxdata.models import Reading


@pytest.fixture
def day() -> date:
    return date(2024, 7, 1)


def make_raw(
    station_id: str = "KSEA", at: str = "2024-07-01T12:00:00+00:00", **kw: object
) -> RawReading:
    fields: dict[str, object] = {
        "temperature": 20.0,
        "temperature_unit": "C",
        "pressure": 1013.2,
        "pressure_unit": "hPa",
        "humidity": 55.0,
    }
    fields.update(kw)
    return RawReading(station_id=station_id, observed_at=at, **fields)  # type: ignore[arg-type]


def make_reading(station_id: str, hour: int, temperature_c: float | None) -> Reading:
    return Reading(
        station_id=station_id,
        observed_at=datetime(2024, 7, 1, hour, tzinfo=UTC),
        temperature_c=temperature_c,
        pressure_hpa=1012.0,
        humidity_pct=50.0,
    )


def make_stats(station_id: str, max_c: float, count: int = 288) -> DailyStats:
    return DailyStats(
        station_id=station_id,
        day=date(2024, 7, 1),
        count=count,
        mean_c=max_c - 8,
        median_c=max_c - 7,
        min_c=max_c - 15,
        max_c=max_c,
        mean_pressure_hpa=1012.0,
    )
