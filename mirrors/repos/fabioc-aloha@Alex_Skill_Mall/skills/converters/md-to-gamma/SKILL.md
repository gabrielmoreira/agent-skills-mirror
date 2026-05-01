---
type: skill
lifecycle: stable
inheritance: inheritable
name: md-to-gamma
description: Pre-process Markdown into a Gamma-import-ready version.
tier: standard
applyTo: '**/*gamma*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# md-to-gamma

Pre-process Markdown into a Gamma-import-ready version.

## When to Use

- Authoring presentations in Markdown then importing to [Gamma](https://gamma.app)
- Converting blog posts or docs into slide decks
- Round-tripping content between writing tools and Gamma

## What's Here

`md-to-gamma.cjs` — Node script (no external deps).

## External Dependencies

- `node` (≥ 16) — that's it

## Usage

```bash
node md-to-gamma.cjs input.md
# Emits input-gamma.md alongside the source
```

## What It Does

- Adjusts heading levels for Gamma's slide-per-heading model
- Strips frontmatter that Gamma doesn't read
- Converts Mermaid blocks to references Gamma can render
- Inserts slide-break markers where Gamma expects them

## Workflow

1. Author your deck as standard Markdown
2. Run `md-to-gamma.cjs your-deck.md`
3. In Gamma, **Import → Markdown** → upload `your-deck-gamma.md`
4. Edit visually in Gamma if you want, or re-run the converter on edits

## Notes

- Works offline — no API key, no network
- Companion to the `gamma-presentation` skill if you want full presentation tooling
