# State Model

Plan C standardizes where reusable project state belongs. All state follows a three-tier temperature model with automatic lifecycle management.

## Temperature Tiers

### HOT — `memory/hot-cache.md`

- Capacity: 80 lines max
- Loaded automatically by SessionStart hook every session
- Content: project goals, hero keywords (max 10), primary competitors (max 5), active veto items, unresolved open loops from `memory/open-loops.md`
- Promotion: **explicit** — the user or a skill pins a finding to HOT ("promote X" / auto-promote of veto items and blockers). No hook counts references, so promotion is never frequency-based.
- Demotion: when the HOT entry's `last_updated` date is older than 30 days — move it out of hot-cache.md; the content remains in its WARM file

### WARM — `memory/<category>/<skill>/`

- Capacity: 200 lines per file
- Loaded on demand when a skill matches the topic
- Paths follow the Durable State definitions below
- Promotion: when the user/skill decides a conclusion is durable, extract it (max 3 lines) to HOT — an explicit action, not a reference counter
- Demotion: when the file's `last_updated` date is older than 90 days — move it to `memory/archive/` with date prefix `YYYY-MM-DD-`

### COLD — `memory/archive/`

- No capacity limit
- Queried only when `memory-management` is explicitly invoked
- Never auto-deleted, only archived
- Filename format: `YYYY-MM-DD-original-filename.md`

### Lifecycle Rules (observable only)

Nothing in the hooks records read/reference counts, so the lifecycle uses only what an agent can
check on disk: an **explicit pin** or a **`last_updated` date**.

```
explicit "promote X" / pin           → WARM promotes to HOT (extract ≤3 lines)
HOT entry last_updated > 30 days      → HOT demotes to WARM
WARM file last_updated > 90 days      → WARM demotes to COLD (archive with YYYY-MM-DD- prefix)
```

### Dual Truncation Rule

HOT tier is limited to 80 lines AND 25KB (whichever triggers first). A cache within both limits is injected in full; the SessionStart hook applies the 80-line cap at a newline boundary and the 25KB cap at the byte limit, so an over-limit cache may be cut mid-line. If exceeded after Claude Write/Edit, the PostToolUse hook warns the user.

### Staleness Protocol

| Age | Treatment |
|-----|-----------|
| ≤7 days | Current — use without caveat |
| 8–30 days | Point-in-time — verify against current state before asserting as fact |
| 31–90 days | Stale — surfaced for review when `memory-management` runs its staleness scan (by `last_updated` date) |
| >90 days | Archive candidate — recommend archival via memory-management |

## Memory File Frontmatter

Every file in `memory/` SHOULD include YAML frontmatter. Two shapes are valid:

**WARM files** — subject matter state (audits, research, decisions, entities, etc.):

```yaml
---
name: campaign-q2-seo
description: Q2 SEO campaign targeting 50 keywords across 3 verticals
type: project
last_updated: 2026-06-10
---
```

Valid `type` values: `project`, `reference`, `decision`, `entity`, `glossary`, `open-loops`, `entity-candidates`

The `description` field enables future semantic search across memory files. **`last_updated`** (a date) is what the demotion/archival rules and `memory-management`'s staleness scan read — write it whenever you create or modify a WARM file. Absent it, fall back to the file's mtime.

**HOT file** (`memory/hot-cache.md`) — session scope declaration:

```yaml
---
tier: hot
project: acme-q2     # null for global scope; set to a project slug to scope memory reads
---
```

When `project` is non-null, the SessionStart hook and `memory-management` preferentially load memory scoped to that project. Switching projects between sessions = swap this field.

## Durable State

### `memory/decisions.md`

Store:

- major strategic choices
- accepted tradeoffs
- abandoned directions worth remembering

### `memory/open-loops.md`

Store:

- unresolved blockers
- missing evidence
- follow-up tasks
- risks that should not be forgotten

### `memory/glossary.md`

Store:

- project terminology
- internal acronyms
- shorthand labels
- segment definitions
- historical naming context

### `memory/entities/`

Store:

- canonical names
- sameAs and profile links
- entity type
- topic associations
- disambiguation notes
- knowledge-base status

Only `entity-optimizer` should write canonical records here. Other skills should keep raw entity leads in their own category notes until canonicalization is needed.

### `memory/creators/`

Store (one file per creator, `<handle-slug>.md`, slug = canonical primary-platform handle):

- verified cross-platform handles with confirmed/unconfirmed status
- audience stats with as-of dates and Measured/User-provided/Estimated provenance
- rate card and negotiation history
- past-campaign performance baselines
- dated disclosure/FTC compliance events citing content-reviewer verdict IDs
- exclusivity windows, contract status, and the confirmed contact path

Only `creator-registry` writes canonical records here. Other skills submit updates to `memory/creators/candidates.md` only.

**Lifecycle exemption**: canonical creator records are roster state, not dated run artifacts — no `YYYY-MM-DD` filename, and they are exempt from the 90-day WARM demotion (like `memory/entities/`). Demotion happens only when the user drops a creator from the roster, and `memory-management` remains the sole executor of that archival.

### `memory/claims/`

Store (standing ledger files, not per-run artifacts):

- `claims-ledger.md` — one row per marketing claim: claim text → substantiation evidence (source, date, provenance label) → approved wording + required disclosures → where used (ads / landing pages / briefs) → review/expiry date
- `offers.md` — live offers: terms, promo codes, dates, landing URLs
- `candidates.md` — intake from other skills (mirror of the entity/creator pattern)

Only `offer-claims-registry` writes canonical records here. Other skills submit updates to `memory/claims/candidates.md` only.

**Lifecycle exemption**: ledger files are standing state, not dated run artifacts — exempt from the 90-day WARM demotion (like `memory/entities/` and `memory/creators/`); rows retire via their review/expiry date, and `memory-management` remains the sole executor of archival.

### `memory/consent/`

Store (one record per subscriber/prospect subject — the email consent & suppression SSOT):

- subscription status and source
- opt-in timestamp + **lawful basis** (consent / legitimate-interest / contract) and double-opt-in proof
- append-only unsubscribe / bounce / spam-complaint history with dates
- suppression flags the S2 veto and N1 unsubscribe-honoring are judged against

Only `consent-registry` writes canonical records here. Other skills submit updates to `memory/consent/candidates.md` only.

**GDPR posture**: subscribers are natural persons — inherit `creator-registry`'s lawful-basis gate and data-minimization posture; store the minimum needed to prove consent and honor suppression, never raw personal data beyond that.

**Lifecycle exemption**: consent/suppression records are standing state, not dated run artifacts — exempt from the 90-day WARM demotion (like `memory/creators/` and `memory/claims/`); records retire on consent withdrawal / suppression, and `memory-management` remains the sole executor of archival.

### `memory/launch-registry/`

Store (the launch truth SSOT — one dossier per launch moment, `<product-or-moment-slug>.md`, plus two standing files):

- per-launch dossier: tier (T1/T2/T3), launch type (new-product / feature / relaunch / partnership), lifecycle stage on the one-way machine `draft → concept → alpha → beta → general-availability` (+ `archived`) with dated evidence per transition, authoritative launch date/window, embargo/partner commitments, the channel submission ledger, asset-manifest version pointers, the declared RAMP goal column, and the post-launch outcome snapshot
- `calendar.md` — every past and planned launch moment (the launch-stacking spacing fact base)
- `candidates.md` — intake from other skills (mirror of the entity/creator/claims/consent pattern)

Only `launch-registry` writes canonical records here. Other skills submit updates to `memory/launch-registry/candidates.md` only.

**T-0 batch-promote clause**: during the launch window, mobilize-phase skills (`community-launch-runner`, `press-media-relations`, `launch-day-conductor`) append dated submission/status lines to `candidates.md` instead of blocking on the sole writer; `launch-registry` promotes the batch into the dossier's submission ledger at day close (or when explicitly invoked), preserving each row's original timestamp and source. This is an intake-cadence provision, not a second writer — canonical files are still written only by `launch-registry`.

**Lifecycle exemption**: dossiers and `calendar.md` are standing state, not dated run artifacts — exempt from the 90-day WARM demotion (like `memory/entities/`, `memory/creators/`, `memory/claims/`, and `memory/consent/`); a dossier retires after its outcome snapshot lands, and `memory-management` remains the sole executor of archival.

### `memory/channels/`

Store (the social channel truth SSOT — **channel-first, never person-shaped**; one dossier per brand-owned handle, `<platform>-<handle-slug>.md`, plus four standing files):

- per-channel dossier: platform + handle URL, ownership/access governance (credential holder, 2FA, agency access, approval ladder), declared objective + ECHO goal column, versioned bio/link-in-bio inventory, voice-card pointer + per-platform register, dated platform-rule snapshot pointer (`references/platforms/*` with last-verified date), cadence commitment with counterparty + source, lifecycle state on the one-way machine `proposed → warming → active → paused → retired` (dated, evidenced transitions; `warming → active` requires participation-warmup graduation evidence; reactivation is a new dated transition, never a rewrite), an append-only activity ledger, and outcome snapshots
- `voice-dossier.md` — the brand/founder voice record every Craft-phase skill reads first
- `ugc-permissions.md` — one row per UGC permission: creator, content ID, scope (organic vs paid), channels, duration, compensation, expiry, evidence link (the ECHO H2 fact base)
- `advocate-roster.md` — handle + disclosure line + opt-in date + voluntary-basis evidence (the ECHO H1/C2 fact base); **minimal, non-authoritative person rows only** — canonical creator records stay in `memory/creators/`, email subjects in `memory/consent/`
- `calendar-commitments.md` — committed cadence per channel (the ECHO over-posting guardrail fact base)
- `candidates.md` — intake from other skills (mirror of the entity/creator/claims/consent/launch pattern)

Only `channel-registry` writes canonical records here. Other skills submit updates to `memory/channels/candidates.md` only.

**Batch-promote clause**: `engagement-inbox-manager` and `social-pulse-monitor` append dated activity/mention lines to `candidates.md` intra-day and the registry promotes them at day close; during an incident, `crisis-response-planner` appends queue-pause/state markers the same way, reconciled post-incident (the launch-registry T-0 precedent). An intake-cadence provision, not a second writer.

**Lifecycle exemption**: dossiers and the four standing files are standing state, not dated run artifacts — exempt from the 90-day WARM demotion (like the other registries); a channel retires on a dated `retired` transition, and `memory-management` remains the sole executor of archival.

### `memory/narrative-registry/`

Store (the brand canon truth SSOT — the versioned narrative of record every discipline reads voice and message from, three standing files):

- `canon.md` — the current brand canon: strategic narrative, tagline, message pillars, brand-language register, and the approved proof points, each judged against **TALE A1**
- `versions.md` — the append-only version log of canon revisions with dated evidence per transition (the narrative-drift fact base)
- `candidates.md` — intake from other skills (mirror of the entity/creator/claims/consent/launch/channel pattern)

Only `narrative-registry` writes canonical records here. Other skills submit updates to `memory/narrative-registry/candidates.md` only. The discipline's WARM working files (drafts, tests, monitoring readouts) live separately under `memory/narrative/<skill>/`.

**Versioned-canon atomic-promotion clause**: a canon revision lands as one atomic promotion — `narrative-registry` rewrites `canon.md` and appends the matching dated row to `versions.md` in the same operation, so the current canon and its version log never disagree. A partial promotion is never a valid state.

**Lifecycle exemption**: `canon.md` and `versions.md` are standing state, not dated run artifacts — exempt from the 90-day WARM demotion (like the other registries); superseded canon is retained in `versions.md` rather than archived, and `memory-management` remains the sole executor of any archival.

### `memory/research/`

Common subfolders:

- `keywords/`
- `competitors/`
- `serp/`
- `content-gaps/`

Store:

- keyword opportunities
- competitor findings
- SERP notes
- content gap summaries

### `memory/content/`

Common subfolders:

- `briefs/`
- `calendar/`
- `published/`

Store:

- content briefs
- approved angles
- meta tag decisions
- schema notes
- refresh plans

### `memory/audits/`

Common subfolders:

- `content/` (content-quality-auditor — CORE-EEAT)
- `domain/` (domain-authority-auditor — CITE)
- `<skill>/` (other Optimize skills, per-skill — e.g. `technical-seo-checker/`, `site-structure-optimizer/`)
- `influencer/` (content-reviewer — C³ ART gate artifacts)
- `ad/` (ad-account-auditor — ROAS gate artifacts)
- `email/` (email-quality-auditor — SEND gate artifacts)
- `launch/` (launch-readiness-auditor — RAMP gate artifacts)
- `social/` (social-quality-auditor — ECHO gate artifacts)

Store:

- audit summaries
- veto items
- prioritized fixes
- pass/fail gate decisions (all gated artifacts carry `class: auditor-output` + the cap schema per [auditor-runbook.md](auditor-runbook.md))

### `memory/monitoring/`

Common subfolders:

- `rank-history/`
- `reports/`
- `alerts/`
- `snapshots/`

Store:

- ranking deltas
- alert history
- backlink changes
- stakeholder reporting summaries
- dated supporting CSV or export files when helpful

### `memory/influencer/`

Per-skill subfolders, one per influencer-marketing skill: `memory/influencer/<skill>/` (e.g. `audience-mapper/`, `fit-scorer/`, `roi-calculator/`). Scored on the [C³ framework](c3-benchmark.md).

Store:

- audience profiles, niche dossiers, trend reports (discover)
- creator shortlists, fit scores (ACE), competitor partner maps (discover)
- campaign plans, briefs, budget allocations (plan)
- outreach threads, content reviews (ART), contract drafts (activate)
- amplification plans, repurposed UGC, landing-page optimizations (activate)
- performance analyses, ROI/CVI calculations, reports (measure)

Same WARM lifecycle as the other categories: dated files `YYYY-MM-DD-<topic>.md`, demoted to `memory/archive/` after 90 days by `last_updated`. (content-reviewer's **gated** ART verdict is an auditor artifact and lives in `memory/audits/influencer/`, not here.)

### `memory/ad/`

Per-skill subfolders, one per Paid Ads skill: `memory/ad/<skill>/` (e.g. `campaign-architect/`, `ad-creative-builder/`, `paid-measurement-loop/`). Scored on the [ROAS framework](roas-benchmark.md).

Store:

- account/campaign structure plans, targeting + negative lists, cannibalization audits (research)
- ad-creative sets and angle matrices (orchestrate)
- ROAS/CPA readback snapshots vs control (scale)

Same WARM lifecycle (dated files, demoted to `memory/archive/` after 90 days). ad-account-auditor's **gated** RQS verdict is an auditor artifact and lives in `memory/audits/ad/`.

### `memory/email/`

Per-skill subfolders, one per email-marketing skill: `memory/email/<skill>/` (e.g. `deliverability-qa/`, `email-creative-builder/`, `email-sequence-designer/`). Scored on the [SEND framework](send-benchmark.md).

Store:

- deliverability pre-flight results (auth/reputation/inbox-placement), segment maps + suppression lists (setup)
- email creative sets, subject-line variants (engage)
- lifecycle-flow designs, cadence/frequency plans, newsletter monetization models (nurture)
- send-test designs and significance reads (deliver)

Same WARM lifecycle (dated files, demoted to `memory/archive/` after 90 days). email-quality-auditor's **gated** EQS verdict is an auditor artifact and lives in `memory/audits/email/`. Consent/suppression facts live in `memory/consent/` (consent-registry's SSOT), not here.

### `memory/launch/`

Per-skill subfolders, one per launch skill: `memory/launch/<skill>/` (e.g. `positioning-mapper/`, `launch-asset-packager/`, `launch-retro-analyzer/`). Scored on the [RAMP framework](ramp-benchmark.md).

Store:

- positioning canvases, tier/type decisions + risk registers, window analyses, early-access program designs (research)
- message houses / PR-FAQ spines, asset manifests + press kits, pricing/packaging plans, enablement kits (assemble)
- launch-day runbooks, channel submission kits, media lists + embargo pitch sequences (mobilize)
- launch-window telemetry snapshots, feedback theme maps, retros, momentum plans (prove)

Same WARM lifecycle (dated files, demoted to `memory/archive/` after 90 days). launch-readiness-auditor's **gated** LQS verdict is an auditor artifact and lives in `memory/audits/launch/`. The canonical launch dossier/calendar lives in `memory/launch-registry/` (launch-registry's SSOT), not here.

### `memory/social/`

Per-skill subfolders, one per social skill: `memory/social/<skill>/` (e.g. `social-calendar-builder/`, `engagement-inbox-manager/`, `social-pulse-monitor/`). Scored on the [ECHO framework](echo-benchmark.md).

Store:

- channel portfolio matrices, voice dossier drafts, norm-card research, participation-warmup plans (explore)
- posting calendars, platform-native content packages, beat sheets, advocacy program blueprints (craft)
- inbox triage logs + SLA reads, selling-block plans, crisis protocols + drill records (host)
- listening baselines + mention sweeps, SOV panels, dark-social method docs, measurement-loop readouts (observe)

Same WARM lifecycle (dated files, demoted to `memory/archive/` after 90 days). social-quality-auditor's **gated** SQS verdict is an auditor artifact and lives in `memory/audits/social/`. The canonical channel dossiers and the voice/UGC/advocate/cadence standing files live in `memory/channels/` (channel-registry's SSOT), not here.

## Writing Guidance

When a skill describes state updates, it should:

- prefer summaries over raw dumps
- distinguish facts from assumptions
- note missing data explicitly
- avoid inventing data when tools are unavailable
- keep raw exports beside the dated summary they support

## Ownership

- `memory-management` is the sole executor of WARM → COLD archival operations
- `entity-optimizer` is the sole writer of canonical records in `memory/entities/<name>.md`
- Other skills write entity candidates to `memory/entities/candidates.md` only
- `creator-registry` is the sole writer of canonical records in `memory/creators/<handle-slug>.md`; other skills write to `memory/creators/candidates.md` only
- `offer-claims-registry` is the sole writer of canonical records in `memory/claims/`; other skills write to `memory/claims/candidates.md` only
- `consent-registry` is the sole writer of canonical records in `memory/consent/`; other skills write to `memory/consent/candidates.md` only
- `launch-registry` is the sole writer of canonical records in `memory/launch-registry/`; other skills write to `memory/launch-registry/candidates.md` only (incl. the T-0 batch-promote appends)
- `channel-registry` is the sole writer of canonical records in `memory/channels/`; other skills write to `memory/channels/candidates.md` only (incl. the intra-day/incident batch-promote appends)
- `narrative-registry` is the sole writer of canonical records in `memory/narrative-registry/`; other skills write to `memory/narrative-registry/candidates.md` only
- `content-quality-auditor` owns publish-readiness state in `memory/audits/content/`
- `domain-authority-auditor` owns citation-trust state in `memory/audits/domain/`
- `content-reviewer` owns the C³ ART gate state in `memory/audits/influencer/`
- `ad-account-auditor` owns the ROAS gate state in `memory/audits/ad/`
- `email-quality-auditor` owns the SEND gate state in `memory/audits/email/`
- `launch-readiness-auditor` owns the RAMP gate state in `memory/audits/launch/`
- `social-quality-auditor` owns the ECHO gate state in `memory/audits/social/`

See [skill-contract.md](skill-contract.md) for the full protocol-layer vs execution-layer behavior matrix.
