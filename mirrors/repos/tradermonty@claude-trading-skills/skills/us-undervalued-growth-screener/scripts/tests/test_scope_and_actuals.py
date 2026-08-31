"""P0 regressions from the v3.6.1 review: economic scope completeness and verified actual EPS."""

from __future__ import annotations

import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


import normalize_estimates as NORMALIZER  # noqa: E402
import run_pipeline as PIPELINE  # noqa: E402

AS_OF = datetime(2026, 8, 22, tzinfo=timezone.utc)


class EconomicScopeTests(unittest.TestCase):
    def _complete(self, mode: str, covered: int, universe: int) -> bool:
        return PIPELINE.economic_scope_complete(
            estimate_acquisition_mode=mode,
            covered_symbol_count=covered,
            universe_symbol_count=universe,
        )

    def test_99pct_coverage_is_not_complete(self) -> None:
        self.assertFalse(self._complete("analyst_estimates_bulk", 99, 100))

    def test_9999_of_10000_is_not_complete(self) -> None:
        self.assertFalse(self._complete("analyst_estimates_bulk", 9999, 10000))

    def test_exact_full_coverage_is_complete(self) -> None:
        self.assertTrue(self._complete("analyst_estimates_bulk", 2371, 2371))

    def test_per_symbol_fallback_is_never_complete(self) -> None:
        self.assertFalse(self._complete("bounded_per_symbol_fallback", 2371, 2371))

    def test_empty_universe_is_not_complete(self) -> None:
        self.assertFalse(self._complete("analyst_estimates_bulk", 0, 0))

    def test_completeness_is_not_configurable(self) -> None:
        # No ratio knob: the function takes no config, and the old key is gone
        # from DEFAULT_CONFIG, so a user cannot lower the bar back to 20%.
        import inspect

        params = inspect.signature(PIPELINE.economic_scope_complete).parameters
        self.assertNotIn("config", params)
        self.assertNotIn("bulk_coverage_pct", params)
        self.assertNotIn("economic_scope_complete_minimum_coverage_pct", PIPELINE.DEFAULT_CONFIG)


def _row(date: str, fiscal_year: str, eps: float, **extra) -> dict:
    base = {
        "symbol": "T",
        "date": date,
        "fiscalYear": fiscal_year,
        "epsAvg": eps,
        "epsLow": eps - 0.1,
        "epsHigh": eps + 0.1,
        "revenueAvg": 1_000_000_000,
        "numAnalystsEps": 5,
        "numAnalystsRevenue": 5,
    }
    base.update(extra)
    return base


def _normalize(rows):
    return NORMALIZER.normalize_symbol(
        "T",
        rows,
        {"symbol": "T", "price": 40.0},
        analysis_as_of=AS_OF,
        estimate_as_of=datetime(2026, 8, 21, tzinfo=timezone.utc),
        source_ids=["estimate-source"],
        minimum_analysts=2,
        max_dispersion_pct=100.0,
        max_fy1_horizon_days=430,
        forward_pe_tolerance_pct=3.0,
    )


class VerifiedActualTests(unittest.TestCase):
    SERIES = [
        _row("2025-12-31", "2025", 2.0),  # unmarked prior-year consensus row
        _row("2026-12-31", "2026", 1.8),
        _row("2027-12-31", "2027", 2.5),
        _row("2028-12-31", "2028", 2.6),
    ]

    def test_unmarked_prior_year_estimate_is_not_an_actual(self) -> None:
        out = _normalize(self.SERIES)
        self.assertIsNone(out["latest_actual_eps"])
        self.assertIsNone(out["fy1_eps_below_latest_actual"])
        # ...but it IS the same-basis consensus reference for the growth pattern
        self.assertEqual(out["fy0_consensus_eps"], 2.0)
        self.assertTrue(out["fy1_eps_below_fy0_consensus"])
        self.assertEqual(out["growth_pattern"], "trough_recovery")
        self.assertEqual(out["growth_pattern_basis"], "consensus_same_basis")

    def test_no_prior_year_row_means_unknown_pattern(self) -> None:
        out = _normalize(self.SERIES[1:])
        self.assertIsNone(out["fy0_consensus_eps"])
        self.assertEqual(out["growth_pattern"], "unknown")
        self.assertEqual(out["growth_pattern_basis"], "unknown")

    def test_marked_actual_after_analysis_as_of_is_ignored(self) -> None:
        rows = list(self.SERIES) + [_row("2027-12-31", "2027", 9.0, isActual=True)]
        out = _normalize(rows)
        self.assertIsNone(out["latest_actual_eps"])
        self.assertEqual(out["fy0_consensus_eps"], 2.0)  # look-ahead row never becomes FY0

    def test_marked_actual_with_publication_timestamp_is_used(self) -> None:
        rows = [
            _row("2025-12-31", "2025", 2.24, isActual=True, publishedDate="2026-02-27 16:05:00")
        ] + self.SERIES[1:]
        out = _normalize(rows)
        self.assertEqual(out["latest_actual_eps"], 2.24)
        self.assertTrue(out["latest_actual_verified"])
        self.assertEqual(out["latest_actual_basis"], "provider_marked_actual")
        self.assertEqual(out["latest_actual_source_ids"], ["estimate-source"])
        self.assertEqual(out["growth_pattern"], "trough_recovery")

    def test_marked_actual_without_publication_timestamp_is_rejected(self) -> None:
        rows = [_row("2025-12-31", "2025", 2.24, isActual=True)] + self.SERIES[1:]
        out = _normalize(rows)
        self.assertIsNone(out["latest_actual_eps"])
        self.assertFalse(out["latest_actual_verified"])
        self.assertIsNone(out["latest_actual_basis"])
        self.assertEqual(out["latest_actual_source_ids"], [])

    def test_historical_as_of_between_period_end_and_publication(self) -> None:
        # Period ended 2025-12-31, published 2026-02-27, but we are replaying
        # as of 2026-01-05: the actual was NOT public yet -> no actual fields.
        rows = [
            _row("2025-12-31", "2025", 2.24, isActual=True, publishedDate="2026-02-27 16:05:00"),
            _row("2026-12-31", "2026", 1.8),
            _row("2027-12-31", "2027", 2.5),
            _row("2028-12-31", "2028", 2.6),
        ]
        out = NORMALIZER.normalize_symbol(
            "T",
            rows,
            {"symbol": "T", "price": 40.0},
            analysis_as_of=datetime(2026, 1, 5, tzinfo=timezone.utc),
            estimate_as_of=datetime(2026, 1, 4, tzinfo=timezone.utc),
            source_ids=["estimate-source"],
            minimum_analysts=2,
            max_dispersion_pct=100.0,
            max_fy1_horizon_days=430,
            forward_pe_tolerance_pct=3.0,
        )
        self.assertIsNone(out["latest_actual_eps"])
        self.assertFalse(out["latest_actual_verified"])

    def test_apply_verified_actual_eps_rederives_growth_basis(self) -> None:
        base = _normalize(self.SERIES)
        out = NORMALIZER.apply_verified_actual_eps(
            base,
            actual_eps=2.24,
            period_end="2025-12-31",
            analysis_as_of=AS_OF,
            source_ids=["fmp-income-statement-annual-2026-08-22"],
        )
        self.assertTrue(out["latest_actual_verified"])
        self.assertEqual(out["latest_actual_eps"], 2.24)
        self.assertEqual(out["latest_actual_basis"], "gaap_diluted")
        self.assertTrue(out["fy1_eps_below_latest_actual"])
        self.assertAlmostEqual(
            out["current_year_growth_pct_vs_gaap_actual"], (1.8 / 2.24 - 1) * 100, places=4
        )
        # consensus FY0 2.0 vs GAAP 2.24 -> 10.7% gap: same basis, no flag
        self.assertFalse(out["estimate_basis_likely_adjusted"])
        self.assertEqual(out["growth_pattern"], "trough_recovery")  # unchanged, consensus basis
        self.assertEqual(
            out["latest_actual_source_ids"], ["fmp-income-statement-annual-2026-08-22"]
        )

    def test_apply_verified_actual_eps_fails_closed_on_future_or_missing(self) -> None:
        base = _normalize(self.SERIES)
        future = NORMALIZER.apply_verified_actual_eps(
            base, actual_eps=2.24, period_end="2027-12-31", analysis_as_of=AS_OF, source_ids=["x"]
        )
        self.assertFalse(future["latest_actual_verified"])
        self.assertIsNone(future["latest_actual_eps"])
        missing = NORMALIZER.apply_verified_actual_eps(
            base, actual_eps=None, period_end=None, analysis_as_of=AS_OF, source_ids=[]
        )
        self.assertIsNone(missing["latest_actual_eps"])
        # consensus-basis pattern is untouched by a missing/invalid actual
        self.assertEqual(missing["growth_pattern"], base["growth_pattern"])

    def test_gaap_actual_far_below_consensus_flags_basis_mismatch(self) -> None:
        # DOCS-like: consensus FY0 1.52 (non-GAAP), GAAP actual 0.98, FY1 1.35
        rows = [
            _row("2026-03-31", "2026", 1.52),
            _row("2027-03-31", "2027", 1.35),
            _row("2028-03-31", "2028", 1.55),
            _row("2029-03-31", "2029", 1.75),
        ]
        base = _normalize(rows)
        self.assertTrue(base["fy1_eps_below_fy0_consensus"])
        self.assertEqual(base["growth_pattern"], "trough_recovery")
        out = NORMALIZER.apply_verified_actual_eps(
            base, actual_eps=0.98, period_end="2026-03-31", analysis_as_of=AS_OF, source_ids=["is"]
        )
        self.assertTrue(out["estimate_basis_likely_adjusted"])
        self.assertFalse(out["fy1_eps_below_latest_actual"])  # 1.35 > 0.98 on mixed bases
        self.assertEqual(out["growth_pattern"], "trough_recovery")  # same-basis verdict kept


class VerifiedAnnualActualParsingTests(unittest.TestCase):
    def test_rejects_filings_accepted_after_analysis_as_of(self) -> None:
        statements = [
            {
                "period": "FY",
                "date": "2025-12-31",
                "acceptedDate": "2026-02-27 16:05:00",
                "epsDiluted": 2.24,
            },
            {
                "period": "FY",
                "date": "2026-12-31",
                "acceptedDate": "2027-02-25 16:05:00",
                "epsDiluted": 9.0,
            },
            {
                "period": "Q2",
                "date": "2026-06-30",
                "acceptedDate": "2026-08-07 16:05:00",
                "epsDiluted": 0.57,
            },
        ]
        eps, end = PIPELINE._verified_annual_actual(statements, analysis_as_of=AS_OF)
        self.assertEqual((eps, end), (2.24, "2025-12-31"))

    def test_filing_date_fallback_is_gone_and_date_only_rejected(self) -> None:
        date_only = [
            {"period": "FY", "date": "2025-12-31", "acceptedDate": "2026-02-27", "epsDiluted": 2.24}
        ]
        self.assertEqual(
            PIPELINE._verified_annual_actual(date_only, analysis_as_of=AS_OF), (None, None)
        )
        filing_only = [
            {"period": "FY", "date": "2025-12-31", "filingDate": "2026-02-27", "epsDiluted": 2.24}
        ]
        self.assertEqual(
            PIPELINE._verified_annual_actual(filing_only, analysis_as_of=AS_OF), (None, None)
        )

    def test_period_ended_but_not_yet_filed_is_rejected(self) -> None:
        statements = [
            {
                "period": "FY",
                "date": "2026-06-30",
                "acceptedDate": "2026-08-30 16:05:00",
                "epsDiluted": 3.0,
            }
        ]
        eps, end = PIPELINE._verified_annual_actual(statements, analysis_as_of=AS_OF)
        self.assertEqual((eps, end), (None, None))

    def test_probe_wires_actual_eps_and_counts_calls(self) -> None:
        class Client:
            def __init__(self):
                self.calls = []

            def get_key_metrics_ttm(self, symbol):
                self.calls.append(("km", symbol))
                return [{"freeCashFlowYieldTTM": 0.05}]

            def get_income_statement(self, symbol, *, period="annual", limit=6):
                self.calls.append(("is", symbol))
                return [
                    {
                        "period": "FY",
                        "date": "2025-12-31",
                        "acceptedDate": "2026-02-27 16:05:00",
                        "epsDiluted": 2.24,
                    }
                ]

        client = Client()
        rows = [_normalize(VerifiedActualTests.SERIES)]
        out, audit = PIPELINE.apply_quality_probe(
            client,
            rows,
            target_symbols=["T"],
            source_id="fmp-key-metrics-ttm-2026-08-22",
            analysis_as_of=AS_OF,
            actual_source_id="fmp-income-statement-annual-2026-08-22",
        )
        self.assertEqual(out[0]["latest_actual_eps"], 2.24)
        self.assertEqual(out[0]["growth_pattern"], "trough_recovery")
        self.assertEqual(audit["actual_eps_resolved"], ["T"])
        self.assertEqual(audit["calls_used"], 2)


if __name__ == "__main__":
    unittest.main()
