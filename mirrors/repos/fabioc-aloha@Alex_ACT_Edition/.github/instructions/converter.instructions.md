---
type: instruction
lifecycle: stable
inheritance: inheritable
description: "Document conversion routing -- detect format, delegate to the converter SA or run the appropriate muscle directly"
application: "When converting between document formats (md to html/word/eml/txt, docx to md, html to md)"
applyTo: "**/*convert*,**/*docx*,**/*word*,**/*eml*,**/*html-to-md*,**/*md-to-*"
currency: 2026-05-02
lastReviewed: 2026-05-02
---

# Document Conversion

Route conversion requests to the right format skill and muscle. Each format has its own skill (domain logic) and muscle (executable).

## Format Routing

| Request pattern | Skill | Muscle | Command prefix |
| --- | --- | --- | --- |
| Markdown to HTML | `md-to-html` | `md-to-html.cjs` | `node .github/muscles/md-to-html.cjs` |
| Markdown to Word | `md-to-word` | `md-to-word.cjs` | `node .github/muscles/md-to-word.cjs` |
| Markdown to email | `md-to-eml` | `md-to-eml.cjs` | `node .github/muscles/md-to-eml.cjs` |
| Markdown to plain text | `md-to-txt` | `md-to-txt.cjs` | `node .github/muscles/md-to-txt.cjs` |
| Word to Markdown | `docx-to-md` | `docx-to-md.cjs` | `node .github/muscles/docx-to-md.cjs` |
| HTML to Markdown | `html-to-md` | `html-to-md.cjs` | `node .github/muscles/html-to-md.cjs` |

## Workflow

1. Detect the source and target format from the user's request
2. Load the matching format skill for domain-specific options and rules
3. Run the muscle with appropriate flags
4. Run `converter-qa.cjs` on the output to validate quality
5. Report results with any QA findings

## Common Options (all formats)

| Flag | Effect |
| --- | --- |
| `--style <preset>` | Apply a style preset (professional, academic, minimal, dark) |
| `--toc` | Add table of contents |
| `--debug` | Keep intermediate files for troubleshooting |

Format-specific options are documented in each format's skill file.
