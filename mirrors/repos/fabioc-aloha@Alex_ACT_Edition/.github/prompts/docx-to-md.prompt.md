---
description: "Convert Word (.docx) documents to clean Markdown with image extraction"
mode: agent
lastReviewed: 2026-04-30
---

# Word → Markdown

Skill: [docx-to-md](../skills/docx-to-md/SKILL.md). Muscle: `.github/muscles/docx-to-md.cjs`.

## Steps

1. **Run.** `node .github/muscles/docx-to-md.cjs source.docx output.md`.
2. **Images** are extracted to a sidecar `images/` folder and referenced from the Markdown.
3. **Tables** convert to GFM tables when the structure is regular; complex Word tables may need manual cleanup.
4. **Tracked changes** are flattened to the accepted version. Run `Accept All Changes` in Word first if you want to control the merge.

## Post-conversion

- Run [lint-clean-markdown](../skills/lint-clean-markdown/SKILL.md) over the output to fix list spacing and heading hierarchy.
- If the document contained Mermaid diagrams pasted as images, they'll come through as PNGs; rebuild as fenced ` ```mermaid ` blocks if you want them re-renderable.
