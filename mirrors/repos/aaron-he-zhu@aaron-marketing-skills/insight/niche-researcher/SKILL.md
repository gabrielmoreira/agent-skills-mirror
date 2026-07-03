---
name: niche-researcher
description: 'Use when the user asks to "research a niche community", "deep-dive a subculture", or "find micro-niches for a brand"; produces a community map, culture decode (language, norms, taboos), key-voice tiers, content ecosystem, brand-fit score, and a phased entry strategy. Not for finding specific creators to contract — use influencer-discovery.'
version: "11.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Entering a new market or category, understanding a subculture before partnering with creators, identifying micro-communities within a broad audience, finding underserved niches with high engagement, or avoiding cultural missteps in an unfamiliar community. Activate before any creator outreach in a specialized space so the brand learns the language, norms, and taboos first."
argument-hint: "<niche or community> [parent category] [brand or product]"
metadata:
  author: aaron-he-zhu
  version: "11.0.0"
  discipline: influencer
  phase: insight
  family: influencer-marketing
  impact-phase: Insight
---

# Niche Researcher

This skill helps you understand specific niche communities before engaging with influencers in that space. It analyzes community culture, identifies key voices, maps content ecosystems, and reveals the unwritten rules that determine authentic engagement.

## Quick Start

Shortest invocation:

```
Research the [niche] community and identify opportunities for [brand]
```

Common scenario:

```
Deep-dive into [subculture] — who are the key voices, what content works,
and would [brand] be a good fit? Flag the cultural risks.
```

## Skill Contract

- **Reads**: niche/community name, parent category, brand or product, research goal (awareness/partnership/entry), platforms to focus on. Optional prior artifacts from `audience-analyzer` or `trend-spotter` in `memory/influencer/`.
- **Writes**: a niche research dossier (community map, culture decode, voice tiers, content ecosystem, brand-fit score, entry strategy) saved to `memory/influencer/niche-researcher/YYYY-MM-DD-<topic>.md`.
- **Promotes**: durable facts — niche name, brand-fit verdict, top 3 key voices, hard red lines/taboos — to `memory/hot-cache.md`.
- **Done when**:
  - The community is mapped (size, platforms, sub-niches) and its culture decoded (language, norms, taboos).
  - Key voices are tiered and a brand-fit score (out of 25) with a Strong/Moderate/Weak/Poor verdict is recorded.
  - A phased entry strategy and explicit red lines are written to the dossier.
- **Primary next skill**: [trend-spotter](../../insight/trend-spotter/SKILL.md) — surface what is moving inside the niche you just mapped.

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../references/skill-contract.md).

## Data Sources

This family has no live integrations required (Tier 1). The skill works with nothing connected: ask the user for the niche name, parent category, brand, and target platforms, then build the dossier from what they provide plus what you can observe.

Optional connectors that deepen the research where available:

- `~~influencer database` — pull follower counts, growth rates, and past brand partnerships for the voice tiers.
- `~~social platform analytics` — measure engagement rates, hashtag volume, and content-format performance inside the niche.
- `~~social listening` — sample real community language, recurring topics, and sentiment toward brands.
- `~~CRM` — check whether the brand already has relationships with creators in the space.

See [CONNECTORS.md](../../CONNECTORS.md) for the free/keyless recipe per category. None are required; absence just means you ask the user for those inputs instead.

## Instructions

When a user requests niche research, run these steps. Each step has a fill-in template in [references/templates.md](references/templates.md) — populate it with what the user and connectors provide.

1. **Define the niche** — capture niche/community, parent category, brand/product, research goal, and target platforms. ([template](references/templates.md#step-1--define-the-niche))
2. **Map the community** — size, growth, platforms, demographics, psychographics (core identity, values hierarchy), and sub-communities. ([template](references/templates.md#step-2--map-the-community))
3. **Analyze community culture** — language/terminology (including language to avoid), unwritten norms, how credibility and status are earned, content culture, and brand attitudes. This is the load-bearing step; misses here cause cultural missteps. ([template](references/templates.md#step-3--analyze-community-culture))
4. **Identify key voices** — tier them: Tier 1 leaders, Tier 2 rising stars, Tier 3 micro-voices, plus a voice map and collaboration networks. ([template](references/templates.md#step-4--identify-key-voices))
5. **Map the content ecosystem** — top-performing content types, evergreen/trending/controversial themes, formats (high-performance vs saturated), and hashtags/discovery pathways. ([template](references/templates.md#step-5--map-content-ecosystem))
6. **Assess opportunities & risks** — market opportunity, the **Brand Fit Score (X/25)** with a Strong/Moderate/Weak/Poor verdict, risk assessment with mitigations, cultural sensitivities, competitive map, and white-space. ([template](references/templates.md#step-6--assess-opportunities--risks-brand-fit-score))
7. **Generate the entry strategy** — recommended approach, phased rollout (Listen & Learn → Soft Entry → Active Engagement), prioritized creator partnerships, content strategy, success metrics, and explicit **Red Lines**. ([template](references/templates.md#step-7--generate-entry-strategy))

Save the assembled dossier to `memory/influencer/niche-researcher/YYYY-MM-DD-<topic>.md` and promote the niche name, brand-fit verdict, top 3 voices, and hard red lines to `memory/hot-cache.md`.

## Example

**User**: "Research the #BookTok community for a publishing brand"

**Output**: Niche dossier on BookTok — community culture, key voices (e.g. @aikitwokki), content types that perform (book reviews, reading vlogs, shelfies), insider language ("booktok made me buy it"), a Brand Fit Score with verdict, and phased partnership recommendations. See the full walkthrough in [references/templates.md](references/templates.md#worked-example--booktok-for-a-publishing-brand).

## Reference Materials

- [references/templates.md](references/templates.md) — fill-in dossier templates for all 7 steps, the worked example, and tips for success.

- [skill-contract.md](../../references/skill-contract.md) — shared contract and Handoff Summary format.
- [state-model.md](../../references/state-model.md) — temperature memory tiers and save-path conventions.
- [CONNECTORS.md](../../CONNECTORS.md) — free/keyless data recipe per connector category.
- Sibling Insight skills: [audience-analyzer](../audience-analyzer/SKILL.md), [trend-spotter](../trend-spotter/SKILL.md).
- Downstream Map skills: [influencer-discovery](../../map/influencer-discovery/SKILL.md), [fit-scorer](../../map/fit-scorer/SKILL.md).

## Next Best Skill

**Primary**: [trend-spotter](../../insight/trend-spotter/SKILL.md) — surface what is currently moving inside the niche you mapped, so partnerships ride live momentum.

**Alternates (same Insight family)**:
- [audience-analyzer](../audience-analyzer/SKILL.md) — widen from one niche to the broader audience picture when the brand needs cross-community reach.
- [influencer-discovery](../../map/influencer-discovery/SKILL.md) — once the niche and voice tiers are set, find and shortlist specific creators to contract.

**Termination note** (visited-set + depth): if any candidate skill has already been invoked this session, stop and report chain-complete instead of re-running it. Cap the handoff chain at depth 3; beyond that, summarize and hand back to the user.

## Related Skills

- [audience-analyzer](../audience-analyzer/SKILL.md) - Broader audience understanding
- [trend-spotter](../trend-spotter/SKILL.md) - Trends within niches
- [influencer-discovery](../../map/influencer-discovery/SKILL.md) - Find niche influencers
- [fit-scorer](../../map/fit-scorer/SKILL.md) - Evaluate niche influencer fit
