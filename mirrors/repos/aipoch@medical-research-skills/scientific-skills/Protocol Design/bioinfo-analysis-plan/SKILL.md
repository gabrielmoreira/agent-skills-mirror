---
name: bioinfo-analysis-plan
description: Bioinformatics literature analysis workflow extraction and customized plan design. Triggered only when the user explicitly refers to a specific paper: the user requests extracting analysis pipelines from a paper, summarizing technical workflows, reproducing analysis approaches...
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)


# Bioinformatics Analysis Workflow Extraction and Plan Design Skill

## Core Task

The core objectives of this skill are:
1. **Systematically extract** the complete analysis workflow of a bioinformatics paper (at the macro pipeline level)
2. **Design customized** analysis plans for new diseases/phenotypes

## Workflow

### Step 1: Confirm Literature Source

When the user expresses intent to extract an analysis workflow:

- **If a PDF file already exists in the workspace** (check the directory for `.pdf` files via Glob): use it directly, inform the user which file is being used
- **If no file exists**: ask the user to upload/provide the PDF literature file
  - Prompt the user that the file should be placed in the current working directory
  - If necessary, remind the user they can provide it via drag-and-drop or upload

### Step 2: Read and Extract Analysis Workflow

This skill includes a built-in `scripts/extract_pdf.py` Python script for PDF text extraction (depends on the PyMuPDF library, pre-installed in the environment).

**PDF Reading Strategy (two complementary methods):**

**Method A — Direct Read tool (preferred):**
Use the `Read` tool to directly read the PDF file. Some environments support PDF rendering and can directly obtain text content.
- Advantage: No extra steps needed, completed in one action
- Limitation: Chart text may be missing or misaligned (this is normal)
- Focus on the Methods and Results sections

**Method B — Python script full-text extraction (recommended/fallback):**
If Read tool output is insufficient, or more complete text is needed, use Bash to run the extraction script:

```bash
python3 scripts/extract_pdf.py <pdf_path> <output_txt_path>
```

The script extracts text from all PDF pages and saves it as a `.txt` file with page number markers. Then use the Read tool to read the generated txt file.

**Recommended workflow:**
1. First use Method A (Read tool) for a quick overview of the PDF to get the overall structure
2. If key information is incomplete (e.g., methods section is truncated, chart text is missing), use Method B to extract full text
3. Cross-reference the txt file text with the Read tool content to ensure completeness

The extracted analysis workflow should be at the **macro pipeline level**, identifying the **major analysis stages** in the paper, with each stage including:
- **Stage name** (e.g., data preprocessing, differential expression analysis, functional enrichment analysis, prognostic model construction, immune infiltration analysis, etc.)
- **Purpose** (why this step is performed)
- **Methods/tools/databases used** (e.g., limma package, clusterProfiler, LASSO regression, TCGA database, etc.)
- **Key parameters or filtering criteria** (e.g., |log2FC|>1, adj.P<0.05, P<0.05, etc.)
- **Input and output** (what data goes in at each step, what results come out)

Notes during extraction:
- Focus on the **logical relationships** and **sequential order** between analysis methods (which step depends on the output of which)
- Identify whether the paper uses **single-dataset analysis** or **multi-dataset validation**, and their validation strategies
- Distinguish between **primary analyses** and **supplementary analyses** (Supplementary)
- If the paper contains multiple independent analysis tracks (e.g., transcriptomics + single-cell + epigenomics), summarize each separately

### Step 3: Output Analysis Workflow Summary

The output process is: **first generate a Markdown intermediate file, then convert to `.docx` format using `scripts/generate_docx.py` for user delivery**.

#### 3a. Generate Markdown Intermediate File

Write a structured summary document in **Chinese Markdown format**, saved as `analysis_workflow_summary.md` (as an intermediate file).

Document structure as follows (adjust according to actual paper content; it is not necessary to strictly follow this structure, but ensure it is structured):

```markdown
# Literature Analysis Workflow Summary

**Literature Information**: [Title], [Journal/Year] (note if identifiable from the PDF)

## Analysis Pipeline Overview
Use a flowchart or bullet points to briefly describe the overall analysis pipeline, giving readers an at-a-glance understanding.

## Stage 1: [Stage Name]
### Purpose
### Data Source
### Methods/Tools
### Key Parameters/Filtering Criteria
### Main Output Results

## Stage 2: [Stage Name]
...

## Key Validation Strategies
- Internal validation:
- External validation:
- Other validation:

## Reusable Analysis Patterns
Extract generalizable analysis approaches (e.g., "differential screening → LASSO dimensionality reduction → multivariate regression model building → multi-dataset validation" as a universal pattern)
```

#### 3b. Convert to Word Document

Use the built-in script to convert Markdown to a professionally formatted `.docx` file:

```bash
python3 scripts/generate_docx.py analysis_workflow_summary.md .
```

The script generates `analysis_workflow_summary.docx`, including:
- Correct Chinese/English font settings (SimSun/Times New Roman)
- Hierarchical heading formats (SimHei bold, Level 1 18pt centered, Level 2 15pt, Level 3 13pt)
- **Bold**, *italic*, `code` inline format rendering
- Markdown tables rendered as Word tables (headers with blue background)
- Code blocks in monospaced font
- List rendering (ordered/unordered)
- Professional page setup (2.54cm margins)

After outputting the `.docx`, **also display a core content summary in the conversation** (no need to show the full text; provide the pipeline overview and key findings, guiding the user to view the `.docx` file).

### Step 4: Ask Whether a Customized Plan is Needed

After outputting the summary, proactively ask the user:

> Would you like a customized analysis plan designed for another disease or phenotype using this analysis workflow? If so, please provide the disease/phenotype name you are interested in.

### Step 5: Design Customized Analysis Plan

If the user provides a disease/phenotype name:

Based on the workflow extracted in Step 2, design an adapted plan stage by stage for the new disease/phenotype.

Output process: first generate `custom_analysis_plan_[disease_name].md` intermediate file, then convert to `.docx`:

```bash
python3 scripts/generate_docx.py custom_analysis_plan_[disease_name].md .
```

Adaptation principles:
- **Maintain the core logic of each analysis stage**, but select appropriate databases, parameters, and tools for the new disease
- **Data sources**: Recommend relevant public databases for the new disease (TCGA, GEO, ICGC, GTEx, etc.) or specify what data needs to be collected independently
- **Sample size considerations**: Different diseases have varying sample availability; adjust analysis strategies accordingly (e.g., rare diseases may require different modeling approaches)
- **Clinical relevance**: Combine with the clinical characteristics of the new disease to suggest clinically meaningful analysis entry points
- **Feasibility assessment**: Provide actionable recommendations for each stage, noting potential difficulties

Output format similar to Step 3, but with added "Adaptation Notes":

```markdown
# Customized Analysis Plan: [New Disease/Phenotype Name]

## Based on Literature Workflow: [Original Paper Analysis Pipeline Name]

### Stage 1: [Stage Name] → Adapted Plan
- **Original method**:
- **Adaptation recommendations**:
- **Recommended databases/tools**:
- **Notes**:

...
```

### Notes and Principles

1. **Chinese interaction**: Communicate with the user in Chinese throughout; output is also in Chinese Markdown
2. **Macro granularity**: Do not go down to line-by-line code or specific syntax level; stay at the method/tool level
3. **Honest labeling**: If PDF content is insufficient to extract information about certain stages, explicitly note "not clearly stated in the paper" rather than fabricating
4. **No preset templates**: Dynamically construct structure based on actual paper content; do not force-fit a fixed template
5. **File management**: First generate `.md` intermediate file (can be cleaned before output), then use `scripts/generate_docx.py` to convert to `.docx` format. The final deliverable to the user is the `.docx` file. Intermediate `.md` files can be kept or deleted as needed
6. **PDF reading strategy**: Prefer using the Read tool to directly read PDFs; if content is incomplete (e.g., chart text missing, methods section truncated), immediately use `scripts/extract_pdf.py` via Bash to extract full text. The extraction script depends on PyMuPDF, pre-installed in the environment. Be especially careful when extracting information from the Methods and Results sections — these are the essence of the analysis workflow
7. **Multiple files scenario**: If there are multiple PDFs in the workspace, ask the user to specify which paper to analyze
8. **Emphasize universal patterns**: When outputting "Reusable Analysis Patterns", distill transferable strategies that can be applied to other similar studies — this is the most valuable part for the user

## Error Handling

- If required inputs are missing, state exactly which fields are missing and request only the minimum additional information.
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If execution fails, report the failure point, summarize what can still be completed safely, and provide a manual fallback.
- Do not fabricate files, citations, data, search results, or execution outcomes.

## Input Validation

This skill accepts requests that match the documented purpose of `bioinfo_analysis_plan` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `bioinfo_analysis_plan` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.
