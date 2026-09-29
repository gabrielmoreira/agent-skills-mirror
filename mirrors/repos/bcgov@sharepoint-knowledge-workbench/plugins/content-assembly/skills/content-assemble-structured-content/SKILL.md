---
name: content-assemble-structured-content
plugin: structured-content-assembly
description: Uses normalized extracted content and a human-confirmed conversion plan to assemble a validated structured content package with stable identities, source lineage, hashes, manifests, and publication mappings. Does not extract source documents, make unconfirmed topic decisions, render output formats, or publish to SharePoint.
allowed-tools: Bash, Read
examples:
  - "python -c \"from structured_content_assembly import build_canonical_package; build_canonical_package(plan, source_dir, output_dir)\""
---

# Assemble Structured Content

## Trigger and Purpose

Use this skill to convert a *confirmed* `analysis-plan` v1 dict (produced
by `document-structure-analysis`'s `recommend_from_normalized` plus human
confirmation) into a validated structured content package on disk:
pandoc extraction, markdown cleanup, heading-based chunking, media
inventory/copy/rewrite, manifest assembly, validation, and atomic
promotion. For a `strategy: "grouped"` plan, also builds and validates a
`publication-map`.

This plugin never constructs or confirms a plan itself — that is
`document-structure-analysis`'s job. It consumes an already-confirmed
plan dict.

## Public Interface

```python
from structured_content_assembly import build_canonical_package

result = build_canonical_package(analysis_plan, source_dir, output_dir)
# {"manifest": ..., "validation_report": ..., "promoted": bool, "package_dir": str}
```

- `analysis_plan` — a confirmed `analysis-plan` v1 dict
  (`confirmation.status == "confirmed"`).
- `source_dir` — path to the directory containing the source `.docx`
  referenced by the plan.
- `output_dir` — path under which the structured content package is
  staged and (on a PASS validation) atomically promoted.
- Returns a dict with the `Manifest`/`ValidationReport` contents,
  whether promotion happened, and the final package directory. See
  `references/contracts/canonical-package.md` and
  `publication-map.md` (symlinked into this skill folder — no
  repository-root or sibling-plugin lookup required).

A `FAIL` validation never promotes: the prior accepted package (if any)
under `output_dir` is left untouched, and the failed staging directory is
retained for diagnosis.

## Installation

```bash
pip install -e plugins/structured-content-assembly
```

No other package needs to be installed first — this plugin has zero
dependency on any other workbench distribution or the repository root.

## Dependencies

`pandoc` and (for legacy `.emf` media) LibreOffice's `soffice` must be on
`PATH` — see `DEPENDENCIES.md` at the repository root.

