# Source Prompt Coverage Map

The original Japanese prompt remains the methodological authority. The skill reorganizes it into progressive research instructions, a source-linked schema, deterministic calculations, audit statuses, and tests.

| Original prompt area | Skill implementation |
|---|---|
| Undervalued growth rather than low P/E | `SKILL.md` overview; methodology objective; minimum constant-multiple upside gate |
| NYSE/Nasdaq/NYSE American and USD 500M–20B focus | scope/configuration and screening funnel |
| Exclusions and liquidity | corporate-action preflight, flags, liquidity gates, hard-exclusion log |
| SEC/IR source priority | evidence map, source ledger, research checklist, data-quality weights |
| Consensus date/period/type/analyst count | separate current/year-2/year-3 valuation records |
| Price timestamp/session and post-event consistency | common price basis, latest-event timestamp, stale-data gate |
| Revenue, EPS, FCF-per-share growth | historical CAGRs and forward per-share periods |
| ROIC, margins, leverage | normalized financials and score components |
| Standard FCF = OCF − capex | non-negative capex convention and three TTM reconstruction methods |
| Company-adjusted FCF disclosure | separate supplemental field and definition; never substitutes for standard FCF |
| GAAP vs non-GAAP | per-period metric basis and arithmetic GAAP reconciliation |
| SBC, dilution, and actual buybacks | SBC/FCF metrics, diluted-share history, explicit penalties |
| Three-to-five genuine peers | sourced peer rows, basis/period validation, peer-median scenario |
| Strict cyclical review | sourced normalization object and fail-closed gate |
| Latest earnings and growth-state classification | latest-earnings object and full report section |
| Sector-specific KPI rules | sector profile; commercial-biopharma LOE and payments cash/take-rate controls |
| Earnings/accounting quality | TTM reconstruction, working-capital review, source checklist |
| Constant multiple, 20% contraction, peer median | deterministic evaluator |
| EPS/FCF forecast construction | numerator/denominator bridge, drivers, arithmetic tolerance |
| Why discounted and market may be right | qualitative contract and report section |
| Catalysts, risk, and invalidation | detailed candidate and final-three sections |
| 100-point ranking | seven preserved score components plus deterministic penalties |
| Complete output contract | full Markdown renderer and structured JSON |
| Do not guess or force recommendations | null contract, evidence gates, review status, no-qualifier result |
| Preserve incomplete work honestly | checkpoint manager and provisional partial-run status |

## Version 2 Enhancements

1. Corporate-action preflight runs before detailed financial research, catching completed acquisitions and inactive symbols early.
2. Data-quality points require resolving evidence and arithmetic; self-attested completeness flags are ignored.
3. Capex sign convention is explicit and negative normalized outflows fail closed.
4. TTM OCF/capex supports four discrete quarters or FY+YTD−prior YTD without double-counting cumulative statements.
5. Standard FCF and company-adjusted FCF are separate.
6. Corporate cash is separated from customer/settlement and restricted funds.
7. Current, year-2, and year-3 accounting bases are stored separately; mixed bases block scenarios.
8. Adjusted/normalized periods require GAAP reconciliation.
9. `screened_out` is distinct from hard `excluded`.
10. Long runs checkpoint every candidate and can resume.
11. Partial coverage produces a provisional report with no final-three claims.
12. Commercial-biopharma LOE and payments take-rate/cash controls are explicit.
13. Full Markdown output now follows all major sections of the original prompt.
14. Synthetic tests cover evidence, FCF, period basis, corporate actions, sector controls, partial runs, and packaging behavior.

## Version 3 Review-Driven Controls

| Original requirement | v3 implementation |
|---|---|
| Current market valuation, rates, economy, sector cycle | Mandatory sourced `market_context`; placeholders/future dates rejected |
| Latest price and latest earnings | Quote/event timestamp gate; latest quarter and full year separated |
| Forward P/E constant-multiple analysis | NTM/FY1 current metric required; TTM supplemental only |
| Do not uncritically use consensus | Analyst-count/range and rankable-horizon controls; forecast bridge required |
| Compare 3–5 peers | Same-basis sourced peer gate |
| Do not mechanically reject 21–30x high growers | Broad-screen high-growth exception |
| Industry-specific leverage | Auto-dealer floorplan-adjusted leverage gate |
| Product concentration and structural risk | Derived/sourced commercial-biopharma concentration and LOE stress |
| Important numbers need source/period/retrieval date | Strict source ledger with typed `supports` arrays |
| Scope and candidate counts | Full listing audit plus bounded candidate-pool artifact, explicit scope, enrichment counts, and SHA-256 |
| Do not recommend when conditions are unmet | `--require-final`, no final-three on provisional runs, explicit no-candidate result |

## Version 3.1 Execution Controls

| Original requirement | v3.5 execution implementation |
|---|---|
| Screen the major US exchanges, with emphasis on USD 500M–20B | Full listing-universe audit records requested and retrieved bounds; reduced scope is disclosed and cannot silently complete |
| Do not guess missing numbers | Missing discovery data is `needs_enrichment`; no placeholder zeros or scores |
| Use multiple metrics but respect industry characteristics | General-company candidate screen plus explicit sector-review routing for banks, REITs, insurers, BDCs, MLPs, cyclicals, and auto dealers |
| Do not force ten recommendations | Deep-dive set is bounded; evidence-based `no_candidates` is a valid final result |
| Important data must be current and sourced | Full listing source, candidate-estimate source, SEC/IR sources, artifact hashes, and timestamps are separate |
| Conditions not met means no recommendation | `insufficient_data` triggers more discovery; it is never relabeled as “no candidates” |
| Complete the task from the screening request | Plan-gated bulk statements automatically route to provider-prefilter or stratified estimate enrichment before selected-name primary-source underwriting |

## Version 3.3 Evidence and Runtime Controls

| Original requirement | v3.5 implementation |
|---|---|
| Do not mix old and current data/processes | Runtime version, contract, schema, and fingerprint are embedded and hard-validated. |
| Do not uncritically use consensus | EPS/FCF is independently rebuilt from operating drivers; circular numerator checks fail. |
| Distinguish GAAP and adjusted forecasts | Driver-derived GAAP and after-tax adjustments separately tie to the reconciliation. |
| Standard FCF and source period integrity | TTM construction method and every component-period source are verified. |
| Do not overstate cash or EV/FCF | Corporate cash normalization and customer/restricted-fund separation feed evaluator-calculated EV. |
| Treat product concentration/LOE structurally | Biopharma aliases normalize to commercial-biopharma and require concentration/LOE/6x/8x stress. |
| Do not use peak cyclical profits | `peak_profit_risk=true` forces sourced normalization even with a low numeric cycle score. |
| Important numbers need sources | ROIC, EBITDA, cash, TTM periods, sector evidence, and forecasts affect quality points and caps. |
| Do not overclaim scope | Audited bounded pools produce explicitly scoped conclusions; market-wide no-candidates requires full economic coverage. |

## Version 3.5 Discovery and Autonomy Controls

| Original requirement | v3.5 implementation |
|---|---|
| Screen the requested US small/mid-cap range | Immutable `user_requested_scope` plus separately audited `executed_scope`; internal single-band narrowing is rejected |
| Exclude extreme illiquidity using trading liquidity | 20+ session ADDV provenance contract; raw one-session volume is ignored |
| Use current Forward P/E and do not mix periods | Dated NTM/FY1 normalization, price/EPS reconciliation, analyst breadth, range-dispersion and continuity checks |
| Do not force the user to supervise internal steps | Exit code 2 and `next-action` are same-execution continuation; selected-set commitment requires every selected name to finish |
