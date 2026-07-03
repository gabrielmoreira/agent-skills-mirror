---
name: content-amplifier
description: 'Use when the user asks to "amplify influencer content with paid media", "set up whitelisting or Spark Ads", or "decide which posts to boost"; produces a content-selection scorecard, a paid amplification strategy (whitelisting/boosting/dark posts), audience targeting, and a budget+optimization plan. Not for creating ad variations from raw clips — use ugc-repurposer.'
version: "11.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Activate when the user has organic influencer content and wants to extend its reach with paid spend: choosing which posts to boost, setting up whitelisted Partnership Ads or TikTok Spark Ads, planning dark posts, allocating an ad budget across creators and platforms, building audience targeting off creator lookalikes, or running an optimization and scale/pause playbook for boosted creator content."
argument-hint: "<campaign or content set> [budget] [platform]"
metadata:
  author: aaron-he-zhu
  version: "11.0.0"
  discipline: influencer
  phase: convert
  family: influencer-marketing
  impact-phase: Convert
---

# Content Amplifier

This skill helps you extend the reach of influencer content through paid amplification strategies. It identifies which content to boost, how to set up campaigns, and how to optimize for maximum impact.

## Quick Start

Shortest invocation:

```
Which influencer content should we amplify from [campaign]?
```

Common scenario:

```
Create a paid amplification plan for our influencer campaign with $[X] budget across TikTok and Instagram
```

## Skill Contract

- **Reads**: organic content set (creator handles, platform, content type, reach, engagement rate, views), amplification budget, campaign objective (awareness/traffic/conversions), target platforms, any prior performance data the user provides.
- **Writes**: content-selection scorecard, paid amplification strategy (whitelisting / brand boosting / dark posts), audience targeting plan, budget allocation, optimization playbook. Save to `memory/influencer/content-amplifier/YYYY-MM-DD-<topic>.md`.
- **Promotes**: durable facts (chosen amplification mix, per-creator spend tiers, winning audiences, scale/pause thresholds) to `memory/hot-cache.md`.
- **Done when**:
  1. Each candidate piece is scored and tiered (must amplify / consider / do not amplify) with a recommended spend.
  2. A budget allocation exists by content, objective, and platform, summing to the stated budget.
  3. An optimization plan with KPI targets and scale/pause rules is recorded.
- **Primary next skill**: [ugc-repurposer](../../convert/ugc-repurposer/SKILL.md) — turn the selected winners into ad variations.

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../references/skill-contract.md).

## Data Sources

This family is Tier 1: it works with no live integrations. Ask the user for the content set, budget, objective, and platforms, and the skill produces the full plan from those inputs.

Where a connector could sharpen the output (all optional):

- `~~social platform analytics` — pull organic reach, engagement rate, and view counts instead of asking the user to paste them.
- `~~ad platform` (Meta Ads Manager, TikTok Ads Manager, Google Ads) — read live CPM/CTR/CPC/ROAS for the optimization playbook, and confirm Spark Ads / Partnership Ad authorization status.
- `~~influencer database` — verify creator audience demographics for lookalike targeting.
- `~~CRM` — supply customer and retargeting audiences for conversion campaigns and exclusions.

See [CONNECTORS.md](../../CONNECTORS.md) for the verified free/keyless recipe per category. None are required; absent a connector, the user supplies the numbers.

## Instructions

When a user requests amplification help, run these steps. Each step has a fill-in template in [references/templates.md](references/templates.md) — produce the populated artifact, do not skip the table.

1. **Assess available content** — build the content inventory: campaign, piece count, budget, and a performance overview table (creator, platform, type, organic reach, ER, views, potential).
2. **Select content for amplification** — weight selection criteria (organic performance, hook quality, message clarity, production quality, CTA), score each piece /25, then tier into Must Amplify / Consider If Budget Allows / Do Not Amplify with recommended spend.
3. **Develop amplification strategy** — pick the mix across three methods: whitelisting / Spark Ads (run through the creator's account, best for native feel and social proof), brand account boosting (full targeting control, less authentic), and dark posts (test variations, specific targeting). Output a budget-split table by method.
4. **Set up targeting** — primary lookalike off the creator's engaged audience, plus expansion segments (interest/behavioral/demographic for awareness; retargeting/custom/lookalike for conversions), ad sets per platform, and exclusions.
5. **Allocate budget** — split the stated budget by content, by objective, and by platform (with CPM estimates), and set a pacing schedule (learning → optimization → scaling). Allocations must sum to the stated budget.
6. **Optimization playbook** — KPI table (CPM, CTR, CPC, CVR, ROAS) with below/above-target actions, an optimization schedule, A/B tests, and explicit scale-up / pause / creative-refresh thresholds.
7. **Platform-specific setup** — creator authorization + campaign steps for Meta Partnership Ads, TikTok Spark Ads, and YouTube video ads. Full step-by-step in the reference.

Save the populated artifact to `memory/influencer/content-amplifier/YYYY-MM-DD-<topic>.md` and promote durable facts (chosen mix, per-creator spend tiers, winning audiences, scale/pause thresholds) to `memory/hot-cache.md`.

## Example

**User**: "We have 5 influencer TikToks from our launch campaign. Which should we amplify with our $5,000 paid budget?"

**Output (abbreviated)**:

```markdown
## Amplification Recommendation

| Creator | Views | ER | Hook | Amplify? | Budget |
|---------|-------|-----|------|----------|--------|
| @creator1 | 245K | 8.2% | 5/5 | ✅ Yes | $2,000 |
| @creator3 | 89K | 6.5% | 4/5 | ✅ Yes | $1,500 |
| @creator4 | 34K | 9.8% | 4/5 | ✅ Yes | $800 |
| @creator2 | 156K | 4.1% | 3/5 | ⚠️ Maybe | $500 |
| @creator5 | 67K | 2.3% | 2/5 | ❌ No | $0 |

Testing reserve $200. Setup: get Spark Ads auth from top 3, run @creator1 as
awareness and @creator3 as traffic, scale winners after the 3-day learning phase.
```

Full ranking, strategy, and setup-priority output: [references/templates.md](references/templates.md#worked-example).

## Reference Materials

- [templates.md](references/templates.md) — fill-in templates for all 7 steps, platform setup guides, the full worked example, and amplification tips.

- [skill-contract.md](../../references/skill-contract.md) — shared contract and Handoff Summary format.
- [state-model.md](../../references/state-model.md) — HOT/WARM/COLD memory tiers and save conventions.
- [CONNECTORS.md](../../CONNECTORS.md) — free/keyless data recipes per connector category.
- Platform format & algorithm specs (for picking placements and tuning paid amplification per channel): [tiktok](../../references/platforms/tiktok.md) · [youtube](../../references/platforms/youtube.md) · [linkedin](../../references/platforms/linkedin.md) · [x](../../references/platforms/x.md) · [reddit](../../references/platforms/reddit.md) · [grokipedia](../../references/platforms/grokipedia.md).
- Sibling skills: [content-reviewer](../../activate/content-reviewer/SKILL.md), [ugc-repurposer](../../convert/ugc-repurposer/SKILL.md), [budget-optimizer](../../plan/budget-optimizer/SKILL.md), [performance-analyzer](../../track/performance-analyzer/SKILL.md).

## Next Best Skill

**Primary**: [ugc-repurposer](../../convert/ugc-repurposer/SKILL.md) — turn the selected amplification winners into ad-ready variations and cut-downs.

**Alternates (same Convert family)**:
- [performance-analyzer](../../track/performance-analyzer/SKILL.md) — measure amplification results once campaigns are live.
- [budget-optimizer](../../plan/budget-optimizer/SKILL.md) — reallocate paid budget across the recommended tiers.

**Termination note**: maintain a visited-set this session. If a recommended skill has already run, stop and report the chain complete rather than re-invoking it. Stop after a maximum chain depth of 3.
