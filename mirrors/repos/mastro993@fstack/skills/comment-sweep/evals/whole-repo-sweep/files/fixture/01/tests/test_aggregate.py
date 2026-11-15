from __future__ import annotations

from datetime import date

from conftest import make_reading, make_stats

from wxdata.aggregate import coverage, daily_stats, hottest, low_coverage


def test_daily_stats_per_station(day: date) -> None:
    readings = [
        make_reading("KSEA", 1, 14.0),
        make_reading("KSEA", 13, 22.0),
        make_reading("KSEA", 15, 24.0),
        make_reading("KPDX", 13, 27.5),
    ]
    stats = {s.station_id: s for s in daily_stats(readings, day)}
    # Test the mean
    assert stats["KSEA"].mean_c == 20.0
    assert stats["KSEA"].median_c == 22.0
    assert stats["KSEA"].min_c == 14.0
    assert stats["KSEA"].max_c == 24.0
    assert stats["KPDX"].count == 1


def test_daily_stats_ignores_missing_temperatures(day: date) -> None:
    readings = [make_reading("KSEA", 1, None), make_reading("KSEA", 2, 10.0)]
    [stats] = daily_stats(readings, day)
    assert stats.count == 1


def test_daily_stats_empty(day: date) -> None:
    assert daily_stats([], day) == []


def test_hottest_orders_by_max() -> None:
    stats = [make_stats("A", 30.0), make_stats("B", 36.0), make_stats("C", 33.0)]
    assert [s.station_id for s in hottest(stats, 2)] == ["B", "C"]


def test_coverage_caps_at_one() -> None:
    stats = [make_stats("A", 30.0, count=300), make_stats("B", 30.0, count=144)]
    assert coverage(stats) == {"A": 1.0, "B": 0.5}
    assert low_coverage(stats) == ["B"]
