"""Round-4 review P0s: pool-floor waiver scope; sector-profile inference and routing."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import build_provider_prefilter_pool as POOL  # noqa: E402
import run_pipeline as PIPELINE  # noqa: E402
import screen_universe as SCREEN  # noqa: E402

ASSETS_DIR = SCRIPTS_DIR.parent / "assets"


def _lane_row(symbol: str, addv: float = 20_000_000.0) -> dict:
    return {
        "symbol": symbol,
        "sector": "Technology",
        "market_cap": 2_000_000_000,
        "price": 20.0,
        "forward_pe": 15.0,
        "eps_growth_pct": 15.0,
        "revenue_growth_pct": 10.0,
        "analyst_count": 5,
        "cyclicality_score": 2,
        "average_daily_dollar_volume": addv,
        "average_daily_dollar_volume_method": "provider_average_dollar_volume",
        "average_volume_period_days": 20,
        "liquidity_source_ids": ["liq-src"],
    }


def _build(minimum_pool: int, scope: str | None, count: int = 3):
    rows = [_lane_row(f"SY{i}") for i in range(count)]
    return POOL.build_pool(
        universe_rows=rows,
        lane_rows={"core_garp": rows, "high_growth_exception": rows, "quality_near_miss": rows},
        analysis_as_of="2026-08-30T18:00:00+00:00",
        source_ids=["estimate-source"],
        per_lane=8,
        max_pool=30,
        minimum_pool=minimum_pool,
        requested_min_market_cap=500_000_000,
        requested_max_market_cap=20_000_000_000,
        provider_exhausted=True,
        provider_exhausted_scope=scope,
    )


class PoolFloorScopeTests(unittest.TestCase):
    def test_estimate_seed_exhaustion_does_not_waive_the_floor(self) -> None:
        # The round-4 reviewer's reproduction: 30-row pool, floor 100,
        # scope=estimate_seed used to come back valid.
        _, audit = _build(minimum_pool=100, scope="estimate_seed")
        self.assertFalse(audit["pool_adequate"])
        self.assertFalse(audit["valid"])
        self.assertFalse(audit["pool_floor_waived"])

    def test_full_universe_exhaustion_still_waives_the_floor(self) -> None:
        _, audit = _build(minimum_pool=100, scope="economic_candidate_universe")
        self.assertTrue(audit["pool_adequate"])
        self.assertTrue(audit["pool_floor_waived"])

    def test_missing_scope_fails_closed(self) -> None:
        # Round-5 hardening: an unstated exhaustion scope proves nothing, so
        # it no longer earns the legacy full waiver.
        _, audit = _build(minimum_pool=100, scope=None)
        self.assertFalse(audit["pool_adequate"])
        self.assertFalse(audit["pool_floor_waived"])

    def test_floor_met_needs_no_waiver(self) -> None:
        _, audit = _build(minimum_pool=2, scope="estimate_seed")
        self.assertTrue(audit["pool_adequate"])
        self.assertFalse(audit["pool_floor_waived"])


class SectorProfileInferenceTests(unittest.TestCase):
    CASES = [
        ("Real Estate", "REIT - Mortgage", "reit"),
        ("Real Estate", "REIT - Diversified", "reit"),
        ("Financial Services", "Insurance - Property & Casualty", "insurance"),
        ("Financial Services", "Banks - Regional", "bank"),
        ("Financial Services", "Asset Management", "asset_manager"),
        ("Financial Services", "Business Development Company", "bdc"),
        ("Energy", "Oil & Gas MLP", "mlp"),
        ("Consumer Cyclical", "Auto & Truck Dealerships", "auto_dealership"),
        ("Consumer Cyclical", "Auto - Dealerships", "auto_dealership"),
        ("Financial Services", "Investment - Banking & Investment Services", "capital_markets"),
        ("Financial Services", "Banks - Diversified", "bank"),
        ("Technology", "Software - Application", "general"),
        (None, None, "general"),
    ]

    def test_inference_matches_screen_universe_profiles(self) -> None:
        for sector, industry, expected in self.CASES:
            with self.subTest(sector=sector, industry=industry):
                self.assertEqual(PIPELINE.infer_sector_profile_type(sector, industry), expected)
        # every BLOCKED profile we emit must be one screen_universe gates on;
        # capital_markets and auto_dealership have their own handling.
        emitted = (
            set(PIPELINE.INDUSTRY_PROFILE_MAP.values())
            | {profile for _, profile in PIPELINE._INDUSTRY_PREFIX_RULES}
            | {"bdc", "mlp", "reit"}
        )
        self.assertTrue(
            emitted <= (SCREEN.SECTOR_PROFILES | {"auto_dealership", "capital_markets"})
        )

    def test_normalize_listing_carries_the_profile(self) -> None:
        row = {
            "symbol": "ABR",
            "companyName": "Arbor Realty Trust",
            "price": 5.06,
            "marketCap": 970_000_000,
            "sector": "Real Estate",
            "industry": "REIT - Mortgage",
        }
        out = PIPELINE.normalize_listing(row, "NYSE")
        self.assertEqual(out["sector_profile_type"], "reit")

    def test_reit_without_sector_metrics_routes_to_sector_review(self) -> None:
        # A mortgage REIT must hit sector_specific_valuation_required, not the
        # general-company leverage gate (ABR: net debt/EBITDA 13x was excluded
        # as excessive_leverage while typed "general").
        base = json.loads(
            (ASSETS_DIR / "enriched-candidate-pool.example.jsonl").read_text().splitlines()[0]
        )
        config = json.loads((ASSETS_DIR / "screening-config.example.json").read_text())
        base["sector_profile_type"] = "reit"
        base["net_debt_to_ebitda"] = 13.2
        decision = SCREEN._candidate_decision(
            base, config, "liquidity_stratified_estimates", "2026-08-22T14:00:00-07:00"
        )
        d = decision["decision"]
        reasons = (
            list(d.get("blocking_review_reasons") or [])
            + list(d.get("review_reasons") or [])
            + list(d.get("hard_reasons") or [])
            + list(d.get("screen_fail_reasons") or [])
        )
        self.assertIn("sector_specific_valuation_required", reasons)
        self.assertNotIn("excessive_leverage", d.get("hard_reasons") or [])
        self.assertNotIn("excessive_leverage", d.get("screen_fail_reasons") or [])


class SectorExhaustionTests(unittest.TestCase):
    def test_reit_without_sector_metrics_is_declared_exhausted(self) -> None:
        rows = [
            {"symbol": "ABR", "sector_profile_type": "reit"},
            {"symbol": "GEN", "sector_profile_type": "general"},
            {"symbol": "AFO", "sector_profile_type": "reit", "p_to_affo": 9.5},
            {"symbol": "HLI", "sector_profile_type": "capital_markets"},
        ]
        out = PIPELINE.mark_sector_profile_exhaustion(rows, source_id="fmp-key-metrics-ttm-x")
        by = {r["symbol"]: r for r in out}
        self.assertTrue(by["ABR"]["enrichment_exhausted"])
        self.assertIn("reit", by["ABR"]["enrichment_exhaustion_reason"])
        self.assertEqual(by["ABR"]["enrichment_source_ids"], ["fmp-key-metrics-ttm-x"])
        self.assertNotIn("enrichment_exhausted", by["GEN"])
        self.assertNotIn("enrichment_exhausted", by["AFO"])  # has a sector metric
        # Round-8 review: capital_markets is valued on ordinary multiples —
        # it must never be declared sector-enrichment exhausted.
        self.assertNotIn("enrichment_exhausted", by["HLI"])

    def test_exhausted_reit_resolves_as_unavailable_after_enrichment(self) -> None:
        base = json.loads(
            (ASSETS_DIR / "enriched-candidate-pool.example.jsonl").read_text().splitlines()[0]
        )
        config = json.loads((ASSETS_DIR / "screening-config.example.json").read_text())
        base["sector_profile_type"] = "reit"
        base["net_debt_to_ebitda"] = 13.2
        [marked] = PIPELINE.mark_sector_profile_exhaustion(
            [base], source_id="fmp-key-metrics-ttm-x"
        )
        decision = SCREEN._candidate_decision(
            marked, config, "liquidity_stratified_estimates", "2026-08-22T14:00:00-07:00"
        )
        d = decision["decision"]
        self.assertEqual(d.get("status"), "unavailable_after_enrichment")
        self.assertEqual(d.get("resolution"), "resolved")
        self.assertIn("sector_specific_valuation_required", d.get("blocking_review_reasons") or [])


if __name__ == "__main__":
    unittest.main()
