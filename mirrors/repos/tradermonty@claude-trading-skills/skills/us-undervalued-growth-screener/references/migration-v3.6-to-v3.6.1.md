# Migration v3.6 → v3.6.1

v3.6.1 hardens the bounded per-symbol fallback that runs when FMP bulk endpoints are plan-gated (HTTP 402). Schema 3 and contract 3.5 are unchanged; the discovery stage gains an honest scope vocabulary, a stratified seed with a documented selection basis, a pre-selection quality probe, and a persistent endpoint-capability cache.

## Runtime identity

```text
skill_version       = 3.6.1
schema_version      = 3
contract_revision   = 3.5
runtime_fingerprint = ug-v3.6.1-claude-code-direct-fmp-20260830
```

Runtime identity is intentionally different from v3.6.0. Do not mix v3.6.0 audits, packets, or checkpoints with v3.6.1 artifacts; rerun discovery.

## Why

A live run on 2026-08-30 (2,371 listings, all five bulk endpoints 402) showed that the fallback seeded 80 of 2,371 names with no economic data at seed time, that the within-cell ranking saturated at USD 100M/day and fell back to ticker order for large caps, that `provider_exhausted=true` was passed unconditionally, that `scope_complete=true` was read as economic coverage, and that a name with EV/FCF 126x reached the deep-dive slots because no FCF evidence existed before selection.

## Behavioural changes

### Seed selection (`diversified_seed`)

- Cells are sector × market-cap bucket. Quota per cell ∝ √(cell size), reconciled to the seed limit with Hamilton apportionment; every non-empty cell gets at least one seat. The result is independent of cell iteration order.
- Within a cell: `pre_enrichment_score` desc → raw single-day dollar volume desc → market cap desc → fewer missing price/volume fields → `sha256(analysis_date:symbol)`. The raw ticker string is never a tie-break. The log10 dollar-volume term is no longer capped.
- `audit/seed-audit.json` (also embedded in `provider-prefilter-audit.json` and `run-summary.json`) records `seed_selection_basis` (`stratified_liquidity_proxy` when economic fields are absent for the majority of rows), `economic_metrics_available_for_seed`, `cell_count`, `quota_method`, tie-break counters, and the configured/effective seed limits.

### Dynamic seed limit

New config keys with defaults: `pre_enrichment_limit: 180` (was 80), `seed_limit_cap: 200`, `quality_probe_limit: 35`, `candidate_packet_reserve_calls: 30`, `retry_reserve_calls: 25`.

```text
reserved  = quality_probe_limit + exact_liquidity_limit
          + candidate_packet_reserve_calls + retry_reserve_calls
effective = min(pre_enrichment_limit, seed_limit_cap,
                max_api_calls - api_calls_made - reserved)
```

An effective limit below 20 fails the run with `estimate seed budget insufficient` instead of silently producing a thin pool. The probe reserve is counted twice per target (key metrics + annual income statement).

### Quality probe before pool selection

After estimate normalization, the union of lane rows is ranked by best lane score and the top `quality_probe_limit` symbols receive one `key-metrics-ttm` call each. Rows gain `roic_pct`, `fcf_yield_pct`, `ev_to_fcf`, `net_debt_to_ebitda`, `sbc_revenue_pct`, and `sbc_adjusted_fcf_yield_pct` (computed on the market-cap basis: FCF yield − SBC/revenue × revenue/market cap). `audit/quality-probe-audit.json` records attempts, resolutions, and calls used.

Lane scores now include an FCF-yield term (weight 1.0 core_garp / quality_near_miss, 0.5 high_growth_exception) and a leverage penalty above 2.5x net debt / EBITDA. A probe-resolved row with SBC-adjusted (or standard) FCF yield below 1% is excluded from every lane except `high_growth_exception`, where it stays with `provider_prefilter_flags: ["weak_fcf_support"]` and a −10 score. Exclusions are listed under `fcf_prefilter_excluded_symbols` in the discovery audit.

### Honest scope fields

Route selection and completeness are separate thresholds: the bulk route is used from `bulk_estimate_minimum_coverage_pct` (20%), but `economic_screen_scope_complete` / `economic_candidate_universe_exhausted` are true only when the bulk estimates covered every listing-universe symbol (exact count equality, `covered_symbol_count >= universe_symbol_count`; deliberately not a configurable ratio, so no setting can declare a partially covered run complete). A 25%- or even 99%-covered bulk run is a bounded economic screen, exactly like the per-symbol fallback.

`run-summary.json` and `NEXT_ACTION.json` add `listing_enumeration_complete`, `economic_screen_scope_complete`, `listing_universe_count`, `estimate_seed_count`, `estimate_seed_coverage_pct`, `valid_estimate_count`, `valid_estimate_coverage_pct`. `scope_complete` is retained for readers of v3.6.0 output and now carries `scope_complete_deprecated_note`. The discovery audit adds `listing_provider_exhausted`, `estimate_seed_exhausted`, `economic_candidate_universe_exhausted`, and `provider_exhausted_scope` (`estimate_seed` on the fallback path). The contract-validated `screening_audit.scope` block is unchanged.

### Growth basis

**Actuals are verified or absent, and growth is compared on one basis.** `latest_actual_eps` is populated only from (a) a provider row explicitly marked as actual whose period has ended AND whose publication timestamp is at or before `analysis_as_of` (rows without a provable publication time are rejected — a current snapshot replayed against a historical as-of must not leak later-published actuals), or (b) the annual income statement fetched during the quality probe whose `acceptedDate` (with time of day; the date-only `filingDate` is never accepted) is at or before `analysis_as_of` (`latest_actual_verified: true`, `latest_actual_basis: gaap_diluted`, `latest_actual_source_ids`). An unmarked prior-year estimate row is never reported as an actual; it is exposed as `fy0_consensus_eps` and, because it shares the provider's (usually adjusted) basis with FY1/FY3, it is the comparator for `current_year_growth_pct`, `fy1_eps_below_fy0_consensus`, and `growth_pattern` (`growth_pattern_basis: consensus_same_basis`; `unknown` without a prior-year row). The GAAP actual is reported alongside (`current_year_growth_pct_vs_gaap_actual`, `fy1_eps_below_latest_actual`) and, when it differs from the FY0 consensus by more than 15%, `estimate_basis_likely_adjusted: true` warns that GAAP-vs-consensus comparisons are mixed-basis. Found on DOCS: FY1 non-GAAP consensus $1.35 vs GAAP actual $0.98 looked like a decline; same-basis FY26 non-GAAP $1.52 → $1.35 is the real (and still negative) comparison.

`normalize_estimates.py` adds `latest_actual_eps`, `latest_actual_period_end`, `fy1_eps_below_latest_actual`, `current_year_growth_pct`, `eps_growth_fy1_to_fy3_pct` (alias of `eps_growth_pct`), `eps_growth_actual_to_fy3_pct`, `growth_pattern` (`steady | accelerating | trough_recovery | declining | unknown`), and `growth_basis_source_ids`. A `trough_recovery` row is removed from `core_garp` and admitted to `quality_near_miss` with the `earnings_recovery` flag.

### Deep-dive selection with a small budget

`screen_universe._selection_lane` now also routes `growth_pattern == trough_recovery` rows to `quality_near_miss` (the pool-stage rule alone did not reach the final lane). When `max_deep_dive_candidates` is smaller than the lane plan total (default 2/1/1/1 = 5), selection walks the priority order and treats each lane quota as a cap instead of filling lanes in plan order; with a 3-name budget the best cyclical can now win a slot rather than every slot going to the first two lanes. Budgets at or above the plan total keep the lane-first fill.

### Cyclicality and foreign private issuers

Gold, silver, precious/base metals, copper, uranium, coal, metals & mining, and mineral names classify as cyclicality 4; aluminum and semiconductor equipment as 3 (the bare `semiconductor` needle was removed so equipment names do not inherit 4). Rows whose ISIN prefix (or, failing that, listing country) is not `US` carry `foreign_private_issuer_review`, and their packets add `form_20f_6k_verification` to `required_next_checks`. Neither flag excludes a name.

### Pool floor and sector profiles (round-4 review)

- `build_provider_prefilter_pool` waives the minimum-pool row floor only when `provider_exhausted_scope` is a full exhaustion (`economic_candidate_universe` or `full_input`). The per-symbol fallback passes `estimate_seed`, which never waives the floor; `pool_floor_waived` is recorded in the audit. Round-5 hardening removed the legacy missing-scope waiver: an unstated scope now fails closed.
- `normalize_listing` infers `sector_profile_type` (reit / insurance / bank / asset_manager / bdc / mlp / auto_dealership) from sector+industry text, so `screen_universe`'s existing sector gates actually fire: such names without sector-specific valuation evidence go to `sector_specific_valuation_required`, and the general-company `excessive_leverage` hard gate is skipped for them (a mortgage REIT at 13x net debt/EBITDA is normal, not a failure). On the direct-FMP path such rows are then declared enrichment-exhausted (the provider cannot supply P/FFO-AFFO, P/TBV, or adjusted leverage) and resolve as `unavailable_after_enrichment` -- audited and excluded from selection, available for manual sector underwriting in a scoped follow-up.
- The Markdown report renames "Universe scope" to "Listing enumeration" and adds an "Economic estimate coverage" line (mode, covered/universe counts, conclusion scope), so the bounded economic scope is visible in prose, not only in JSON.

### Unit reconciliation, taxonomy map, and the ET filing clock (round-5 review)

- Foreign issuers (non-US ISIN prefix or listing country) are now blocked from selection unless `unit_reconciliation_verified: true` with currency/ADS-unit evidence: a USD ADS price against local-currency statements produced QFIN at forward P/E 0.45x and 94% FCF yield — a unit mismatch, not deep value. On the direct-FMP path such rows are declared enrichment-exhausted and resolve as `unavailable_after_enrichment`. Independent circuit breakers stop implausible ratios on any issuer (`minimum_plausible_forward_pe` 2.0, `maximum_plausible_fcf_yield_pct` 50, reported EPS > 2x price) as `unit_mismatch_suspected`.
- Sector-profile inference now uses an explicit map over real FMP taxonomy labels instead of substring needles: `Auto - Dealerships` maps to `auto_dealership` (the old needle never matched it), `Investment - Banking & Investment Services` maps to `capital_markets` (labelled, valued on ordinary multiples — never the deposit-bank gate), `Banks - *` prefixes map to `bank`, and BDCs are caught by industry (`Business Development ...`) or company-name needles, with `sector_profile_overrides` in config to pin names the listing frame cannot classify (e.g. `{"ARCC": "bdc"}`).
- FMP `acceptedDate` / naive publish stamps are US/Eastern (the SEC acceptance clock), not UTC: a 17:23 ET acceptance read as UTC leaked the filing 4-5 hours early. Both `_verified_annual_actual` and the consensus publish check convert from `America/New_York`; date-only publish stamps count only after the whole publication day (ET) has passed.
- The scope-less pool-floor waiver was removed (fail closed; see the round-4 section above).

### Fail-closed unit context, actual attempt counts, capital_markets exemption (round-8 review)

- The unit gate is inverted from "block what is proven foreign" to "exempt only what is proven domestic": the shared `requires_unit_reconciliation()` (in `screen_universe`, used by both discovery's exhaustion marker and the screen's blocking gate) demands reconciliation evidence whenever the country is missing or non-US, the currency is non-USD, the ISIN is non-US, or the row is an ADR/ADS. `normalize_listing` now preserves `isin` and `is_adr` so those signals survive into the pipeline — a provider dropping the country field can no longer route a CNY-denominated row through as domestic.
- Discovery records the ACTUAL attempted count (`economic_attempt_count = len(estimate frame)`) in the generation audit; the evaluator copies it and fails closed to `diagnostic` when the field is missing, zero, or exceeds the universe (a 180 seed LIMIT over a 50-name universe must never display 360% coverage).
- `capital_markets` (advisory/investment banking) is excluded from the sector-enrichment exhaustion marker: only profiles the screen actually blocks (`SECTOR_PROFILES` + `auto_dealership`) are declared provider-unservable.

### Honest ranking scope (round-6 review)

- Listing 2,371 names and economically comparing 2,371 names are different claims: a run that attempted estimates for 180 seeds (98 evaluable, 4.1% of the universe) is a **scoped pilot**, not a market ranking, and the remaining ~96% are *unexamined*, not rejected. Every run now carries a tri-state `ranking_scope` — `final_marketwide` (estimate acquisition attempted for every listed symbol, exact counts), `final_scoped` (a bounded, fully processed subset; conclusions bind only to it), or `diagnostic` (unresolved queue) — plus per-stage coverage counts and percentages (`economic_attempt_*`, `economically_evaluable_*`, `quality_probe_*`, `deep_dive_*`) in the run summary and report JSON.
- The report title, scope banner, and the no-qualifying-candidates conclusion state the subset explicitly ("Scoped Pilot (180 of 2,371 listed names economically attempted)"; "the remaining names were never economically compared").
- `final_marketwide` is currently unreachable on the direct-FMP Starter path by design: reaching it requires the v3.7 sharded full-universe estimate collection (persistent snapshot store, ~8 deterministic shards within the per-run call budget) tracked as a follow-up issue, together with a discovery-recall gold-set harness (Recall@K against known past candidates).

### Endpoint capability cache

The generated client remembers a 402/403 bulk response in the SQLite cache (`capability:<url>`, 30-day TTL) and pre-disables that endpoint on later runs without spending a call. `respect_capability_cache=False` re-probes unconditionally. Diagnostics add `capability_cache_hits` and `remaining_calls`.

## Operator checklist

1. Build `market-context.json` and `global-sources.json` **before** running `run_pipeline.py`; every source `retrieved_at` must precede `analysis_as_of`.
2. Run discovery, then `manage_run_state.py init` / `set-screening-audit` / `set-funnel --preflight-passed-count N`.
3. `set-screening-audit` now copies the enrichment queue and provider-prefilter pool into `run/audit/` and rewrites their paths to the same run-relative base as the universe/candidate artifacts, and `prepublish_audit.py` also accepts audit-relative bare names, so `--artifact-root <run>` resolves every artifact from one root.
4. Keep shared `fmp-*` source entries byte-identical across candidate ledgers and the global ledger.
