---
type: instruction
lifecycle: stable
inheritance: inheritable
description: "HTML to Markdown conversion via pandoc"
application: "When converting HTML documents to Markdown"
applyTo: "**/*html-to-md*,**/*.html"
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# HTML to Markdown — Auto-Loaded Rules

Full skill: [html-to-md](../skills/html-to-md/SKILL.md). Muscle: `.github/muscles/html-to-md.cjs`.

## Quick Reference

| Use case | Command |
|---|---|
| Basic conversion | `node html-to-md.cjs page.html page.md` |
| Download images | `node html-to-md.cjs page.html --download-images` |
| Custom wrap | `node html-to-md.cjs page.html --wrap 100` |
