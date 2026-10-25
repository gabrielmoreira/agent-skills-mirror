---
name: converting-sharepoint-documents
description: Converts Word documents into structured, validated Markdown or SharePoint page outputs through extraction, analysis, assembly, templating, rendering, comparison, and single-topic review. Use when running any stage of the local SharePoint document-conversion pipeline; all operations are offline or read-only.
---

# Converting SharePoint Documents

Use this domain hub for the complete document-conversion pipeline. Start with the
mode instructions in `references/modes/`; each mode preserves the former
micro-skill's flags, examples, prompts, constraints, and verification contract.

## Quick start

Run from this skill's root with `scripts/` on `sys.path`:

```python
import sys
sys.path.insert(0, "scripts")
from extraction import extract_and_normalize
result = extract_and_normalize("intake/Manual.docx", "analysis/Manual")
```

Follow the pipeline in order: `extract` -> `analyze` -> human confirmation ->
`assemble` -> `template-md` or `template-sp` -> `render-md` or `render-sp` ->
`validate`. Use `compare` for golden-master fidelity and `review` for one-topic
editorial review.

## Constraints

- Keep source observation, structural decisions, assembly, rendering, and review
  in their stated modes; do not invent decisions or silently skip gates.
- Require a human-confirmed conversion plan before assembly.
- Validate templates before rendering and validate rendered output before accepting
  or publishing it.
- All operations are local/read-only with zero SharePoint tenant I/O. Never upload
  raw `.aspx` files or publish content from this skill.
- Run from this skill root and use only the bundled `scripts/` and `references/`.

## Modes

| Mode | Purpose | Instructions |
|---|---|---|
| `extract` | Extract DOCX text, tables, images, headings, defects, and statistics. | [mode](references/modes/content-extract-docx.md) |
| `analyze` | Analyze document structure, heading hierarchy, boundaries, and conversion plan. | [mode](references/modes/content-analyze-document-structure.md) |
| `assemble` | Assemble a confirmed plan into a canonical structured content package. | [mode](references/modes/content-assemble-structured-content.md) |
| `template-md` | Create and validate Markdown rendering templates. | [create](references/modes/content-create-markdown-rendering-template.md), [validate](references/modes/content-validate-rendering-template.md) |
| `template-sp` | Create and validate SharePoint rendering templates. | [create](references/modes/content-create-sharepoint-rendering-template.md), [validate](references/modes/content-validate-rendering-template.md) |
| `render-md` | Render validated packages to multipage Markdown. | [mode](references/modes/content-render-markdown-pages.md) |
| `render-sp` | Render validated packages to modern SharePoint page payloads. | [mode](references/modes/content-render-sharepoint-pages.md) |
| `validate` | Validate templates or rendered output and promote only on PASS. | [template](references/modes/content-validate-rendering-template.md), [output](references/modes/content-validate-rendered-output.md) |
| `compare` | Compare rendered trees against golden-master output. | [mode](references/modes/content-compare-rendered-output.md) |
| `review` | Review exactly one manual topic and limited related evidence. | [mode](references/modes/content-review-manual-topic.md) |

## Verification

Use the mode-specific acceptance criteria under `references/` and run:

```bash
pytest plugins/sharepoint-document-conversion/tests/
```
