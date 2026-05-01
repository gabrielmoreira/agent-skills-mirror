---
type: instruction
lifecycle: stable
inheritance: inheritable
description: "Markdown to plain text conversion via pandoc"
application: "When converting Markdown to plain text"
applyTo: "**/*md-to-txt*,**/*.txt"
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Markdown to Plain Text — Auto-Loaded Rules

Full skill: [md-to-txt](../skills/md-to-txt/SKILL.md). Muscle: `.github/muscles/md-to-txt.cjs`.

## Quick Reference

| Use case | Command |
|---|---|
| Default 80-col wrap | `node md-to-txt.cjs doc.md` |
| No wrap | `node md-to-txt.cjs doc.md --wrap 0` |
| Strip diagrams | `node md-to-txt.cjs doc.md --strip-mermaid` |
| Keep em-dashes | `node md-to-txt.cjs doc.md --no-replace-em-dashes` |
| Strip decorative `---` | `node md-to-txt.cjs doc.md --strip-decorative-rules` |
