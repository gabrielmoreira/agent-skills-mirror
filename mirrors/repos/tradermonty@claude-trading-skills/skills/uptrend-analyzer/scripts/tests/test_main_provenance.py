"""Provenance integration tests execute the real producer main."""

import json
from datetime import datetime, timedelta
from unittest import mock

import pytest
import uptrend_analyzer as analyzer
from helpers import make_all_timeseries, make_full_sector_summary
from test_uptrend_analyzer import _build_full_timeseries, _make_mock_fetcher


def run_main(output, run_id=None, invalid=False):
    rows = make_all_timeseries(n=25, base_ratio=0.28, slope=0.001)
    expected_date = rows[-1]["date"]
    summary = make_full_sector_summary()
    fetcher = _make_mock_fetcher(_build_full_timeseries(rows, summary), summary)
    if invalid:
        fetcher.get_latest_all.return_value = {"date": "not-a-date"}
    argv = ["uptrend_analyzer.py", "--output-dir", str(output)]
    if run_id is not None:
        argv += ["--run-id", run_id]
    with (
        mock.patch.object(analyzer, "UptrendDataFetcher", return_value=fetcher),
        mock.patch("sys.argv", argv),
    ):
        analyzer.main()
    report = next(output.glob("*.json"))
    return json.loads(report.read_text())["data_provenance"], expected_date


def test_main_records_primary_date_and_run(tmp_path):
    block, expected_date = run_main(tmp_path, "shared-run")
    assert block["run_id"] == "shared-run"
    assert block["as_of"] == expected_date
    assert datetime.fromisoformat(block["retrieved_at"]).utcoffset() == timedelta(0)
    assert block["endpoint"] == analyzer.TIMESERIES_URL
    assert "primary timeseries" in block["scope"]
    assert block["auxiliary_sources"][0]["as_of_verified"] is False
    for flag in ("adjusted", "point_in_time", "survivorship_free", "corporate_actions_handled"):
        assert block[flag] is False


def test_invalid_primary_date_writes_no_report(tmp_path):
    with pytest.raises(ValueError):
        run_main(tmp_path, "shared-run", invalid=True)
    assert list(tmp_path.iterdir()) == []


def test_default_run_id_is_unique(tmp_path):
    first, _ = run_main(tmp_path / "first")
    second, _ = run_main(tmp_path / "second")
    assert first["run_id"] and second["run_id"]
    assert first["run_id"] != second["run_id"]
