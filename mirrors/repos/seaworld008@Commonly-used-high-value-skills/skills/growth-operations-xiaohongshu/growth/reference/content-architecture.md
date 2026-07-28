# Content Architecture — Pillar-Cluster / Topic Clusters

Purpose: structure a content library so search engines (and AI answer engines) recognize
topical authority, and so internal linking concentrates ranking signal. This is the
information-architecture layer above keyword research — it decides *how pages relate*, not
just which keywords to target.

Use this when planning an SEO/GEO content program, auditing a sprawling blog with no
internal-link strategy, or deciding URL/linking structure for a new content section.

## Contents
- The pillar-cluster model
- Building a cluster
- Internal linking rules
- GEO / AI-answer-engine angle
- Audit & handoffs

## The Pillar-Cluster Model

| Element | Role | Targets |
|---------|------|---------|
| `Pillar page` | broad, comprehensive page on a core topic | high-volume head term ("email marketing") |
| `Cluster pages` | focused pages on subtopics | long-tail / intent-specific terms ("email subject line length") |
| `Links` | every cluster links **up** to the pillar; the pillar links **down** to each cluster | distributes authority, signals topical coverage |

One pillar + 5-20 clusters = one **topic cluster**. The pillar ranks for the head term *because*
it sits at the hub of many supporting pages — authority flows inward through the links.

This replaces the legacy "one page per keyword, no structure" approach, which fragments
authority and creates keyword cannibalization (multiple pages competing for the same term).

## Building a Cluster

1. Pick the core topic from `keyword-research.md` (must have enough subtopic breadth — a single
   long-tail term is not a pillar).
2. Map subtopics by search intent; each distinct intent = one cluster page. Merge near-duplicate
   intents to avoid cannibalization.
3. Write the pillar as the comprehensive overview; write clusters as the deep dives.
4. Wire links: cluster → pillar (required), pillar → every cluster, cluster ↔ cluster only when
   genuinely related.
5. Use a consistent URL pattern (`/topic/` pillar, `/topic/subtopic/` clusters) where practical.

## Internal Linking Rules
- Every cluster page links to its pillar with descriptive anchor text (not "click here").
- The pillar maintains a link to each live cluster — update it when clusters publish.
- Avoid orphan content: any page with no inbound internal link wastes its authority.
- Cross-cluster links only on real topical overlap; forced links dilute the signal.

## GEO / AI-Answer-Engine Angle
- Topical-authority structure also helps **Generative Engine Optimization** (`geo-optimization.md`):
  AI answer engines favor sources with comprehensive, well-interlinked coverage of a topic.
- A complete cluster raises extractability and entity clarity (two of the GEO four signals),
  improving citation/mention rate, not just blue-link ranking.

## Audit & Handoffs
- Audit signals: orphan pages, multiple pages ranking for one term (cannibalization), pillars
  with <5 clusters (thin), clusters with no link to a pillar.
- Handoffs: keyword/intent sourcing → `keyword-research.md`; per-page on-page SEO → `seo-audit.md`
  / `seo-checklist.md`; AI-citation optimization → `geo-optimization.md`; content drafting →
  `Prose`; lifecycle/channel placement of the content → `channel-lifecycle-planning.md`.
