"""Round-5 review P0s: FPI unit reconciliation, unit-anomaly gates, ET filing clock."""

from __future__ import annotations

import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import normalize_estimates as NORM  # noqa: E402
import run_pipeline as PIPELINE  # noqa: E402
import screen_universe as SCREEN  # noqa: E402

ASSETS_DIR = SCRIPTS_DIR.parent / "assets"
AS_OF_TEXT = "2026-08-22T14:00:00-07:00"


def _base_row() -> dict:
    return json.loads(
        (ASSETS_DIR / "enriched-candidate-pool.example.jsonl").read_text().splitlines()[0]
    )


def _config() -> dict:
    return json.loads((ASSETS_DIR / "screening-config.example.json").read_text())


def _decide(row: dict) -> dict:
    return SCREEN._candidate_decision(row, _config(), "liquidity_stratified_estimates", AS_OF_TEXT)[
        "decision"
    ]


class UnitReconciliationGateTests(unittest.TestCase):
    def test_foreign_issuer_without_verification_is_blocked(self) -> None:
        row = _base_row()
        row["country"] = "CN"
        d = _decide(row)
        self.assertIn("unit_reconciliation_required", d.get("blocking_review_reasons") or [])
        self.assertFalse(d.get("selection_eligible"))

    def test_verified_foreign_issuer_passes_the_gate(self) -> None:
        row = _base_row()
        row["country"] = "CN"
        row["unit_reconciliation_verified"] = True
        d = _decide(row)
        self.assertNotIn("unit_reconciliation_required", d.get("blocking_review_reasons") or [])

    def test_qfin_like_ratios_are_unit_mismatch_not_deep_value(self) -> None:
        # QFIN as shipped: $8.80 ADS price against CNY-denominated EPS/FCF.
        row = _base_row()
        row["country"] = "CN"
        row["price"] = 8.80
        row["fcf_yield_pct"] = 93.72
        row["latest_actual_eps"] = 85.58
        d = _decide(row)
        self.assertIn("unit_mismatch_suspected", d.get("screen_fail_reasons") or [])
        self.assertFalse(d.get("selection_eligible"))

    def test_domestic_eps_above_twice_price_is_stopped(self) -> None:
        row = _base_row()
        row["latest_actual_eps"] = float(row.get("price") or 20.0) * 3.0
        d = _decide(row)
        self.assertIn("unit_mismatch_suspected", d.get("screen_fail_reasons") or [])
        self.assertFalse(d.get("selection_eligible"))

    def test_domestic_implausible_fcf_yield_is_stopped(self) -> None:
        row = _base_row()
        row["fcf_yield_pct"] = 61.0
        d = _decide(row)
        self.assertIn("unit_mismatch_suspected", d.get("screen_fail_reasons") or [])
        self.assertFalse(d.get("selection_eligible"))

    def test_unverified_foreign_issuer_resolves_after_exhaustion(self) -> None:
        row = _base_row()
        row["country"] = "CN"
        [marked] = PIPELINE.mark_unit_reconciliation_exhaustion([row], source_id="fmp-probe-x")
        self.assertTrue(marked["enrichment_exhausted"])
        self.assertIn("ADS-unit", marked["enrichment_exhaustion_reason"])
        d = _decide(marked)
        self.assertEqual(d.get("status"), "unavailable_after_enrichment")
        self.assertFalse(d.get("selection_eligible"))

    def test_exhaustion_marker_leaves_domestic_and_verified_rows_alone(self) -> None:
        rows = [
            {"symbol": "USA", "country": "US"},
            {"symbol": "OKF", "country": "CN", "unit_reconciliation_verified": True},
        ]
        out = PIPELINE.mark_unit_reconciliation_exhaustion(rows, source_id="src")
        for row in out:
            self.assertNotIn("enrichment_exhausted", row)


class UnitContextFailClosedTests(unittest.TestCase):
    """Round-8 review: an UNKNOWN unit context is unreconciled, never domestic."""

    def test_missing_country_with_cny_currency_is_blocked(self) -> None:
        row = _base_row()
        row["country"] = None
        row["currency"] = "CNY"
        d = _decide(row)
        self.assertIn("unit_reconciliation_required", d.get("blocking_review_reasons") or [])
        self.assertFalse(d.get("selection_eligible"))

    def test_missing_country_with_foreign_isin_is_blocked(self) -> None:
        row = _base_row()
        row["country"] = None
        row["currency"] = None
        row["isin"] = "KYG123456789"
        d = _decide(row)
        self.assertIn("unit_reconciliation_required", d.get("blocking_review_reasons") or [])
        self.assertFalse(d.get("selection_eligible"))

    def test_adr_flag_is_blocked_even_with_us_country(self) -> None:
        row = _base_row()
        row["country"] = "US"
        row["is_adr"] = True
        d = _decide(row)
        self.assertIn("unit_reconciliation_required", d.get("blocking_review_reasons") or [])

    def test_proven_domestic_row_passes_the_gate(self) -> None:
        row = _base_row()
        row["country"] = "US"
        row["currency"] = "USD"
        row["isin"] = "US1564311082"
        d = _decide(row)
        self.assertNotIn("unit_reconciliation_required", d.get("blocking_review_reasons") or [])

    def test_requires_unit_reconciliation_unit_cases(self) -> None:
        req = SCREEN.requires_unit_reconciliation
        self.assertTrue(req({}))  # nothing proven -> fail closed
        self.assertTrue(req({"country": "US", "currency": "CNY"}))
        self.assertTrue(req({"country": "US", "isin": "KYG8464W1069"}))
        self.assertTrue(req({"country": "US", "is_adr": True}))
        self.assertFalse(req({"country": "US"}))
        self.assertFalse(req({"country": "US", "currency": "USD", "isin": "US1564311082"}))
        self.assertFalse(req({"country": "CN", "unit_reconciliation_verified": True}))

    def test_normalize_listing_keeps_unit_identity_signals(self) -> None:
        out = PIPELINE.normalize_listing(
            {
                "symbol": "QFIN",
                "companyName": "Qifu Technology",
                "price": 8.8,
                "marketCap": 1_200_000_000,
                "country": "CN",
                "currency": "CNY",
                "isin": "KYG8464W1069",
                "isAdr": True,
            },
            "NASDAQ",
        )
        self.assertEqual(out["isin"], "KYG8464W1069")
        self.assertTrue(out["is_adr"])
        self.assertTrue(SCREEN.requires_unit_reconciliation(out))


class AcceptedDateTimezoneTests(unittest.TestCase):
    def _statements(self, accepted: str) -> list[dict]:
        return [{"period": "FY", "date": "2025-12-31", "acceptedDate": accepted, "epsDiluted": 2.0}]

    def test_summer_acceptance_is_eastern_not_utc(self) -> None:
        # 17:23:10 ET (EDT) == 21:23:10 UTC. At 16:00 ET (20:00 UTC) the
        # filing is NOT yet public; the old UTC reading leaked it 4h early.
        statements = self._statements("2026-04-03 17:23:10")
        before = datetime(2026, 4, 3, 20, 0, tzinfo=timezone.utc)
        after = datetime(2026, 4, 3, 21, 30, tzinfo=timezone.utc)
        self.assertEqual(
            PIPELINE._verified_annual_actual(statements, analysis_as_of=before), (None, None)
        )
        self.assertEqual(
            PIPELINE._verified_annual_actual(statements, analysis_as_of=after),
            (2.0, "2025-12-31"),
        )

    def test_winter_acceptance_uses_est_offset(self) -> None:
        # 17:00 ET (EST) == 22:00 UTC.
        statements = self._statements("2026-01-15 17:00:00")
        before = datetime(2026, 1, 15, 21, 30, tzinfo=timezone.utc)
        after = datetime(2026, 1, 15, 22, 30, tzinfo=timezone.utc)
        self.assertEqual(
            PIPELINE._verified_annual_actual(statements, analysis_as_of=before), (None, None)
        )
        self.assertEqual(
            PIPELINE._verified_annual_actual(statements, analysis_as_of=after),
            (2.0, "2025-12-31"),
        )


class PublishedBeforeTimezoneTests(unittest.TestCase):
    def _record(self, published: str) -> dict:
        return {
            "is_actual": True,
            "period_end": "2026-03-31T00:00:00+00:00",
            "published_at": published,
            "eps_avg": 1.0,
        }

    def test_naive_publish_stamp_is_eastern(self) -> None:
        rec = self._record("2026-04-03 17:23:10")
        early = datetime(2026, 4, 3, 20, 0, tzinfo=timezone.utc)  # 16:00 ET
        late = datetime(2026, 4, 3, 22, 0, tzinfo=timezone.utc)
        self.assertIsNone(NORM._latest_actual_period([rec], early))
        self.assertIsNotNone(NORM._latest_actual_period([rec], late))

    def test_date_only_publish_stamp_counts_after_the_whole_day(self) -> None:
        rec = self._record("2026-04-03")
        same_day = datetime(2026, 4, 3, 12, 0, tzinfo=timezone.utc)
        next_day = datetime(2026, 4, 4, 6, 0, tzinfo=timezone.utc)  # past 23:59:59 EDT
        self.assertIsNone(NORM._latest_actual_period([rec], same_day))
        self.assertIsNotNone(NORM._latest_actual_period([rec], next_day))


class TaxonomyRound5Tests(unittest.TestCase):
    def test_fmp_auto_dealership_label_is_mapped(self) -> None:
        # 14 dealers (ABG, AN, KMX, LAD, PAG, ...) sat in "general" because the
        # old needle never matched FMP's actual "Auto - Dealerships" label.
        self.assertEqual(
            PIPELINE.infer_sector_profile_type("Consumer Cyclical", "Auto - Dealerships"),
            "auto_dealership",
        )

    def test_investment_banks_are_not_deposit_banks(self) -> None:
        profile = PIPELINE.infer_sector_profile_type(
            "Financial Services", "Investment - Banking & Investment Services"
        )
        self.assertEqual(profile, "capital_markets")
        # advisory firms are valued on ordinary earnings multiples: never
        # routed to the deposit-bank (P/TBV, NIM) blocking gate.
        self.assertNotIn("capital_markets", SCREEN.SECTOR_PROFILES)

    def test_bdc_detected_from_company_name_within_asset_management(self) -> None:
        self.assertEqual(
            PIPELINE.infer_sector_profile_type(
                "Financial Services", "Asset Management", "Golub Capital BDC, Inc."
            ),
            "bdc",
        )
        self.assertEqual(
            PIPELINE.infer_sector_profile_type(
                "Financial Services", "Asset Management", "Prospect Business Development"
            ),
            "bdc",
        )

    def test_override_config_key_exists_for_unmarked_bdcs(self) -> None:
        self.assertIn("sector_profile_overrides", PIPELINE.DEFAULT_CONFIG)


if __name__ == "__main__":
    unittest.main()
