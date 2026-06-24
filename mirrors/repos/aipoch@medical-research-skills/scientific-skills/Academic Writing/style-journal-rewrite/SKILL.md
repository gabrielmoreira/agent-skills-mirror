---
name: style-journal-rewrite
description: Rewrite drafts according to target writing style or target journal format. Triggers when user says "rewrite in XX style", "match this tone", "format for XX journal", "rewrite following this format". Input can be .docx / .md / .txt or conversation text.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)


# Style and Journal Format Adaptation Skill

## Trigger Conditions

### Triggers
- Style change: "rewrite in XX style", "write like XX", "match this tone"
- Journal format: "format for XX journal", "rewrite following this format", "convert to NC format"
- Adjust reference style or abstract structure

### Does Not Trigger
- Factual additions, content expansion
- Proofreading typos
- Complete structural rewrite (unrelated to style/format)
- Adding references only (use `find-paper-references`)

## Requirements

- `python-docx`: `pip install python-docx` (required for B4/C4 visual formatting, B1/B2 scripts)

## Process

### 0. Define Boundaries

Determine three things:
- **Input format**: DOCX / MD / TXT / conversation text?
- **Task type**: Style only / format only / both?
- **Output format**: Same as input or specific format requested?

Then branch into the corresponding path below.

### 1. Extract Target Profile

Read extraction guides from `references/`:
- Style adaptation → `references/style-profile-extraction.md`
- Journal format adaptation → `references/journal-format-extraction.md`

**Do not fabricate** rules not found in the user's materials.

---

## Path A: Pure Style Adaptation (any input format)

Read `references/rewriting-criteria.md` directly, rewrite according to profile. Change only expression style, not formatting.

Output matches input format. DOCX: change text only, not styles; MD/TXT: output same format; conversation text: output directly.

**After completion, skip to Section 5 QC.**

---

## Path B: DOCX + Format Adaptation

Input is `.docx`, requires journal format changes (may also include style changes).

### B1. Structure Layer
- Heading numbering:
  - Reference article has no numbering → run `scripts/remove_heading_numbers.py <input> <output>`
  - Reference article has numbering but different format → manually edit heading text
- Abstract structure, section order: AI modifies directly

### B2. Citation Layer
- End-of-text list numbering: use `convert_ref_format.py --ref-list-style` to switch between `[N]` / `N.`
- In-text citations: use `convert_ref_format.py --style` to switch superscript (Unicode / font format)
- `--range-joiner` and `--group-separator` **must be extracted from the reference article's actual writing style**, do not assume
- How the reference article combines consecutive citations: observe multi-citation sequences in text, then set parameters

### B3. Field Code Detection
Scan `w:instrText` in DOCX XML:
- Contains `ADDIN ZOTERO_ITEM` → load `format-references-zotero` skill, search CSL style → install → Refresh
- Contains `{Author, Year, Title}` → load `format-references-endnote` skill, check `.ris` in same directory → deliver
- Plain text citations (no field codes) → skip this step, B2 already handled

### B4. Visual Formatting
`python-docx` adjusts font, size, line spacing, paragraph spacing, indentation, alignment per paragraph. Use `para.runs` to set `font.name` / `font.size`, use `para.paragraph_format` for spacing.

**/!\** Do NOT use `para._element.clear()` to clear paragraphs containing field codes — this destroys Zotero/EndNote field codes. B4 only modifies `w:rPr` and `w:pPr`.

---

## Path C: MD + Format Adaptation

Input is `.md`, requires journal format changes (may also include style changes).

### C1. Check PMID Markers
MD must contain `[PMID:xxxxxxxx]` markers to use this path.

- Has markers → continue
- No markers → **prompt user**: run `find-paper-references` first to insert PMID markers, then return to this skill

### C2. Style and Structure Adjustment
AI directly modifies MD text:
- Remove heading numbers, adjust abstract structure, adjust section order
- Change writing style (if needed)

**/!\ Critical constraint**: When moving or rewriting sentences with citations, `[PMID:xxxxxxxx]` markers must follow the text — do not lose, change numbers, or modify spaces.

### C3. Hand Off to Citation Formatting Skill
Load the corresponding skill based on user's tool:
- Zotero → `Skill("format-references-zotero")`
- EndNote → `Skill("format-references-endnote")`

Both skills do: parse `[PMID:xxxxx]` → fetch PubMed metadata → download target journal CSL style → output DOCX (in-text citations and bibliography formatted per journal style).

**This step replaces all work done by `convert_ref_format.py` in Path B**, with more professional results — citation formatting is driven by Zotero/EndNote engines, avoiding inconsistencies from manual Unicode superscript assembly.

### C4. Visual Formatting
`python-docx` applies journal-required font, size, line spacing, margins, and figure/table caption positioning on the DOCX produced by C3.

Same as B4: only modify `w:rPr` and `w:pPr`, do not affect Zotero/EndNote field codes.

### C5. Output
Final DOCX = C2 (structure+style) → C3 (citation formatting) → C4 (visual formatting)

---

## 4. Output and Delivery

- DOCX → `doc.save()` → `deliver_attachments`
- MD → `Write()` → `deliver_attachments`
- TXT → `Write()` → `deliver_attachments`
- Conversation text → output directly to conversation
- After delivery, summarize changes in one sentence

---

## 5. Quality Check

Verify each item:

- [ ] Original key information fully preserved, no example content mixed in
- [ ] If style target: consistent tone throughout, not just first few paragraphs
- [ ] If journal format target:
  - [ ] Heading numbering matches reference article
  - [ ] Abstract structure matches reference article
  - [ ] (DOCX path) Field codes detected, corresponding citation skill executed
  - [ ] (MD path) PMID markers intact, citation skill executed
  - [ ] Visual formatting (font/size/line spacing) applied
- [ ] No fabricated "journal rules" unsupported by user materials
- [ ] File opens normally, no formatting issues (MD path: final DOCX opens with working Refresh/Update Citations)

## Error Handling

- If required inputs are missing, state exactly which fields are missing and request only the minimum additional information.
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If execution fails, report the failure point, summarize what can still be completed safely, and provide a manual fallback.
- Do not fabricate files, citations, data, search results, or execution outcomes.

## Input Validation

This skill accepts requests that match the documented purpose of `style-journal-rewrite` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `style-journal-rewrite` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.
