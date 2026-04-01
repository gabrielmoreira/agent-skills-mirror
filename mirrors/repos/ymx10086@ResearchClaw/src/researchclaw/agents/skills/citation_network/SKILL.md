---
name: citation-network
description: "Explore citation relationships around a known paper to find related work, cited papers, and citing papers. Use when the user asks for follow-up reading around a seed paper."
emoji: "🕸️"
triggers:
  - citation network
  - related papers
  - citing papers
  - references
---

# Citation Network Exploration

Use this skill when the user wants papers related to a known DOI, Semantic Scholar paper ID, or arXiv ID.

## Tools

- `find_related_papers`: expand from a seed paper into citing and referenced papers

## Guidance

- Ask for a paper identifier if the seed paper is ambiguous.
- Keep `depth` small unless the user explicitly wants a broad graph.
- Summarize the relationship between the source paper and the returned papers instead of dumping raw IDs.
