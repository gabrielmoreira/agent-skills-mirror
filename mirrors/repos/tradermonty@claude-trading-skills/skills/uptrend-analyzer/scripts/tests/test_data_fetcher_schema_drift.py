"""Schema-drift hardening tests for UptrendDataFetcher (inline CSV, mocked HTTP)."""

import sys
from unittest.mock import MagicMock, patch

import pytest
import requests
import uptrend_analyzer as analyzer
from data_fetcher import UptrendDataFetcher

TS_HEADER = "worksheet,date,count,total,ratio,ma_10,slope,trend"
SS_HEADER = "Sector,Ratio,10MA,Trend,Slope,Status"
GOOD_TS = TS_HEADER + "\nall,2026-01-15,840,2800,0.300,0.280,0.0015,up\n"
GOOD_SS = SS_HEADER + "\nTechnology,0.288,0.266,Up,0.002,Normal\n"
TS_ERR = "ERROR: uptrend_ratio_timeseries.csv schema drift:"
SS_ERR = "ERROR: sector_summary.csv schema drift:"
NO_ALL = f"{TS_ERR} no usable 'all' ratio values"


def _resp(text):
    resp = MagicMock()
    resp.text = text
    resp.raise_for_status = MagicMock()
    return resp


def test_timeseries_header_drift_errors_once_and_returns_empty(capsys):
    fetcher = UptrendDataFetcher()
    body = "worksheet,date,count,total,ratio_pct,ma_10,slope,trend\nall,2026-01-15,1,2,0.3,,,up\n"
    with patch.object(fetcher.session, "get", return_value=_resp(body)):
        assert fetcher.fetch_timeseries() == []

    err = capsys.readouterr().err
    assert err.count(TS_ERR) == 1
    assert f"{TS_ERR} missing columns [ratio]" in err


def test_timeseries_drift_lists_sorted_names(capsys):
    fetcher = UptrendDataFetcher()
    with patch.object(fetcher.session, "get", return_value=_resp("worksheet,date\nall,x\n")):
        assert fetcher.fetch_timeseries() == []
    expected = f"{TS_ERR} missing columns [count,ma_10,ratio,slope,total,trend]"
    assert expected in capsys.readouterr().err


@pytest.mark.parametrize("which", ["timeseries", "sector"])
def test_unparsable_csv_reports_drift_once_and_caches(capsys, which):
    oversized = "x" * 200_000  # beyond csv.field_size_limit() -> csv.Error
    fetcher = UptrendDataFetcher()
    header = TS_HEADER if which == "timeseries" else SS_HEADER
    prefix = TS_ERR if which == "timeseries" else SS_ERR
    fetch = fetcher.fetch_timeseries if which == "timeseries" else fetcher.fetch_sector_summary
    body = f'{header}\n"{oversized}",1\n'
    with patch.object(fetcher.session, "get", return_value=_resp(body)) as get:
        assert fetch() == []
        assert fetch() == []
    assert get.call_count == 1
    assert capsys.readouterr().err.count(f"{prefix} unparsable CSV") == 1


def test_timeseries_drift_is_cached_prints_once_single_http_call(capsys):
    fetcher = UptrendDataFetcher()
    with patch.object(fetcher.session, "get", return_value=_resp("a,b\n1,2\n")) as mock_get:
        assert fetcher.fetch_timeseries() == []
        assert fetcher.fetch_timeseries() == []
        assert fetcher.get_all_timeseries() == []
        assert mock_get.call_count == 1
    assert capsys.readouterr().err.count(TS_ERR) == 1


def test_timeseries_bom_header_is_accepted(capsys):
    fetcher = UptrendDataFetcher()
    with patch.object(fetcher.session, "get", return_value=_resp("﻿" + GOOD_TS)):
        rows = fetcher.fetch_timeseries()
    assert len(rows) == 1 and rows[0]["ratio"] == 0.3
    assert "ERROR" not in capsys.readouterr().err


def test_timeseries_all_rows_with_empty_ratio_is_drift(capsys):
    body = (
        TS_HEADER
        + "\nall,2026-01-14,,,,,,\nall,2026-01-15,,,,,,\nsec_energy,2026-01-15,1,2,0.5,,,up\n"
    )
    fetcher = UptrendDataFetcher()
    with patch.object(fetcher.session, "get", return_value=_resp(body)) as mock_get:
        assert fetcher.fetch_timeseries() == []
        assert fetcher.fetch_timeseries() == []
        assert mock_get.call_count == 1
    assert capsys.readouterr().err.count(NO_ALL) == 1


def test_timeseries_all_rows_with_nan_ratio_is_drift(capsys):
    body = TS_HEADER + "\nall,2026-01-15,1,2,nan,,,up\nall,2026-01-16,1,2,NaN,,,up\n"
    fetcher = UptrendDataFetcher()
    with patch.object(fetcher.session, "get", return_value=_resp(body)):
        assert fetcher.fetch_timeseries() == []
    assert NO_ALL in capsys.readouterr().err


def test_timeseries_zero_all_rows_is_drift(capsys):
    body = TS_HEADER + "\nsec_energy,2026-01-15,1,2,0.5,,,up\n"
    fetcher = UptrendDataFetcher()
    with patch.object(fetcher.session, "get", return_value=_resp(body)):
        assert fetcher.fetch_timeseries() == []
    assert NO_ALL in capsys.readouterr().err


def test_timeseries_one_usable_all_ratio_is_not_drift(capsys):
    body = TS_HEADER + "\nall,2026-01-14,,,,,,\nall,2026-01-15,1,2,0.4,,,up\n"
    fetcher = UptrendDataFetcher()
    with patch.object(fetcher.session, "get", return_value=_resp(body)):
        assert len(fetcher.fetch_timeseries()) == 2
    assert "ERROR" not in capsys.readouterr().err


def test_timeseries_transport_failure_is_not_cached():
    fetcher = UptrendDataFetcher()
    boom = requests.exceptions.Timeout("t")
    with patch.object(fetcher.session, "get", side_effect=boom) as mock_get:
        assert fetcher.fetch_timeseries() == []
        assert fetcher.fetch_timeseries() == []
        assert mock_get.call_count == 2


def test_sector_summary_header_drift_errors_once_single_http_call(capsys):
    fetcher = UptrendDataFetcher()
    body = "Sector,Ratio,10MA,Trend,Slope,State\nTechnology,0.1,0.1,Up,0.1,Normal\n"
    with patch.object(fetcher.session, "get", return_value=_resp(body)) as mock_get:
        assert fetcher.fetch_sector_summary() == []
        assert fetcher.fetch_sector_summary() == []
        assert mock_get.call_count == 1
    err = capsys.readouterr().err
    assert err.count(SS_ERR) == 1
    assert f"{SS_ERR} missing columns [Status]" in err


def test_sector_summary_happy_path_and_bom(capsys):
    fetcher = UptrendDataFetcher()
    with patch.object(fetcher.session, "get", return_value=_resp("﻿" + GOOD_SS)):
        rows = fetcher.fetch_sector_summary()
    assert rows[0]["Sector"] == "Technology" and rows[0]["Ratio"] == 0.288
    assert "ERROR" not in capsys.readouterr().err


def test_sector_summary_transport_failure_is_not_cached():
    fetcher = UptrendDataFetcher()
    boom = requests.exceptions.Timeout("t")
    with patch.object(fetcher.session, "get", side_effect=boom) as mock_get:
        assert fetcher.fetch_sector_summary() == []
        assert fetcher.fetch_sector_summary() == []
        assert mock_get.call_count == 2


@pytest.mark.parametrize(
    "body",
    [
        "worksheet,date,count,total,ratio_pct,ma_10,slope,trend\nall,2026-01-15,1,2,0.3,,,up\n",
        TS_HEADER + "\nall,2026-01-15,,,,,,\n",
    ],
)
def test_main_exits_1_for_drifted_timeseries(body, capsys, tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["uptrend_analyzer.py", "--output-dir", str(tmp_path)])
    with patch.object(requests.Session, "get", return_value=_resp(body)) as mock_get:
        with pytest.raises(SystemExit) as exc:
            analyzer.main()
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert err.count("schema drift") == 1
    assert "Cannot proceed without timeseries data" in err
    assert mock_get.call_count == 1
    assert list(tmp_path.iterdir()) == []


def test_timeseries_padded_header_parses_values(capsys):
    fetcher = UptrendDataFetcher()
    body = "worksheet, date, count, total, ratio, ma_10, slope, trend\n" + (
        "all,2026-01-15,840,2800,0.300,0.280,0.0015,up\n"
    )
    with patch.object(fetcher.session, "get", return_value=_resp(body)):
        rows = fetcher.fetch_timeseries()

    assert len(rows) == 1
    assert rows[0]["date"] == "2026-01-15"
    assert rows[0]["ratio"] == 0.3
    assert rows[0]["count"] == 840
    assert "schema drift" not in capsys.readouterr().err


def test_sector_summary_padded_header_parses_values(capsys):
    fetcher = UptrendDataFetcher()
    body = "Sector, Ratio, 10MA, Trend, Slope, Status\nTechnology,0.288,0.266,Up,0.002,Normal\n"
    with patch.object(fetcher.session, "get", return_value=_resp(body)):
        rows = fetcher.fetch_sector_summary()

    assert len(rows) == 1
    assert rows[0]["Ratio"] == 0.288
    assert rows[0]["10MA"] == 0.266
    assert rows[0]["Slope"] == 0.002
    assert "schema drift" not in capsys.readouterr().err


def test_short_timeseries_row_does_not_raise():
    from data_fetcher import _parse_timeseries_row

    parsed = _parse_timeseries_row({"worksheet": "all", "date": "2026-01-15"})

    assert parsed["worksheet"] == "all"
    assert parsed["ratio"] is None
    assert parsed["trend"] == ""
    assert parsed["count"] is None


def test_none_restval_timeseries_row_does_not_raise():
    from data_fetcher import _parse_timeseries_row

    parsed = _parse_timeseries_row(
        {"worksheet": "all", "date": None, "count": None, "ratio": None, "trend": None}
    )

    assert parsed["date"] == "" and parsed["trend"] == "" and parsed["ratio"] is None


def test_short_sector_summary_row_does_not_raise():
    from data_fetcher import _parse_sector_summary_row

    parsed = _parse_sector_summary_row({"Sector": "Energy", "Ratio": "0.4", "Trend": None})

    assert parsed["Sector"] == "Energy"
    assert parsed["Ratio"] == 0.4
    assert parsed["10MA"] is None
    assert parsed["Trend"] == "" and parsed["Status"] == ""
