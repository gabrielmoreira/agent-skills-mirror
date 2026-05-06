---
mode: agent
description: "Convert a document between formats (md/html/word/eml/txt). Detects source and target format, runs the appropriate muscle, validates with converter-qa."
lastReviewed: 2026-05-05
---

# /convert

Convert a document to another format.

## Steps

1. **Detect formats**: Identify the source file and target format from the user's request. If ambiguous, ask.
2. **Load format skill**: Read the matching skill from `.github/skills/<format>/SKILL.md` for format-specific rules and options.
3. **Run muscle**: Execute the conversion muscle with the user's options:
   ```
   node .github/muscles/<format>.cjs <source> [output] [options]
   ```
4. **Validate**: Run converter-qa on the output:
   ```
   node .github/muscles/converter-qa.cjs <output>
   ```
5. **Report**: Show the output path, file size, and any QA findings.

## Format Detection

| User says | Source | Target | Muscle |
| --- | --- | --- | --- |
| "convert to word" / "make a docx" | .md | .docx | md-to-word.cjs |
| "convert to html" / "make a webpage" | .md | .html | md-to-html.cjs |
| "convert to email" / "make an eml" | .md | .eml | md-to-eml.cjs |
| "convert to plain text" | .md | .txt | md-to-txt.cjs |
| "convert this word doc" / "docx to md" | .docx | .md | docx-to-md.cjs |
| "convert this html" / "html to md" | .html | .md | html-to-md.cjs |

## If the user provides no file

Ask which file to convert. Do not guess.
