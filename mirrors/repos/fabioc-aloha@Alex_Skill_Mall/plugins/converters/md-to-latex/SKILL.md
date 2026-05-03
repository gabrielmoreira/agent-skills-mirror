---
type: skill
lifecycle: stable
inheritance: inheritable
name: md-to-latex
description: Convert Markdown to LaTeX source via Pandoc.
tier: standard
applyTo: '**/*latex*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# md-to-latex

Convert Markdown to LaTeX source via Pandoc.

## When to Use

- Academic papers, theses, and journal submissions
- Documents needing fine-grained typesetting control
- Pipelines that further process `.tex` (BibTeX, custom preamble, journal classes)

## What's Here

`md-to-latex.cjs` — Node script that wraps Pandoc and emits standalone `.tex`.

## External Dependencies

- `node` (≥ 16)
- `pandoc` (≥ 3.0) on PATH
- TeX distribution (TeX Live, MiKTeX) only if you compile the output

## Usage

```bash
node md-to-latex.cjs paper.md
node md-to-latex.cjs paper.md --output paper.tex
node md-to-latex.cjs paper.md --bibliography refs.bib --csl ieee.csl
node md-to-latex.cjs paper.md --template custom-template.tex
```

## Frontmatter Hooks

```yaml
---
title: Paper Title
author: Your Name
documentclass: article
classoption: 11pt
bibliography: refs.bib
csl: ieee.csl
---
```

## Notes

- Output is standalone — compiles directly with `pdflatex`/`lualatex`
- Citations in Pandoc syntax (`[@key]`) become `\cite{key}`
- For journal-specific formatting, supply `--template`
