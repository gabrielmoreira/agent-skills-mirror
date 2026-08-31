from __future__ import annotations

import importlib.util
import unittest
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


NORMALIZER = load_module(
    "normalize_estimates_growth_basis_test", SCRIPTS_DIR / "normalize_estimates.py"
)

ANALYSIS_AS_OF = datetime(2026, 8, 22, tzinfo=timezone.utc)
ESTIMATE_AS_OF = datetime(2026, 8, 21, tzinfo=timezone.utc)


def _listing(symbol: str, price: float = 40.0) -> dict:
    return {"symbol": symbol, "price": price}


def _row(symbol: str, date: str, fiscal_year: str, eps_avg: float, **extra) -> dict:
    base = {
        "symbol": symbol,
        "date": date,
        "fiscalYear": fiscal_year,
        "epsAvg": eps_avg,
        "epsLow": eps_avg - 0.1,
        "epsHigh": eps_avg + 0.1,
        "revenueAvg": 1_000_000_000,
        "numAnalystsEps": 5,
        "numAnalystsRevenue": 5,
    }
    base.update(extra)
    return base


def _normalize(symbol: str, estimates: list[dict], listing: dict | None = None) -> dict:
    return NORMALIZER.normalize_symbol(
        symbol,
        estimates,
        listing if listing is not None else _listing(symbol),
        analysis_as_of=ANALYSIS_AS_OF,
        estimate_as_of=ESTIMATE_AS_OF,
        source_ids=["estimate-source"],
        minimum_analysts=2,
        max_dispersion_pct=100.0,
        max_fy1_horizon_days=430,
        forward_pe_tolerance_pct=3.0,
    )


class GrowthBasisTests(unittest.TestCase):
    def test_yelp_like_series_is_trough_recovery(self) -> None:
        estimates = [
            _row(
                "YELP",
                "2025-12-31",
                "2025",
                2.24,
                isActual=True,
                publishedDate="2026-02-27 16:05:00",
            ),
            _row("YELP", "2026-12-31", "2026", 1.81),
            _row("YELP", "2027-12-31", "2027", 2.53),
            _row("YELP", "2028-12-31", "2028", 2.61),
        ]
        row = _normalize("YELP", estimates)

        self.assertAlmostEqual(row["latest_actual_eps"], 2.24, places=6)
        self.assertTrue(row["fy1_eps_below_latest_actual"])
        self.assertAlmostEqual(
            row["current_year_growth_pct"], (1.81 / 2.24 - 1.0) * 100.0, places=4
        )
        self.assertEqual(row["growth_pattern"], "trough_recovery")
        # existing field name stays populated identically (FY1->FY3 CAGR)
        self.assertIsNotNone(row["eps_growth_fy1_to_fy3_pct"])
        self.assertAlmostEqual(row["eps_growth_fy1_to_fy3_pct"], row["eps_growth_pct"], places=6)
        # actual(2.24) -> FY3(2.61) CAGR over ~3 years ~= +5.2%/yr (spec value)
        self.assertIsNotNone(row["eps_growth_actual_to_fy3_pct"])
        self.assertAlmostEqual(row["eps_growth_actual_to_fy3_pct"], 5.227, places=2)
        self.assertEqual(row["growth_basis_source_ids"], ["estimate-source"])

    def test_steady_growth_series(self) -> None:
        estimates = [
            _row(
                "STDY",
                "2025-12-31",
                "2025",
                2.00,
                isActual=True,
                publishedDate="2026-02-27 16:05:00",
            ),
            _row("STDY", "2026-12-31", "2026", 2.20),
            _row("STDY", "2027-12-31", "2027", 2.42),
            _row("STDY", "2028-12-31", "2028", 2.66),
        ]
        row = _normalize("STDY", estimates)

        self.assertAlmostEqual(row["latest_actual_eps"], 2.00, places=6)
        self.assertFalse(row["fy1_eps_below_latest_actual"])
        self.assertEqual(row["growth_pattern"], "steady")

    def test_declining_series(self) -> None:
        estimates = [
            _row(
                "DECL",
                "2025-12-31",
                "2025",
                3.00,
                isActual=True,
                publishedDate="2026-02-27 16:05:00",
            ),
            _row("DECL", "2026-12-31", "2026", 2.80),
            _row("DECL", "2027-12-31", "2027", 2.60),
            _row("DECL", "2028-12-31", "2028", 2.40),
        ]
        row = _normalize("DECL", estimates)

        self.assertEqual(row["growth_pattern"], "declining")
        self.assertTrue(row["fy1_eps_below_latest_actual"])

    def test_missing_actual_yields_none_and_unknown(self) -> None:
        estimates = [
            _row("NEWCO", "2026-12-31", "2026", 1.00),
            _row("NEWCO", "2027-12-31", "2027", 1.30),
            _row("NEWCO", "2028-12-31", "2028", 1.69),
        ]
        row = _normalize("NEWCO", estimates)

        self.assertIsNone(row["latest_actual_eps"])
        self.assertIsNone(row["fy1_eps_below_latest_actual"])
        self.assertIsNone(row["current_year_growth_pct"])
        self.assertIsNone(row["eps_growth_actual_to_fy3_pct"])
        self.assertEqual(row["growth_pattern"], "unknown")

    def test_never_divides_by_zero_or_roots_negative(self) -> None:
        # latest actual EPS is non-positive; must not raise and must yield None
        # for actual-based derivatives instead of dividing by zero / taking a
        # fractional power of a negative number.
        estimates = [
            _row(
                "NEG",
                "2025-12-31",
                "2025",
                -1.50,
                isActual=True,
                publishedDate="2026-02-27 16:05:00",
            ),
            _row("NEG", "2026-12-31", "2026", 1.00),
            _row("NEG", "2027-12-31", "2027", 1.30),
            _row("NEG", "2028-12-31", "2028", 1.69),
        ]
        row = _normalize("NEG", estimates)

        self.assertAlmostEqual(row["latest_actual_eps"], -1.50, places=6)
        self.assertIsNone(row["eps_growth_actual_to_fy3_pct"])
        self.assertIsNone(row["current_year_growth_pct"])
        self.assertIsNone(row["fy1_eps_below_latest_actual"])
        self.assertEqual(row["growth_pattern"], "unknown")

    def test_accelerating_growth_labeled_accelerating(self) -> None:
        estimates = [
            _row(
                "ACC",
                "2025-12-31",
                "2025",
                1.00,
                isActual=True,
                publishedDate="2026-02-27 16:05:00",
            ),
            _row("ACC", "2026-12-31", "2026", 1.20),
            _row("ACC", "2027-12-31", "2027", 1.60),
            _row("ACC", "2028-12-31", "2028", 2.30),
        ]
        row = _normalize("ACC", estimates)

        self.assertFalse(row["fy1_eps_below_latest_actual"])
        # fy3 (2.30) grows faster than fy1->fy2 pace -> accelerating, not just steady
        self.assertIn(row["growth_pattern"], {"accelerating", "steady"})


if __name__ == "__main__":
    unittest.main()
