---
name: reference-retrieval-skill
description: Based on user input, directly find relevant literature or automatically construct PubMed Boolean search queries to retrieve and filter references suitable for citation. Applicable for quickly finding high-quality evidence on specific topics and completing reference lists.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)


# Reference Retrieval Skill

## Core Function

This skill helps users quickly retrieve and filter high-quality, highly relevant references from PubMed based on natural language descriptions.



## Workflow

### Step 1: Construct Boolean Query

1.  **Analyze intent**: Understand user semantics, extract core medical keywords (MeSH Terms preferred).
2.  **Construct Boolean query**:
    - **Logical operators**: Use `AND` (intersection), `OR` (union), `NOT` (exclusion).
    - **Truncation**: Use `*` to match variants (e.g., `diagno*` matches diagnosis, diagnostic).
    - **Example**: For "metformin treatment of type 2 diabetes", construct: `Metformin AND "Diabetes Mellitus, Type 2" AND (Therapy OR Treatment)`.

> [!TIP]
> **About Escaping**:
> If the query contains double quotes `"` (e.g., phrase search), you **must** wrap the entire query in **single quotes** or escape internal double quotes with `\"` to avoid command-line parsing errors.
> - Correct: `python scripts/pubmed_search.py 'Metformin AND "Type 2 Diabetes"'`
> - Correct: `python scripts/pubmed_search.py "Metformin AND \"Type 2 Diabetes\""`

### Step 2: Execute Search

**Prefer LitSense for semantic search**; only use PubMed Boolean search when precise control or complex Boolean logic is needed.

**Scenario A: Semantic/Natural Language Search (LitSense) [Preferred]**
Suitable for direct natural language queries or finding literature related to complex statements.
```bash
python scripts/litsense_search.py "natural language query"
```

**Scenario B: Basic Boolean Search (PubMed)**
Suitable when a precise Boolean query has been constructed.
```bash
python scripts/pubmed_search.py "YOUR_BOOLEAN_QUERY"
```

- `--max`: Returns **20** articles by default; specify `--max 50` for more.

### Step 3: Evaluation & Iteration

If initial results are inadequate (too few, low relevance, or empty), **must** automatically iterate, up to **5 rounds**.

1.  **Analyze cause**:
    - Zero results: Keywords may be misspelled or too specific.
    - Irrelevant results: Keywords are ambiguous or Boolean logic is incorrect.
2.  **Refine query**:
    - **Broaden scope**: Remove non-essential `AND` conditions, add `OR` synonyms.
    - **Narrow scope**: Add qualifiers (e.g., `diagnosis`, `therapy`), or use field tags `[ti]`.
    - **Switch API**: If LitSense search fails or lacks precision, try constructing a precise Boolean query for PubMed.
3.  **Iterate**:
    - Repeat the cycle: modify query, run script, evaluate results.
    - **Limit**: Maximum 5 retries. If still no satisfactory results after 5 attempts, report tried strategies and request more information from the user.

### Step 4: Filter & Present

After the script returns JSON results, filter **3-5** best references based on these criteria:

1.  **Selection criteria**:
    - **Relevance**: Title/abstract must directly address the user's question.
    - **Article type**: Prefer **Review**, **Systematic Review**, **Meta-Analysis**. Then high-quality **RCT** or **Original Article**. **Never** cite Letters, Editorials, or Comments.
    - **Recency**: Prefer literature from the past **5-10 years** (exceptions for classic foundational works).
    - **Open Access (OA)**: If looking for OA/free literature, check for `is_oa: true` or `pmcid` field in results, indicating free full text via PMC.

2.  **Output format**:
    Present results strictly in the following structure:

    **I. Citation Marking**
    Add citation markers at key points in the response content (or in user-provided text).
    - Format example: `...effectively improved prognosis [1].` or `...treatment efficacy [1].`
    - Language should match the user's query language.

    **II. References**
    List references in citation order, **format as follows**:

    ```markdown
    [1] PMID: 34479503 | Title. Journal. https://pubmed.ncbi.nlm.nih.gov/34479503/
    
    Citation rationale: Briefly explain why this reference supports the stated point.

    [2] ...
    ```

    **PubMed link generation rules**:
    - Always provide direct link: `https://pubmed.ncbi.nlm.nih.gov/{pmid}`
    - For example, PMID `34479503` becomes: `https://pubmed.ncbi.nlm.nih.gov/34479503`

    > [!NOTE]
    > Example:
    > [1] The augment of regulatory T cells undermines the efficacy of anti-PD-L1 treatment in cervical cancer. BMC Immunol. https://pubmed.ncbi.nlm.nih.gov/34479503/

## Important Notes

- **Accuracy**: A query that is too broad yields irrelevant results; too narrow may yield nothing. If results are few, try reducing search terms.
- **Language consistency**: **Never auto-translate**. Summary language must match the user's query language.
- **Search language**: Always translate non-English keywords to accurate English medical terms for searching (searches must use English), but present final results matching the user's language.

## When to Use

- Use this skill when the user explicitly needs to perform the core task of reference-retrieval-skill and has provided the minimum executable input.
- Use this skill when you need a structured deliverable rather than general advice.
- Use this skill when the current task can be completed using this skill's bundled scripts, templates, or reference materials.

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

This skill accepts requests that match the documented purpose of `reference-retrieval-skill` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `reference-retrieval-skill` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

## Quick Validation

- Check that key scripts, templates, or reference file paths this skill depends on exist.
- Check that the final output contains the core fields, sections, or files specified for this task.
- Check that results clearly mark assumptions, limitations, and incomplete items.
