# Required Output Template — v3.5

## 1. Files

Write both:

```text
us_undervalued_growth_<timestamp>.json
us_undervalued_growth_<timestamp>.md
```

Use the evaluator-generated files as the canonical calculation artifacts. Preserve timestamps and source IDs.

## 2. Run Status

At the beginning, state:

- analysis timestamp,
- quote timestamp and session,
- strict-mode flag,
- `ranking_status` (`final` or `provisional`),
- deep-dive input/ranked/review/screened-out/excluded counts,
- broad-screen selected/deferred/unresolved/unavailable/screened-out/excluded counts.

When `ranking_status = provisional`, `selection_outcome = insufficient_data`, or `selection_outcome = selected_pending_enrichment`:

- place a prominent incomplete-coverage warning,
- list unprocessed candidates,
- do not present final-three selections,
- do not describe the displayed order as the final market ranking.

## 3. Screening Funnel and Market Context

Include:

- requested and actual retrieval scope,
- full listing-universe count and listing-data coverage,
- bounded candidate-pool count and generation mode,
- discovery-evaluable count, enrichment attempted/resolved/unresolved counts, resolution percentage, queue, and exhaustion state,
- `candidate_pool_status` and `selection_outcome`,
- selected/deferred/enrichment/sector-review/screened-out/excluded counts,
- corporate-action preflight pass count,
- detailed-underwriting count,
- market valuation, rates, growth, inflation, and sector-cycle assumptions,
- main data sources and as-of dates.

## 4. A. Ranking Table

Recommended columns:

| Rank | Company | Ticker | Price | Market cap | Valuation basis | Current multiple | Standard FCF yield | ROIC/sector return | Diluted-share CAGR | Cyclicality | 3Y constant-multiple upside | Final score | Data quality |
|---:|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|

Use `確認できず` / `not verified` for missing values.

## 5. B. Scenario Table

Include current metric/multiple and year-2/year-3 results for:

- constant multiple,
- configured multiple contraction,
- peer median only when basis/period/source validation passes.

Do not render a scenario when accounting bases are mixed.

## 6. C. Candidate Detail

For each eligible candidate, use the following order.

### 1. Basic Information

- company, ticker, exchange,
- sector/industry/special case,
- price, market cap, liquidity,
- price timestamp and source,
- business overview.

### 2. Investment Thesis

Three to five sentences covering per-share compounding, valuation, quality, and why the opportunity exists.

### 3. Valuation

- basis, accounting basis, period kind,
- current metric and recomputed multiple,
- peer median and validity,
- EV/FCF where meaningful,
- standard and SBC-adjusted FCF yield,
- supplied-multiple reconciliation warning if any.

### 4. Growth History and Forecast

- revenue CAGR,
- GAAP EPS CAGR,
- standard FCF-per-share CAGR,
- diluted-share CAGR,
- current/year-2/year-3 metrics,
- forecast-bridge verdict and source classification,
- analyst count and dispersion.

### 5. Latest Earnings

- fiscal period and publication time,
- revenue and growth,
- GAAP operating margin,
- GAAP/adjusted EPS,
- OCF and standard FCF,
- guidance, key KPIs, segments, one-time items,
- growth-state classification.

### 6. Growth Drivers

List the two- to three-year drivers in priority order.

### 7. Peer Comparison

Show three to five genuine peers with multiple, basis, period, and selection reason. Explain why the comparison is valid.

### 8. Why It Is Discounted

- market concern,
- temporary versus structural classification,
- why the market may be correct,
- conditions for discount narrowing,
- whether returns remain attractive without narrowing.

### 9. Constant-Multiple Scenario

| Item | Current | Year 2 | Year 3 |
|---|---:|---:|---:|
| Per-share metric | | | |
| Multiple | | | |
| Implied price | | | |
| Upside | — | | |
| Annualized return | — | | |

### 10. Multiple-Contraction Scenario

Show year-2/year-3 price and return using the configured contraction, normally 20%.

### 11. Catalysts

List 6–24 month catalysts with timing and probability where available.

### 12. Maximum Risk

State the single most important concrete risk.

### 13. Invalidation Conditions

Use measurable thresholds or events.

### 14. Cyclical Assessment

- score 1–5,
- cycle position,
- peak-profit risk,
- normalized metric/multiple and method when required.

### 15. Score

Show all seven raw components, raw total, explicit penalties, and final score.

### 16. Cash-Flow and Evidence Audit

- TTM method,
- OCF, capex cash outflow, standard FCF,
- company-adjusted FCF and definition,
- corporate versus settlement cash where relevant,
- data-quality score and item breakdown,
- warnings, blockers, and unresolved data.

## 7. D. Review-Required and Deferred Work

### Deep-dive review blockers

| Ticker | Company | Final score | Blockers | Evidence needed |
|---|---|---:|---|---|

Keep these out of the ranked list until blockers are resolved.

### Broad-screen dispositions

Always surface nonzero broad-screen rows that still require or defer work:

| Ticker | Company | Status | Fwd P/E | Revenue growth | Per-share growth | Priority | Reasons / requirements |
|---|---|---|---:|---:|---:|---:|---|

Include `selected`, `deferred_by_budget`, `needs_enrichment`, `sector_review_required`/preselection requirements, `near_miss_review`, and `unavailable_after_enrichment` as applicable. A selected cyclical must show its mid-cycle requirement.

## 8. E. Screened-Out Log

Show deep-dive and broad-screen failures separately.

| Stage | Ticker | Company | Reason |
|---|---|---|---|

Do not hide broad-screen failures merely because no deep-dive candidate record exists. Do not mix these with corporate-action or listing exclusions.

## 9. F. Hard Exclusion Log

Include inactive/delisted symbols, completed/pending M&A, OTC, shell/SPAC, extreme illiquidity, invalid sector basis, and other hard flags.

| Ticker | Company | Reason |
|---|---|---|

## 10. G. Final Three

Render only for a final run with at least one eligible candidate.

Categories:

- highest conviction,
- most undervalued,
- largest upside.

For each selection include all nine required points:

1. reason it is most attractive,
2. upside from EPS/FCF-per-share growth alone,
3. what the market may be missing,
4. best catalyst,
5. largest risk,
6. best reason not to buy now,
7. bear case,
8. invalidation conditions,
9. next-earnings KPIs.

The same ticker may occupy more than one category.

## 11. H. Source Ledger

Show source ID, tier, kind, publication/retrieval timestamps, and supported fields. Do not cite a source for a field it does not support.

## 12. I. Unresolved Data and Global Warnings

List:

- unprocessed candidates,
- missing funnel data,
- stale estimates or quotes,
- source conflicts,
- weak analyst coverage,
- basis mismatches,
- unresolved sector/cycle evidence,
- limitations of the run.

If none, state none explicitly.

## 13. JSON Output Contract

The evaluator output contains:

```json
{
  "schema_version": 3,
  "runtime": {"skill_version": "3.6.1", "contract_revision": "3.5", "runtime_fingerprint": "..."},
  "analysis_as_of": "...",
  "run_metadata": {},
  "ranking_status": "final",
  "strict_mode": true,
  "config": {},
  "contract": {"valid": true},
  "market_context": {},
  "global_sources": [],
  "price_basis": {},
  "screening_funnel": {},
  "screening_audit": {"valid": true},
  "broad_screen": {
    "counts": {
      "selected": 0,
      "deferred_by_budget": 0,
      "review_required": 0,
      "screened_out": 0,
      "excluded": 0,
      "unavailable_after_enrichment": 0
    },
    "selected": [],
    "deferred_by_budget": [],
    "review_required": [],
    "screened_out": [],
    "excluded": [],
    "unavailable_after_enrichment": []
  },
  "counts": {
    "input_candidates": 0,
    "ranked": 0,
    "review_required": 0,
    "screened_out": 0,
    "excluded": 0
  },
  "ranked_candidates": [],
  "review_required": [],
  "screened_out": [],
  "excluded": [],
  "final_three": {},
  "global_warnings": []
}
```

Each candidate result preserves:

- status and reasons,
- identity and source-linked corporate-action result,
- normalized financial metrics and TTM method,
- valuation periods and scenarios,
- forecast/reconciliation details,
- sector profile,
- score components and penalties,
- data-quality item details,
- warnings and unresolved fields,
- qualitative thesis fields,
- source ledger.

## 14. Schema-v3 Mandatory Presentation Controls

The final Markdown must additionally show:

- forward metric period kind and accounting basis,
- analyst count/range for each forecast horizon,
- whether each horizon is rankable,
- market-context values and source-backed timestamp,
- listing-enumeration evidence, broad-screen artifact row count, and SHA-256,
- broad-screen attempted/resolved/unresolved and pool-exhaustion state,
- all nonzero broad-screen disposition groups,
- runtime/version and bounded/full conclusion scope,
- separate latest-quarter and latest-full-year blocks,
- evaluator-calculated EV/FCF and cash definition,
- cash/debt reconciliation status,
- sector stress scenarios where applicable,
- source `supports` values,
- `final` versus `provisional` status.

Never render example/placeholder text. Always show 2Y base, 2Y 20%-contraction, 3Y base, and 3Y 20%-contraction as four separately labeled values. A provisional report must not populate the final-three section. `No qualifying candidates` may appear only when the exhausted pool has zero unresolved rows, an empty queue, all final dispositions, and at least one economically assessable row.

## v3.5 Conditional Candidates and Publication Bundle

Insert a distinct **Conditional Candidates** section between ranked and review-required names. State each failed quality gate and the KPI that would promote the name to `eligible`.

`final_three` labels are optional and category-gated. Use `確認できず` when no candidate meets the relevant conviction, cash-flow valuation, or low-case upside threshold.

Before publication, provide:

```text
prepublish-audit.json
us-undervalued-growth-screen-<date>.zip
BUNDLE_MANIFEST.json inside the ZIP
```

The ZIP must include every file referenced by the final snapshot: universe audit, candidate-pool audit/results, generation audit, enrichment queue, candidate records, source ledger, market context, final JSON, and final Markdown.
