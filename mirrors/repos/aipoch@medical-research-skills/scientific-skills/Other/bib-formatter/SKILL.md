---
name: bib-formatter
description: Convert reference lists and in-text citations between RIS, BibTeX, plain text, and CSL-JSON, triggered when you need to unify bibliography/citation styles before journal submission or compare before/after formatting differences.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)


## When to Use

- You have a bibliography in **RIS/BibTeX/plain text/CSL-JSON** and must reformat it to a journal style (e.g., **NEJM**, **The Lancet**, **Nature**) before submission.
- You need to switch **in-text citation formatting** (e.g., generating formatted citations for specific cite keys/IDs).
- You are consolidating references from multiple sources and want a **single consistent output style**.
- You want a **before/after comparison** to verify formatting changes and spot missing metadata.
- You need to validate and repair incomplete entries (missing authors, year, journal, pages, DOI/URL) prior to final export.

## Key Features

- Supports input formats: **RIS**, **BibTeX**, **plain text**, **CSL-JSON**.
- Outputs bibliography entries compatible with **CSL styles** (including NEJM/Lancet/Nature or any custom `.csl`).
- Journal-name driven style selection with **automatic CSL retrieval** (exact match preferred; download first, then search fallback).
- Batch conversion via `scripts/format_bibliography.py`.
- In-text citation generation mode for specified cite keys/IDs.
- Produces a **Markdown Before/After table** (minimum 2 examples) for quick review.
- Detects entries that cannot be reliably parsed and requests missing fields.

## Dependencies

- Python **3.10+**
- Citation Style Language (CSL) style files (`.csl`) for target formatting (e.g., `styles/nature.csl`, `styles/the-lancet.csl`, `styles/new-england-journal-of-medicine.csl`)

## Example Usage

### 1) Auto-retrieve a journal style (recommended)

```bash
python scripts/format_bibliography.py \
  --input refs.bib \
  --input-format bibtex \
  --journal "Nature"
```

### 2) Use a local CSL style file for bibliography formatting

```bash
python scripts/format_bibliography.py \
  --input refs.bib \
  --input-format bibtex \
  --style "styles/nature.csl" \
  --output formatted.txt
```

### 3) RIS input example

```bash
python scripts/format_bibliography.py \
  --input refs.ris \
  --input-format ris \
  --style "styles/the-lancet.csl"
```

### 4) In-text citations mode (format citations for specific IDs)

```bash
python scripts/format_bibliography.py \
  --input refs.json \
  --input-format csljson \
  --style "styles/new-england-journal-of-medicine.csl" \
  --mode citations \
  --cite-keys "ITEM-1,ITEM-2"
```

## Implementation Details

- **Workflow**
  1. Collect input text/files and identify the input format: `ris | bibtex | plain | csljson`.
  2. Choose the target style by either:
     - providing `--journal "<Journal Name>"` (auto-retrieval; exact match prioritized; download first, then search), or
     - providing `--style "<path/to/style.csl>"` (local CSL file).
  3. Run batch conversion using `scripts/format_bibliography.py`.
  4. Validate completeness of critical fields and rerun after fixing missing metadata:
     - author(s), year, title, journal/container title, volume/issue, pages, DOI/URL.
  5. After formatting, append a **Markdown comparison table** with at least **two** Before/After examples.

- **Input parsing and field mapping**
  - Refer to `references/input-formats.md` for parsing rules, field mapping, and format-specific details.

- **Output requirements**
  - All instructions/prompts shown to the user must be **in Chinese**.
  - Clearly state the **target CSL style** and the **source input format**.
  - For entries that cannot be reliably parsed, prompt in Chinese and list the missing fields that must be completed.
  - Always include a **Markdown Before/After comparison table** (≥ 2 examples) at the end.

- **Quality checklist**
  - Output matches the target journal style (NEJM/Lancet/Nature/custom CSL).
  - Required metadata is complete: author, year, journal, volume/issue/pages, DOI/URL.
  - Sorting, punctuation, and capitalization follow the CSL style rules.

## When Not to Use

- Do not proceed when required input files, identifiers, parameters, or context are missing — ask the user to provide them first.
- Do not assume capabilities beyond this skill's declared scope when the user requests external operations or inferences.
- Do not proceed without user confirmation when overwriting existing results, executing high-cost batch operations, or expanding task scope.

## Required Inputs

| Field | Required | Format/Source | Example | If Missing |
|---|---|---|---|---|
| User task description | Yes | Text | Research question, writing goal, analysis objective | Stop and ask user to provide |
| Primary input material | Depends on task | Text, file path, ID, table, or literature | PMID, PDF, CSV, DOCX, keywords, etc. | Specify which material type is missing |
| Output preference | No | Text | Language, format, target journal, template | Use skill default format |

## Output Contract

- Primary output: Structured result or target file aligned with this skill's objective.
- Optional output: Intermediate check notes, issue list, supplementary suggestions, or generated file paths.
- Format requirement: Unless the user specifies otherwise, prefer stable, reviewable Markdown or JSON; if the skill's bundled script requires a fixed format, use that format.
- If partially complete: Must explicitly mark as PARTIAL and state which steps are completed and which remain.

## Failure Handling

- Missing critical input: Explicitly state which fields, files, or identifiers are missing and pause.
- Script, template, or resource execution failure: Report the failing step, likely cause, and recovery suggestions — do not silently degrade.
- Partial completion only: Return the verified portion first, then list remaining blockers and suggested next steps.

## User Checkpoints

- Before executing batch processing, overwriting files, long-running searches, or multi-stage generation, confirm scope and output format with the user.
- Before proceeding when a key judgment is ambiguous, evidence is insufficient, or the workflow is entering the next stage, confirm with the user.


## Input Validation

This skill accepts requests that match the documented purpose of `bib-formatter` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `bib-formatter` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

## Quick Validation

- Check that key scripts, templates, or reference file paths this skill depends on exist.
- Check that the final output contains the core fields, sections, or files specified for this task.
- Check that results clearly mark assumptions, limitations, and incomplete items.
