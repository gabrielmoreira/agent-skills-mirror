---
name: bulletmind
description: "Rewrites any input as a hyphen-only hierarchical bullet tree (lite, full, or ultra) with 2-space nesting and no prose bridges. Use for bullet summaries, cleaned notes, or turning messy lists into a parent-child tree. Never apply this format to stories, essays, tables, JSON, code blocks, or a request that already asked for paragraphs."
version: 1.0.1
category: writing
risk: safe
source: community
date_added: "2026-04-21"
tags:
  - writing
  - summarization
  - note-taking
  - formatting
  - structured-output
tools:
  - claude
  - cursor
  - gemini
  - codex
---

# Bulletmind

When active, every response is delivered as a structured bullet hierarchy—no paragraphs, no prose blocks, no commentary, no drift. Only bullet output.

---

## When to Use

Activate this skill when the user requests any of the following:

- Bullet-only summaries of dense text, notes, explanations, articles, or webpages
- Cleaned-up note-taking output with clear parent-child relationships
- Structured study material that is easier to scan and memorize
- Consistent formatting for messy or mixed bullet lists
- Hierarchical restructuring of existing flat or disorganized bullets
- Conversion of short input into a bullet tree

### When NOT to Use

- User explicitly requests paragraphs or prose
- Creative writing tasks such as stories or essays
- Formats where bullets reduce clarity or violate the requested output format (tables, code blocks, JSON)
- Deliverables that require narrative flow or exact source quotation
- A higher-priority instruction requires a non-bullet format

---

## Prerequisites

- None. This is a pure formatting/transformation skill with no external dependencies, scripts, or API calls.
- If the user wants to see concrete output templates before applying the skill, load `EXAMPLES.md` from the skill directory. Do this only when the user asks for examples or when unsure about expected output shape.

---

## Procedure

### 1. Determine intensity level

Default mode is **full**. If the user specifies a different level, switch accordingly.

| Level  | Behavior                                                                                      |
| ------ | --------------------------------------------------------------------------------------------- |
| lite   | Clean hierarchical bullets, light restructuring, preserve sentence flow                      |
| full   | Default strict hierarchy, balanced compression, clear grouping + splitting                   |
| ultra  | Deep hierarchical decomposition, aggressive splitting, high granularity, maximal clarity     |

If the user issues `/bulletmind lite`, `/bulletmind full`, or `/bulletmind ultra`, honor that selection for the current session.

### 2. Parse the input

- Identify main ideas → these become top-level bullets
- Identify supporting details → these become nested bullets
- Identify messy or mixed existing bullets → normalize depth and grouping
- For short input, still produce a bullet tree (do not refuse or pad with prose)

### 3. Apply transformation logic

- Paragraph → extract main ideas → top-level bullets
- Details → nested bullets under the relevant parent
- Messy notes → cleaned hierarchy with consistent indentation
- Existing bullets → restructure + normalize depth
- Short input → convert into the smallest valid bullet tree

### 4. Apply compression strategy

- Remove filler words
- Split complex sentences into smaller bullets
- Preserve key facts and relationships
- Do NOT flatten structure into a single level
- Prefer clarity over maximum compression

### 5. Format the output

- Use `-` for ALL bullets—no `*`, no `+`, no numbered lists unless the user explicitly requests them
- Indent exactly 2 spaces per nesting level
- Keep each bullet short: one idea per line
- No mixed symbols
- No prose bridging lines between bullets
- No commentary or explanation before/after the bullet block

### 6. Verify structure before returning

- Every bullet is `-` followed by a space
- Indentation increases by exactly 2 spaces per level
- No paragraph blocks exist anywhere in the output
- Meaning is intact—no over-summarization that drops key facts

---

## Bullet Structure Reference

```
- Top-level idea
  - Sub-point
    - Detail
  - Sub-point
- Next top-level idea
  - Sub-point
```

---

## Hard Rules

These rules are non-negotiable while the skill is active:

1. **NO paragraphs** — zero prose blocks anywhere in the output
2. **ONLY bullets** — every line of content is a `-` bullet
3. **ALWAYS hierarchical** — output must be a tree, not a flat list
4. **GROUP related ideas** under parent bullets
5. **SPLIT long sentences** into smaller bullets
6. **KEEP meaning intact** — no over-summarize, no invented structure beyond source
7. **REMOVE filler words** — tighten without losing facts
8. **No commentary** — no introductory or concluding prose
9. **Yield to higher-priority instructions** — if the user or a parent instruction requires tables, code blocks, JSON, or paragraphs, do not force bullet format

---

## Pitfalls

- **Flattening everything into one level** — defeats the purpose; always maintain a logical tree
- **Over-compressing until meaning is lost** — prefer clarity over maximum compression
- **Mixing bullet symbols** (`-`, `*`, `+`) — use `-` exclusively
- **Inconsistent indentation** — use exactly 2 spaces per level, not tabs or 4-space jumps
- **Adding prose bridges** like "Here are the points:" or "In summary:" — omit all commentary
- **Inventing structure beyond the source** — when the user asks for faithful summarization, do not add ideas that are not present in the input
- **Refusing short input** — even a single sentence should be converted into the smallest valid bullet tree
- **Ignoring higher-priority format requests** — if the user needs JSON, a table, or a code block, bullets must yield

---

## Verification

After producing output, mentally (or explicitly when debugging) check:

- [ ] Every content line starts with `- ` (hyphen + space)
- [ ] Indentation increases by exactly 2 spaces per nesting level
- [ ] No paragraph or prose block appears anywhere
- [ ] No commentary before or after the bullet block
- [ ] Key facts and relationships from the source are preserved
- [ ] Structure is a tree (each nested bullet has a logical parent)
- [ ] No mixed bullet symbols

**Quick self-test command (PowerShell, when debugging a generated file):**

```powershell
# Count non-bullet, non-empty lines in a file (should be 0)
Select-String -Path .\output.md -Pattern '^(?!\s*-\s).*\S' |
  Where-Object { $_.Line.Trim() -ne '' }
```

If the command returns any lines, the output violates the bullet-only rule.

---

## Examples

- Refer to `EXAMPLES.md` in the skill directory for concrete input → output templates.
- Load `EXAMPLES.md` when the user asks to see examples or when uncertain about the expected output shape.

---

## Important Notes

- Prefer clarity over strict compression
- Avoid flattening everything into one level
- Maintain a logical tree structure at all times
- Default intensity is **full**; escalate to **ultra** only when the user asks for maximal granularity
- De-escalate to **lite** when the user wants lighter restructuring with sentence flow preserved
