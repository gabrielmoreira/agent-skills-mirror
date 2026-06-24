---
name: mindmap-html-generator
description: Generate offline interactive mindmap HTML and convert Markdown, outlines, meeting notes, chapter structures, or JSON trees into markmap-compatible format. Use when organizing long text into mindmaps, converting meeting notes to mindmap pages, generating final HTML via markmap-cli, or adding browsable mindmaps to deliverables.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Mindmap HTML Generation

## Overview

First organize input into a clear tree hierarchy, then call `scripts/generate_mindmap_html.py` to generate offline HTML.
Prioritize reusing existing heading structure; do not modify visual code first — get structure correct, then let the script generate the output.

> Tip: The generated HTML page now includes a top toolbar: Export PNG / Fullscreen. Content generation logic remains identical.

## Workflow

### 1. Determine Input Source

- If the user has already provided Markdown headings or lists, render directly.
- If the user provides meeting notes, long text, or chat logs, first organize into Markdown hierarchy, then render.
- If the user provides a JSON tree, confirm fields are `text` / `children`, then render directly.

### 2. Organize Structure

- Prioritize preserving the user's original heading hierarchy.
- If the original text has no headings, first extract 1 main topic and several level-1 and level-2 branches.
- If the original is plain paragraphs or sentences, the script adaptively splits by blank lines, line breaks, colons, and periods.
- Recommended depth is 2-4 levels to avoid pages becoming hard to read.
- Keep node text as short phrases; do not stuff entire paragraphs into nodes.

## Content Richness Requirements

- The default goal is not just "producing a map" but "complete information, clear hierarchy, usable for review, presentation, or reporting".
- Level-1 branches under root should typically be at least 6; if the topic is information-dense, expand to 8-12.
- Each level-1 branch should preferably have 3-6 level-2 nodes; do not force equal branch lengths for neatness.
- If a level-2 node contains methods, conditions, results, mechanisms, impacts, exceptions, or evidence, continue splitting to level-3 nodes.
- For information-dense paragraphs, prioritize splitting into more nodes rather than compressing into one summary sentence.
- For long texts, papers, and meeting notes, do not just keep section names — also include the actual information points under each section.
- Node text must be concise, but conciseness does not mean deleting details.

## Information Extraction Priority

- Prioritize extracting: background, problem, objective, subject, method, materials, process, key variables, results, mechanism, conclusion, significance, limitations, applications.
- If the source text contains causal, conditional, parallel, or contrasting relationships, split into multiple nodes.
- If the source text contains proper nouns, core mechanisms, metrics, sample sizes, models, drugs, groups, or key conclusions, prioritize preserving them.
- If a level-1 node name is too abstract, add specific child nodes to carry the details.
- If content can be split into "subject / action / result / significance", prefer this structure.

## Paper Input Enhancement Rules

- When processing papers, PDFs, or research abstracts, do not just extract section names — include information points within each section.
- Cover at minimum: research background, research question, experimental design, key results, mechanism chain, conclusions and implications.
- If paper information is sufficient, additionally include: research subject, sample size, model, groups, experimental methods, key molecules or pathways, intervention, efficacy, limitations.
- If PDF auto-extraction is too coarse, generate intermediate Markdown first, then restructure before rendering.

## Prohibited Behaviors

- Do not distribute branches evenly just for neatness.
- Do not just restate headings without adding information beneath them.
- Do not write only one vague summary sentence for each of "Background, Methods, Results, Conclusion".
- Do not omit key numbers, key steps, key mechanisms, or key experimental subjects.
- Do not sacrifice information density for brevity.

### 3. Configure Script

- Edit the `CONFIG` block at the top of `scripts/generate_mindmap_html.py`.
- Common configuration options:
  - `input_path`: Input file path.
  - `output_html_path`: Output HTML path.
  - `output_markdown_path`: Intermediate Markdown path.
  - `page_title`: Page title.
  - `fallback_title`: Fallback title when no root heading exists.
  - `auto_bold_levels`: Heading levels to bold by default, recommend keeping `[1, 2]`.
  - `plain_text_root_max_children`: Maximum level-1 branches when auto-splitting plain text.
  - `plain_text_child_max_children`: Maximum child items per level-1 branch when auto-splitting plain text.

### 4. Run Script

Run:

```bash
python scripts/generate_mindmap_html.py
```

The script will:

1. Read the input file.
2. Parse tree structure.
3. Generate intermediate Markdown.
4. Call `npx markmap-cli` to export offline HTML.
5. Inject fixed layout and color rules.

### 5. Validate Results

- Open the generated HTML, confirm root node, level-1 branch order, and text display are correct.
- Confirm only level-1 and level-2 headings remain bold; level-3 and deeper are not bold.
- Confirm branch counts and child counts follow content variation, not mechanical equal lengths.
- Self-check that level-1 branches sufficiently cover the topic.
- Self-check that key numbers, mechanisms, subjects, and conclusions are not omitted.
- Self-check for multiple level-1 branches with identical structure but empty content.
- If nodes are too long, go back to compress input text, then re-run the script.
- If `npx` or `markmap-cli` is missing, install the Node.js environment first.

## Input Rules

- Supports `.md`, `.txt`, `.json`.
- Markdown: prioritizes ATX headings (`#` to `######`), then indented lists.
- Plain text prioritizes splitting by blank lines, line breaks, colons, periods, and other punctuation into unequal-length branches and children.
- JSON must be a single tree with fields `text` and `children`.
- Output path, page title, and fallback title go in `CONFIG` — do not pile CLI arguments.

## Style Conventions

- The script has a built-in fixed final layout; manual style changes after HTML export are not recommended.
- Only `#` and `##` level headings are bold by default; `###` and below automatically remove bold.
- To adjust bold levels, modify `CONFIG["auto_bold_levels"]`, but bolding level-3+ is not recommended.
- Exported HTML automatically assigns unified color groups per level-1 branch.
- Key parameter: `MARKMAP_INIT_OPTIONS["colorFreezeLevel"] = 2`. This freezes colors at "root + level-1 branch"; setting to `1` makes the entire map nearly monochrome.
- To adjust colors, modify `MARKMAP_THEME` — do not manually edit line colors in exported HTML.

## Resources

### `scripts/generate_mindmap_html.py`

Converts structured text to markmap source Markdown and generates offline HTML.

### `references/input-patterns.md`

Read when deciding how to organize input — contains recommended structure templates and examples.

## Execution Constraints

- All file I/O must explicitly use `encoding="utf-8"`.
- When writing JSON, use `ensure_ascii=False`.
- Prefer modifying script top-level CONFIG; do not hide key parameters in long command lines.
- Generate offline pages by default; avoid online CDN dependencies.

## When to Use

- Use this skill when the user explicitly needs to perform the core task of mindmap-html-generator and has provided the minimum executable input.
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

This skill accepts requests that match the documented purpose of `mindmap-html-generator` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions.

## Quick Validation

- Check that key scripts, templates, or reference file paths this skill depends on exist.
- Check that the final output contains the core fields, sections, or files specified for this task.
- Check that results clearly mark assumptions, limitations, and incomplete items.
