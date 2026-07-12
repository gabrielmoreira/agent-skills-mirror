# C³ Benchmark — Influencer Marketing Evaluation Standard

C³ evaluates influencer marketing at three separate scopes: **Creator · Content · Campaign**, using the **ACE · ART · ROI** rubrics. It is an advisory quality-control framework, not a validated predictor of campaign outcomes.

This file is the human entry point. Executable identity, profiles, evidence policy, missingness, vetoes, and rollup constraints live in [`framework-catalog.json`](framework-catalog.json); shared semantics live in [`scoring-semantics.md`](scoring-semantics.md). The detailed item anchors live under [`references/c3/`](c3).

## The Three Scopes

| Scope | Rubric | Unit | Core question |
|---|---|---|---|
| **Creator** | **ACE** | One creator, platform, comparison window, and observation date | Is the creator's audience asset credible and behaviorally healthy? |
| **Content** | **ART** | One deliverable or tightly defined asset set | Is the work appealing, relevant, compliant, and truthful? |
| **Campaign** | **ROI** | One initiative, attribution window, and declared goal | What return, orchestration quality, and impact were observed or forecast? |

ACE is a reusable creator baseline only when it excludes campaign-specific brand fit. A specific brand/category conflict belongs in `ROI.O1`. Naming follows the value chain; report drill-down may run `Campaign → Creator → Content`.

## Dimensions and Ownership

| Scope | Dimensions | Boundary corrections |
|---|---|---|
| **ACE** | **A**udience Asset · **C**redibility · **E**ngagement | `A1` is audience composition/stability, not brand fit; `A3` is reach reliability, not campaign-tier fit; `C4` is commercial saturation/history; `E3` is repeat audience action, not campaign conversion. |
| **ART** | **A**ppeal · **R**elevance · **T**ransparency | Scores the actual deliverable; disclosure and claim integrity are veto-bearing. |
| **ROI** | **R**eturn · **O**rchestration · **I**mpact | Owns brand conflict, campaign conversion, incrementality, and realized outcomes. |

Each dimension contains four stable item IDs. The detailed rubrics define the anchors; the catalog defines item identity and policy.

## Scoring

Per item: Pass = 10, Partial = 5, Fail = 0. A scope score is the floor-rounded, profile-weighted mean of its three dimensions. A score is emitted only at 100% coverage of applicable items. Missing evidence is `unknown` and prevents a score; catalog-authorized `na` requires a reason.

Profiles are scope × goal: `ace-*`, `art-*`, and `roi-*`, where the goal is `awareness`, `engagement`, `conversion`, or `brand-building`. Do not compare profiles as though their weights were identical.

Exactly one verified veto failure caps that scope at `min(raw, 59)`. Two or more verified veto failures produce `verdict: BLOCK` with no final score. Missing veto evidence is `unknown`, not a failure. See [`scoring-semantics.md`](scoring-semantics.md) for status/verdict behavior.

### Campaign Value Index

After one complete ACE, ART, and ROI result exists, C³ may report:

`CVI = floor((ACE × ART × ROI)^(1/3))`

When a campaign has multiple creators or assets, keep the budget-weighted ACE mean and equal-weighted ART mean exact through the geometric product. Do not floor either component mean before the one final CVI floor.

The three components must share one `rollup_id`, goal, `observed_at`, `assessment_time`, and catalog version. A forecast CVI contains forecast components only; an actual CVI contains actual components only. Never replace missing actual outcomes with forecast values or combine unrelated creators/assets/campaigns merely because their dates match. Always show the three scope scores beside CVI because the components diagnose what the index only summarizes.

For one creator/asset/campaign triplet, `c3-rollup` accepts the legacy three-result `scopes` array. For a real multi-creator campaign, use the typed [`c3-rollup.schema.json`](c3-rollup.schema.json) `components` form: ACE is budget-weighted, ART is equal-weighted, and exactly one ROI result is used. Multiple ACE entries require explicit positive weights; ART/ROI reject weights so the aggregation rule cannot drift silently.

Golden fixtures:

- No veto: `ACE=90`, `ART=80`, `ROI=70` → `CVI=79`.
- One ACE veto: raw ACE capped to `59`, `ART=80`, `ROI=70` → `CVI=69`.
- A blocked component has no final scope score, so CVI is not emitted.

## Veto Items

| Qualified ID | Trigger |
|---|---|
| `C3-ACE.A2` | Verified follower fraud or a measured real-follower rate below the rubric threshold. Refused/missing access is `unknown`. |
| `C3-ACE.C1` | Documented disqualifying brand-safety evidence under the declared policy and observation window. |
| `C3-ACE.E2` | Verified bought, coordinated, or pod-based engagement. |
| `C3-ART.T1` | Missing or materially inadequate disclosure where a material connection exists. |
| `C3-ART.T2` | False or unsubstantiated material claim in the deliverable. |

Disclosure requirements depend on market and relationship. For U.S. work, the framework uses FTC Endorsement Guides and the Consumer Reviews and Testimonials Rule as compliance inputs. This is not legal advice.

## Benchmark Regimes

Audience, reach, engagement, return, and impact are relative to a locked creator-tier × platform × niche cohort and stated window. Compliance and control-presence items use explicit criterion anchors. A platform-wide number without cohort, source, and date is an estimate, not a universal pass/fail threshold.

## Components

- [`c3/scoring-architecture.md`](c3/scoring-architecture.md) — item scoring, profiles, boundaries, and rollup
- [`c3/ace-creator-benchmark.md`](c3/ace-creator-benchmark.md) — Creator/ACE anchors
- [`c3/art-content-benchmark.md`](c3/art-content-benchmark.md) — Content/ART anchors
- [`c3/roi-campaign-benchmark.md`](c3/roi-campaign-benchmark.md) — Campaign/ROI anchors

## Skill Ownership

- **Discover** — [`fit-scorer`](../influencer/discover/fit-scorer/SKILL.md) produces ACE; `influencer-discovery` only supplies candidates/evidence.
- **Activate** — [`content-reviewer`](../influencer/activate/content-reviewer/SKILL.md) produces ART and applies `ART.T1/T2`.
- **Measure** — [`roi-calculator`](../influencer/measure/roi-calculator/SKILL.md) produces ROI and CVI; `performance-analyzer` supplies measured inputs.

All outputs remain advisory until the versioned profile passes the reliability and outcome-calibration protocol in [`scoring-semantics.md`](scoring-semantics.md).
