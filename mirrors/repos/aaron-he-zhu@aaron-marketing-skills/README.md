# Aaron Marketing Skills

**54 skills. 4 commands. Three marketing disciplines — SEO/GEO, influencer, paid ads — on one operating contract.**

[![GitHub Stars](https://img.shields.io/github/stars/aaron-he-zhu/aaron-marketing-skills?style=flat)](https://github.com/aaron-he-zhu/aaron-marketing-skills)
[![Version](https://img.shields.io/badge/version-11.0.0-orange)](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/VERSIONS.md)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/aaron-he-zhu/aaron-marketing-skills)](https://github.com/aaron-he-zhu/aaron-marketing-skills/commits/main)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-compatible-purple)](https://claude.ai/download)

[English](README.md) | [中文](docs/README.zh.md)

A library of Claude Skills and slash commands that turns a chat agent into a marketing operator. Three disciplines and a shared protocol layer, at a glance:

| Layer | Skills | Lifecycle (phase directories) | Framework → gate | Entrypoint |
|-------|--------|-------------------------------|------------------|------------|
| **SEO/GEO** | 24 | research → build → optimize → monitor | [CORE-EEAT](references/core-eeat-benchmark.md) → `content-quality-auditor` · [CITE](references/cite-domain-rating.md) → `domain-authority-auditor` | `/aaron-marketing:seo-geo` |
| **Influencer (IMPACT)** | 18 | insight → map → plan → activate → convert → track | [C³](references/c3-benchmark.md) → `content-reviewer` (ART); `fit-scorer` scores ACE | `/aaron-marketing:impact` |
| **Paid ads (ROAS)** | 8 | research → orchestrate → activate → scale | [ROAS](references/roas-benchmark.md) → `ad-account-auditor` (RQS) | `/aaron-marketing:paid` |
| **Protocol layer** | 4 | — (shared machinery, outside the phase flows) | 3 truth registries (entity · creator · offer/claims) + HOT/WARM/COLD memory | — |

`/aaron-marketing:auto` routes any natural-language goal across all of it. Everything is **plain Markdown** — the only code is a Bash hook runner, a Bash validator, and zero-dependency Python-stdlib data helpers (no `pip`, no build step). **Every skill runs at Tier 1 with nothing but data you paste in**; connectors only automate retrieval.

> The SEO/GEO half also ships on its own, unchanged, at [seo-geo-claude-skills](https://github.com/aaron-he-zhu/seo-geo-claude-skills) for users who only want SEO/GEO work.

---

## Contents

- [Why this library](#why-this-library)
- [Install](#install)
- [First run](#first-run)
- [Architecture](#architecture)
  - [The shared skill contract](#the-shared-skill-contract)
  - [One lifecycle, three dialects](#one-lifecycle-three-dialects)
  - [Quality system: four frameworks, four gates](#quality-system-four-frameworks-four-gates)
  - [The protocol layer](#the-protocol-layer)
  - [Memory & automation hooks](#memory--automation-hooks)
- [Skill catalog](#skill-catalog)
  - [SEO/GEO (24)](#seogeo-24)
  - [Influencer — IMPACT (18)](#influencer--impact-18)
  - [Paid Ads — ROAS (8)](#paid-ads--roas-8)
  - [Protocol layer (4)](#protocol-layer-4)
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
| **One shared contract** | All 54 skills expose the same seven sections and self-declare `discipline` + `phase` metadata, so the library behaves like one operating system: each skill knows its inputs, outputs, and the next best skill to hand off to. |
| **Gated quality** | Four benchmarks drive four auditor-class gates that emit structured, machine-checkable verdicts — not vibes. A PostToolUse hook validates every gated artifact before it lands. |
| **Truth lives in registries** | Canonical facts (brand entities, creator dossiers, offer/claim substantiation) live in dedicated protocol-layer registries with sole-writer rules — gates judge against them instead of re-deriving them. |
| **Memory across turns** | A HOT/WARM/COLD memory model carries findings, scores, and open loops between skills and sessions, sanitized on the way in. |
| **Plain voice** | Skills ship an AI-slop detector and a banned-phrase list so output reads like a human wrote it. |

---

## Install

Use it with Claude Code, any Agent Skills-compatible host, or a plain `git clone`:

| Host | Install |
|------|---------|
| **Claude Code** | `/plugin marketplace add aaron-he-zhu/aaron-marketing-skills` then `/plugin install aaron-marketing@aaron` |
| **skills.sh / generic Agent Skills hosts** | `npx skills add aaron-he-zhu/aaron-marketing-skills` |
| **Any host** | `git clone https://github.com/aaron-he-zhu/aaron-marketing-skills` |

In Claude Code, `marketplace add` only registers the catalog — run `/plugin install aaron-marketing@aaron` (or pick it from `/plugin`) to actually enable the skills and commands. To pull a **single** skill on a generic host: `npx skills add aaron-he-zhu/aaron-marketing-skills -s keyword-research`.

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

Every skill also self-declares `metadata.discipline` (seo-geo / influencer / paid / protocol) and `metadata.phase`, so routing and clustering work uniformly. The contract is documented once in [skill-contract.md](references/skill-contract.md); the shared cross-skill state lives in [state-model.md](references/state-model.md).

### One lifecycle, three dialects

The three disciplines share one meta-lifecycle spine; each adapts the granularity to its own workflow (phase *counts* differ by design):

| Meta-stage | SEO/GEO | Influencer (IMPACT) | Paid (ROAS) |
|------------|---------|---------------------|-------------|
| **Understand** | research | insight, map | research |
| **Plan / create** | build | plan | orchestrate |
| **Activate / optimize** | optimize | activate, convert | activate |
| **Measure** | monitor | track | scale |

All three use phase **directories** (`research/`…, `insight/`…, `paid/research/`…). Note "activate" means creator outreach in IMPACT but account-gating in ROAS — same word, discipline-specific scope.

### Quality system: four frameworks, four gates

Four benchmarks make "good" measurable. Each defines dimensions, a rollup method, and a small set of **veto items** (hard fails that cap or block a score regardless of the rest):

| Framework | Scores | Items / dimensions | Rollup | Veto items |
|-----------|--------|--------------------|--------|------------|
| **[CORE-EEAT](references/core-eeat-benchmark.md)** | Content quality (GEO = CORE avg, SEO = EEAT avg) | 80 items / 8 dimensions | per-dimension averages | `T04`, `C01`, `R10` |
| **[CITE](references/cite-domain-rating.md)** | Domain authority & citation trust | 40 items / 4 dimensions | arithmetic weighted mean | `T03`, `T05`, `T09` |
| **[C³](references/c3-benchmark.md)** | Influencer Creator / Content / Campaign | ACE / ART / ROI · 9 dimensions | **CVI = (ACE × ART × ROI)^⅓** (geometric) | ACE `A2`/`C1`/`E2`, ART `T1`/`T2` |
| **[ROAS](references/roas-benchmark.md)** | Paid ads Return / Offer / Audience / Spend-efficiency | R / O / A / S | **RQS = floor(goal-weighted mean)** (arithmetic) | `R1`/`R2`/`O1`/`O2`/`A1` |

Each framework is enforced by an **auditor-class gate** — a skill that writes a gated artifact (`class: auditor-output`) validated by the PostToolUse hook. Gates are workflow steps, so each lives in its discipline and is counted there:

| Gate | Framework | Lives in | Verdict |
|------|-----------|----------|---------|
| [content-quality-auditor](optimize/content-quality-auditor/SKILL.md) | CORE-EEAT | `optimize/` (SEO/GEO) | SHIP / FIX / BLOCK before publishing |
| [domain-authority-auditor](monitor/domain-authority-auditor/SKILL.md) | CITE | `monitor/` (SEO/GEO) | TRUSTED / CAUTIOUS / UNTRUSTED |
| [content-reviewer](activate/content-reviewer/SKILL.md) | C³ ART | `activate/` (influencer) | APPROVED / REVISIONS / REJECTED before a creator post ships |
| [ad-account-auditor](paid/activate/ad-account-auditor/SKILL.md) | ROAS RQS | `paid/activate/` (paid) | SHIP / FIX / BLOCK before budgets scale |

**Shared cap chassis:** a single veto caps the affected dimension and the overall at `min(raw, 60)`; **two or more vetoes → `BLOCKED`** (no final score). Verdicts are translated to plain language (no item IDs in user-facing reports). Gate mechanics — handoff schema, cap arithmetic, artifact-gate checklist — are specified once in [auditor-runbook.md](references/auditor-runbook.md), and the arithmetic of all four frameworks is locked by a deterministic golden test (see [Quality guards](#quality-guards-ci)).

### The protocol layer

The `protocol/` directory holds the **shared truth & memory machinery** that sits outside the discipline phase-flows — 4 skills, counted separately:

| Skill | Job | Anchored to | Canonical store |
|-------|-----|-------------|-----------------|
| [entity-optimizer](protocol/entity-optimizer/SKILL.md) | Canonical brand/entity profile (Knowledge Graph, Wikidata, AI disambiguation) | SEO/GEO | `memory/entities/` |
| [creator-registry](protocol/creator-registry/SKILL.md) | Canonical creator roster/dossier — deduped handles, provenance-labeled audience stats, rates, compliance history | influencer | `memory/creators/` |
| [offer-claims-registry](protocol/offer-claims-registry/SKILL.md) | Offer & claim-substantiation ledger — the record the O1/T2 claim checks are judged against | paid | `memory/claims/` |
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
| `SessionStart` | `startup\|resume\|clear\|compact` | Injects the **sanitized** hot-cache + an open-loops pointer (prompt-injection lines are redacted; symlinked caches are rejected). |
| `UserPromptSubmit` | (all) | Lightweight per-prompt context hook. |
| `PostToolUse` | `Write\|Edit` | Hot-cache size warning **+ the Artifact Gate**: any file under `memory/audits/` that declares `class: auditor-output` is validated against the handoff schema and cap fields, or the write is blocked. The four auditor-class gates must declare that marker by contract; unmarked files are not auditor artifacts and pass through. |
| `Stop` | (all) | No-op (exits silently). |

The Artifact Gate is **framework-agnostic** — the same hook validates CORE-EEAT, CITE, C³, and ROAS artifacts with no per-framework code.

---

## Skill catalog

Skill links open each `SKILL.md`. Expand the **Details** under each discipline for a one-line purpose per skill.

### SEO/GEO (24)

Four phase directories plus the discipline's two quality gates (marked ⛩).

| Phase | Skills |
|-------|--------|
| **Research** | [keyword-research](research/keyword-research/SKILL.md), [competitor-analysis](research/competitor-analysis/SKILL.md), [serp-analysis](research/serp-analysis/SKILL.md), [content-gap-analysis](research/content-gap-analysis/SKILL.md) |
| **Build** | [seo-content-writer](build/seo-content-writer/SKILL.md), [geo-content-optimizer](build/geo-content-optimizer/SKILL.md), [meta-tags-optimizer](build/meta-tags-optimizer/SKILL.md), [schema-markup-generator](build/schema-markup-generator/SKILL.md), [programmatic-seo](build/programmatic-seo/SKILL.md), [parasite-seo](build/parasite-seo/SKILL.md), [comparison-page-builder](build/comparison-page-builder/SKILL.md), [local-seo](build/local-seo/SKILL.md) |
| **Optimize** | [on-page-seo-auditor](optimize/on-page-seo-auditor/SKILL.md), [technical-seo-checker](optimize/technical-seo-checker/SKILL.md), [internal-linking-optimizer](optimize/internal-linking-optimizer/SKILL.md), [content-refresher](optimize/content-refresher/SKILL.md), [site-architecture](optimize/site-architecture/SKILL.md), ⛩ [content-quality-auditor](optimize/content-quality-auditor/SKILL.md) |
| **Monitor** | [rank-tracker](monitor/rank-tracker/SKILL.md), [backlink-analyzer](monitor/backlink-analyzer/SKILL.md), [performance-reporter](monitor/performance-reporter/SKILL.md), [alert-manager](monitor/alert-manager/SKILL.md), [ai-traffic](monitor/ai-traffic/SKILL.md), ⛩ [domain-authority-auditor](monitor/domain-authority-auditor/SKILL.md) |

<details><summary><b>Per-skill purpose (SEO/GEO)</b></summary>

| Skill | What it does |
|-------|--------------|
| keyword-research | Start keyword work for a page/topic/campaign — intent, demand, and striking-distance opportunities. |
| competitor-analysis | Analyze a competitor's SEO strategy, compare domains, surface their keywords and gaps. |
| serp-analysis | Read a SERP — features, snippets, People Also Ask, ranking patterns for a query. |
| content-gap-analysis | Find missing topics and coverage holes versus competitors. |
| seo-content-writer | Write SEO-optimized articles, blog posts, landing pages, and product copy. |
| geo-content-optimizer | Optimize content for AI engines (ChatGPT, Perplexity, AI Overviews, Gemini, Claude, Copilot). |
| meta-tags-optimizer | Title tags, meta descriptions, Open Graph, and Twitter Cards. |
| schema-markup-generator | Generate JSON-LD / Schema.org structured data. |
| programmatic-seo | Generate hundreds–thousands of pages from one template plus a structured dataset. |
| parasite-seo | Publish on high-authority third-party platforms (Medium, Reddit, LinkedIn, Quora, GitHub) for rankings/AI citations. |
| comparison-page-builder | Build "vs", alternatives, and competitor-comparison pages for SEO + sales enablement. |
| local-seo | Google Business Profile, NAP consistency, citations, and location/service-area pages. |
| on-page-seo-auditor | Audit page-level on-page health — headings, keyword placement, images, quality signals. |
| technical-seo-checker | Site speed, Core Web Vitals, indexing, crawlability, robots. |
| internal-linking-optimizer | Internal link structure, anchor-text distribution, orphan pages. |
| content-refresher | Update outdated or declining content with fresh information. |
| site-architecture | Page hierarchy, navigation, URL taxonomy, hub/spoke topic clusters. |
| ⛩ content-quality-auditor | 80-item CORE-EEAT publish-readiness gate (SHIP/FIX/BLOCK). |
| rank-tracker | Track keyword rankings, position changes, and drops. |
| backlink-analyzer | Backlink profile, link quality, toxic links, anchor-text distribution. |
| performance-reporter | Multi-metric SEO/GEO performance reports and stakeholder dashboards. |
| alert-manager | Alerts for rankings, traffic, backlinks, technical issues, AI visibility. |
| ai-traffic | Measure referral traffic from AI assistants in your own GA4 / GSC / server logs. |
| ⛩ domain-authority-auditor | 40-item CITE domain-trust gate (TRUSTED/CAUTIOUS/UNTRUSTED). |

</details>

### Influencer — IMPACT (18)

Six phase directories; the discipline's gate (⛩ content-reviewer) sits in Activate.

| Phase | Skills |
|-------|--------|
| **Insight** | [audience-analyzer](insight/audience-analyzer/SKILL.md), [niche-researcher](insight/niche-researcher/SKILL.md), [trend-spotter](insight/trend-spotter/SKILL.md) |
| **Map** | [influencer-discovery](map/influencer-discovery/SKILL.md), [fit-scorer](map/fit-scorer/SKILL.md), [competitor-tracker](map/competitor-tracker/SKILL.md) |
| **Plan** | [campaign-planner](plan/campaign-planner/SKILL.md), [brief-generator](plan/brief-generator/SKILL.md), [budget-optimizer](plan/budget-optimizer/SKILL.md) |
| **Activate** | [outreach-manager](activate/outreach-manager/SKILL.md), ⛩ [content-reviewer](activate/content-reviewer/SKILL.md), [contract-helper](activate/contract-helper/SKILL.md) |
| **Convert** | [content-amplifier](convert/content-amplifier/SKILL.md), [ugc-repurposer](convert/ugc-repurposer/SKILL.md), [landing-optimizer](convert/landing-optimizer/SKILL.md) |
| **Track** | [performance-analyzer](track/performance-analyzer/SKILL.md), [roi-calculator](track/roi-calculator/SKILL.md), [report-generator](track/report-generator/SKILL.md) |

<details><summary><b>Per-skill purpose (Influencer)</b></summary>

| Skill | What it does |
|-------|--------------|
| audience-analyzer | Profile the target audience at the start of a program or a new segment. |
| niche-researcher | Map a subculture / micro-community before partnering with creators. |
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
| content-amplifier | Extend organic creator content with paid spend (whitelisting, Spark Ads, dark posts). |
| ugc-repurposer | Repurpose UGC across paid ads, website, email, and organic social. |
| landing-optimizer | Landing pages for creator/paid traffic — message match, mobile, A/B (also serves paid post-click). |
| performance-analyzer | Evaluate creator results, compare creators, sentiment, conversions (also the paid cross-channel scorecard). |
| roi-calculator | Measure/project ROI, defend budgets, value creators/tiers (shared return-math engine, incl. paid). |
| report-generator | Written stakeholder reports after a period (also paid-ads reports). |

</details>

### Paid Ads — ROAS (8)

Four phase directories under `paid/` follow the ROAS loop; the gate (⛩ ad-account-auditor) sits in Activate. Only the gate computes the goal-weighted RQS — every other skill works one lever and hands off.

| Phase | Skills |
|-------|--------|
| **Research** | [campaign-architect](paid/research/campaign-architect/SKILL.md), [audience-segment-builder](paid/research/audience-segment-builder/SKILL.md) |
| **Orchestrate** | [ad-creative-builder](paid/orchestrate/ad-creative-builder/SKILL.md), [ad-test-designer](paid/orchestrate/ad-test-designer/SKILL.md) |
| **Activate** | ⛩ [ad-account-auditor](paid/activate/ad-account-auditor/SKILL.md), [conversion-signal-qa](paid/activate/conversion-signal-qa/SKILL.md) |
| **Scale** | [paid-measurement-loop](paid/scale/paid-measurement-loop/SKILL.md), [attribution-reconciler](paid/scale/attribution-reconciler/SKILL.md) |

<details><summary><b>Per-skill purpose (Paid Ads)</b></summary>

| Skill | ROAS lever | What it does |
|-------|-----------|--------------|
| campaign-architect | A + structure | Account/campaign structure, campaign-type fit, match types, negatives/exclusions, paid↔organic cannibalization; carries a recurring **search-term-mining** mode. |
| audience-segment-builder | A | Turns your own customer/CRM/GA4 export into seed audiences, lookalike seeds, exclusion segments, and a funnel-stage targeting map. |
| ad-creative-builder | O | RSA headlines/descriptions, hooks, and an angle matrix, message-matched to the destination page. |
| ad-test-designer | O (+S) | Design A/B/n & incrementality tests (hypothesis, variant matrix, sample size/power) and read out significance → promote/kill. |
| ⛩ ad-account-auditor | R+O+A+S (RQS) | Auditor-class ROAS gate: scores RQS, enforces R1/R2/O1/O2/A1, emits SHIP/FIX/BLOCK; carries a **launch go/no-go** mode. |
| conversion-signal-qa | R | Pre-launch tracking QA (event firing, UTM hygiene, dedup gate, window alignment, iOS-ATT flags) — the R1/R2 prerequisite (builds the signal; the gate scores it). |
| paid-measurement-loop | R (+S) | Read one shipped change back against a control over a window → Promote / Keep-testing / Rollback / Unproven. |
| attribution-reconciler | R | Standing order-ID de-dup against the GA4/ecommerce truth set, window/currency normalization, model comparison, incrementality. |

**Reused cross-discipline** (counted in their home phases, not duplicated): [budget-optimizer](plan/budget-optimizer/SKILL.md) (spend + bid-pacing/learning-phase mode), [landing-optimizer](convert/landing-optimizer/SKILL.md) (post-click), [roi-calculator](track/roi-calculator/SKILL.md) (return math), [report-generator](track/report-generator/SKILL.md), [performance-analyzer](track/performance-analyzer/SKILL.md).

</details>

### Protocol layer (4)

The shared truth & memory machinery — see [Architecture § The protocol layer](#the-protocol-layer) for roles and sole-writer rules.

| Group | Skills |
|-------|--------|
| **Protocol** | [entity-optimizer](protocol/entity-optimizer/SKILL.md), [creator-registry](protocol/creator-registry/SKILL.md), [offer-claims-registry](protocol/offer-claims-registry/SKILL.md), [memory-management](protocol/memory-management/SKILL.md) |

<details><summary><b>Per-skill purpose (Protocol)</b></summary>

| Skill | What it does |
|-------|--------------|
| entity-optimizer | Canonical entity profile for Knowledge Graph, Wikidata, AI disambiguation. |
| creator-registry | Canonical creator roster/dossier — deduped handles, provenance-labeled audience stats, rates, compliance history. |
| offer-claims-registry | Canonical offer & claim-substantiation ledger — the record the O1/T2 claim checks are judged against. |
| memory-management | Review, promote, demote, and archive HOT/WARM/COLD project memory. |

</details>

---

## Commands

Four commands: `/aaron-marketing:auto` routes any goal across all three disciplines, and each discipline has exactly one explicit entrypoint. Source: [commands/](commands/).

| Command | Use it for | Narrowing |
|---------|-----------|-----------|
| `/aaron-marketing:auto` | Describe any goal — infers intent and runs the smallest useful workflow | `--deep` (exhaustive / stress-test) |
| `/aaron-marketing:seo-geo` | SEO/GEO end-to-end: research demand/competitors, create content, audit quality/tech/visibility/authority, track rankings/reports/memory | `--mode research\|create\|audit\|track` + per-mode flags (`--competitors` `--map` · `--brief` `--series` `--refresh` `--publish` `--meta` `--schema` `--type` · `--full` `--tech` `--visibility` `--authority` · `--alert` `--report` `--remember` `--period`) |
| `/aaron-marketing:impact` | Influencer (IMPACT): audience insight, discovery & fit, planning, outreach, amplification, ROI | `--phase insight\|map\|plan\|activate\|convert\|track` |
| `/aaron-marketing:paid` | Paid ads (ROAS loop): segments, structure, creative, experiment design, the audit gate, measurement | `--phase research\|orchestrate\|activate\|scale` |

Daily work normally starts with `/aaron-marketing:auto`; the other three are explicit discipline entrypoints, with `--mode` / `--phase` to narrow the stage.

**Rename note:** commands use the `/aaron-marketing:` prefix. The former `research` / `create` / `audit` / `track` commands are now modes of `/aaron-marketing:seo-geo` (flags unchanged). Older `/seo:*` and `/aaron-seo-geo:*` names recover via `auto` — e.g. `/aaron-marketing:auto /aaron-seo-geo:audit https://example.com/blog/post` returns `/aaron-marketing:seo-geo https://example.com/blog/post --mode audit`.

---

## Connectors & enhancement tiers

Skills name tools with `~~category` placeholders (`~~SEO tool`, `~~web analytics`, `~~ad platform`, …) instead of specific vendors, and every category has a **keyless Tier-1 path**. Full recipes — including the free/first-party endpoint for each category — are in [CONNECTORS.md](CONNECTORS.md).

| Tier | Requires | You get |
|------|----------|---------|
| **Tier 1** (default) | Nothing | Paste data, or pull it from free/public sources. The full analysis framework runs either way. |
| **Tier 2** | One free first-party API or MCP | Automatic retrieval of your own GSC / GA4 / Core Web Vitals data. |
| **Tier 3** | A fuller MCP set | Fully automated multi-source workflows. |

- **Bundled zero-dependency helpers** under `scripts/connectors/` (Python stdlib only) pull public/own data locally — e.g. PageSpeed/CrUX, Open PageRank, page crawl, Wayback CDX, Wikidata SPARQL, Common Crawl, advertools recipes.
- **Free/keyless sources** documented per category: Google Search Console & GA4 (own data), PageSpeed/CrUX, Wikidata, Common Crawl, Open PageRank, and more.
- **Opt-in MCP servers** (Ahrefs, Semrush, SE Ranking, SISTRIX, SimilarWeb, the self-hosted free **OpenSEO** suite, Cloudflare, Vercel, HubSpot, Amplitude, Notion, Webflow, Sanity, Contentful, Slack) are catalogued in [`docs/mcp-catalog.json`](docs/mcp-catalog.json) as a **copy-paste reference only** — the catalog sits outside the auto-registered plugin-root `.mcp.json` path, so nothing is registered for you. Copy the entries you want into your own MCP config.

Paid-ads skills score from your **own-account manual export** (native ad-manager CSV, GA4, ecommerce). Keyed ad-platform APIs (Google Ads SDK, Meta Marketing API) are opt-in Tier-2/3 only and **never** a Tier-1 requirement.

---

## Recommended workflows

**SEO/GEO**
1. **Research** — `keyword-research` → `competitor-analysis` → `content-gap-analysis`
2. **Build** — `seo-content-writer` → `geo-content-optimizer` → `meta-tags-optimizer` / `schema-markup-generator`
3. **Optimize** — `content-quality-auditor` (⛩ publish gate) → `on-page-seo-auditor` → `technical-seo-checker`
4. **Monitor** — `rank-tracker` → `performance-reporter` → `alert-manager`; `domain-authority-auditor` (⛩) for the trust review

**Influencer (IMPACT)**
1. **Insight** — `audience-analyzer` → `trend-spotter` → `niche-researcher`
2. **Map** — `influencer-discovery` → `fit-scorer` (C³ ACE) → `competitor-tracker`
3. **Plan** — `campaign-planner` → `brief-generator` → `budget-optimizer`
4. **Activate** — `outreach-manager` → `content-reviewer` (⛩ ART gate) → `contract-helper`
5. **Convert** — `content-amplifier` → `ugc-repurposer` → `landing-optimizer`
6. **Track** — `performance-analyzer` → `roi-calculator` → `report-generator`

**Paid Ads (ROAS loop)**
1. **Research** — `audience-segment-builder` → `campaign-architect`
2. **Orchestrate** — `ad-creative-builder` → `ad-test-designer` (+ `landing-optimizer` for the page)
3. **Activate** — `conversion-signal-qa` → `ad-account-auditor` (⛩ RQS gate) before any budget goes live
4. **Scale** — `paid-measurement-loop` → `attribution-reconciler` → `roi-calculator` → `report-generator`

For a full trust review, pair `content-quality-auditor` with `domain-authority-auditor` for a combined 120-item assessment. With `memory-management` active, handoffs and open loops persist in HOT/WARM/COLD memory automatically.

---

## Repository layout

```
research/ build/ optimize/ monitor/                  # SEO/GEO (24, incl. its 2 gates)
insight/ map/ plan/ activate/ convert/ track/        # Influencer — IMPACT (18, incl. its gate)
paid/research|orchestrate|activate|scale/            # Paid Ads — ROAS (8, incl. its gate)
protocol/                                            # Protocol layer (4) — truth registries + memory
commands/        # 4 slash commands (auto, seo-geo, impact, paid)
references/      # shared contract, state model, the 4 benchmarks, auditor runbook, platform packs
evals/           # per-skill structural eval cases + structure-manifest.json
hooks/           # hooks.json + claude-hook.sh (the only runtime logic)
scripts/         # validate-skill.sh + connectors/ (stdlib) + CI guards
memory/          # HOT/WARM/COLD scaffolding + registry stores (entities/creators/claims)
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
| `validate-skill.sh` | Frontmatter, required sections, version consistency, plugin-relative links across all 54 skills. |
| `golden-auditor-math.py` | Deterministic weight-sum + worked-example arithmetic for **all four** frameworks. |
| `check-evals.py` | Eval structural lint + `structure-manifest.json` (54/54 skills carry eval cases). |
| `check-pii.py` | Blocks committed secrets / PII (token-level allowlist, fail-closed). |
| `check-stdlib-only.sh` | Dependency-creep guard + the Paid-Ads keyed-API red line. |
| `tests/test_hook_artifact_gate.sh` | Behavior tests for the hook's Artifact Gate + SessionStart sanitization. |

---

## Contributing & project docs

- **[CONTRIBUTING.md](CONTRIBUTING.md)** — authoring rules, the contribution checklist, and the authoritative 8-file tracking list.
- **[VERSIONS.md](VERSIONS.md)** — per-skill versions + changelog (current bundle: `11.0.0`).
- **[SECURITY.md](SECURITY.md)** · **[PRIVACY.md](PRIVACY.md)** · **[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)** — security, privacy, and community policy.
- **[CLAUDE.md](CLAUDE.md)** / **[AGENTS.md](AGENTS.md)** — agent-facing context for this repo.

---

## Disclaimer

These skills assist SEO/GEO, influencer-marketing, and paid-ads workflows but do **not** guarantee rankings, AI citations, traffic, engagement, conversions, ROAS, or business outcomes. Influencer- and ad-compliance checks (FTC disclosure, claim integrity, platform policy) are guidance, not legal advice. Verify recommendations with qualified professionals before relying on them for major strategy, financial, or legal decisions.

## License

Apache License 2.0 — see [LICENSE](LICENSE).

## Star History

<a href="https://www.star-history.com/?repos=aaron-he-zhu%2Faaron-marketing-skills&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&legend=top-left" />
 </picture>
</a>
