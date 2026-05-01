---
type: skill
lifecycle: stable
inheritance: inheritable
name: md-to-epub
description: Convert Markdown to EPUB 3 e-books via Pandoc.
tier: standard
applyTo: '**/*epub*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# md-to-epub

Convert Markdown to EPUB 3 e-books via Pandoc.

## When to Use

- Long-form documents distributed as e-books
- Multi-chapter content with embedded images
- Documents needing TOC, cover, and reflowable text

## What's Here

`md-to-epub.cjs` — Node script that wraps Pandoc.

## External Dependencies

- `node` (≥ 16)
- `pandoc` (≥ 3.0) on PATH

## Usage

```bash
node md-to-epub.cjs input.md
node md-to-epub.cjs input.md --output book.epub
node md-to-epub.cjs input.md --cover cover.png
```

## Frontmatter Hooks

```yaml
---
title: My Book
author: Your Name
publisher: Press Name
language: en
cover-image: cover.png
toc: true
---
```

## Notes

- Mermaid diagrams pre-rendered to PNG and embedded
- Each H1 becomes a chapter; H2 subsections
- Validate with epubcheck before distribution
