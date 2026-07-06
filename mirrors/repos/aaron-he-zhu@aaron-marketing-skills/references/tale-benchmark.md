# TALE Benchmark — Brand Narrative & Messaging Evaluation Standard

The eighth framework in this library, alongside [CORE-EEAT](core-eeat-benchmark.md) (content quality), [CITE](cite-domain-rating.md) (domain authority), [C³](c3-benchmark.md) (influencer), [ROAS](roas-benchmark.md) (paid ads), [SEND](send-benchmark.md) (email), [RAMP](ramp-benchmark.md) (launch), and [ECHO](echo-benchmark.md) (organic social). TALE scores a **brand's narrative and messaging system** — the durable answer to "what do we say, and can we back it" that every channel discipline downstream expresses. It is deliberately **use-case-agnostic**: the same four dimensions score a B2B category-creation motion, a DTC consumer brand, and a founder/personal brand; the *goal-weight column* encodes which one you are running. Copywriting folklore (formula worship, power-word lists, headline superstition) is **never a sub-item** — TALE scores whether the message is true, coherent, consistently landed, and proven, not whether it followed a template.

**Keyless by design**: every input comes from the user's **own data or public keyless surfaces** — the positioning canvas and brand canon (project memory), the claims ledger (project memory), the live brand surfaces (own pages/decks/listings, User-provided or scraped), and public resonance telemetry via the keyless connectors reused from the other disciplines (`bluesky.py`, `gdelt.py`, `pageviews.py`, `tavily.py`, `firecrawl.py`, `wayback.py`). TALE ships **no new connector** — narrative resonance is measured with the same surfaces ECHO and the SEO/GEO monitors already use. Closed platforms (X/Instagram/TikTok/LinkedIn) have **no compliant keyless read surface**; their numbers enter only as user-exported analytics (Measured, as-of date) or as proxy reads (GDELT/Tavily/Bluesky-as-adjacent-signal) that must be **labeled proxy, never Measured**. Review-site voice (G2/Capterra/Trustpilot) has no free compliant automation — it enters only as User-provided pasted excerpts the user has the right to read.

## The four dimensions (T · A · L · E)

| Letter | Dimension | What it measures |
|--------|-----------|------------------|
| **T** | **Truth** | Positioning truth and defensible differentiation — the onlyness/difference claim **holds against named alternatives**, the positioning canvas is complete, the category frame and beachhead are chosen, and every differentiating claim is **in the ledger or marked `[needs source]`** (never asserted as fact) |
| **A** | **Architecture** | Message-system coherence — a complete message house (tagline/one-liner/pillars/proof), a strategic narrative arc, brand voice + naming rules, and a **canon record in the narrative-registry** whose hierarchy does not contradict itself |
| **L** | **Landing** | Cross-surface consistency — every flagship surface (homepage, pricing, store listing, sales deck, social bio, docs) **matches the canon**, announcement ↔ landing ↔ offer message-match holds, and per-channel adaptations point up to the canon rather than redefining it |
| **E** | **Evidence** | Proof and resonance — differentiating claims are **substantiated**, the message is **tested before scale**, resonance is measured with declared method (echo rate, share-of-voice on a locked panel, AI-answer perception), and **no proxy number is presented as Measured** |

Mnemonic for the levers: **is it true (T) → is it coherent (A) → does it land the same everywhere (L) → is it proven and does it resonate (E)**. The same four letters also frame the lifecycle as the **TALE loop**: Trace → Architect → Land → Evaluate — the phase directories under `narrative/`.

## Scoring chassis

| | |
|---|---|
| Per sub-item | Pass = 10 · Partial = 5 · Fail = 0 |
| Dimension score | mean of sub-items × 10 → 0–100 |
| Rollup | **arithmetic goal-weighted mean** (same chassis as CITE / ROAS / SEND / RAMP / ECHO), floor-rounded — **not** C³'s geometric CVI |
| Rating bands | 90–100 Excellent · 75–89 Good · 60–74 Medium · 40–59 Low · 0–39 Poor |
| Veto-cap | delegated to [auditor-runbook.md](auditor-runbook.md) §2 — single veto caps the weighted overall at `min(raw, 60)`; 2+ veto fails → `status: BLOCKED` |

**Narrative Quality Score (NQS, 0–100)** = `floor(weighted({T, A, L, E}, goal-weights))`. ⚠ The NQS (a 0–100 quality score) is **not** any single messaging KPI (recall, message pull-through, share-of-voice, sentiment); those are *inputs* to the dimensions. NQS is likewise distinct from the GEO/SEO Scores, CVI, RQS, EQS, LQS, and SQS.

### Sub-items (40 = 4 × 10, Pass / Partial / Fail each — all use-case-agnostic)

- **T** — **the onlyness/difference statement holds against named alternatives (including status quo / spreadsheet / do-nothing) — no alternative can honestly claim the same sentence** · positioning canvas complete (named alternatives, unique attributes, value themes) sourced from [positioning-mapper](../launch/research/positioning-mapper/SKILL.md) or equivalent · category frame chosen and defensible (the "only \[frame\] that…" is a category the beachhead recognizes) · beachhead/ICP truth — the narrative targets a segment scored on serviceability / pain / reachability, not "everyone" · every differentiating claim is verifiable or marked `[needs source]` and routed to the claims candidates (this framework never adjudicates a claim) · no unearned superlatives — "best/leading/#1" carries a dated, sourced basis or is cut · positioning matches shippable reality (a GA-tense narrative for a beta product is a stage-truth failure) · aspirational framing separated from claimed fact and labeled as vision · competitive alternatives named from win-loss and interviews, not a vendor feature matrix · the narrative canon exists in the [narrative-registry](../protocol/narrative-registry/SKILL.md) and is current (not a stale prior version).
- **A** — **a canon record exists in the [narrative-registry](../protocol/narrative-registry/SKILL.md) and its hierarchy is internally consistent (tagline ↔ pillars ↔ boilerplate do not contradict each other)** · message house complete (tagline, one-liner, three value pillars, per-persona proof points) · each pillar traces to a positioning value theme (no orphan pillar) · a strategic narrative arc is present (old world → the shift → the new game → the promised land → proof), not just a feature list · per-persona proof points each labeled Measured / User-provided / `[needs source]` · brand voice codified (register, tone, banned phrases, few-shots from own material only) · naming/lexicon tax defined (product/feature/tier naming rules, approved and banned terms) · boilerplate set present and consistent (25 / 50 / 100-word) · the narrative spine passes the numbers-over-adjectives and empty-chair checks · canon is versioned — a re-version supersedes atomically and the prior version is preserved append-only, never edited in place.
- **L** — **every flagship surface (homepage, pricing page, store listing, sales deck, social bio, docs) matches the canon — no surface contradicts the tagline, pillars, or claim wording** · announcement ↔ landing ↔ offer message-match holds across a campaign · per-channel angle packs are derived from the canon, not improvised at the surface · a cascade plan exists (how canon propagates to each discipline's creative builder) · localization maps to the canon (per-market adaptation points up, never redefines the message) · per-platform voice adaptations point up to the brand canon (the [channel-registry](../protocol/channel-registry/SKILL.md) `voice-dossier.md` seam — channel voice is an adaptation, not a second source of truth) · objection reframes are consistent across surfaces (the same objection gets the same answer everywhere) · proof points are placed where the claim is made (no claim on a surface without its proof) · the sales/enablement narrative repeats the same story (battle cards and talk track do not fork the message) · a message-consistency pass is run before any flagship surface ships a major change.
- **E** — **no resonance or effectiveness claim is asserted with zero Measured/User-provided evidence, and no proxy-sourced number (GDELT/Tavily/Bluesky-as-adjacent) is presented as Measured** · every differentiating claim is substantiated in `memory/claims/claims-ledger.md` or held out of the message · the message is tested before scale (comprehension / 5-second / message-market-fit panel) — design here, execution handed to the experiment builders · echo rate declared and measured (overlap of market language with the canon lexicon, method stated) · share-of-voice tracked on a locked competitor panel (a panel switch restarts the trend) · AI-answer perception probed (how answer engines describe the brand vs the canon, `tavily.py --answer`, proxy-labeled) · proof-point assets exist for each pillar (case, benchmark, demo, or testimonial the user has rights to) · a message-shift retro is run (D1 / W1 / M1 actual-vs-intended narrative pull-through) · win-loss and objection language is written back to the canon candidates · a failed message test triggers revision, not louder repetition of the same message.

### Goal-weight columns (each sums to 1.0)

| Goal | T | A | L | E |
|------|---|---|---|---|
| **B2B category** | 0.35 | 0.30 | 0.20 | 0.15 |
| **DTC brand** | 0.20 | 0.25 | 0.20 | 0.35 |
| **Founder brand** | 0.30 | 0.20 | 0.15 | 0.35 |

- B2B category weights: `NQS_b2b = T×0.35 + A×0.30 + L×0.20 + E×0.15`
- DTC brand weights: `NQS_dtc = T×0.20 + A×0.25 + L×0.20 + E×0.35`
- Founder brand weights: `NQS_founder = T×0.30 + A×0.20 + L×0.15 + E×0.35`

*Rationale:* a B2B category-creation motion lives or dies on **differentiation truth and message coherence** — you are teaching a market a new frame, so Truth and Architecture carry the weight (T + A = 0.65) and proof accrues later. A DTC consumer brand plays to feed-first audiences where **resonance and social proof** decide the read, so Evidence dominates (E = 0.35) and Truth is lightest because the positioning is rarely about named vendor alternatives. A founder/personal brand is carried by an **authentic, consistent point of view backed by proof** — Truth (the POV) and Evidence (that it lands) lead, and Landing is lightest because there are fewer owned surfaces to keep in sync (T + E = 0.65). ⚠ *DTC data caveat:* the DTC column's E dimension leans hardest on closed-platform resonance (IG/TikTok/小红书 have no compliant keyless connector), so DTC users should expect a thinner Measured column than B2B (own-site GA4/GSC + Bluesky/HN) or founder-led users — the labels make that visible rather than hiding it.

### Worked examples (golden-math fixture)

Kept here so `scripts/golden-auditor-math.py` can assert the arithmetic deterministically. Input vector `T=80 A=76 L=72 E=70`:

- **B2B category goal** → 28 + 22.8 + 14.4 + 10.5 = `floor(75.7) = 75`.
- **DTC brand goal** (same vector) → 16 + 19 + 14.4 + 24.5 = `floor(73.9) = 73`. (The same vector drops two bands' worth: weighting toward Evidence *lowers* a DTC read on a presence whose weakest lever is proof/resonance — the weights encode the goal.)
- **Founder brand goal** (same vector) → 24 + 15.2 + 10.8 + 24.5 = `floor(74.5) = 74`.
- **Veto-capped** — if TALE T1 (differentiation truth) fails on the B2B example, the weighted overall is capped: `min(75, 60) = 60`, `cap_applied: true`.

## Veto items (red lines — stable IDs, distributed T:1 / A:1 / L:1 / E:1)

| ID | Dimension | Trigger |
|----|-----------|---------|
| **T1** | Truth | **Differentiation integrity** — the onlyness/difference claim does not hold against the named alternatives (an alternative can honestly claim the same sentence), or it rests on a product/comparative claim absent from or contradicting `memory/claims/claims-ledger.md`. *Carve-out:* framing explicitly labeled as aspirational vision, not present-tense fact. |
| **A1** | Architecture | **Canon integrity** — no narrative canon on file in the [narrative-registry](../protocol/narrative-registry/SKILL.md) (`memory/narrative-registry/`), or a hierarchy that contradicts itself (a pillar, tagline, or boilerplate asserting something another part of the canon denies). *No canon on file* = **NEEDS_INPUT**, not pass-by-default. *Carve-out:* a draft canon explicitly marked WIP for a pre-messaging product. |
| **L1** | Landing | **Message-match failure** — a flagship surface (homepage, pricing, store listing, sales deck) contradicts the canon's tagline, pillars, or approved claim wording. *Carve-out:* a per-market localization recorded in the registry as an intentional adaptation, not a drift. |
| **E1** | Evidence | **Evidence integrity** — a resonance/effectiveness claim asserted with zero Measured/User-provided evidence, a proxy-sourced number (GDELT/Tavily/Bluesky-as-adjacent) presented as Measured, or doubling down on a message after it failed its test. *Carve-out:* proxies pass when labeled proxy; internal scratch analyses not reported outward are not gated. |

**Narrative whiplash** (re-cutting the core narrative or repositioning faster than the market can absorb it, with no triggering evidence — a drift signal or a failed message test) is a high-severity **guardrail/flag under A**, *not* a veto — it erodes recognition and compounding, but it does not by itself make the NQS untrustworthy (mirrors ROAS's premature-scaling, SEND's over-frequency, RAMP's launch-stacking, and ECHO's over-posting guardrails). Its fact base is the registry's `versions.md` cadence.

## Data contract (keyless inputs)

| Need | Source (own data / keyless public) |
|------|-------------------------------------|
| T / positioning truth, named alternatives | [positioning-mapper](../launch/research/positioning-mapper/SKILL.md) output in `memory/launch/positioning-mapper/`, win-loss + interviews (User-provided) |
| T / competitor messaging | `firecrawl.py` / `tavily.py` (keyless, robots pre-flight, proxy-labeled), `wayback.py` (competitor copy over time) |
| T / E / claims | approved wording in `memory/claims/claims-ledger.md` (**[offer-claims-registry](../protocol/offer-claims-registry/SKILL.md)** is the sole adjudicator) |
| A / canon, voice, naming, boilerplate | the [narrative-registry](../protocol/narrative-registry/SKILL.md) `canon.md` + `versions.md` (**no canon = NEEDS_INPUT**) |
| L / surface truth | the live brand surfaces (own pages/decks/listings, User-provided or scraped), `wayback.py` for change history |
| E / resonance + SOV telemetry | `bluesky.py`, `gdelt.py` (news echo, proxy-labeled), `tavily.py --answer` (AI-answer perception, proxy-labeled), `pageviews.py` (attention denominator), reused [share-of-voice-tracker](../social/observe/share-of-voice-tracker/SKILL.md) — see [CONNECTORS.md](../CONNECTORS.md) |
| E / closed-platform / review-site voice | user-exported native analytics (Measured, as-of date) or proxy reads **labeled proxy**; G2/Capterra/Trustpilot excerpts only as User-provided |

## Naming disambiguation

TALE's veto IDs collide *textually* with other frameworks' IDs — the letters and numbers match but the meanings are unrelated, and each framework's letters are independent. In any shared document (e.g. [auditor-runbook.md](auditor-runbook.md) §2/§5) always qualify the ID with the framework name. The dangerous rows:

- **TALE E1** (evidence integrity, veto) vs **ECHO E1** (embeddedness / channel-truth, veto) — the highest-risk pair in the library: both are vetoes, both in adjacent disciplines (narrative + social), a mixed session must always write `TALE-E1` / `ECHO-E1`.
- **TALE A1** (canon integrity, veto) vs **ROAS A1** (audience, veto) and **RAMP A1** (asset/claim integrity, veto) — a mixed launch+narrative session must always qualify: `TALE-A1` / `RAMP-A1`.
- **TALE T1** (differentiation integrity, veto) vs **C³ ART T1 / T2** (Trust items) — unrelated meanings.
- **TALE L1** (message-match failure, veto) is collision-free — L is a fresh dimension letter in this library.

The NQS is likewise distinct from RQS (ROAS), EQS (SEND), LQS (RAMP), and SQS (ECHO). The runbook lists TALE vetoes under a Narrative sub-heading.

## Where it is used

The narrative skills apply TALE across the **TALE loop** — Trace → Architect → Land → Evaluate (directories under `narrative/<phase>/`). Only [narrative-quality-auditor](../narrative/evaluate/narrative-quality-auditor/SKILL.md) computes the goal-weighted NQS and runs the four vetoes; every other skill operates on a single lever and hands off.

- **Trace (T)** — [narrative-baseline-mapper](../narrative/trace/narrative-baseline-mapper/SKILL.md) inventories what every surface says today and the gap vs intent; [category-narrative-mapper](../narrative/trace/category-narrative-mapper/SKILL.md) maps the category's stories and competitive narratives; [audience-belief-mapper](../narrative/trace/audience-belief-mapper/SKILL.md) captures beliefs, objections, and switching forces; [positioning-truth-tracer](../narrative/trace/positioning-truth-tracer/SKILL.md) reconciles the positioning canvas against shippable reality and the claims ledger (the upstream of `T1`). Positioning input is reused from [positioning-mapper](../launch/research/positioning-mapper/SKILL.md).
- **Architect (A)** — [strategic-narrative-designer](../narrative/architect/strategic-narrative-designer/SKILL.md) builds the old-world→new-game→promised-land arc; [message-system-architect](../narrative/architect/message-system-architect/SKILL.md) authors the durable brand message hierarchy that seeds the canon (the per-launch [message-house-builder](../launch/assemble/message-house-builder/SKILL.md) is reused, deriving from it — the upstream of `A1`); [brand-language-codifier](../narrative/architect/brand-language-codifier/SKILL.md) codifies voice, tone, lexicon, and the naming tax; [story-bank-builder](../narrative/architect/story-bank-builder/SKILL.md) assembles reusable story units tagged to claim IDs.
- **Land (L)** — [narrative-cascade-planner](../narrative/land/narrative-cascade-planner/SKILL.md) maps per-surface message-match and hands off to each discipline's creative builder (the upstream of `L1`); [pitch-narrative-builder](../narrative/land/pitch-narrative-builder/SKILL.md) builds the sales/fundraising pitch narrative; [narrative-enablement-kit](../narrative/land/narrative-enablement-kit/SKILL.md) makes everyone tell the same story; [proof-point-packager](../narrative/land/proof-point-packager/SKILL.md) turns ledger-approved proofs into reusable proof modules.
- **Evaluate (E)** — [narrative-quality-auditor](../narrative/evaluate/narrative-quality-auditor/SKILL.md) is the auditor-class gate (NQS + T1/A1/L1/E1 + pre-publish consistency mode, artifacts at `memory/audits/narrative/`); [message-test-designer](../narrative/evaluate/message-test-designer/SKILL.md) designs the comprehension/panel tests (execution handed to the experiment builders); [narrative-resonance-monitor](../narrative/evaluate/narrative-resonance-monitor/SKILL.md) measures echo rate and AI-answer perception (reusing `bluesky.py` and [share-of-voice-tracker](../social/observe/share-of-voice-tracker/SKILL.md)); [narrative-drift-monitor](../narrative/evaluate/narrative-drift-monitor/SKILL.md) watches self-drift, competitor repositioning, and the repositioning triggers.

Reused cross-discipline (counted in their home phases): `positioning-mapper`, `message-house-builder`, `audience-mapper`, `competitor-analysis`, `share-of-voice-tracker`, `trend-spotter`, `content-writer`, `sales-enablement-kit`, `landing-optimizer`, `send-experiment-designer`, `ad-test-designer`, `offer-claims-registry`, `entity-optimizer`, `performance-analyzer` / `report-generator`, `memory-management`. The narrative truth registry [narrative-registry](../protocol/narrative-registry/SKILL.md) lives in the protocol layer.

> **Provisional**: TALE is a new framework. Treat its bands as provisional until calibrated against ~30 real narrative audits in `memory/audits/narrative/`, per the runbook's calibration discipline.
