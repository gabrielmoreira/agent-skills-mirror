---
name: content-analyze-document-structure
plugin: document-structure-analysis
description: Analyzes normalized extracted document content to identify heading hierarchy, topic boundaries, cross-references, structural deficiencies, and a proposed conversion plan for human review. Use after source-document extraction. Does not parse DOCX files, assemble the structured content package, render outputs, or publish to SharePoint.
allowed-tools: Bash, Read
examples:
  - "python -c \"from document_structure_analysis import recommend_from_normalized; recommend_from_normalized(normalized)\""
---

# Analyze Document Structure

## Trigger and Purpose

Use this skill to reason about a `normalized-source-document` v1 dict
(produced by `source-document-extraction`'s `extract_and_normalize`) and
produce an `analysis-plan` v1 dict: a chunking-strategy recommendation,
topic-boundary preview, structural anchors (stable chunk identity), and a
draft `ConversionPlan` (`confirmation.status == "draft"`).

This plugin never re-parses headings or re-detects defect signals — those
are `source-document-extraction`'s job and already present on the input
dict. It reasons *about* those observations only.

## Public Interface

```python
from document_structure_analysis import recommend_from_normalized

analysis_plan = recommend_from_normalized(normalized_source_document)
```

- `normalized_source_document` — a `normalized-source-document` v1 dict.
- Returns an `analysis-plan` v1 dict, validated against this plugin's own
  bundled schema (see `references/contracts/analysis-plan.md`, symlinked
  into this skill folder — no repository-root or sibling-plugin lookup
  required).

Never writes to disk and never mutates its input.

## Installation

```bash
pip install -e plugins/document-structure-analysis
```

No other package needs to be installed first — this plugin has zero
dependency on any other workbench distribution or the repository root.

## Dependencies

None beyond the Python standard library.

