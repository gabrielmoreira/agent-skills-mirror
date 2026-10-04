---
name: content-analyze-document-structure
plugin: sharepoint-document-conversion
description: Analyzes normalized extracted document content to identify heading hierarchy, topic boundaries, cross-references, structural deficiencies, and a proposed conversion plan for human review. Use after source-document extraction. Does not parse DOCX files, assemble the structured content package, render outputs, or publish to SharePoint.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from document_structure_analysis import recommend_from_normalized; recommend_from_normalized(normalized)\""
---

# Analyze Document Structure

Turn a `normalized-source-document` v1 dict into a draft `analysis-plan` v1 dict for human review.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Reason about the extraction step's observations only. Never re-parse headings or re-detect defect signals.
- Never write to disk and never mutate the input dict.
- The result is a draft (`confirmation.status == "draft"`). Never confirm a plan; a human does, and only a
  confirmed plan goes to `sharepoint-document-conversion`.
- Out of scope: parsing DOCX files, assembling the package, rendering, publishing to SharePoint.
- Python standard library only. Run from this skill's root with `scripts/` on `sys.path`.

## Quick start

```python
import sys; sys.path.insert(0, "scripts")
from document_structure_analysis import recommend_from_normalized
analysis_plan = recommend_from_normalized(normalized_source_document)
```

## Workflow

1. Get the `normalized-source-document` v1 dict from the `sharepoint-document-conversion` plugin.
2. Call `recommend_from_normalized`.
3. Present the strategy recommendation, topic-boundary preview, structural anchors and draft plan to the user
   for confirmation.

## Verification

Confirm the result is an `analysis-plan` v1 dict with `confirmation.status == "draft"` and that the input dict
is unchanged. Do not treat the plan as final until a human confirms it.

## References

- [Interface](references/analysis-interface.md): read for input and output, guarantees and the next step.
- [Analysis plan contract](references/contracts/analysis-plan.md): read when checking the plan shape.
- [Analyze and confirm diagram](references/diagrams/02-analyze-and-confirm.mmd): read for where this step
  sits in the pipeline.
