---
description: "Convert a Markdown document to a polished Word (.docx) file with professional layout, Mermaid PNGs, and APA-margin sizing"
mode: agent
lastReviewed: 2026-04-30
---

# Markdown → Word

Professional Word output. Skill: [md-to-word](../skills/md-to-word/SKILL.md). Muscle: `.github/muscles/md-to-word.cjs`.

## Steps

1. **Confirm source and target.** Source `.md` path, output `.docx` path. If output omitted, default to source basename with `.docx`.
2. **Choose style preset.**
   - `professional` (default) — corporate reports, exec summaries, status updates
   - `academic` — thesis, papers, literature reviews
   - `course` — instructional material with exercises
   - `creative` — opinion pieces, narratives
3. **Optional flags.**
   - `--toc` or insert `[toc]` marker line in the source — Table of Contents
   - `--cover` — title page from frontmatter
   - `--page-size letter|a4|6x9`
   - `--no-replace-em-dashes` — keep `—` in prose (default: replaced with `, `)
   - `--no-strip-decorative-rules` — keep decorative `---` thematic breaks (default: stripped)
4. **Run.** Example: `node .github/muscles/md-to-word.cjs docs/spec.md --style professional --toc`.
5. **Verify.** Open the `.docx`. Tables should be Microsoft-branded with smaller font and tight line spacing; Mermaid diagrams centered, max 90% width / 60% height; em-dash AI-tells removed; decorative `---` gone.
6. **Polish.** Word's File → Save As → PDF if a PDF is needed.

## Related

- [lint-clean-markdown](../skills/lint-clean-markdown/SKILL.md) — pre-flight the source so the converter has clean input
- [markdown-sanitization-chain](../skills/markdown-sanitization-chain/SKILL.md) — when the source contains user-provided content
- [markdown-mermaid (Mode Fragility section)](../skills/markdown-mermaid (Mode Fragility section)/SKILL.md) — diagram-mode pitfalls
