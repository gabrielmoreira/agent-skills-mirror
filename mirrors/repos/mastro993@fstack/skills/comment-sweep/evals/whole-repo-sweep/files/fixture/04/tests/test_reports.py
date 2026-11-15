from __future__ import annotations

from datetime import date

from conftest import make_stats

from wxdata.reports import render_alert, render_daily_report


def test_daily_report_lists_every_station(day: date) -> None:
    html = render_daily_report([make_stats("KSEA", 24.0), make_stats("KPDX", 31.0)], day)
    assert 'id="ksea"' in html
    assert 'id="kpdx"' in html
    assert "Station report for 2024-07-01" in html


def test_daily_report_flags_low_coverage(day: date) -> None:
    html = render_daily_report([make_stats("KSEA", 24.0, count=100)], day)
    assert '<a href="#ksea">KSEA</a>' in html


def test_alert_skipped_below_threshold(day: date) -> None:
    assert render_alert([make_stats("KSEA", 34.9)], day) is None


def test_alert_lists_hot_stations_hottest_first(day: date) -> None:
    body = render_alert([make_stats("KSEA", 35.0), make_stats("KPHX", 44.2)], day)
    assert body is not None
    assert body.index("KPHX") < body.index("KSEA")
    assert "Subject: Heat alert for 2024-07-01: 2 station(s)" in body
