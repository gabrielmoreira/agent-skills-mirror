---
name: content-compare-rendered-output
plugin: content-rendering
description: Compares a freshly produced rendered-output tree (Markdown or ASPX) against a recorded golden-master baseline for byte-identical fidelity, checking file-set completeness and byte-for-byte content while excluding run-specific files. Use to prove a refactor or re-render reproduces known-good output. A standalone, reusable golden-master comparison primitive.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); import compare_rendered_output as cro; print(cro.compare_rendered_trees('fresh/rendered-output', 'golden/rendered-output').status)\""
---

# Compare Rendered Output

Prove a rendered-output tree is byte-identical to a recorded golden-master baseline.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)

## Constraints

- Format-agnostic: both renderers' output (`index.md` and `pages/*.md`, or `page-manifest.json` and
  `pages/*.html`) is just a directory of files, so no format-specific logic applies.
- `generator-info.json` and `render-result.json` are excluded by default because they carry run-specific
  fields. Override only deliberately with `excluded_filenames=frozenset(...)`.
- Read-only comparison. Standard library only. Run from this skill's root with `scripts/` on `sys.path`.

## Quick start

```python
import sys; sys.path.insert(0, "scripts")
from compare_rendered_output import compare_rendered_trees
report = compare_rendered_trees("fresh/rendered-output", "golden/rendered-output")
# ComparisonReport(status="MATCH"|"MISMATCH", issues=[...])
```

## Workflow

1. Point `compare_rendered_trees` at the fresh tree and the golden tree.
2. Report the status and each issue by kind: `missing_in_b` (in the first tree, absent from the second),
   `extra_in_b` (in the second, absent from the first), or `content_mismatch` (byte difference in a file
   present in both).

## Verification

`status` must be `MATCH` with no issues for byte-identical fidelity. Any `MISMATCH` is a real difference; do
not widen `excluded_filenames` to make it pass.
