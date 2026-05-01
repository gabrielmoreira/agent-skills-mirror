---
description: "Convert HTML documents to clean Markdown via pandoc"
mode: agent
lastReviewed: 2026-04-30
---

# HTML → Markdown

Skill: [html-to-md](../skills/html-to-md/SKILL.md). Muscle: `.github/muscles/html-to-md.cjs`.

## Steps

1. **Run.** `node .github/muscles/html-to-md.cjs page.html page.md`.
2. **Inline styles** are stripped; semantic structure (headings, lists, tables, links) is preserved.
3. **Scripts and tracking pixels** are dropped.
4. **Images** stay as URL references; pass `--download-images` to fetch them locally.

## Post-conversion

- Run [lint-clean-markdown](../skills/lint-clean-markdown/SKILL.md) over the output.
- Review heading hierarchy: HTML often has multiple `<h1>` tags; Markdown wants exactly one.
