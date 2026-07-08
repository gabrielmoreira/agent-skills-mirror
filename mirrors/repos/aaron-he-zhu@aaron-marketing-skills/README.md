<div align="center">

# Aaron Marketing Skills

**120 marketing skills — brand narrative, SEO/GEO, influencer, paid ads, email, launch, social — on one contract.**

<p align="center">
  <a href="https://github.com/aaron-he-zhu/aaron-marketing-skills"><img src="https://img.shields.io/github/stars/aaron-he-zhu/aaron-marketing-skills?style=flat" alt="GitHub Stars"></a>
  <a href="https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/VERSIONS.md"><img src="https://img.shields.io/badge/version-16.1.0-orange" alt="Version"></a>
  <a href="https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-green" alt="License"></a>
  <a href="https://github.com/aaron-he-zhu/aaron-marketing-skills/commits/main"><img src="https://img.shields.io/github/last-commit/aaron-he-zhu/aaron-marketing-skills" alt="Last Commit"></a>
</p>
<p align="center">
  <a href="https://www.skills.sh/aaron-he-zhu"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/aaron-he-zhu/aaron-marketing-skills/main/badges/skillssh.json" alt="skills.sh"></a>
  <a href="https://clawhub.ai/aaron-he-zhu"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/aaron-he-zhu/aaron-marketing-skills/main/badges/clawhub.json" alt="ClawHub"></a>
  <a href="https://skillhub.cn/user/user_2c0f1e77"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/aaron-he-zhu/aaron-marketing-skills/main/badges/skillhub.json" alt="SkillHub"></a>
</p>

**English** | [Deutsch](docs/README.de.md) | [Español](docs/README.es.md) | [Français](docs/README.fr.md) | [Italiano](docs/README.it.md) | [日本語](docs/README.ja.md) | [한국어](docs/README.ko.md) | [Português](docs/README.pt.md) | [简体中文](docs/README.zh.md) | [繁體中文](docs/README.zh-Hant.md)

</div>

A library of Claude Skills and slash commands that turns a chat agent into a marketing operator. Seven disciplines and a shared protocol layer, at a glance:

| Layer | Skills | Lifecycle (phase directories) | Framework → gate | Entrypoint |
|-------|--------|-------------------------------|------------------|------------|
| **Narrative** | 16 | trace → architect → land → evaluate | [TALE](references/tale-benchmark.md) → `narrative-quality-auditor` (NQS) | `/aaron-marketing:narrative` |
| **SEO/GEO** | 16 | research → build → optimize → monitor | [CORE-EEAT](references/core-eeat-benchmark.md) → `content-quality-auditor` · [CITE](references/cite-domain-rating.md) → `domain-authority-auditor` | `/aaron-marketing:seo-geo` |
| **Influencer** | 16 | discover → plan → activate → measure | [C³](references/c3-benchmark.md) → `content-reviewer` (ART); `fit-scorer` scores ACE | `/aaron-marketing:influencer` |
| **Paid ads** | 16 | research → orchestrate → activate → scale | [ROAS](references/roas-benchmark.md) → `ad-account-auditor` (RQS) | `/aaron-marketing:ad` |
| **Email** | 16 | setup → engage → nurture → deliver | [SEND](references/send-benchmark.md) → `email-quality-auditor` (EQS) | `/aaron-marketing:email` |
| **Launch** | 16 | research → assemble → mobilize → prove | [RAMP](references/ramp-benchmark.md) → `launch-readiness-auditor` (LQS) | `/aaron-marketing:launch` |
| **Social** | 16 | explore → craft → host → observe | [ECHO](references/echo-benchmark.md) → `social-quality-auditor` (SQS) | `/aaron-marketing:social` |
| **Protocol layer** | 8 | — (shared machinery, outside the phase flows) | 7 truth registries (entity · creator · offer/claims · consent · launch · channel · narrative) + HOT/WARM/COLD memory | — |

`/aaron-marketing:auto` routes any natural-language goal across all of it. Everything is **plain Markdown** — the only code is a Bash hook runner, a Bash validator, and zero-dependency Python-stdlib data helpers (no `pip`, no build step). **Every skill runs at Tier 1 with nothing but data you paste in**; connectors only automate retrieval.

> The pre-merge standalone repos are now **signpost repos** pointing here — [seo-geo-claude-skills](https://github.com/aaron-he-zhu/seo-geo-claude-skills) (final 20-skill line preserved at tag `v9.9.12`) and [influencer-marketing-agent-skills](https://github.com/aaron-he-zhu/influencer-marketing-agent-skills) (final IMPACT line at tag `standalone-final`). Sibling-repo policy: [docs/repo-family.md](docs/repo-family.md).

---

## Contents

- [Why this library](#why-this-library)
- [Install](#install)
- [First run](#first-run)
- [Architecture](#architecture)
  - [The shared skill contract](#the-shared-skill-contract)
  - [The system: a four-layer marketing operating system](#the-system-a-four-layer-marketing-operating-system)
  - [Quality system: eight frameworks, eight gates](#quality-system-eight-frameworks-eight-gates)
  - [The protocol layer](#the-protocol-layer)
  - [Memory & automation hooks](#memory--automation-hooks)
- [Skill catalog](#skill-catalog)
  - [Narrative — TALE (16)](#narrative--tale-16)
  - [SEO/GEO (16)](#seogeo-16)
  - [Influencer (16)](#influencer-16)
  - [Paid Ads — ROAS (16)](#paid-ads--roas-16)
  - [Email — SEND (16)](#email--send-16)
  - [Launch — RAMP (16)](#launch--ramp-16)
  - [Social — ECHO (16)](#social--echo-16)
  - [Protocol layer (8)](#protocol-layer-8)
- [Commands](#commands)
- [Connectors & enhancement tiers](#connectors--enhancement-tiers)
- [Recommended workflows](#recommended-workflows)
- [Repository layout](#repository-layout)
- [Design philosophy](#design-philosophy)
- [Quality guards (CI)](#quality-guards-ci)
- [Contributing & project docs](#contributing--project-docs)
- [Disclaimer](#disclaimer)
- [License](#license)

---

## Why this library

| Principle | What it means in practice |
|-----------|---------------------------|
| **Keyless by default** | Every skill works at **Tier 1** with data you paste or pull from free/first-party sources. Paid tools and MCP servers are an opt-in convenience, never a precondition. Paid-ads skills score from your **own-account manual export** — keyed ad APIs are never required. |
| **Markdown, not a framework** | Skills are content. The only executable code is `hooks/claude-hook.sh` (Bash), `scripts/validate-skill.sh` (Bash), and `scripts/connectors/*.py` (Python **standard library only**). Nothing to install, audit, or keep up to date. |
| **One shared contract** | All 120 skills expose the same seven sections and self-declare `discipline` + `phase` metadata, so the library behaves like one operating system: each skill knows its inputs, outputs, and the next best skill to hand off to. |
| **Gated quality** | Eight benchmarks drive eight auditor-class gates that emit structured, machine-checkable verdicts — not vibes. A PostToolUse hook validates every gated artifact before it lands. |
| **Truth lives in registries** | Canonical facts (brand entities, creator dossiers, offer/claim substantiation, per-subject consent) live in dedicated protocol-layer registries with sole-writer rules — gates judge against them instead of re-deriving them. |
| **Memory across turns** | A HOT/WARM/COLD memory model carries findings, scores, and open loops between skills and sessions, sanitized on the way in. |
| **Plain voice** | Skills ship an AI-slop detector and a banned-phrase list so output reads like a human wrote it. |

---

## Install

Use it with Claude Code, any Agent Skills-compatible host, or a plain `git clone`:

| Host | Install |
|------|---------|
| **Claude Code** | `/plugin marketplace add aaron-he-zhu/aaron-marketing-skills` then `/plugin install aaron-marketing@aaron` |
| **Codex · Cursor · OpenCode · Antigravity · Gemini CLI · Copilot CLI · OpenClaw · Hermes · [70+ hosts](https://github.com/vercel-labs/skills#supported-agents)** | `npx skills add aaron-he-zhu/aaron-marketing-skills` |
| **[SkillHub.cn](https://skillhub.cn) (中文社区)** | `skillhub install <frontmatter-slug>` (e.g. `aaron-campaign-architect` or legacy unprefixed slugs like `keyword-research`) |
| **Any host** | `git clone https://github.com/aaron-he-zhu/aaron-marketing-skills` |

In Claude Code, `marketplace add` only registers the catalog — run `/plugin install aaron-marketing@aaron` (or pick it from `/plugin`) to actually enable the skills and commands. To pull a **single** skill on a generic host: `npx skills add aaron-he-zhu/aaron-marketing-skills -s keyword-research`. Browse the bundle on the [skills.sh registry](https://skills.sh/aaron-he-zhu/aaron-marketing-skills). Per-agent directories, frontmatter quirks, and what degrades outside the plugin: [docs/agent-compatibility.md](docs/agent-compatibility.md) (verified 120/120 installable, 2026-07).

Installing the plugin adds **nothing** to your `/mcp` list — the MCP catalogue lives in [`docs/mcp-catalog.json`](docs/mcp-catalog.json), deliberately outside the plugin-root `.mcp.json` path that Claude Code auto-registers, so it is a copy-paste reference only (see [Connectors](#connectors--enhancement-tiers)).

---

## First run

If your host supports automatic skill routing, just describe the goal:

```text
Research keywords for my SaaS product targeting small teams
```
```text
Find TikTok creators for a skincare launch and score their fit
```
```text
Audit this Google Ads account before I scale — exports attached
```

Or use the slash commands — `/auto` for routing, or a discipline entrypoint:

```text
/aaron-marketing:auto turn our pricing page into an AI-citable comparison hub
```
```text
/aaron-marketing:seo-geo https://example.com/blog/my-article --mode audit
```

`/aaron-marketing:auto` infers intent and runs the smallest useful workflow, stopping only at blocking decisions. Every skill works with pasted data; optional tools are documented in [CONNECTORS.md](CONNECTORS.md).

---

## Architecture

### The shared skill contract

Every skill follows the **same activation contract** — seven sections in a fixed order:

1. **Trigger / when-to-use** — when the skill should fire.
2. **Quick Start** — copy-paste prompts.
3. **Skill Contract** — Expected output · Reads · Writes · Promotes · Done-when · Primary next skill.
4. **Handoff Summary** — the standard hand-off shape so the next skill picks up cleanly.
5. **Data Sources** — `~~category` placeholders, each with a keyless Tier-1 path.
6. **Instructions** — the numbered method (treats all exports as untrusted input).
7. **Next Best Skill** — where to go next (with visited-set + max-depth termination rules).

Every skill also self-declares `metadata.discipline` (narrative / seo-geo / influencer / ad / email / launch / social / protocol, where `ad` is Paid Ads/ROAS) and `metadata.phase`, so routing and clustering work uniformly. The contract is documented once in [skill-contract.md](references/skill-contract.md); the shared cross-skill state lives in [state-model.md](references/state-model.md).

### The system: a four-layer marketing operating system

One brand voice, expressed through five always-on channels, concentrated into launch moments, all reading and writing a shared system of record. Seven disciplines, four altitudes — a system, not a pile.

| Layer | Adopt | Disciplines | Cadence |
|-------|-------|-------------|---------|
| **L1 · Strategy** — what we say / who we are | crawl | **Narrative** · TALE | always-on |
| **L2 · Channels** — always-on engines that express the strategy (owned → bought) | walk | **SEO/GEO** · CORE-EEAT + CITE · **Organic Social** · ECHO · **Email** · SEND · **Paid Ads** · ROAS · **Influencer** · C³ | always-on (influencer episodic-leaning) |
| **L3 · Orchestration** — the time-boxed moment across channels | run | **Product Launch** · RAMP | episodic |
| **L4 · Protocol** — the shared system of record | — | 8 truth registries + memory · 8 auditor gates · one skill contract | — |

Narrative is the message; the channels are the mediums that express it — remove any one channel and the record is intact; remove Narrative and every channel speaks an unsourced, ungoverned message. Each channel inherits voice and claims from L1 the same way every creative builder already reads the claims ledger today. Each discipline's 4-phase loop lives inside its layer (Narrative = Trace → Architect → Land → Evaluate).

All seven use phase **directories** (`narrative/trace/`…, `seo-geo/research/`…, `influencer/discover/`…, `ad/research/`…, `email/setup/`…, `launch/research/`…, `social/explore/`…). Note "activate" means creator outreach for influencer but account-gating for paid ads — same word, discipline-specific scope.

### Quality system: eight frameworks, eight gates

Eight benchmarks make "good" measurable. Each defines dimensions, a rollup method, and a small set of **veto items** (hard fails that cap or block a score regardless of the rest):

| Framework | Scores | Items / dimensions | Rollup | Veto items |
|-----------|--------|--------------------|--------|------------|
| **[TALE](references/tale-benchmark.md)** | Brand narrative Truth / Architecture / Landing / Evidence | T / A / L / E | **NQS = floor(goal-weighted mean)** (arithmetic) | `T1`/`A1`/`L1`/`E1` |
| **[CORE-EEAT](references/core-eeat-benchmark.md)** | Content quality (GEO = CORE avg, SEO = EEAT avg) | 80 items / 8 dimensions | per-dimension averages | `T04`, `C01`, `R10` |
| **[CITE](references/cite-domain-rating.md)** | Domain authority & citation trust | 40 items / 4 dimensions | arithmetic weighted mean | `T03`, `T05`, `T09` |
| **[C³](references/c3-benchmark.md)** | Influencer Creator / Content / Campaign | ACE / ART / ROI · 9 dimensions | **CVI = (ACE × ART × ROI)^⅓** (geometric) | ACE `A2`/`C1`/`E2`, ART `T1`/`T2` |
| **[ROAS](references/roas-benchmark.md)** | Paid ads Return / Offer / Audience / Spend-efficiency | R / O / A / S | **RQS = floor(goal-weighted mean)** (arithmetic) | `R1`/`R2`/`O1`/`O2`/`A1` |
| **[SEND](references/send-benchmark.md)** | Email marketing Sender-integrity / Engagement / Nurture / Direct-response | S / E / N / D | **EQS = floor(goal-weighted mean)** (arithmetic) | `S1`/`S2`/`N1`/`D1` |
| **[RAMP](references/ramp-benchmark.md)** | Product launch Readiness / Assets / Momentum / Proof | R / A / M / P · 40 items | **LQS = floor(goal-weighted mean)** (arithmetic) | `R1`/`A1`/`M1`/`P1` (framework-qualified — distinct from ROAS `R1`/`A1`) |
| **[ECHO](references/echo-benchmark.md)** | Organic social Embeddedness / Craft / Hosting / Observability | E / C / H / O | **SQS = floor(goal-weighted mean)** (arithmetic) | `E1`/`C1`/`C2`/`H1`/`H2`/`O1` (framework-qualified — distinct from ROAS `O1`/`O2`) |

Each framework is enforced by an **auditor-class gate** — a skill that writes a gated artifact (`class: auditor-output`) validated by the PostToolUse hook. Gates are workflow steps, so each lives in its discipline and is counted there:

| Gate | Framework | Lives in | Verdict |
|------|-----------|----------|---------|
| [narrative-quality-auditor](narrative/evaluate/narrative-quality-auditor/SKILL.md) | TALE NQS | `narrative/evaluate/` (narrative) | SHIP / FIX / BLOCK before the narrative is adopted |
| [content-quality-auditor](seo-geo/optimize/content-quality-auditor/SKILL.md) | CORE-EEAT | `seo-geo/optimize/` (SEO/GEO) | SHIP / FIX / BLOCK before publishing |
| [domain-authority-auditor](seo-geo/monitor/domain-authority-auditor/SKILL.md) | CITE | `seo-geo/monitor/` (SEO/GEO) | TRUSTED / CAUTIOUS / UNTRUSTED |
| [content-reviewer](influencer/activate/content-reviewer/SKILL.md) | C³ ART | `influencer/activate/` (influencer) | APPROVED / REVISIONS / REJECTED before a creator post ships |
| [ad-account-auditor](ad/activate/ad-account-auditor/SKILL.md) | ROAS RQS | `ad/activate/` (paid) | SHIP / FIX / BLOCK before budgets scale |
| [email-quality-auditor](email/deliver/email-quality-auditor/SKILL.md) | SEND EQS | `email/deliver/` (email) | SHIP / FIX / BLOCK before send |
| [launch-readiness-auditor](launch/mobilize/launch-readiness-auditor/SKILL.md) | RAMP LQS | `launch/mobilize/` (launch) | SHIP / FIX / BLOCK before the launch moment is committed |
| [social-quality-auditor](social/host/social-quality-auditor/SKILL.md) | ECHO SQS | `social/host/` (social) | SHIP / FIX / BLOCK before publishing |

**Shared cap chassis:** a single veto caps the affected dimension and the overall at `min(raw, 60)`; **two or more vetoes → `BLOCKED`** (no final score). Verdicts are translated to plain language (no item IDs in user-facing reports). Gate mechanics — handoff schema, cap arithmetic, artifact-gate checklist — are specified once in [auditor-runbook.md](references/auditor-runbook.md), and the arithmetic of all eight frameworks is locked by a deterministic golden test (see [Quality guards](#quality-guards-ci)).

### The protocol layer

The `protocol/` directory holds the **shared truth & memory machinery** that sits outside the discipline phase-flows — 8 skills, counted separately:

| Skill | Job | Anchored to | Canonical store |
|-------|-----|-------------|-----------------|
| [entity-optimizer](protocol/entity-optimizer/SKILL.md) | Canonical brand/entity profile (Knowledge Graph, Wikidata, AI disambiguation) | SEO/GEO | `memory/entities/` |
| [creator-registry](protocol/creator-registry/SKILL.md) | Canonical creator roster/dossier — deduped handles, provenance-labeled audience stats, rates, compliance history | influencer | `memory/creators/` |
| [offer-claims-registry](protocol/offer-claims-registry/SKILL.md) | Offer & claim-substantiation ledger — the record the O1/T2 claim checks are judged against | paid | `memory/claims/` |
| [consent-registry](protocol/consent-registry/SKILL.md) | Canonical per-subject consent/suppression record — the S2/N1 vetoes judge against it | email | `memory/consent/` |
| [launch-registry](protocol/launch-registry/SKILL.md) | Canonical launch dossier/calendar — tier, one-way lifecycle stage, authoritative dates/embargo, channel submission ledger; the launch truth SSOT the R1 stage-truth veto judges against | launch | `memory/launch-registry/` |
| [channel-registry](protocol/channel-registry/SKILL.md) | Canonical per-channel record — handles, ownership/authorization, platform norms, disclosure defaults; the channel truth SSOT the ECHO E1 channel-truth veto judges against | social | `memory/channels/` |
| [narrative-registry](protocol/narrative-registry/SKILL.md) | Canonical brand-narrative canon — approved strategic narrative, message system, language/lexicon, proof points; the brand-canon SSOT the TALE T1 truth veto judges against | narrative | `memory/narrative-registry/` |
| [memory-management](protocol/memory-management/SKILL.md) | HOT/WARM/COLD memory lifecycle (capture · promote · demote · archive · query) | all disciplines | `memory/` |

The registries follow a **sole-writer rule** (other skills submit via `candidates.md`), and they *curate* — the gates *judge*. The genuinely horizontal layer beneath everything is the `references/` protocols ([auditor-runbook](references/auditor-runbook.md), [state-model](references/state-model.md), [skill-contract](references/skill-contract.md), [humanizer-slop](references/humanizer-slop.md), [measurement-protocol](references/measurement-protocol.md)) — shared by design as documents, not skills.

### Memory & automation hooks

**Memory** is temperature-tiered, so context survives across skills and sessions without bloating the prompt:

| Tier | Location | Behavior |
|------|----------|----------|
| **HOT** | `memory/hot-cache.md` | Auto-loaded each session; capped at **80 lines AND 25 KB** (whichever trips first). |
| **WARM** | `memory/<subdir>/` | Per-skill working state, gated audit artifacts (`memory/audits/`), and the registries' canonical stores (`memory/entities\|creators\|claims/`). |
| **COLD** | `memory/archive/` | Demoted/older records, kept for recall. |

**Hooks** (`hooks/hooks.json`, runner `hooks/claude-hook.sh`) wire four Claude Code events:

| Event | Matcher | What it does |
|-------|---------|--------------|
| `SessionStart` | `startup\|resume\|clear\|compact` | Injects the **sanitized** hot-cache + load-time over-limit & oldest-dated-entry staleness signals + an open-loops pointer (prompt-injection lines are redacted; symlinked caches are rejected). |
| `UserPromptSubmit` | (all) | Lightweight per-prompt context hook. |
| `PostToolUse` | `Write\|Edit` | Hot-cache size warning **+ the Artifact Gate**: any file under `memory/audits/` that declares `class: auditor-output` is validated against the handoff schema and cap fields, or the write is blocked. The eight auditor-class gates must declare that marker by contract; unmarked files are not auditor artifacts and pass through. |
| `Stop` | (all) | No-op (exits silently). |

The Artifact Gate is **framework-agnostic** — the same hook validates TALE, CORE-EEAT, CITE, C³, ROAS, SEND, RAMP, and ECHO artifacts with no per-framework code.

---

## Skill catalog

Skill links open each `SKILL.md`. Expand the **Details** under each discipline for a one-line purpose per skill. Catalog order follows the [four-layer strata](#the-system-a-four-layer-marketing-operating-system) — Narrative (L1 · Strategy) first, the five always-on channels next, Launch (L3 · Orchestration), then the Protocol layer.

### Narrative — TALE (16)

Four phase directories under `narrative/` (4 skills each) follow the TALE loop (Trace → Architect → Land → Evaluate); the gate (⛩ narrative-quality-auditor) sits in Evaluate. Only the gate computes the goal-weighted NQS — every other skill works one lever and hands off. Narrative is the L1 · Strategy layer: one brand voice the five always-on channels inherit. It absorbs positioning — `positioning-mapper` stays physically in `launch/` but reads logically as the front of TALE Trace.

| Phase | Skills |
|-------|--------|
| **Trace** | [narrative-baseline-mapper](narrative/trace/narrative-baseline-mapper/SKILL.md), [category-narrative-mapper](narrative/trace/category-narrative-mapper/SKILL.md), [audience-belief-mapper](narrative/trace/audience-belief-mapper/SKILL.md), [positioning-truth-tracer](narrative/trace/positioning-truth-tracer/SKILL.md) |
| **Architect** | [strategic-narrative-designer](narrative/architect/strategic-narrative-designer/SKILL.md), [message-system-architect](narrative/architect/message-system-architect/SKILL.md), [brand-language-codifier](narrative/architect/brand-language-codifier/SKILL.md), [story-bank-builder](narrative/architect/story-bank-builder/SKILL.md) |
| **Land** | [narrative-cascade-planner](narrative/land/narrative-cascade-planner/SKILL.md), [pitch-narrative-builder](narrative/land/pitch-narrative-builder/SKILL.md), [narrative-enablement-kit](narrative/land/narrative-enablement-kit/SKILL.md), [proof-point-packager](narrative/land/proof-point-packager/SKILL.md) |
| **Evaluate** | ⛩ [narrative-quality-auditor](narrative/evaluate/narrative-quality-auditor/SKILL.md), [message-test-designer](narrative/evaluate/message-test-designer/SKILL.md), [narrative-resonance-monitor](narrative/evaluate/narrative-resonance-monitor/SKILL.md), [narrative-drift-monitor](narrative/evaluate/narrative-drift-monitor/SKILL.md) |

<details><summary><b>Per-skill purpose (Narrative)</b></summary>

| Skill | TALE lever | What it does |
|-------|-----------|--------------|
| narrative-baseline-mapper | T | Capture the current, actual brand story as it lives across owned surfaces — the honest starting point before any redesign. |
| category-narrative-mapper | T | Map the category's dominant narratives and named alternatives so the brand can claim a defensible, differentiated position. |
| audience-belief-mapper | T | Surface what the target audience already believes, doubts, and cares about — the beliefs the narrative must move. |
| positioning-truth-tracer | T | Trace every positioning claim back to substantiation, retiring anything unsupported (upstream of the T1 truth veto). |
| strategic-narrative-designer | A | Design the core strategic narrative — the change-in-the-world story arc, stakes, and resolution the brand leads with. |
| message-system-architect | A | Architect the message system — tagline, pillars, proof points, and per-audience angles as one coherent structure. |
| brand-language-codifier | A | Codify voice, tone, lexicon, and do/don't language so every channel sounds like one brand. |
| story-bank-builder | A | Build a reusable bank of proof stories, customer narratives, and analogies channels can draw from. |
| narrative-cascade-planner | L | Plan how the narrative cascades into each channel and moment without dilution or drift. |
| pitch-narrative-builder | L | Shape the narrative into pitch form — deck spine, demo story, and investor/press framing. |
| narrative-enablement-kit | L | Enablement kit that lets every team tell the story consistently — talk track, FAQ, and message map. |
| proof-point-packager | L | Package proof points into channel-ready, claims-ledger-aware assets. |
| ⛩ narrative-quality-auditor | T+A+L+E (NQS) | Auditor-class TALE gate: scores NQS, enforces T1/A1/L1/E1, emits SHIP/FIX/BLOCK; carries a **narrative-adoption go/no-go** mode. |
| message-test-designer | E | Design message tests — variant matrix, audience cells, and resonance read for the strategic narrative. |
| narrative-resonance-monitor | E | Track how the narrative is landing across channels from keyless sources (proxy data labeled). |
| narrative-drift-monitor | E | Watch for narrative drift — where channels have wandered off the approved canon — and flag corrections. |

**Reused cross-discipline** (counted in their home phases, not duplicated): [positioning-mapper](launch/research/positioning-mapper/SKILL.md) (logically the front of Trace, physically in `launch/`), [message-house-builder](launch/assemble/message-house-builder/SKILL.md), `audience-mapper`, `share-of-voice-tracker` (resonance denominator). **No new connector** — narrative resonance reuses `bluesky.py` / `gdelt.py` / `tavily.py` / `wayback.py` — see [tale-benchmark.md](references/tale-benchmark.md).

</details>

### SEO/GEO (16)

Four phase directories (4 skills each) plus the discipline's two quality gates (marked ⛩).

| Phase | Skills |
|-------|--------|
| **Research** | [keyword-research](seo-geo/research/keyword-research/SKILL.md), [competitor-analysis](seo-geo/research/competitor-analysis/SKILL.md), [serp-analysis](seo-geo/research/serp-analysis/SKILL.md), [content-gap-analysis](seo-geo/research/content-gap-analysis/SKILL.md) |
| **Build** | [content-writer](seo-geo/build/content-writer/SKILL.md), [geo-content-optimizer](seo-geo/build/geo-content-optimizer/SKILL.md), [serp-markup-builder](seo-geo/build/serp-markup-builder/SKILL.md), [page-play-builder](seo-geo/build/page-play-builder/SKILL.md) |
| **Optimize** | ⛩ [content-quality-auditor](seo-geo/optimize/content-quality-auditor/SKILL.md), [technical-seo-checker](seo-geo/optimize/technical-seo-checker/SKILL.md), [on-page-seo-auditor](seo-geo/optimize/on-page-seo-auditor/SKILL.md), [site-structure-optimizer](seo-geo/optimize/site-structure-optimizer/SKILL.md) |
| **Monitor** | ⛩ [domain-authority-auditor](seo-geo/monitor/domain-authority-auditor/SKILL.md), [rank-tracker](seo-geo/monitor/rank-tracker/SKILL.md), [performance-monitor](seo-geo/monitor/performance-monitor/SKILL.md), [offsite-signal-analyzer](seo-geo/monitor/offsite-signal-analyzer/SKILL.md) |

<details><summary><b>Per-skill purpose (SEO/GEO)</b></summary>

| Skill | What it does |
|-------|--------------|
| keyword-research | Start keyword work for a page/topic/campaign — intent, demand, and striking-distance opportunities. |
| competitor-analysis | Analyze a competitor's SEO strategy, compare domains, surface their keywords and gaps. |
| serp-analysis | Read a SERP — features, snippets, People Also Ask, ranking patterns for a query. |
| content-gap-analysis | Find missing topics and coverage holes versus competitors. |
| content-writer | *(merge: seo-content-writer + content-refresher)* Write and refresh SEO-optimized articles, landing pages, and product copy. |
| geo-content-optimizer | Optimize content for AI engines (ChatGPT, Perplexity, AI Overviews, Gemini, Claude, Copilot). |
| serp-markup-builder | *(merge: meta-tags-optimizer + schema-markup-generator)* Title/meta/OG/Twitter tags plus JSON-LD / Schema.org structured data. |
| page-play-builder | *(merge: programmatic + parasite + comparison + local SEO, 4 modes)* Template-driven page plays — programmatic pages, parasite platforms, comparison pages, local/GBP. |
| ⛩ content-quality-auditor | 80-item CORE-EEAT publish-readiness gate (SHIP/FIX/BLOCK). |
| technical-seo-checker | Site speed, Core Web Vitals, indexing, crawlability, robots. |
| on-page-seo-auditor | Audit page-level on-page health — headings, keyword placement, images, quality signals. |
| site-structure-optimizer | *(merge: internal-linking-optimizer + site-architecture)* Internal links, anchor-text, orphan pages, page hierarchy, URL taxonomy, hub/spoke clusters. |
| ⛩ domain-authority-auditor | 40-item CITE domain-trust gate (TRUSTED/CAUTIOUS/UNTRUSTED). |
| rank-tracker | Track keyword rankings, position changes, and drops. |
| performance-monitor | *(merge: performance-reporter + alert-manager)* Multi-metric SEO/GEO reports, dashboards, and threshold alerts. |
| offsite-signal-analyzer | *(merge: backlink-analyzer + ai-traffic)* Backlink profile + link quality, plus referral traffic from AI assistants in your own GA4/GSC/logs. |

</details>

### Influencer (16)

Four phase directories (4 skills each); the discipline's gate (⛩ content-reviewer) sits in Activate.

| Phase | Skills |
|-------|--------|
| **Discover** | [audience-mapper](influencer/discover/audience-mapper/SKILL.md), [trend-spotter](influencer/discover/trend-spotter/SKILL.md), [influencer-discovery](influencer/discover/influencer-discovery/SKILL.md), [fit-scorer](influencer/discover/fit-scorer/SKILL.md) |
| **Plan** | [competitor-tracker](influencer/plan/competitor-tracker/SKILL.md), [campaign-planner](influencer/plan/campaign-planner/SKILL.md), [brief-generator](influencer/plan/brief-generator/SKILL.md), [budget-optimizer](influencer/plan/budget-optimizer/SKILL.md) |
| **Activate** | [outreach-manager](influencer/activate/outreach-manager/SKILL.md), ⛩ [content-reviewer](influencer/activate/content-reviewer/SKILL.md), [contract-helper](influencer/activate/contract-helper/SKILL.md), [content-amplifier](influencer/activate/content-amplifier/SKILL.md) |
| **Measure** | [landing-optimizer](influencer/measure/landing-optimizer/SKILL.md), [performance-analyzer](influencer/measure/performance-analyzer/SKILL.md), [roi-calculator](influencer/measure/roi-calculator/SKILL.md), [report-generator](influencer/measure/report-generator/SKILL.md) |

<details><summary><b>Per-skill purpose (Influencer)</b></summary>

| Skill | What it does |
|-------|--------------|
| audience-mapper | *(merge: audience-analyzer + niche-researcher)* Profile the target audience and map its subculture / micro-community before partnering with creators. |
| trend-spotter | Campaign timing and themes — trending hashtags, sounds, formats, cultural moments. |
| influencer-discovery | Build a creator roster from scratch, expand to a new platform, source nano/micro at scale. |
| fit-scorer | Objective, weighted fit score for a shortlist (scored on C³ ACE). |
| competitor-tracker | A competitor's creators, campaigns, formats, estimated reach/spend, and gaps. |
| campaign-planner | Plan a campaign, product launch, tentpole, or always-on creator program. |
| brief-generator | Standardized influencer briefs and reusable team templates. |
| budget-optimizer | Allocate spend across tiers/platforms, project ROI, model scenarios (also serves paid-ads spend + bid-pacing). |
| outreach-manager | Pitch, follow-up cadence, re-engagement, rate negotiation, status tracking. |
| ⛩ content-reviewer | Pre-publish gate decision on a creator submission (C³ ART: FTC disclosure T1, claim integrity T2). |
| contract-helper | Draft/review creator agreements — usage rights, exclusivity, standard clauses. |
| content-amplifier | *(merge: content-amplifier + ugc-repurposer)* Extend organic creator content with paid spend and repurpose UGC across paid, web, email, and organic. |
| landing-optimizer | Landing pages for creator/paid traffic — message match, mobile, A/B (also serves paid post-click). |
| performance-analyzer | Evaluate creator results, compare creators, sentiment, conversions (also the paid cross-channel scorecard). |
| roi-calculator | Measure/project ROI, defend budgets, value creators/tiers (shared return-math engine, incl. paid). |
| report-generator | Written stakeholder reports after a period (also paid-ads reports). |

</details>

### Paid Ads — ROAS (16)

Four phase directories under `ad/` (4 skills each) follow the ROAS loop; the gate (⛩ ad-account-auditor) sits in Activate. Only the gate computes the goal-weighted RQS — every other skill works one lever and hands off.

| Phase | Skills |
|-------|--------|
| **Research** | [campaign-architect](ad/research/campaign-architect/SKILL.md), [audience-segment-builder](ad/research/audience-segment-builder/SKILL.md), [search-term-miner](ad/research/search-term-miner/SKILL.md), [product-feed-optimizer](ad/research/product-feed-optimizer/SKILL.md) |
| **Orchestrate** | [ad-creative-builder](ad/orchestrate/ad-creative-builder/SKILL.md), [ad-test-designer](ad/orchestrate/ad-test-designer/SKILL.md), [bid-strategy-planner](ad/orchestrate/bid-strategy-planner/SKILL.md), [landing-experience-checker](ad/orchestrate/landing-experience-checker/SKILL.md) |
| **Activate** | ⛩ [ad-account-auditor](ad/activate/ad-account-auditor/SKILL.md), [conversion-signal-qa](ad/activate/conversion-signal-qa/SKILL.md), [placement-exclusion-manager](ad/activate/placement-exclusion-manager/SKILL.md), [conversion-value-mapper](ad/activate/conversion-value-mapper/SKILL.md) |
| **Scale** | [paid-measurement-loop](ad/scale/paid-measurement-loop/SKILL.md), [attribution-reconciler](ad/scale/attribution-reconciler/SKILL.md), [budget-pacing-monitor](ad/scale/budget-pacing-monitor/SKILL.md), [fatigue-frequency-manager](ad/scale/fatigue-frequency-manager/SKILL.md) |

<details><summary><b>Per-skill purpose (Paid Ads)</b></summary>

| Skill | ROAS lever | What it does |
|-------|-----------|--------------|
| campaign-architect | A + structure | Account/campaign structure, campaign-type fit, match types, negatives/exclusions, paid↔organic cannibalization; carries a recurring **search-term-mining** mode. |
| audience-segment-builder | A | Turns your own customer/CRM/GA4 export into seed audiences, lookalike seeds, exclusion segments, and a funnel-stage targeting map. |
| search-term-miner | A | *(NEW)* Mine the search-terms report for negatives, new keyword candidates, and match-type refinements. |
| product-feed-optimizer | O | *(NEW)* Shopping/PMax feed hygiene — titles, attributes, GTINs, category mapping, and disapproval fixes. |
| ad-creative-builder | O | RSA headlines/descriptions, hooks, and an angle matrix, message-matched to the destination page. |
| ad-test-designer | O (+S) | Design A/B/n & incrementality tests (hypothesis, variant matrix, sample size/power) and read out significance → promote/kill. |
| bid-strategy-planner | S | *(NEW)* Pick and configure bid strategy vs goal (tCPA/tROAS/max-conversions), seed targets, and plan learning-phase transitions. |
| landing-experience-checker | O | *(NEW)* Post-click page QA for ad relevance, load speed, mobile, and policy — the ad↔page message-match check. |
| ⛩ ad-account-auditor | R+O+A+S (RQS) | Auditor-class ROAS gate: scores RQS, enforces R1/R2/O1/O2/A1, emits SHIP/FIX/BLOCK; carries a **launch go/no-go** mode. |
| conversion-signal-qa | R | Pre-launch tracking QA (event firing, UTM hygiene, dedup gate, window alignment, iOS-ATT flags) — the R1/R2 prerequisite (builds the signal; the gate scores it). |
| placement-exclusion-manager | A | *(NEW)* Placement/audience exclusion lists — brand-safety blocks, junk-placement pruning, wasted-spend suppression. |
| conversion-value-mapper | R | *(NEW)* Map conversion actions to values/weights and value rules so tROAS bids on true margin, not raw counts. |
| paid-measurement-loop | R (+S) | Read one shipped change back against a control over a window → Promote / Keep-testing / Rollback / Unproven. |
| attribution-reconciler | R | Standing order-ID de-dup against the GA4/ecommerce truth set, window/currency normalization, model comparison, incrementality. |
| budget-pacing-monitor | S | *(NEW)* Track spend pace against budget over the flight, flag under/over-delivery, and recommend pacing corrections. |
| fatigue-frequency-manager | O | *(NEW)* Watch frequency and creative-decay signals, flag fatigued ads, and schedule refresh/rotation. |

**Reused cross-discipline** (counted in their home phases, not duplicated): [budget-optimizer](influencer/plan/budget-optimizer/SKILL.md) (spend + bid-pacing/learning-phase mode), [landing-optimizer](influencer/measure/landing-optimizer/SKILL.md) (post-click), [roi-calculator](influencer/measure/roi-calculator/SKILL.md) (return math), [report-generator](influencer/measure/report-generator/SKILL.md), [performance-analyzer](influencer/measure/performance-analyzer/SKILL.md).

</details>

### Email — SEND (16)

Four phase directories under `email/` (4 skills each) follow the SEND loop; the gate (⛩ email-quality-auditor) sits in Deliver. Only the gate computes the goal-weighted EQS — every other skill works one lever and hands off. Use-case-agnostic (B2C lifecycle / B2B cold outbound / newsletter-creator); the goal-weight column picks the emphasis.

| Phase | Skills |
|-------|--------|
| **Setup** | [deliverability-qa](email/setup/deliverability-qa/SKILL.md), [list-segment-builder](email/setup/list-segment-builder/SKILL.md), [list-growth-designer](email/setup/list-growth-designer/SKILL.md), [list-hygiene-monitor](email/setup/list-hygiene-monitor/SKILL.md) |
| **Engage** | [email-creative-builder](email/engage/email-creative-builder/SKILL.md), [subject-line-lab](email/engage/subject-line-lab/SKILL.md), [email-render-builder](email/engage/email-render-builder/SKILL.md), [dynamic-content-personalizer](email/engage/dynamic-content-personalizer/SKILL.md) |
| **Nurture** | [email-sequence-designer](email/nurture/email-sequence-designer/SKILL.md), [newsletter-monetization-planner](email/nurture/newsletter-monetization-planner/SKILL.md), [preference-frequency-manager](email/nurture/preference-frequency-manager/SKILL.md), [reactivation-specialist](email/nurture/reactivation-specialist/SKILL.md) |
| **Deliver** | ⛩ [email-quality-auditor](email/deliver/email-quality-auditor/SKILL.md), [send-experiment-designer](email/deliver/send-experiment-designer/SKILL.md), [inbox-placement-monitor](email/deliver/inbox-placement-monitor/SKILL.md), [cold-outbound-sequencer](email/deliver/cold-outbound-sequencer/SKILL.md) |

<details><summary><b>Per-skill purpose (Email)</b></summary>

| Skill | SEND lever | What it does |
|-------|-----------|--------------|
| deliverability-qa | S | Pre-flight SPF/DKIM/DMARC/BIMI auth, reputation, inbox-placement, spam-content, and list hygiene (the S1 check). |
| list-segment-builder | E | Behavioral + lifecycle-stage segments and suppression rules from your own list/CRM/GA4 export. |
| list-growth-designer | S (+N) | List-growth strategy — acquisition channels, lead-magnet concepts, a compliant opt-in capture-flow spec, and referral-loop mechanics; feeds S consent-quality captured at acquisition. |
| list-hygiene-monitor | S | *(NEW)* Ongoing list health — bounce/complaint pruning, sunset policies, re-permission, and inactive-segment suppression. |
| email-creative-builder | E (+D) | Subject/preheader/body/CTA, message-matched to the landing page, claims-ledger-aware. |
| subject-line-lab | E | *(NEW)* Subject/preheader ideation and scoring — length, spam-trigger, curiosity/clarity balance, variant sets for testing. |
| email-render-builder | E | *(NEW)* HTML email build/QA — client compatibility, dark-mode, accessibility, plain-text alt, and render-test checklist. |
| dynamic-content-personalizer | E | *(NEW)* Merge-tag/liquid personalization blocks, conditional content rules, and fallback-value safety. |
| email-sequence-designer | N | Lifecycle/automation flows (welcome, cart, post-purchase, win-back) + frequency governance. |
| newsletter-monetization-planner | D | Paid-sub, sponsorship inventory + rate card, and referral growth-loop economics. |
| preference-frequency-manager | N | *(NEW)* Preference-center design and send-frequency governance to cut fatigue and unsubscribes. |
| reactivation-specialist | N | *(NEW)* Win-back / re-engagement flows for dormant subscribers with sunset-or-recover decision rules. |
| ⛩ email-quality-auditor | S+E+N+D (EQS) | Auditor-class SEND gate: scores EQS, enforces S1/S2/N1/D1, emits SHIP/FIX/BLOCK; carries a **pre-send go/no-go** mode. |
| send-experiment-designer | E | A/B / send-time / hold-out design with sample-size + significance read (promote/kill). |
| inbox-placement-monitor | S | *(NEW)* Ongoing inbox-vs-spam placement tracking via seed lists and provider signals, with reputation-drift alerts. |
| cold-outbound-sequencer | D | *(NEW)* Compliant B2B cold-outbound cadences — deliverability-safe ramp, personalization tokens, and reply-handling steps. |

**Reused cross-discipline** (counted in their home phases, not duplicated): [audience-mapper](influencer/discover/audience-mapper/SKILL.md), [landing-optimizer](influencer/measure/landing-optimizer/SKILL.md), [roi-calculator](influencer/measure/roi-calculator/SKILL.md), [report-generator](influencer/measure/report-generator/SKILL.md), [performance-analyzer](influencer/measure/performance-analyzer/SKILL.md), [offer-claims-registry](protocol/offer-claims-registry/SKILL.md).

</details>

### Launch — RAMP (16)

Four phase directories under `launch/` (4 skills each) follow the RAMP loop; the gate (⛩ launch-readiness-auditor) sits in Mobilize. Only the gate computes the goal-weighted LQS — every other skill works one lever and hands off. Use-case-agnostic (B2B SaaS sales-led / dev-tool community launch / mobile app-store launch); the goal-weight column picks the emphasis.

| Phase | Skills |
|-------|--------|
| **Research** | [positioning-mapper](launch/research/positioning-mapper/SKILL.md), [launch-tier-planner](launch/research/launch-tier-planner/SKILL.md), [launch-window-planner](launch/research/launch-window-planner/SKILL.md), [early-access-designer](launch/research/early-access-designer/SKILL.md) |
| **Assemble** | [message-house-builder](launch/assemble/message-house-builder/SKILL.md), [launch-asset-packager](launch/assemble/launch-asset-packager/SKILL.md), [pricing-packaging-planner](launch/assemble/pricing-packaging-planner/SKILL.md), [sales-enablement-kit](launch/assemble/sales-enablement-kit/SKILL.md) |
| **Mobilize** | ⛩ [launch-readiness-auditor](launch/mobilize/launch-readiness-auditor/SKILL.md), [launch-day-conductor](launch/mobilize/launch-day-conductor/SKILL.md), [community-launch-runner](launch/mobilize/community-launch-runner/SKILL.md), [press-media-relations](launch/mobilize/press-media-relations/SKILL.md) |
| **Prove** | [launch-monitor](launch/prove/launch-monitor/SKILL.md), [launch-feedback-synthesizer](launch/prove/launch-feedback-synthesizer/SKILL.md), [launch-retro-analyzer](launch/prove/launch-retro-analyzer/SKILL.md), [momentum-planner](launch/prove/momentum-planner/SKILL.md) |

<details><summary><b>Per-skill purpose (Launch)</b></summary>

| Skill | RAMP lever | What it does |
|-------|-----------|--------------|
| positioning-mapper | R | Dunford-style positioning canvas — named competitive alternatives, unique attributes, value themes, beachhead segment, onlyness statement. |
| launch-tier-planner | R | Tier decision (Tier 1 flagship / Tier 2 targeted / Tier 3 changelog-level), launch-type declaration, KPI targets, risk register with kill criteria. |
| launch-window-planner | R | Candidate-window comparison (conflicts / tailwinds / risk), launch-week vs rolling-release call, store-review buffer, embargo window definition. |
| early-access-designer | R | Waitlist→concept→alpha→beta→GA stage ladder with graduation criteria, cohort gating, feedback loop, referral mechanics (upstream of the R1 stage-truth veto). |
| message-house-builder | A | Message house (tagline, one-liner, value pillars, proof points) + working-backwards PR-FAQ spine + per-channel angle packs (upstream of A1). |
| launch-asset-packager | A | Tier-scoped launch asset manifest — press kit spec, demo/screenshot specs, launch FAQ, store-listing metadata, technical go-live checklist. |
| pricing-packaging-planner | A | Launch pricing & packaging — tier structure, value-to-price map, launch-offer ladder, beta pricing with graduation path, guarantee terms. |
| sales-enablement-kit | A | Internal enablement — battle cards, sales talk track, objection-handling table, internal FAQ + CS macros, embargo-disciplined internal announcement. |
| ⛩ launch-readiness-auditor | R+A+M+P (LQS) | Auditor-class RAMP gate: scores LQS, enforces R1/A1/M1/P1, emits SHIP/FIX/BLOCK; carries a **T-1 go/no-go** mode. |
| launch-day-conductor | M | Hour-blocked launch-day runbook — pre-conditions gate check, observation-window verdicts after irreversible pushes, P0–P3 incident ladder + rollback playbooks. |
| community-launch-runner | M | Per-platform submission packages (Product Hunt, Show HN, subreddits, directory waves, regional/Chinese channels) under a platform red-line check. |
| press-media-relations | M | Three-tier media/analyst list, embargo pitch timing, press-release draft in standard structure, analyst briefing outline. |
| launch-monitor | P | T-0→T+30 window watch — instrumentation verification (upstream of P1), rank/review/news polling, D0/W1/M1 KPI snapshots, spike-vs-sustain reads. |
| launch-feedback-synthesizer | P | Feedback theme digest, open→shipped status loop ("you asked, we shipped"), compliant social-proof harvest. |
| launch-retro-analyzer | P | D1/W1/M1 retro — per-channel actual-vs-target, 5-Whys on the largest miss, keep/kill/change decisions, outcome snapshot to the registry. |
| momentum-planner | P | T+1→T+30 momentum plan — launch-moment calendar, announcement-tier routing, relaunch legitimacy call, next Tier-1 moment. |

**Reused cross-discipline** (counted in their home phases, not duplicated): `audience-mapper`, `trend-spotter`, `budget-optimizer`, `landing-optimizer`, `campaign-planner`, `outreach-manager`, `content-amplifier`, `email-creative-builder` / `email-sequence-designer` / `cold-outbound-sequencer`, `campaign-architect` / `ad-creative-builder`, `page-play-builder` / `content-writer`, `technical-seo-checker` / `serp-markup-builder`, `performance-monitor`, `keyword-research`, `entity-optimizer`, `offer-claims-registry`, `consent-registry`, `list-growth-designer`, `roi-calculator` / `performance-analyzer` / `report-generator` — see [ramp-benchmark.md](references/ramp-benchmark.md).

</details>

### Social — ECHO (16)

Four phase directories under `social/` (4 skills each) follow the ECHO loop; the gate (⛩ social-quality-auditor) sits in Host. Only the gate computes the goal-weighted SQS — every other skill works one lever and hands off. Use-case-agnostic (community/dev-tool / B2C brand / B2B founder-led); the goal-weight column picks the emphasis. The discipline ships **no** posting, engagement, or DM automation of any kind.

| Phase | Skills |
|-------|--------|
| **Explore** | [channel-portfolio-planner](social/explore/channel-portfolio-planner/SKILL.md), [voice-dossier-builder](social/explore/voice-dossier-builder/SKILL.md), [platform-norm-profiler](social/explore/platform-norm-profiler/SKILL.md), [participation-warmup-planner](social/explore/participation-warmup-planner/SKILL.md) |
| **Craft** | [social-calendar-builder](social/craft/social-calendar-builder/SKILL.md), [social-creative-builder](social/craft/social-creative-builder/SKILL.md), [short-video-scripter](social/craft/short-video-scripter/SKILL.md), [advocacy-program-designer](social/craft/advocacy-program-designer/SKILL.md) |
| **Host** | ⛩ [social-quality-auditor](social/host/social-quality-auditor/SKILL.md), [engagement-inbox-manager](social/host/engagement-inbox-manager/SKILL.md), [social-selling-planner](social/host/social-selling-planner/SKILL.md), [crisis-response-planner](social/host/crisis-response-planner/SKILL.md) |
| **Observe** | [social-pulse-monitor](social/observe/social-pulse-monitor/SKILL.md), [share-of-voice-tracker](social/observe/share-of-voice-tracker/SKILL.md), [dark-social-attributor](social/observe/dark-social-attributor/SKILL.md), [social-measurement-loop](social/observe/social-measurement-loop/SKILL.md) |

<details><summary><b>Per-skill purpose (Social)</b></summary>

| Skill | ECHO lever | What it does |
|-------|-----------|--------------|
| channel-portfolio-planner | E | Pick the platform mix and per-channel role/cadence from where the audience actually is (records channels to the registry). |
| voice-dossier-builder | E | Brand voice, tone, persona, and do/don't lexicon for consistent human-sounding presence. |
| platform-norm-profiler | E | Per-platform norms, formats, ranking signals, and red-line rules before you post there. |
| participation-warmup-planner | E | Non-promotional community warm-up plan — where to show up and add value before selling. |
| social-calendar-builder | C | Editorial calendar — themes, series, cadence balanced to real capacity (no over-posting). |
| social-creative-builder | C | Platform-native posts (hook/body/CTA), message-matched and claims-ledger-aware. |
| short-video-scripter | C | Short-form video scripts — hook, beats, on-screen text, retention structure. |
| advocacy-program-designer | C | Employee/community advocacy program — opt-in, disclosure defaults, sharable asset kit. |
| ⛩ social-quality-auditor | E+C+H+O (SQS) | Auditor-class ECHO gate: scores SQS, enforces E1/C1/C2/H1/H2/O1, emits SHIP/FIX/BLOCK; carries a **pre-publish go/no-go** mode. |
| engagement-inbox-manager | H | Reply/comment/DM triage playbook — response tiers, escalation, genuine-engagement discipline (no manufactured/baited engagement). |
| social-selling-planner | H | Founder/team social-selling motion — relationship-first outreach, no automated DMs. |
| crisis-response-planner | H | Pre-drafted crisis tiers, holding statements, escalation ladder, and pause-the-queue triggers. |
| social-pulse-monitor | O | Mentions/sentiment/topic pulse from keyless sources, spike-vs-sustain reads (proxy data labeled). |
| share-of-voice-tracker | O | Share-of-voice vs named competitors over a period-stable denominator. |
| dark-social-attributor | O | Attribute dark-social/unlinked traffic — UTM discipline, self-reported-attribution capture, referral parsing. |
| social-measurement-loop | O | Read one shipped change back against a baseline over a window → Promote / Keep-testing / Rollback. |

**Reused cross-discipline** (counted in their home phases, not duplicated): `trend-spotter`, `audience-mapper`, `content-amplifier`, `outreach-manager`, `competitor-tracker`, `landing-optimizer`, `performance-analyzer`, `roi-calculator`, `report-generator`, `offer-claims-registry`, `community-launch-runner`, `creator-registry`, `page-play-builder`, `memory-management` — see [echo-benchmark.md](references/echo-benchmark.md).

</details>

### Protocol layer (8)

The shared truth & memory machinery — see [Architecture § The protocol layer](#the-protocol-layer) for roles and sole-writer rules.

| Group | Skills |
|-------|--------|
| **Protocol** | [entity-optimizer](protocol/entity-optimizer/SKILL.md), [creator-registry](protocol/creator-registry/SKILL.md), [offer-claims-registry](protocol/offer-claims-registry/SKILL.md), [consent-registry](protocol/consent-registry/SKILL.md), [launch-registry](protocol/launch-registry/SKILL.md), [channel-registry](protocol/channel-registry/SKILL.md), [narrative-registry](protocol/narrative-registry/SKILL.md), [memory-management](protocol/memory-management/SKILL.md) |

<details><summary><b>Per-skill purpose (Protocol)</b></summary>

| Skill | What it does |
|-------|--------------|
| entity-optimizer | Canonical entity profile for Knowledge Graph, Wikidata, AI disambiguation. |
| creator-registry | Canonical creator roster/dossier — deduped handles, provenance-labeled audience stats, rates, compliance history. |
| offer-claims-registry | Canonical offer & claim-substantiation ledger — the record the O1/T2 claim checks are judged against. |
| consent-registry | Canonical per-subject consent/suppression record — opt-in timestamp + lawful basis, double-opt-in proof, append-only unsub/bounce/complaint history; the record the S2/N1 vetoes judge against. |
| launch-registry | Canonical per-launch dossier + launch calendar — tier, launch type, one-way lifecycle stage (draft→…→GA), authoritative dates + embargo commitments, channel submission ledger, outcome snapshot; the launch truth SSOT. |
| channel-registry | Canonical per-channel record — handles, ownership/authorization, platform norms, disclosure defaults; the channel truth SSOT the ECHO E1 channel-truth veto judges against. |
| narrative-registry | Canonical brand-narrative canon — approved strategic narrative, message system, language/lexicon, proof points; the brand-canon SSOT the TALE T1 truth veto judges against. |
| memory-management | Review, promote, demote, and archive HOT/WARM/COLD project memory. |

</details>

---

## Commands

Eight commands: `/aaron-marketing:auto` routes any goal across all seven disciplines, and each discipline has exactly one explicit entrypoint. Source: [commands/](commands).

| Command | Use it for | Narrowing |
|---------|-----------|-----------|
| `/aaron-marketing:auto` | Describe any goal — infers intent and runs the smallest useful workflow | `--deep` (exhaustive / stress-test) |
| `/aaron-marketing:narrative` | Brand narrative (TALE loop): trace the current story & category, architect the strategic narrative & message system, land it across channels, the quality gate, resonance & drift | `--phase trace\|architect\|land\|evaluate` |
| `/aaron-marketing:seo-geo` | SEO/GEO end-to-end: research demand/competitors, create content, audit quality/tech/visibility/authority, track rankings/reports/memory | `--mode research\|create\|audit\|track` + per-mode flags (`--competitors` `--map` · `--brief` `--series` `--refresh` `--publish` `--meta` `--schema` `--type` · `--full` `--tech` `--visibility` `--authority` · `--alert` `--report` `--remember` `--period`) |
| `/aaron-marketing:influencer` | Influencer: audience insight, discovery & fit, planning, outreach, amplification, ROI | `--phase discover\|plan\|activate\|measure` |
| `/aaron-marketing:ad` | Paid ads (ROAS loop): segments, structure, creative, experiment design, the audit gate, measurement | `--phase research\|orchestrate\|activate\|scale` |
| `/aaron-marketing:email` | Email (SEND loop): deliverability/consent, segmentation, creative, lifecycle flows, monetization, send-testing, the audit gate | `--phase setup\|engage\|nurture\|deliver` |
| `/aaron-marketing:launch` | Product launch (RAMP loop): positioning, tier & window, message house & assets, the readiness gate, launch-day run, monitoring & retro | `--phase research\|assemble\|mobilize\|prove` |
| `/aaron-marketing:social` | Organic social (ECHO loop): channel portfolio & voice, calendar & creative, the quality gate, engagement/crisis hosting, pulse & measurement | `--phase explore\|craft\|host\|observe` |

Daily work normally starts with `/aaron-marketing:auto`; the other seven are explicit discipline entrypoints, with `--mode` / `--phase` to narrow the stage.

**Rename note:** commands use the `/aaron-marketing:` prefix. The former `research` / `create` / `audit` / `track` commands are now modes of `/aaron-marketing:seo-geo` (flags unchanged). Older `/seo:*` and `/aaron-seo-geo:*` names recover via `auto` — e.g. `/aaron-marketing:auto /aaron-seo-geo:audit https://example.com/blog/post` returns `/aaron-marketing:seo-geo https://example.com/blog/post --mode audit`.

---

## Connectors & enhancement tiers

Skills name tools with `~~category` placeholders (`~~SEO tool`, `~~web analytics`, `~~ad platform`, `~~email platform`, …) instead of specific vendors, and every category has a **keyless Tier-1 path**. Full recipes — including the free/first-party endpoint for each category — are in [CONNECTORS.md](CONNECTORS.md).

### The connector layer is a product in itself

**100+ documented integration paths** across three engineered layers — and every one of them earns its place:

| Layer | What you get |
|-------|--------------|
| **21 bundled zero-dependency connectors** | Pure Python stdlib — no `pip`, no build step. Keyless live SERP + JS-rendered scraping (Firecrawl, Tavily), an AI-answer citation probe, DNS-over-HTTPS email-auth pulls, Wikipedia attention series, GDELT news mentions, real YouTube creator metrics, IndexNow + Baidu index push, Resend ESP automation, and a git-diffable measurement ledger that turns any of them into a before/after time series. |
| **60+ documented official/free APIs** | Every row links the vendor's **official documentation**, carries a verified-on date, and every link is HTTP-checked before it ships. Includes the paths most tool lists miss: GSC URL Inspection, CrUX History (40 weeks of field CWV), the Gmail Postmaster Tools API, Meta's Ad Library, Microsoft Clarity's Data Export API. |
| **Vendor MCP servers** | 18 remote endpoints catalogued (never auto-registered — your `/mcp` list stays clean) plus the official self-hosted servers for Google Analytics, Search Console, **Google Ads**, and **Microsoft Clarity**. Two remote MCPs work with no key at all (Firecrawl, Tavily). |

What makes them trustworthy rather than just numerous:

- **Three safety classes, engineered gates** ([SECURITY.md](SECURITY.md)): hosted fetchers run a **local robots.txt pre-flight** before every delegated fetch and refuse on Disallow; anything that mutates external state (email sends, index pushes) is **dry-run by default** behind an explicit `--live` flag, with idempotency keys where the vendor supports them and no auto-retry where it doesn't.
- **Verified, then re-verified**: endpoints are checked against primary vendor docs with dates, keyless paths are live-tested, a CI guard enforces version/tracking sync, and a pre-release live smoke catches endpoint drift (it has already caught real API changes — twice).
- **Facts, not verdicts**: connectors report record presence, parsed tags, and raw series; the auditor gates do the judging, and skills label every number **Measured / User-provided / Estimated**.
- **A written playbook** ([docs/connector-playbook.md](docs/connector-playbook.md)) governs every addition — qualify, verify, implement, test, wire, document, track, regress, record — so quality holds as the catalog grows.

| Tier | Requires | You get |
|------|----------|---------|
| **Tier 1** (default) | Nothing | Paste data, or pull it from free/public sources. The full analysis framework runs either way. |
| **Tier 2** | One free first-party API or MCP | Automatic retrieval of your own GSC / GA4 / Core Web Vitals data. |
| **Tier 3** | A fuller MCP set | Fully automated multi-source workflows. |

- **Bundled zero-dependency helpers** under `scripts/connectors/` (Python stdlib only) pull public/own data locally — e.g. PageSpeed/CrUX, Open PageRank, page crawl, Wayback CDX, Wikidata SPARQL, Common Crawl, advertools recipes — plus **`resend.py`**, direct Resend ESP automation for the email skills (free-tier key: domain-auth status, seed-test sends, suppression sync, broadcast scheduling; mutating subcommands dry-run by default and require `--live`), and **`firecrawl.py`** + **`tavily.py`**, keyless hosted-fetcher automation for the research skills (Firecrawl: live web SERP + JS-rendered page markdown + site maps; Tavily: scored search + an AI answer engine's cited-sources probe for GEO + URL extract — both free with no key at all, both with a local robots.txt pre-flight built in).
- **Free/keyless sources** documented per category: Google Search Console & GA4 (own data), PageSpeed/CrUX, Wikidata, Common Crawl, Open PageRank, Firecrawl keyless SERP/scrape, Tavily keyless AI-search, DNS-over-HTTPS email-auth records (`doh.py`), Wikipedia attention series (`pageviews.py`), GDELT news mentions (`gdelt.py`), YouTube creator metrics on a free key (`youtube.py`), IndexNow + Baidu index push (`indexpush.py`, dry-run gated), the ad-transparency libraries (Meta/Google/TikTok), and recipe rows for crt.sh, the W3C validator, oEmbed, and HN Algolia.
- **Opt-in MCP servers** (Ahrefs, Semrush, SE Ranking, SISTRIX, SimilarWeb, the self-hosted free **OpenSEO** suite, Cloudflare, Vercel, HubSpot, Amplitude, Notion, Webflow, Sanity, Contentful, Slack, Resend, the keyless Firecrawl and Tavily) are catalogued in [`docs/mcp-catalog.json`](docs/mcp-catalog.json) as a **copy-paste reference only** — the catalog sits outside the auto-registered plugin-root `.mcp.json` path, so nothing is registered for you. Copy the entries you want into your own MCP config.

Paid-ads skills score from your **own-account manual export** (native ad-manager CSV, GA4, ecommerce). Keyed ad-platform APIs (Google Ads SDK, Meta Marketing API) are opt-in Tier-2/3 only and **never** a Tier-1 requirement. Email skills score the same way — from your **own ESP export** — and every deliverability signal is keyless (DNS lookups, a DMARC RUA report, and a seed-list inbox test), so a keyed ESP API is never a Tier-1 requirement either; when Resend is your ESP, the bundled `resend.py` automates the same loop on the free tier.

---

## Recommended workflows

**SEO/GEO**
1. **Research** — `keyword-research` → `competitor-analysis` → `content-gap-analysis`
2. **Build** — `content-writer` → `geo-content-optimizer` → `serp-markup-builder` / `page-play-builder`
3. **Optimize** — `content-quality-auditor` (⛩ publish gate) → `on-page-seo-auditor` → `technical-seo-checker` → `site-structure-optimizer`
4. **Monitor** — `rank-tracker` → `performance-monitor` → `offsite-signal-analyzer`; `domain-authority-auditor` (⛩) for the trust review

**Influencer**
1. **Discover** — `audience-mapper` → `trend-spotter` → `influencer-discovery` → `fit-scorer` (C³ ACE)
2. **Plan** — `competitor-tracker` → `campaign-planner` → `brief-generator` → `budget-optimizer`
3. **Activate** — `outreach-manager` → `content-reviewer` (⛩ ART gate) → `contract-helper` → `content-amplifier`
4. **Measure** — `landing-optimizer` → `performance-analyzer` → `roi-calculator` → `report-generator`

**Paid Ads (ROAS loop)**
1. **Research** — `audience-segment-builder` → `campaign-architect`
2. **Orchestrate** — `ad-creative-builder` → `ad-test-designer` (+ `landing-optimizer` for the page)
3. **Activate** — `conversion-signal-qa` → `ad-account-auditor` (⛩ RQS gate) before any budget goes live
4. **Scale** — `paid-measurement-loop` → `attribution-reconciler` → `roi-calculator` → `report-generator`

**Email (SEND loop)**
1. **Setup** — `deliverability-qa` → `list-segment-builder`
2. **Engage** — `email-creative-builder`
3. **Nurture** — `email-sequence-designer` → `newsletter-monetization-planner`
4. **Deliver** — `send-experiment-designer` → `email-quality-auditor` (⛩ EQS gate) before send

For a full trust review, pair `content-quality-auditor` with `domain-authority-auditor` for a combined 120-item assessment. With `memory-management` active, handoffs and open loops persist in HOT/WARM/COLD memory automatically.

---

## Repository layout

```
narrative/{trace,architect,land,evaluate}/                  # Narrative — TALE (16, incl. its gate)
seo-geo/{research,build,optimize,monitor}/                  # SEO/GEO (16, incl. its 2 gates)
influencer/{discover,plan,activate,measure}/                   # Influencer (16, incl. its gate)
ad/research|orchestrate|activate|scale/            # Paid Ads — ROAS (16, incl. its gate)
email/setup|engage|nurture|deliver/                  # Email — SEND (16, incl. its gate)
launch/research|assemble|mobilize|prove/             # Launch — RAMP (16, incl. its gate)
social/explore|craft|host|observe/                   # Social — ECHO (16, incl. its gate)
protocol/                                            # Protocol layer (8) — truth registries + memory
commands/        # 8 slash commands (auto, narrative, seo-geo, influencer, ad, email, launch, social)
references/      # shared contract, state model, the 8 benchmarks, auditor runbook, platform packs
evals/           # per-skill structural eval cases + structure-manifest.json
hooks/           # hooks.json + claude-hook.sh (the only runtime logic)
scripts/         # validate-skill.sh + connectors/ (stdlib) + CI guards
memory/          # HOT/WARM/COLD scaffolding + registry stores (entities/creators/claims/consent/launch/channels/narrative-registry)
docs/            # localized README (zh)
.claude-plugin/  # plugin.json + marketplace.json mirror
```

---

## Design philosophy

- **Skills are content.** The only code is the Bash validator, the Bash hook runner, and zero-dependency Python-stdlib connector/check helpers. No third-party / `pip` dependencies, ever — enforced by a dependency-creep guard.
- **Keyless first.** Every `~~category` has a free/own-data recipe; MCP and paid tools are pure convenience.
- **Surgical & MECE.** Each skill owns one job with a crisp scope boundary; overlapping work ships as a *mode* of an existing skill rather than a new thin skill. Registries curate, gates judge, analyzers feed gates.
- **No invented numbers.** Skills label every figure Measured / User-provided / Estimated and ship an AI-slop / banned-phrase detector.
- **Compliance is guidance, not law.** FTC-disclosure and claim-integrity checks flag risk; they are not legal advice.

---

## Quality guards (CI)

Every change runs against a set of fail-closed guards (all in `scripts/` and `tests/`):

| Guard | Checks |
|-------|--------|
| `validate-skill.sh` | Frontmatter, required sections, version consistency, plugin-relative links across all 120 skills. |
| `golden-auditor-math.py` | Deterministic weight-sum + worked-example arithmetic for **all eight** frameworks. |
| `check-evals.py` | Eval structural lint + `structure-manifest.json` (120/120 skills carry eval cases). |
| `check-pii.py` | Blocks committed secrets / PII (token-level allowlist, fail-closed). |
| `check-stdlib-only.sh` | Dependency-creep guard + the Paid-Ads keyed-API red line. |
| `check-versions.sh` | Version-sync guard: bundle version identical across plugin.json / both marketplace mirrors / both README badges / CLAUDE.md / VERSIONS.md release line + changelog entry, and every SKILL.md version matches its VERSIONS.md row. |
| `tests/test_connectors_local.py` | Offline unit tests for every connector's pure request-builders (no network in CI). |
| `tests/test_hook_artifact_gate.sh` | Behavior tests for the hook's Artifact Gate + SessionStart sanitization. |

Live endpoint drift is covered separately by the **manual** [`scripts/connectors/smoke-live.sh`](scripts/connectors/smoke-live.sh) — one minimal real call per hosted connector with shape assertions (rate-limit answers count as SKIP); run it before a release, never in CI.

---

## Contributing & project docs

- **[CONTRIBUTING.md](CONTRIBUTING.md)** — authoring rules, the contribution checklist, and the authoritative 8-file tracking list.
- **[VERSIONS.md](VERSIONS.md)** — per-skill versions + changelog (current bundle: `16.1.0`).
- **[SECURITY.md](SECURITY.md)** · **[PRIVACY.md](PRIVACY.md)** · **[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)** — security, privacy, and community policy.
- **[CLAUDE.md](CLAUDE.md)** / **[AGENTS.md](AGENTS.md)** — agent-facing context for this repo.

---

## Disclaimer

These skills assist brand-narrative, SEO/GEO, influencer-marketing, paid-ads, email-marketing, product-launch, and organic-social workflows but do **not** guarantee rankings, AI citations, traffic, engagement, conversions, ROAS, deliverability, or business outcomes. Influencer-, ad-, email-, and social-compliance checks (FTC disclosure, claim integrity, platform policy, consent/opt-in, material-connection disclosure) are guidance, not legal advice. Verify recommendations with qualified professionals before relying on them for major strategy, financial, or legal decisions.

## License

Apache License 2.0 — see [LICENSE](LICENSE).

## Star History

<a href="https://www.star-history.com/?repos=aaron-he-zhu%2Faaron-marketing-skills&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&theme=dark&legend=top-left&sealed_token=K6urMhBIrcVIXJvMDWhgZP6KneM8cTo073XO6c-99j4vYWm7J_YIu_W3HFewr-QySk00ZWB9V0Btf-aJPMWiYZjcmuIqBh2G6aEd69Sw43PX7ypi90Il-lwwtdBkmx_1g_Sw589a2axs_lHmFfnANYjjmJwtTtmXy7RY07-HAASvV5LxsgpYwabVPwKZ" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&legend=top-left&sealed_token=K6urMhBIrcVIXJvMDWhgZP6KneM8cTo073XO6c-99j4vYWm7J_YIu_W3HFewr-QySk00ZWB9V0Btf-aJPMWiYZjcmuIqBh2G6aEd69Sw43PX7ypi90Il-lwwtdBkmx_1g_Sw589a2axs_lHmFfnANYjjmJwtTtmXy7RY07-HAASvV5LxsgpYwabVPwKZ" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&legend=top-left&sealed_token=K6urMhBIrcVIXJvMDWhgZP6KneM8cTo073XO6c-99j4vYWm7J_YIu_W3HFewr-QySk00ZWB9V0Btf-aJPMWiYZjcmuIqBh2G6aEd69Sw43PX7ypi90Il-lwwtdBkmx_1g_Sw589a2axs_lHmFfnANYjjmJwtTtmXy7RY07-HAASvV5LxsgpYwabVPwKZ" />
 </picture>
</a>
