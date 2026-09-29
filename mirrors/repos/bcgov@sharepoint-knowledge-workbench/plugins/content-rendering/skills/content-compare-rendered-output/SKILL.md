---
name: content-compare-rendered-output
plugin: structured-content-rendering
description: Compares a freshly-produced rendered-output tree (Markdown or ASPX) against a recorded golden-master baseline for byte-identical fidelity -- file-set completeness (nothing missing, nothing extra) plus byte-for-byte content match, excluding run-specific files (generator-info.json, render-result.json). Packages the golden-master comparison pattern from Phase 2 Subphase 2.5.4 as a standalone, reusable primitive.
allowed-tools: Bash, Read
examples:
  - "python -c \"import compare_rendered_output as cro; print(cro.compare_rendered_trees('fresh/rendered-output', 'golden/rendered-output').status)\""
---

# Compare Rendered Output

## Trigger and Purpose

Use this skill to prove a freshly-produced rendered-output tree is
byte-identical to a recorded golden-master baseline — the same pattern
this repo already used at Phase 2 Subphase 2.5.4 (proving Phase 4.5's
decomposed plugin architecture reproduced the pre-decomposition
combined plugin's output byte-for-byte) and Phase 6 Task 0.16's own
ASPX golden-master proof
(`tests/integration/test_golden_master_aspx.py`), now packaged as a
standalone, reusable comparison primitive rather than a one-off script.

Works against either renderer's output shape (`render-multipage-
markdown`'s `index.md`/`pages/*.md`, or `render-sharepoint-aspx`'s
`page-manifest.json`/`pages/*.html`) — both are just a directory of
files, so no format-specific logic is needed.

## Public Interface

```python
from compare_rendered_output import compare_rendered_trees

report = compare_rendered_trees("fresh/rendered-output", "golden/rendered-output")
# ComparisonReport(status="MATCH"|"MISMATCH", issues=[...])
```

Detects: files present in the first tree but missing from the second
(`missing_in_b`), files present in the second but not the first
(`extra_in_b`), and byte-content mismatches for files present in both
(`content_mismatch`).

Two filenames are excluded from comparison by default (`generator-
info.json`, `render-result.json` — both carry run-specific fields);
pass `excluded_filenames=frozenset(...)` to override.

## Installation

```bash
pip install -e plugins/structured-content-rendering
```

## Dependencies

None beyond the Python standard library.

