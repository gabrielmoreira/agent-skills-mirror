# Primary-Source Research Checklist — Schema 3 / Contract 3.5 / Audit v3.5

Use this checklist for every broad-screen survivor. Mark each item `verified`, `not applicable`, or `not verified`. A blank field or a Boolean assertion without a resolving source ID is not a pass.


## v3.5 Runtime and Independent-Bridge Checks

- [ ] Every helper `--version` reports v3.6.1 / contract 3.5 / the expected fingerprint.
- [ ] Audit, checkpoint, and snapshot runtime metadata match the installed skill.
- [ ] The user-requested scope remains separate from the executed retrieval scope; no internal single-band rewrite occurred.
- [ ] Discovery liquidity uses a documented 20+ session average and source IDs, never one-session volume.
- [ ] Current Forward P/E is dated NTM/FY1 and reconciles to positive EPS and price; no distant outer-year substitution.
- [ ] Every Broad Screen-selected symbol is present in the committed set and reaches a verified terminal candidate record.
- [ ] A bounded pool has a valid generation audit and a clearly labeled conclusion scope.
- [ ] Forecast EPS/FCF is independently derived from operating drivers; numerator is not reverse-engineered from target per-share metric.
- [ ] Adjusted forecast GAAP and adjustment portions separately tie to the reconciliation.
- [ ] Each TTM cash-flow component period has resolving source IDs.
- [ ] Corporate cash, eligible securities, customer/settlement funds, and restricted cash are correctly classified.
- [ ] ROIC and EBITDA have source-linked inputs or transparent calculations.
- [ ] Commercial-biopharma aliases trigger concentration, LOE, and 6x/8x stress checks.
- [ ] `peak_profit_risk=true` has sourced normalization.
- [ ] Broad-screen statuses were not overridden by an informal revenue-growth or cycle gate.

## 0. Checkpoint and Run Integrity

- [ ] Initialize a run with `manage_run_state.py`.
- [ ] Record `analysis_as_of`, common quote basis, repository commit, and configuration.
- [ ] Record requested and actual retrieval scope; do not silently narrow the market-cap range.
- [ ] Preserve `user_requested_scope` separately from `executed_scope`; tool/context budget is not scope authorization.
- [ ] If execution is narrower, confirm explicit user authorization and label the limited conclusion scope.
- [ ] Reject single-session volume as ADDV; require provider-average or 20+ trading-day average-volume evidence with source IDs.
- [ ] Prove universe enumeration with provider total plus exhausted pagination or exhausted market-cap-band audits.
- [ ] Attach both listing-universe and candidate-pool audit artifacts with verified SHA-256.
- [ ] Record listing-data coverage separately from candidate-pool economic coverage.
- [ ] Record candidate-pool status (`sufficient`, `sufficient_pending_enrichment`, `no_qualifying_candidates`, or `insufficient_data`).
- [ ] Preserve the enrichment queue and documented attempts when bulk fundamentals are unavailable.
- [ ] Record attempted, resolved, and unresolved counts separately.
- [ ] Confirm every in-scope listing symbol is represented in the candidate pool before a market-wide no-candidates claim.
- [ ] Confirm `candidate_pool_exhaustion_declared=true` only after every candidate row is resolved or evidenced as unavailable.
- [ ] Confirm independently verified `candidate_pool_exhausted=true`; do not rely on the declaration alone.
- [ ] Confirm only genuinely scored, selection-eligible rows enter the deep-dive set.
- [ ] Permit strong cyclicals to enter deep dive with a mid-cycle-normalization requirement.
- [ ] Treat growth thresholds as guidelines; document isolated misses rather than using them as automatic rejects.
- [ ] Record every screening-funnel stage.
- [ ] Save each candidate after preflight and after full verification.
- [ ] Enforce `unprocessed_candidates = selected_symbols - verified_symbols`.
- [ ] Verify the selected-set SHA-256 commitment and configured deep-dive budget.
- [ ] Resolve every committed selected symbol; never let an LLM silently choose a smaller subset.
- [ ] Keep an interrupted run `partial`; do not publish final-three selections.
- [ ] Before publishing “no candidates,” confirm full in-scope candidate coverage, explicit and verified exhaustion, zero queue/unresolved rows, all final dispositions, and at least one assessable row.
- [ ] Confirm Markdown exposes nonzero broad-screen review, unavailable, screened-out, and exclusion groups.

## 1. Corporate-Action Preflight — Perform First

- [ ] Confirm exchange listing is active.
- [ ] Confirm symbol is active and quote volume is plausible.
- [ ] Search for pending or completed acquisitions/mergers.
- [ ] Check delisting, suspension, ticker change, split, reverse split, and spin-off.
- [ ] Record `checked_at` and `latest_material_event_at`.
- [ ] Attach resolving source IDs.
- [ ] Hard-exclude completed/pending M&A and inactive/delisted securities from normal GARP ranking.
- [ ] Route rumors, unknown status, or stale preflight to review.

## 2. Snapshot Integrity

- [ ] Record current-price timestamp, timezone, and session.
- [ ] Confirm regular-close versus after-hours/pre-market/intraday.
- [ ] Record latest earnings period and publication timestamp.
- [ ] Confirm no earnings release or material event occurred after the price timestamp.
- [ ] Confirm split adjustment for price, EPS, and shares.
- [ ] Confirm reporting currency.
- [ ] Map FY1, FY2, and FY3 to the company's fiscal calendar.
- [ ] Normalize the formal current valuation period as NTM or FY1 with period end, estimate-as-of date, analyst count, and source IDs.
- [ ] Reject outer-year-only, pre-operating, zero-crossing, or excessively dispersed consensus as a current Forward P/E.
- [ ] Confirm fiscal versus calendar-year estimates.

## 3. Source Ledger and Evidence Map

For every load-bearing field, create a source-ledger row with:

- source ID,
- tier,
- document kind,
- title,
- publication and retrieval timestamps,
- URL or filing identifier,
- supported field names.

Create candidate-level `evidence` entries for price, latest earnings, revenue, cash flow, SBC, debt, cash classification, diluted shares, and corporate-action preflight.

### Tier 1 — SEC

- [ ] 10-K
- [ ] 10-Q
- [ ] 8-K
- [ ] DEF 14A
- [ ] S-3 / 424B5 when dilution risk exists
- [ ] Form 4 when insider activity matters
- [ ] 20-F / 6-K for foreign issuers

### Tier 2 — Company IR

- [ ] Earnings release
- [ ] Shareholder letter
- [ ] Investor presentation
- [ ] Prepared remarks/transcript supplied by company
- [ ] Guidance
- [ ] Investor-day materials

### Tier 3/4 — Supplemental

- [ ] Quote/market-data vendor
- [ ] Consensus database with retrieval time and analyst count
- [ ] Exchange/company status source
- [ ] Analyst model or calculation with explicit assumptions
- [ ] News/context source

When sources conflict, prefer the latest correcting SEC filing and document the discrepancy.

## 4. Business and Growth

- [ ] Summarize business model and revenue drivers.
- [ ] Identify recurring, transactional, cyclical, project, and acquired revenue.
- [ ] Calculate three- to five-year revenue CAGR.
- [ ] Calculate three-year GAAP EPS CAGR when meaningful.
- [ ] Calculate three-year standard FCF-per-share CAGR.
- [ ] Separate organic and acquisition growth.
- [ ] Separate price, volume, mix, and FX where material.
- [ ] Identify customer, product, platform, channel, and geographic concentration.
- [ ] Assess market share and competitive advantages.
- [ ] Classify growth as accelerating, stable, modestly decelerating, clearly decelerating, bottoming, or peaking.

## 5. Latest Earnings

- [ ] Fiscal period/end date/release timestamp
- [ ] Revenue, YoY, sequential, and organic growth
- [ ] Gross profit and margin
- [ ] GAAP operating income and margin
- [ ] Adjusted operating income and margin
- [ ] GAAP and adjusted EPS
- [ ] Operating cash flow
- [ ] Standard FCF
- [ ] Capex cash-outflow magnitude
- [ ] SBC
- [ ] Basic and diluted shares
- [ ] Guidance and revision direction
- [ ] Same-basis consensus comparison
- [ ] Segment performance
- [ ] Orders, backlog, or sector KPIs
- [ ] One-time costs/gains
- [ ] Working-capital and tax-rate changes

Do not let a headline beat override deteriorating guidance, cash flow, backlog, take rate, prescription growth, or another core KPI.

## 6. TTM Cash Flow and FCF

- [ ] Identify source statement as standalone quarter, YTD cumulative, FY, or explicit TTM.
- [ ] Normalize every `capex_cash_outflow` as a non-negative magnitude.
- [ ] Select one method: `reported_ttm`, `sum_4_discrete`, or `fy_plus_current_ytd_minus_prior_ytd`.
- [ ] For `sum_4_discrete`, confirm four unique standalone quarters.
- [ ] For YTD reconstruction, confirm comparable current/prior periods.
- [ ] Recalculate standard FCF = OCF − capex cash outflow.
- [ ] Reconcile supplied and reconstructed values within configured tolerance.
- [ ] Keep company-adjusted FCF separate and document its definition.
- [ ] Calculate SBC-adjusted economic FCF separately.
- [ ] Explain working-capital contributions.

## 7. GAAP / Adjusted Discipline

- [ ] Record a separate `metric_basis` for current, year-2, and year-3 periods.
- [ ] Confirm all periods use one basis.
- [ ] Never combine current GAAP EPS with future adjusted EPS under one multiple.
- [ ] For adjusted/normalized metrics, record the GAAP starting metric.
- [ ] List every adjustment, amount, label, and recurring status.
- [ ] Confirm arithmetic tie-out to the valuation metric.
- [ ] Attach source IDs.
- [ ] Distinguish company non-GAAP from analyst-created normalization.
- [ ] Flag recurring exclusions and changed definitions.

Review exclusions:

- SBC
- restructuring
- acquisition costs
- intangible amortization
- acquired IPR&D
- litigation
- impairment
- tax items
- asset-sale gains
- other recurring “one-time” items

## 8. Accounting and Earnings Quality

- [ ] Reconcile net income and operating cash flow.
- [ ] Review receivables, DSO, inventory, and inventory days.
- [ ] Review unbilled revenue, contract assets, deferred revenue, and customer advances.
- [ ] Review capitalized software/R&D.
- [ ] Review goodwill, intangibles, and impairments.
- [ ] Review asset-sale gains, tax effects, and pension/non-operating income.
- [ ] Review related parties, auditor changes, material weaknesses, restatements, and SEC investigations.

## 9. Balance Sheet and Cash Classification

- [ ] Corporate cash
- [ ] Marketable securities available to shareholders
- [ ] Customer/settlement funds
- [ ] Restricted cash
- [ ] Total debt
- [ ] Net debt using only eligible cash
- [ ] Net debt/EBITDA
- [ ] Interest expense and coverage
- [ ] Debt maturities, rates, covenants, leases, preferred stock, and minority interests
- [ ] Goodwill/intangibles and contingent acquisition obligations

For payments/marketplace businesses, never treat settlement float as corporate cash.

## 10. SBC, Dilution, and Capital Allocation

- [ ] SBC amount, SBC/revenue, and SBC/OCF
- [ ] Basic and diluted share history
- [ ] Annualized diluted-share change
- [ ] RSUs, options, warrants, convertibles
- [ ] ATM, shelf, and public-offering history
- [ ] Actual buyback dollars and shares
- [ ] Average repurchase price
- [ ] Net share reduction after employee issuance
- [ ] Buyback funding source
- [ ] Acquisition returns and impairment history

## 11. Forecast Quality and Arithmetic Bridge

For every current/year-2/year-3 metric used:

- [ ] Period label and period kind
- [ ] Metric basis
- [ ] Source classification
- [ ] Retrieval time and source IDs
- [ ] Analyst count
- [ ] Estimate low/high or dispersion

For year-2/year-3:

- [ ] Revenue assumption
- [ ] Gross/operating or FCF margin assumption
- [ ] Interest assumption
- [ ] Tax rate
- [ ] Diluted shares
- [ ] Buyback/dilution assumptions
- [ ] Acquisition/divestiture assumptions
- [ ] Metric numerator and denominator
- [ ] Arithmetic tie to valuation metric within tolerance

Flag single-analyst outer-year estimates and unexplained linear extrapolation.

## 12. Valuation and Scenarios

- [ ] Sector-appropriate valuation basis
- [ ] Current multiple recomputed as price/current metric
- [ ] Supplied multiple reconciled
- [ ] NTM/FY1/FY2 multiple labels
- [ ] EV/EBITDA, EV/EBIT, EV/FCF where appropriate
- [ ] Standard and SBC-adjusted FCF yield
- [ ] Own-history median
- [ ] Three to five genuine peers
- [ ] Same-basis/same-period peer median
- [ ] Constant-multiple 2Y and 3Y cases
- [ ] 20% contraction 2Y and 3Y cases
- [ ] Peer-median case only when valid

## 13. Sector-Specific Review

### Commercial biopharma

- [ ] Product-level revenue and top-product concentration
- [ ] Nearest material LOE date
- [ ] Patent settlement/litigation status
- [ ] Next-generation formulation/indication strategy
- [ ] Replacement pipeline and launch costs
- [ ] Source IDs for concentration and LOE

### Payments

- [ ] TPV growth
- [ ] Revenue/TPV and gross-profit/TPV
- [ ] Current and prior gross-profit take rate
- [ ] Corporate versus settlement cash
- [ ] FX and country exposure
- [ ] Standard versus adjusted FCF
- [ ] Source IDs

Use `sector-kpis.md` for all other sectors.

## 14. Cyclical Review

For scores 3–5:

- [ ] Five- to ten-year revenue, margin, EPS, and FCF history
- [ ] Orders/backlog/book-to-bill
- [ ] Inventory/utilization/capacity
- [ ] Customer/industry capex
- [ ] Commodity/freight exposure
- [ ] Price versus volume
- [ ] Recession drawdown
- [ ] Mid-cycle revenue and margin
- [ ] Normalized per-share metric and multiple
- [ ] Normalization method and source IDs

## 15. Peer Set

- [ ] Three to five genuine peers
- [ ] Selection reason per peer
- [ ] Same metric basis and period kind
- [ ] Growth, margins, ROIC/sector return, leverage, SBC, dilution, and valuation compared
- [ ] Discount classified as temporary, structural, justified, or unverified

## 16. Governance and Thesis

- [ ] Management capital allocation
- [ ] Insider ownership and transactions with 10b5-1 context
- [ ] Dual-class/founder control
- [ ] Related parties and compensation alignment
- [ ] Three- to five-sentence thesis
- [ ] Why discounted and why market may be right
- [ ] Six- to 24-month catalysts
- [ ] Largest concrete risk
- [ ] Bear case
- [ ] Measurable invalidation conditions
- [ ] Next-quarter KPIs
- [ ] Best reason not to buy now

## 17. Final Gate

A candidate may be `eligible` only when:

- [ ] Corporate action is fresh, active, and sourced.
- [ ] No hard flag is unresolved.
- [ ] Price and event timestamps are consistent.
- [ ] Core financial fields have Tier 1/2 evidence.
- [ ] TTM cash flow and capex signs are valid.
- [ ] Current/future metric bases match.
- [ ] Forecast bridge and required GAAP reconciliation pass.
- [ ] Valuation basis is sector-appropriate.
- [ ] Peer set is valid or explicitly unavailable without inventing a median.
- [ ] Data-quality score meets threshold.
- [ ] Required cyclical/sector evidence is complete.
- [ ] Minimum upside gate passes.
- [ ] Invalidation conditions are measurable.
- [ ] Run is complete before final-three publication.

## 18. Schema-v3 Autonomous Completion Checks

Before presenting a live run, confirm:

- [ ] Market context contains no placeholder text, is not future-dated, and has policy rate, 10Y yield, inflation, market forward P/E, small/mid-cap context, and resolving source IDs.
- [ ] `screening_audit` hashes to the full row-level universe artifact.
- [ ] Every audit-selected symbol has a verified candidate checkpoint.
- [ ] No selected symbol remains in `unprocessed_candidates`.
- [ ] `source.supports` is an array for every source.
- [ ] Source kind/tier is correct; no third-party transcript is labeled company IR.
- [ ] Q4 and full-year figures are stored separately.
- [ ] Current formal valuation metric is NTM or FY1.
- [ ] At least one future horizon is rankable after analyst-count checks.
- [ ] Current/future metric bases match.
- [ ] EV/FCF uses corporate cash plus eligible marketable securities consistently.
- [ ] Latest-release and normalized cash/debt values reconcile or have a source-backed note.
- [ ] High-growth 21–30x P/E exceptions were not mechanically discarded.
- [ ] Auto dealers use floorplan-adjusted leverage.
- [ ] Commercial biopharma product concentration and LOE are sourced or derived.
- [ ] `evaluate_candidates.py --strict --require-final` exits 0.
- [ ] The first diagnostic report was inspected and repairable blockers were corrected.

## v3.5 Final Quality Checklist

- [ ] Broad Screen selected lanes are diversified across core/high-growth/near-miss/cyclical opportunities where available.
- [ ] Candidate rows retain `average_volume` and `liquidity_source_ids`.
- [ ] Provider-side share-volume filters are disclosed and do not count as full listing enumeration.
- [ ] Every forecast driver has origin, source IDs, and `target_solved=false`.
- [ ] No margin, share count, or residual adjustment was reverse-solved merely to match target EPS.
- [ ] Every discrete cash-flow period has explicit source support.
- [ ] SEC filing evidence uses an accession-specific Archives URL.
- [ ] Recent spin-offs/acquisitions have pro-forma transition normalization.
- [ ] Formal eligible names pass score, FCF, ROIC, leverage, dilution, low-case, and LOE quality gates.
- [ ] `final_three` categories remain null when category thresholds are not met.
- [ ] `prepublish_audit.py` exits 0.
- [ ] `bundle_run_artifacts.py` produces a self-contained, manifest-hashed ZIP.
