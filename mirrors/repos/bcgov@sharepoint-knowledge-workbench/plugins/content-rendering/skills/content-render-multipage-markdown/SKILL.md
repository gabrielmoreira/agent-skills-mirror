---
name: content-render-multipage-markdown
plugin: content-rendering
description: Renders an accepted structured content package into a multipage Markdown publication output, one page per chunk with a path-aware index, rewritten media and page-relative links, validated and atomically promoted. Use after the package has been built and validated. Does not extract source documents, determine topic boundaries, assemble the package, or publish to SharePoint.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from structured_content_rendering import render; render(package_dir, output_dir)\""
---

# Render Structured Content as Multipage Markdown

Load an already-accepted structured content package and render it to multipage Markdown.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Consume only an accepted package promoted by the `content-assembly` plugin. Never build or validate a
  package here.
- A `FAIL` validation never promotes. The prior accepted render under `output_dir` is left untouched and the
  failed staging directory is kept for diagnosis.
- Out of scope: extracting source documents, topic boundaries, assembling the package, publishing to SharePoint.
- Python standard library only. Run from this skill's root with `scripts/` on `sys.path`.

## Quick start

```python
import sys; sys.path.insert(0, "scripts")
from structured_content_rendering import render
result = render(package_dir, output_dir)
# {"render_result": ..., "validation_report": ..., "promoted": bool, "output_dir": str}
```

## Workflow

1. Confirm `package_dir` is an accepted package and choose an `output_dir`.
2. Call `render(package_dir, output_dir)`. It writes one page per chunk, a hierarchical path-aware index,
   copied and reference-rewritten media, and page-relative internal links.
3. On a PASS validation the render is atomically promoted to `output_dir / "rendered-output"`.
4. Report `promoted`, `output_dir` and the validation report.

## Verification

Check `result["promoted"]` is true and the validation report is PASS. If not, report the failures and the
retained staging directory; do not present the render as accepted.

## References

- [Rendered output profile](references/contracts/rendered-output-profile.md): read when checking the
  rendered-output layout and profile.
