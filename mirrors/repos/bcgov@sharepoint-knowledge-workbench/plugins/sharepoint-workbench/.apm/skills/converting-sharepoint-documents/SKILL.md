---
name: converting-sharepoint-documents
description: Converts Word (.docx) and text-layer PDF documents into structured, validated Markdown or SharePoint page outputs through extraction, analysis, assembly, templating, rendering, comparison, and single-topic review, with an optional, clearly flagged AI navigation layer (summaries, index) for weakly structured documents. Use when running any stage of the local SharePoint document-conversion pipeline for DOCX or PDF; all operations are offline or read-only.
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

For a text-layer PDF use `extract-pdf` instead (needs PyMuPDF; scanned PDFs need OCR first):

```python
sys.path.insert(0, "scripts/extraction")
from pdf_extraction import extract_pdf_and_normalize
result = extract_pdf_and_normalize("intake/Manual.pdf", "analysis/Manual")
```

Follow the pipeline in order: `extract` (DOCX) or `extract-pdf` (PDF) -> `analyze` ->
human confirmation -> `assemble` -> `template-md` or `template-sp` -> `render-md` or
`render-sp` -> `validate`. PDFs reach `assemble` through `convert.run_extraction`. Use
`compare` for golden-master fidelity and `review` for one-topic editorial review.

`enrich` is optional and off by default: after extraction it scores the document's own
structure and, only with the user's consent, adds AI-generated summaries and an index for
weakly structured documents. Good bookmarks and headings are kept.

## Constraints

- Keep source observation, structural decisions, assembly, rendering, and review
  in their stated modes; do not invent decisions or silently skip gates.
- Require a human-confirmed conversion plan before assembly.
- Validate templates before rendering and validate rendered output before accepting
  or publishing it.
- All operations are local/read-only with zero SharePoint tenant I/O. Never upload
  raw `.aspx` files or publish content from this skill.
- Run from this skill root and use only the bundled `scripts/` and `references/`.
- AI-generated content is never authoritative: ask before generating (it costs credits and shares
  document text with the provider), flag every generated file, and keep it apart from the extraction.

## Modes

| Mode | Purpose | Instructions |
|---|---|---|
| `extract` | Extract DOCX text, tables, images, headings, defects, and statistics. | [mode](references/modes/content-extract-docx.md) |
| `extract-pdf` | Extract a text-layer PDF (PyMuPDF) into the same contract, with heading page numbers. | [mode](references/modes/content-extract-pdf.md) |
| `analyze` | Analyze document structure, heading hierarchy, boundaries, and conversion plan. | [mode](references/modes/content-analyze-document-structure.md) |
| `enrich` | Optional: assess structure quality; AI navigation layer is opt-in and always flagged. | [mode](references/modes/content-enrich-navigation.md), [trust model](references/enrichment-trust-model.md) |
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
pytest plugins/sharepoint-workbench/tests/
```
