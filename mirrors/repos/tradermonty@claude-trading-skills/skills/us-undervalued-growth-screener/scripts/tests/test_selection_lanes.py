"""v3.6.1 selection-lane behaviour in screen_universe."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

_spec = importlib.util.spec_from_file_location(
    "screen_universe", SCRIPTS_DIR / "screen_universe.py"
)
SCREEN = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(SCREEN)


def _row(symbol, lane, priority, sector, *, growth_pattern=None):
    pre = {
        "core": "passed",
        "growth": "passed_exception",
        "near": "near_miss_review",
        "cycle": "passed",
    }[lane]
    cyclicality = 4 if lane == "cycle" else 1
    requirements = ["mid_cycle_normalization_required"] if lane == "cycle" else []
    metrics = {"analyst_count": 5, "cyclicality_score": cyclicality}
    if growth_pattern:
        metrics["growth_pattern"] = growth_pattern
    return {
        "symbol": symbol,
        "sector": sector,
        "deep_dive_priority_score": priority,
        "broad_score": priority,
        "fundamental_completeness_count": 8,
        "metrics": metrics,
        "decision": {
            "preselection_status": pre,
            "status": pre,
            "exception_admitted": lane == "growth",
            "deep_dive_requirements": requirements,
        },
    }


PLAN = {
    "selection_lane_quota_core_garp": 2,
    "selection_lane_quota_high_growth": 1,
    "selection_lane_quota_near_miss": 1,
    "selection_lane_quota_cyclical": 1,
    "maximum_selected_per_sector": 2,
}


class SelectionLaneTests(unittest.TestCase):
    def test_trough_recovery_is_never_core_garp(self) -> None:
        row = _row("YELP", "core", 90, "Communication", growth_pattern="trough_recovery")
        self.assertEqual(SCREEN._selection_lane(row), "quality_near_miss")
        steady = _row("STDY", "core", 90, "Communication", growth_pattern="steady")
        self.assertEqual(SCREEN._selection_lane(steady), "core_garp")

    def test_small_budget_ranks_by_priority_with_lane_caps(self) -> None:
        # Three top-priority cyclicals, then a core name, then near-miss names.
        rows = [
            _row("BTG", "cycle", 105, "Materials"),
            _row("FSM", "cycle", 102, "Materials"),
            _row("CENX", "cycle", 99, "Materials"),
            _row("YELP", "core", 100, "Communication"),
            _row("JAZZ", "near", 84, "Healthcare"),
            _row("DOCS", "near", 83, "Healthcare"),
        ]
        selected, counts = SCREEN._select_multilane(rows, limit=3, config=PLAN)
        symbols = [row["symbol"] for row in selected]
        # Best cyclical takes its single-slot cap; the lane-first fill used to
        # hand all three slots to core/near-miss and defer BTG/FSM/CENX.
        self.assertIn("BTG", symbols)
        self.assertIn("YELP", symbols)
        self.assertEqual(counts["cyclical_normalization"], 1)
        self.assertNotIn("FSM", symbols)  # cyclical cap is 1
        self.assertEqual(len(symbols), 3)

    def test_full_budget_keeps_lane_first_plan(self) -> None:
        rows = [
            _row("C1", "core", 100, "Technology"),
            _row("C2", "core", 99, "Industrials"),
            _row("G1", "growth", 98, "Healthcare"),
            _row("N1", "near", 97, "Consumer"),
            _row("Y1", "cycle", 96, "Materials"),
            _row("C3", "core", 95, "Energy"),
        ]
        selected, counts = SCREEN._select_multilane(rows, limit=5, config=PLAN)
        self.assertEqual({row["symbol"] for row in selected}, {"C1", "C2", "G1", "N1", "Y1"})
        self.assertEqual(counts["core_garp"], 2)
        self.assertEqual(counts["cyclical_normalization"], 1)

    def test_small_budget_is_deterministic_and_respects_sector_cap(self) -> None:
        rows = [
            _row("A", "cycle", 100, "Materials"),
            _row("B", "core", 99, "Materials"),
            _row("C", "core", 98, "Materials"),  # third Materials name: sector cap 2
            _row("D", "near", 97, "Healthcare"),
        ]
        first, _ = SCREEN._select_multilane(rows, limit=3, config=PLAN)
        second, _ = SCREEN._select_multilane(list(reversed(rows)), limit=3, config=PLAN)
        self.assertEqual([r["symbol"] for r in first], [r["symbol"] for r in second])
        self.assertEqual({r["symbol"] for r in first}, {"A", "B", "D"})


if __name__ == "__main__":
    unittest.main()
