---
type: skill
lifecycle: stable
inheritance: inheritable
name: md-to-pptx
description: Convert Markdown to PowerPoint presentations via Pandoc.
tier: standard
applyTo: '**/*pptx*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# md-to-pptx

Convert Markdown to PowerPoint presentations via Pandoc.

## When to Use

- Authoring decks in Markdown, delivering in PowerPoint
- Generating slide decks from existing documentation
- Pipelines that need `.pptx` for corporate templates

## What's Here

`md-to-pptx.cjs` — Node script that wraps Pandoc.

## External Dependencies

- `node` (≥ 16)
- `pandoc` (≥ 3.0) on PATH

## Usage

```bash
node md-to-pptx.cjs deck.md
node md-to-pptx.cjs deck.md --output deck.pptx
node md-to-pptx.cjs deck.md --reference-doc template.pptx
```

## Slide Structure

| Markdown | PowerPoint |
|----------|------------|
| `# Title` | Title slide |
| `## Section` | Content slide |
| Body paragraphs / lists | Slide body |
| `---` (HR) | Slide break (no heading) |

## Frontmatter Hooks

```yaml
---
title: My Deck
author: Your Name
date: 2026-04-28
---
```

## Notes

- Use `--reference-doc` with a corporate `.pptx` to inherit theme, fonts, master slides
- Round-trip with `pptx-to-md` is lossy for complex layouts; lossless for text/image content
