---
name: medical-vector-search
description: Vector database retrieval and evidence-based answering for medical research topics. Use when users need knowledge-base-backed answers about methodology, disease mechanisms, drug effects, clinical research, or research tools. Input is a medical research question; output is a st...
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)


# Medical Research Vector Search Skill

## Skill Objective

When users ask medical research questions, intelligently rewrite queries and call the vector knowledge base to retrieve the most relevant document segments, then provide evidence-backed answers. This ensures answers come from a reliable knowledge base rather than solely from model internal knowledge.

## Workflow

### Step 1: Rewrite User Question into High-Quality Search Query

Before calling the API, rewrite the user's original question into a professional query suited for vector retrieval. The purpose is to improve recall, as colloquial questions often fail to match professional expressions in documents.

**Rewriting principles:**

- Extract core medical concepts, use standardized professional terminology
- Remove interrogative tone, convert to declarative keyword combinations
- If the original question is vague, expand to include related concepts
- Keep queries concise, focusing on key concepts (10-30 words typically works best)

**Rewriting examples:**

| User Original Question | Rewritten Search Query |
| --- | --- |
| What is the review workbench? | review workbench features usage methods |
| How to do meta-analysis? | meta-analysis systematic review methodology statistical analysis |
| What are CAR-T cell therapy side effects? | CAR-T cell therapy adverse reactions cytokine release syndrome neurotoxicity |
| I want to learn about CRISPR gene editing | CRISPR-Cas9 gene editing principles applications off-target effects |

### Step 2: Call Vector Database Search API

The skill directory contains a pre-packaged search script `scripts/search.py` - call it directly:

```bash
python scripts/search.py "<rewritten query>"
```

The script automatically outputs relevance scores, source titles, and document content segments.

You can also import its `search()` function directly in Python code:

```python
from scripts.search import search

results = search("<rewritten query>")
```

**API parameters (fixed, no modification needed):**

| Parameter | Value | Description |
| --- | --- |
| `collection_alias` | `wiki_production` | Knowledge base to search |
| `search_method` | `hybrid_search` | Hybrid retrieval (vector + keyword) |
| `alpha` | `0.7` | Vector weight 70% |
| `score_threshold` | `0.1` | Minimum relevance threshold |
| `limit` | `10` | Return max 10 results |

### Step 3: Parse Results and Generate Answer

- Prioritize organizing answers based on high-relevance documents (score > 0.3)
- Use `[1]`, `[2]` citation markers in the text (merge numbers when multiple passages cite the same document)
- List all citations at the end in reference format using Markdown hyperlinks, with `helix_wiki_knowledge_name` as link text and `helix_wiki_node_url` as URL:

```markdown
**References**
[1] [Protein-Protein Interaction Research - Basic Research Elements](https://helixwiki.newidea.pro/xxx)
[2] [Introduction to Research Design - Basic Scientific Research Elements and Logic](https://helixwiki.newidea.pro/yyy)
```

URL comes from the `child_chunks[0].properties.metadata.helix_wiki_node_url` field in each API result.

- If different results share the same URL, merge into a single reference entry
- If relevance is low or results are insufficient, honestly state this and supplement with model knowledge (without citation markers)

## Example Use Cases

- Research platform feature usage (e.g., review workbench, literature management)
- Medical literature search and review methodology
- Clinical trial design and statistical methods
- Drug mechanisms of action and side effects
- Disease diagnosis and treatment guidelines
- Biomedical experimental techniques (PCR, sequencing, flow cytometry, etc.)
- Bioinformatics analysis methods
- Medical writing and submission guidelines

## Important Notes

- Never directly answer complex medical research questions without searching first — search-then-answer is the core value of this skill
- For very basic common knowledge questions (e.g., 'what is DNA'), a brief direct answer is acceptable, but deep questions must always be searched
- If first search results are unsatisfactory, try changing the query angle — e.g., switch to English terminology or split into multiple sub-queries

## When to Use

- Use this skill when the user explicitly needs to perform the core task of medical-vector-search and has provided the minimum executable input.
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

This skill accepts requests that match the documented purpose of `medical-vector-search` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `medical-vector-search` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

## Quick Validation

- Check that key scripts, templates, or reference file paths this skill depends on exist.
- Check that the final output contains the core fields, sections, or files specified for this task.
- Check that results clearly mark assumptions, limitations, and incomplete items.
