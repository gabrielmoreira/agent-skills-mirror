---
name: spreadsheet-ops
description: Spreadsheet processing and analysis for CSV/Excel; trigger when users ask to merge/clean tabular data, run statistics, add/edit Excel formulas, apply formatting, generate charts, or force workbook recalculation.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)


## When to Use

- You need to merge multiple CSV/Excel files into a single dataset and align columns.
- You need to clean tabular data (normalize headers, deduplicate rows, resolve conflicts) before downstream use.
- You need to perform data analysis/statistics on CSV/Excel (summaries, distributions, group-by metrics).
- You need to add or edit formulas in an Excel workbook (including applying formulas across ranges).
- You need to apply Excel formatting (including conditional formatting), generate charts, or force formula recalculation.

## Key Features

- **CSV/Excel merge & cleaning**: combine files, normalize column names, deduplicate, and resolve conflicts.
- **CSV/Excel analysis**: compute descriptive statistics and analysis reports.
- **Excel-only formula operations**: create/edit formulas and apply them to specified ranges.
- **Excel-only formatting**: apply cell styles and conditional formatting rules.
- **Excel-only visualization**: build charts from worksheet ranges.
- **Excel-only recalculation**: set workbook to full recalculation (recalc flag) to ensure formulas update.

## Dependencies

- Python **3.x**
- Project Python dependencies are defined by the repository environment (e.g., `requirements.txt` / lockfile if present).  
  *(No explicit versions were provided in the source document.)*

## Example Usage

> The following commands assume you are in the repository root and have a Python environment available.

### 1) Merge files (CSV/Excel)

```bash
python scripts/merge_files.py
```

### 2) Analyze data (CSV/Excel)

```bash
python scripts/analyze_data.py
```

### 3) Apply formulas (Excel only)

```bash
python scripts/apply_formulas.py
```

### 4) Apply formatting (Excel only)

```bash
python scripts/apply_formatting.py
```

### 5) Build charts (Excel only)

```bash
python scripts/build_charts.py
```

### 6) Force workbook recalculation (Excel only)

```bash
python scripts/recalc_workbook.py
```

## Implementation Details

- **Workflow**
  1. Confirm inputs/outputs: file paths, file formats (CSV vs Excel), worksheet names, and target ranges.
  2. Choose the task type: merge, analysis, formula, formatting, chart, or recalculation.
  3. Run the corresponding script and configure parameters in `CONFIG` (as used by the scripts).
  4. Produce output files and any generated reports.

- **Task boundaries**
  - **CSV/Excel supported**: merging/cleaning, data analysis.
  - **Excel only**: formula creation/editing, formatting, chart visualization, and recalculation.

- **Key parameters to clarify (priority)**
  - Input type: CSV or Excel; single file or multiple files.
  - Worksheet names and cell ranges to operate on (Excel).
  - Whether formulas/formatting/charts must preserve original styles.
  - Desired output format: CSV / Excel / JSON / Parquet.

- **Standards / constraints**
  - Python file I/O must explicitly specify `encoding='utf-8'`.
  - `json.dump(...)` must set `ensure_ascii=False`.

- **Reference documentation (optional)**
  - Column name matching & normalization: `references/column-matching.md`
  - Deduplication & conflict resolution: `references/dedup-conflict.md`
  - Large files & performance: `references/large-files.md`
  - Formula design & ranges: `references/formulas.md`
  - Formatting & conditional formatting: `references/formatting.md`
  - Data analysis & statistics: `references/analysis.md`
  - Charts & visualization: `references/visualization.md`
  - Formula recalculation: `references/recalc.md`

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

This skill accepts requests that match the documented purpose of `spreadsheet-ops` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `spreadsheet-ops` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

## Quick Validation

- Check that key scripts, templates, or reference file paths this skill depends on exist.
- Check that the final output contains the core fields, sections, or files specified for this task.
- Check that results clearly mark assumptions, limitations, and incomplete items.
