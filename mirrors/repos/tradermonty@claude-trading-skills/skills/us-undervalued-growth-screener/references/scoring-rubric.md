# Scoring Rubric, Evidence Quality, Penalties, and Gates — v3.5

## 1. Philosophy

Use two independent dimensions:

1. **Investment score** — attractiveness of the company and return setup.
2. **Data-quality score** — whether the evidence is sufficient to trust the investment score.

A high investment score never overrides missing evidence. A candidate below the configured data-quality floor is `review_required`, not rankable.

## 2. Raw Investment Score — 100 Points

### A. Growth Sustainability — 20

Assess:

- two- to three-year revenue and per-share growth visibility,
- durability of drivers,
- organic versus acquisition growth,
- customer/product concentration,
- forecast breadth and plausibility,
- sector-specific lifecycle or cycle risks.

Guide:

- 17–20: durable 20%+ per-share growth or exceptional 15%+ visibility.
- 13–16: credible mid-teens growth with manageable risks.
- 8–12: growth exists but is volatile, concentrated, or fading.
- 0–7: weak or unsupported growth.

### B. Valuation Attractiveness — 20

Assess:

- same-basis current/forward multiple,
- standard and SBC-adjusted FCF yield,
- own-history and peer comparison,
- constant-multiple upside,
- 20% contraction resilience,
- value-trap risk.

Do not award a high score merely for low trailing P/E.

### C. Financial Quality and Capital Efficiency — 15

Assess:

- ROIC/sector return metric,
- margins and operating leverage,
- usable corporate cash,
- net leverage and refinancing risk,
- goodwill/intangible burden,
- resilience under stress.

### D. FCF and Earnings Quality — 15

Assess:

- correctly reconstructed standard FCF,
- OCF versus net income,
- working-capital quality,
- standard versus company-adjusted FCF gap,
- SBC-adjusted economics,
- accounting red flags.

### E. Competitive Advantage — 10

Assess:

- switching costs,
- network effects,
- brand/data/regulatory moat,
- recurring revenue,
- customer retention,
- market-share durability.

### F. Capital Allocation, SBC, and Dilution — 10

Assess:

- actual net share change,
- buyback price discipline and funding,
- SBC burden,
- acquisition returns and impairments,
- debt repayment and reinvestment quality.

### G. Catalyst / Risk Balance — 10

Assess:

- catalyst timing and probability,
- identifiable route to estimate delivery,
- downside asymmetry,
- measurable invalidation conditions,
- reason not to buy now.

## 2A. Broad-Screen Guidance Versus Hard Gates

Broad-screen growth and preferred valuation thresholds are guidelines. Store isolated misses in `guideline_misses`; they reduce priority or trigger a near-miss review but do not automatically reject a company.

Selection-eligible patterns include:

- preferred forward valuation plus credible per-share growth,
- P/E 21–30 with 20%+ per-share growth,
- attractive P/E and mid-teens per-share growth even when headline revenue growth is below the preferred range,
- strong cyclical growth/valuation combinations that require mid-cycle normalization.

Hard broad failures are reserved for severe conditions such as non-positive standard FCF when applicable, negative ROIC, excessive leverage beyond the hard limit, extreme forward valuation unsupported by growth, or negative revenue and per-share growth.

`sector_review_required` is selection-eligible when the remaining work is nonblocking cyclical normalization. Missing bank/REIT/BDC/MLP valuation or auto-dealer floorplan-adjusted leverage remains blocking and produces `needs_enrichment`.


## 3. Evidence-Derived Data-Quality Score — 100

The evaluator awards points only when fields and resolving source IDs pass. Self-attested completeness flags are ignored.

| Item | Weight | Required evidence |
|---|---:|---|
| Quote verified | 5 | Price source resolves. |
| Latest earnings verified | 7 | Quarter/full-year separation, timestamps, Tier 1/2 source. |
| Core financials and TTM periods verified | 10 | Revenue, TTM OCF/capex periods, SBC, debt, cash, and shares have primary evidence. |
| Guidance/consensus labeled | 8 | Each valuation period has type, date, analysts, and sources. |
| Driver-derived forecast bridge | 15 | Independent operating-driver arithmetic and source evidence pass. |
| Diluted shares verified | 8 | History and Tier 1/2 evidence. |
| SBC verified | 8 | TTM SBC and Tier 1/2 evidence. |
| Peer set verified | 8 | At least three genuine same-basis forward peers. |
| GAAP/non-GAAP reconciled | 8 | Adjusted periods tie GAAP and adjustment components. |
| Corporate actions verified | 4 | Fresh active listing/symbol/M&A preflight. |
| Cyclical/peak-profit normalization | 5 | Sourced normalization whenever cycle or peak-profit risk requires it. |
| Cash classification verified | 5 | Source-backed corporate cash; customer/restricted funds separated where applicable. |
| ROIC/EBITDA evidence verified | 4 | Reported or transparent analyst-calculated values with sources. |
| Sector risk verified | 5 | LOE/concentration, payments cash, or auto-dealer leverage evidence as applicable. |
| **Total** | **100** | |

Default minimum: 70. A score of 100 means deterministic evidence checks passed; it does not guarantee the thesis is correct.

## 4. Deterministic Penalties

Penalties subtract from the raw 100-point investment score.

### Data-quality penalty

| Data quality | Penalty |
|---:|---:|
| 90–100 | 0 |
| 80–89 | 2 |
| 70–79 | 5 |
| 60–69 | 10 |
| below 60 | 20 |

The minimum-quality gate may still prevent ranking regardless of penalty.

### Cyclicality penalty

| Score | Penalty |
|---:|---:|
| 1 | 0 |
| 2 | 1 |
| 3 | 3 |
| 4 | 6 |
| 5 | 10 |

Missing required normalization is also a review blocker.

### Estimate breadth

Use the minimum analyst count among available year-2/year-3 metrics.

| Minimum count | Penalty |
|---:|---:|
| 5+ | 0 |
| 3–4 | 2 |
| 1–2 | 4 |
| unavailable | 5 |

### Estimate dispersion

Use the maximum normalized low/high spread among future periods.

| Dispersion | Penalty |
|---:|---:|
| ≤20% | 0 |
| >20–30% | 1 |
| >30–50% | 2 |
| >50% | 4 |

### SBC / revenue

| SBC/revenue | Penalty |
|---:|---:|
| missing | 2 |
| ≤5% | 0 |
| >5–10% | 2 |
| >10–15% | 3 |
| >15–25% | 5 |
| >25% | 8 |

### Annualized diluted-share growth

| Growth | Penalty |
|---:|---:|
| missing | 2 |
| ≤3% | 0 |
| >3–5% | 2 |
| >5–10% | 4 |
| >10% | 8 |

Net share reduction is not inferred from a buyback authorization.

### Liquidity

- Below preferred dollar-volume threshold but above hard floor: 2 points.
- Below hard floor: hard exclusion as extreme illiquidity.

### Sector-specific risk

Current deterministic examples:

- Commercial biopharma with top-product concentration ≥50% and nearest material LOE within five years: 2 points.
- The same condition with LOE within three years: 4 points.

Missing required sector evidence causes review rather than a silent neutral score.

## 5. Gates and Statuses

### `excluded`

Hard exclusion includes:

- inactive, delisted, or suspended symbol,
- pending or completed M&A/special-situation pricing,
- OTC, penny stock, shell/SPAC, or development-stage economics,
- repeated financing dependence,
- unresolved restatement/material weakness/SEC investigation,
- meme-only thesis,
- extreme illiquidity,
- invalid special-case valuation basis.

### `screened_out`

Use when the security is valid and active but does not satisfy the broad economic screen. Preserve reasons and sources.

### `review_required`

Examples:

- stale quote/event mismatch,
- stale or unresolved corporate-action preflight,
- TTM/capex reconstruction failure,
- mixed GAAP/adjusted periods,
- forecast bridge or required reconciliation failure,
- data quality below threshold,
- missing cyclicality normalization,
- missing sector-critical evidence,
- insufficient constant-multiple upside when configured,
- materially conflicting supplied multiple.

### `eligible`

All hard and review gates pass. Eligible does not mean “buy”; it means the candidate may be compared and ranked.

## 6. Run-Level Ranking Status

- `final`: run metadata says complete and no symbols remain unprocessed.
- `provisional`: partial run or non-empty unprocessed list.

A provisional report may show completed candidate calculations, but `final_three` must remain empty.

## 7. Confidence Labels

- `high`: eligible, data quality ≥85, analyst breadth ≥5, and no major unresolved caveat.
- `medium`: eligible with data quality 70–84 or analyst breadth 3–4.
- `low`: eligible only under an exception or with fragile estimates.
- `not_ranked`: review-required, screened-out, or excluded.

## 8. Sorting and Tie-Breaking

Sort eligible candidates by:

1. final score,
2. data-quality score,
3. preferred three-year constant-multiple upside,
4. lower cyclicality,
5. symbol for deterministic stability.

Final selections use separate lenses:

- highest conviction: final score, data quality, confidence,
- most undervalued: SBC-adjusted FCF yield and lower current multiple,
- largest upside: preferred three-year constant-multiple upside.

## 9. Schema-v3 Quality Caps

The lowest applicable cap wins.

| Failure | Maximum data-quality score |
|---|---:|
| Latest quarter/full-year mixed or incomplete | 55 |
| Source ledger kind/domain/supports invalid | 60 |
| Forward basis or driver-derived forecast bridge invalid | 60 |
| Core financial/TTM-period evidence incomplete | 65 |
| Required cyclical or peak-profit normalization missing | 65 |
| Required sector/LOE stress evidence missing | 65 |
| ROIC/EBITDA evidence incomplete | 65 |
| Broad-screen audit/runtime invalid | 65 |
| Cash classification incomplete or conflicting | 70 |
| Market context absent, stale, future-dated, or placeholder | 70 |

These caps prevent unsupported 90–100 quality scores.

## 10. Forecast-Horizon Rankability

- Current formal valuation: NTM or FY1.
- A consensus future horizon normally requires at least three analysts.
- A one- or two-analyst horizon is supplemental unless a sourced independent model passes the forecast bridge.
- A candidate must have at least one rankable two- or three-year horizon.
- TTM multiples, unsupported outer-year estimates, and mixed metric bases cannot satisfy the 30% upside gate.

## 11. Run-Level Finality

A final ranking requires:

```text
run_metadata.status = complete
unprocessed_candidates = []
screening_audit.valid = true
screening_audit.runtime matches installed v3.6 fingerprint
screening_audit.candidate_pool.generation_audit.valid = true for bounded pools
screening_audit.enrichment.candidate_pool_exhausted = true
screening_audit.enrichment.unresolved_count = 0
screening_audit.enrichment.queue_count = 0
screening_audit.enrichment.all_rows_resolved = true
contract.valid = true
```

A full-market no-candidates conclusion additionally requires full in-scope economic coverage. A bounded-pool no-candidates conclusion must be explicitly scoped to the audited bounded pool and requires at least one economically assessable row. Attempt counts and evaluable-count thresholds cannot replace pool resolution.

The CLI `--require-final` returns exit code 2 otherwise. Diagnostic files are still written for the repair loop.

## 12. v3.5 Formal Eligibility Quality Gate

Passing the 30% base-case upside test is necessary but not sufficient. A formal `eligible` name must satisfy all configured floors:

| Gate | Default |
|---|---:|
| Final investment score | ≥70 |
| SBC-adjusted FCF yield | ≥3%, **or** EV/FCF ≤30x |
| ROIC / sector-equivalent return | ≥8% |
| Net Debt / EBITDA | ≤3.0x when applicable |
| Diluted-share CAGR | ≤5% |
| Supported low-consensus-case upside | ≥15% |
| Severe LOE stress | no loss worse than -25% |

A candidate with one or two ordinary failures may be labeled `conditional`. A candidate with more failures, severely weak FCF support (for example SBC-adjusted yield below 1% or EV/FCF above 50x), or severe LOE downside is `review_required`.

### Category-specific final selections

`final_three` categories may be null. Never force the sole eligible name into every label.

- **Highest conviction:** score ≥75, DQ ≥80, stress upside ≥0.
- **Most undervalued:** SBC-adjusted FCF yield ≥5% or EV/FCF ≤20x.
- **Largest upside:** supported low-consensus-case upside ≥20%.

If no ranked candidate meets a category threshold, render `確認できず` / `not verified`.
