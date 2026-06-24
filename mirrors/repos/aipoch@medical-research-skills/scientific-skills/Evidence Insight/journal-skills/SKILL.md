---
name: journal-skills
description: Recommends target journals for manuscript submission by analyzing the paper topic/abstract and the journal distribution of similar PubMed literature; use when users ask for journal recommendation/matching, submission strategy, PubMed search, or similar-literature statistics.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)


## When to Use

- You have a manuscript title/abstract and need a shortlist of suitable journals to submit to.
- You want evidence-based journal matching using **similar PubMed literature** and journal distribution statistics.
- You need to compare candidate journals by **scope fit**, **open access requirements**, and **review/publication timelines**.
- You must provide a clear **matching rationale** (why each journal fits) for internal review or co-author alignment.
- You are planning a **submission strategy** (primary target + backups) and want to highlight risks and alternatives.

## Key Features

- Topic- and abstract-driven journal recommendation workflow.
- PubMed-based similar literature search and **journal frequency distribution** compilation.
- Candidate journal screening using scope, policy constraints (e.g., OA), and practical considerations (e.g., review cycle).
- Structured recommendation output with rationale, risks, and backup options.
- Reusable CSV template for consistent reporting.

## Dependencies

- Python 3.9+ (recommended)
- PubMed E-utilities access (NCBI)
  - `EMAIL` required (per NCBI policy)
  - `API_KEY` optional (recommended for higher rate limits)

## Example Usage

### 1) Prepare inputs
Have the manuscript **title** and **abstract** ready.

### 2) Configure the script
Open `scripts/pubmed_journal_recommender.py` and set the `CONFIG` values:

- `EMAIL`: your email (required)
- `API_KEY`: your NCBI API key (optional)
- Output directory (if the script supports/requests it)

### 3) Run the recommender
```bash
python scripts/pubmed_journal_recommender.py
```

When prompted, paste the manuscript title and abstract. The script will query PubMed for similar records and produce journal statistics.

### 4) Produce a structured recommendation table
Use the template below to standardize the final output:

- Template: `assets/journal_recommendation_template.csv`

Fill it with:
- Candidate journals (from the script’s distribution + domain knowledge)
- Matching rationale (scope fit + audience + similarity evidence)
- Constraints (OA, policies)
- Practical notes (review cycle, risks)
- Primary target and backup options

### 5) Follow the checklist and formatting guidance
For recommended output formats, checklists, and key points, see:

- `references/guide.md`

## Implementation Details

### Workflow Overview
1. **Topic and Scope Definition**
   - Identify the research field, subfield, and intended readership.
   - Confirm journal type preferences and constraints (e.g., OA mandates).

2. **Similar Literature Analysis (PubMed)**
   - Use the manuscript title/abstract to retrieve similar PubMed records.
   - Aggregate results by **journal** to compute a distribution (e.g., counts per journal).
   - Prioritize journals that appear frequently among highly relevant records.

3. **Journal Screening**
   - Cross-check each candidate against:
     - Journal scope/aims
     - Policy requirements (OA, data availability, ethics)
     - Review/publication timelines (if available)
   - Remove journals that are out-of-scope or non-compliant.

4. **Recommendation Output**
   - Provide a ranked list with:
     - Fit rationale (topic alignment + similarity evidence)
     - Risks (scope mismatch, policy conflicts, timeline concerns)
     - Alternatives (backup journals)

### Key Parameters / Notes
- **NCBI `EMAIL`**: required to comply with NCBI E-utilities usage policy.
- **NCBI `API_KEY`**: optional but recommended to reduce throttling and improve throughput.
- **Output structuring**: use `assets/journal_recommendation_template.csv` to ensure consistent fields and downstream usability.

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

This skill accepts requests that match the documented purpose of `journal-skills` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `journal-skills` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

## Quick Validation

- Check that key scripts, templates, or reference file paths this skill depends on exist.
- Check that the final output contains the core fields, sections, or files specified for this task.
- Check that results clearly mark assumptions, limitations, and incomplete items.
