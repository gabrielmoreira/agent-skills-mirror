---
type: skill
lifecycle: stable
inheritance: inheritable
name: pptx-to-md
description: Convert PowerPoint (.pptx) to Markdown via Pandoc.
tier: standard
applyTo: '**/*pptx*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# pptx-to-md

Convert PowerPoint (.pptx) to Markdown via Pandoc.

## When to Use

- Extracting slide content for editing in plain text
- Migrating decks into documentation systems
- Salvaging content from legacy `.pptx` files

## What's Here

`pptx-to-md.cjs` — Node script that wraps Pandoc.

## External Dependencies

- `node` (≥ 16)
- `pandoc` (≥ 3.0) on PATH

## Usage

```bash
node pptx-to-md.cjs deck.pptx
node pptx-to-md.cjs deck.pptx --output deck.md
node pptx-to-md.cjs deck.pptx --extract-media ./media
```

## Output Structure

| PowerPoint | Markdown |
|------------|----------|
| Each slide | `## Slide N` heading |
| Title placeholder | First line under heading |
| Body text / bullets | Paragraphs and lists |
| Speaker notes | Quoted block at slide end |
| Embedded images | Saved to `--extract-media` dir, referenced as `![]()` |

## Notes

- Animations, transitions, and complex layouts are lost — content survives, motion does not
- Pair with `md-to-pptx` for round-trip workflows (lossy for layouts, lossless for content)
- Use `--extract-media` to keep images as separate files instead of inlining
