"""Tests for the FMPClient endpoint capability cache (workstream C, v3.6.1).

Covers: a 402/403 on a bulk endpoint is persisted to the SQLite cache under
``capability:<endpoint>``; a fresh second client instance pointed at the same
cache path pre-disables that endpoint and skips the HTTP call entirely; a
stale (TTL-expired) capability entry is re-probed; and the
``respect_capability_cache=False`` flag disables the whole mechanism.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import time
import unittest
from pathlib import Path
from typing import Any

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


FMP = load_module("fmp_client_capability_cache_test", SCRIPTS / "fmp_client.py")


class FakeResponse:
    def __init__(self, status_code: int, payload: Any):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class SequenceSession:
    def __init__(self, responses: list[FakeResponse]):
        self.responses = list(responses)
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def get(self, url: str, params=None, timeout=30):
        self.calls.append((url, dict(params or {})))
        if not self.responses:
            raise AssertionError("unexpected HTTP request")
        return self.responses.pop(0)

    def close(self):
        pass


def make_client(cache_path: Path, **kwargs) -> FMP.FMPClient:
    defaults = dict(
        api_key="key",  # pragma: allowlist secret
        cache_path=cache_path,
        max_api_calls=5,
        rate_limit_delay=0,
    )
    defaults.update(kwargs)
    return FMP.FMPClient(**defaults)


class CapabilityCacheTests(unittest.TestCase):
    def test_first_run_records_402_into_capability_cache(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            cache_path = Path(temp) / "cache.sqlite3"
            client = make_client(cache_path)
            client.session = SequenceSession([FakeResponse(402, {"error": "plan"})])
            rows = client.get_bulk_dataset("some-bulk-endpoint")
            self.assertEqual(rows, [])
            self.assertEqual(client.api_calls_made, 1)
            client.close()

            cache = FMP.SQLiteJsonCache(cache_path)
            key = "capability:https://financialmodelingprep.com/stable/some-bulk-endpoint"
            stored = cache.get(key, ttl_seconds=30 * 86_400)
            self.assertIsNotNone(stored)
            self.assertEqual(stored["status"], 402)
            self.assertEqual(stored["ttl_days"], 30)
            self.assertIn("checked_at", stored)
            cache.close()

    def test_second_client_instance_skips_call_on_cached_402(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            cache_path = Path(temp) / "cache.sqlite3"
            first = make_client(cache_path)
            first.session = SequenceSession([FakeResponse(402, {"error": "plan"})])
            first.get_bulk_dataset("some-bulk-endpoint")
            first.close()

            second = make_client(cache_path)
            second.session = SequenceSession([])  # any GET call raises AssertionError
            rows = second.get_bulk_dataset("some-bulk-endpoint")
            self.assertEqual(rows, [])
            self.assertEqual(second.api_calls_made, 0)
            self.assertEqual(second.capability_cache_hits, 1)
            self.assertIn(
                "https://financialmodelingprep.com/stable/some-bulk-endpoint",
                second._disabled_endpoints,
            )
            second.close()

    def test_403_is_also_cached_and_pre_disables(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            cache_path = Path(temp) / "cache.sqlite3"
            first = make_client(cache_path)
            first.session = SequenceSession([FakeResponse(403, {"error": "forbidden"})])
            first.get_bulk_dataset("another-endpoint")
            first.close()

            second = make_client(cache_path)
            second.session = SequenceSession([])
            rows = second.get_bulk_dataset("another-endpoint")
            self.assertEqual(rows, [])
            self.assertEqual(second.api_calls_made, 0)
            second.close()

    def test_ttl_expiry_re_probes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            cache_path = Path(temp) / "cache.sqlite3"
            first = make_client(cache_path)
            first.session = SequenceSession([FakeResponse(402, {"error": "plan"})])
            first.get_bulk_dataset("some-bulk-endpoint")
            first.close()

            # Manually age the stored capability row past the 30-day TTL.
            cache = FMP.SQLiteJsonCache(cache_path)
            key = "capability:https://financialmodelingprep.com/stable/some-bulk-endpoint"
            cache._connection.execute(
                "UPDATE responses SET created_at = ? WHERE cache_key = ?",
                (time.time() - 31 * 86_400, key),
            )
            cache._connection.commit()
            cache.close()

            second = make_client(cache_path)
            second.session = SequenceSession([FakeResponse(200, [{"symbol": "ACME"}])])
            rows = second.get_bulk_dataset("some-bulk-endpoint")
            self.assertEqual(rows, [{"symbol": "ACME"}])
            self.assertEqual(second.api_calls_made, 1)
            second.close()

    def test_respect_capability_cache_false_disables_mechanism(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            cache_path = Path(temp) / "cache.sqlite3"
            first = make_client(cache_path)
            first.session = SequenceSession([FakeResponse(402, {"error": "plan"})])
            first.get_bulk_dataset("some-bulk-endpoint")
            first.close()

            second = make_client(cache_path, respect_capability_cache=False)
            second.session = SequenceSession([FakeResponse(200, [{"symbol": "ACME"}])])
            rows = second.get_bulk_dataset("some-bulk-endpoint")
            self.assertEqual(rows, [{"symbol": "ACME"}])
            self.assertEqual(second.api_calls_made, 1)
            self.assertEqual(second.capability_cache_hits, 0)
            second.close()

    def test_quality_probe_or_other_endpoints_unaffected_on_200(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            cache_path = Path(temp) / "cache.sqlite3"
            client = make_client(cache_path)
            client.session = SequenceSession([FakeResponse(200, [{"symbol": "ACME"}])])
            rows = client.get_bulk_dataset("healthy-endpoint")
            self.assertEqual(rows, [{"symbol": "ACME"}])
            self.assertEqual(client.capability_cache_hits, 0)
            client.close()

    def test_remaining_calls_property(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            client = make_client(Path(temp) / "cache.sqlite3", max_api_calls=5)
            self.assertEqual(client.remaining_calls, 5)
            client.session = SequenceSession([FakeResponse(200, [{"symbol": "A"}])])
            client.get_bulk_dataset("healthy-endpoint")
            self.assertEqual(client.remaining_calls, 4)
            client.close()

    def test_diagnostics_exposes_capability_cache_hits(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            cache_path = Path(temp) / "cache.sqlite3"
            first = make_client(cache_path)
            first.session = SequenceSession([FakeResponse(402, {"error": "plan"})])
            first.get_bulk_dataset("some-bulk-endpoint")
            first.close()

            second = make_client(cache_path)
            second.session = SequenceSession([])
            second.get_bulk_dataset("some-bulk-endpoint")
            diag = second.diagnostics()
            self.assertEqual(diag["capability_cache_hits"], 1)
            second.close()


if __name__ == "__main__":
    unittest.main()
