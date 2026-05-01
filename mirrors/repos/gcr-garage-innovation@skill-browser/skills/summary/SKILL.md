---
name: summary
description: Shortest English alias for content-summary / content-search-summarization. Use this to search public content platforms, rank top results, and summarize them with links.
license: Proprietary session artifact for local Copilot use
---

# Summary skill

This is the shortest English alias for:

- `content-summary`
- `content-search-summarization`

It is best when you want to:

- search public content platforms
- rank the top N relevant results
- summarize each item with links and confidence notes

## Primary guidance

1. prefer `opencli` for supported platforms
2. fall back to public-page scraping when needed
3. rank by relevance first, popularity second
4. keep summaries conservative when based on metadata

## Quick invocation template

```text
Use /summary to find the top 5 results for <topic> on <platform> and summarize each item with links and confidence labels.
```

```text
请用 /summary 在 <平台> 搜索 <主题>，筛选 Top 5，并输出带链接与置信度的摘要。
```

## Pointer

For the full detailed playbook, see:

- `skills/content-search-summarization/SKILL.md` in this repository
