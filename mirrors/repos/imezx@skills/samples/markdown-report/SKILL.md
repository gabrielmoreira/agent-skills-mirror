# markdown-report

Use this skill for any long-form structured writing: reports, documentation, articles, summaries, and writeups.

---

## Structure Rules

Every report must follow this skeleton - adapt section names to the topic but never skip the hierarchy:

```
# Title

> One-sentence summary of the entire document.

## Background / Context
Why this exists, what problem it addresses.

## Findings / Body
The main content. Use H3 for sub-sections. Use tables for comparisons. Use bullet lists only for truly enumerable items - never as a substitute for prose.

## Conclusion
What it means. What should happen next.

## References (if applicable)
```

---

## Writing Rules

- Lead every section with a topic sentence that could stand alone.
- One idea per paragraph. Max four sentences per paragraph.
- Never write "In conclusion" or "In summary" - the section heading already signals that.
- Avoid passive voice. Prefer "the team decided" over "it was decided".
- Numbers under ten are written as words. Ten and above use numerals.
- Spell out acronyms on first use: "Large Language Model (LLM)".

---

## Formatting Rules

- Use `**bold**` only for genuinely critical terms - maximum three per page.
- Use `_italic_` for titles of works, technical terms on first introduction, and emphasis.
- Use tables when comparing three or more things across the same attributes.
- Code blocks for all code, commands, file paths, and config snippets - even single-line.
- Never use H1 (`#`) more than once (the document title). Body sections start at H2.

---

## Length Calibration

| Request type | Target length |
|---|---|
| Quick summary | 150-300 words |
| Standard report | 400-800 words |
| Deep-dive / technical doc | 800-2000 words |
| Executive brief | 200-400 words, bullets acceptable |

When in doubt, write shorter. A tight 400-word report is better than a padded 800-word one.

---

## Checklist Before Outputting

- [ ] Title is specific, not generic ("Q1 API Performance Analysis" not "Report")
- [ ] First sentence of document summarises the whole thing
- [ ] No orphan H2 sections with only one sentence of content
- [ ] Tables have aligned columns and a header row
- [ ] No two consecutive bullet lists without prose between them
- [ ] Conclusion contains a concrete next step or recommendation
