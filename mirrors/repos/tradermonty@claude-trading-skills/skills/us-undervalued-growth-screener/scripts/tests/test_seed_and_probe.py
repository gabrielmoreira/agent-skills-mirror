"""Tests for v3.6.1 workstream A: seed apportionment, dynamic seed limit,
quality probe, FCF prefilter exclusion, cyclicality keywords, and the honest
scope fields surfaced through run-summary.json.
"""

from __future__ import annotations

import importlib.util
import random
import sys
import tempfile
import unittest
from datetime import datetime, timezone
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


PIPELINE = load_module("run_pipeline_seed_probe_test", SCRIPTS / "run_pipeline.py")
POOL = load_module("build_pool_seed_probe_test", SCRIPTS / "build_provider_prefilter_pool.py")


def _listing_row(
    symbol: str,
    *,
    sector: str,
    market_cap: float,
    price: float = 20.0,
    volume: float = 100_000.0,
) -> dict[str, Any]:
    return {
        "symbol": symbol,
        "sector": sector,
        "market_cap": market_cap,
        "price": price,
        "volume": volume,
    }


class QuotaApportionmentTests(unittest.TestCase):
    def test_quota_sums_to_limit_and_is_order_independent(self) -> None:
        sizes = {
            ("technology", "500000000-1000000000"): 40,
            ("industrials", "1000000000-2000000000"): 12,
            ("healthcare", "2000000000-5000000000"): 3,
            ("energy", "5000000000-10000000000"): 1,
        }
        quotas_a = PIPELINE._apportion_quota(sizes, 30)
        # Rebuild the same sizes dict with a shuffled insertion order; the
        # apportionment must not depend on Python dict iteration order.
        items = list(sizes.items())
        random.Random(7).shuffle(items)
        quotas_b = PIPELINE._apportion_quota(dict(items), 30)
        self.assertEqual(sum(quotas_a.values()), 30)
        self.assertEqual(quotas_a, quotas_b)
        for key, count in quotas_a.items():
            self.assertGreaterEqual(count, 1)
            self.assertLessEqual(count, sizes[key])

    def test_quota_below_cell_count_allocates_one_per_largest_cells(self) -> None:
        sizes = {
            ("a", "bucket"): 10,
            ("b", "bucket"): 5,
            ("c", "bucket"): 1,
        }
        quotas = PIPELINE._apportion_quota(sizes, 2)
        self.assertEqual(sum(quotas.values()), 2)
        self.assertEqual(quotas[("a", "bucket")], 1)
        self.assertEqual(quotas[("b", "bucket")], 1)
        self.assertEqual(quotas[("c", "bucket")], 0)


class DiversifiedSeedTests(unittest.TestCase):
    def _rows(self) -> list[dict[str, Any]]:
        rows = []
        for idx in range(40):
            sector = "Technology" if idx % 2 == 0 else "Industrials"
            rows.append(
                _listing_row(
                    f"SYM{idx:03d}",
                    sector=sector,
                    market_cap=700_000_000 + idx * 10_000_000,
                    price=10.0 + (idx % 5),
                    volume=100_000 + idx * 1_000,
                )
            )
        return rows

    def test_within_cell_ranking_prefers_dollar_volume_never_ticker(self) -> None:
        rows = self._rows()
        selected_a, audit_a = PIPELINE.diversified_seed(rows, 10, run_salt="2026-08-29")
        shuffled = list(rows)
        random.Random(11).shuffle(shuffled)
        selected_b, audit_b = PIPELINE.diversified_seed(shuffled, 10, run_salt="2026-08-29")
        symbols_a = sorted(PIPELINE._symbol(row) for row in selected_a)
        symbols_b = sorted(PIPELINE._symbol(row) for row in selected_b)
        self.assertEqual(symbols_a, symbols_b)
        self.assertEqual(audit_a["cell_count"], audit_b["cell_count"])
        self.assertEqual(audit_a["quota_method"], "sqrt_hamilton")
        self.assertEqual(audit_a["alphabetic_tie_break_used_count"], 0)

    def test_ties_use_hash_not_ticker(self) -> None:
        # Two rows in the same cell, identical price/volume/market-cap/missing
        # counts: the tie can only be broken by the salted hash.
        rows = [
            _listing_row(
                "ZZZZ", sector="Technology", market_cap=800_000_000, price=10, volume=1000
            ),
            _listing_row(
                "AAAA", sector="Technology", market_cap=800_000_000, price=10, volume=1000
            ),
        ]
        selected, audit = PIPELINE.diversified_seed(rows, 1, run_salt="salt-1")
        self.assertEqual(len(selected), 1)
        self.assertEqual(audit["hash_tie_break_used_count"], 1)
        # A different salt may pick the other row, but must remain deterministic
        # for a fixed salt across shuffled input order.
        reselected, _ = PIPELINE.diversified_seed(list(reversed(rows)), 1, run_salt="salt-1")
        self.assertEqual(PIPELINE._symbol(selected[0]), PIPELINE._symbol(reselected[0]))

    def test_economic_metrics_available_flips_selection_basis(self) -> None:
        rows = self._rows()
        for row in rows:
            row["eps_growth_pct"] = 12.0
        selected, audit = PIPELINE.diversified_seed(rows, 10, run_salt="2026-08-29")
        self.assertTrue(audit["economic_metrics_available_for_seed"])
        self.assertEqual(audit["seed_selection_basis"], "stratified_economic_score")

        rows_no_econ = self._rows()
        _, audit_no_econ = PIPELINE.diversified_seed(rows_no_econ, 10, run_salt="2026-08-29")
        self.assertFalse(audit_no_econ["economic_metrics_available_for_seed"])
        self.assertEqual(audit_no_econ["seed_selection_basis"], "stratified_liquidity_proxy")


class DynamicSeedLimitTests(unittest.TestCase):
    def test_effective_limit_is_bounded_by_remaining_budget(self) -> None:
        effective = PIPELINE.compute_effective_seed_limit(
            pre_enrichment_limit=180,
            seed_limit_cap=200,
            max_api_calls=350,
            api_calls_made=0,
            quality_probe_limit=35,
            exact_liquidity_limit=40,
            candidate_packet_reserve_calls=30,
            retry_reserve_calls=25,
        )
        # reserved = 35*2+40+30+25 = 165 (probe = key metrics + annual income
        # statement); remaining = 350; 350-165 = 185; min(180, 200, 185) = 180
        self.assertEqual(effective, 180)

    def test_effective_limit_shrinks_with_calls_already_made(self) -> None:
        effective = PIPELINE.compute_effective_seed_limit(
            pre_enrichment_limit=180,
            seed_limit_cap=200,
            max_api_calls=350,
            api_calls_made=165,
            quality_probe_limit=35,
            exact_liquidity_limit=40,
            candidate_packet_reserve_calls=30,
            retry_reserve_calls=25,
        )
        # remaining = 185; reserved = 165; 185-165 = 20
        self.assertEqual(effective, 20)

    def test_effective_limit_below_20_raises(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            PIPELINE.compute_effective_seed_limit(
                pre_enrichment_limit=180,
                seed_limit_cap=200,
                max_api_calls=350,
                api_calls_made=166,
                quality_probe_limit=35,
                exact_liquidity_limit=40,
                candidate_packet_reserve_calls=30,
                retry_reserve_calls=25,
            )
        self.assertIn("estimate seed budget insufficient", str(ctx.exception))


class QualityProbeTests(unittest.TestCase):
    class FakeClient:
        def __init__(self, payloads: dict[str, list[dict[str, Any]]]):
            self.payloads = payloads
            self.calls: list[str] = []

        def get_key_metrics_ttm(self, symbol: str):
            self.calls.append(symbol)
            return self.payloads.get(symbol, [])

    def test_probe_maps_fields_and_tolerates_failing_symbol(self) -> None:
        client = self.FakeClient(
            {
                "AAA": [
                    {
                        "returnOnInvestedCapitalTTM": 0.20,
                        "freeCashFlowYieldTTM": 0.08,
                        "evToFreeCashFlowTTM": 12.5,
                        "netDebtToEBITDATTM": 1.5,
                        "stockBasedCompensationToRevenueTTM": 0.03,
                        # revenue = EV / (EV/Sales) = 1.2B / 2.0 = 600M
                        "enterpriseValueTTM": 1_200_000_000,
                        "evToSalesTTM": 2.0,
                    }
                ],
                # BBB has no payload -> unresolved, must not raise.
            }
        )
        rows = [{"symbol": "AAA", "market_cap": 1_000_000_000}, {"symbol": "BBB"}]
        output, audit = PIPELINE.apply_quality_probe(
            client, rows, target_symbols=["AAA", "BBB"], source_id="fmp-key-metrics-ttm-2026-08-29"
        )
        by_symbol = {row["symbol"]: row for row in output}
        self.assertEqual(by_symbol["AAA"]["roic_pct"], 20.0)
        self.assertEqual(by_symbol["AAA"]["fcf_yield_pct"], 8.0)
        self.assertEqual(by_symbol["AAA"]["ev_to_fcf"], 12.5)
        self.assertEqual(by_symbol["AAA"]["net_debt_to_ebitda"], 1.5)
        self.assertEqual(by_symbol["AAA"]["sbc_revenue_pct"], 3.0)
        # (FCF - SBC) / mktcap = 8% - 3% * 600M / 1,000M = 8% - 1.8% = 6.2%
        self.assertAlmostEqual(by_symbol["AAA"]["sbc_adjusted_fcf_yield_pct"], 6.2, places=6)
        self.assertTrue(by_symbol["AAA"]["quality_probe_resolved"])
        self.assertFalse(by_symbol["BBB"]["quality_probe_resolved"])
        self.assertTrue(by_symbol["BBB"]["quality_probe_attempted"])
        self.assertEqual(audit["calls_used"], 2)
        self.assertEqual(sorted(audit["resolved"]), ["AAA"])

    def test_rows_outside_target_symbols_are_untouched(self) -> None:
        client = self.FakeClient({})
        rows = [{"symbol": "CCC"}]
        output, audit = PIPELINE.apply_quality_probe(
            client, rows, target_symbols=[], source_id="src"
        )
        self.assertFalse(output[0]["quality_probe_attempted"])
        self.assertEqual(audit["calls_used"], 0)
        self.assertEqual(client.calls, [])


class FcfPrefilterTests(unittest.TestCase):
    def _liquid_row(self, symbol: str, **overrides: Any) -> dict[str, Any]:
        row = {
            "symbol": symbol,
            "price": 20.0,
            "average_volume": 500_000.0,
            "average_daily_dollar_volume_method": "price_x_20d_average_volume",
            "average_volume_period_days": 20,
            "liquidity_source_ids": ["fmp-historical-eod-2026-08-29"],
            "forward_pe": 15.0,
            "eps_growth_pct": 15.0,
            "revenue_growth_pct": 12.0,
            "analyst_count": 5,
            "roic_pct": 12.0,
            "cyclicality_score": 2,
        }
        row.update(overrides)
        return row

    def test_low_fcf_yield_excludes_row_from_non_high_growth_lanes(self) -> None:
        row = self._liquid_row(
            "AEIS", fcf_yield_pct=0.5, quality_probe_resolved=True, net_debt_to_ebitda=1.0
        )
        pool, audit = POOL.build_pool(
            universe_rows=[row],
            lane_rows={
                "core_garp": [row],
                "high_growth_exception": [],
                "quality_near_miss": [],
                "cyclical_normalization": [],
            },
            analysis_as_of="2026-08-29T00:00:00+00:00",
            source_ids=["src"],
            per_lane=10,
            max_pool=10,
            minimum_pool=1,
            requested_min_market_cap=500_000_000,
            requested_max_market_cap=20_000_000_000,
            provider_exhausted=True,
        )
        self.assertNotIn("AEIS", {item["symbol"] for item in pool})
        self.assertIn("AEIS", audit["fcf_prefilter_excluded_symbols"])

    def test_low_fcf_yield_in_high_growth_lane_is_tagged_not_excluded(self) -> None:
        row = self._liquid_row(
            "GROW", fcf_yield_pct=0.5, quality_probe_resolved=True, net_debt_to_ebitda=1.0
        )
        pool, audit = POOL.build_pool(
            universe_rows=[row],
            lane_rows={
                "core_garp": [],
                "high_growth_exception": [row],
                "quality_near_miss": [],
                "cyclical_normalization": [],
            },
            analysis_as_of="2026-08-29T00:00:00+00:00",
            source_ids=["src"],
            per_lane=10,
            max_pool=10,
            minimum_pool=1,
            requested_min_market_cap=500_000_000,
            requested_max_market_cap=20_000_000_000,
            provider_exhausted=True,
        )
        by_symbol = {item["symbol"]: item for item in pool}
        self.assertIn("GROW", by_symbol)
        self.assertIn("weak_fcf_support", by_symbol["GROW"].get("provider_prefilter_flags", []))
        self.assertNotIn("GROW", audit["fcf_prefilter_excluded_symbols"])

    def test_unresolved_probe_does_not_trigger_exclusion(self) -> None:
        row = self._liquid_row("UNSET", fcf_yield_pct=0.1, quality_probe_resolved=False)
        pool, audit = POOL.build_pool(
            universe_rows=[row],
            lane_rows={
                "core_garp": [row],
                "high_growth_exception": [],
                "quality_near_miss": [],
                "cyclical_normalization": [],
            },
            analysis_as_of="2026-08-29T00:00:00+00:00",
            source_ids=["src"],
            per_lane=10,
            max_pool=10,
            minimum_pool=1,
            requested_min_market_cap=500_000_000,
            requested_max_market_cap=20_000_000_000,
            provider_exhausted=True,
        )
        self.assertIn("UNSET", {item["symbol"] for item in pool})
        self.assertEqual(audit["fcf_prefilter_excluded_symbols"], [])


class CyclicalityTests(unittest.TestCase):
    def test_gold_miner_scores_four(self) -> None:
        self.assertEqual(PIPELINE.classify_cyclicality("Basic Materials", "Gold"), 4)

    def test_mining_keywords_score_four(self) -> None:
        # "Coal" is intentionally excluded here: it already scores 5 via the
        # dry-bulk/steel/coal/iron-ore tier, checked before the score-4 tier.
        for industry in ("Copper", "Silver", "Uranium", "Other Precious Metals"):
            self.assertEqual(
                PIPELINE.classify_cyclicality("Basic Materials", industry), 4, industry
            )

    def test_coal_scores_five_via_higher_tier(self) -> None:
        self.assertEqual(PIPELINE.classify_cyclicality("Energy", "Coal"), 5)

    def test_semiconductor_equipment_scores_three(self) -> None:
        self.assertEqual(PIPELINE.classify_cyclicality("Technology", "Semiconductor Equipment"), 3)

    def test_aluminum_scores_three(self) -> None:
        self.assertEqual(PIPELINE.classify_cyclicality("Basic Materials", "Aluminum"), 3)


class LaneTroughRecoveryTests(unittest.TestCase):
    def test_trough_recovery_moves_row_out_of_core_garp_into_near_miss(self) -> None:
        config = PIPELINE.load_config(None)
        row = {
            "forward_pe": 15.0,
            "eps_growth_pct": 15.0,
            "revenue_growth_pct": 12.0,
            "cyclicality_score": 2,
            "growth_pattern": "trough_recovery",
        }
        lanes = PIPELINE.lane_memberships(row, config)
        self.assertNotIn("core_garp", lanes)
        self.assertIn("quality_near_miss", lanes)

    def test_missing_growth_pattern_is_treated_as_none(self) -> None:
        config = PIPELINE.load_config(None)
        row = {
            "forward_pe": 15.0,
            "eps_growth_pct": 15.0,
            "revenue_growth_pct": 12.0,
            "cyclicality_score": 2,
        }
        lanes = PIPELINE.lane_memberships(row, config)
        self.assertIn("core_garp", lanes)


class ForeignPrivateIssuerTests(unittest.TestCase):
    def test_non_us_country_flags_fpi(self) -> None:
        self.assertTrue(PIPELINE._is_foreign_private_issuer({"country": "GB"}))

    def test_us_country_is_not_fpi(self) -> None:
        self.assertFalse(PIPELINE._is_foreign_private_issuer({"country": "US"}))

    def test_isin_prefix_takes_precedence(self) -> None:
        self.assertTrue(
            PIPELINE._is_foreign_private_issuer({"isin": "GB0002634946", "country": "US"})
        )
        self.assertFalse(
            PIPELINE._is_foreign_private_issuer({"isin": "US0378331005", "country": "GB"})
        )


class ScopeFieldsTests(unittest.TestCase):
    def test_run_summary_carries_honest_scope_fields(self) -> None:
        from test_claude_code_pipeline import FakePipelineClient

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
            summary = result.summary
            for key in (
                "listing_enumeration_complete",
                "economic_screen_scope_complete",
                "listing_universe_count",
                "estimate_seed_count",
                "estimate_seed_coverage_pct",
                "valid_estimate_count",
                "valid_estimate_coverage_pct",
                "scope_complete_deprecated_note",
            ):
                self.assertIn(key, summary, key)
            self.assertTrue(summary["economic_screen_scope_complete"])
            self.assertEqual(summary["listing_enumeration_complete"], summary["scope_complete"])

            next_action = __import__("json").loads(
                (output / "NEXT_ACTION.json").read_text(encoding="utf-8")
            )
            for key in (
                "listing_enumeration_complete",
                "economic_screen_scope_complete",
                "listing_universe_count",
                "estimate_seed_count",
                "valid_estimate_count",
            ):
                self.assertIn(key, next_action, key)

            discovery_audit = __import__("json").loads(
                (output / "audit" / "provider-prefilter-audit.json").read_text(encoding="utf-8")
            )
            self.assertTrue(discovery_audit["listing_provider_exhausted"])
            self.assertTrue(discovery_audit["estimate_seed_exhausted"])
            self.assertIn("quality_probe", discovery_audit)
            self.assertEqual(discovery_audit["provider_exhausted_scope"], "estimate_seed")


if __name__ == "__main__":
    unittest.main()
