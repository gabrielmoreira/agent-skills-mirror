from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPTS = Path(__file__).resolve().parents[1]
import sys

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    import sys

    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


FMP = load_module("fmp_client_direct_test", SCRIPTS / "fmp_client.py")
PIPELINE = load_module("run_pipeline_direct_test", SCRIPTS / "run_pipeline.py")


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


class FMPClientTests(unittest.TestCase):
    def test_persistent_cache_and_raw_store_do_not_expose_api_key(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            cache = root / "cache.sqlite3"
            raw = root / "raw"
            client = FMP.FMPClient(
                api_key="top-secret-key",  # pragma: allowlist secret
                cache_path=cache,
                raw_store_dir=raw,
                max_api_calls=5,
                rate_limit_delay=0,
            )
            session = SequenceSession(
                [FakeResponse(200, [{"symbol": "ACME", "companyName": "Acme"}])]
            )
            client.session = session
            profile = client.get_profile("ACME")
            self.assertEqual(profile["symbol"], "ACME")
            self.assertEqual(client.api_calls_made, 1)
            client.close()

            raw_files = list(raw.glob("*.json"))
            self.assertEqual(len(raw_files), 1)
            raw_text = raw_files[0].read_text(encoding="utf-8")
            self.assertNotIn("top-secret-key", raw_text)
            self.assertNotIn("apikey", json.loads(raw_text)["params"])

            offline = FMP.FMPClient(
                api_key=None,
                offline=True,
                cache_path=cache,
                raw_store_dir=None,
                max_api_calls=5,
                rate_limit_delay=0,
            )
            cached = offline.get_profile("ACME")
            self.assertEqual(cached["companyName"], "Acme")
            self.assertEqual(offline.api_calls_made, 0)
            self.assertEqual(offline.cache_hits, 1)
            offline.close()

    def test_stable_failure_falls_back_to_v3(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            client = FMP.FMPClient(
                api_key="key",  # pragma: allowlist secret
                cache_path=Path(temp) / "cache.sqlite3",
                max_api_calls=5,
                rate_limit_delay=0,
            )
            client.session = SequenceSession(
                [
                    FakeResponse(403, {"error": "plan"}),
                    FakeResponse(200, [{"symbol": "ACME", "companyName": "Acme"}]),
                ]
            )
            profile = client.get_profile("ACME")
            self.assertEqual(profile["symbol"], "ACME")
            self.assertEqual(client.api_calls_made, 2)
            client.close()

    def test_call_budget_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            client = FMP.FMPClient(
                api_key="key",  # pragma: allowlist secret
                cache_path=Path(temp) / "cache.sqlite3",
                max_api_calls=1,
                rate_limit_delay=0,
            )
            client.session = SequenceSession(
                [
                    FakeResponse(200, [{"symbol": "A", "companyName": "A"}]),
                ]
            )
            self.assertIsNotNone(client.get_profile("A"))
            with self.assertRaises(FMP.ApiCallBudgetExceeded):
                client.get_profile("B")
            client.close()


class FakePipelineClient:
    def __init__(self):
        self.api_calls_made = 0
        self.max_api_calls = 999
        self.cache_hits = 0
        self.symbol_rows: dict[str, dict[str, Any]] = {}
        sectors = [
            ("Technology", "Software"),
            ("Industrials", "Machinery"),
            ("Basic Materials", "Chemicals"),
            ("Consumer Defensive", "Packaged Foods"),
        ]
        counter = 0
        for exchange in PIPELINE.EXCHANGES:
            for lane_idx, (sector, industry) in enumerate(sectors):
                counter += 1
                symbol = f"T{counter:02d}"
                self.symbol_rows[symbol] = {
                    "symbol": symbol,
                    "companyName": f"Test {symbol}",
                    "exchangeShortName": exchange,
                    "sector": sector,
                    "industry": industry,
                    "price": (20.0, 50.0, 30.0, 45.0)[lane_idx],
                    "marketCap": 700_000_000 + counter * 500_000_000,
                    "volume": 600_000,
                    "isEtf": False,
                    "isFund": False,
                    "isActivelyTrading": True,
                    "currency": "USD",
                    "country": "US",
                    "lane_idx": lane_idx,
                }

    def get_company_screener(self, *, exchange, min_market_cap, max_market_cap, min_price, limit):
        self.api_calls_made += 1
        return [
            {k: v for k, v in row.items() if k != "lane_idx"}
            for row in self.symbol_rows.values()
            if row["exchangeShortName"] == exchange
            and min_market_cap < row["marketCap"] < max_market_cap
            and row["price"] > min_price
        ][:limit]

    def get_bulk_dataset(self, endpoint: str, **params):
        self.api_calls_made += 1
        if endpoint == "analyst-estimates-bulk":
            year = int(params["year"])
            rows = []
            for symbol, source in self.symbol_rows.items():
                idx = source["lane_idx"]
                fy1 = 1.5 + idx * 0.2
                growth = (1.18, 1.32, 1.10, 1.20)[idx]
                offset = year - 2026
                eps = fy1 * (growth**offset)
                revenue_growth = (1.11, 1.24, 1.05, 1.12)[idx]
                revenue = 500_000_000 * (revenue_growth**offset)
                rows.append(
                    {
                        "symbol": symbol,
                        "date": f"{year}-12-31",
                        "fiscalYear": str(year),
                        "epsAvg": eps,
                        "epsLow": eps * 0.9,
                        "epsHigh": eps * 1.1,
                        "revenueAvg": revenue,
                        "numAnalystsEps": 6,
                        "numAnalystsRevenue": 6,
                    }
                )
            return rows
        if endpoint == "eod-bulk":
            return [
                {"symbol": symbol, "volume": 500_000 + idx * 50_000}
                for idx, symbol in enumerate(sorted(self.symbol_rows))
            ]
        if endpoint == "ratios-ttm-bulk":
            return [
                {"symbol": symbol, "freeCashFlowYield": 0.07, "netDebtToEBITDA": 1.2}
                for symbol in self.symbol_rows
            ]
        if endpoint == "key-metrics-ttm-bulk":
            return [
                {"symbol": symbol, "returnOnInvestedCapital": 0.16, "enterpriseValueOverFCF": 14.0}
                for symbol in self.symbol_rows
            ]
        if endpoint == "income-statement-growth-bulk":
            return [
                {"symbol": symbol, "growthRevenue": 0.12, "growthEPS": 0.18}
                for symbol in self.symbol_rows
            ]
        return []

    def get_analyst_estimates(self, symbol, *, period="annual", limit=6):
        raise AssertionError("bulk estimate path should be used")

    def get_key_metrics_ttm(self, symbol):
        self.api_calls_made += 1
        return [
            {
                "symbol": symbol,
                "returnOnInvestedCapitalTTM": 0.16,
                "freeCashFlowYieldTTM": 0.07,
                "evToFreeCashFlowTTM": 14.0,
                "netDebtToEBITDATTM": 1.2,
                "stockBasedCompensationToRevenueTTM": 0.02,
            }
        ]

    def get_historical_prices(self, symbol, *, from_date, to_date):
        return [{"date": f"2026-08-{day:02d}", "volume": 500_000} for day in range(1, 25)]

    def diagnostics(self):
        return {
            "api_calls_made": self.api_calls_made,
            "max_api_calls": self.max_api_calls,
            "cache_hits": self.cache_hits,
            "failure_count": 0,
            "failure_samples": [],
            "disabled_endpoint_count": 0,
            "offline": False,
        }


class DirectPipelineTests(unittest.TestCase):
    def test_direct_pipeline_keeps_provider_payloads_on_disk_and_emits_compact_summary(
        self,
    ) -> None:
        config = PIPELINE.load_config(None)
        config.update(
            {
                "company_screener_limit": 100,
                "pre_enrichment_limit": 20,
                "exact_liquidity_limit": 20,
                "provider_prefilter_pool_size": 12,
                "provider_prefilter_minimum_pool": 8,
                "provider_prefilter_per_lane": 4,
                "max_deep_dive_candidates": 3,
                "bulk_estimate_minimum_coverage_pct": 10.0,
            }
        )
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "run-direct"
            result = PIPELINE.execute_pipeline(
                FakePipelineClient(),
                config,
                analysis_as_of=datetime(2026, 8, 29, 17, tzinfo=timezone.utc),
                output_dir=output,
                include_packets=False,
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.summary["status"], "ready_for_underwriting")
            self.assertEqual(result.summary["runtime"]["skill_version"], "3.6.1")
            self.assertEqual(result.summary["estimate_acquisition_mode"], "analyst_estimates_bulk")
            self.assertTrue(result.summary["listing_enumeration_verified"])
            self.assertGreaterEqual(len(result.summary["selected_symbols"]), 1)
            self.assertLess(len(json.dumps(result.summary).encode("utf-8")), 20_000)
            self.assertTrue((output / "run-summary.json").is_file())
            self.assertTrue((output / "NEXT_ACTION.json").is_file())
            self.assertTrue((output / "audit" / "provider-prefilter-audit.json").is_file())
            self.assertTrue((output / "audit" / "broad-screen-audit.json").is_file())
            next_action = json.loads((output / "NEXT_ACTION.json").read_text(encoding="utf-8"))
            self.assertFalse(next_action["user_confirmation_required"])
            self.assertTrue(next_action["do_not_read_bulk_provider_payloads_into_model_context"])

    def test_adaptive_enumeration_splits_saturated_band(self) -> None:
        class SaturatedClient:
            def get_company_screener(
                self, *, exchange, min_market_cap, max_market_cap, min_price, limit
            ):
                width = max_market_cap - min_market_cap
                count = limit if width > 100_000_000 else max(1, limit - 1)
                return [
                    {
                        "symbol": f"{exchange[:1]}{int(min_market_cap)}{idx}",
                        "companyName": "Test",
                        "exchangeShortName": exchange,
                        "price": 10,
                        "marketCap": min_market_cap + (idx + 1) * max(width / (count + 1), 1),
                        "isEtf": False,
                        "isFund": False,
                        "isActivelyTrading": True,
                    }
                    for idx in range(count)
                ]

        rows, audit = PIPELINE.collect_listing_universe(
            SaturatedClient(),
            min_market_cap=500_000_000,
            max_market_cap=1_000_000_000,
            min_price=5,
            page_limit=4,
            minimum_band_width=50_000_000,
            maximum_depth=8,
        )
        self.assertTrue(audit["enumeration_verified"])
        self.assertGreater(audit["query_count"], len(PIPELINE.EXCHANGES))
        self.assertTrue(rows)


if __name__ == "__main__":
    unittest.main()
