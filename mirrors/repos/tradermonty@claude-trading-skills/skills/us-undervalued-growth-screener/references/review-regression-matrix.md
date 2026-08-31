# Review Regression Matrix — v3.6

The first section records inherited contract-3.5 controls; the final section covers the v3.6 Claude Code acquisition architecture.

| Observed failure | Prevention | Regression/release check |
|---|---|---|
| Default USD 500M–20B request was silently changed to USD 3B–4B | Immutable `user_requested_scope`, separate `executed_scope`, and explicit authorization gate | scope-preservation and unauthorized-reduction tests |
| One-session volume was labeled as ADDV and used to build the pool | Shared average-liquidity validator requires provider average or 20+ trading days and source IDs | single-session rejection and 20-day/provider-average acceptance tests |
| FRMI-like outer-year EPS produced a misleading 4x current Forward P/E | Estimate normalizer requires a resolving NTM/FY1 horizon and clears canonical values for outer-year/pre-operating/zero-crossing data | normalizer outer-year, FY1-horizon, and FRMI regression tests |
| Five selected names were later reduced to two by model preference | Selected-set SHA-256 commitment; every selected symbol must reach a terminal verified record; budget changes require re-screening | selected-commitment and all-selected completion tests |
| Intermediate output asked the user whether to continue or choose a subset | Exit code 2 is an internal continuation signal; run-state next action is deterministic and never requires user confirmation | autonomous-continuation and no-user-choice tests |
| A cached v3.1 package produced artifacts after v3.5 was installed | Single-source runtime metadata and fingerprint in every audit/snapshot; hard mismatch rejection; `--version` on all entry points | stale-runtime and cross-script version tests |
| LLM replaced deterministic broad-screen rules with an 8% revenue gate | Script output is authoritative; soft misses remain `guideline_misses`; near-miss/high-growth/cyclical routing preserved | broad-screen near-miss and high-growth tests |
| Cyclicals were rejected instead of normalized | Cycle 3–5 or `peak_profit_risk=true` forces sourced normalization before eligibility | peak-profit and cyclical normalization tests |
| A bounded 20-name pool was treated as a full-market conclusion | Explicit conclusion scope and validated generation audit; bounded ranking/no-candidate wording | bounded-pool completion and scoped no-candidate tests |
| Candidate pool stayed unresolved while run claimed final | Exhausted + all resolved + queue zero required; checkpoint and evaluator recompute | unresolved-pool finality tests |
| Forecast bridge passed because numerator was set to EPS × shares | Driver-derived revenue/margin/interest/tax/share reconstruction; numerator is cross-check only | circular-numerator rejection and valid driver bridge tests |
| Adjusted EPS bridge did not tie back to GAAP | Driver GAAP EPS and after-tax adjustments must tie to GAAP reconciliation | adjusted bridge reconciliation tests |
| `biopharma` alias bypassed LOE controls | Sector aliases normalize to `commercial_biopharma`; concentration/LOE/6x/8x evidence required | biopharma alias LOE test |
| Peak-profit risk was flagged but normalization was marked unnecessary | `peak_profit_risk=true` overrides a low numeric cyclicality score | peak-profit normalization test |
| EV/FCF text used manual cash while evaluator could not classify cash | Ordinary cash normalization; payments/custodial cash separation; evaluator-calculated EV only | cash normalization and payments cash tests |
| Data-quality score was 100 despite missing ROIC/EBITDA evidence | Source-linked ROIC/EBITDA evidence required; fail-closed quality cap | financial-quality evidence-cap test |
| TTM FCF periods cited only the latest 10-Q | Every TTM method/component requires resolving period source IDs | TTM period-source test |
| Funnel said preflight passed 0 although selected candidates passed | Evaluator recomputes selected-candidate preflight and completion counts | funnel-count consistency test |
| Report mixed 2Y base with 3Y stress | Explicit 2Y/3Y base and 2Y/3Y contraction columns | scenario-rendering regression |
| Official-statistics label pointed to a nonofficial domain | Source kind/domain validation | official-domain validation test |
| Standalone and overlay packages differed | Build package once from canonical source, embed identical bytes, compare SHA-256 and logical contents | release packaging checks |
| Global priority selected only one factor style | Four deterministic selection lanes with quotas, sector cap, and backfill | multi-lane opportunity-type test |
| Candidate serializer dropped average-volume provenance | Broad-screen metrics preserve `average_volume` and `liquidity_source_ids` | serializer provenance test |
| Provider share-volume filters were called full-universe enumeration | Retrieval-filter inspection downgrades conclusion scope and enumeration claim | provider-prefilter scope test |
| DKS-like low-P/E name ranked despite EV/FCF 79x and sub-1% adjusted FCF yield | Post-score quality eligibility gate routes severe weak-FCF names to review | low-FCF quality-gate test |
| Driver margins were solved backwards to consensus EPS | Per-driver provenance and `target_solved=false` contract | target-solved bridge rejection test |
| SEC browse page stood in for an immutable filing | Accession-specific SEC Archives URL required | SEC browse-page rejection test |
| Generic TTM support label stood in for four discrete quarters | Exact period support paths required | discrete-period support test |
| Recent spin-off was hard-excluded as an invalid special case | Corporate-transition normalization routes to review | recent-spin-off migration test |
| One eligible name was forced into every final-three category | Category-specific thresholds and nullable labels | nullable final-three test |
| Final ZIP contained only summaries, not audit evidence | Prepublication audit plus deterministic complete-run bundle | bundle completeness test |
| Final prose asked the user to continue | Prepublication prose audit rejects unfinished-run language | continue-language rejection test |

## v3.6 Claude Code direct-FMP regressions

| Observed failure | v3.6 prevention | Regression/release check |
|---|---|---|
| Bulk FMP JSON consumed the model context before underwriting | Direct Python pipeline writes provider payloads to disk and prints a compact summary only | direct-pipeline compact-summary test |
| Existing skills duplicated FMP transport, fallback, and retry logic | GARP client is generated from the repository-level `scripts/fmp_client/` registry/special-template source of truth | generator-source/package equivalence check |
| Repeated runs refetched unchanged provider data | SQLite response cache with dataset TTLs | persistent-cache cross-client test |
| Company-screener responses silently truncated at the provider limit | Adaptive overlapping market-cap-band splitting; scope is complete only when every leaf is unsaturated | saturated-band enumeration test |
| Per-symbol liquidity work was allocated before economic relevance was known | Bulk EOD first; fallback exact-liquidity targets are chosen round-robin from the four GARP lanes | direct-pipeline lane-target test |
| Overlapping core/high-growth symbols made the provider-pool audit report too few represented lanes | Lane coverage is calculated from final candidate memberships, not only the insertion loop | overlapping-lane provider-pool test |
| Full FMP packets still burdened the model after discovery | Full payloads remain under `provider/candidate-data`; projected packets contain only underwriting-relevant fields and artifact paths | candidate-packet size/content review |
| Claude stopped and requested another user turn | `NEXT_ACTION.json` sets `user_confirmation_required=false`; Claude Code command forbids “Continue” handoff | command contract and prepublish phrase gate |
