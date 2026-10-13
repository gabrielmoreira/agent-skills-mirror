"""Invalid-JSON retry is per call chain and respects the API budget."""

import pytest
import requests
from fmp_client import ApiCallBudgetExceeded, FMPClient


class Bad:
    status_code = 200
    text = ""

    def json(self):
        raise ValueError("not json")


class Good:
    status_code = 200
    text = ""

    def json(self):
        return [{"ok": 1}]


class Session:
    def __init__(self, *outcomes):
        self.outcomes = list(outcomes)

    def get(self, url, *, params, timeout):
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def make(max_api_calls, *outcomes):
    client = FMPClient(api_key="test-key-123456", max_api_calls=max_api_calls)
    client.RATE_LIMIT_DELAY = 0
    client.session = Session(*outcomes)
    return client


def test_retry_hits_budget_cap_then_fresh_budget_still_retries():
    client = make(1, Bad())
    with pytest.raises(ApiCallBudgetExceeded):
        client._rate_limited_get("https://example.invalid/x", quiet=True)

    client.max_api_calls = 10
    client.session = Session(Bad(), Good())
    assert client._rate_limited_get("https://example.invalid/x", quiet=True) == [{"ok": 1}]


def test_retry_counts_against_budget():
    client = make(10, Bad(), Good())
    assert client._rate_limited_get("https://example.invalid/x", quiet=True) == [{"ok": 1}]
    assert client.api_calls_made == 2


def test_retry_ending_in_request_exception_does_not_poison_next_call():
    client = make(10, Bad(), requests.ConnectionError("boom"))
    assert client._rate_limited_get("https://example.invalid/x", quiet=True) is None
    client.session = Session(Bad(), Good())
    assert client._rate_limited_get("https://example.invalid/x", quiet=True) == [{"ok": 1}]
