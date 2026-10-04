---
name: content-validate-rendered-output
plugin: sharepoint-document-conversion
description: Validates a staged rendered-output directory (Markdown or ASPX) against the canonical package it was rendered from, and promotes it atomically on PASS. Use after rendering and before accepting or publishing a render. Detects missing or orphan pages, broken links and media references, path traversal, stale source content, and content not traceable to its source chunk. Always PASS or FAIL, never WARN.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from renderers.validate_rendered import render_and_promote; render_and_promote(package, output_root)\""
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from renderers.validate_rendered import render_and_promote_aspx; render_and_promote_aspx(package, output_root)\""
---

# Validate Rendered Output

Validate a STAGED render against its `CanonicalPackage` and promote it only on PASS.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Run against a staged rendered-output directory, not an already-promoted one.
- Status is always `PASS` or `FAIL`, never `WARN`; every issue is an error.
- A `FAIL` never promotes. The prior accepted render under `output_root / "rendered-output"` is left
  untouched and the failed staging directory is kept for diagnosis.
- A pandoc failure while re-deriving ASPX page content means "cannot verify", not a
  `page_content_not_traceable` finding.
- Run from this skill's root with `scripts/` on `sys.path`.

## Quick start

```python
import sys; sys.path.insert(0, "scripts")
from renderers.validate_rendered import render_and_promote, render_and_promote_aspx
result, report, promoted, output_dir = render_and_promote(package, output_root)  # Markdown
# or: render_and_promote_aspx(package, output_root)                                # ASPX
```

## Workflow

1. Load the `CanonicalPackage` the render came from.
2. Run `render_and_promote` (Markdown) or `render_and_promote_aspx` (ASPX): stage, validate, promote.
   Use `validate_rendered_output` or `validate_aspx_rendered_output` to validate only.
3. Report `promoted`, `output_dir` and every issue in the report.

## Verification

Confirm the report is PASS and `promoted` is true. On FAIL, list each issue (missing or orphan page, broken
link, path traversal, stale `source_content_sha256`, untraceable content) and the retained staging directory.

## References

- [Validation details](references/validate-rendered-output-details.md): read for the full detection list,
  interface and the pandoc dependency note.
- [Rendered output profile](references/contracts/rendered-output-profile.md): read when checking the
  profile contract.
