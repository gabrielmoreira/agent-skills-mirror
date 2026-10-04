---
name: content-extract-docx
plugin: sharepoint-document-conversion
description: Runs pandoc against a source .docx and produces a normalized-source-document contract (markdown text, media files, heading structure, defect signals, statistics) for downstream structure analysis. Use as the first step when converting a Word document into structured content. Observes the source only; never interprets strategy or writes structured content.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from extraction import extract_and_normalize; extract_and_normalize('intake/Manual.docx', 'analysis/Manual')\""
---

# Extract DOCX

Extract a source `.docx` into a `normalized-source-document` v1 contract that the structure-analysis
step consumes without re-parsing.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Observe only. Never choose a strategy (single or chunked), propose topic boundaries, or write
  structured content.
- `pandoc` must be on `PATH`; otherwise `dependencies.MissingDependencyError` is raised. A missing
  `source` raises `FileNotFoundError`.
- Run from this skill's root with `scripts/` on `sys.path`. No other workbench package is required.

## Quick start

```python
import sys; sys.path.insert(0, "scripts")
from extraction import extract_and_normalize
result = extract_and_normalize(source="intake/Manual.docx", output_dir="analysis/Manual")
```

## Workflow

1. Confirm the `.docx` exists and choose an `output_dir` for the transitory `raw/` pandoc output.
2. Call `extract_and_normalize(source, output_dir)`.
3. Report the returned `normalized-source-document` v1 dict: markdown text, media file list, content
   hash, heading structure, defect signals and statistics.
4. Hand the result to the `sharepoint-document-conversion` plugin; do not interpret it here.

## Verification

Confirm the call returned a dict validated against the bundled schema and that `output_dir/raw/`
holds the pandoc output. Report any raw-TOC or defect signals as observed, not as decisions.

## References

- [Interface](references/extraction-interface.md): read for arguments, return value, errors and scope.
- [Normalized source document contract](references/contracts/normalized-source-document.md): read
  when checking the output shape.
