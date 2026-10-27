"""Schema-drift hardening tests for the market breadth CSV client (inline CSV, no network)."""

import sys
from unittest.mock import Mock

import csv_client
import market_breadth_analyzer
import pytest

DETAIL_COLUMNS = list(csv_client.DETAIL_COLUMNS)
DETAIL_HEADER = ",".join(DETAIL_COLUMNS)
GOOD_ROW = "2025-01-01,5000,0.50,0.45,0.55,1,false,0,no,yes"
DRIFT_PREFIX = "ERROR: market_breadth_data.csv schema drift: missing columns ["


def _response(text):
    response = Mock()
    response.text = text
    response.headers = {}
    return response


def _patch_get(monkeypatch, text):
    get = Mock(return_value=_response(text))
    monkeypatch.setattr(csv_client.requests, "get", get)
    return get


def test_detail_header_drift_prints_one_error_and_returns_empty(monkeypatch, capsys):
    header = DETAIL_HEADER.replace("Is_Peak", "Is_Peak_Renamed").replace("Date,", "Trade_Date,", 1)
    _patch_get(monkeypatch, "\n".join([header, GOOD_ROW, GOOD_ROW, GOOD_ROW]))

    assert csv_client.fetch_detail_csv("https://example.test/d.csv") == []

    err = capsys.readouterr().err
    assert err.count("schema drift") == 1
    assert f"{DRIFT_PREFIX}Date,Is_Peak]" in err
    assert "Skipping line" not in err


def test_detail_drift_lists_sorted_comma_separated_names(monkeypatch, capsys):
    header = ",".join(c for c in DETAIL_COLUMNS if c not in ("Is_Trough", "Bearish_Signal"))
    _patch_get(monkeypatch, header + "\n")

    assert csv_client.fetch_detail_csv("https://example.test/d.csv") == []

    assert f"{DRIFT_PREFIX}Bearish_Signal,Is_Trough]" in capsys.readouterr().err


@pytest.mark.parametrize("fetch", ["detail", "summary"])
def test_unparsable_csv_reports_drift_instead_of_crashing(monkeypatch, capsys, fetch):
    oversized = "x" * 200_000  # beyond csv.field_size_limit() -> csv.Error
    if fetch == "detail":
        _patch_get(monkeypatch, f'{DETAIL_HEADER}\n"{oversized}",1\n')
        assert csv_client.fetch_detail_csv("https://example.test/d.csv") == []
        name = "market_breadth_data.csv"
    else:
        _patch_get(monkeypatch, f'Metric,Value\n"{oversized}",1\n')
        assert csv_client.fetch_summary_csv("https://example.test/s.csv") == {}
        name = "market_breadth_summary.csv"
    err = capsys.readouterr().err
    assert err.count(f"ERROR: {name} schema drift: unparsable CSV") == 1


def test_detail_bom_header_is_accepted(monkeypatch, capsys):
    _patch_get(monkeypatch, "﻿" + DETAIL_HEADER + "\n" + GOOD_ROW + "\n")

    rows = csv_client.fetch_detail_csv("https://example.test/d.csv")

    assert [r["Date"] for r in rows] == ["2025-01-01"]
    assert "ERROR" not in capsys.readouterr().err


def test_detail_empty_body_is_drift(monkeypatch, capsys):
    _patch_get(monkeypatch, "")

    assert csv_client.fetch_detail_csv("https://example.test/d.csv") == []
    assert "schema drift" in capsys.readouterr().err


def test_detail_happy_path_has_no_error(monkeypatch, capsys):
    _patch_get(monkeypatch, DETAIL_HEADER + "\n" + GOOD_ROW + "\n")

    assert len(csv_client.fetch_detail_csv("https://example.test/d.csv")) == 1
    assert "ERROR" not in capsys.readouterr().err


REQUIRED = ("Average Peaks (200MA)", "Average Troughs (8MA < 0.4)")


def test_summary_missing_metrics_warns_once_each(monkeypatch, capsys):
    _patch_get(monkeypatch, "Metric,Value\nCurrent,0.55\n")

    assert csv_client.fetch_summary_csv("https://example.test/s.csv") == {"Current": "0.55"}

    err = capsys.readouterr().err
    for name in REQUIRED:
        assert err.count(f"WARN: market_breadth_summary.csv missing metric '{name}'") == 1


def test_summary_with_required_metrics_and_bom_has_no_warning(monkeypatch, capsys):
    body = "Metric,Value\nAverage Peaks (200MA),0.6\nAverage Troughs (8MA < 0.4),0.3\n"
    _patch_get(monkeypatch, "﻿" + body)

    result = csv_client.fetch_summary_csv("https://example.test/s.csv")

    assert result == {"Average Peaks (200MA)": "0.6", "Average Troughs (8MA < 0.4)": "0.3"}
    assert capsys.readouterr().err == ""


def test_summary_only_one_missing_metric_warns_for_that_one(monkeypatch, capsys):
    _patch_get(monkeypatch, "Metric,Value\nAverage Peaks (200MA),0.6\n")

    csv_client.fetch_summary_csv("https://example.test/s.csv")

    err = capsys.readouterr().err
    assert "missing metric 'Average Troughs (8MA < 0.4)'" in err
    assert "missing metric 'Average Peaks (200MA)'" not in err


def test_summary_header_drift_errors_and_returns_empty(monkeypatch, capsys):
    _patch_get(monkeypatch, "Name,Val\nAverage Peaks (200MA),0.6\n")

    assert csv_client.fetch_summary_csv("https://example.test/s.csv") == {}

    err = capsys.readouterr().err
    assert "ERROR: market_breadth_summary.csv schema drift: missing columns [Metric,Value]" in err
    assert "missing metric" not in err


def test_summary_header_drift_single_missing_column(monkeypatch, capsys):
    _patch_get(monkeypatch, "Metric,Val\nx,1\n")

    assert csv_client.fetch_summary_csv("https://example.test/s.csv") == {}
    assert "missing columns [Value]" in capsys.readouterr().err


def test_main_exits_1_for_drifted_detail_csv(monkeypatch, capsys, tmp_path):
    get = _patch_get(monkeypatch, "Wrong,Header\n1,2\n")
    monkeypatch.setattr(sys, "argv", ["market_breadth_analyzer.py", "--output-dir", str(tmp_path)])

    with pytest.raises(SystemExit) as exc:
        market_breadth_analyzer.main()

    assert exc.value.code == 1
    assert capsys.readouterr().err.count("schema drift") == 1
    assert get.call_count == 1
    assert list(tmp_path.iterdir()) == []


def test_detail_padded_header_parses_values(monkeypatch, capsys):
    header = ", ".join(DETAIL_COLUMNS)
    _patch_get(monkeypatch, header + "\n" + GOOD_ROW + "\n")

    rows = csv_client.fetch_detail_csv("https://example.test/d.csv")

    assert len(rows) == 1
    assert rows[0]["Date"] == "2025-01-01"
    assert rows[0]["S&P500_Price"] == 5000.0
    assert "ERROR" not in capsys.readouterr().err


def test_summary_padded_header_parses_values(monkeypatch):
    _patch_get(monkeypatch, "Metric , Value \nCurrent,0.55\n")

    assert csv_client.fetch_summary_csv("https://example.test/s.csv") == {"Current": "0.55"}
