---
type: instruction
lifecycle: stable
inheritance: inheritable
description: "Word to Markdown document conversion"
application: "When converting Word documents to Markdown format"
applyTo: "**/*.docx,**/*docx*"
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Word to Markdown Conversion

Auto-loaded for Word document conversion requests.

Full protocol in `.github/skills/docx-to-md/SKILL.md`.

## Quick Reference

| Option | Usage |
|--------|-------|
| `--add-frontmatter` | Add YAML frontmatter with title/date |
| `--fix-headings` | Normalize heading hierarchy to H1 |
| `--strip-comments` | Remove Word review comments |
| `--extract-images` | Extract to images/ folder (default) |
| `--debug` | Keep raw pandoc output |
