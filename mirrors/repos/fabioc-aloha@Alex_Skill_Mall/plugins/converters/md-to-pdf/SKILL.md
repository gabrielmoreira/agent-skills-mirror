---
type: skill
lifecycle: stable
inheritance: inheritable
name: md-to-pdf
description: Convert Markdown to PDF via Pandoc with two rendering engines.
tier: standard
applyTo: '**/*pdf*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# md-to-pdf

Convert Markdown to PDF via Pandoc with two rendering engines.

## When to Use

- Reports, manuscripts, and printable documentation
- Documents needing high-fidelity typography (LaTeX engine)
- Faster turnaround drafts (HTML/wkhtmltopdf engine)

## What's Here

`md-to-pdf.cjs` — Node script that wraps Pandoc.

## External Dependencies

- `node` (≥ 16)
- `pandoc` (≥ 3.0) on PATH
- One of:
  - `lualatex` / TeX Live (high-quality typography, slower)
  - `wkhtmltopdf` (HTML route, faster, less precise)

## Usage

```bash
node md-to-pdf.cjs input.md
node md-to-pdf.cjs input.md --engine lualatex
node md-to-pdf.cjs input.md --engine wkhtmltopdf
node md-to-pdf.cjs input.md --output custom.pdf
```

The script auto-detects available engines if `--engine` is omitted, preferring `lualatex` when present.

## Frontmatter Hooks

YAML frontmatter is forwarded to Pandoc. Useful keys:

```yaml
---
title: My Document
author: Your Name
date: 2026-04-28
toc: true
geometry: margin=1in
---
```

## Notes

- Mermaid diagrams are pre-rendered to PNG and embedded
- Code blocks get syntax highlighting via Pandoc's `--highlight-style`
- Round-trip from `md-to-html` → `wkhtmltopdf` is roughly equivalent to the HTML engine
