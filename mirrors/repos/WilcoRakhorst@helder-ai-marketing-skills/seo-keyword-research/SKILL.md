---
name: seo-keyword-research
description: "Deep competitive keyword research and SEO strategy. Takes a primary keyword and researches supporting keywords, competitor analysis, search intent, and per-page keyword mapping. Triggers on 'keyword research', 'SEO research', 'SEO strategy', 'competitive analysis', 'rank for keyword', 'keyword analysis', 'search volume', 'keyword difficulty', 'content gap analysis', 'SERP analysis'."
---

# SEO Keyword Research & Competitive Analysis

Comprehensive keyword research to rank in competitive markets.

## Prerequisites

- A sitemap or page overview of the target website
- User provides the primary keyword

## Workflow

1. **Gather input** — Primary keyword, location, business type, competitors
2. **Competitive analysis** — Analyze top-5 rankings via web search
3. **Keyword discovery** — Find primary, secondary, long-tail, local, and semantic keywords
4. **Intent classification** — Categorize each keyword by search intent
5. **SERP analysis** — Understand what Google rewards for target keywords
6. **Keyword mapping** — Map keywords to specific pages
7. **Content gap analysis** — Find opportunities that competitors miss
8. **Write output** — Generate keyword research report

Full process and output format: see `references/keyword-process.md`

## Input template

```
Primary Keyword: [The main keyword you want to rank for]
Location: [Target geographic area]
Business Type: [Industry/niche]
Known Competitors: [URLs, optional]
```

## Rules

1. ALWAYS use web search for real competitive data — never guess
2. Classify every keyword by search intent
3. Map every keyword to a specific page
4. Identify at least 3 competitive gaps
5. Deliver actionable per-page recommendations
6. Prioritize quick wins (long-tail) alongside primary keywords
7. One primary keyword per page — avoid cannibalization

## Scope

This skill covers strategy and analysis only.
- Content writing → content-creator skill
- Technical SEO → seo-strategy skill
- AI visibility → geo-optimization skill

## Data integrity

No assumptions. Every claim must be traceable to a source. When in doubt: leave it out.
