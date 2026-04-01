---
name: arxiv
description: "Search arXiv, inspect paper metadata, and download papers by keyword or arXiv ID. Use when the user wants fresh arXiv search results, paper detail lookup, or direct PDF/source downloads."
emoji: "📚"
triggers:
  - arxiv
  - paper search
  - preprint
---

# ArXiv Search and Download

Use this skill when the user asks for arXiv papers, categories, IDs, or paper downloads.

## Tools

- `arxiv_search`: search arXiv by keywords and optional filters
- `arxiv_get_paper`: fetch metadata for a specific arXiv paper
- `arxiv_download`: download PDF or source files for a paper

## Guidance

- Prefer `arxiv_search` when the request is exploratory.
- Prefer `arxiv_get_paper` when the user already has an arXiv ID.
- Use `arxiv_download` only when the user wants the actual file.
