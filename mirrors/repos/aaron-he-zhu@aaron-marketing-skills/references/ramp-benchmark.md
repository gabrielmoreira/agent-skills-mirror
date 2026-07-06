# RAMP Benchmark — Product Launch Evaluation Standard

The sixth framework in this library, alongside [CORE-EEAT](core-eeat-benchmark.md) (content quality), [CITE](cite-domain-rating.md) (domain authority), [C³](c3-benchmark.md) (influencer), [ROAS](roas-benchmark.md) (paid ads), and [SEND](send-benchmark.md) (email). RAMP scores a **product launch** — named for the launch ramp the whole discipline climbs — across four goal-weighted levers whose initials spell the name. It is deliberately **use-case-agnostic**: the same four dimensions score a B2B SaaS sales-led launch, a developer-tool community launch, and a mobile app-store launch; the *goal-weight column* encodes which one you are running. Platform-specific tactics (vote-velocity heuristics, karma ladders, submission-hour lore) are **never sub-items** — they live in skill reference packs as Estimated values with named sources.

**Keyless by design**: every input comes from the user's **own data or public keyless surfaces** — the positioning canvas and launch plan (user-provided), the claims ledger and launch-registry records (project memory), own analytics exports (GA4/store console, manual export), and public launch telemetry via the keyless/free-key connectors (`hn.py`, `producthunt.py`, `appstore.py`, `gdelt.py`). Keyed launch platforms and commercial ASO suites are an optional Tier-2/3 MCP convenience, **never a Tier-1 precondition**.

## The four dimensions (R · A · M · P)

| Letter | Dimension | What it measures |
|--------|-----------|------------------|
| **R** | **Readiness** | Positioning clarity, ICP/beachhead fit, launch tier & type declared, **stage-truth** (draft→concept→alpha→beta→GA honesty vs launch-registry), timing window, risk register, internal readiness, KPI targets set pre-launch |
| **A** | **Assets** | Message house & narrative spine, **claim substantiation** (vs the claims ledger), press kit, per-channel asset kits to documented spec, pricing/packaging clarity, enablement, landing message-match, technical go-live pass |
| **M** | **Momentum** | Channel mix vs tier (owned/rented/borrowed balance), T-minus timeline & embargo coordination, **platform-rule compliance**, launch-day runbook quality, media/community activation, live monitoring coverage |
| **P** | **Proof** | Measurement instrumentation on every launch surface, KPI actuals vs targets (D0/W1/M1), attribution read, spike-vs-sustain retention, feedback loop, compliant social-proof pipeline, retro & next-moment discipline |

Mnemonic for the levers: **is it worth launching (R) → is the kit ready (A) → can you move the market on the day (M) → what survives the spike (P)**. The same four letters also frame the lifecycle as the **RAMP loop**: Research → Assemble → Mobilize → Prove — the phase directories under `launch/`.

## Scoring chassis

| | |
|---|---|
| Per sub-item | Pass = 10 · Partial = 5 · Fail = 0 |
| Dimension score | mean of sub-items × 10 → 0–100 |
| Rollup | **arithmetic goal-weighted mean** (same chassis as CITE / ROAS / SEND), floor-rounded — **not** C³'s geometric CVI |
| Rating bands | 90–100 Excellent · 75–89 Good · 60–74 Medium · 40–59 Low · 0–39 Poor |
| Veto-cap | delegated to [auditor-runbook.md](auditor-runbook.md) §2 — single veto caps the weighted overall at `min(raw, 60)`; 2+ veto fails → `status: BLOCKED` |

**Launch Quality Score (LQS, 0–100)** = `floor(weighted({R, A, M, P}, goal-weights))`. ⚠ The LQS (a 0–100 quality score) is **not** any single launch KPI (upvotes, day-one signups, press mentions, downloads); those KPIs are *inputs* to the dimensions.

### Sub-items (40 = 4 × 10, Pass / Partial / Fail each — all channel-agnostic)

- **R** — positioning canvas complete (named competitive alternatives, unique attributes, value themes) · ICP/beachhead segment defined and matched to launch scope · launch tier & type declared (T1/T2/T3; new-product / feature / relaunch / partnership) with effort calibrated · **stage-truth: announced stage matches verifiable public access + pricing state** · timing window chosen deliberately (event cycles, competitor calendar, review-latency buffers) · competitor launch teardown reviewed for counter-positioning · early-access program design sound (stage gating + graduation criteria) where applicable · risk register exists (likelihood × blast-radius, owners, kill criteria / rollback thresholds) · internal readiness (support/sales/CS briefed, owners + escalation path) · launch KPI targets (D0/W1/M1) declared before launch.
- **A** — message house complete (tagline, one-liner, value pillars, per-persona proof points) · narrative spine (PR-FAQ or equivalent) in launch-day tense, numbers over adjectives · **every product/comparative claim substantiated in the claims ledger with required disclosures** · press kit complete (factsheet, boilerplate, logo/screenshot/video, contact) · per-channel asset kits complete per tier to each surface's documented spec (store listing character limits cite the stores' official docs) · pricing & packaging clear (tiers, launch-offer terms, guarantee/refund) · sales/support enablement ready where sales-led · announcement ↔ landing ↔ offer message-match · technical go-live pass (robots/staging flip, sitemap, OG/rich-snippet tags, analytics events verified) · localization/regional variants prepared where the audience requires (including non-EN channels).
- **M** — channel mix fits tier & use-case (owned/rented/borrowed balance, no single-channel dependence) · T-minus timeline exists and is being met · embargo & partner commitments coordinated against one authoritative date/stage (the launch-registry record) · **platform-rule compliance per channel — no vote/engagement solicitation, community norms honored, store precheck clean** · launch-day runbook hour-blocked (act/watch/consolidate) with owners and forced go/rollback observation windows · media/analyst/community activation right-sized and personalized under embargo sequence · owned-channel activation (announcement email, changelog, blog) sequenced with the moment · community engagement plan (reply ownership, response expectations, objection handling) · live monitoring coverage during the window with alert thresholds · launch-stacking guardrail respected (spacing since the last Tier-1 moment).
- **P** — **measurement instrumentation: every launch surface tagged (UTM/conversion events) and verified pre-launch** · KPI actuals vs targets tracked D0/W1/M1 with Measured/User-provided/Estimated labels · per-channel attribution reconciled against own analytics (not platform self-reported) · spike-vs-sustain: week-2 retention of traffic/signups tracked against the launch spike · owned-capture rate (launch traffic → email/community) measured · feedback loop live (themes, status transitions, requester notification) · social-proof pipeline compliant (**no incentivized store reviews**; incentives only where the platform allows) · retro completed (channel actual-vs-target, 5-whys on misses, keep/kill) · learnings promoted to memory + launch-registry outcome snapshot · momentum plan (T+1→T+30) and next launch moment identified.

### Goal-weight columns (each sums to 1.0)

| Goal | R | A | M | P |
|------|---|---|---|---|
| **B2B SaaS / sales-led** | 0.30 | 0.35 | 0.15 | 0.20 |
| **Dev-tool / community** | 0.20 | 0.20 | 0.35 | 0.25 |
| **Mobile / app-store** | 0.35 | 0.25 | 0.20 | 0.20 |

- B2B SaaS weights: `LQS_b2b = R×0.30 + A×0.35 + M×0.15 + P×0.20`
- Dev-tool / community weights: `LQS_devtool = R×0.20 + A×0.20 + M×0.35 + P×0.25`
- Mobile / app-store weights: `LQS_mobile = R×0.35 + A×0.25 + M×0.20 + P×0.20`

*Rationale:* a sales-led B2B launch lives on positioning and enablement, and its pipeline outlives the spike (R + A = 0.65). A dev-tool community launch concentrates its fate into the launch window itself and what survives it (M + P = 0.60). A mobile launch is dominated by review/listing readiness before the store will even carry the moment (R + A = 0.60, R heaviest).

### Worked examples (golden-math fixture)

Kept here so `scripts/golden-auditor-math.py` can assert the arithmetic deterministically. Input vector `R=80 A=75 M=70 P=78`:

- **B2B SaaS / sales-led goal** → 24 + 26.25 + 10.5 + 15.6 = `floor(76.35) = 76`.
- **Dev-tool / community goal** (same vector) → 16 + 15 + 24.5 + 19.5 = `floor(75.0) = 75`. (Weighting toward Momentum + Proof *lowers* a community read on a launch whose weakest lever is the day itself — the weights encode the goal.)
- **Mobile / app-store goal** (same vector) → 28 + 18.75 + 14 + 15.6 = `floor(76.35) = 76`.
- **Veto-capped** — if R1 (stage-truth) fails on the B2B example, the weighted overall is capped: `min(76, 60) = 60`, `cap_applied: true`.

## Veto items (red lines — stable IDs, distributed R:1 / A:1 / M:1 / P:1)

| ID | Dimension | Trigger |
|----|-----------|---------|
| **R1** | Readiness | **Stage-truth violation** — announcing GA without verifiable public access + a live pricing page, or a beta dressed as GA. Judged against the stage record in [launch-registry](../protocol/launch-registry/SKILL.md) (`memory/launch-registry/`). *No stage record on file* = **NEEDS_INPUT**, not pass-by-default. |
| **A1** | Assets | **Claim integrity** — false / unsubstantiated product or comparative claim, or missing required disclosure, in launch copy (checked against `memory/claims/claims-ledger.md` — same red line as ROAS O1 / SEND D1). |
| **M1** | Momentum | **Platform manipulation / policy** — soliciting votes/engagement rings on community platforms, breaching an embargo commitment, or store-precheck-class violations (placeholder text, dead URLs, future-functionality promises). *Carve-out:* asking your audience for **feedback** (not votes) = Pass. |
| **P1** | Proof | **Measurement broken** — launch surfaces untagged/untracked so traction is unverifiable (mirrors ROAS R1). *Carve-out:* privacy-limited modeled data, clearly labeled, = Partial, **not** a veto. |

**Launch-stacking / audience fatigue** (back-to-back Tier-1 moments burning the same audience) is a high-severity **guardrail/flag under M**, *not* a veto — it wastes attention and suppresses the next launch's ceiling, but it does not by itself make the LQS untrustworthy (mirrors ROAS's premature-scaling and SEND's over-frequency guardrails).

## Data contract (keyless inputs)

| Need | Source (own data / keyless public) |
|------|-------------------------------------|
| R / positioning, tier, timing, risk register | user's positioning canvas + launch plan (User-provided) |
| R1 (stage-truth) | public access check + live pricing page + the stage record in `memory/launch-registry/` (**no record = NEEDS_INPUT**) |
| A / message house, press kit, enablement | the launch asset manifest (User-provided; completeness is checkable) |
| A1 (claim integrity) | approved wording + required disclosures from `memory/claims/claims-ledger.md` |
| A / store listing spec compliance | official App Store Connect / Play Console documented limits (cite the stores, not third-party tools) |
| A / technical go-live | `technical-seo-checker` pass + own analytics event verification |
| M / platform rules | each platform's published guidelines; community norms labeled Estimated with named sources when undocumented |
| M·P / launch-window telemetry | `hn.py` (keyless Algolia + Firebase), `producthunt.py` (free-key developer token), `appstore.py` (keyless documented endpoints), `gdelt.py` (news echo) — see [CONNECTORS.md](../CONNECTORS.md) |
| P / conversion & attribution | GA4 / own analytics export with UTM truth set — **not** platform self-reported numbers |
| P / feedback & social proof | own feedback board / review exports; store-review incentive rules per the stores' policies |

## Naming disambiguation

RAMP's veto IDs **R1** and **A1** collide *textually* with ROAS's **R1** (conversion tracking broken) and **A1** (brand/placement safety) — the letters and numbers match but the meanings are unrelated, and RAMP-R (Readiness) has nothing to do with ROAS-R (Return). Each framework's letters and veto IDs are independent. In any shared document (e.g. [auditor-runbook.md](auditor-runbook.md) §2/§5) always qualify the letter with the framework name (`RAMP-R1` vs `ROAS-R1`); the runbook lists RAMP vetoes under a Launch sub-heading. The LQS is likewise distinct from RQS (ROAS) and EQS (SEND).

## Where it is used

The launch skills apply RAMP across the **RAMP loop** — Research → Assemble → Mobilize → Prove (directories under `launch/<phase>/`). Only [launch-readiness-auditor](../launch/mobilize/launch-readiness-auditor/SKILL.md) computes the goal-weighted LQS and runs the four vetoes; every other skill operates on a single lever and hands off.

- **Research (R)** — [positioning-mapper](../launch/research/positioning-mapper/SKILL.md) builds the positioning canvas; [launch-tier-planner](../launch/research/launch-tier-planner/SKILL.md) declares tier/type and owns the risk register + kill criteria; [launch-window-planner](../launch/research/launch-window-planner/SKILL.md) picks the window; [early-access-designer](../launch/research/early-access-designer/SKILL.md) designs the waitlist→GA stage ladder (the upstream of `R1` stage-truth). Stage/date/embargo facts come from [launch-registry](../protocol/launch-registry/SKILL.md).
- **Assemble (A)** — [message-house-builder](../launch/assemble/message-house-builder/SKILL.md) produces the messaging hierarchy + PR-FAQ spine (claims marked for the ledger — the upstream of `A1`); [launch-asset-packager](../launch/assemble/launch-asset-packager/SKILL.md) owns the tier-scoped asset manifest incl. press kit + store listing spec + technical go-live checklist; [pricing-packaging-planner](../launch/assemble/pricing-packaging-planner/SKILL.md) owns launch pricing/packaging; [sales-enablement-kit](../launch/assemble/sales-enablement-kit/SKILL.md) derives the internal kit.
- **Mobilize (M gate phase)** — [launch-readiness-auditor](../launch/mobilize/launch-readiness-auditor/SKILL.md) is the auditor-class gate (LQS + R1/A1/M1/P1 + T-1 go/no-go mode, artifacts at `memory/audits/launch/`); [launch-day-conductor](../launch/mobilize/launch-day-conductor/SKILL.md) runs the hour-blocked runbook; [community-launch-runner](../launch/mobilize/community-launch-runner/SKILL.md) executes community/directory submissions under platform rules (incl. regional/中文 channels); [press-media-relations](../launch/mobilize/press-media-relations/SKILL.md) runs the media/analyst motion.
- **Prove (P)** — [launch-monitor](../launch/prove/launch-monitor/SKILL.md) tracks the T-0→T+30 window; [launch-feedback-synthesizer](../launch/prove/launch-feedback-synthesizer/SKILL.md) triages feedback + harvests compliant social proof; [launch-retro-analyzer](../launch/prove/launch-retro-analyzer/SKILL.md) runs the D1/W1/M1 retro; [momentum-planner](../launch/prove/momentum-planner/SKILL.md) fights the second-week cliff and books the next moment.

Reused cross-discipline (counted in their home phases): `audience-mapper`, `trend-spotter`, `budget-optimizer`, `landing-optimizer`, `campaign-planner` (creator lane), `outreach-manager` (pitch mechanics), `content-amplifier`, `email-creative-builder` / `email-sequence-designer` / `cold-outbound-sequencer`, `campaign-architect` / `ad-creative-builder`, `page-play-builder` / `content-writer`, `technical-seo-checker` / `serp-markup-builder`, `performance-monitor`, `keyword-research`, `entity-optimizer`, `offer-claims-registry`, `consent-registry`, `list-growth-designer`, `roi-calculator` / `performance-analyzer` / `report-generator`.

> **Provisional**: RAMP is a new framework. Treat its bands as provisional until calibrated against ~30 real launch audits in `memory/audits/launch/`, per the runbook's calibration discipline.
