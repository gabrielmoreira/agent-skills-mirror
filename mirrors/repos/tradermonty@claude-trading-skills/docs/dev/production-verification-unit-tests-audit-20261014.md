# Production unit-test evidence inventory — 2026-10-14

Preparation for [Issue #496](https://github.com/tradermonty/claude-trading-skills/issues/496).
Assessed source revision: `34af7f8226647c722899a5837eff7e887cf7fbe6` (origin/main at discovery).
Inventory captured 2026-10-14 UTC. This is a historical snapshot; later changes require a fresh inventory.

## Result and limits

All 62 production skills are inventoried below: 59 have non-test Python helper candidates,
and three have none. The index declares `unit_tests: not_verified` for the 59 and
`not_applicable` for the three. This inventory changes no verification declarations.

This is a file and policy inventory, not a completed semantic test audit. It does **not**
satisfy any acceptance criterion of #496, prove missing coverage, or establish `passed`.
The confirmed evidence gap is the conservative shared baseline rationale: no retained,
helper-by-helper happy/boundary/error-path, fail-closed, and schema-conformance audit.
Whether existing tests already meet those requirements is **NOT_ASSESSED** here.
Tests were not executed to produce this table. File counts cannot establish test quality.
Security review and instruction-contract review are also **NOT_ASSESSED**.

## Discovery and triage rules

- Read the index, policy, file modes, and file contents from the exact source revision using
  `git show` / `git ls-tree`; untracked files, local caches, and the working tree cannot alter the snapshot.
- Include every `status: production` ID exactly once, sorted by ID. Scope is each skill's
  `scripts/` tree. Files outside that tree are not assessed as helper candidates.
- Count non-test `.py` files as helper candidates, including generated clients and library modules.
  This does not assert that each file is a CLI entry point.
- Test modules are `.py` files in any `tests/` directory or named `test_*` / `*_test.py`.
  `__init__.py` and `conftest.py` are counted separately as support files, including those
  outside tests. Support files may contain executable imports or fixtures and need review too.
- Other files include test fixtures and data. None has a tracked executable bit or shebang;
  discovery aborts if such a non-Python candidate is found, requiring manual classification.
  Consequently the three skills with no Python helpers have no detected non-Python script
  executable either. This does not audit executable snippets in SKILL.md.
- Read coverage waivers from `config/ci-test-policy.yaml` at the assessed revision. Missing or
  malformed policy fails discovery. “No skill waiver” means no per-skill waiver entry;
  it is not a measured coverage result. Waiver presence does not itself block an axis pass,
  nor does meeting a coverage floor prove the axis criteria.

The table lists helper paths relative to `skills/<id>/scripts/`. Test/support counts refer
to that same tree; the reproduction command enumerates their exact membership. All 59
helper-bearing rows have the same outstanding semantic review task: map every helper and
relevant support module to happy, boundary, and error fixtures, demonstrate applicable
fail-closed behavior and schema conformance, then run and record the exact test command,
exit status, revision and date. For outputs without a schema requirement, record why it
is inapplicable rather than inventing schema evidence.

Prioritize core risk/state skills (`drawdown-circuit-breaker`, `futures-position-sizer`,
`position-sizer`, `trader-memory-core`) for that review. Then address waiver-bearing skills
with #293. Coordinate FMP client evidence with PR #556: its generated clients differ from
this snapshot, so evidence from this revision must not be carried forward automatically.
Do not infer coverage gaps from helper/test filename mismatches or module-count ratios.

## Complete production inventory

| Production skill | Python helpers (relative to `scripts/`) | Test modules / support | Other files | Waiver floor / target / expiry |
|---|---|---|---|---|
| `backtest-expert` (not_verified) | `evaluate_backtest.py` | 1 / 1 | None | No skill waiver |
| `breadth-chart-analyst` (not_verified) | `detect_breadth_values.py`<br>`detect_uptrend_ratio.py`<br>`extract_chart_right_edge.py`<br>`fetch_breadth_csv.py` | 2 / 2 | None | 25 / 70 / 2027-01-31 |
| `breakout-trade-planner` (not_verified) | `_market_calendar.py`<br>`order_builder.py`<br>`plan_breakout_trades.py`<br>`risk_calculator.py` | 4 / 1 | None | No skill waiver |
| `canslim-screener` (not_verified) | `calculators/earnings_calculator.py`<br>`calculators/growth_calculator.py`<br>`calculators/institutional_calculator.py`<br>`calculators/leadership_calculator.py`<br>`calculators/market_calculator.py`<br>`calculators/new_highs_calculator.py`<br>`calculators/supply_demand_calculator.py`<br>`check_institutional_endpoint.py`<br>`finviz_stock_client.py`<br>`fmp_client.py`<br>`report_generator.py`<br>`scorer.py`<br>`screen_canslim.py` | 5 / 1 | None | 48 / 70 / 2027-01-31 |
| `contrarian-setup-gate` (not_verified) | `gate_logic.py`<br>`run_contrarian_setup_gate.py` | 2 / 1 | None | No skill waiver |
| `cot-contrarian-detector` (not_verified) | `cot_index.py`<br>`fmp_client.py`<br>`screen_cot_crowding.py` | 3 / 0 | None | No skill waiver |
| `data-quality-checker` (not_verified) | `check_data_quality.py` | 1 / 1 | None | No skill waiver |
| `dividend-growth-pullback-screener` (not_verified) | `screen_dividend_growth_rsi.py` | 2 / 0 | None | 39 / 70 / 2027-01-31 |
| `downtrend-duration-analyzer` (not_verified) | `analyze_downtrends.py`<br>`generate_histogram_html.py` | 3 / 1 | None | 46 / 70 / 2027-01-31 |
| `drawdown-circuit-breaker` (not_verified) | `_market_calendar.py`<br>`check_circuit_breaker.py` | 2 / 1 | None | No skill waiver |
| `dual-axis-skill-reviewer` (not_verified) | `run_dual_axis_review.py` | 1 / 1 | None | No skill waiver |
| `earnings-calendar` (not_verified) | `_fmp_compat.py`<br>`fetch_earnings_fmp.py`<br>`fmp_client.py`<br>`generate_report.py` | 3 / 1 | None | No skill waiver |
| `earnings-trade-analyzer` (not_verified) | `_fmp_compat.py`<br>`_market_calendar.py`<br>`analyze_earnings_trades.py`<br>`calculators/gap_size_calculator.py`<br>`calculators/ma200_calculator.py`<br>`calculators/ma50_calculator.py`<br>`calculators/pre_earnings_trend_calculator.py`<br>`calculators/volume_trend_calculator.py`<br>`fmp_client.py`<br>`report_generator.py`<br>`scorer.py` | 5 / 2 | None | No skill waiver |
| `economic-calendar-fetcher` (not_verified) | `fmp_client.py`<br>`get_economic_calendar.py` | 2 / 0 | None | No skill waiver |
| `edge-candidate-agent` (not_verified) | `auto_detect_candidates.py`<br>`candidate_contract.py`<br>`export_candidate.py`<br>`validate_candidate.py` | 4 / 1 | None | 40 / 70 / 2027-01-31 |
| `edge-concept-synthesizer` (not_verified) | `synthesize_edge_concepts.py` | 1 / 1 | None | No skill waiver |
| `edge-hint-extractor` (not_verified) | `build_hints.py` | 1 / 1 | None | No skill waiver |
| `edge-pipeline-orchestrator` (not_verified) | `orchestrate_edge_pipeline.py` | 1 / 1 | None | No skill waiver |
| `edge-signal-aggregator` (not_verified) | `aggregate_signals.py` | 1 / 1 | None | No skill waiver |
| `edge-strategy-designer` (not_verified) | `design_strategy_drafts.py` | 1 / 1 | None | 47 / 70 / 2027-01-31 |
| `edge-strategy-reviewer` (not_verified) | `review_strategy_drafts.py` | 1 / 1 | None | No skill waiver |
| `exposure-coach` (not_verified) | `calculate_exposure.py` | 1 / 1 | None | No skill waiver |
| `finviz-screener` (not_verified) | `open_finviz_screener.py` | 1 / 1 | None | No skill waiver |
| `ftd-detector` (not_verified) | `fmp_client.py`<br>`ftd_detector.py`<br>`post_ftd_monitor.py`<br>`rally_tracker.py`<br>`report_generator.py` | 6 / 1 | None | No skill waiver |
| `futures-position-sizer` (not_verified) | `futures_position_sizer.py`<br>`futures_sizing.py` | 2 / 1 | None | No skill waiver |
| `ibd-distribution-day-monitor` (not_verified) | `_fmp_compat.py`<br>`data_loader.py`<br>`distribution_day_tracker.py`<br>`exposure_policy.py`<br>`fmp_client.py`<br>`history_utils.py`<br>`ibd_monitor.py`<br>`math_utils.py`<br>`models.py`<br>`report_generator.py`<br>`risk_classifier.py` | 10 / 1 | None | 44 / 70 / 2027-01-31 |
| `institutional-flow-tracker` (not_verified) | `analyze_single_stock.py`<br>`data_quality.py`<br>`fmp_client.py`<br>`track_institution_portfolio.py`<br>`track_institutional_flow.py` | 6 / 1 | None | No skill waiver |
| `kanchi-dividend-review-monitor` (not_verified) | `build_review_queue.py` | 1 / 1 | None | No skill waiver |
| `kanchi-dividend-sop` (not_verified) | `build_entry_signals.py`<br>`build_sop_plan.py`<br>`dividend_basis.py`<br>`event_scanner.py`<br>`payout_safety.py`<br>`thresholds.py`<br>`verdict.py` | 11 / 1 | None | No skill waiver |
| `kanchi-dividend-us-tax-accounting` (not_verified) | `build_tax_planning_sheet.py` | 1 / 1 | None | No skill waiver |
| `macro-regime-detector` (not_verified) | `calculators/concentration_calculator.py`<br>`calculators/credit_conditions_calculator.py`<br>`calculators/equity_bond_calculator.py`<br>`calculators/sector_rotation_calculator.py`<br>`calculators/size_factor_calculator.py`<br>`calculators/utils.py`<br>`calculators/yield_curve_calculator.py`<br>`fmp_client.py`<br>`macro_regime_detector.py`<br>`report_generator.py`<br>`scorer.py` | 13 / 2 | None | No skill waiver |
| `market-breadth-analyzer` (not_verified) | `calculators/bearish_signal_calculator.py`<br>`calculators/cycle_calculator.py`<br>`calculators/divergence_calculator.py`<br>`calculators/historical_context_calculator.py`<br>`calculators/ma_crossover_calculator.py`<br>`calculators/trend_level_calculator.py`<br>`csv_client.py`<br>`history_tracker.py`<br>`market_breadth_analyzer.py`<br>`report_generator.py`<br>`scorer.py` | 10 / 2 | None | No skill waiver |
| `market-environment-analysis` (not_verified) | `_market_calendar.py`<br>`market_utils.py` | 2 / 1 | None | No skill waiver |
| `market-news-analyst` (not_applicable) | None | 1 / 0 | None | No skill waiver |
| `market-top-detector` (not_verified) | `_market_calendar.py`<br>`breadth_csv_client.py`<br>`calculators/breadth_calculator.py`<br>`calculators/defensive_rotation_calculator.py`<br>`calculators/distribution_day_calculator.py`<br>`calculators/index_technical_calculator.py`<br>`calculators/leading_stock_calculator.py`<br>`calculators/math_utils.py`<br>`calculators/sentiment_calculator.py`<br>`fmp_client.py`<br>`historical_comparator.py`<br>`market_top_detector.py`<br>`report_generator.py`<br>`scenario_engine.py`<br>`scorer.py`<br>`utils.py` | 18 / 2 | None | No skill waiver |
| `news-reaction-failure-analyzer` (not_verified) | `analyze_news_reaction.py`<br>`reaction_math.py` | 2 / 0 | None | No skill waiver |
| `options-strategy-advisor` (not_verified) | `black_scholes.py` | 2 / 1 | None | No skill waiver |
| `pair-trade-screener` (not_verified) | `analyze_spread.py`<br>`find_pairs.py`<br>`statsmodels_support.py` | 2 / 1 | None | 56 / 70 / 2027-01-31 |
| `parabolic-short-trade-planner` (not_verified) | `_fmp_compat.py`<br>`_market_calendar.py`<br>`adapters/alpaca_inventory_adapter.py`<br>`adapters/alpaca_market_data_adapter.py`<br>`adapters/fixture_market_data_adapter.py`<br>`adapters/market_data_adapter.py`<br>`bar_normalizer.py`<br>`broker_short_inventory_adapter.py`<br>`calculators/acceleration_calculator.py`<br>`calculators/atr_calculator.py`<br>`calculators/liquidity_metrics_calculator.py`<br>`calculators/ma_extension_calculator.py`<br>`calculators/parabolic_score_calculator.py`<br>`calculators/range_expansion_calculator.py`<br>`check_live_apis.py`<br>`fmp_client.py`<br>`generate_pre_market_plan.py`<br>`intraday_evaluators/first_red_evaluator.py`<br>`intraday_evaluators/orl_evaluator.py`<br>`intraday_evaluators/vwap_fail_evaluator.py`<br>`intraday_size_resolver.py`<br>`intraday_state_machine.py`<br>`intraday_state_store.py`<br>`invalidation_rules.py`<br>`manual_reasons.py`<br>`market_clock.py`<br>`math_helpers.py`<br>`monitor_intraday_trigger.py`<br>`parabolic_report_generator.py`<br>`parabolic_scorer.py`<br>`plan_builders/first_red_plan_builder.py`<br>`plan_builders/orl_plan_builder.py`<br>`plan_builders/vwap_fail_plan_builder.py`<br>`screen_parabolic.py`<br>`size_recipe_builder.py`<br>`ssr_state_tracker.py`<br>`state_caps.py`<br>`vwap.py` | 34 / 5 | `tests/fixtures/dry_run_minimal.json`<br>`tests/fixtures/intraday_bars/first_red_clean.json`<br>`tests/fixtures/intraday_bars/first_red_invalidated.json`<br>`tests/fixtures/intraday_bars/first_red_same_bar_invalidation_wins.json`<br>`tests/fixtures/intraday_bars/no_bars_yet.json`<br>`tests/fixtures/intraday_bars/orl_clean_break.json`<br>`tests/fixtures/intraday_bars/orl_invalidated.json`<br>`tests/fixtures/intraday_bars/orl_low_volume_no_fire.json`<br>`tests/fixtures/intraday_bars/vwap_full_fsm.json`<br>`tests/fixtures/intraday_bars/vwap_invalidated_after_trigger.json`<br>`tests/fixtures/phase2_plan_smoke.json` | No skill waiver |
| `pead-screener` (not_verified) | `_fmp_compat.py`<br>`calculators/breakout_calculator.py`<br>`calculators/liquidity_calculator.py`<br>`calculators/risk_reward_calculator.py`<br>`calculators/weekly_candle_calculator.py`<br>`fmp_client.py`<br>`report_generator.py`<br>`scorer.py`<br>`screen_pead.py` | 2 / 2 | None | No skill waiver |
| `portfolio-manager` (not_verified) | `check_alpaca_connection.py`<br>`reconcile_positions.py` | 2 / 1 | None | No skill waiver |
| `position-sizer` (not_verified) | `position_sizer.py` | 1 / 1 | None | No skill waiver |
| `pre-trade-discipline-gate` (not_verified) | `check_pre_trade_discipline.py` | 1 / 1 | None | No skill waiver |
| `scenario-analyzer` (not_applicable) | None | 1 / 0 | None | No skill waiver |
| `sector-analyst` (not_verified) | `analyze_sector_rotation.py` | 2 / 1 | None | No skill waiver |
| `signal-postmortem` (not_verified) | `postmortem_analyzer.py`<br>`postmortem_recorder.py` | 3 / 1 | None | No skill waiver |
| `skill-designer` (not_verified) | `build_design_prompt.py` | 1 / 1 | None | 47 / 70 / 2027-01-31 |
| `skill-idea-miner` (not_verified) | `mine_session_logs.py`<br>`score_ideas.py` | 3 / 2 | None | No skill waiver |
| `skill-integration-tester` (not_verified) | `validate_workflows.py` | 1 / 1 | None | No skill waiver |
| `stanley-druckenmiller-investment` (not_verified) | `allocation_engine.py`<br>`report_generator.py`<br>`report_loader.py`<br>`scorer.py`<br>`strategy_synthesizer.py` | 5 / 1 | None | No skill waiver |
| `strategy-pivot-designer` (not_verified) | `detect_stagnation.py`<br>`generate_pivots.py` | 4 / 1 | None | No skill waiver |
| `technical-analyst` (not_verified) | `check_weekly_price_action.py`<br>`weekly_price_action.py` | 3 / 0 | None | No skill waiver |
| `theme-detector` (not_verified) | `_market_calendar.py`<br>`calculators/heat_calculator.py`<br>`calculators/industry_ranker.py`<br>`calculators/lifecycle_calculator.py`<br>`calculators/theme_classifier.py`<br>`calculators/theme_discoverer.py`<br>`config_loader.py`<br>`default_theme_config.py`<br>`etf_scanner.py`<br>`finviz_performance_client.py`<br>`leadership.py`<br>`report_generator.py`<br>`representative_stock_selector.py`<br>`scorer.py`<br>`theme_detector.py`<br>`theme_history.py`<br>`theme_matcher.py`<br>`uptrend_client.py` | 19 / 2 | `tests/README.md`<br>`themes.yaml` | No skill waiver |
| `trade-hypothesis-ideator` (not_verified) | `pipeline/evidence_extractor.py`<br>`pipeline/format_output.py`<br>`pipeline/normalize.py`<br>`pipeline/ranking.py`<br>`pipeline/strategy_exporter.py`<br>`run_hypothesis_ideator.py` | 6 / 2 | None | No skill waiver |
| `trader-memory-core` (not_verified) | `fmp_price_adapter.py`<br>`thesis_ingest.py`<br>`thesis_review.py`<br>`thesis_store.py`<br>`trader_memory_cli.py` | 6 / 1 | None | No skill waiver |
| `trading-skills-navigator` (not_verified) | `build_snapshot.py`<br>`intent_benchmark.py`<br>`recommend.py` | 2 / 1 | None | No skill waiver |
| `uptrend-analyzer` (not_verified) | `calculators/historical_context_calculator.py`<br>`calculators/market_breadth_calculator.py`<br>`calculators/momentum_calculator.py`<br>`calculators/sector_participation_calculator.py`<br>`calculators/sector_rotation_calculator.py`<br>`data_fetcher.py`<br>`report_generator.py`<br>`scorer.py`<br>`uptrend_analyzer.py` | 11 / 2 | None | No skill waiver |
| `us-market-bubble-detector` (not_verified) | `bubble_scorer.py` | 1 / 0 | None | No skill waiver |
| `us-stock-analysis` (not_applicable) | None | 1 / 0 | None | No skill waiver |
| `value-dividend-screener` (not_verified) | `screen_dividend_stocks.py` | 2 / 1 | None | 34 / 70 / 2027-01-31 |
| `vcp-screener` (not_verified) | `_fmp_compat.py`<br>`calculators/execution_state.py`<br>`calculators/forward_outcome.py`<br>`calculators/pattern_classifier.py`<br>`calculators/pivot_proximity_calculator.py`<br>`calculators/relative_strength_calculator.py`<br>`calculators/trend_template_calculator.py`<br>`calculators/vcp_pattern_calculator.py`<br>`calculators/volume_pattern_calculator.py`<br>`fmp_client.py`<br>`historical_report.py`<br>`historical_scanner.py`<br>`report_generator.py`<br>`scorer.py`<br>`screen_vcp.py` | 4 / 2 | None | No skill waiver |
| `weekly-performance-digest` (not_verified) | `generate_weekly_digest.py` | 1 / 1 | None | No skill waiver |

Production skills: 62. Totals: {'helpers': 267, 'not_applicable': 3, 'not_verified': 59, 'other': 13, 'support': 68, 'tests': 251, 'with_helpers': 59, 'without_helpers': 3}.

## Reproduce the inventory

Run from a checkout containing the assessed commit, with Python 3.9 and PyYAML installed.
The command is read-only and emits the table and totals above. It pins all inputs to the
assessed revision, even when run from another branch. To inspect exact test/support paths,
inspect the `groups` lists in the command; the classification is explicit.

```bash
python3.9 - <<'PY'
import subprocess
from collections import Counter
from pathlib import Path

import yaml

revision = "34af7f8226647c722899a5837eff7e887cf7fbe6"


def read(path):
    return subprocess.check_output(["git", "show", f"{revision}:{path}"])


skills = yaml.safe_load(read("skills-index.yaml"))["skills"]
production = sorted(
    (skill for skill in skills if skill["status"] == "production"),
    key=lambda skill: skill["id"],
)
waivers = yaml.safe_load(read("config/ci-test-policy.yaml"))["coverage"]["waivers"]
files = subprocess.check_output(["git", "ls-tree", "-r", "-z", revision]).decode().split("\0")
tracked = {}
for entry in filter(None, files):
    metadata, path = entry.split("\t", 1)
    mode, kind, _ = metadata.split()
    if kind == "blob":
        tracked[path] = mode

totals = Counter()
print(
    "| Production skill | Python helpers (relative to `scripts/`) | Test modules / support | Other files | Waiver floor / target / expiry |"
)
print("|---|---|---|---|---|")
for skill in production:
    prefix = f"skills/{skill['id']}/scripts/"
    groups = {key: [] for key in ("helpers", "tests", "support", "other")}
    for path in sorted(tracked):
        if not path.startswith(prefix):
            continue
        relative = path[len(prefix) :]
        item = Path(relative)
        is_test = (
            "tests" in item.parts
            or item.name.startswith("test_")
            or item.name.endswith("_test.py")
            or item.name == "conftest.py"
        )
        if item.name in {"__init__.py", "conftest.py"}:
            group = "support"
        elif item.suffix == ".py":
            group = "tests" if is_test else "helpers"
        else:
            group = "other"
            first_line = read(path).split(b"\n", 1)[0]
            if tracked[path] == "100755" or first_line.startswith(b"#!"):
                raise RuntimeError(f"Review non-Python executable before classifying: {path}")
        groups[group].append(relative)
    totals.update({key: len(value) for key, value in groups.items()})
    totals["with_helpers" if groups["helpers"] else "without_helpers"] += 1
    declaration = skill["verification"]["unit_tests"]
    totals[declaration] += 1
    helper_text = "<br>".join(f"`{path}`" for path in groups["helpers"]) or "None"
    other_text = "<br>".join(f"`{path}`" for path in groups["other"]) or "None"
    waiver = waivers.get(skill["id"])
    waiver_text = (
        f"{waiver['floor']} / {waiver['target']} / {waiver['expires_on']}"
        if waiver is not None
        else "No skill waiver"
    )
    print(
        f"| `{skill['id']}` ({declaration}) | {helper_text} | "
        f"{len(groups['tests'])} / {len(groups['support'])} | "
        f"{other_text} | {waiver_text} |"
    )
print()
print(f"Production skills: {len(production)}. Totals: {dict(sorted(totals.items()))}.")
PY
```

## Follow-up evidence record

For each skill, retain helper/support path, test node IDs, exercised behavior, output schema
(or applicability rationale), command and exit status, reviewed revision, reviewer and date.
Use the [production criteria](production-verification.md) before any `passed` override;
update the baseline and index together only when every requirement is established.
Issue #496 remains open for the semantic audit, security review, and instruction contracts.
