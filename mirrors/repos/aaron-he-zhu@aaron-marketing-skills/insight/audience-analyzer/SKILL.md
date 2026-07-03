---
name: audience-analyzer
description: 'Use when the user asks to "analyze my target audience" or "build an audience profile for influencer targeting"; produces demographic/psychographic profiles, platform-priority matrices, named personas, and influencer-selection criteria. Not for finding specific creators — use influencer-discovery; not for niche community deep-dives — use niche-researcher.'
version: "11.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Run at the start of an influencer program or when entering a new audience segment. Use when the user wants to understand who their customer is, where that customer spends time online, which creators they trust, and what influencer-selection criteria follow from that. Also use to diagnose why a prior campaign underperformed or to build personas for a creative brief. Works from a brand or product name alone, or from supplied customer data."
argument-hint: "<brand or product> [category] [geographic focus]"
metadata:
  author: aaron-he-zhu
  version: "11.0.0"
  discipline: influencer
  phase: insight
  family: influencer-marketing
  impact-phase: Insight
---

# Audience Analyzer

This skill helps you deeply understand your target audience before selecting influencers. It analyzes demographics, behaviors, content preferences, and platform habits to ensure influencer partnerships reach the right people.

## Quick Start

Shortest invocation:

```
Analyze the target audience for [brand/product/category]
```

Common scenario — build a profile from your own data:

```
Here's our customer data: [data]. Build an audience profile for influencer targeting.
```

## Skill Contract

- **Reads**: brand or product name, category, geographic focus, price point, campaign objective, and any supplied customer data (surveys, social insights, sales records). Prior `niche-researcher` or `trend-spotter` output if present in the hot cache.
- **Writes**: an audience analysis to `memory/influencer/audience-analyzer/YYYY-MM-DD-<topic>.md` — demographic + psychographic profiles, behavioral map, platform-priority matrix, content preferences, influencer-affinity table, named persona, and a must-have/nice-to-have influencer-selection criteria set.
- **Promotes**: durable facts (target age range, priority platforms, ideal influencer profile, persona name) to `memory/hot-cache.md` so downstream skills inherit them.
- **Done when**:
  1. Primary and secondary audiences are profiled across demographics, psychographics, and behavior with stated confidence levels.
  2. A platform-priority matrix and a named persona exist.
  3. An influencer-selection criteria set (must-have, nice-to-have, red flags) is written and ready to hand to discovery.
- **Primary next skill**: [niche-researcher](../../insight/niche-researcher/SKILL.md) — deepen specific communities the persona belongs to before scoring creators.

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../references/skill-contract.md).

## Data Sources

This family is Tier 1 — every step works with no live integration. Ask the user for inputs (brand, category, geography, price point, objective, any customer data) and reason from those. When a connector is available it sharpens the profile but is never required:

- `~~influencer database` — validate which creator tiers and categories the audience actually follows.
- `~~social platform analytics` — confirm platform usage, active times, and engagement style instead of estimating.
- `~~CRM` / `~~customer survey data` — replace assumed demographics and psychographics with first-party facts.
- `~~web analytics` — corroborate the decision journey and discovery method.

Lead with what the user gives you; mark every inferred attribute with a confidence level so unsupported guesses are visible. Connector recipes (free/keyless options included) are in [CONNECTORS.md](../../CONNECTORS.md).

## Instructions

Work through these steps in order. Each step has a fill-in template in [references/templates.md](references/templates.md) — open it and use the matching block. Lead with user-supplied data; mark every inferred attribute with a confidence level (High/Med/Low).

1. **Gather context** — capture brand, category, customer base, geography, price point, and objective. (Template §1.)
2. **Analyze demographics** — profile primary and secondary audiences with confidence levels, then draw implications for influencer selection. (Template §2.)
3. **Profile psychographics** — values, interests, lifestyle, aspirations, and personality traits. (Template §3.)
4. **Map behavioral patterns** — purchase journey, triggers/barriers, daily media diet, and how they interact with influencers. (Template §4.)
5. **Analyze platform preferences** — build the platform-priority matrix, deep-dive the top platform, and recommend where to spend. (Template §5.)
6. **Identify content preferences** — format, tone, aesthetics, engaging topics, and content red flags. (Template §6.)
7. **Profile influencer affinity** — tiers followed, why they follow, trust factors, and the ideal influencer profile. (Template §7.)
8. **Generate an audience persona** — one named persona with bio, day-in-the-life, goals, media consumption, and a key quote. (Template §8.)
9. **Summarize influencer-selection criteria** — must-have / nice-to-have / red flags plus a recommended influencer mix, ready to hand to discovery. (Template §9.)

Save the full analysis to `memory/influencer/audience-analyzer/YYYY-MM-DD-<topic>.md` and promote durable facts (target age range, priority platforms, ideal influencer profile, persona name) to `memory/hot-cache.md`.

## Example

**User**: "Analyze the target audience for a premium skincare brand targeting millennial women."

**Output**: a full analysis following steps 1-9 — demographic and psychographic profiles for millennial women, a platform-priority matrix favoring Instagram and TikTok, a named persona, and a must-have/nice-to-have/red-flag influencer-selection set sized to a mega/macro/micro/nano budget mix. Saved to `memory/influencer/audience-analyzer/`, with age range, priority platforms, and persona name promoted to the hot cache.

## Reference Materials

- Step-by-step fill-in templates and tips: [references/templates.md](references/templates.md)

- Shared contract and handoff schema: [skill-contract.md](../../references/skill-contract.md)
- Shared state model (memory tiers, save paths): [state-model.md](../../references/state-model.md)
- Connector recipes (free/keyless options): [CONNECTORS.md](../../CONNECTORS.md)
- C3 scoring architecture (downstream creator/fit scoring): [references/c3/scoring-architecture.md](../../references/c3/scoring-architecture.md)
- Sibling Insight skills: [niche-researcher](../../insight/niche-researcher/SKILL.md), [trend-spotter](../../insight/trend-spotter/SKILL.md)
- Downstream Map skills: [influencer-discovery](../../map/influencer-discovery/SKILL.md), [fit-scorer](../../map/fit-scorer/SKILL.md)

## Next Best Skill

**Primary**: [niche-researcher](../../insight/niche-researcher/SKILL.md) — deep-dive the specific communities your persona belongs to before scoring creators.

**Alternates** (same Insight family):
- [trend-spotter](../../insight/trend-spotter/SKILL.md) — surface trends and content angles relevant to this audience.

**Termination**: maintain a visited-set across the session. If a recommended skill has already been invoked this run, stop and report the chain is complete rather than re-entering it. Cap any handoff chain at max-depth 3. Once influencer-selection criteria are written and promoted to the hot cache, the audience phase is terminal — hand off to discovery and stop.
