---
name: content-validate-rendered-output
plugin: structured-content-rendering
description: Validates a staged rendered-output directory (Markdown via render-multipage-markdown, or ASPX via render-sharepoint-aspx) against the canonical package it was rendered from, and promotes it atomically on PASS. Detects missing/orphan pages, broken links/media references, path traversal, stale source content, and content not traceable back to its source chunk. Always PASS or FAIL, never WARN.
allowed-tools: Bash, Read
examples:
  - "python -c \"from renderers.validate_rendered import render_and_promote; render_and_promote(package, output_root)\""
  - "python -c \"from renderers.validate_rendered import render_and_promote_aspx; render_and_promote_aspx(package, output_root)\""
---

# Validate Rendered Output

## Trigger and Purpose

Use this skill to validate a staged render (produced by
`render-multipage-markdown` or `render-sharepoint-aspx`) against the
`CanonicalPackage` it was rendered from, and atomically promote it on a
PASS result. Runs against a STAGED rendered-output directory, not an
already-promoted one.

Detections, both formats:

- missing index/page-manifest, missing `pages/` dir;
- missing or orphan pages, page-count mismatch;
- broken local links / media references;
- path traversal or absolute-path references escaping the rendered
  output;
- stale source content (the canonical package was reconverted after
  this render was staged, detected via `render-result.json`'s recorded
  `source_content_sha256`);
- rendered page content not traceable back to its source chunk.

Every issue is `severity="error"` — status is always `PASS` or `FAIL`,
never `WARN` (nothing about a broken render-layer link or a stale
source hash is a reviewable discrepancy the way a canonical-content
heading-drift smell might be).

## Public Interface

```python
from renderers.validate_rendered import (
    validate_rendered_output,       # Markdown: (rendered_dir, package) -> ValidationReport
    validate_aspx_rendered_output,  # ASPX: (rendered_dir, package) -> ValidationReport
    render_and_promote,             # Markdown: full stage -> validate -> promote pipeline
    render_and_promote_aspx,        # ASPX: full stage -> validate -> promote pipeline
)

result, report, promoted, output_dir = render_and_promote(package, output_root)
# or, for the ASPX renderer:
result, report, promoted, output_dir = render_and_promote_aspx(package, output_root)
```

A `FAIL` never promotes: the prior accepted render (if any) under
`output_root / "rendered-output"` is left untouched, and the failed
staging directory is retained for diagnosis.

## Installation

```bash
pip install -e plugins/structured-content-rendering
```

## Dependencies

None beyond the Python standard library for Markdown validation. ASPX
traceability re-derives expected page content via `pandoc` (see
`render-sharepoint-aspx`'s own dependency note) — a pandoc failure
during that recomputation is treated as "cannot verify," not a false
`page_content_not_traceable` finding.

