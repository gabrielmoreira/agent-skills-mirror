# AGENTS.md

Guidelines for AI agents working in this repository. For full runtime context, see [CLAUDE.md](CLAUDE.md).

## Repository Overview

- **Name**: aaron-marketing-skills — 120 skills (16 × 7 disciplines + 8 protocol), 7 disciplines + a protocol layer, 8 commands, shared references
- **Repository**: https://github.com/aaron-he-zhu/aaron-marketing-skills
- **Author**: Aaron He Zhu | **License**: Apache 2.0
- **Specs**: [Agent Skills](https://agentskills.io/specification.md)
- **Cross-agent compatibility**: all 120 skills install on the 70+ SKILL.md hosts served by `npx skills` (which reads the skill declarations from `.claude-plugin/plugin.json` — no mirror directory needed, never add one). Per-agent matrix + degradation rules: [docs/agent-compatibility.md](docs/agent-compatibility.md); CI enforces the discovery count. New/renamed skills must also be added to a grouping in the repo-root `skills.sh.json` (lays out the [skills.sh page](https://skills.sh/aaron-he-zhu/aaron-marketing-skills); CI-enforced coverage).
Content-first repository: skills and commands are Markdown; Claude Code hooks use a small Bash runner; `scripts/connectors/` holds zero-dependency Python-stdlib helpers (no pip deps) — data pullers (including the keyless hosted fetchers `firecrawl.py` and `tavily.py`, which robots-pre-flight every delegated site fetch) plus one ESP-automation helper (`resend.py`, whose mutating subcommands dry-run by default and require `--live`). Primary directories: SEO/GEO `seo-geo/research/`, `seo-geo/build/`, `seo-geo/optimize/`, `seo-geo/monitor/`; protocol layer `protocol/`; influencer `influencer/discover/`, `influencer/plan/`, `influencer/activate/`, `influencer/measure/`; paid ads `ad/research`, `ad/orchestrate`, `ad/activate`, `ad/scale`; email `email/setup`, `email/engage`, `email/nurture`, `email/deliver`; launch `launch/research`, `launch/assemble`, `launch/mobilize`, `launch/prove`; social `social/explore`, `social/craft`, `social/host`, `social/observe`; narrative `narrative/trace`, `narrative/architect`, `narrative/land`, `narrative/evaluate`; plus `commands/`, `references/`, `scripts/connectors/`.

Install instructions live in [README.md](README.md). Keep this file focused on authoring and maintenance rules.

### The system — a four-layer marketing operating system

The bundle is told as a **four-layer marketing operating system**, not a chronological list of peer disciplines. Seven disciplines, four altitudes — a system, not a pile. Canonical logical ordering: **Narrative → SEO/GEO · Social · Email · Paid · Influencer → Launch → Protocol**.

| Layer | Adopt | Disciplines | Cadence |
|-------|-------|-------------|---------|
| **L1 · Strategy** — what we say / who we are | crawl | **Narrative** · TALE | always-on |
| **L2 · Channels** — always-on engines that express the strategy (owned → bought) | walk | **SEO/GEO** · CORE-EEAT + CITE · **Organic Social** · ECHO · **Email** · SEND · **Paid Ads** · ROAS · **Influencer** · C³ | always-on (influencer episodic-leaning) |
| **L3 · Orchestration** — the time-boxed moment across channels | run | **Product Launch** · RAMP | episodic |
| **L4 · Protocol** — the shared system of record | — | 8 truth registries + memory · 8 auditor gates · one skill contract | — |

Narrative is the message; the channels are the mediums that express it — remove any one channel and the record is intact; remove Narrative and every channel speaks an unsourced, ungoverned message. Each discipline's 4-phase loop lives inside its layer (Narrative = Trace → Architect → Land → Evaluate).

The strata are the system; the 4×4 shape is how each workflow is drawn. Each discipline is exactly **4 phases × 4 skills = 16** (112 discipline + 8 protocol = **120**); no capability was deleted — reductions are mode-preserving merges. Full per-phase listings are in [CLAUDE.md § Skills by Phase](CLAUDE.md).

**Narrative/TALE (16)** — L1 strategy layer, phases Trace → Architect → Land → Evaluate. Trace: `narrative-baseline-mapper`, `category-narrative-mapper`, `audience-belief-mapper`, `positioning-truth-tracer` · Architect: `strategic-narrative-designer`, `message-system-architect`, `brand-language-codifier`, `story-bank-builder` · Land: `narrative-cascade-planner`, `pitch-narrative-builder`, `narrative-enablement-kit`, `proof-point-packager` · Evaluate: `narrative-quality-auditor` (TALE NQS gate), `message-test-designer`, `narrative-resonance-monitor`, `narrative-drift-monitor`. Reuses `positioning-mapper`, `message-house-builder`, `audience-mapper`, `share-of-voice-tracker` cross-discipline; no new connector (resonance reuses `bluesky.py`/`gdelt.py`/`tavily.py`/`wayback.py`).

**SEO/GEO (16)** — merges: `content-writer` (seo-content-writer + content-refresher) · `serp-markup-builder` (meta-tags-optimizer + schema-markup-generator) · `page-play-builder` (programmatic + parasite + comparison + local SEO, 4 modes) · `site-structure-optimizer` (internal-linking-optimizer + site-architecture) · `performance-monitor` (performance-reporter + alert-manager) · `offsite-signal-analyzer` (backlink-analyzer + ai-traffic).

**Influencer (16)** — 6 phases → 4 (insight + map → **discover**, activate + convert → **activate**, track → **measure**). Merges: `audience-mapper` (audience-analyzer + niche-researcher) · `content-amplifier` (content-amplifier + ugc-repurposer). Moves: `competitor-tracker` (map → plan) · `landing-optimizer` (convert → measure).

**Paid/ROAS (16)** — new: `search-term-miner`, `product-feed-optimizer` (research) · `bid-strategy-planner`, `landing-experience-checker` (orchestrate) · `placement-exclusion-manager`, `conversion-value-mapper` (activate) · `budget-pacing-monitor`, `fatigue-frequency-manager` (scale).

**Email/SEND (16)** — new: `list-hygiene-monitor` (setup) · `subject-line-lab`, `email-render-builder`, `dynamic-content-personalizer` (engage) · `preference-frequency-manager`, `reactivation-specialist` (nurture) · `inbox-placement-monitor`, `cold-outbound-sequencer` (deliver). Renamed: `send-experiment-designer` (was send-test-designer).

### New skills (v11.0.0)

Sixteen skills added across the 38 → 54 expansion (six SEO/GEO + four paid in v11, then four more paid in the Balanced paid-ads expansion, plus the two protocol truth registries). Full per-phase listings are in [CLAUDE.md § Skills by Phase](CLAUDE.md). Paid phases are directories under `ad/` following the ROAS loop (ad/research, ad/orchestrate, ad/activate, ad/scale).

| Discipline | Phase | Skill |
|------------|-------|-------|
| SEO/GEO | Build | `programmatic-seo` |
| SEO/GEO | Build | `parasite-seo` |
| SEO/GEO | Build | `comparison-page-builder` |
| SEO/GEO | Build | `local-seo` |
| SEO/GEO | Optimize | `site-architecture` |
| SEO/GEO | Monitor | `ai-traffic` |
| Paid Ads | Research (structure + search-term mining) | `campaign-architect` |
| Paid Ads | Research (audiences) | `audience-segment-builder` |
| Paid Ads | Orchestrate (creative) | `ad-creative-builder` |
| Paid Ads | Orchestrate (experiment design) | `ad-test-designer` |
| Paid Ads | Activate (auditor-class gate; ROAS RQS + launch go/no-go) | `ad-account-auditor` |
| Paid Ads | Activate (conversion-signal QA) | `conversion-signal-qa` |
| Paid Ads | Scale (readback) | `paid-measurement-loop` |
| Paid Ads | Scale (attribution de-dup / incrementality) | `attribution-reconciler` |
| Protocol | Truth registry (canonical creator roster/dossier — influencer SSOT) | `creator-registry` |
| Protocol | Truth registry (offer & claim-substantiation record — paid SSOT) | `offer-claims-registry` |

## Skill Format Specifications

### Required Frontmatter

| Field | Required | Rules |
|-------|----------|-------|
| `name` | Yes | 1-64 chars, lowercase a-z, numbers, hyphens. Must match directory name. Lowercase slug `^[a-z0-9][a-z0-9-]*$`. |
| `version` | Yes | Semver string. Must match `metadata.version` and the row in `VERSIONS.md`. |
| `description` | Yes | 1-1024 chars. Include: what it does, trigger phrases, scope boundaries. Optimized for `npx skills find`. |

### Repo-Required / Spec-Optional Frontmatter

| Field | Purpose |
|-------|---------|
| `license` | License name (default: Apache-2.0) |
| `compatibility` | Platform list |
| `allowed-tools` | Pre-approved tools (e.g., `WebFetch`) |
| `metadata` | **Single-line strict-JSON object** — OpenClaw's parser reads single-line keys only; the validator fails a YAML block map. `metadata.version` must match top-level `version`. |
| `metadata.author/geo-relevance` | Discovery and categorization. |
| `metadata.discipline` + `metadata.phase` | On every skill (120/120): `discipline` = seo-geo/influencer/paid/email/launch/social/narrative/protocol; `phase` = lifecycle phase. Uniform routing/clustering tags. |
| `metadata.hermes` | Hermes Agent extension: `{"tags": ["marketing", <discipline>, <phase>], "category": <discipline>}` for `hermes skills browse` filtering. |
| `metadata.openclaw` | OpenClaw extension: `{"emoji": <discipline emoji>, "homepage": <repo URL>}` for the macOS UI. |
| `slug` | SkillHub.cn publishing identity — must be `aaron-<skill-name>` (validator-enforced). |
| `displayName` + `summary` | SkillHub.cn listing card: bilingual display name + Chinese one-liner. |
| `when_to_use` | Trigger scenarios for auto-invocation (underscores, not hyphens) |
| `argument-hint` | Argument format hint in command picker |

### Description Best Practices

Start with `Use when the user asks to "..."`, then one sentence on function, then scope boundaries linking related skills.

## Quality Frameworks

See [CLAUDE.md § Quality Frameworks](CLAUDE.md) for details. Summary:
- **CORE-EEAT** (80 items, 8 dimensions): content quality. [Full reference](references/core-eeat-benchmark.md)
- **CITE** (40 items, 4 dimensions): domain authority. [Full reference](references/cite-domain-rating.md)
- **C³** (9 dimensions, Creator/Content/Campaign on ACE/ART/ROI, CVI geometric rollup): influencer marketing. [Full reference](references/c3-benchmark.md)
- **ROAS** (R Return / O Offer / A Audience / S Spend-efficiency, RQS arithmetic weighted-mean rollup like CITE): paid ads. [Full reference](references/roas-benchmark.md)
- **SEND** (S Sender-integrity/deliverability / E Engagement / N Nurture-lifecycle / D Direct-response, EQS arithmetic goal-weighted-mean rollup like ROAS): email marketing. [Full reference](references/send-benchmark.md)
- **RAMP** (40 items, 4 dimensions × 10: R Readiness / A Assets / M Momentum / P Proof, LQS arithmetic goal-weighted floor-mean rollup like ROAS/SEND): product launch. [Full reference](references/ramp-benchmark.md)
- **ECHO** (40 items, 4 dimensions × 10: E Embeddedness / C Craft / H Hosting / O Observability, SQS arithmetic goal-weighted floor-mean rollup like RAMP): organic social. [Full reference](references/echo-benchmark.md)
- **TALE** (4 dimensions: T Truth / A Architecture / L Landing / E Evidence, NQS rollup): brand narrative & messaging. [Full reference](references/tale-benchmark.md)
- Veto items: CORE-EEAT (T04, C01, R10) · CITE (T03, T05, T09) · C³ (ACE A2/C1/E2, ART T1/T2) · ROAS (R1/R2/O1/O2/A1) · SEND (S1/S2/N1/D1) · RAMP (R1/A1/M1/P1 — IDs collide with ROAS, always qualify with the framework name) · ECHO (E1/C1/C2/H1/H2/O1 — always qualify with the framework name; ECHO O1 vs ROAS O1, ECHO C1 vs C³ C1/CORE C01) · TALE (T1/A1/L1/E1 — always qualify with the framework name)

## Tool Connector Pattern

Skills use `~~category` placeholders. See [CONNECTORS.md](CONNECTORS.md). Every skill works at Tier 1 (no tools). MCP adds Tier 2/3.

## Inter-Skill Handoff

See [CLAUDE.md § Inter-Skill Handoff](CLAUDE.md). Key fields (per skill-contract §Handoff Summary Format): status, objective, key findings, evidence, assumptions, open loops, recommended next skill — plus `cap_applied` / `raw_overall_score` / `final_overall_score` for the 8 auditor-class gates.

Auditor-class gates: `content-quality-auditor` (CORE-EEAT publish gate), `domain-authority-auditor` (CITE citation-trust gate), `content-reviewer` (C³ ART gate → `memory/audits/influencer/`), `ad-account-auditor` (ROAS gate → `memory/audits/ad/`), `email-quality-auditor` (SEND gate → `memory/audits/email/`), `launch-readiness-auditor` (RAMP LQS gate → `memory/audits/launch/`), `social-quality-auditor` (ECHO SQS gate → `memory/audits/social/`), and `narrative-quality-auditor` (TALE NQS gate → `memory/audits/narrative/`). New cross-cutting reference protocols: `humanizer-slop`, the `measurement-protocol` decision protocol, and `platforms/`.

## Git Workflow

- **Branch naming**: `feature/skill-name`, `fix/skill-name`, `docs/description`
- **Conventional Commits**: `feat:`, `fix:`, `docs:`
- **After skill changes**: update the tracking files — the authoritative 8-file list is in [CONTRIBUTING.md §6](CONTRIBUTING.md) (VERSIONS.md, `.claude-plugin/plugin.json`, root `marketplace.json` + its `.claude-plugin/marketplace.json` mirror, README.md, CLAUDE.md, AGENTS.md, docs/README.zh.md). For release bumps, also sync localized README badges. `scripts/check-versions.sh` (CI) fails on any drift — run it locally after syncing.
- **Adding a connector**: follow [docs/connector-playbook.md](docs/connector-playbook.md) end to end — qualify (category / connector-vs-recipe / safety class), verify against primary docs + a live call, implement to house style, offline-test the pure builders, wire skills by the differentiation rule, hit the six doc touchpoints, track, regress, record.
- **Use `references/` for detail** — keep `SKILL.md` focused. Auditor-class skills `Read references/auditor-runbook.md` at activation (the framework-agnostic SSOT) and keep only their framework-specific §2 worked examples, §3 guardrails, and §5 veto-ID rows inline.
- **Validate**: `./scripts/validate-skill.sh <category>/<skill-name>` before release PRs. CI guards: `golden-math` (8 frameworks), `check-evals`, `check-pii`, `check-stdlib-only` (incl. the Paid-Ads keyed-API red line).

## Writing Style

- Direct, instructional, second person
- Bold key terms on first use
- Code blocks for commands/templates; tables for structured data
- One skill per file; put extras in `references/`
