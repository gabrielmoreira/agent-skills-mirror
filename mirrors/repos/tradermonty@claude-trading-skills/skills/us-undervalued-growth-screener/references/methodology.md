# US Undervalued Growth Screening Methodology

## 1. Objective

Identify US-listed companies whose **per-share economic value** can compound fast enough to produce attractive two- to three-year returns without relying on multiple expansion.

The central test is:

> If the current valuation multiple remains unchanged, can healthy EPS or free-cash-flow-per-share growth alone support a credible 30% to 50% total price increase over two to three years?

A low P/E ratio is not sufficient. The candidate must also demonstrate sustainable growth, acceptable financial risk, high-quality earnings, sensible capital allocation, limited dilution, and a defensible business position.


## Version 3.5 Mandatory Controls

Contract 3.5 adds the following non-negotiable controls:

1. Every artifact carries the installed runtime fingerprint; stale v3.1-v3.4 artifacts are rejected.
2. A bounded provider/discovery pool can support a scoped final ranking only when its generation is audited and every pool row is resolved; it cannot support a market-wide no-candidates claim.
3. Forecasts are reconstructed from revenue, margin, interest/other, tax, adjustments, and diluted shares. A numerator reverse-engineered from target EPS is not a forecast bridge.
4. Adjusted forecasts separately reconcile the driver-derived GAAP metric and after-tax adjustments.
5. TTM cash-flow periods require resolving source evidence.
6. Cash classification, ROIC, and EBITDA require evidence before quality points can be awarded.
7. Commercial-biopharma aliases trigger concentration, LOE, and 6x/8x stress controls.
8. `peak_profit_risk=true` requires normalization regardless of the numeric cycle score.
9. The deterministic broad-screen decision is authoritative; the narrative layer cannot reintroduce a mechanical revenue-growth or cyclical exclusion.
10. Preserve the user-requested market-cap range independently from the executed retrieval range; internal budget pressure cannot silently redefine the request.
11. Accept only 20+ session average-dollar-liquidity evidence; one-session volume cannot determine discovery eligibility or order.
12. Normalize dated annual estimates to the current NTM/FY1 horizon before computing Forward P/E; never substitute FY2/FY3 because FY1 is missing.
13. Commit the selected set and complete every selected symbol; any budget reduction requires a new deterministic broad-screen run.
14. Treat helper exit code 2 as an internal continuation signal and never require a separate user “continue” turn.

## Inherited v3.2 Controls Retained in v3.5

Contract revision 3.2 preserves schema-v3 accounting and evidence controls while correcting the v3.1 completion and candidate-routing defects:

1. Audit listing, quote, market-cap, and liquidity fields across the full requested universe.
2. Prove universe enumeration through provider totals plus exhausted pagination or exhausted market-cap-band audits. Requested/retrieved endpoints alone do not prove completeness.
3. Do **not** require complete statements, ROIC, FCF, leverage, and forward estimates for most of the market.
4. Generate a bounded candidate pool through a provider prefilter, available estimates, or a deterministic sector/market-cap/liquidity fallback.
5. Distinguish `enrichment_attempted` from `enrichment_resolved`. Attempt-count and evaluable-count thresholds never complete a pool with unresolved rows.
6. Permit high-quality near misses and P/E 21–30 high-growth exceptions. Growth thresholds are guidelines, not isolated hard gates.
7. Route strong cyclicals to deep dive with `mid_cycle_normalization_required`; do not automatically reject them. Financial-sector and auto-dealer valuation/leverage gaps remain blocking.
8. Prioritize enrichment by GARP information value, not ticker order or liquidity alone.
9. A valid no-candidates result requires an exhausted pool, zero unresolved rows, an empty queue, all final dispositions, and at least one economically assessable row.
10. Enforce `unprocessed = selected - verified`; every selected symbol ends with a verified candidate record.
11. Render broad-screen selected, deferred, review, unavailable, screened-out, and excluded rows in the final Markdown instead of hiding them behind empty deep-dive counts.
12. Validate dynamic market fields against their `data_as_of`/publication date and require official sources for policy, Treasury, inflation, and GDP.

The existing schema-v3 controls remain mandatory: separate quarter/full-year records; NTM/FY1 formal valuation; analyst-count rankability; typed source ledgers; consistent EV/FCF cash definition; commercial-biopharma concentration/LOE stress; auto-dealer floorplan treatment; corporate-action preflight; evidence-derived quality; positive capex-outflow convention; explicit TTM reconstruction; standard versus adjusted FCF separation; same-basis periods; GAAP reconciliation; checkpointing; and `--require-final`.

## Tiered Screening Process

### Layer A: Listing-universe audit

Audit all retrieved symbols for exchange, active/common-stock status, price, market cap, and liquidity. This layer establishes scope and trading eligibility; it does not claim full financial coverage.

### Layer B: Bounded economic discovery

Create a transparent candidate pool with forward valuation and per-share growth evidence. Use a provider prefilter when available. If bulk fundamentals are unavailable, stratify up to 120 liquid in-scope symbols across sectors and market-cap bands, enrich them with available estimates, and record every attempt.

### Layer C: Primary-source underwriting

Verify the selected set with SEC and IR materials, normalize cash flow and accounting basis, compare genuine peers, apply cycle/sector controls, and calculate formal scenarios.

## 2. Universe

### Default scope

- Exchanges: NYSE, Nasdaq, NYSE American.
- Security type: operating-company common stock.
- Market capitalization: normally USD 500 million to USD 20 billion.
- Minimum price: configurable; default USD 5.
- Minimum average daily dollar volume: configurable; default USD 5 million.
- Final ranking: no more than 10 candidates, and fewer when evidence is weak.

### Allowed exceptions

Include a company outside the default market-cap range only when it strongly satisfies the methodology. Record the reason for the exception.

### Hard or presumptive exclusions

- OTC securities.
- Penny stocks or extreme liquidity risk.
- Shell companies and pre-combination SPACs.
- Development-stage biotechnology companies with little operating revenue.
- Businesses dependent on repeated equity issuance for survival.
- Pending merger-arbitrage situations where price is anchored to transaction terms.
- Companies with unresolved material restatements, internal-control weaknesses, severe governance concerns, or active SEC investigations.
- Meme-driven securities without operating support.

Preserve excluded names and reasons in the screening audit trail.

## 3. Staged Screening Process

### Stage 0: Full listing-universe audit

Retain one row per requested symbol with active/common-stock status, exchange, price, market capitalization, liquidity, source ID, and actual retrieval bounds. This layer proves scope and tradability; it does not claim full financial coverage.

### Stage 1: Bounded candidate generation and enrichment

Use a reproducible provider prefilter, already-available estimates, or a deterministic sector × market-cap × liquidity discovery pool. Enrich only the bounded pool with forward valuation and per-share growth. Missing blocking discovery metrics become `needs_enrichment` and receive no score. Financial-sector or auto-dealer valuation/leverage gaps remain blocking. A cyclical normalization requirement is nonblocking: a strong candidate may receive `sector_review_required`, a real score, and selection for mid-cycle deep-dive verification.

Suggested guidelines for assessable rows:

- Revenue growth near 10% or better where appropriate.
- EPS or FCF-per-share growth near 15% or better; 20%–30% preferred.
- Forward P/E normally 20x or lower, with justified high-growth exceptions through 30x.
- Positive standard FCF or a sector-appropriate substitute.
- ROIC near 10% or better where relevant.
- Net debt/EBITDA normally 2.5x or lower using sector adjustments.
- Diluted-share growth normally 3% or lower.
- Adequate dollar-volume liquidity.

The pool is complete only after every bounded row is resolved and the operator has verified exhaustion. A query attempt does not equal resolution. `no_qualifying_candidates` additionally requires zero selected rows and at least one economically assessable row. If no assessable row exists, the result is `insufficient_data`, not “no candidates.”

### Stage 2: Corporate-action preflight

Before deep financial work, verify active listing/symbol, pending or completed M&A, delisting/suspension, ticker changes, splits, spin-offs, and the latest material-event time. Pending/completed M&A and inactive/delisted securities are hard exclusions from normal GARP ranking. Preserve source IDs and checkpoint the result.

### Stage 3: Primary-source underwriting

For every selected name, verify load-bearing facts with SEC filings or company IR and complete one auditable record even when the final classification is review-required, screened-out, or excluded.

The deep dive must answer:

1. Is growth real and durable?
2. Is growth visible on a per-share basis?
3. Is reported profit supported by operating cash flow?
4. Is the valuation low for a temporary reason or a structural one?
5. Does the return case survive without re-rating?
6. Does the return case survive a 20% multiple contraction?
7. What measurable facts would invalidate the thesis?

## 4. Immutable Analysis Snapshot

Create one analysis snapshot before comparing candidates.

Record:

- Analysis timestamp and timezone.
- Price timestamp, session, and timezone.
- Whether price is regular close, pre-market, or after-hours.
- Latest earnings period and publication timestamp.
- Latest material corporate action timestamp.
- Consensus retrieval timestamp.
- Fiscal-year mapping used for FY1, FY2, and FY3.
- Currency and split-adjustment status.

### Stale-data gate

A price is stale when it predates a later earnings release or material corporate action while the analysis uses the post-event information. Either update the price or clearly label the report as a pre-event valuation. In strict mode, reject the candidate.

### Fiscal-year consistency

Do not mix calendar-year estimates with fiscal-year estimates. Do not compare a trailing metric for one company with a forward metric for another without labeling the mismatch.

## 5. Source Classification and Hierarchy

Classify every important figure as one of:

- `reported_fact`
- `company_guidance`
- `market_consensus`
- `analyst_estimate`

Primary-source hierarchy:

1. SEC 10-K, 10-Q, 8-K, 20-F, or 6-K.
2. Company earnings release, shareholder letter, investor presentation, prepared remarks, or investor-day material.
3. Company guidance transcribed by a reputable data source.
4. Market-data vendor or consensus database.
5. Reputable news or analysis for context only.

When sources conflict, prefer the SEC filing, then explain the discrepancy.

For consensus estimates record:

- retrieval date,
- fiscal period,
- FY1/FY2/NTM classification,
- GAAP or adjusted basis,
- analyst count,
- estimate range or dispersion when available.

Never silently fill missing values.

## 6. Core Financial Definitions

### Standard free cash flow

Normalize capex as a **non-negative cash-outflow magnitude**. A vendor value reported with a negative cash-flow sign must be converted before evaluation.

```text
Standard FCF = operating cash flow - capex cash outflow
```

Declare one TTM method: explicitly reported TTM; four unique discrete quarters; or latest FY plus current YTD minus prior-year comparable YTD. Never sum overlapping cumulative 3-, 6-, and 9-month cash-flow statements. If the company presents adjusted FCF, show it separately with its definition; do not substitute it for standard FCF.

### SBC-adjusted economic FCF

```text
SBC-adjusted FCF = standard FCF - stock-based compensation
```

This is an economic lens, not a GAAP cash-flow measure. Show both values. Do not double-count SBC if the selected FCF definition already deducts it.

### FCF per share

```text
FCF per share = standard FCF / diluted weighted-average shares
```

Use diluted shares and a consistent period.

### Enterprise value

```text
Enterprise value = market capitalization + total debt + preferred stock
                   + non-controlling interest - cash and equivalents
```

Use a consistent definition and document material adjustments.

### Net debt / EBITDA

```text
Usable cash = corporate cash + eligible marketable securities
Net debt / EBITDA = (total debt - usable cash) / EBITDA
```

Exclude customer, merchant, settlement, and restricted funds from usable cash. Use normalized EBITDA for cyclicals. Negative net debt is acceptable and should not be forced to zero.

### ROIC

Preferred definition:

```text
NOPAT = adjusted operating income * (1 - normalized cash tax rate)
Invested capital = average operating assets - average operating liabilities
ROIC = NOPAT / average invested capital
```

Use a vendor ROIC only after confirming its definition. For financial companies, use sector-appropriate returns instead.

## 7. Growth Analysis

Measure both aggregate and per-share growth.

Required historical views when available:

- Three- to five-year revenue CAGR.
- Three-year GAAP EPS CAGR.
- Three-year standard FCF-per-share CAGR.
- Basic and diluted-share change.
- Gross, operating, and FCF margin trends.
- ROIC trend.

Required forward views:

- Current fiscal-year revenue and EPS growth.
- Next fiscal-year revenue and EPS growth.
- Two- and three-year EPS or FCF-per-share forecast.
- Forecast diluted-share count.

### Growth-quality checklist

Positive drivers include:

- market expansion,
- market-share gains,
- recurring revenue,
- switching costs,
- network effects,
- pricing backed by stable volume,
- mix improvement,
- new products or capacity,
- international expansion,
- cross-selling,
- aftermarket revenue,
- operating leverage.

Negative drivers include:

- customer or product concentration,
- acquisition-only growth,
- equity-funded acquisitions,
- temporary demand surges,
- subsidy dependence,
- commodity-price-only growth,
- price increases with declining volume,
- deteriorating customer-acquisition economics,
- growth achieved by sacrificing unit economics.

## 8. Forecast Bridge

Do not treat consensus as self-validating. Reconstruct the estimate.

At minimum bridge:

```text
Revenue
x gross margin
- operating expenses
= operating income
+/- interest and other income
- taxes
= net income
/ diluted shares
= EPS
```

For FCF, bridge:

```text
Operating income / net income
+ non-cash charges
+/- working-capital change
- capex
= standard FCF
/ diluted shares
= FCF per share
```

Test whether margins, tax rate, interest, and share count are plausible. Flag forecasts that rely on unexplained linear extrapolation, abrupt margin expansion, or aggressive buyback assumptions.

## 9. GAAP and Non-GAAP Discipline

The current, year-2, and year-3 valuation metrics must use one accounting basis: `gaap`, `company_adjusted`, `analyst_normalized`, or `sector_defined`. A current GAAP metric cannot be compared with future adjusted consensus under a constant multiple. Mixed bases block the scenario. Company-adjusted and analyst-normalized metrics require an arithmetic reconciliation from GAAP with labeled adjustment rows, recurring/nonrecurring classification, and source IDs.


Always distinguish:

- GAAP operating income,
- adjusted operating income,
- GAAP net income,
- GAAP EPS,
- adjusted EPS,
- adjusted EBITDA,
- standard FCF,
- company-defined adjusted FCF.

Investigate recurring exclusions:

- stock-based compensation,
- restructuring costs,
- acquisition costs,
- intangible amortization,
- litigation costs,
- impairment charges,
- one-time tax benefits.

A cost that recurs every quarter or year is not economically one-time. Penalize large or widening GAAP/non-GAAP gaps.

## 10. Earnings and Cash-Flow Quality

Review:

- Net income versus operating cash flow.
- Accounts-receivable growth and DSO.
- Inventory growth and days inventory.
- Unbilled revenue and contract assets.
- Capitalized software or R&D.
- Recurring restructuring and acquisition charges.
- Goodwill and intangible growth.
- Asset sales, tax benefits, or pension income.
- Related-party transactions.
- Auditor changes.
- Material weaknesses, restatements, or SEC inquiries.
- Frequent changes to KPI definitions.

Working-capital releases can temporarily inflate FCF. Identify the structural and temporary portions.

## 11. Stock-Based Compensation, Dilution, and Buybacks

Collect:

- SBC amount.
- SBC / revenue.
- SBC / operating cash flow.
- Basic and diluted shares for at least three years.
- RSUs, options, warrants, convertibles, ATM programs, shelves, and recent offerings.
- Actual repurchase amount and shares retired.

Evaluate buybacks by **net share reduction**, not authorization announcements.

```text
Net share change = ending diluted shares / beginning diluted shares - 1
```

Ask:

- Did repurchases offset employee issuance?
- Were shares bought above reasonable value?
- Was debt increased to fund repurchases?
- Did diluted shares actually decline?

## 12. Valuation

Use multiple measures:

- NTM, FY1, and FY2 P/E.
- EV/EBITDA.
- EV/EBIT.
- EV/FCF.
- FCF yield.
- SBC-adjusted FCF yield.
- PEG.
- Five-year own-history median.
- Genuine peer median.

### Value-trap checks

A low multiple is not attractive when:

- earnings are at a cycle peak,
- orders or revenue are decelerating,
- EPS includes one-time tax or asset-sale gains,
- leverage is excessive,
- market share is structurally eroding,
- customer concentration is severe,
- EPS rises while FCF does not,
- dilution transfers value away from owners.

## 13. Return Scenarios

### Constant-multiple scenario

For an EPS-based candidate:

```text
Future price = future diluted EPS * current forward P/E
Upside = future price / current price - 1
CAGR = (future price / current price)^(1 / years) - 1
```

For other sectors, substitute the appropriate per-share metric and multiple.

### 20% multiple-contraction stress

```text
Stressed multiple = current multiple * 0.80
Stressed future price = future metric * stressed multiple
```

### Peer-median scenario

Use only when peers are economically comparable and the same metric basis is available.

```text
Peer case price = future metric * peer median multiple
```

The peer case is secondary. Never rank primarily on assumed re-rating.

## 14. Peer Selection

Choose three to five peers based on:

- business economics,
- customers and end markets,
- growth stage,
- recurring versus transactional revenue,
- margins,
- capital intensity,
- geographic mix.

Explain each peer choice. Do not use a faster-growing or unrelated company merely to make the target look cheap.

Compare:

- growth,
- margins,
- ROIC or sector return measure,
- leverage,
- FCF yield,
- SBC,
- dilution,
- forward valuation.

Classify the discount as:

- temporary and potentially resolvable,
- structural and difficult to resolve,
- justified by superior risk,
- unsupported because the peer set is weak.

## 15. Cyclicality

Rate cyclicality from 1 to 5:

1. Low economic sensitivity.
2. Mild sensitivity.
3. Moderate sensitivity.
4. High sensitivity.
5. Extreme cyclicality.

For cyclical companies analyze five to ten years when available:

- revenue,
- operating margin,
- EPS,
- FCF,
- orders and backlog,
- book-to-bill,
- inventory and utilization,
- customer and industry capex,
- commodity prices,
- price versus volume,
- recession drawdowns.

Calculate mid-cycle revenue, margin, EPS, and FCF when possible. Use normalized earnings for valuation, not peak earnings.

## 16. Latest-Earnings Assessment

Record:

- fiscal period and publication date,
- revenue and year-over-year / sequential growth,
- organic growth,
- gross and operating margins,
- GAAP and adjusted EPS,
- operating cash flow and FCF,
- capex and SBC,
- diluted shares,
- guidance changes,
- consensus differences,
- segment results,
- orders/backlog and sector KPIs,
- one-time items,
- working-capital and tax changes.

Classify the growth state:

- accelerating,
- stable,
- modestly decelerating,
- clearly decelerating,
- cycle bottoming,
- cycle peaking.

A headline beat does not override deteriorating guidance, cash flow, backlog, or core KPIs.

## 17. Catalysts, Risks, and Invalidation

Evaluate catalysts over six to 24 months and specify timing, probability, and likely mechanism.

Examples:

- growth reacceleration,
- end of inventory correction,
- order recovery,
- new product or capacity,
- margin improvement,
- debt reduction,
- actual buybacks,
- divestiture or spin-off,
- regulatory or litigation resolution.

Define the largest risk concretely. Write measurable invalidation conditions, such as:

- revenue growth below a threshold for two quarters,
- backlog declining year over year,
- gross margin below a threshold,
- NRR below a threshold,
- net leverage above a threshold,
- annualized dilution above a threshold,
- FCF turning negative,
- loss of a major customer,
- guidance withdrawal.

## 18. Fail-Closed Decision Policy

Do not rank a candidate when:

- critical snapshot data is stale,
- the valuation basis is inappropriate,
- source provenance is missing for load-bearing numbers,
- data-quality score is below the configured floor,
- a hard-exclusion flag is unresolved,
- future per-share estimates cannot be reconciled,
- peer or cyclical normalization is essential but unavailable.

Status values:

- `eligible`: enough evidence to rank.
- `review_required`: promising but unresolved evidence prevents final ranking.
- `screened_out`: active/researchable security that failed the broad economic screen.
- `excluded`: hard exclusion, inactive security, special-situation pricing, or invalid input.

A partial run or a run with unprocessed candidates is `provisional`. It may show completed candidate calculations but must not publish final-three selections.

## 19. Final Selection

Select up to three categories:

- Highest conviction.
- Most undervalued.
- Largest upside.

For each answer:

1. Why it qualifies.
2. Return from per-share growth alone.
3. What the market may be missing.
4. Most important catalyst.
5. Largest risk.
6. Best reason not to buy now.
7. Bear case.
8. Invalidation condition.
9. KPI to monitor next quarter.

The same company may occupy multiple categories. No candidate is preferable to a forced recommendation.

## Version 3.5 Candidate-Quality Improvements

- Use deterministic multi-lane sampling to improve discovery diversity and avoid selecting only one factor style.
- Apply formal quality gates after the upside screen so low-P/E/high-EV-FCF transition stories do not become automatic winners.
- Test low-consensus-case upside in addition to average consensus.
- Require independent, sourced driver provenance and reject target-solved bridges.
- Treat spin-offs and transformative M&A as pro-forma corporate transitions.
- Publish only self-contained, pre-audited run bundles.
