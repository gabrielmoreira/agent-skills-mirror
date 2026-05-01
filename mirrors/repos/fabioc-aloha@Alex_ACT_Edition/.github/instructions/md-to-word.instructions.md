---
type: instruction
lifecycle: stable
inheritance: inheritable
description: "Markdown to Word document conversion with style presets and professional features"
application: "When converting Markdown to Word documents"
applyTo: "**/*md-to-word*,**/*docx*"
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Markdown to Word — Auto-Loaded Rules

Full documentation, all options, style presets, professional features → see [md-to-word skill](../skills/md-to-word/SKILL.md).

Full protocol in `.github/skills/md-to-word/SKILL.md`.

## Quick Reference

| Use Case | Command |
|----------|---------|
| Basic conversion | `node md-to-word.cjs doc.md` |
| With Table of Contents | `node md-to-word.cjs doc.md --toc` |
| Professional report | `node md-to-word.cjs doc.md --style professional --toc --cover` |
| Academic paper | `node md-to-word.cjs thesis.md --style academic --toc` |
| Debug issues | `node md-to-word.cjs doc.md --debug --keep-temp` |
