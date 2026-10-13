"""Tests for get_economic_calendar.py"""

import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from unittest.mock import patch

import get_economic_calendar as _script_mod
import pytest
import requests

# Patch the vendored class via the script module's import binding.
FMPClient = _script_mod.FMPClient

# Add parent directory to path so we can import the script module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from get_economic_calendar import (
    fetch_economic_calendar,
    format_event_output,
    get_api_key,
    main,
    validate_date_range,
)

# ---------------------------------------------------------------------------
# Sample fixtures
# ---------------------------------------------------------------------------

SAMPLE_EVENTS = [
    {
        "date": "2025-01-15 14:30:00",
        "country": "US",
        "event": "Consumer Price Index (CPI) YoY",
        "currency": "USD",
        "previous": 2.6,
        "estimate": 2.7,
        "actual": None,
        "change": None,
        "impact": "High",
        "changePercentage": None,
    },
    {
        "date": "2025-01-16 10:00:00",
        "country": "EU",
        "event": "ECB Interest Rate Decision",
        "currency": "EUR",
        "previous": 4.5,
        "estimate": 4.5,
        "actual": None,
        "change": None,
        "impact": "High",
        "changePercentage": None,
    },
]


# ---------------------------------------------------------------------------
# get_api_key tests
# ---------------------------------------------------------------------------


class TestGetApiKey:
    def test_returns_key_when_set(self, monkeypatch):
        monkeypatch.setenv("FMP_API_KEY", "test_key_123")
        assert get_api_key() == "test_key_123"

    def test_returns_none_when_not_set(self, monkeypatch):
        monkeypatch.delenv("FMP_API_KEY", raising=False)
        assert get_api_key() is None


# ---------------------------------------------------------------------------
# fetch_economic_calendar tests
# ---------------------------------------------------------------------------


@dataclass
class RateFailure:
    """Shaped HTTP failure injected through the vendored client."""

    message: str


def patch_get(monkeypatch, outcome):
    """Patch FMPClient._rate_limited_get: outcome is a payload, RateFailure,
    or exception instance; returns captured calls."""

    calls = []

    def fake(self, url, params=None, quiet=False):
        calls.append({"url": url, "params": params, "quiet": quiet, "client": self})
        if isinstance(outcome, requests.exceptions.RequestException):
            # The real client catches transport exceptions internally and
            # surfaces them via _last_error ("request exception: <str>").
            self._last_error = f"request exception: {outcome}"
            return None
        if isinstance(outcome, Exception):
            raise outcome
        if isinstance(outcome, RateFailure):
            self._last_error = outcome.message
            return None
        self._last_error = None
        return outcome

    monkeypatch.setattr(_script_mod.FMPClient, "_rate_limited_get", fake)
    return calls


class TestFetchEconomicCalendar:
    def test_uses_singular_stable_endpoint(self, monkeypatch):
        calls = patch_get(monkeypatch, [])
        fetch_economic_calendar("2025-01-01", "2025-01-07", "test_key")

        assert calls[0]["url"] == "https://financialmodelingprep.com/stable/economic-calendar"
        assert "economics-calendar" not in calls[0]["url"]
        # Header auth (deliberate change, Issue #495): no apikey in the URL.
        assert "apikey" not in calls[0]["url"]

    def test_success_returns_events(self, monkeypatch):
        calls = patch_get(monkeypatch, SAMPLE_EVENTS)
        events = fetch_economic_calendar("2025-01-01", "2025-01-07", "test_key")

        assert events == SAMPLE_EVENTS
        assert calls[0]["client"].session.headers.get("apikey") == "test_key"

    def test_402_raises_clear_restricted_endpoint_error(self, monkeypatch):
        patch_get(
            monkeypatch,
            RateFailure("HTTP 402 - not available under your current subscription"),
        )
        with pytest.raises(ValueError, match="402|subscription|upgrade"):
            fetch_economic_calendar("2025-01-01", "2025-01-07", "test_key")

    def test_402_message_includes_upgrade_advice_and_body(self, monkeypatch):
        patch_get(
            monkeypatch,
            RateFailure("HTTP 402 - not available under your current subscription"),
        )
        with pytest.raises(ValueError) as excinfo:
            fetch_economic_calendar("2025-01-01", "2025-01-07", "test_key")
        assert "Upgrade your plan" in str(excinfo.value)
        assert "not available under your current subscription" in str(excinfo.value)

    def test_genuine_404_raises_instead_of_swallowing(self, monkeypatch):
        patch_get(monkeypatch, RateFailure('HTTP 404 - {"Error Message": "Not found"}'))
        with pytest.raises(ValueError, match="status code 404"):
            fetch_economic_calendar("2025-01-01", "2025-01-07", "test_key")

    def test_404_with_empty_array_body_no_longer_swallowed(self, monkeypatch):
        # Regression test: a 404 must never be silently treated as "zero events",
        # even if the error body happens to be "[]".
        patch_get(monkeypatch, RateFailure("HTTP 404 - []"))
        with pytest.raises(ValueError, match="status code 404"):
            fetch_economic_calendar("2025-01-01", "2025-01-07", "test_key")

    def test_non_200_response_fails_closed(self, monkeypatch):
        patch_get(monkeypatch, RateFailure("HTTP 503 - []"))
        with pytest.raises(ValueError, match="status code 503"):
            fetch_economic_calendar("2025-01-01", "2025-01-07", "test_key")

    def test_non_list_payload_fails_closed(self, monkeypatch):
        patch_get(monkeypatch, {"events": SAMPLE_EVENTS})
        with pytest.raises(ValueError, match="Unexpected API response format"):
            fetch_economic_calendar("2025-01-01", "2025-01-07", "test_key")

    def test_transport_error_has_clear_network_message(self, monkeypatch):
        patch_get(
            monkeypatch,
            requests.exceptions.ConnectionError("offline"),
        )
        with pytest.raises(ValueError, match="Network error: offline"):
            fetch_economic_calendar("2025-01-01", "2025-01-07", "test_key")


# ---------------------------------------------------------------------------
# validate_date_range tests
# ---------------------------------------------------------------------------


class TestValidateDateRange:
    def test_valid_range(self):
        validate_date_range("2025-01-01", "2025-01-31")

    def test_same_day(self):
        validate_date_range("2025-06-15", "2025-06-15")

    def test_max_90_days(self):
        validate_date_range("2025-01-01", "2025-03-31")  # 89 days

    def test_exceeds_90_days(self):
        with pytest.raises(ValueError, match="exceeds maximum of 90 days"):
            validate_date_range("2025-01-01", "2025-06-01")

    def test_start_after_end(self):
        with pytest.raises(ValueError, match="after end date"):
            validate_date_range("2025-03-01", "2025-01-01")

    def test_invalid_date_format(self):
        with pytest.raises(ValueError, match="Invalid date format"):
            validate_date_range("01-01-2025", "2025-01-31")

    def test_invalid_date_value(self):
        with pytest.raises(ValueError, match="Invalid date format"):
            validate_date_range("2025-13-01", "2025-14-01")

    def test_past_dates_warns(self, capsys):
        past = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        past_end = (datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d")
        validate_date_range(past, past_end)
        captured = capsys.readouterr()
        assert "in the past" in captured.err


# ---------------------------------------------------------------------------
# format_event_output tests
# ---------------------------------------------------------------------------


class TestFormatEventOutput:
    def test_json_format_roundtrip(self):
        output = format_event_output(SAMPLE_EVENTS, "json")
        parsed = json.loads(output)
        assert len(parsed) == 2
        assert parsed[0]["event"] == "Consumer Price Index (CPI) YoY"

    def test_json_empty_list(self):
        output = format_event_output([], "json")
        assert json.loads(output) == []

    def test_text_format_header(self):
        output = format_event_output(SAMPLE_EVENTS, "text")
        assert "Total: 2" in output

    def test_text_format_contains_event_name(self):
        output = format_event_output(SAMPLE_EVENTS, "text")
        assert "Consumer Price Index (CPI) YoY" in output
        assert "ECB Interest Rate Decision" in output

    def test_text_format_shows_previous(self):
        output = format_event_output(SAMPLE_EVENTS, "text")
        assert "Previous: 2.6" in output

    def test_text_format_omits_none_actual(self):
        output = format_event_output(SAMPLE_EVENTS, "text")
        assert "Actual:" not in output

    def test_text_format_shows_actual_when_present(self):
        events = [
            {
                "date": "2025-01-10 14:30:00",
                "country": "US",
                "event": "NFP",
                "currency": "USD",
                "previous": 200,
                "estimate": 210,
                "actual": 256,
                "change": 56,
                "impact": "High",
                "changePercentage": 28.0,
            }
        ]
        output = format_event_output(events, "text")
        assert "Actual: 256" in output
        assert "Change: 56" in output
        assert "Change %: 28.0%" in output

    def test_unknown_format_raises(self):
        with pytest.raises(ValueError, match="Unknown output format"):
            format_event_output([], "csv")


class TestMain:
    def test_missing_key_exits_without_fetching(self, monkeypatch, capsys):
        monkeypatch.delenv("FMP_API_KEY", raising=False)
        monkeypatch.setattr(sys, "argv", ["get_economic_calendar.py"])

        with pytest.raises(SystemExit) as exc:
            main()

        assert exc.value.code == 1
        assert "FMP API key is required" in capsys.readouterr().err

    def test_success_writes_requested_output(self, monkeypatch, tmp_path, capsys):
        output_path = tmp_path / "calendar.json"
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "get_economic_calendar.py",
                "--api-key",
                "test-key",
                "--from",
                "2026-08-11",
                "--to",
                "2026-08-12",
                "--output",
                str(output_path),
            ],
        )

        with patch("get_economic_calendar.fetch_economic_calendar", return_value=SAMPLE_EVENTS):
            with pytest.raises(SystemExit) as exc:
                main()

        assert exc.value.code == 0
        assert json.loads(output_path.read_text(encoding="utf-8")) == SAMPLE_EVENTS
        assert "Retrieved 2 events" in capsys.readouterr().err

    def test_fetch_failure_exits_one(self, monkeypatch, capsys):
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "get_economic_calendar.py",
                "--api-key",
                "test-key",
                "--from",
                "2026-08-11",
                "--to",
                "2026-08-12",
            ],
        )

        with patch("get_economic_calendar.fetch_economic_calendar", side_effect=ValueError("bad")):
            with pytest.raises(SystemExit) as exc:
                main()

        assert exc.value.code == 1
        assert "Error: bad" in capsys.readouterr().err
