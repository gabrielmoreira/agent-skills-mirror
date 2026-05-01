---
description: "Strip Markdown formatting and produce clean plain text via pandoc"
mode: agent
lastReviewed: 2026-04-30
---

# Markdown → Plain Text

Skill: [md-to-txt](../skills/md-to-txt/SKILL.md). Muscle: `.github/muscles/md-to-txt.cjs`.

## Steps

1. **Run.** `node .github/muscles/md-to-txt.cjs doc.md doc.txt`.
2. **Wrap.** Default 80 columns. `--wrap N` to change, `--wrap 0` for no wrap.
3. **Strip flags.** `--strip-frontmatter`, `--strip-mermaid`, `--strip-images`.
4. **Em-dash.** Default ON for txt — em-dash AI-tells look bad in monospace. `--no-replace-em-dashes` to keep.
5. **Decorative rules.** Default OFF for txt — pandoc renders `---` as visible dividers, usually intentional. `--strip-decorative-rules` to remove.

## When to use

- Clipboard export
- Email body fallback
- Accessibility (screen reader friendly)
- Input to text analysis tools
