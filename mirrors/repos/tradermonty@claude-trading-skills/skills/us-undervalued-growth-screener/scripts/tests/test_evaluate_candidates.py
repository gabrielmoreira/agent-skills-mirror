from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets"
EXAMPLE_PATH = ASSETS_DIR / "candidate-input.example.json"
AUDIT_ROWS_PATH = ASSETS_DIR / "broad-screen-results.example.jsonl"
UNIVERSE_AUDIT_ROWS_PATH = ASSETS_DIR / "universe-audit-results.example.jsonl"
UNIVERSE_AUDIT_PATH = UNIVERSE_AUDIT_ROWS_PATH
MARKET_CONTEXT_PATH = ASSETS_DIR / "market-context.example.json"
GLOBAL_SOURCES_PATH = ASSETS_DIR / "global-sources.example.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


EVALUATOR = load_module("evaluate_candidates", SCRIPTS_DIR / "evaluate_candidates.py")
RUN_STATE = load_module("manage_run_state", SCRIPTS_DIR / "manage_run_state.py")
CONTRACT = load_module("research_contract_test", SCRIPTS_DIR / "research_contract.py")
SCREEN = load_module("screen_universe_test", SCRIPTS_DIR / "screen_universe.py")
DISCOVERY = load_module("build_discovery_pool_test", SCRIPTS_DIR / "build_discovery_pool.py")
NORMALIZER = load_module("normalize_estimates_test", SCRIPTS_DIR / "normalize_estimates.py")
VERSION = load_module("skill_version_test", SCRIPTS_DIR / "skill_version.py")
PREPUBLISH = load_module("prepublish_audit_test", SCRIPTS_DIR / "prepublish_audit.py")
BUNDLER = load_module("bundle_run_artifacts_test", SCRIPTS_DIR / "bundle_run_artifacts.py")
PROVIDER_POOL = load_module(
    "build_provider_prefilter_pool_test", SCRIPTS_DIR / "build_provider_prefilter_pool.py"
)
ORIGINAL_SCREEN_RUN = SCREEN.run
ORIGINAL_SCREEN_RUN_LAYERED = SCREEN.run_layered
ORIGINAL_DISCOVERY_BUILD_POOL = DISCOVERY.build_pool


def _prepare_screen_rows(
    rows: list[dict], *, analysis_as_of: str = "2026-08-22T14:00:00-07:00"
) -> list[dict]:
    """Upgrade legacy test rows to the current discovery input contract.

    Production code remains fail-closed.  Only general regression fixtures are
    normalized here; v3.4 rejection tests call the original functions directly.
    """
    prepared = deepcopy(rows)
    for row in prepared:
        metrics = row.get("metrics") if isinstance(row.get("metrics"), dict) else {}

        def first(*keys, row=row, metrics=metrics):
            for key in keys:
                if row.get(key) is not None:
                    return row.get(key)
                if metrics.get(key) is not None:
                    return metrics.get(key)
            return None

        addv = first("average_daily_dollar_volume", "avg_dollar_volume")
        avg_volume = first("average_volume", "avg_volume")
        if addv is not None:
            row.setdefault("average_daily_dollar_volume", addv)
            row.setdefault("average_daily_dollar_volume_method", "provider_average_dollar_volume")
            row.setdefault("average_volume_period_days", 20)
            row.setdefault("liquidity_source_ids", ["listing-source"])
        elif avg_volume is not None:
            row.setdefault("average_volume", avg_volume)
            row.setdefault("average_daily_dollar_volume_method", "price_x_provider_average_volume")
            row.setdefault("average_volume_period_days", 20)
            row.setdefault("liquidity_source_ids", ["listing-source"])

        pe = first("forward_pe")
        price = first("price", "last")
        if (
            isinstance(pe, (int, float))
            and pe > 0
            and isinstance(price, (int, float))
            and price > 0
        ):
            row.setdefault("forward_pe", pe)
            row.setdefault("forward_eps", price / pe)
            row.setdefault("forward_pe_period", "FY1")
            row.setdefault("forward_fiscal_year", "FY2027")
            row.setdefault("forward_period_end", "2027-06-30")
            row.setdefault("forward_estimate_as_of", analysis_as_of)
            row.setdefault("forward_estimate_source_ids", ["estimate-source"])
            row.setdefault("forward_metric_origin", "provider_fy1_pe_with_eps_reconciliation")
            row.setdefault("analyst_count", first("analyst_count", "fy1_analyst_count") or 4)
    return prepared


def _screen_run_layered_with_contract(universe_rows, candidate_rows, config, *args, **kwargs):
    analysis_as_of = kwargs.get("analysis_as_of", "2026-08-22T14:00:00-07:00")
    prepared_universe = _prepare_screen_rows(list(universe_rows), analysis_as_of=analysis_as_of)
    prepared_candidates = _prepare_screen_rows(list(candidate_rows), analysis_as_of=analysis_as_of)
    mode = kwargs.get("candidate_generation_mode", "full_universe_fundamentals")
    if mode != "full_universe_fundamentals":
        audit = deepcopy(kwargs.get("discovery_audit") or {})
        audit.setdefault("runtime", VERSION.runtime_metadata())
        audit.setdefault("valid", True)
        audit.setdefault("selection_method", "sector_market_cap_stratified_validated_liquidity")
        audit.setdefault("input_row_count", len(prepared_universe))
        audit.setdefault("selected_count", len(prepared_candidates))
        audit.setdefault(
            "selected_symbols",
            sorted(str(row.get("symbol") or "").upper() for row in prepared_candidates),
        )
        audit.setdefault("source_ids", ["listing-source"])
        audit.setdefault("artifact_path", "discovery-pool.jsonl")
        audit.setdefault("artifact_sha256", "synthetic-test-sha")
        audit.setdefault(
            "liquidity_validation", {"basis_validated": True, "minimum_window_days": 20}
        )
        audit.setdefault(
            "coverage_plan",
            {
                "coverage_plan_valid": True,
                "user_requested_range_spanned": True,
                "market_cap_buckets_cover_user_requested_range": True,
                "single_band_only": False,
            },
        )
        audit.setdefault(
            "scope",
            {
                "user_requested_min_market_cap": 500_000_000,
                "user_requested_max_market_cap": 20_000_000_000,
                "user_requested_scope_complete": True,
                "scope_valid": True,
            },
        )
        kwargs["discovery_audit"] = audit
    return ORIGINAL_SCREEN_RUN_LAYERED(
        prepared_universe, prepared_candidates, config, *args, **kwargs
    )


SCREEN.run_layered = _screen_run_layered_with_contract


def _screen_run_with_contract(rows, config, *args, **kwargs):
    analysis_as_of = kwargs.get("analysis_as_of", "2026-08-22T14:00:00-07:00")
    return ORIGINAL_SCREEN_RUN(
        _prepare_screen_rows(list(rows), analysis_as_of=analysis_as_of), config, *args, **kwargs
    )


SCREEN.run = _screen_run_with_contract


def _discovery_build_pool_with_contract(rows, *args, **kwargs):
    return ORIGINAL_DISCOVERY_BUILD_POOL(_prepare_screen_rows(list(rows)), *args, **kwargs)


DISCOVERY.build_pool = _discovery_build_pool_with_contract


def canonical_jsonl(rows: list[dict]) -> bytes:
    return b"".join(
        (json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode(
            "utf-8"
        )
        for row in rows
    )


def deep_dive_plan(selected: list[str], analysis_as_of: str, *, maximum: int = 3) -> dict:
    payload = {
        "analysis_as_of": analysis_as_of,
        "max_deep_dive_candidates": maximum,
        "selected_symbols": sorted(selected),
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "selected_symbols": sorted(selected),
        "selected_count": len(selected),
        "all_selected_must_be_resolved": True,
        "budget_locked": True,
        "budget_change_requires_rescreen": True,
        "user_confirmation_required": False,
        "user_continue_instruction_allowed": False,
        "selected_set_is_committed": True,
        "max_deep_dive_candidates": maximum,
        "selected_set_sha256": digest,
        "commitment_payload": payload,
    }


class FixtureMixin:
    def setUp(self) -> None:
        self.payload = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
        self.audit_rows = [
            json.loads(line)
            for line in AUDIT_ROWS_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.universe_audit_rows = [
            json.loads(line)
            for line in UNIVERSE_AUDIT_ROWS_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.universe_rows = [
            json.loads(line)
            for line in UNIVERSE_AUDIT_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def candidate(self, symbol: str) -> dict:
        for row in self.payload["candidates"]:
            if row.get("identity", {}).get("symbol") == symbol:
                return row
        raise AssertionError(f"missing candidate {symbol}")

    def audit_row(self, symbol: str) -> dict:
        for row in self.audit_rows:
            if row.get("symbol") == symbol:
                return deepcopy(row)
        raise AssertionError(f"missing audit row {symbol}")

    def universe_audit_row(self, symbol: str) -> dict:
        for row in self.universe_audit_rows:
            if row.get("symbol") == symbol:
                return deepcopy(row)
        raise AssertionError(f"missing universe audit row {symbol}")

    def universe_row(self, symbol: str) -> dict:
        for row in self.universe_rows:
            if row.get("symbol") == symbol:
                return deepcopy(row)
        raise AssertionError(f"missing universe row {symbol}")

    def single(self, symbol: str) -> dict:
        payload = deepcopy(self.payload)
        payload["candidates"] = [deepcopy(self.candidate(symbol))]
        candidate_row = self.audit_row(symbol)
        universe_row = self.universe_audit_row(symbol)
        decision = candidate_row["decision"]["status"]
        selected = [symbol] if decision == "selected" else []
        universe_rows = [universe_row]
        candidate_rows = [candidate_row]
        universe_sha = hashlib.sha256(canonical_jsonl(universe_rows)).hexdigest()
        candidate_sha = hashlib.sha256(canonical_jsonl(candidate_rows)).hexdigest()

        attempted = candidate_row.get("enrichment_attempted") is True
        resolved = candidate_row.get("enrichment_resolved") is True
        unresolved = not resolved
        evaluable = candidate_row.get("discovery_evaluable") is True
        selection_eligible = candidate_row.get("selection_eligible") is True
        exhausted = resolved

        if selected:
            pool_status = "sufficient" if resolved else "sufficient_pending_enrichment"
            outcome = "selected" if resolved else "selected_pending_enrichment"
        elif unresolved:
            pool_status = "insufficient_data"
            outcome = "insufficient_data"
        else:
            pool_status = "no_qualifying_candidates"
            outcome = "no_candidates"

        payload["screening_audit"] = {
            "audit_schema_version": 3,
            "contract_revision": VERSION.CONTRACT_REVISION,
            "runtime": VERSION.runtime_metadata(),
            "analysis_as_of": payload["analysis_as_of"],
            "generated_at": payload["analysis_as_of"],
            "candidate_generation_mode": "full_universe_fundamentals",
            "candidate_pool_status": pool_status,
            "selection_outcome": outcome,
            "selected_symbols": selected,
            "deep_dive_plan": deep_dive_plan(selected, payload["analysis_as_of"], maximum=3),
            "filters": {
                "test_fixture": True,
                "minimum_listing_data_coverage_pct": 95.0,
                "max_deep_dive_candidates": 3,
            },
            "source_ids": ["universe-fmp-20260822"],
            "scope": {
                "requested_min_market_cap": 500_000_000,
                "requested_max_market_cap": 20_000_000_000,
                "retrieval_min_market_cap": 500_000_000,
                "retrieval_max_market_cap": 20_000_000_000,
                "retrieval_scope_explicit": True,
                "scope_override_authorized": False,
                "scope_reduction_reason": None,
                "user_scope_evidence": None,
                "user_requested_scope": {
                    "min_market_cap": 500_000_000,
                    "max_market_cap": 20_000_000_000,
                    "source": "skill_default",
                },
                "scope_reduced": False,
                "scope_reduction_mode": "none",
                "scope_reduction_disclosed": True,
                "user_requested_scope_complete": True,
                "executed_scope_complete": True,
                "bounded_sampling_ready": False,
                "screening_scope_ready": True,
                "executed_scope": {
                    "min_market_cap": 500_000_000,
                    "max_market_cap": 20_000_000_000,
                },
                "scope_complete": True,
                "reasons": [],
                "enumeration": {
                    "verified": True,
                    "provider_reported_total": 1,
                    "rows_fetched": 1,
                    "pages_fetched": 1,
                    "pagination_exhausted": True,
                    "band_audit": [],
                    "bands_well_formed": False,
                    "bands_cover_executed_range": False,
                    "bands_cover_requested_range": False,
                    "bands_verified": False,
                },
            },
            "universe": {
                "row_count": 1,
                "decision_counts": {universe_row["listing_decision"]["status"]: 1},
                "listing_data_complete_count": int(
                    universe_row.get("listing_data_complete") is True
                ),
                "listing_data_complete_pct": 100.0
                if universe_row.get("listing_data_complete") is True
                else 0.0,
                "in_scope_count": int(
                    universe_row["listing_decision"]["status"] in {"in_scope", "liquidity_review"}
                ),
                "source_ids": ["universe-fmp-20260822"],
                "embedded_rows": universe_rows,
                "artifact_sha256": universe_sha,
            },
            "candidate_pool": {
                "row_count": 1,
                "decision_counts": {decision: 1},
                "discovery_evaluable_count": int(evaluable),
                "discovery_evaluable_pct": 100.0 if evaluable else 0.0,
                "selection_eligible_count": int(selection_eligible),
                "selected_count": len(selected),
                "in_scope_covered_count": 1,
                "in_scope_missing_count": 0,
                "in_scope_missing_symbols": [],
                "coverage_complete": True,
                "coverage_scope": "full_listing_universe",
                "listing_coverage_complete": True,
                "generation_audit": {
                    "runtime": VERSION.runtime_metadata(),
                    "valid": True,
                    "selection_method": "full_universe_fundamentals",
                    "input_row_count": 1,
                    "selected_count": 1,
                    "selected_symbols": [symbol],
                    "liquidity_validation": {
                        "basis_validated": True,
                        "minimum_window_days": 20,
                    },
                    "coverage_plan": {
                        "coverage_plan_valid": True,
                        "user_requested_range_spanned": True,
                        "market_cap_buckets_cover_user_requested_range": True,
                        "single_band_only": False,
                    },
                },
                "generation_review_reasons": [],
                "fundamental_complete_count": int(
                    candidate_row.get("fundamental_complete") is True
                ),
                "fundamental_complete_pct": 100.0
                if candidate_row.get("fundamental_complete") is True
                else 0.0,
                "source_ids": ["universe-fmp-20260822"],
                "symbols_not_in_universe": [],
                "embedded_rows": candidate_rows,
                "artifact_sha256": candidate_sha,
            },
            "enrichment": {
                "status": "complete" if resolved else "pending",
                "next_action": (
                    "proceed_to_deep_dive"
                    if selected and resolved
                    else "continue_enrichment"
                    if unresolved
                    else "publish_no_candidates"
                ),
                "discovery_pool_required": False,
                "attempted_count": int(attempted),
                "resolved_count": int(resolved),
                "unresolved_count": int(unresolved),
                "resolution_pct": 100.0 if resolved else 0.0,
                "all_rows_resolved": resolved,
                "maximum_attempts": 60,
                "candidate_pool_exhaustion_declared": exhausted,
                "candidate_pool_exhausted": exhausted,
                "candidate_pool_covers_in_scope": True,
                "candidate_pool_scope_verified": True,
                "conclusion_scope": "full_listing_universe",
                "queue_count": int(unresolved),
                "queue_symbols": [symbol] if unresolved else [],
            },
        }
        payload["screening_funnel"] = {
            "universe_count": 1,
            "listing_in_scope_count": int(
                universe_row["listing_decision"]["status"] in {"in_scope", "liquidity_review"}
            ),
            "candidate_pool_count": 1,
            "discovery_evaluable_count": int(evaluable),
            "deep_dive_selected_count": len(selected),
            "preflight_passed_count": len(selected),
            "deep_dive_completed_count": len(selected),
        }
        payload["run_metadata"]["status"] = (
            "complete" if pool_status in {"sufficient", "no_qualifying_candidates"} else "partial"
        )
        payload["run_metadata"]["selected_symbols"] = selected
        payload["run_metadata"]["unprocessed_candidates"] = [] if resolved else [symbol]
        return payload

    def evaluate(self, payload: dict, *, strict: bool = True) -> dict:
        return EVALUATOR.evaluate_snapshot(payload, strict=strict, artifact_root=ASSETS_DIR)


class EvaluatorTests(FixtureMixin, unittest.TestCase):
    def test_example_strict_statuses(self) -> None:
        report = self.evaluate(self.payload)
        self.assertEqual([row["symbol"] for row in report["ranked_candidates"]], ["ACME"])
        self.assertEqual({row["symbol"] for row in report["review_required"]}, {"CYCLE", "STALE"})
        self.assertEqual([row["symbol"] for row in report["screened_out"]], ["SCREEN"])
        self.assertEqual({row["symbol"] for row in report["excluded"]}, {"MNA", "OTCX"})
        self.assertEqual(report["ranked_candidates"][0]["data_quality_score"], 100)
        self.assertEqual(report["ranking_status"], "final")
        self.assertTrue(report["contract"]["valid"])

    def test_constant_multiple_scenario_uses_forward_metric(self) -> None:
        report = self.evaluate(self.single("ACME"))
        acme = report["ranked_candidates"][0]
        self.assertEqual(acme["valuation"]["current_period_kind"], "fy1")
        year_three = acme["valuation"]["constant_multiple"]["year_3"]
        stress = acme["valuation"]["multiple_contraction"]["year_3"]
        self.assertAlmostEqual(year_three["implied_price"], 66.6667, places=3)
        self.assertAlmostEqual(year_three["upside_pct"], 66.6667, places=3)
        self.assertAlmostEqual(stress["implied_price"], 53.3333, places=3)
        self.assertAlmostEqual(stress["upside_pct"], 33.3333, places=3)

    def test_ttm_current_metric_blocks_formal_scenario(self) -> None:
        payload = self.single("ACME")
        candidate = payload["candidates"][0]
        candidate["identity"]["symbol"] = "TTMX"
        candidate["valuation_case"]["periods"]["current"]["period_kind"] = "ttm"
        report = self.evaluate(payload)
        row = report["review_required"][0]
        self.assertFalse(row["valuation"]["formal_forward_scenario_valid"])
        self.assertIsNone(row["valuation"]["constant_multiple"]["year_3"])
        self.assertTrue(any("NTM or FY1" in reason for reason in row["review_reasons"]))

    def test_one_analyst_year3_cannot_be_sole_ranked_horizon(self) -> None:
        payload = self.single("ACME")
        candidate = payload["candidates"][0]
        candidate["identity"]["symbol"] = "THIN"
        candidate["valuation_case"]["periods"]["year_2"]["metric"] = None
        candidate["valuation_case"]["periods"]["year_3"]["analyst_count"] = 1
        report = self.evaluate(payload)
        row = report["review_required"][0]
        self.assertFalse(row["valuation"]["rankable_horizons"]["year_3"])
        self.assertTrue(any("no rankable" in reason.lower() for reason in row["review_reasons"]))

    def test_sum_four_discrete_cash_flow_is_canonical(self) -> None:
        report = self.evaluate(self.single("ACME"))
        cash = report["ranked_candidates"][0]["financial_metrics"]["cash_flow_ttm"]
        self.assertEqual(cash["operating_cash_flow"], 210_000_000)
        self.assertEqual(cash["capex_cash_outflow"], 30_000_000)
        self.assertEqual(cash["standard_fcf"], 180_000_000)
        self.assertEqual(len(cash["used_periods"]), 4)

    def test_negative_capex_sign_is_fail_closed(self) -> None:
        payload = self.single("ACME")
        candidate = payload["candidates"][0]
        candidate["identity"]["symbol"] = "NEGCF"
        candidate["financials"]["cash_flow_periods"][0]["capex_cash_outflow"] = -7_000_000
        report = self.evaluate(payload)
        row = report["review_required"][0]
        self.assertTrue(
            any("capex_cash_outflow must be non-negative" in warning for warning in row["warnings"])
        )
        self.assertTrue(
            any("missing/invalid OCF or capex" in reason for reason in row["review_reasons"])
        )

    def test_ytd_reconstruction(self) -> None:
        payload = self.single("ACME")
        candidate = payload["candidates"][0]
        candidate["identity"]["symbol"] = "YTD"
        candidate["financials"]["cash_flow_ttm"].update(
            {
                "method": "fy_plus_current_ytd_minus_prior_ytd",
                "operating_cash_flow": 230_000_000,
                "capex_cash_outflow": 36_000_000,
                "standard_fcf": 194_000_000,
            }
        )
        candidate["financials"]["ttm_reconstruction"] = {
            "latest_fy": {
                "period": "FY2025",
                "operating_cash_flow": 200_000_000,
                "capex_cash_outflow": 30_000_000,
                "source_ids": ["acme-10q"],
            },
            "current_ytd": {
                "period": "H1 FY2026",
                "operating_cash_flow": 120_000_000,
                "capex_cash_outflow": 18_000_000,
                "source_ids": ["acme-10q"],
            },
            "prior_ytd": {
                "period": "H1 FY2025",
                "operating_cash_flow": 90_000_000,
                "capex_cash_outflow": 12_000_000,
                "source_ids": ["acme-10q"],
            },
        }
        sec_source = next(source for source in candidate["sources"] if source["id"] == "acme-10q")
        for support_path in (
            "financials.ttm_reconstruction.latest_fy",
            "financials.ttm_reconstruction.current_ytd",
            "financials.ttm_reconstruction.prior_ytd",
        ):
            if support_path not in sec_source["supports"]:
                sec_source["supports"].append(support_path)
        report = self.evaluate(payload)
        cash = report["ranked_candidates"][0]["financial_metrics"]["cash_flow_ttm"]
        self.assertEqual(cash["operating_cash_flow"], 230_000_000)
        self.assertEqual(cash["capex_cash_outflow"], 36_000_000)
        self.assertEqual(cash["standard_fcf"], 194_000_000)

    def test_company_adjusted_fcf_is_not_used_as_standard(self) -> None:
        payload = self.single("ACME")
        candidate = payload["candidates"][0]
        candidate["financials"]["cash_flow_ttm"]["company_adjusted_fcf"] = 999_000_000
        report = self.evaluate(payload)
        metrics = report["ranked_candidates"][0]["financial_metrics"]
        self.assertEqual(metrics["standard_fcf"], 180_000_000)
        self.assertEqual(metrics["company_adjusted_fcf"], 999_000_000)

    def test_ev_to_fcf_uses_corporate_cash_and_marketable_securities(self) -> None:
        report = self.evaluate(self.single("ACME"))
        metrics = report["ranked_candidates"][0]["financial_metrics"]
        self.assertEqual(metrics["cash_definition"], "corporate_cash_plus_marketable_securities")
        self.assertAlmostEqual(metrics["enterprise_value"], 4_920_000_000, delta=1)
        self.assertAlmostEqual(metrics["ev_to_fcf"], 27.3333, places=3)

    def test_cash_inconsistency_without_reconciliation_blocks(self) -> None:
        payload = self.single("ACME")
        candidate = payload["candidates"][0]
        candidate["identity"]["symbol"] = "CASHX"
        candidate["latest_earnings"]["quarter"]["metrics"].update(
            {
                "cash_and_equivalents": 100_000_000,
                "marketable_securities": 20_000_000,
                "total_debt": 100_000_000,
            }
        )
        report = self.evaluate(payload)
        row = report["review_required"][0]
        self.assertTrue(
            any("cash_and_equivalents differs" in reason for reason in row["review_reasons"])
        )
        self.assertLessEqual(row["data_quality_score"], 70)

    def test_consistent_adjusted_basis_with_reconciliation_can_rank(self) -> None:
        payload = self.single("ACME")
        candidate = payload["candidates"][0]
        candidate["identity"]["symbol"] = "ADJBASIS"
        for key in ("current", "year_2", "year_3"):
            candidate["valuation_case"]["periods"][key]["metric_basis"] = "company_adjusted"
        candidate["forecast_bridge"]["periods"]["year_2"]["metric_basis"] = "company_adjusted"
        candidate["forecast_bridge"]["periods"]["year_3"]["metric_basis"] = "company_adjusted"
        candidate["gaap_reconciliation"] = {
            "periods": {
                "current": {
                    "gaap_metric": 2.8,
                    "adjustments": [
                        {"label": "Recurring amortization", "amount": 0.2, "recurring": True}
                    ],
                    "source_ids": ["acme-10q", "analyst-model"],
                },
                "year_2": {
                    "gaap_metric": 4.0,
                    "adjustments": [
                        {"label": "Recurring amortization", "amount": 0.2, "recurring": True}
                    ],
                    "source_ids": ["consensus-20260822", "analyst-model"],
                },
                "year_3": {
                    "gaap_metric": 4.8,
                    "adjustments": [
                        {"label": "Recurring amortization", "amount": 0.2, "recurring": True}
                    ],
                    "source_ids": ["consensus-20260822", "analyst-model"],
                },
            }
        }
        # Driver model must independently produce GAAP EPS and then add the
        # same after-tax per-share adjustment used by the reconciliation.
        for key, gaap_eps, adjustment_per_share in (("year_2", 4.0, 0.2), ("year_3", 4.8, 0.2)):
            period = candidate["valuation_case"]["periods"][key]
            bridge = candidate["forecast_bridge"]["periods"][key]
            drivers = bridge["drivers"]
            shares = float(drivers["diluted_shares"])
            tax_rate = float(drivers["tax_rate_pct"]) / 100.0
            net_interest_income = float(drivers.get("net_interest_income", 0.0))
            gaap_net_income = gaap_eps * shares
            pretax_income = gaap_net_income / (1.0 - tax_rate)
            operating_income = pretax_income - net_interest_income
            drivers["operating_margin_pct"] = operating_income / float(drivers["revenue"]) * 100.0
            drivers["after_tax_adjustments"] = adjustment_per_share * shares
            bridge.setdefault("driver_provenance", {})["after_tax_adjustments"] = {
                "origin": "analyst_assumption",
                "source_ids": ["analyst-model"],
                "target_solved": False,
            }
            bridge["metric_numerator"] = float(period["metric"]) * shares
            bridge["metric_denominator"] = shares
        for peer in candidate["peers"]:
            peer["metric_basis"] = "company_adjusted"
        candidate["valuation_case"]["peer_median_multiple"]["metric_basis"] = "company_adjusted"
        report = self.evaluate(payload)
        row = report["ranked_candidates"][0]
        self.assertTrue(row["valuation"]["metric_basis_consistent"])
        self.assertTrue(row["valuation"]["gaap_reconciliation_valid"])

    def test_metric_basis_mismatch_blocks_scenario(self) -> None:
        payload = self.single("ACME")
        candidate = payload["candidates"][0]
        candidate["identity"]["symbol"] = "MIXED"
        candidate["valuation_case"]["periods"]["year_3"]["metric_basis"] = "company_adjusted"
        report = self.evaluate(payload)
        row = report["review_required"][0]
        self.assertFalse(row["valuation"]["metric_basis_consistent"])
        self.assertIsNone(row["valuation"]["constant_multiple"]["year_3"])

    def test_self_attestation_does_not_create_quality_evidence(self) -> None:
        payload = self.single("ACME")
        candidate = payload["candidates"][0]
        candidate["identity"]["symbol"] = "CLAIM"
        candidate["research_completeness"] = {key: True for key in EVALUATOR.QUALITY_WEIGHTS}
        candidate.pop("forecast_bridge")
        candidate["evidence"] = {"identity.price": ["quote-20260821"]}
        report = self.evaluate(payload)
        row = report["review_required"][0]
        self.assertFalse(row["data_quality_details"]["forecast_bridge_verified"]["awarded"])
        self.assertTrue(
            any("forecast bridge" in reason.lower() for reason in row["review_reasons"])
        )

    def test_commercial_biopharma_concentration_is_derived_and_loe_stressed(self) -> None:
        payload = self.single("ACME")
        candidate = payload["candidates"][0]
        candidate["identity"]["symbol"] = "BIO"
        candidate["sector_profile"] = {
            "type": "commercial_biopharma",
            "kpis": {
                "top_product_revenue": 82_700_000,
                "total_revenue": 100_000_000,
                "nearest_material_loe_date": "2028-08-22",
                "source_ids": ["acme-10q"],
            },
        }
        report = self.evaluate(payload)
        row = report["ranked_candidates"][0]
        self.assertAlmostEqual(row["sector_profile"]["top_product_revenue_pct"], 82.7, places=1)
        self.assertTrue(row["sector_profile"]["concentration_derived"])
        self.assertEqual(
            [x["multiple"] for x in row["sector_profile"]["loe_stress_scenarios"]], [6.0, 8.0]
        )
        self.assertGreater(row["penalties"]["sector_specific_risk"], 0)

    def test_payments_profile_requires_sourced_cash_separation(self) -> None:
        payload = self.single("ACME")
        candidate = payload["candidates"][0]
        candidate["identity"]["symbol"] = "PAY"
        candidate["sector_profile"] = {
            "type": "payments",
            "kpis": {"gross_profit_to_tpv_pct": 0.72, "gross_profit_to_tpv_prior_pct": 1.07},
        }
        report = self.evaluate(payload)
        row = report["review_required"][0]
        self.assertTrue(any("sourced corporate cash" in reason for reason in row["review_reasons"]))
        self.assertTrue(any("take rate declined" in warning for warning in row["warnings"]))

    def test_auto_dealer_requires_floorplan_adjustment(self) -> None:
        payload = self.single("ACME")
        candidate = payload["candidates"][0]
        candidate["identity"]["symbol"] = "AUTO"
        candidate["sector_profile"] = {
            "type": "auto_dealership",
            "kpis": {"source_ids": ["acme-10q"]},
        }
        report = self.evaluate(payload)
        row = report["review_required"][0]
        self.assertTrue(any("floorplan debt" in reason for reason in row["review_reasons"]))

    def test_completed_mna_is_hard_excluded(self) -> None:
        report = self.evaluate(self.single("MNA"))
        self.assertTrue(
            any(
                "M&A status is completed" in reason
                for reason in report["excluded"][0]["hard_exclusion_reasons"]
            )
        )

    def test_stale_event_price_is_review_required(self) -> None:
        report = self.evaluate(self.single("STALE"))
        self.assertTrue(
            any(
                "predates the latest earnings" in reason
                for reason in report["review_required"][0]["review_reasons"]
            )
        )

    def test_cyclical_normalization_is_evidence_based(self) -> None:
        report = self.evaluate(self.single("CYCLE"))
        row = report["review_required"][0]
        self.assertTrue(
            any("normalization is required" in reason for reason in row["review_reasons"])
        )

    def test_minimum_upside_gate(self) -> None:
        payload = self.single("ACME")
        candidate = payload["candidates"][0]
        candidate["identity"]["symbol"] = "LOWUP"
        candidate["valuation_case"]["periods"]["year_2"]["metric"] = 3.1
        candidate["valuation_case"]["periods"]["year_3"]["metric"] = 3.3
        candidate["forecast_bridge"]["periods"]["year_2"]["metric_numerator"] = 387_500_000
        candidate["forecast_bridge"]["periods"]["year_3"]["metric_numerator"] = 405_900_000
        report = self.evaluate(payload)
        self.assertTrue(
            any(
                "constant-multiple upside" in reason
                for reason in report["review_required"][0]["review_reasons"]
            )
        )

    def test_score_penalties_are_explicit(self) -> None:
        payload = self.single("ACME")
        candidate = payload["candidates"][0]
        candidate["identity"]["symbol"] = "DILUTE"
        candidate["financials"]["sbc_ttm"] = 180_000_000
        candidate["financials"]["histories"]["diluted_shares"] = [
            {"date": "2023-12-31", "period": "FY2023", "value": 100_000_000},
            {"date": "2024-12-31", "period": "FY2024", "value": 112_000_000},
            {"date": "2025-12-31", "period": "FY2025", "value": 125_000_000},
        ]
        report = self.evaluate(payload)
        candidates = (
            report["ranked_candidates"] + report.get("conditional", []) + report["review_required"]
        )
        result = next(row for row in candidates if row["symbol"] == "DILUTE")
        self.assertEqual(result["penalties"]["sbc"], 5)
        self.assertEqual(result["penalties"]["dilution"], 8)
        self.assertEqual(result["total_penalty"], 13)

    def test_completed_no_candidates_run_is_final_without_ranked_names(self) -> None:
        payload = self.single("SCREEN")
        payload["candidates"] = []
        payload["run_metadata"]["status"] = "complete"
        report = self.evaluate(payload)
        self.assertEqual(report["ranking_status"], "final")
        self.assertTrue(report["contract"]["valid"])
        self.assertEqual(report["contract"]["selection_outcome"], "no_candidates")
        self.assertEqual(report["ranked_candidates"], [])
        self.assertEqual(
            report["final_three"],
            {"highest_conviction": None, "most_undervalued": None, "largest_upside": None},
        )

    def test_partial_run_is_provisional_and_has_no_final_three(self) -> None:
        payload = self.single("ACME")
        payload["run_metadata"]["status"] = "partial"
        payload["run_metadata"]["unprocessed_candidates"] = ["OTHER"]
        report = self.evaluate(payload)
        self.assertEqual(report["ranking_status"], "provisional")
        self.assertIsNone(report["final_three"]["highest_conviction"])

    def test_markdown_contains_full_contract_sections_and_no_placeholder(self) -> None:
        report = self.evaluate(self.single("ACME"))
        markdown = EVALUATOR.render_markdown(report, language="ja")
        for heading in [
            "#### 1. 基本情報",
            "#### 5. 直近決算",
            "#### 7. 同業他社比較",
            "#### 9. 倍率据え置きシナリオ",
            "#### 13. 投資仮説の無効化条件",
            "## H. 最終選定3銘柄",
            "## I. 情報源台帳",
            "## J. 未解決データと全体警告",
        ]:
            self.assertIn(heading, markdown)
        self.assertNotIn("Replace this", markdown)
        self.assertNotIn("placeholder", markdown.lower())

    def test_cli_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            exit_code = EVALUATOR.main(
                [
                    "--input",
                    str(EXAMPLE_PATH),
                    "--artifact-root",
                    str(ASSETS_DIR),
                    "--output-dir",
                    temp_dir,
                    "--language",
                    "ja",
                    "--strict",
                ]
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(len(list(Path(temp_dir).glob("*.json"))), 1)
            self.assertEqual(len(list(Path(temp_dir).glob("*.md"))), 1)

    def test_cli_require_final_returns_two_for_partial_run(self) -> None:
        payload = self.single("ACME")
        payload["run_metadata"]["status"] = "partial"
        payload["run_metadata"]["unprocessed_candidates"] = ["OTHER"]
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "partial.json"
            input_path.write_text(json.dumps(payload), encoding="utf-8")
            output_dir = Path(temp_dir) / "out"
            exit_code = EVALUATOR.main(
                [
                    "--input",
                    str(input_path),
                    "--artifact-root",
                    str(ASSETS_DIR),
                    "--output-dir",
                    str(output_dir),
                    "--strict",
                    "--require-final",
                ]
            )
            self.assertEqual(exit_code, 2)
            self.assertEqual(len(list(output_dir.glob("*.json"))), 1)
            self.assertEqual(len(list(output_dir.glob("*.md"))), 1)


class ContractTests(FixtureMixin, unittest.TestCase):
    def validate(self, payload: dict) -> tuple[dict, dict]:
        return CONTRACT.validate_and_normalize_snapshot(payload, artifact_root=ASSETS_DIR)

    def test_market_context_placeholder_is_blocked_and_quality_capped(self) -> None:
        payload = self.single("ACME")
        payload["market_context"]["summary"] = "Replace this placeholder"
        normalized, contract = self.validate(payload)
        self.assertFalse(contract["market_context_valid"])
        caps = normalized["candidates"][0]["_contract"]["quality_caps"]
        self.assertTrue(any(cap["cap"] == 70 for cap in caps))

    def test_market_context_after_analysis_is_blocked(self) -> None:
        payload = self.single("ACME")
        payload["market_context"]["as_of"] = "2026-08-23T12:00:00-07:00"
        _, contract = self.validate(payload)
        self.assertFalse(contract["valid"])
        self.assertTrue(
            any("after analysis_as_of" in reason for reason in contract["review_reasons"])
        )

    def test_supports_must_be_array(self) -> None:
        payload = self.single("ACME")
        payload["candidates"][0]["sources"][0]["supports"] = "latest_earnings;cash"
        normalized, _ = self.validate(payload)
        row_contract = normalized["candidates"][0]["_contract"]
        self.assertFalse(row_contract["source_schema_valid"])
        self.assertTrue(
            any("supports must be" in reason for reason in row_contract["review_reasons"])
        )

    def test_source_kind_tier_mismatch_is_blocked(self) -> None:
        payload = self.single("ACME")
        payload["candidates"][0]["sources"][1]["tier"] = 3
        normalized, _ = self.validate(payload)
        reasons = normalized["candidates"][0]["_contract"]["review_reasons"]
        self.assertTrue(any("incompatible with tier" in reason for reason in reasons))

    def test_third_party_transcript_cannot_be_company_ir(self) -> None:
        payload = self.single("ACME")
        source = payload["candidates"][0]["sources"][1]
        source["title"] = "Motley Fool transcript"
        source["kind"] = "third_party_transcript"
        source["tier"] = 2
        normalized, _ = self.validate(payload)
        reasons = normalized["candidates"][0]["_contract"]["review_reasons"]
        self.assertTrue(any("incompatible with tier" in reason for reason in reasons))

    def test_mixed_quarter_and_full_year_period_is_blocked(self) -> None:
        payload = self.single("ACME")
        payload["candidates"][0]["latest_earnings"]["quarter"]["period"] = "Q4 FY2026 / FY2026"
        normalized, _ = self.validate(payload)
        reasons = normalized["candidates"][0]["_contract"]["review_reasons"]
        self.assertTrue(any("must not combine" in reason for reason in reasons))

    def test_separate_quarter_and_full_year_records_are_accepted(self) -> None:
        payload = self.single("ACME")
        candidate = payload["candidates"][0]
        candidate["latest_earnings"]["full_year"] = {
            "period_type": "full_year",
            "period": "FY2025",
            "period_end": "2025-12-31",
            "published_at": "2026-02-15T16:05:00-05:00",
            "source_ids": ["acme-10q", "acme-ir"],
            "metrics": {"revenue": 880_000_000, "gaap_eps": 2.55},
            "guidance": [],
            "key_kpis": [],
            "one_time_items": [],
        }
        normalized, _ = self.validate(payload)
        contract = normalized["candidates"][0]["_contract"]
        self.assertTrue(contract["latest_earnings_valid"])
        self.assertIsNotNone(normalized["candidates"][0]["latest_earnings_records"]["quarter"])
        self.assertIsNotNone(normalized["candidates"][0]["latest_earnings_records"]["full_year"])

    def test_audit_hash_mismatch_blocks(self) -> None:
        payload = deepcopy(self.payload)
        payload["screening_audit"]["universe"]["artifact_sha256"] = "0" * 64
        _, contract = self.validate(payload)
        self.assertFalse(contract["screening_audit_valid"])
        self.assertTrue(any("artifact_sha256" in reason for reason in contract["review_reasons"]))

    def test_valid_audit_passes(self) -> None:
        _, contract = self.validate(self.payload)
        self.assertTrue(contract["screening_audit_valid"])
        self.assertEqual(contract["selected_symbols"], ["ACME", "CYCLE", "STALE"])


class BroadScreenTests(FixtureMixin, unittest.TestCase):
    def test_high_growth_exception_is_selected(self) -> None:
        row = {
            "symbol": "EXLSX",
            "country": "US",
            "company_name": "High Growth",
            "exchange": "NASDAQ",
            "is_actively_trading": True,
            "is_common_stock": True,
            "price": 30,
            "market_cap": 5_000_000_000,
            "average_daily_dollar_volume": 20_000_000,
            "revenue_growth_pct": 18,
            "eps_growth_pct": 25,
            "standard_fcf": 200_000_000,
            "roic_pct": 16,
            "forward_pe": 25,
            "ev_to_fcf": 24,
            "fcf_yield_pct": 4.2,
            "dilution_pct": 1,
            "net_debt_to_ebitda": 1.0,
        }
        decisions, _, selected, _ = SCREEN.run(
            [row],
            dict(SCREEN.DEFAULTS),
            analysis_as_of="2026-08-22T14:00:00-07:00",
            source_ids=["u"],
        )
        self.assertEqual(selected, ["EXLSX"])
        self.assertTrue(decisions[0]["decision"]["exception_admitted"])

    def test_auto_dealer_without_floorplan_adjustment_is_review_required(self) -> None:
        row = {
            "symbol": "GPIX",
            "country": "US",
            "company_name": "Dealer",
            "exchange": "NYSE",
            "is_actively_trading": True,
            "is_common_stock": True,
            "price": 300,
            "market_cap": 8_000_000_000,
            "average_daily_dollar_volume": 20_000_000,
            "revenue_growth_pct": 10,
            "eps_growth_pct": 15,
            "standard_fcf": 500_000_000,
            "roic_pct": 12,
            "forward_pe": 8,
            "dilution_pct": -2,
            "net_debt_to_ebitda": 7,
            "sector_profile_type": "auto_dealership",
        }
        decisions, _, selected, _ = SCREEN.run(
            [row],
            dict(SCREEN.DEFAULTS),
            analysis_as_of="2026-08-22T14:00:00-07:00",
            source_ids=["u"],
        )
        self.assertEqual(selected, [])
        self.assertEqual(decisions[0]["decision"]["status"], "needs_enrichment")
        self.assertIn(
            "sector_adjusted_leverage_required", decisions[0]["decision"]["review_reasons"]
        )
        self.assertIsNone(decisions[0]["broad_score"])

    def test_all_universe_rows_are_audited_and_budget_defers(self) -> None:
        rows = []
        for index in range(7):
            rows.append(
                {
                    "symbol": f"S{index}",
                    "country": "US",
                    "exchange": "NASDAQ",
                    "is_actively_trading": True,
                    "is_common_stock": True,
                    "price": 20,
                    "market_cap": 1_000_000_000,
                    "average_daily_dollar_volume": 10_000_000,
                    "revenue_growth_pct": 12,
                    "eps_growth_pct": 18 + index,
                    "standard_fcf": 100_000_000,
                    "roic_pct": 15,
                    "forward_pe": 15,
                    "fcf_yield_pct": 6,
                    "dilution_pct": 1,
                    "net_debt_to_ebitda": 1,
                }
            )
        config = dict(SCREEN.DEFAULTS)
        config["max_deep_dive_candidates"] = 5
        decisions, audit, selected, _ = SCREEN.run(
            rows, config, analysis_as_of="2026-08-22T14:00:00-07:00", source_ids=["u"]
        )
        self.assertEqual(len(decisions), 7)
        self.assertEqual(len(selected), 5)
        self.assertEqual(audit["candidate_pool"]["decision_counts"]["deferred_by_budget"], 2)

    def test_missing_fundamentals_are_not_shortlisted(self) -> None:
        rows = [
            {
                "symbol": "MISSB",
                "country": "US",
                "exchange": "NASDAQ",
                "sector": "Technology",
                "is_actively_trading": True,
                "is_common_stock": True,
                "price": 20,
                "market_cap": 3_000_000_000,
                "average_daily_dollar_volume": 50_000_000,
            },
            {
                "symbol": "MISSA",
                "country": "US",
                "exchange": "NYSE",
                "sector": "Industrials",
                "is_actively_trading": True,
                "is_common_stock": True,
                "price": 30,
                "market_cap": 7_000_000_000,
                "average_daily_dollar_volume": 40_000_000,
            },
        ]
        _, decisions, audit, selected, _ = SCREEN.run_layered(
            rows,
            rows,
            dict(SCREEN.DEFAULTS),
            analysis_as_of="2026-08-22T14:00:00-07:00",
            universe_source_ids=["u"],
            candidate_source_ids=["e"],
            candidate_generation_mode="liquidity_stratified_estimates",
            retrieval_min_market_cap=500_000_000,
            retrieval_max_market_cap=20_000_000_000,
        )
        self.assertEqual(selected, [])
        self.assertTrue(all(row["decision"]["status"] == "needs_enrichment" for row in decisions))
        self.assertTrue(all(row["broad_score"] is None for row in decisions))
        self.assertEqual(audit["selection_outcome"], "insufficient_data")

    def test_empty_candidate_pool_is_insufficient_data_not_no_candidates(self) -> None:
        rows = [
            {
                "symbol": "ONLY",
                "country": "US",
                "exchange": "NASDAQ",
                "sector": "Technology",
                "is_actively_trading": True,
                "is_common_stock": True,
                "price": 20,
                "market_cap": 3_000_000_000,
                "average_daily_dollar_volume": 20_000_000,
            }
        ]
        _, decisions, audit, selected, _ = SCREEN.run_layered(
            rows,
            [],
            dict(SCREEN.DEFAULTS),
            analysis_as_of="2026-08-22T14:00:00-07:00",
            universe_source_ids=["u"],
            candidate_source_ids=["e"],
            candidate_generation_mode="liquidity_stratified_estimates",
            retrieval_min_market_cap=500_000_000,
            retrieval_max_market_cap=20_000_000_000,
        )
        self.assertEqual(decisions, [])
        self.assertEqual(selected, [])
        self.assertEqual(audit["selection_outcome"], "insufficient_data")

    def test_evaluable_rows_can_be_selected_while_pool_exhaustion_is_pending(self) -> None:
        rows = [
            {
                "symbol": "EARLY",
                "country": "US",
                "exchange": "NASDAQ",
                "sector": "Technology",
                "is_actively_trading": True,
                "is_common_stock": True,
                "price": 20,
                "market_cap": 3_000_000_000,
                "average_daily_dollar_volume": 20_000_000,
                "revenue_growth_pct": 12,
                "eps_growth_pct": 20,
                "forward_pe": 15,
                "analyst_count": 4,
                "enrichment_attempted": True,
            }
        ]
        _, decisions, audit, selected, _ = SCREEN.run_layered(
            rows,
            rows,
            dict(SCREEN.DEFAULTS),
            analysis_as_of="2026-08-22T14:00:00-07:00",
            universe_source_ids=["u"],
            candidate_source_ids=["e"],
            candidate_generation_mode="liquidity_stratified_estimates",
            retrieval_min_market_cap=500_000_000,
            retrieval_max_market_cap=20_000_000_000,
        )
        self.assertEqual(selected, ["EARLY"])
        self.assertEqual(decisions[0]["decision"]["status"], "selected")
        self.assertIsNotNone(decisions[0]["broad_score"])
        self.assertEqual(audit["candidate_pool_status"], "sufficient_pending_enrichment")
        self.assertEqual(audit["selection_outcome"], "selected_pending_enrichment")
        self.assertEqual(audit["selected_symbols"], ["EARLY"])
        self.assertFalse(audit["enrichment"]["candidate_pool_exhausted"])

    def test_genuine_no_candidates_requires_assessable_rows(self) -> None:
        rows = [
            {
                "symbol": "FAIL",
                "country": "US",
                "exchange": "NASDAQ",
                "sector": "Technology",
                "is_actively_trading": True,
                "is_common_stock": True,
                "price": 20,
                "market_cap": 3_000_000_000,
                "average_daily_dollar_volume": 20_000_000,
                "revenue_growth_pct": 1,
                "eps_growth_pct": 2,
                "standard_fcf": 100_000_000,
                "roic_pct": 5,
                "forward_pe": 35,
                "fcf_yield_pct": 3,
                "dilution_pct": 1,
                "net_debt_to_ebitda": 1,
            }
        ]
        _, decisions, audit, selected, _ = SCREEN.run_layered(
            rows,
            rows,
            dict(SCREEN.DEFAULTS),
            analysis_as_of="2026-08-22T14:00:00-07:00",
            universe_source_ids=["u"],
            candidate_source_ids=["u"],
            candidate_generation_mode="full_universe_fundamentals",
            retrieval_min_market_cap=500_000_000,
            retrieval_max_market_cap=20_000_000_000,
            candidate_pool_exhausted=True,
            provider_reported_total=1,
            pages_fetched=1,
            pagination_exhausted=True,
        )
        self.assertEqual(decisions[0]["decision"]["status"], "screened_out")
        self.assertEqual(selected, [])
        self.assertEqual(audit["selection_outcome"], "no_candidates")
        self.assertTrue(audit["enrichment"]["all_rows_resolved"])

    def test_review_only_rows_are_never_alphabetically_selected(self) -> None:
        rows = []
        for symbol in ("AGNC", "AHR", "ALLY", "AMH"):
            rows.append(
                {
                    "symbol": symbol,
                    "country": "US",
                    "exchange": "NASDAQ",
                    "sector": "Financial Services",
                    "sector_profile_type": "reit",
                    "is_actively_trading": True,
                    "is_common_stock": True,
                    "price": 20,
                    "market_cap": 12_000_000_000,
                    "average_daily_dollar_volume": 20_000_000,
                }
            )
        _, decisions, _, selected, _ = SCREEN.run_layered(
            rows,
            rows,
            dict(SCREEN.DEFAULTS),
            analysis_as_of="2026-08-22T14:00:00-07:00",
            universe_source_ids=["u"],
            candidate_source_ids=["e"],
            candidate_generation_mode="liquidity_stratified_estimates",
            retrieval_min_market_cap=500_000_000,
            retrieval_max_market_cap=20_000_000_000,
        )
        self.assertEqual(selected, [])
        self.assertTrue(all(row["decision"]["status"] == "needs_enrichment" for row in decisions))
        self.assertTrue(all(row["broad_score"] is None for row in decisions))

    def test_reduced_scope_is_disclosed_and_not_completion_ready(self) -> None:
        row = {
            "symbol": "READY",
            "country": "US",
            "exchange": "NASDAQ",
            "is_actively_trading": True,
            "is_common_stock": True,
            "price": 20,
            "market_cap": 12_000_000_000,
            "average_daily_dollar_volume": 20_000_000,
            "revenue_growth_pct": 12,
            "eps_growth_pct": 18,
            "standard_fcf": 100_000_000,
            "roic_pct": 15,
            "forward_pe": 15,
            "fcf_yield_pct": 6,
            "dilution_pct": 1,
            "net_debt_to_ebitda": 1,
        }
        _, _, audit, _, _ = SCREEN.run_layered(
            [row],
            [row],
            dict(SCREEN.DEFAULTS),
            analysis_as_of="2026-08-22T14:00:00-07:00",
            universe_source_ids=["u"],
            candidate_source_ids=["u"],
            candidate_generation_mode="full_universe_fundamentals",
            retrieval_min_market_cap=10_000_000_000,
            retrieval_max_market_cap=20_000_000_000,
        )
        self.assertFalse(audit["scope"]["scope_complete"])

    def test_discovery_pool_is_stratified_and_deterministic(self) -> None:
        rows = []
        for sector in ("Technology", "Healthcare", "Industrials"):
            for index, cap in enumerate((700_000_000, 3_000_000_000, 12_000_000_000)):
                rows.append(
                    {
                        "symbol": f"{sector[0]}{index}",
                        "country": "US",
                        "exchange": "NASDAQ",
                        "sector": sector,
                        "is_actively_trading": True,
                        "is_common_stock": True,
                        "price": 20,
                        "market_cap": cap,
                        "average_daily_dollar_volume": 10_000_000 + index,
                    }
                )
        first, audit1 = DISCOVERY.build_pool(
            rows,
            min_market_cap=500_000_000,
            max_market_cap=20_000_000_000,
            min_price=5,
            hard_min_adv=1_000_000,
            max_pool=6,
            per_cell=1,
        )
        second, audit2 = DISCOVERY.build_pool(
            list(reversed(rows)),
            min_market_cap=500_000_000,
            max_market_cap=20_000_000_000,
            min_price=5,
            hard_min_adv=1_000_000,
            max_pool=6,
            per_cell=1,
        )
        self.assertEqual([r["symbol"] for r in first], [r["symbol"] for r in second])
        self.assertGreaterEqual(len({r["sector"] for r in first}), 2)
        self.assertEqual(audit1["selection_method"], audit2["selection_method"])

    def test_discovery_partial_layer_uses_liquidity_not_sector_alphabetical_order(self) -> None:
        rows = [
            {
                "symbol": "ALOWV",
                "country": "US",
                "exchange": "NASDAQ",
                "sector": "Aerospace",
                "is_actively_trading": True,
                "is_common_stock": True,
                "price": 20,
                "market_cap": 3_000_000_000,
                "average_daily_dollar_volume": 2_000_000,
            },
            {
                "symbol": "BMID",
                "country": "US",
                "exchange": "NASDAQ",
                "sector": "Banks",
                "is_actively_trading": True,
                "is_common_stock": True,
                "price": 20,
                "market_cap": 3_000_000_000,
                "average_daily_dollar_volume": 20_000_000,
            },
            {
                "symbol": "ZHIGH",
                "country": "US",
                "exchange": "NASDAQ",
                "sector": "Zoology",
                "is_actively_trading": True,
                "is_common_stock": True,
                "price": 20,
                "market_cap": 3_000_000_000,
                "average_daily_dollar_volume": 50_000_000,
            },
        ]
        pool, _ = DISCOVERY.build_pool(
            rows,
            min_market_cap=500_000_000,
            max_market_cap=20_000_000_000,
            min_price=5,
            hard_min_adv=1_000_000,
            max_pool=2,
            per_cell=1,
        )
        self.assertEqual([row["symbol"] for row in pool], ["ZHIGH", "BMID"])

    def test_cli_refuses_listing_only_input_without_candidate_pool(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            listing = root / "listing.jsonl"
            listing.write_text(
                json.dumps(
                    {
                        "symbol": "ONLY",
                        "country": "US",
                        "exchange": "NASDAQ",
                        "is_actively_trading": True,
                        "is_common_stock": True,
                        "price": 20,
                        "market_cap": 2_000_000_000,
                        "average_daily_dollar_volume": 10_000_000,
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            code = SCREEN.main(
                [
                    "--input",
                    str(listing),
                    "--output-dir",
                    str(root / "out"),
                    "--analysis-as-of",
                    "2026-08-22T14:00:00-07:00",
                    "--source-id",
                    "listing-source",
                    "--retrieval-min-market-cap",
                    "500000000",
                    "--retrieval-max-market-cap",
                    "20000000000",
                    "--provider-reported-total",
                    "1",
                    "--pages-fetched",
                    "1",
                    "--pagination-exhausted",
                ]
            )
            self.assertEqual(code, 2)
            audit = json.loads(
                (root / "out" / "broad-screen-audit.json").read_text(encoding="utf-8")
            )
            self.assertEqual(audit["enrichment"]["next_action"], "build_discovery_pool")
            self.assertTrue(audit["enrichment"]["discovery_pool_required"])

    def test_cli_refuses_implicit_retrieval_scope_even_with_evaluable_pool(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            listing = root / "listing.jsonl"
            listing.write_text(
                json.dumps(
                    {
                        "symbol": "READY",
                        "country": "US",
                        "exchange": "NASDAQ",
                        "is_actively_trading": True,
                        "is_common_stock": True,
                        "price": 20,
                        "market_cap": 2_000_000_000,
                        "average_daily_dollar_volume": 10_000_000,
                        "revenue_growth_pct": 12,
                        "eps_growth_pct": 18,
                        "standard_fcf": 100_000_000,
                        "roic_pct": 15,
                        "forward_pe": 15,
                        "fcf_yield_pct": 6,
                        "dilution_pct": 1,
                        "net_debt_to_ebitda": 1,
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            code = SCREEN.main(
                [
                    "--input",
                    str(listing),
                    "--output-dir",
                    str(root / "out"),
                    "--analysis-as-of",
                    "2026-08-22T14:00:00-07:00",
                    "--source-id",
                    "listing-source",
                ]
            )
            self.assertEqual(code, 2)

    def test_insufficient_data_outcome_is_not_completion_ready(self) -> None:
        payload = self.single("ACME")
        row = payload["screening_audit"]["candidate_pool"]["embedded_rows"][0]
        row["decision"]["status"] = "needs_enrichment"
        row["decision"]["resolution"] = "unresolved"
        row["decision"]["selection_eligible"] = False
        row["broad_score"] = None
        row["discovery_evaluable"] = False
        row["fundamental_complete"] = False
        row["enrichment_attempted"] = False
        row["enrichment_resolved"] = False
        row["selection_eligible"] = False

        audit = payload["screening_audit"]
        pool = audit["candidate_pool"]
        audit["selected_symbols"] = []
        audit["deep_dive_plan"] = deep_dive_plan([], payload["analysis_as_of"], maximum=3)
        audit["candidate_pool_status"] = "insufficient_data"
        audit["selection_outcome"] = "insufficient_data"
        pool["decision_counts"] = {"needs_enrichment": 1}
        pool["discovery_evaluable_count"] = 0
        pool["discovery_evaluable_pct"] = 0.0
        pool["fundamental_complete_count"] = 0
        pool["fundamental_complete_pct"] = 0.0
        pool["selection_eligible_count"] = 0
        pool["selected_count"] = 0
        pool["artifact_sha256"] = hashlib.sha256(canonical_jsonl([row])).hexdigest()
        audit["enrichment"] = {
            "status": "pending",
            "next_action": "continue_enrichment",
            "discovery_pool_required": False,
            "attempted_count": 0,
            "resolved_count": 0,
            "unresolved_count": 1,
            "resolution_pct": 0.0,
            "all_rows_resolved": False,
            "queue_count": 1,
            "queue_symbols": ["ACME"],
            "maximum_attempts": 60,
            "candidate_pool_exhaustion_declared": False,
            "candidate_pool_exhausted": False,
            "candidate_pool_covers_in_scope": True,
            "candidate_pool_scope_verified": True,
            "conclusion_scope": "full_listing_universe",
        }
        payload["screening_funnel"]["discovery_evaluable_count"] = 0
        payload["screening_funnel"]["deep_dive_selected_count"] = 0
        payload["screening_funnel"]["preflight_passed_count"] = 0
        payload["screening_funnel"]["deep_dive_completed_count"] = 0
        payload["run_metadata"]["status"] = "partial"
        payload["run_metadata"]["selected_symbols"] = []
        payload["run_metadata"]["unprocessed_candidates"] = []
        payload["candidates"] = []

        _, contract = CONTRACT.validate_and_normalize_snapshot(payload, artifact_root=ASSETS_DIR)
        self.assertTrue(contract["screening_audit_valid"])
        self.assertFalse(contract["screening_completion_ready"])
        self.assertEqual(contract["selection_outcome"], "insufficient_data")


class RegressionV33Tests(FixtureMixin, unittest.TestCase):
    def _run_layered(
        self,
        universe_rows: list[dict],
        candidate_rows: list[dict],
        *,
        exhausted: bool = False,
        mode: str = "liquidity_stratified_estimates",
    ):
        return SCREEN.run_layered(
            universe_rows,
            candidate_rows,
            dict(SCREEN.DEFAULTS),
            analysis_as_of="2026-08-22T14:00:00-07:00",
            universe_source_ids=["listing-source"],
            candidate_source_ids=["estimate-source"],
            candidate_generation_mode=mode,
            retrieval_min_market_cap=500_000_000,
            retrieval_max_market_cap=20_000_000_000,
            candidate_pool_exhausted=exhausted,
            provider_reported_total=len(universe_rows),
            pages_fetched=1,
            pagination_exhausted=True,
        )

    def test_twenty_one_attempts_and_six_evaluable_do_not_override_unresolved_queue(self) -> None:
        rows: list[dict] = []
        for index in range(6):
            rows.append(
                {
                    "symbol": f"FAIL{index}",
                    "country": "US",
                    "exchange": "NASDAQ",
                    "sector": "Technology",
                    "is_actively_trading": True,
                    "is_common_stock": True,
                    "price": 20,
                    "market_cap": 3_000_000_000,
                    "average_daily_dollar_volume": 20_000_000,
                    "revenue_growth_pct": 1,
                    "eps_growth_pct": 2,
                    "forward_pe": 80,
                    "analyst_count": 5,
                    "enrichment_attempted": True,
                }
            )
        for index in range(15):
            rows.append(
                {
                    "symbol": f"WAIT{index}",
                    "country": "US",
                    "exchange": "NYSE",
                    "sector": "Industrials",
                    "is_actively_trading": True,
                    "is_common_stock": True,
                    "price": 25,
                    "market_cap": 4_000_000_000,
                    "average_daily_dollar_volume": 15_000_000,
                    "revenue_growth_pct": 12,
                    "analyst_count": 4,
                    "enrichment_attempted": True,
                }
            )
        _, decisions, audit, selected, queue = self._run_layered(rows, rows, exhausted=False)
        self.assertEqual(audit["enrichment"]["attempted_count"], 21)
        self.assertEqual(audit["candidate_pool"]["discovery_evaluable_count"], 6)
        self.assertEqual(audit["enrichment"]["unresolved_count"], 15)
        self.assertEqual(len(queue), 15)
        self.assertEqual(selected, [])
        self.assertEqual(audit["candidate_pool_status"], "insufficient_data")
        self.assertEqual(audit["selection_outcome"], "insufficient_data")
        self.assertFalse(audit["enrichment"]["all_rows_resolved"])
        self.assertFalse(audit["enrichment"]["candidate_pool_exhausted"])
        self.assertTrue(any(row["decision"]["status"] == "needs_enrichment" for row in decisions))

    def test_high_growth_cyclicals_advance_to_mid_cycle_deep_dive(self) -> None:
        rows = [
            {
                "symbol": "MODX",
                "country": "US",
                "exchange": "NYSE",
                "sector": "Industrials",
                "is_actively_trading": True,
                "is_common_stock": True,
                "price": 120,
                "market_cap": 6_000_000_000,
                "average_daily_dollar_volume": 30_000_000,
                "revenue_growth_pct": 24.38,
                "eps_growth_pct": 46.28,
                "forward_pe": 25.86,
                "analyst_count": 6,
                "cyclicality_score": 4,
            },
            {
                "symbol": "MKSX",
                "country": "US",
                "exchange": "NASDAQ",
                "sector": "Technology",
                "is_actively_trading": True,
                "is_common_stock": True,
                "price": 150,
                "market_cap": 10_000_000_000,
                "average_daily_dollar_volume": 25_000_000,
                "revenue_growth_pct": 20.08,
                "eps_growth_pct": 23.17,
                "forward_pe": 21.25,
                "analyst_count": 9,
                "cyclicality_score": 4,
            },
        ]
        _, decisions, audit, selected, _ = self._run_layered(rows, rows, exhausted=False)
        self.assertEqual(set(selected), {"MODX", "MKSX"})
        self.assertEqual(audit["candidate_pool_status"], "sufficient_pending_enrichment")
        for row in decisions:
            self.assertEqual(row["decision"]["preselection_status"], "sector_review_required")
            self.assertIn(
                "mid_cycle_normalization_required", row["decision"]["deep_dive_requirements"]
            )
            self.assertTrue(row["selection_eligible"])
            self.assertIsNotNone(row["broad_score"])

    def test_growth_guidelines_are_not_mechanical_cutoffs(self) -> None:
        row = {
            "symbol": "BFAMX",
            "country": "US",
            "exchange": "NYSE",
            "sector": "Consumer Defensive",
            "is_actively_trading": True,
            "is_common_stock": True,
            "price": 100,
            "market_cap": 8_000_000_000,
            "average_daily_dollar_volume": 20_000_000,
            "revenue_growth_pct": 5.5,
            "eps_growth_pct": 15.92,
            "forward_pe": 14.26,
            "analyst_count": 5,
            "cyclicality_score": 2,
        }
        _, decisions, _, selected, _ = self._run_layered([row], [row], exhausted=False)
        self.assertEqual(selected, ["BFAMX"])
        self.assertEqual(decisions[0]["decision"]["status"], "selected")
        self.assertIn(
            "revenue_growth_below_guideline", decisions[0]["decision"]["guideline_misses"]
        )
        self.assertEqual(decisions[0]["decision"]["screen_fail_reasons"], [])

    def test_enrichment_queue_prioritizes_garp_information_value_over_liquidity(self) -> None:
        rows = [
            {
                "symbol": "GARP",
                "country": "US",
                "exchange": "NASDAQ",
                "sector": "Technology",
                "is_actively_trading": True,
                "is_common_stock": True,
                "price": 50,
                "market_cap": 5_000_000_000,
                "average_daily_dollar_volume": 5_000_000,
                "revenue_growth_pct": 18,
                "eps_growth_pct": 25,
                "forward_pe": 22,
                "analyst_count": 1,
                "enrichment_attempted": True,
            },
            {
                "symbol": "BASE",
                "country": "US",
                "exchange": "NYSE",
                "sector": "Materials",
                "is_actively_trading": True,
                "is_common_stock": True,
                "price": 20,
                "market_cap": 5_000_000_000,
                "average_daily_dollar_volume": 200_000_000,
                "revenue_growth_pct": 100,
                "eps_growth_pct": 800,
                "forward_pe": 3474,
                "analyst_count": 1,
                "enrichment_attempted": True,
            },
        ]
        _, _, audit, _, queue = self._run_layered(rows, rows, exhausted=False)
        self.assertEqual([row["symbol"] for row in queue], ["GARP", "BASE"])
        self.assertEqual(audit["enrichment"]["next_action"], "enrich_queue")

    def test_full_cap_range_without_pagination_evidence_is_not_scope_complete(self) -> None:
        row = {
            "symbol": "READY",
            "country": "US",
            "exchange": "NASDAQ",
            "is_actively_trading": True,
            "is_common_stock": True,
            "price": 20,
            "market_cap": 2_000_000_000,
            "average_daily_dollar_volume": 10_000_000,
            "revenue_growth_pct": 12,
            "eps_growth_pct": 18,
            "forward_pe": 15,
            "analyst_count": 4,
        }
        _, _, audit, _, _ = SCREEN.run_layered(
            [row],
            [row],
            dict(SCREEN.DEFAULTS),
            analysis_as_of="2026-08-22T14:00:00-07:00",
            universe_source_ids=["u"],
            candidate_source_ids=["e"],
            candidate_generation_mode="liquidity_stratified_estimates",
            retrieval_min_market_cap=500_000_000,
            retrieval_max_market_cap=20_000_000_000,
        )
        self.assertFalse(audit["scope"]["scope_complete"])
        self.assertIn("executed_scope_enumeration_not_verified", audit["scope"]["reasons"])

    def test_unavailable_after_enrichment_requires_reason_and_sources(self) -> None:
        base = {
            "symbol": "MISSING",
            "country": "US",
            "exchange": "NASDAQ",
            "sector": "Technology",
            "is_actively_trading": True,
            "is_common_stock": True,
            "price": 20,
            "market_cap": 2_000_000_000,
            "average_daily_dollar_volume": 10_000_000,
            "revenue_growth_pct": 12,
            "analyst_count": 4,
            "enrichment_attempted": True,
            "enrichment_exhausted": True,
            "enrichment_exhaustion_reason": "forward EPS was not published by available providers",
        }
        decisions, _, _, _ = SCREEN.run(
            [base],
            dict(SCREEN.DEFAULTS),
            analysis_as_of="2026-08-22T14:00:00-07:00",
            source_ids=["e"],
        )
        self.assertEqual(decisions[0]["decision"]["status"], "needs_enrichment")
        evidenced = dict(base)
        evidenced["enrichment_source_ids"] = ["e"]
        decisions, _, _, _ = SCREEN.run(
            [evidenced],
            dict(SCREEN.DEFAULTS),
            analysis_as_of="2026-08-22T14:00:00-07:00",
            source_ids=["e"],
        )
        self.assertEqual(decisions[0]["decision"]["status"], "unavailable_after_enrichment")
        self.assertEqual(decisions[0]["decision"]["resolution"], "resolved")

    def test_stale_market_valuation_source_blocks_market_context(self) -> None:
        payload = self.single("ACME")
        for source in payload["global_sources"]:
            if source["id"] == "market-valuation-20260822":
                source["published_at"] = "2026-05-28T00:00:00-04:00"
                source["data_as_of"] = "2026-05-28T00:00:00-04:00"
        _, contract = CONTRACT.validate_and_normalize_snapshot(payload, artifact_root=ASSETS_DIR)
        self.assertFalse(contract["market_context_valid"])
        self.assertTrue(
            any(
                "market_forward_pe lacks a source within" in reason
                for reason in contract["review_reasons"]
            )
        )

    def test_tampered_no_candidates_with_unresolved_queue_is_rejected(self) -> None:
        payload = self.single("SCREEN")
        payload["candidates"] = []
        audit = payload["screening_audit"]
        row = audit["candidate_pool"]["embedded_rows"][0]
        row["decision"]["status"] = "needs_enrichment"
        row["decision"]["resolution"] = "unresolved"
        row["decision"]["selection_eligible"] = False
        row["enrichment_resolved"] = False
        row["selection_eligible"] = False
        row["discovery_evaluable"] = False
        row["broad_score"] = None
        audit["candidate_pool"]["decision_counts"] = {"needs_enrichment": 1}
        audit["candidate_pool"]["discovery_evaluable_count"] = 0
        audit["candidate_pool"]["discovery_evaluable_pct"] = 0.0
        audit["candidate_pool"]["selection_eligible_count"] = 0
        audit["candidate_pool"]["artifact_sha256"] = hashlib.sha256(
            canonical_jsonl([row])
        ).hexdigest()
        audit["candidate_pool_status"] = "no_qualifying_candidates"
        audit["selection_outcome"] = "no_candidates"
        audit["enrichment"].update(
            {
                "status": "pending",
                "next_action": "enrich_queue",
                "resolved_count": 0,
                "unresolved_count": 1,
                "resolution_pct": 0.0,
                "all_rows_resolved": False,
                "candidate_pool_exhausted": False,
                "queue_count": 1,
                "queue_symbols": ["SCREEN"],
            }
        )
        payload["run_metadata"]["status"] = "complete"
        _, contract = CONTRACT.validate_and_normalize_snapshot(payload, artifact_root=ASSETS_DIR)
        self.assertFalse(contract["screening_audit_valid"])
        self.assertFalse(contract["screening_completion_ready"])
        self.assertTrue(
            any(
                "no_qualifying_candidates" in reason or "completion" in reason
                for reason in contract["review_reasons"]
            )
        )

    def test_runtime_fingerprint_rejects_stale_cached_skill(self) -> None:
        payload = self.single("ACME")
        payload["runtime"]["contract_revision"] = "3.2"
        with self.assertRaises(CONTRACT.ContractError):
            CONTRACT.validate_and_normalize_snapshot(payload, artifact_root=ASSETS_DIR)

    def test_reverse_engineered_numerator_does_not_replace_driver_bridge(self) -> None:
        payload = self.single("ACME")
        candidate = payload["candidates"][0]
        # Keep metric_numerator / shares tied to consensus, but break the
        # independent operating-driver model. This was the v3.2 circular bug.
        candidate["forecast_bridge"]["periods"]["year_2"]["drivers"]["operating_margin_pct"] = 25.0
        report = self.evaluate(payload)
        row = report["review_required"][0]
        self.assertFalse(row["valuation"]["forecast_bridge_valid"])
        self.assertLessEqual(row["data_quality_score"], 60)
        self.assertTrue(
            any("driver-derived forecast" in reason for reason in row["review_reasons"])
        )

    def test_adjusted_bridge_must_reconcile_gaap_eps_and_adjustments(self) -> None:
        payload = self.single("ACME")
        candidate = payload["candidates"][0]
        for key in ("current", "year_2", "year_3"):
            candidate["valuation_case"]["periods"][key]["metric_basis"] = "company_adjusted"
        for key, gaap_eps in (("year_2", 4.0), ("year_3", 4.8)):
            bridge = candidate["forecast_bridge"]["periods"][key]
            bridge["metric_basis"] = "company_adjusted"
            drivers = bridge["drivers"]
            shares = float(drivers["diluted_shares"])
            tax_rate = float(drivers["tax_rate_pct"]) / 100.0
            net_interest_income = float(drivers.get("net_interest_income", 0.0))
            gaap_net_income = gaap_eps * shares
            pretax_income = gaap_net_income / (1.0 - tax_rate)
            drivers["operating_margin_pct"] = (
                (pretax_income - net_interest_income) / float(drivers["revenue"]) * 100.0
            )
            # Deliberately wrong: reconciliation requires $0.20/share.
            drivers["after_tax_adjustments"] = 0.05 * shares
        candidate["gaap_reconciliation"] = {
            "periods": {
                "current": {
                    "gaap_metric": 2.8,
                    "adjustments": [{"label": "Amortization", "amount": 0.2, "recurring": True}],
                    "source_ids": ["acme-10q", "analyst-model"],
                },
                "year_2": {
                    "gaap_metric": 4.0,
                    "adjustments": [{"label": "Amortization", "amount": 0.2, "recurring": True}],
                    "source_ids": ["consensus-20260822", "analyst-model"],
                },
                "year_3": {
                    "gaap_metric": 4.8,
                    "adjustments": [{"label": "Amortization", "amount": 0.2, "recurring": True}],
                    "source_ids": ["consensus-20260822", "analyst-model"],
                },
            }
        }
        for peer in candidate["peers"]:
            peer["metric_basis"] = "company_adjusted"
        candidate["valuation_case"]["peer_median_multiple"]["metric_basis"] = "company_adjusted"
        report = self.evaluate(payload)
        row = report["review_required"][0]
        self.assertFalse(row["valuation"]["forecast_bridge_valid"])
        self.assertTrue(
            any("adjusted forecast bridge" in reason for reason in row["review_reasons"])
        )

    def test_ordinary_cash_is_normalized_from_cash_and_equivalents(self) -> None:
        payload = self.single("ACME")
        candidate = payload["candidates"][0]
        cash = candidate["financials"]["cash_classification"]
        cash["cash_and_equivalents"] = cash.pop("corporate_cash")
        report = self.evaluate(payload)
        row = report["ranked_candidates"][0]
        self.assertEqual(row["financial_metrics"]["corporate_cash"], 160_000_000)
        self.assertEqual(
            row["financial_metrics"]["cash_classification_method"],
            "derived_from_reported_cash_and_equivalents",
        )

    def test_peak_profit_risk_forces_normalization_even_with_low_cyclicality_score(self) -> None:
        payload = self.single("ACME")
        candidate = payload["candidates"][0]
        candidate["identity"]["symbol"] = "PEAKX"
        candidate["cyclicality"].update(
            {
                "score": 2,
                "position": "late_cycle",
                "peak_profit_risk": True,
                "normalization_required": False,
                "normalization": None,
            }
        )
        report = self.evaluate(payload)
        row = report["review_required"][0]
        self.assertTrue(row["cyclicality"]["normalization_required"])
        self.assertFalse(row["cyclicality"]["normalization_valid"])
        self.assertLessEqual(row["data_quality_score"], 65)

    def test_biopharma_alias_triggers_loe_stress(self) -> None:
        payload = self.single("ACME")
        candidate = payload["candidates"][0]
        candidate["identity"]["symbol"] = "BIOALIAS"
        candidate["sector_profile"] = {
            "type": "biopharma",
            "kpis": {
                "top_product_revenue": 800_000_000,
                "total_revenue": 1_000_000_000,
                "nearest_material_loe_date": "2029-12-31",
                "source_ids": ["acme-10q", "acme-ir"],
            },
        }
        report = self.evaluate(payload)
        row = report["ranked_candidates"][0]
        self.assertEqual(row["sector_profile"]["type"], "commercial_biopharma")
        self.assertTrue(row["sector_profile"]["type_normalized"])
        self.assertEqual(row["sector_profile"]["top_product_revenue_pct"], 80.0)
        self.assertEqual(
            {item["multiple"] for item in row["sector_profile"]["loe_stress_scenarios"]}, {6.0, 8.0}
        )

    def test_missing_roic_and_ebitda_evidence_caps_quality(self) -> None:
        payload = self.single("ACME")
        candidate = payload["candidates"][0]
        candidate["evidence"].pop("financials.roic_pct", None)
        candidate["evidence"].pop("financials.ebitda_ttm", None)
        for source in candidate["sources"]:
            source["supports"] = [
                field
                for field in source.get("supports", [])
                if field not in {"financials.roic_pct", "financials.ebitda_ttm"}
            ]
        report = self.evaluate(payload)
        row = report["review_required"][0]
        self.assertLessEqual(row["data_quality_score"], 65)
        self.assertFalse(
            row["data_quality_details"]["roic_ebitda_evidence_verified"]["evidence_ok"]
        )

    def test_ttm_cash_flow_periods_require_source_ids(self) -> None:
        payload = self.single("ACME")
        candidate = payload["candidates"][0]
        candidate["financials"]["cash_flow_periods"][0]["source_ids"] = []
        report = self.evaluate(payload)
        row = report["review_required"][0]
        self.assertLessEqual(row["data_quality_score"], 65)
        self.assertTrue(any("cash-flow period" in reason for reason in row["review_reasons"]))

    def test_valid_bounded_pool_can_publish_final_ranking_scope(self) -> None:
        universe = [
            {
                "symbol": "ACME",
                "country": "US",
                "exchange": "NASDAQ",
                "sector": "Technology",
                "is_actively_trading": True,
                "is_common_stock": True,
                "price": 40,
                "market_cap": 5_000_000_000,
                "average_daily_dollar_volume": 45_000_000,
            },
            {
                "symbol": "OTHER",
                "country": "US",
                "exchange": "NYSE",
                "sector": "Industrials",
                "is_actively_trading": True,
                "is_common_stock": True,
                "price": 30,
                "market_cap": 3_000_000_000,
                "average_daily_dollar_volume": 20_000_000,
            },
        ]
        pool = [
            {
                **universe[0],
                "revenue_growth_pct": 14,
                "eps_growth_pct": 22,
                "forward_pe": 13.33,
                "analyst_count": 8,
            }
        ]
        discovery_audit = {
            "selection_method": "sector_market_cap_stratified_liquidity",
            "input_row_count": 2,
            "selected_count": 1,
            "selected_symbols": ["ACME"],
            "source_ids": ["listing-source"],
            "artifact_path": "discovery-pool.jsonl",
            "artifact_sha256": "abc123",
        }
        _, _, audit, selected, queue = SCREEN.run_layered(
            universe,
            pool,
            dict(SCREEN.DEFAULTS),
            analysis_as_of="2026-08-22T14:00:00-07:00",
            universe_source_ids=["listing-source"],
            candidate_source_ids=["estimate-source"],
            candidate_generation_mode="liquidity_stratified_estimates",
            retrieval_min_market_cap=500_000_000,
            retrieval_max_market_cap=20_000_000_000,
            candidate_pool_exhausted=True,
            provider_reported_total=2,
            pages_fetched=1,
            pagination_exhausted=True,
            discovery_audit=discovery_audit,
        )
        self.assertEqual(selected, ["ACME"])
        self.assertEqual(queue, [])
        self.assertEqual(audit["candidate_pool_status"], "sufficient")
        self.assertEqual(audit["candidate_pool"]["coverage_scope"], "stratified_discovery_pool")
        self.assertFalse(audit["candidate_pool"]["listing_coverage_complete"])
        self.assertTrue(audit["candidate_pool"]["coverage_complete"])
        self.assertTrue(audit["enrichment"]["candidate_pool_exhausted"])

    def test_bounded_no_candidates_conclusion_is_scoped(self) -> None:
        universe = [
            {
                "symbol": "FAIL",
                "country": "US",
                "exchange": "NASDAQ",
                "sector": "Technology",
                "is_actively_trading": True,
                "is_common_stock": True,
                "price": 20,
                "market_cap": 2_000_000_000,
                "average_daily_dollar_volume": 10_000_000,
            },
            {
                "symbol": "OTHER",
                "country": "US",
                "exchange": "NYSE",
                "sector": "Industrials",
                "is_actively_trading": True,
                "is_common_stock": True,
                "price": 30,
                "market_cap": 3_000_000_000,
                "average_daily_dollar_volume": 20_000_000,
            },
        ]
        pool = [
            {
                **universe[0],
                "revenue_growth_pct": -5,
                "eps_growth_pct": -10,
                "forward_pe": 80,
                "analyst_count": 5,
            }
        ]
        discovery_audit = {
            "selection_method": "sector_market_cap_stratified_liquidity",
            "input_row_count": 2,
            "selected_count": 1,
            "selected_symbols": ["FAIL"],
            "source_ids": ["listing-source"],
            "artifact_path": "discovery-pool.jsonl",
            "artifact_sha256": "abc123",
        }
        _, _, audit, selected, queue = SCREEN.run_layered(
            universe,
            pool,
            dict(SCREEN.DEFAULTS),
            analysis_as_of="2026-08-22T14:00:00-07:00",
            universe_source_ids=["listing-source"],
            candidate_source_ids=["estimate-source"],
            candidate_generation_mode="liquidity_stratified_estimates",
            retrieval_min_market_cap=500_000_000,
            retrieval_max_market_cap=20_000_000_000,
            candidate_pool_exhausted=True,
            provider_reported_total=2,
            pages_fetched=1,
            pagination_exhausted=True,
            discovery_audit=discovery_audit,
        )
        self.assertEqual(selected, [])
        self.assertEqual(queue, [])
        self.assertEqual(audit["candidate_pool_status"], "no_qualifying_candidates_in_bounded_pool")
        self.assertEqual(audit["selection_outcome"], "no_candidates_in_bounded_pool")
        self.assertEqual(audit["conclusion_scope"], "stratified_discovery_pool")

    def test_runtime_version_flags_are_consistent_across_scripts(self) -> None:
        expected = VERSION.runtime_metadata()
        for module in (
            SCREEN,
            PROVIDER_POOL,
            DISCOVERY,
            NORMALIZER,
            EVALUATOR,
            RUN_STATE,
            CONTRACT,
            PREPUBLISH,
            BUNDLER,
        ):
            self.assertEqual(module.runtime_metadata(), expected)

    def test_markdown_surfaces_broad_stage_review_and_screened_out_rows(self) -> None:
        report = self.evaluate(self.payload)
        report["ranking_status"] = "provisional"
        report["broad_screen"] = {
            "counts": {
                "selected": 0,
                "deferred_by_budget": 0,
                "review_required": 1,
                "screened_out": 1,
                "excluded": 0,
                "unavailable_after_enrichment": 0,
            },
            "selected": [],
            "deferred_by_budget": [],
            "review_required": [
                {
                    "symbol": "MODX",
                    "country": "US",
                    "company_name": "Modine-like Cyclical",
                    "status": "sector_review_required",
                    "review_reasons": ["mid_cycle_normalization_required"],
                    "deep_dive_requirements": ["mid_cycle_normalization_required"],
                    "metrics": {"forward_pe": 25.86, "per_share_growth_pct": 46.28},
                }
            ],
            "screened_out": [
                {
                    "symbol": "FAILX",
                    "country": "US",
                    "company_name": "Extreme Valuation",
                    "status": "screened_out",
                    "screen_fail_reasons": ["extreme_forward_valuation"],
                    "metrics": {"forward_pe": 80.0, "per_share_growth_pct": 2.0},
                }
            ],
            "excluded": [],
            "unavailable_after_enrichment": [],
        }
        markdown = EVALUATOR.render_markdown(report, language="ja")
        self.assertIn("MODX", markdown)
        self.assertIn("mid_cycle_normalization_required", markdown)
        self.assertIn("FAILX", markdown)
        self.assertIn("extreme_forward_valuation", markdown)

    def test_no_candidates_requires_candidate_pool_coverage_of_all_in_scope_symbols(self) -> None:
        universe = [
            {
                "symbol": "FAILA",
                "country": "US",
                "exchange": "NASDAQ",
                "sector": "Technology",
                "is_actively_trading": True,
                "is_common_stock": True,
                "price": 20,
                "market_cap": 2_000_000_000,
                "average_daily_dollar_volume": 10_000_000,
            },
            {
                "symbol": "UNSEEN",
                "country": "US",
                "exchange": "NYSE",
                "sector": "Industrials",
                "is_actively_trading": True,
                "is_common_stock": True,
                "price": 25,
                "market_cap": 3_000_000_000,
                "average_daily_dollar_volume": 12_000_000,
            },
        ]
        pool = [
            {
                **universe[0],
                "revenue_growth_pct": 1,
                "eps_growth_pct": 2,
                "forward_pe": 80,
                "analyst_count": 5,
            }
        ]
        _, _, audit, selected, _ = self._run_layered(universe, pool, exhausted=True)
        self.assertEqual(selected, [])
        self.assertTrue(audit["candidate_pool"]["coverage_complete"])
        self.assertFalse(audit["candidate_pool"]["listing_coverage_complete"])
        self.assertEqual(audit["candidate_pool"]["in_scope_missing_symbols"], ["UNSEEN"])
        self.assertEqual(audit["candidate_pool"]["coverage_scope"], "stratified_discovery_pool")
        self.assertTrue(audit["enrichment"]["candidate_pool_exhaustion_declared"])
        self.assertTrue(audit["enrichment"]["candidate_pool_exhausted"])
        self.assertEqual(audit["candidate_pool_status"], "no_qualifying_candidates_in_bounded_pool")
        self.assertEqual(audit["enrichment"]["next_action"], "publish_no_candidates")

    def test_band_audit_must_cover_requested_market_cap_range_without_gaps(self) -> None:
        row = {
            "symbol": "READY",
            "country": "US",
            "exchange": "NASDAQ",
            "sector": "Technology",
            "is_actively_trading": True,
            "is_common_stock": True,
            "price": 20,
            "market_cap": 2_000_000_000,
            "average_daily_dollar_volume": 10_000_000,
            "revenue_growth_pct": 12,
            "eps_growth_pct": 18,
            "forward_pe": 15,
            "analyst_count": 4,
        }
        _, _, audit, _, _ = SCREEN.run_layered(
            [row],
            [row],
            dict(SCREEN.DEFAULTS),
            analysis_as_of="2026-08-22T14:00:00-07:00",
            universe_source_ids=["u"],
            candidate_source_ids=["e"],
            candidate_generation_mode="full_universe_fundamentals",
            retrieval_min_market_cap=500_000_000,
            retrieval_max_market_cap=20_000_000_000,
            candidate_pool_exhausted=True,
            band_audit=[
                {
                    "min_market_cap": 500_000_000,
                    "max_market_cap": 1_000_000_000,
                    "rows_fetched": 1,
                    "provider_exhausted": True,
                },
                {
                    "min_market_cap": 2_000_000_000,
                    "max_market_cap": 20_000_000_000,
                    "rows_fetched": 1,
                    "provider_exhausted": True,
                },
            ],
        )
        enum = audit["scope"]["enumeration"]
        self.assertTrue(enum["bands_well_formed"])
        self.assertFalse(enum["bands_cover_requested_range"])
        self.assertFalse(enum["bands_verified"])
        self.assertFalse(audit["scope"]["scope_complete"])


class RegressionV34Tests(FixtureMixin, unittest.TestCase):
    ANALYSIS_AS_OF = "2026-08-22T14:00:00-07:00"

    def valid_discovery_row(self, symbol: str = "VALID") -> dict:
        return {
            "symbol": symbol,
            "country": "US",
            "exchange": "NASDAQ",
            "sector": "Technology",
            "is_actively_trading": True,
            "is_common_stock": True,
            "price": 40.0,
            "market_cap": 3_500_000_000,
            "average_daily_dollar_volume": 12_000_000.0,
            "average_daily_dollar_volume_method": "provider_average_dollar_volume",
            "average_volume_period_days": 20,
            "liquidity_source_ids": ["listing-source"],
            "revenue_growth_pct": 14.0,
            "eps_growth_pct": 22.0,
            "standard_fcf": 250_000_000.0,
            "roic_pct": 18.0,
            "forward_pe": 16.0,
            "forward_eps": 2.5,
            "forward_pe_period": "FY1",
            "forward_fiscal_year": "FY2027",
            "forward_period_end": "2027-06-30",
            "forward_estimate_as_of": self.ANALYSIS_AS_OF,
            "forward_estimate_source_ids": ["estimate-source"],
            "forward_metric_origin": "computed_from_price_and_fy1_eps",
            "analyst_count": 6,
            "dilution_pct": 1.0,
            "net_debt_to_ebitda": 1.0,
            "fcf_yield_pct": 6.0,
        }

    def run_original(
        self, universe: list[dict], pool: list[dict], *, config=None, exhausted=False, **kwargs
    ):
        cfg = dict(SCREEN.DEFAULTS)
        if config:
            cfg.update(config)
        return ORIGINAL_SCREEN_RUN_LAYERED(
            universe,
            pool,
            cfg,
            analysis_as_of=self.ANALYSIS_AS_OF,
            universe_source_ids=["listing-source"],
            candidate_source_ids=["estimate-source"],
            candidate_generation_mode=kwargs.pop("mode", "full_universe_fundamentals"),
            retrieval_min_market_cap=kwargs.pop("retrieval_min_market_cap", 500_000_000),
            retrieval_max_market_cap=kwargs.pop("retrieval_max_market_cap", 20_000_000_000),
            retrieval_scope_explicit=True,
            candidate_pool_exhausted=exhausted,
            provider_reported_total=len(universe),
            pages_fetched=1,
            pagination_exhausted=True,
            **kwargs,
        )

    def test_single_session_volume_is_not_accepted_as_addv(self) -> None:
        row = self.valid_discovery_row("SINGLE")
        row["average_daily_dollar_volume_method"] = "price_x_single_session_volume"
        row["average_volume_period_days"] = 1
        row["average_volume"] = 600_000
        _, decisions, _, selected, queue = self.run_original([row], [row], exhausted=False)
        self.assertEqual(selected, [])
        self.assertEqual(decisions[0]["decision"]["status"], "needs_enrichment")
        self.assertIn(
            "single_session_volume_not_valid_for_addv",
            decisions[0]["decision"]["blocking_review_reasons"],
        )
        self.assertEqual([item["symbol"] for item in queue], ["SINGLE"])

    def test_twenty_day_provider_average_liquidity_is_accepted(self) -> None:
        row = self.valid_discovery_row("AVG20")
        _, decisions, audit, selected, queue = self.run_original([row], [row], exhausted=True)
        self.assertEqual(selected, ["AVG20"])
        self.assertEqual(queue, [])
        self.assertTrue(decisions[0]["metrics"]["liquidity_valid_for_screen"])
        self.assertEqual(decisions[0]["metrics"]["average_volume_period_days"], 20)
        self.assertEqual(audit["candidate_pool_status"], "sufficient")

    def test_generic_forward_pe_without_ntm_or_fy1_metadata_is_rejected(self) -> None:
        row = self.valid_discovery_row("NOHORIZON")
        for key in (
            "forward_eps",
            "forward_pe_period",
            "forward_fiscal_year",
            "forward_period_end",
            "forward_estimate_as_of",
            "forward_estimate_source_ids",
        ):
            row.pop(key, None)
        _, decisions, _, selected, queue = self.run_original([row], [row], exhausted=False)
        self.assertEqual(selected, [])
        reasons = decisions[0]["decision"]["blocking_review_reasons"]
        self.assertIn("forward_pe_period_must_be_ntm_or_fy1", reasons)
        self.assertIn("current_forward_eps_unavailable_or_non_positive", reasons)
        self.assertEqual([item["symbol"] for item in queue], ["NOHORIZON"])

    def test_outer_year_frmi_like_pe_is_not_a_current_forward_multiple(self) -> None:
        row = self.valid_discovery_row("FRMIX")
        row.update(
            {
                "forward_pe": 4.0,
                "forward_eps": 10.0,
                "forward_pe_period": "FY1",
                "forward_fiscal_year": "FY2030",
                "forward_period_end": "2030-12-31",
                "forward_eps_low": -0.23,
                "forward_eps_high": 15.99,
                "analyst_count": 2,
                "operating_stage": "pre_operating",
            }
        )
        _, decisions, _, selected, queue = self.run_original([row], [row], exhausted=False)
        self.assertEqual(selected, [])
        reasons = decisions[0]["decision"]["blocking_review_reasons"]
        self.assertIn("current_forward_period_is_not_fy1_or_ntm", reasons)
        self.assertIn("forward_eps_range_crosses_zero", reasons)
        self.assertIn("pre_operating_company_not_pe_evaluable", reasons)
        self.assertEqual([item["symbol"] for item in queue], ["FRMIX"])

    def test_executed_scope_cannot_replace_default_user_requested_scope(self) -> None:
        row = self.valid_discovery_row("BAND")
        _, _, audit, _, _ = self.run_original(
            [row],
            [row],
            config={"min_market_cap": 3_000_000_000, "max_market_cap": 4_000_000_000},
            retrieval_min_market_cap=3_000_000_000,
            retrieval_max_market_cap=4_000_000_000,
            exhausted=True,
            scope_reduction_reason="bounded automatically to finish within the execution budget",
        )
        self.assertEqual(audit["scope"]["user_requested_scope"]["min_market_cap"], 500_000_000)
        self.assertEqual(audit["scope"]["user_requested_scope"]["max_market_cap"], 20_000_000_000)
        self.assertEqual(audit["scope"]["executed_scope"]["min_market_cap"], 3_000_000_000)
        self.assertEqual(audit["scope"]["executed_scope"]["max_market_cap"], 4_000_000_000)
        self.assertFalse(audit["scope"]["user_requested_scope_complete"])
        self.assertIn("executed_scope_narrower_than_user_request", audit["scope"]["reasons"])
        self.assertFalse(audit["scope"]["scope_override_authorized"])

    def test_next_action_requires_every_selected_symbol_without_user_choice(self) -> None:
        state = {
            "status": "partial",
            "screening_audit": {
                "candidate_pool_status": "sufficient",
                "selection_outcome": "selected",
                "selected_symbols": ["JOYY", "MWH", "FSM", "EXK", "FRMI"],
                "enrichment": {"queue_count": 0, "queue_symbols": [], "all_rows_resolved": True},
            },
            "candidates": {
                "JOYY": {"stage": "verified"},
                "MWH": {"stage": "verified"},
            },
            "unprocessed_candidates": ["EXK", "FRMI", "FSM"],
        }
        action = RUN_STATE._next_action_payload(state)
        self.assertEqual(action["action"], "complete_all_selected_deep_dives")
        self.assertEqual(action["symbols"], ["EXK", "FRMI", "FSM"])
        self.assertFalse(action["user_confirmation_required"])
        self.assertIn("Never ask the user", action["instruction"])
        self.assertIn("rerunning the deterministic broad screen", action["instruction"])

    def test_normalizer_emits_auditable_fy1_and_resolves_valid_row(self) -> None:
        listing = self.valid_discovery_row("VALIDFY1")
        listing.pop("forward_pe", None)
        listing.pop("forward_eps", None)
        listing.pop("forward_pe_period", None)
        listing.pop("forward_fiscal_year", None)
        listing.pop("forward_period_end", None)
        listing.pop("forward_estimate_as_of", None)
        listing.pop("forward_estimate_source_ids", None)
        listing.pop("forward_metric_origin", None)
        estimates = [
            {
                "symbol": "VALIDFY1",
                "country": "US",
                "date": "2026-12-31",
                "fiscalYear": "2026",
                "epsAvg": 2.5,
                "epsLow": 2.3,
                "epsHigh": 2.7,
                "revenueAvg": 1_000_000_000,
                "numAnalystsEps": 5,
                "numAnalystsRevenue": 5,
            },
            {
                "symbol": "VALIDFY1",
                "country": "US",
                "date": "2027-12-31",
                "fiscalYear": "2027",
                "epsAvg": 3.0,
                "epsLow": 2.8,
                "epsHigh": 3.2,
                "revenueAvg": 1_150_000_000,
                "numAnalystsEps": 5,
                "numAnalystsRevenue": 5,
            },
            {
                "symbol": "VALIDFY1",
                "country": "US",
                "date": "2028-12-31",
                "fiscalYear": "2028",
                "epsAvg": 3.6,
                "epsLow": 3.3,
                "epsHigh": 3.9,
                "revenueAvg": 1_320_000_000,
                "numAnalystsEps": 4,
                "numAnalystsRevenue": 4,
            },
        ]
        row = NORMALIZER.normalize_symbol(
            "VALIDFY1",
            estimates,
            listing,
            analysis_as_of=datetime(2026, 8, 22, tzinfo=timezone.utc),
            estimate_as_of=datetime(2026, 8, 21, tzinfo=timezone.utc),
            source_ids=["estimate-source"],
            minimum_analysts=2,
            max_dispersion_pct=100.0,
            max_fy1_horizon_days=430,
            forward_pe_tolerance_pct=3.0,
        )
        self.assertEqual(row["estimate_normalization_status"], "valid")
        self.assertTrue(row["enrichment_resolved"])
        self.assertFalse(row["enrichment_exhausted"])
        self.assertEqual(row["forward_pe_period"], "FY1")
        self.assertEqual(row["forward_fiscal_year"], "2026")
        self.assertEqual(row["forward_metric_origin"], "computed_from_price_and_fy1_eps")
        self.assertEqual(row["forward_estimate_source_ids"], ["estimate-source"])
        self.assertAlmostEqual(row["forward_pe"], listing["price"] / 2.5, places=5)

        _, decisions, _, selected, queue = self.run_original([row], [row], exhausted=True)
        self.assertEqual(selected, ["VALIDFY1"])
        self.assertEqual(queue, [])
        self.assertTrue(decisions[0]["metrics"]["forward_validation_reasons"] == [])

    def test_normalizer_rejects_outer_year_and_clears_current_forward_fields(self) -> None:
        listing = self.valid_discovery_row("FRMIRAW")
        listing.update({"is_pre_operating": True, "operating_stage": "pre_operating"})
        estimates = [
            {
                "symbol": "FRMIRAW",
                "country": "US",
                "date": "2028-12-31",
                "fiscalYear": "2028",
                "epsAvg": 1.35,
                "epsLow": -0.23,
                "epsHigh": 2.93,
                "revenueAvg": 10_000_000,
                "numAnalystsEps": 2,
                "numAnalystsRevenue": 2,
            },
            {
                "symbol": "FRMIRAW",
                "country": "US",
                "date": "2030-12-31",
                "fiscalYear": "2030",
                "epsAvg": 8.0,
                "epsLow": 0.30,
                "epsHigh": 15.99,
                "revenueAvg": 500_000_000,
                "numAnalystsEps": 2,
                "numAnalystsRevenue": 2,
            },
        ]
        row = NORMALIZER.normalize_symbol(
            "FRMIRAW",
            estimates,
            listing,
            analysis_as_of=datetime(2026, 8, 28, tzinfo=timezone.utc),
            estimate_as_of=datetime(2026, 8, 27, tzinfo=timezone.utc),
            source_ids=["estimate-source"],
            minimum_analysts=2,
            max_dispersion_pct=100.0,
            max_fy1_horizon_days=430,
            forward_pe_tolerance_pct=3.0,
        )
        self.assertEqual(row["estimate_normalization_status"], "unavailable")
        self.assertTrue(row["enrichment_resolved"])
        self.assertTrue(row["enrichment_exhausted"])
        self.assertIsNone(row["forward_pe"])
        self.assertIsNone(row["forward_eps"])
        self.assertIsNotNone(row["raw_forward_candidate"]["computed_pe"])
        reasons = row["estimate_normalization_reasons"]
        self.assertIn("invalid_fy1_horizon", reasons)
        self.assertIn("pre_operating_company", reasons)
        self.assertIn("fy1_eps_range_crosses_zero", reasons)
        self.assertIn("annual_estimate_series_not_contiguous", reasons)

        _, decisions, _, selected, queue = self.run_original([row], [row], exhausted=True)
        self.assertEqual(selected, [])
        self.assertEqual(queue, [])
        self.assertEqual(decisions[0]["decision"]["status"], "unavailable_after_enrichment")
        self.assertIn(
            "estimate_normalization_not_valid",
            decisions[0]["decision"]["blocking_review_reasons"],
        )

    def test_forward_validator_honors_failed_normalization_status(self) -> None:
        row = self.valid_discovery_row("TAMPER")
        row["estimate_normalization_status"] = "unavailable"
        row["estimate_normalization_reasons"] = ["invalid_fy1_horizon"]
        evidence = SCREEN.normalize_forward_valuation(
            row,
            price=row["price"],
            analysis_as_of=self.ANALYSIS_AS_OF,
        )
        self.assertFalse(evidence["valid"])
        self.assertIn("estimate_normalization_not_valid", evidence["reasons"])
        self.assertIn("invalid_fy1_horizon", evidence["reasons"])

    def test_normalizer_requires_explicit_estimate_as_of(self) -> None:
        with self.assertRaises(SystemExit):
            NORMALIZER.parse_args(
                [
                    "--estimates",
                    "estimates.json",
                    "--listing-input",
                    "listing.jsonl",
                    "--analysis-as-of",
                    self.ANALYSIS_AS_OF,
                    "--source-id",
                    "estimate-source",
                    "--output",
                    "normalized.jsonl",
                ]
            )


class RunStateTests(FixtureMixin, unittest.TestCase):
    def test_checkpoint_requires_all_selected_verified_before_complete(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            run_dir = root / "run-1"
            self.assertEqual(
                RUN_STATE.main(
                    [
                        "init",
                        "--run-dir",
                        str(run_dir),
                        "--analysis-as-of",
                        self.payload["analysis_as_of"],
                        "--price-as-of",
                        self.payload["price_basis"]["as_of"],
                        "--session",
                        "regular_close",
                        "--price-source-id",
                        "quote-20260821",
                        "--base-commit",
                        "759151ee92e0eed9a7f2ddf4d6b0e4d6707df409",  # pragma: allowlist secret
                        "--config",
                        str(ASSETS_DIR / "screening-config.example.json"),
                        "--market-context",
                        str(MARKET_CONTEXT_PATH),
                        "--global-sources",
                        str(GLOBAL_SOURCES_PATH),
                    ]
                ),
                0,
            )
            self.assertEqual(
                RUN_STATE.main(
                    [
                        "set-screening-audit",
                        "--run-dir",
                        str(run_dir),
                        "--audit",
                        str(ASSETS_DIR / "broad-screen-audit.example.json"),
                        "--universe-artifact",
                        str(UNIVERSE_AUDIT_PATH),
                        "--candidate-artifact",
                        str(AUDIT_ROWS_PATH),
                    ]
                ),
                0,
            )
            self.assertEqual(
                RUN_STATE.main(["set-status", "--run-dir", str(run_dir), "complete"]), 1
            )

    def test_checkpoint_resume_and_assemble_schema_v3(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            run_dir = root / "run-1"
            self.assertEqual(
                RUN_STATE.main(
                    [
                        "init",
                        "--run-dir",
                        str(run_dir),
                        "--analysis-as-of",
                        self.payload["analysis_as_of"],
                        "--price-as-of",
                        self.payload["price_basis"]["as_of"],
                        "--session",
                        "regular_close",
                        "--price-source-id",
                        "quote-20260821",
                        "--base-commit",
                        "759151ee92e0eed9a7f2ddf4d6b0e4d6707df409",  # pragma: allowlist secret
                        "--config",
                        str(ASSETS_DIR / "screening-config.example.json"),
                        "--market-context",
                        str(MARKET_CONTEXT_PATH),
                        "--global-sources",
                        str(GLOBAL_SOURCES_PATH),
                    ]
                ),
                0,
            )
            self.assertEqual(
                RUN_STATE.main(
                    [
                        "set-screening-audit",
                        "--run-dir",
                        str(run_dir),
                        "--audit",
                        str(ASSETS_DIR / "broad-screen-audit.example.json"),
                        "--universe-artifact",
                        str(UNIVERSE_AUDIT_PATH),
                        "--candidate-artifact",
                        str(AUDIT_ROWS_PATH),
                    ]
                ),
                0,
            )
            for symbol in ("ACME", "CYCLE", "STALE"):
                candidate_file = root / f"{symbol}.json"
                candidate_file.write_text(json.dumps(self.candidate(symbol)), encoding="utf-8")
                self.assertEqual(
                    RUN_STATE.main(
                        [
                            "save-candidate",
                            "--run-dir",
                            str(run_dir),
                            "--candidate",
                            str(candidate_file),
                            "--stage",
                            "verified",
                        ]
                    ),
                    0,
                )
            self.assertEqual(
                RUN_STATE.main(
                    [
                        "set-funnel",
                        "--run-dir",
                        str(run_dir),
                        "--preflight-passed-count",
                        "3",
                    ]
                ),
                0,
            )
            self.assertEqual(
                RUN_STATE.main(["set-status", "--run-dir", str(run_dir), "complete"]), 0
            )
            assembled = root / "assembled.json"
            self.assertEqual(
                RUN_STATE.main(
                    [
                        "assemble",
                        "--run-dir",
                        str(run_dir),
                        "--output",
                        str(assembled),
                    ]
                ),
                0,
            )
            snapshot = json.loads(assembled.read_text(encoding="utf-8"))
            self.assertEqual(snapshot["schema_version"], 3)
            self.assertEqual(snapshot["run_metadata"]["status"], "complete")
            self.assertEqual(
                {c["identity"]["symbol"] for c in snapshot["candidates"]},
                {"ACME", "CYCLE", "STALE"},
            )
            report = EVALUATOR.evaluate_snapshot(snapshot, strict=True, artifact_root=run_dir)
            self.assertEqual(report["ranking_status"], "final")
            self.assertEqual(RUN_STATE.main(["status", "--run-dir", str(run_dir)]), 0)

    def test_manage_run_state_version_cli(self):
        completed = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "manage_run_state.py"), "--version"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["skill_version"], "3.6.1")
        self.assertEqual(payload["contract_revision"], "3.5")
        self.assertEqual(
            payload["runtime_fingerprint"], "ug-v3.6.1-claude-code-direct-fmp-20260830"
        )


class RegressionV35Tests(FixtureMixin, unittest.TestCase):
    def test_provider_prefilter_builder_combines_four_lanes(self) -> None:
        universe = [
            json.loads(line)
            for line in (ASSETS_DIR / "universe-input.example.jsonl").read_text().splitlines()
            if line.strip()
        ]
        base = universe[0]
        lane_rows = {}
        for lane, suffix, pe, growth in (
            ("core_garp", "C", 14.0, 18.0),
            ("high_growth_exception", "H", 27.0, 32.0),
            ("quality_near_miss", "N", 11.0, 10.0),
            ("cyclical_normalization", "Y", 16.0, 22.0),
        ):
            rows = []
            for index in range(2):
                row = deepcopy(base)
                row["symbol"] = f"{suffix}{index}"
                row["price"] = 28.0 + index
                row["forward_pe"] = pe
                row["forward_eps"] = row["price"] / pe
                row["eps_growth_pct"] = growth
                row["revenue_growth_pct"] = max(4.0, growth / 2.0)
                row["analyst_count"] = 5
                row["cyclicality_score"] = 4 if lane == "cyclical_normalization" else 1
                rows.append(row)
            lane_rows[lane] = rows
        pool, audit = PROVIDER_POOL.build_pool(
            universe_rows=universe,
            lane_rows=lane_rows,
            analysis_as_of="2026-08-22T14:00:00-07:00",
            source_ids=["universe-fmp-20260822"],
            per_lane=2,
            max_pool=8,
            minimum_pool=6,
            requested_min_market_cap=500_000_000,
            requested_max_market_cap=20_000_000_000,
            provider_exhausted=False,
        )
        self.assertTrue(audit["valid"])
        self.assertEqual(audit["lane_coverage_count"], 4)
        self.assertEqual(len(pool), 8)
        self.assertEqual(
            {lane for row in pool for lane in row["provider_prefilter_lanes"]},
            PROVIDER_POOL.ALLOWED_LANES,
        )

    def test_multilane_selection_preserves_opportunity_types(self) -> None:
        def row(symbol, lane, priority, sector):
            pre = {
                "core": "passed",
                "growth": "passed_exception",
                "near": "near_miss_review",
                "cycle": "passed",
            }[lane]
            cyclicality = 4 if lane == "cycle" else 1
            requirements = ["mid_cycle_normalization_required"] if lane == "cycle" else []
            return {
                "symbol": symbol,
                "country": "US",
                "sector": sector,
                "deep_dive_priority_score": priority,
                "broad_score": priority,
                "fundamental_completeness_count": 8,
                "metrics": {"analyst_count": 5, "cyclicality_score": cyclicality},
                "decision": {
                    "preselection_status": pre,
                    "status": pre,
                    "exception_admitted": lane == "growth",
                    "deep_dive_requirements": requirements,
                },
            }

        rows = [
            row("CORE", "core", 100, "Technology"),
            row("GROW", "growth", 95, "Healthcare"),
            row("NEAR", "near", 90, "Consumer"),
            row("CYCL", "cycle", 85, "Materials"),
            row("CORE2", "core", 80, "Technology"),
        ]
        config = {
            "selection_lane_quota_core_garp": 1,
            "selection_lane_quota_high_growth": 1,
            "selection_lane_quota_near_miss": 1,
            "selection_lane_quota_cyclical": 1,
            "maximum_selected_per_sector": 1,
        }
        selected, counts = SCREEN._select_multilane(rows, limit=4, config=config)
        self.assertEqual({row["symbol"] for row in selected}, {"CORE", "GROW", "NEAR", "CYCL"})
        self.assertEqual(counts["core_garp"], 1)
        self.assertEqual(counts["high_growth_exception"], 1)
        self.assertEqual(counts["quality_near_miss"], 1)
        self.assertEqual(counts["cyclical_normalization"], 1)

    def test_candidate_serializer_preserves_liquidity_provenance(self) -> None:
        row = json.loads(
            (ASSETS_DIR / "enriched-candidate-pool.example.jsonl").read_text().splitlines()[0]
        )
        config = json.loads((ASSETS_DIR / "screening-config.example.json").read_text())
        decision = SCREEN._candidate_decision(
            row, config, "liquidity_stratified_estimates", "2026-08-22T14:00:00-07:00"
        )
        metrics = decision["metrics"]
        self.assertIn("average_volume", metrics)
        self.assertEqual(metrics["liquidity_source_ids"], ["universe-fmp-20260822"])
        self.assertTrue(metrics["liquidity_valid_for_screen"])

    def test_provider_share_volume_prefilter_cannot_claim_full_listing_scope(self) -> None:
        universe = [
            json.loads((ASSETS_DIR / "universe-input.example.jsonl").read_text().splitlines()[0])
        ]
        config = json.loads((ASSETS_DIR / "screening-config.example.json").read_text())
        _, _, audit, _, _ = ORIGINAL_SCREEN_RUN_LAYERED(
            universe,
            universe,
            config,
            analysis_as_of="2026-08-22T14:00:00-07:00",
            universe_source_ids=["universe-fmp-20260822"],
            candidate_source_ids=["universe-fmp-20260822"],
            candidate_generation_mode="full_universe_fundamentals",
            retrieval_min_market_cap=500_000_000,
            retrieval_max_market_cap=20_000_000_000,
            requested_min_market_cap=500_000_000,
            requested_max_market_cap=20_000_000_000,
            provider_reported_total=1,
            pages_fetched=1,
            pagination_exhausted=True,
            candidate_pool_exhausted=True,
            band_audit=[
                {
                    "min_market_cap": 500_000_000,
                    "max_market_cap": 20_000_000_000,
                    "rows_fetched": 1,
                    "provider_exhausted": True,
                    "retrieval_filters": {"min_volume": 500_000},
                }
            ],
        )
        self.assertTrue(audit["scope"]["enumeration"]["provider_listing_prefiltered"])
        self.assertFalse(audit["scope"]["enumeration"]["full_listing_enumeration_verified"])
        self.assertFalse(audit["scope"]["user_requested_scope_complete"])

    def test_dks_like_low_fcf_candidate_is_not_formally_eligible(self) -> None:
        payload = self.single("ACME")
        candidate = payload["candidates"][0]
        candidate["identity"]["symbol"] = "LOWFCF"
        candidate["financials"]["roic_pct"] = 8.1
        candidate["financials"]["ebitda_ttm"] = 100_000_000
        candidate["financials"]["total_debt"] = 500_000_000
        candidate["financials"]["cash_classification"]["corporate_cash"] = 150_000_000
        candidate["financials"]["cash_classification"]["cash_and_equivalents"] = 150_000_000
        candidate["financials"]["cash_classification"]["marketable_securities"] = 0
        for item in candidate["financials"]["cash_flow_periods"]:
            item["operating_cash_flow"] = 10_000_000
            item["capex_cash_outflow"] = 9_000_000
        candidate["financials"]["cash_flow_ttm"].update(
            {
                "operating_cash_flow": 40_000_000,
                "capex_cash_outflow": 36_000_000,
                "standard_fcf": 4_000_000,
            }
        )
        candidate["financials"]["sbc_ttm"] = 5_000_000
        report = self.evaluate(payload)
        self.assertEqual(report["ranked_candidates"], [])
        row = report["review_required"][0]
        self.assertIn("severely_weak_fcf_support", row["severe_quality_gate_failures"])

    def test_provider_prefilter_skips_invalid_liquidity_without_poisoning_valid_pool(self) -> None:
        valid = {
            "symbol": "GOOD",
            "country": "US",
            "price": 25.0,
            "market_cap": 2_000_000_000,
            "average_volume": 500_000,
            "average_volume_period_days": 20,
            "average_daily_dollar_volume_method": "price_x_provider_average_volume",
            "liquidity_source_ids": ["quote"],
            "forward_pe": 14.0,
            "forward_eps": 25.0 / 14.0,
            "forward_pe_period": "FY1",
            "forward_fiscal_year": "FY2027",
            "forward_period_end": "2027-12-31",
            "forward_estimate_as_of": "2026-08-22T14:00:00-07:00",
            "forward_estimate_source_ids": ["estimate"],
            "analyst_count": 5,
            "eps_growth_pct": 18.0,
            "revenue_growth_pct": 10.0,
        }
        invalid = {"symbol": "BAD", "price": 10.0, "volume": 3_000_000}
        lanes = {
            "core_garp": [valid, invalid],
            "high_growth_exception": [{**valid, "symbol": "HIGH", "eps_growth_pct": 30.0}],
            "quality_near_miss": [
                {**valid, "symbol": "NEAR", "forward_pe": 12.0, "forward_eps": 25.0 / 12.0}
            ],
            "cyclical_normalization": [{**valid, "symbol": "CYCLE", "cyclicality_score": 4}],
        }
        pool, audit = PROVIDER_POOL.build_pool(
            universe_rows=[valid],
            lane_rows=lanes,
            analysis_as_of="2026-08-22T14:00:00-07:00",
            source_ids=["provider"],
            per_lane=1,
            max_pool=4,
            minimum_pool=4,
            requested_min_market_cap=500_000_000,
            requested_max_market_cap=20_000_000_000,
            provider_exhausted=False,
        )
        self.assertTrue(audit["valid"])
        self.assertEqual(audit["invalid_liquidity_symbols"], ["BAD"])
        self.assertNotIn("BAD", [row["symbol"] for row in pool])

    def test_target_solved_driver_bridge_is_rejected(self) -> None:
        payload = self.single("ACME")
        bridge = payload["candidates"][0]["forecast_bridge"]["periods"]["year_2"]
        bridge["driver_provenance"]["operating_margin_pct"]["target_solved"] = True
        report = self.evaluate(payload)
        self.assertEqual(report["ranked_candidates"], [])
        self.assertTrue(
            any(
                "target-solved" in reason
                for reason in report["review_required"][0]["review_reasons"]
            )
        )

    def test_sec_browse_page_is_not_primary_filing_evidence(self) -> None:
        payload = self.single("ACME")
        source = next(row for row in payload["candidates"][0]["sources"] if row["id"] == "acme-10q")
        source["url"] = "https://www.sec.gov/edgar/browse/?CIK=1000000"
        normalized, contract = CONTRACT.validate_and_normalize_snapshot(
            payload, artifact_root=ASSETS_DIR
        )
        candidate_contract = normalized["candidates"][0]["_contract"]
        self.assertFalse(candidate_contract["source_schema_valid"])
        self.assertTrue(
            any("accession-specific" in reason for reason in candidate_contract["review_reasons"])
        )

    def test_generic_cash_flow_support_does_not_verify_discrete_periods(self) -> None:
        payload = self.single("ACME")
        source = next(row for row in payload["candidates"][0]["sources"] if row["id"] == "acme-10q")
        source["supports"] = [
            value
            for value in source["supports"]
            if not value.startswith("financials.cash_flow_periods.")
        ]
        self.assertIn("financials.cash_flow_ttm", source["supports"])
        report = self.evaluate(payload)
        self.assertEqual(report["ranked_candidates"], [])
        self.assertTrue(
            any(
                "cash-flow period" in reason
                for reason in report["review_required"][0]["review_reasons"]
            )
        )

    def test_recent_spin_off_routes_to_review_not_hard_exclusion(self) -> None:
        payload = self.single("ACME")
        candidate = payload["candidates"][0]
        candidate["identity"]["symbol"] = "SPIN"
        candidate["identity"]["special_case"] = "recent_spin_off"
        report = self.evaluate(payload)
        self.assertEqual(report["excluded"], [])
        self.assertEqual(report["review_required"][0]["symbol"], "SPIN")
        self.assertTrue(
            any(
                "corporate transition" in reason.lower()
                for reason in report["review_required"][0]["review_reasons"]
            )
        )

    def test_final_three_categories_can_remain_null(self) -> None:
        report = self.evaluate(self.single("ACME"))
        self.assertIsNotNone(report["final_three"]["highest_conviction"])
        self.assertIsNone(report["final_three"]["most_undervalued"])

    def test_prepublish_audit_and_bundle_are_self_contained(self) -> None:
        report = self.evaluate(self.payload)
        markdown = EVALUATOR.render_markdown(report, language="ja")
        self.assertTrue(
            PREPUBLISH.audit_publication(
                report, report_markdown=markdown, artifact_root=ASSETS_DIR
            )["valid"]
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir) / "run"
            run_dir.mkdir()
            for name in (
                "universe-audit-results.example.jsonl",
                "broad-screen-results.example.jsonl",
                "enrichment-queue.example.json",
            ):
                (run_dir / name).write_bytes((ASSETS_DIR / name).read_bytes())
            report_path = run_dir / "final.json"
            md_path = run_dir / "final.md"
            report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
            md_path.write_text(markdown, encoding="utf-8")
            output = Path(temp_dir) / "bundle.zip"
            result = BUNDLER.build_bundle(run_dir, report_path, md_path, output)
            self.assertTrue(output.is_file())
            self.assertGreaterEqual(result["file_count"], 5)
            from zipfile import ZipFile

            with ZipFile(output) as archive:
                names = set(archive.namelist())
                self.assertIn("BUNDLE_MANIFEST.json", names)
                self.assertIn("universe-audit-results.example.jsonl", names)
                self.assertIn("broad-screen-results.example.jsonl", names)

    def test_prepublish_audit_rejects_continue_language(self) -> None:
        report = self.evaluate(self.payload)
        markdown = EVALUATOR.render_markdown(report, language="ja") + "\n次のターンで続けます。\n"
        audit = PREPUBLISH.audit_publication(
            report, report_markdown=markdown, artifact_root=ASSETS_DIR
        )
        self.assertFalse(audit["valid"])
        self.assertTrue(any("unfinished-run phrase" in error for error in audit["errors"]))


if __name__ == "__main__":
    unittest.main()
