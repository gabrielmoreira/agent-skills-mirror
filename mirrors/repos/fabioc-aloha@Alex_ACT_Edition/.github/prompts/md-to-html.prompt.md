---
description: "Convert a Markdown document to standalone HTML with embedded CSS, images, and Mermaid diagrams"
mode: agent
lastReviewed: 2026-04-30
---

# Markdown → HTML

Skill: [md-to-html](../skills/md-to-html/SKILL.md). Muscle: `.github/muscles/md-to-html.cjs`.

## Steps

1. **Run.** `node .github/muscles/md-to-html.cjs doc.md doc.html`.
2. **Style presets.** `--style professional|academic|minimal|dark`.
3. **Table of Contents.** `--toc` flag, or insert `[toc]` marker line in the source.
4. **Em-dash and HR.** Default for HTML: em-dash → comma is ON (AI-tell removal); decorative `---` is OFF (HRs render as visual dividers in HTML and are usually intentional). Override with `--no-replace-em-dashes` or `--strip-decorative-rules`.
5. **Output is one self-contained file** with embedded CSS and base64 images. Open directly in a browser; no external assets required.

## Related

- [lint-clean-markdown](../skills/lint-clean-markdown/SKILL.md)
- [markdown-sanitization-chain](../skills/markdown-sanitization-chain/SKILL.md)
- [markdown-mermaid (Mode Fragility section)](../skills/markdown-mermaid (Mode Fragility section)/SKILL.md)
