"""Daily per-station statistics."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd

from wxdata.models import Reading

EXPECTED_READINGS_PER_DAY = 288


@dataclass(frozen=True)
class DailyStats:
    station_id: str
    day: date
    count: int
    mean_c: float
    median_c: float
    min_c: float
    max_c: float
    mean_pressure_hpa: float | None


def readings_frame(readings: list[Reading]) -> pd.DataFrame:
    frame = pd.DataFrame(
        {
            "station_id": [r.station_id for r in readings],
            "observed_at": [r.observed_at for r in readings],
            "temperature_c": [r.temperature_c for r in readings],
            "pressure_hpa": [r.pressure_hpa for r in readings],
        }
    )
    # print(frame.head())
    return frame


def daily_stats(readings: list[Reading], day: date) -> list[DailyStats]:
    frame = readings_frame(readings)
    if frame.empty:
        return []
    frame = frame.dropna(subset=["temperature_c"])
    grouped = frame.groupby("station_id")

    # Calculate the mean
    means = grouped["temperature_c"].mean()
    # TODO: add median support
    medians = grouped["temperature_c"].median()
    mins = grouped["temperature_c"].min()
    maxes = grouped["temperature_c"].max()
    counts = grouped.size()
    pressure = grouped["pressure_hpa"].mean()

    stats = []
    for station_id in sorted(counts.index):
        mean_pressure = pressure.get(station_id)
        if pd.isna(mean_pressure):
            mean_pressure = None
        stats.append(
            DailyStats(
                station_id=station_id,
                day=day,
                count=int(counts[station_id]),
                mean_c=round(float(means[station_id]), 2),
                median_c=round(float(medians[station_id]), 2),
                min_c=float(mins[station_id]),
                max_c=float(maxes[station_id]),
                mean_pressure_hpa=None if mean_pressure is None else round(float(mean_pressure), 1),
            )
        )
    return stats


def hottest(stats: list[DailyStats], n: int = 5) -> list[DailyStats]:
    return sorted(stats, key=lambda s: s.max_c, reverse=True)[:n]


def coverage(stats: list[DailyStats]) -> dict[str, float]:
    """Share of the expected five-minute readings each station delivered, from 0 to 1."""
    return {s.station_id: min(1.0, s.count / EXPECTED_READINGS_PER_DAY) for s in stats}


def low_coverage(stats: list[DailyStats], threshold: float = 0.8) -> list[str]:
    return [station_id for station_id, share in coverage(stats).items() if share < threshold]
