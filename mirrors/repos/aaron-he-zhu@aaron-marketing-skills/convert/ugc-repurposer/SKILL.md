---
name: ugc-repurposer
description: 'Use when the user asks to "repurpose influencer content", "turn one video into multiple ads", or "build a UGC asset library"; produces a content inventory with rights, a multi-channel repurposing map (1 video to 10+ assets), per-format transformation specs, and a 30-day distribution plan. Not for paid amplification spend planning — use content-amplifier.'
version: "11.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when a brand has influencer or user-generated content (videos, reels, reviews, images) and wants to extract more value by adapting it across paid ads, website, email, and organic social. Triggers include maximizing ROI on existing UGC, generating ad variations from organic clips, building a searchable content library, populating product pages with social proof, or planning a multi-channel rollout from a small set of source assets."
argument-hint: "<campaign or content set> [target channels]"
metadata:
  author: aaron-he-zhu
  version: "11.0.0"
  discipline: influencer
  phase: convert
  family: influencer-marketing
  impact-phase: Convert
---

# UGC Repurposer

This skill helps you extract maximum value from influencer-generated content by repurposing it across multiple channels and formats. One great piece of content can become many assets.

## Quick Start

Shortest invocation:

```
How can we repurpose this influencer content across channels?
```

Common scenario — turn a small set of clips into a multi-channel plan:

```
We have 3 great TikTok videos from our campaign. Build a repurposing plan and a 30-day distribution calendar.
```

## Skill Contract

- **Reads**: source UGC assets (videos, reels, reviews, images), creator handles and platforms, usage rights per asset, original performance metrics, target channels. Pulls prior campaign context from `memory/hot-cache.md` when `memory-management` is active.
- **Writes**: content inventory, repurposing opportunity map, 30-day distribution plan, format transformation specs, and a rights tracker to `memory/influencer/ugc-repurposer/YYYY-MM-DD-<topic>.md`.
- **Promotes**: durable facts (rights levels, expiration dates, library naming convention, top-performing source assets) to `memory/hot-cache.md`.
- **Done when**:
  - Every source asset has a rights level and expiration recorded.
  - At least one source asset is mapped to 3+ distinct output formats across 2+ channels.
  - A dated distribution plan with an asset checklist exists.
- **Primary next skill**: [landing-optimizer](../../convert/landing-optimizer/SKILL.md) — place the repurposed social-proof assets where they convert.

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../references/skill-contract.md).

## Data Sources

This family needs no live integrations (Tier 1) — it works by asking you for inputs: the asset list, creator handles, rights terms, and original metrics. Provide those and the skill produces the full plan.

Where a tool could speed up or enrich the work, use a `~~` connector placeholder:

- `~~influencer database` — pull creator handles, platforms, and contract rights terms.
- `~~social platform analytics` — original view/engagement metrics to rank repurpose priority.
- `~~DAM / asset library` — store and tag processed assets; enforce the naming convention.
- `~~CRM` — reconcile creator records with usage-rights expirations.

No connector is required. See [CONNECTORS.md](../../CONNECTORS.md) for the free/keyless recipe per category.

## Instructions

When a user requests repurposing help, run these steps. Each step's fill-in template lives in [references/templates.md](references/templates.md) — produce the table/spec for each.

1. **Audit available content** — build a content inventory and rights summary: every asset gets an ID, creator, platform, type, rights level, and status. See [Step 1 template](references/templates.md#step-1--content-inventory).
2. **Map repurposing opportunities** — for each source asset, list output formats, target channels, modifications, and effort (one video → 10+ assets). See [Step 2 template](references/templates.md#step-2--repurposing-opportunity-map).
3. **Create the repurposing plan** — rank source assets by performance and rights, then lay out a channel distribution plan across paid, owned, social, and sales. See [Step 3 template](references/templates.md#step-3--repurposing-plan).
4. **Specify format transformations** — give aspect ratio, duration, and modification specs for video→video, video→static, quote/review, and image conversions. See [Step 4 specs](references/templates.md#step-4--format-transformation-specs). Per-platform specs live in [references/platforms/](../../references/platforms/).
5. **Apply channel guidelines** — website, email, paid (incl. a creative testing matrix), and organic social best practices. See [Step 5 guidelines](references/templates.md#step-5--channel-specific-guidelines).
6. **Build the content library** — folder structure, the `[campaign]_[creator]_[platform]_[type]_[variation]_[date]` naming convention, and metadata fields. See [Step 6 structure](references/templates.md#step-6--content-library-structure).
7. **Track rights** — rights-by-content matrix, expiring-rights alerts, and rights-expansion opportunities. See [Step 7 tracker](references/templates.md#step-7--usage-rights-tracker).

For slicing one source into many output atoms, apply the 7-tier extraction and near-duplicate flag in [references/atom-extraction.md](references/atom-extraction.md). Worked example, extra format specs, and optimization tips: [references/templates.md](references/templates.md).

## Example

**User**: "We have 3 great TikTok videos. How should we repurpose them?"

**Output (abridged)**: 3 source clips ranked by performance → @creator1's 45s demo expands to 6 assets (Spark Ad, IG Reel, website embed, 3 stills, 15s Stories cut), backed by a 30-day calendar and an asset checklist. Full version: [references/templates.md#worked-example--3-tiktok-videos](references/templates.md#worked-example--3-tiktok-videos).

## Reference Materials

- [references/platforms/](../../references/platforms/) — per-platform format specs ([tiktok](../../references/platforms/tiktok.md), [youtube](../../references/platforms/youtube.md), [x](../../references/platforms/x.md), [linkedin](../../references/platforms/linkedin.md), [reddit](../../references/platforms/reddit.md), [grokipedia](../../references/platforms/grokipedia.md)) for adapting one asset to each channel.
- [references/templates.md](references/templates.md) — fill-in templates for all 7 steps, extra format specs, the worked example, and optimization tips.
- [references/atom-extraction.md](references/atom-extraction.md) — 7-tier content-atom extraction, the virality heuristic, and the Jaccard near-duplicate flag for slicing one source into many.
- [skill-contract.md](../../references/skill-contract.md) — shared contract and Handoff Summary format.
- [state-model.md](../../references/state-model.md) — memory tiers and save-path conventions.
- [CONNECTORS.md](../../CONNECTORS.md) — free/keyless data recipe per connector category.
- [content-reviewer](../../activate/content-reviewer/SKILL.md) — ensure source content quality before repurposing.
- [content-amplifier](../../convert/content-amplifier/SKILL.md) — paid amplification of the repurposed UGC.
- [contract-helper](../../activate/contract-helper/SKILL.md) — secure or expand usage rights.
- [performance-analyzer](../../track/performance-analyzer/SKILL.md) — track how repurposed assets perform.

## Next Best Skill

**Primary**: [landing-optimizer](../../convert/landing-optimizer/SKILL.md) — drop the repurposed testimonials, hero videos, and quote cards onto the pages that convert.

**Alternates** (same Convert family):

- [content-amplifier](../../convert/content-amplifier/SKILL.md) — when the repurposed ad variations are ready for paid spend.

Termination note: track a visited-set. If a skill has already run this session, stop and report chain-complete instead of re-invoking it. Max chain depth is 3 hops.

## Related Skills

- [content-reviewer](../../activate/content-reviewer/SKILL.md) - Ensure content quality
- [content-amplifier](../../convert/content-amplifier/SKILL.md) - Paid amplification of UGC
- [contract-helper](../../activate/contract-helper/SKILL.md) - Secure usage rights
- [performance-analyzer](../../track/performance-analyzer/SKILL.md) - Track UGC performance
