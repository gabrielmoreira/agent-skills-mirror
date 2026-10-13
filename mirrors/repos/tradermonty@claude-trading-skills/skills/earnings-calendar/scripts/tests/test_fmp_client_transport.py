"""Offline transport tests for the vendored FMP client core.

Covers value-based API-key redaction and the per-call invalid-JSON retry.
"""

import requests
from fmp_client import FMPClient

SECRET = "secret-token-xyz"  # pragma: allowlist secret
URL = "https://example.invalid/x"


class Bad:
    status_code = 200
    text = ""

    def json(self):
        raise ValueError(f"bad body echoing {SECRET}")


class Good:
    status_code = 200
    text = ""

    def json(self):
        return [{"ok": 1}]


class Http:
    def __init__(self, status, text=""):
        self.status_code = status
        self.text = text

    def json(self):
        return {}


class Session:
    def __init__(self, *outcomes):
        self.outcomes = list(outcomes)
        self.calls = 0

    def get(self, url, *, params, timeout):
        self.calls += 1
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def make(*outcomes):
    client = FMPClient(api_key=SECRET)
    client.RATE_LIMIT_DELAY = 0
    client.session = Session(*outcomes)
    return client


def test_redact_secret_masks_bare_value_and_url_pattern():
    client = make()
    text = client._redact_secret(f"echo {SECRET} and https://h/x?apikey=abc&y=1")
    assert SECRET not in text
    assert "abc" not in text


def test_redact_secret_masks_short_keys_by_value():
    client = FMPClient(api_key="abcde")
    assert "abcde" not in client._redact_secret("proxy echoed abcde in failure")


def test_request_exception_message_is_redacted_on_stderr_and_last_error(capsys):
    client = make(requests.ConnectionError(f"proxy echoed {SECRET}"))
    assert client._rate_limited_get(URL) is None
    assert SECRET not in capsys.readouterr().err
    assert SECRET not in client._last_error


def test_http_error_body_is_redacted_on_stderr_and_last_error(capsys):
    client = make(Http(403, f"denied {SECRET}"))
    assert client._rate_limited_get(URL) is None
    assert SECRET not in capsys.readouterr().err
    assert SECRET not in client._last_error


def test_invalid_json_retries_then_soft_fails_with_redacted_reason(capsys):
    client = make(Bad(), Bad())
    assert client._rate_limited_get(URL) is None
    err = capsys.readouterr().err
    assert SECRET not in err
    assert "invalid JSON response" in err
    assert "invalid JSON response" in client._last_error
    assert SECRET not in client._last_error
    assert client.session.calls == 2


def test_invalid_json_quiet_prints_nothing(capsys):
    client = make(Bad(), Bad())
    assert client._rate_limited_get(URL, quiet=True) is None
    assert capsys.readouterr().err == ""
    assert "invalid JSON response" in client._last_error


def test_invalid_json_then_success_returns_data():
    client = make(Bad(), Good())
    assert client._rate_limited_get(URL, quiet=True) == [{"ok": 1}]
    assert client.session.calls == 2


def test_retry_after_failed_chain_still_happens_on_next_call():
    client = make(Bad(), Http(500, "boom"), Bad(), Good())
    assert client._rate_limited_get(URL, quiet=True) is None
    assert client._rate_limited_get(URL, quiet=True) == [{"ok": 1}]


def test_429_chain_passes_json_retry_flag_through(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda _s: None)
    client = make(Http(429), Good())
    assert client._rate_limited_get(URL, quiet=True) == [{"ok": 1}]
