# ECHO Benchmark — Organic Social Evaluation Standard

The seventh framework in this library, alongside [CORE-EEAT](core-eeat-benchmark.md) (content quality), [CITE](cite-domain-rating.md) (domain authority), [C³](c3-benchmark.md) (influencer), [ROAS](roas-benchmark.md) (paid ads), [SEND](send-benchmark.md) (email), and [RAMP](ramp-benchmark.md) (launch). ECHO scores an **organic social presence** — named for what community marketing actually is (resonance, not broadcast) and for dark social, the echo of your work you cannot directly observe — across four goal-weighted levers whose initials spell the name. It is deliberately **use-case-agnostic**: the same four dimensions score a B2C brand running feed-first channels, a dev-tool company living in communities, and a B2B founder-led motion on LinkedIn-class platforms; the *goal-weight column* encodes which one you are running. Platform folklore (posting-hour lore, hashtag-count rules, algorithm superstition) is **never a sub-item** — it lives in the dated norm cards under `references/platforms/` as Estimated values with named sources and last-verified dates.

**Keyless by design**: every input comes from the user's **own data or public keyless surfaces** — the channel dossiers and voice cards (project memory), the claims ledger (project memory), own analytics exports (GA4/GSC and the platforms' native analytics, manual export), and public social telemetry via the keyless connectors (`bluesky.py`, `fediverse.py`, `discourse.py`, `youtube.py --rss`, `hn.py`, `gdelt.py`, `pageviews.py`, `tavily.py`). X/Instagram/TikTok/LinkedIn have **no compliant keyless read surface** — their numbers enter only as user-exported analytics (Measured, as-of date) or as proxy reads (GDELT/Tavily/Bluesky-as-adjacent-signal) that must be **labeled proxy, never Measured**. Keyed social suites are an optional Tier-2/3 MCP convenience, never a Tier-1 precondition.

## The four dimensions (E · C · H · O)

| Letter | Dimension | What it measures |
|--------|-----------|------------------|
| **E** | **Embeddedness** | Right-channel presence and genuine community standing — **channel-truth** (activity matches the channel-registry dossier), participation-before-promotion, give:ask discipline, rule digests current, profile/handle governance |
| **C** | **Craft** | Platform-native content quality plus claim/disclosure integrity — **claims match the ledger**, **required disclosures present**, dated-norm-card adaptation (no verbatim cross-posting), hook/payload match, accessibility, voice adherence |
| **H** | **Hosting** | Running the presence as a host — zero manufactured engagement, UGC permissions, inbox SLAs, crisis protocol, cadence consistency, advocacy voluntariness, selling-block discipline, moderation |
| **O** | **Observability** | Measurement integrity including dark social — declared denominators, dark-social method declared, locked competitor panel, median rollups, EMV exclusion, instrumentation coverage, listening baseline, write-back loop |

Mnemonic for the levers: **are you genuinely there (E) → is the work native and honest (C) → do you host, not broadcast (H) → do you know what actually happened (O)**. The same four letters also frame the lifecycle as the **ECHO loop**: Explore → Craft → Host → Observe — the phase directories under `social/`.

## Scoring chassis

| | |
|---|---|
| Per sub-item | Pass = 10 · Partial = 5 · Fail = 0 |
| Dimension score | mean of sub-items × 10 → 0–100 |
| Rollup | **arithmetic goal-weighted mean** (same chassis as CITE / ROAS / SEND / RAMP), floor-rounded — **not** C³'s geometric CVI |
| Rating bands | 90–100 Excellent · 75–89 Good · 60–74 Medium · 40–59 Low · 0–39 Poor |
| Veto-cap | delegated to [auditor-runbook.md](auditor-runbook.md) §2 — single veto caps the weighted overall at `min(raw, 60)`; 2+ veto fails → `status: BLOCKED` |

**Social Quality Score (SQS, 0–100)** = `floor(weighted({E, C, H, O}, goal-weights))`. ⚠ The SQS (a 0–100 quality score) is **not** any single social KPI (followers, engagement rate, reach, mentions); those KPIs are *inputs* to the dimensions. SQS is likewise distinct from the GEO/SEO Scores, CVI, RQS, EQS, and LQS.

### Sub-items (40 = 4 × 10, Pass / Partial / Fail each — all platform-agnostic)

- **E** — **channel-truth: every active handle has a [channel-registry](../protocol/channel-registry/SKILL.md) dossier and its activity matches the recorded state, voice card, and posting rules** · participation-before-promotion (account history/tenure meets each community's norms; `warming → active` graduation evidence on file) · give:ask ledger maintained per community (ledger presence is scored; the target ratio itself is a labeled Estimated heuristic) · per-community rule digest current (last-verified date) and platform red-lines checked before posting · profile/bio/link-in-bio complete, message-matched, and versioned in the registry · owned-space entry and member-lifecycle health designed where an owned community exists (entry paths, lifecycle stages, exit hygiene) · platform-capability fit — each channel's role matches the portfolio matrix (publish/comments/DM/insights capability and documented access class vs the declared objective) · handle governance recorded (credential holder, 2FA, verification state, handle-squat audit done) · bio-link freshness — links and pinned assets re-verified on a schedule, no dead links · cross-community rule-conflict check before multi-community pushes (no one-size blast into rule-divergent spaces).
- **C** — **every product/offer claim in social copy matches the approved wording in the claims ledger** · **required disclosures present — material-connection tags on employee/founder/advocate endorsements and AI-disclosure on realistic synthetic media** · platform-adapted per the dated norm card, never verbatim cross-posting · hook matches payload; format specs (char limits, visible-fold cutoffs, aspect ratios) cite the dated norm card · accessibility pack complete (alt text, captions/subtitles, text-safe zones) · voice-card adherence (per-platform register, banned phrases respected, few-shots from own posts only) · pillar-allocation adherence — the published mix tracks the declared content pillars within the calendar's tolerance · evergreen recycled only with a freshness pass (dates, prices, claims re-checked at each recycle) · link and first-comment placement per the platform norm card · short-video beat-sheet completeness where video ships (timestamped hook/confirmation/payoff/CTA, on-screen text, spec-only — no rendering claims).
- **H** — **zero manufactured or baited engagement — no pods, no bought followers/engagement, no automated replies/DMs, no like/tag/share/comment-bait mechanics** · **UGC republished only with a recorded permission entry in the registry's `ugc-permissions.md`** · inbox SLA attainment vs the declared response tiers per channel · crisis protocol on file including the pause-the-queue rule (all scheduled posts AND paid amplification) · cadence consistency vs the committed calendar (the over-posting guardrail's scored twin — sustained over- or under-posting is flagged here) · advocacy voluntariness (opt-in evidence, per-person variation, staggered human posting) · selling-block cadence adherence (founder/seller daily engagement blocks honored; warm-touch-before-ask sequencing evidenced) · escalation matrix live (commenter-taxonomy routing with named owners, ending at the crisis path) · moderation ladder and house rules current in owned spaces, enforcement logged · advocate-roster hygiene (disclosure lines and opt-in dates on file; periodic per-person-variation spot-check done).
- **O** — **declared, period-stable denominators on every reported rate; no proxy-sourced number presented as Measured** · dark-social method declared and Estimated-labeled before any social-ROI claim · locked competitor panel for share-of-voice (a panel switch restarts the trend; sentiment-weighting labeled) · median-not-mean per-post rollups with organic and boosted separated · EMV/vanity metrics excluded from any score (labeled exec-translation only) · dark-social instrumentation coverage (share-link/UTM hygiene live plus a self-reported attribution field running) · 7-day listening baseline maintained with spike thresholds set · listening-query architecture current (brand variants incl. 中文 names and misspellings, exclusion terms, per-source syntax reviewed on schedule) · community-health metrics employee-excluded (orbit-level distribution and time-to-first-response measured without staff inflation) · learnings written back — best/worst performers promoted to memory and consumed by the next calendar cycle.

### Goal-weight columns (each sums to 1.0)

| Goal | E | C | H | O |
|------|---|---|---|---|
| **Community / dev-tool** | 0.30 | 0.20 | 0.30 | 0.20 |
| **B2C brand** | 0.10 | 0.45 | 0.25 | 0.20 |
| **B2B founder-led** | 0.20 | 0.30 | 0.15 | 0.35 |

- Community / dev-tool weights: `SQS_community = E×0.30 + C×0.20 + H×0.30 + O×0.20`
- B2C brand weights: `SQS_b2c = E×0.10 + C×0.45 + H×0.25 + O×0.20`
- B2B founder-led weights: `SQS_founder = E×0.20 + C×0.30 + H×0.15 + O×0.35`

*Rationale:* for a dev-tool, community standing and hosting ops **are** the growth engine — credibility dies on inauthentic participation (E + H = 0.60). A B2C brand plays to feed-first audiences where craft dominates and embeddedness is lightest because reach is broadcast-shaped (C = 0.45). A B2B founder-led motion is carried by dark-funnel attribution truth and founder-post craft; H is lightest because there is rarely an owned community to moderate — its selling-cadence items are a minority of H's ten — while pipeline truth lives in O (C + O = 0.65). ⚠ *B2C data caveat:* the B2C column's O dimension leans hardest on **manually exported** platform analytics — IG/TikTok/小红书 have no compliant keyless connector — so B2C users should expect a thinner Measured column than dev-tool (Discourse/HN/Bluesky) or founder-led (GA4/GSC) users; the labels make that visible rather than hiding it.

### Worked examples (golden-math fixture)

Kept here so `scripts/golden-auditor-math.py` can assert the arithmetic deterministically. Input vector `E=80 C=75 H=70 O=78`:

- **Community / dev-tool goal** → 24 + 15 + 21 + 15.6 = `floor(75.6) = 75`.
- **B2C brand goal** (same vector) → 8 + 33.75 + 17.5 + 15.6 = `floor(74.85) = 74`. (The same vector drops a band: weighting toward Craft *lowers* a B2C read on a presence whose weakest lever is execution polish — the weights encode the goal.)
- **B2B founder-led goal** (same vector) → 16 + 22.5 + 10.5 + 27.3 = `floor(76.3) = 76`.
- **Veto-capped** — if ECHO O1 (denominator integrity) fails on the founder-led example, the weighted overall is capped: `min(76, 60) = 60`, `cap_applied: true`.

## Veto items (red lines — stable IDs, distributed E:1 / C:2 / H:2 / O:1)

| ID | Dimension | Trigger |
|----|-----------|---------|
| **E1** | Embeddedness | **Channel-truth violation** — activity on a handle/channel with no [channel-registry](../protocol/channel-registry/SKILL.md) record (`memory/channels/`), or contradicting its dossier (state, voice card, posting rules). *No record on file* = **NEEDS_INPUT**, not pass-by-default. *Carve-out:* `warming`-state channels get N/A handling on promotion-dependent items — not a veto. |
| **C1** | Craft | **Claim integrity** — product/offer claim in social copy absent from or contradicting `memory/claims/claims-ledger.md` (same red line as ROAS O1 / SEND D1 / RAMP A1). *Carve-out:* opinion/culture posts making no product claim need no ledger entry. |
| **C2** | Craft | **Disclosure failure** — undisclosed material connection on an employee/founder/advocate endorsement, or undisclosed realistic synthetic media (FTC, 《互联网广告管理办法》, EU AI Act Art. 50). *Carve-out:* opinion posts with no product endorsement need no disclosure line; obviously stylized/non-realistic generative art per platform policy. |
| **H1** | Hosting | **Manufactured or baited engagement** — engagement pods, bought followers/engagement, coordinated identical reshares, automated replies/DMs, or explicit like/tag/share/comment-bait mechanics (platform-manipulation ToS across all networks). *Carve-out:* genuine questions/feedback asks ≠ bait (the RAMP M1 feedback carve-out); voluntary opt-in advocates posting in their own words with disclosure ≠ pod. |
| **H2** | Hosting | **UGC permission missing** — republishing user content without a recorded permission entry in the registry's `ugc-permissions.md`. Public posting, tagging, or branded-hashtag use is **never** permission; organic consent **never** covers paid/ad use. *Carve-out:* platform-native share/repost/retweet inside the origin platform with attribution preserved ≠ republishing. |
| **O1** | Observability | **Denominator integrity broken** — any reported engagement rate without a named denominator, a denominator switched across periods, or proxy-sourced numbers (GDELT/Tavily/Bluesky-as-adjacent-proxy) presented as Measured. *Carve-out:* proxies pass when labeled proxy; internal scratch analyses not reported outward are not gated. |

**Over-posting / cadence-over-capacity** (posting past the committed calendar and inbox SLA capacity, trend-hijack velocity beyond what the team can host) is a high-severity **guardrail/flag under H**, *not* a veto — it burns audience attention and erodes trust, but it does not by itself make the SQS untrustworthy (mirrors ROAS's premature-scaling, SEND's over-frequency, and RAMP's launch-stacking guardrails). Its fact base is the registry's `calendar-commitments.md`.

## Data contract (keyless inputs)

| Need | Source (own data / keyless public) |
|------|-------------------------------------|
| E / channel-truth, states, cadence commitments | the dossiers in `memory/channels/` (**no record = NEEDS_INPUT**) |
| E / participation evidence, community standing | `discourse.py` (public forum JSON), `hn.py`, `bluesky.py` / `fediverse.py` profile+feed pulls, user platform exports |
| C / claims | approved wording in `memory/claims/claims-ledger.md` |
| C / voice + norms | the voice dossier (registry pointer) + dated norm cards in `references/platforms/` |
| C / disclosures | advocacy roster disclosure lines + per-platform paid-partnership/AI-label rules (official platform docs) |
| H / inbox, advocacy, UGC facts | inbox/advocacy logs under `memory/social/` + registry `ugc-permissions.md`, `advocate-roster.md`, `calendar-commitments.md` |
| O / own-surface truth | GA4/GSC exports with UTM truth set — never platform self-reported numbers alone |
| O / listening + SOV telemetry | `bluesky.py`, `fediverse.py`, `discourse.py`, `hn.py`, `gdelt.py` (news echo, proxy-labeled), `tavily.py` (web chatter, proxy-labeled), `pageviews.py` (attention denominator) — see [CONNECTORS.md](../CONNECTORS.md) |
| O / closed-platform metrics (X/IG/TikTok/LinkedIn/小红书) | user-exported native analytics (Measured, as-of date) or proxy reads **labeled proxy** |

## Naming disambiguation

ECHO's veto IDs collide *textually* with other frameworks' IDs — the letters and numbers match but the meanings are unrelated, and each framework's letters are independent. In any shared document (e.g. [auditor-runbook.md](auditor-runbook.md) §2/§5) always qualify the ID with the framework name. The dangerous rows:

- **ECHO O1** (denominator integrity, veto) vs **ROAS O1** (offer claim integrity, veto) — the highest-traffic same-ID pair in the library; a mixed paid+social session must always write `ECHO-O1` / `ROAS-O1`.
- **ECHO O2** (dark-social method declared, *scored item, not a veto*) vs **ROAS O2** (platform-policy violation, **veto**) — the asymmetric direction: an unqualified "O2 failed" reads as a veto in ROAS but not in ECHO.
- **ECHO E2** (participation-before-promotion, *scored item*) vs **C³ ACE E2** (authenticity, **veto**) — same asymmetry.
- **ECHO C1** (claim integrity) vs **C³ C1** (Content scope veto) and CORE-EEAT **C01** — unrelated meanings.
- ECHO **H1/H2** are collision-free — H is a fresh dimension letter in this library.

The SQS is likewise distinct from RQS (ROAS), EQS (SEND), and LQS (RAMP). The runbook lists ECHO vetoes under a Social sub-heading. (`ECHO` as a grep token also matches the shell builtin `echo` in scripts — search case-sensitively for the framework name.)

## Where it is used

The social skills apply ECHO across the **ECHO loop** — Explore → Craft → Host → Observe (directories under `social/<phase>/`). Only [social-quality-auditor](../social/host/social-quality-auditor/SKILL.md) computes the goal-weighted SQS and runs the six vetoes; every other skill operates on a single lever and hands off.

- **Explore (E)** — [channel-portfolio-planner](../social/explore/channel-portfolio-planner/SKILL.md) picks the channels and owns the capability/access matrix; [voice-dossier-builder](../social/explore/voice-dossier-builder/SKILL.md) codifies brand + founder voice and content pillars; [platform-norm-profiler](../social/explore/platform-norm-profiler/SKILL.md) maintains the dated norm cards; [participation-warmup-planner](../social/explore/participation-warmup-planner/SKILL.md) designs the pre-promotion ramp (the upstream of `E1` channel-truth and the E participation sub-items). Channel states and governance come from [channel-registry](../protocol/channel-registry/SKILL.md).
- **Craft (C)** — [social-calendar-builder](../social/craft/social-calendar-builder/SKILL.md) owns the always-on calendar (its publish step hard-requires the gate's pre-publish mode); [social-creative-builder](../social/craft/social-creative-builder/SKILL.md) turns one idea into N platform-native packages (claims marked for the ledger — the upstream of `C1`); [short-video-scripter](../social/craft/short-video-scripter/SKILL.md) writes retention-gate beat sheets; [advocacy-program-designer](../social/craft/advocacy-program-designer/SKILL.md) blueprints advocacy/founder programs (the upstream of `C2` disclosures and `H1` anti-pod rules).
- **Host (H gate phase)** — [social-quality-auditor](../social/host/social-quality-auditor/SKILL.md) is the auditor-class gate (SQS + E1/C1/C2/H1/H2/O1 + pre-publish go/no-go mode, artifacts at `memory/audits/social/`); [engagement-inbox-manager](../social/host/engagement-inbox-manager/SKILL.md) triages comments/DMs/mentions and owns the UGC permission mode (the upstream of `H2`); [social-selling-planner](../social/host/social-selling-planner/SKILL.md) runs the founder/seller operating block; [crisis-response-planner](../social/host/crisis-response-planner/SKILL.md) owns the severity ladder and the pause-the-queue rule.
- **Observe (O)** — [social-pulse-monitor](../social/observe/social-pulse-monitor/SKILL.md) runs always-on listening (query architecture, baselines, trigger watchlist); [share-of-voice-tracker](../social/observe/share-of-voice-tracker/SKILL.md) tracks SOV on a locked panel; [dark-social-attributor](../social/observe/dark-social-attributor/SKILL.md) declares the dark-social method (the upstream of the `O` dark-social sub-items); [social-measurement-loop](../social/observe/social-measurement-loop/SKILL.md) owns the metric dictionary and write-back loop (the upstream of `O1`).

Reused cross-discipline (counted in their home phases): `trend-spotter`, `audience-mapper`, `content-amplifier`, `outreach-manager`, `competitor-tracker`, `landing-optimizer`, `performance-analyzer` / `roi-calculator` / `report-generator`, `offer-claims-registry`, `community-launch-runner`, `creator-registry`, `page-play-builder`, `memory-management`.

> **Provisional**: ECHO is a new framework. Treat its bands as provisional until calibrated against ~30 real social audits in `memory/audits/social/`, per the runbook's calibration discipline.
