---
name: content-extract-docx
plugin: source-document-extraction
description: Run pandoc against a source .docx and produce a normalized-source-document contract (markdown text, media files, heading structure, defect signals, statistics) for downstream document-structure-analysis.
allowed-tools: Bash, Read
examples:
  - "python -c \"from extraction import extract_and_normalize; extract_and_normalize('intake/Manual.docx', 'analysis/Manual')\""
---

# Extract DOCX

## Trigger and Purpose

Use this skill to extract a source `.docx` into a `normalized-source-document`
v1 contract: raw markdown text (via a single `pandoc` pass), the extracted
media file list, a source content hash, and source-level observations
(heading structure, image stats, raw-TOC/defect signals, extended
statistics) that `document-structure-analysis`'s `recommend_from_normalized` consumes
without re-parsing.

This plugin only observes the source; it never interprets strategy
(single/chunked), never proposes topic boundaries, and never writes
structured content.

## Public Interface

```python
from extraction import extract_and_normalize

result = extract_and_normalize(source="intake/Manual.docx", output_dir="analysis/Manual")
```

- `source` — path to the source `.docx` file (must exist).
- `output_dir` — directory to write the transitory `raw/` pandoc output to
  (created if missing).
- Returns a `normalized-source-document` v1 dict, validated against this
  plugin's own bundled schema (see `references/contracts/normalized-source-document.md`,
  symlinked into this skill folder — no repository-root or sibling-plugin
  lookup required).

Raises `FileNotFoundError` if `source` does not exist, and
`dependencies.MissingDependencyError` if `pandoc` is not on PATH.

## Installation

```bash
pip install -e plugins/source-document-extraction
```

No other package needs to be installed first — this plugin has zero
dependency on any other workbench distribution or the repository root.

## Dependencies

Requires `pandoc` on PATH (see repository `DEPENDENCIES.md`).

