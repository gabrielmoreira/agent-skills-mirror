from __future__ import annotations

from conftest import make_raw

from wxdata.ingest import dedupe_readings, drop_outliers, normalize_units


def test_normalize_converts_fahrenheit_and_inhg() -> None:
    raw = make_raw(temperature=68.0, temperature_unit="F", pressure=29.92, pressure_unit="inHg")
    [r] = normalize_units([raw])
    assert r.temperature == 20.0
    assert r.temperature_unit == "C"
    assert r.pressure == 1013.2
    assert r.pressure_unit == "hPa"


def test_normalize_keeps_missing_values() -> None:
    [r] = normalize_units([make_raw(temperature=None, pressure=None)])
    assert r.temperature is None
    assert r.pressure is None


def test_dedupe_drops_exact_repeats() -> None:
    readings = [make_raw(), make_raw(), make_raw(at="2024-07-01T12:05:00+00:00")]
    assert len(dedupe_readings(readings)) == 2


def test_dedupe_keeps_different_stations() -> None:
    readings = [make_raw("KSEA"), make_raw("KPDX")]
    assert len(dedupe_readings(readings)) == 2


def test_drop_outliers() -> None:
    readings = [make_raw(temperature=-75.0), make_raw(temperature=21.0), make_raw(temperature=None)]
    kept = drop_outliers(readings)
    assert [r.temperature for r in kept] == [21.0, None]
