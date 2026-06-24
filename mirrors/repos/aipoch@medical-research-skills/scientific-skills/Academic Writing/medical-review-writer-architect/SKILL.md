---
name: medical-review-writer-architect
description: A multi-stage workflow for writing long-form medical reviews; used when the user needs to build an outline based on PubMed literature, write chapter by chapter, perform supplementary searches, and format citations; input is the review topic and project directory, output is a c...
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)


# Medical Review Writer (Architect)

## When to Use

- The user explicitly wants to write a medical review, narrative review, or long-form review based on PubMed evidence.
- The user accepts a multi-stage process of outline, search, chapter-by-chapter writing, verification, and formatting.
- The user needs real intermediate files, rather than generating the final long document in one shot within the conversation.

## When Not to Use

- When the user only needs a summary, single paragraph review, or brief background introduction, do not launch the full workflow.
- When the user has no topic, target audience, language requirements, or project directory, do not start writing directly — first collect the minimum inputs.
- When the current task does not allow creating or modifying intermediate files, do not use this skill, as its core workflow depends on real files and state machine checks.

## Required Inputs

| Field | Required | Format/Source | Example | If Missing |
|---|---|---|---|---|
| `topic` | Yes | Text | `TP53 in lung cancer` | Stop and ask user to provide |
| `project_dir` | Yes | Local directory | `TP53/` | Confirm working directory first |
| `language` | No | Text | `Chinese` / `English` | Default to Chinese if not provided |
| `target_scope` | No | Text | narrative review / mini review | Execute as standard long review if not provided |

## Output Contract

- Primary output: `Review_Final.md` and `Review_Final_Formatted.md`.
- Intermediate files: `outline.md`, `references.json`, `introduction.md`, `section_*.md`, `abstract.md`, `conclusion.md`.
- Citation format: Body text uses only `[PMID: xxx]` as intermediate citations, with final formatting applied later.
- If the process is interrupted: Must state which stage was completed, what is missing, and mark as `PARTIAL`.

## User Checkpoints

- After the outline is completed, the user must confirm before entering the search and writing stages.
- After each chapter passes verification, report the current chapter status and obtain user confirmation before proceeding to the next chapter.

## Core Workflow

Strictly follow the six-step process below. **Core mechanism**: After each script execution, the terminal prints a [State Machine] prompt — strictly read the current state and follow the "next step suggestion."

### Stage 1: Outline Construction (Outline)

1. Analyze the topic and plan 3-5 major chapters (Body Sections).
2. **Critical mandatory requirement**: The outline **must be detailed down to the sub-heading level** (i.e., `### 1.1`, `### 1.2`, etc.). Each major chapter must have 2-4 pre-planned sub-headings with distinct logical divisions — writing only to the `## 1. Chapter Name` level is never permitted.
3. Create `outline.md`. Must include: Title, Introduction, Body Sections (including all sub-headings), Conclusion.
4. Confirm the outline with the user before proceeding to the next step.

**Detailed instructions**: See [references/workflow-details.md](references/workflow-details.md) Stage 1

### Stage 2: Data Retrieval and Library Construction

1. Design search strategies for each chapter (**must include Introduction**)
2. Execute searches: `python scripts/pubmed_search.py "QUERY" --section "introduction|section_1|..."`
   - **Naming convention**: `--section` must strictly correspond to file names (e.g., use `introduction` NOT `Intro`, use `section_1` NOT `Section1_TP53`) so subsequent scripts can auto-match
   - **Batch retrieval**: The script has batch PMID detail fetching enabled for improved efficiency
   - **Rate limiting**: Automatically controls approximately 1 request/second for stability and API compliance
   - **Default count**: `--max` defaults to 20 articles; adjust as needed
   - **Safety check**: Automatically handles missing PMID or title fields
   - **Important**: `references.json` should be saved in the **project directory** (e.g., `TP53/references.json`), not the skill directory
3. **Check counts**: Run `python scripts/count_references.py`
   - **Target**: Ensure total Unique PMIDs in `references.json` **reach at least 150**
   - If insufficient, optimize search terms and perform additional searches
4. Ensure each chapter has adequate literature support

**Detailed instructions**: See [references/workflow-details.md](references/workflow-details.md) Stage 2

### Stage 3: Chapter-by-Chapter Writing

1. Read chapter references: `python scripts/read_references.py "SectionName"`
2. Create `introduction.md` (Introduction) and `section_1.md`, `section_2.md`, etc. for body sections
3. **Format and word count requirements** (refer to `assets/Review_Final.md`):
   - **Never write an entire Section as a single long paragraph!** Each major chapter (e.g., `## 1. xxx`) **must be divided into 2-4 specific sub-headings** (e.g., `### 1.1 xxx`).
   - Content under each sub-heading must be developed into detailed, coherent academic paragraphs — using simple bullet-point shorthand is not permitted.
4. **Literature citation marking**: Every objective academic claim needs literature support, using `[PMID: xxx]` format.
5. **Write-as-you-search (Dynamic Retrieval)**: If you find insufficient evidence, immediately perform supplementary searches:
   - `python scripts/pubmed_search.py "Specific Query" --section "CurrentSection"`
6. **Post-writing verification and supplementation**:
   - After completing a chapter, verify: `python scripts/check_section.py "section_1.md"`
   - If the state machine indicates insufficient citations, perform supplementary searches with the `--post-write` parameter as suggested.
   - If the state machine indicates word count below the predetermined requirement (i.e., < 7000 characters), expand the content depth of each sub-heading as needed.
   - If the state machine detects dense citations (i.e., a single sentence containing > 2 references), expand and revise that sentence to discuss multiple references separately — **stacking more than 2 references at the end of one sentence is prohibited**.
   - **Mandatory requirement**: Once verification fully passes (no count/word-count/density warnings), **you must report the current chapter's writing status to the user and ask whether to continue** — proceed to the next chapter only after receiving explicit user approval.
7. **Document revision mechanism**: If revisions are needed to the already-formatted final document, **never directly modify the version with hyperlinks**. First run `python scripts/revert_citations.py Review_Final_Formatted.md -o draft.md` to revert to `[PMID: xxx]` format. **Pay attention to the state machine output regarding reference count** — if it indicates insufficient references (e.g., < 30), also use `pubmed_search.py` with the `--post-write` parameter to supplement with new literature during revision, then re-run the formatting script.
8. Format reference: The body section portions of `assets/Review_Final.md`

**Detailed instructions**:

- Workflow: [references/workflow-details.md](references/workflow-details.md) Stage 3

- Citation standards: [references/citation-guide.md](references/citation-guide.md)

### Stage 4: Conclusion Writing

1. Review all `section_*.md` files  
2. Create `conclusion.md`: Summarize core findings, echo the introduction, look ahead to the future (**do not include citations**)
3. Format reference: The conclusion section of `assets/Review_Final.md`

**Detailed instructions**: See [references/workflow-details.md](references/workflow-details.md) Stage 4

### Stage 5: Abstract and Finalization

1. Create `abstract.md`:
   - **Must include the review title** (refer to `assets/Review_Final.md` format)
   - Include: Background, Content, Findings, Conclusion
   - **Do not include citations**
   - 5-7 keywords, separated by Chinese semicolons (；)
2. Merge and finalize: `python scripts/merge_review.py abstract.md introduction.md section_1.md ... -o Review_Final.md` (**Note**: do not include `outline.md`)
3. Format verification: Compare `Review_Final.md` against `assets/Review_Final.md`

**Detailed instructions**: See [references/workflow-details.md](references/workflow-details.md) Stage 5

### Stage 6: Citation Formatting

1. Run: `python scripts/format_citations.py Review_Final.md -o Review_Final_Formatted.md`
2. Verify: Check citation links and reference list

**Detailed instructions**: See [references/citation-guide.md](references/citation-guide.md)

## Core Principles

- **Intermediate files**: Must create real files; cannot process only in memory
- **Citation standards**: Use only `[PMID: xxx]` format for easy downstream script parsing
- **Language**: Default to Chinese for writing; technical terms may retain English
- **Rigor**: Every claim in the introduction and body sections should be supported by literature from `references.json`
- **Citation scope**: Use citations only in the **Introduction** and **Body Sections** — **Abstract** and **Conclusion** do not use citations
- **Diversity**: A single reference should ideally be cited no more than 2 times (3 at most); aim to cite as many different references as possible

## Resource Files

- **scripts/**: Automation scripts (pubmed_search.py, merge_review.py, format_citations.py, etc.)
- **assets/**: Output templates (Review_Final.md)
- **references/**: Detailed documentation (workflow-details.md, citation-guide.md)

## Failure Handling

- Missing critical input: Explicitly state which fields, files, or identifiers are missing and pause.
- Script, template, or resource execution failure: Report the failing step, likely cause, and recovery suggestions — do not silently degrade.
- Partial completion only: Return the verified portion first, then list remaining blockers and suggested next steps.


## Input Validation

This skill accepts requests that match the documented purpose of `medical-review-writer-architect` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `medical-review-writer-architect` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

## Quick Validation

- Check that key scripts, templates, or reference file paths this skill depends on exist.
- Check that the final output contains the core fields, sections, or files specified for this task.
- Check that results clearly mark assumptions, limitations, and incomplete items.
