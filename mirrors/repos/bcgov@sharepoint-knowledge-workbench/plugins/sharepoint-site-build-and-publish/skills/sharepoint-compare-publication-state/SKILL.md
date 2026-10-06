---
name: sharepoint-compare-publication-state
plugin: sharepoint-site-build-and-publish
description: >-
  Read-only comparison of an expected UploadPackage against the actual observed SharePoint library state (a CSV export), reporting missing, duplicate, mismatched or unexpected items. Use after an upload to check that the library matches the package. Reports differences only: applies no fixes and performs no tenant I/O.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from sharepoint_reconcile import load_actual_state_from_csv, reconcile; print(reconcile(pkg, load_actual_state_from_csv('actual.csv')))\""
---

# Reconcile SharePoint Publication

Diff an `UploadPackage` (expected state) against `ActualLibraryItem` evidence loaded from a CSV export.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Read-only and zero tenant I/O; no tenant write of any kind.
- CSV export is the only confirmed evidence-capture mechanism; a Graph or PnP reader is left open.
- Comparison is scoped to the package's own entries.
- Run from this skill's root with `scripts/` on `sys.path`.

## Quick start

```python
import sys; sys.path.insert(0, "scripts")
from sharepoint_reconcile import load_actual_state_from_csv, reconcile
report = reconcile(pkg, load_actual_state_from_csv("actual.csv"))
```

## Workflow

1. Get the `UploadPackage` (built by `build_upload_package`) and a CSV export of the target library's default view.
2. Load the CSV with `load_actual_state_from_csv`; its headers must match exactly (see the CSV format reference).
3. Call `reconcile(pkg, actual_items)` and report each issue.

## Verification

Check the report for `MISSING_IN_LIBRARY`, `DUPLICATE_IN_LIBRARY`, `FIELD_MISMATCH` and `UNEXPECTED_IN_LIBRARY` (an item present
in the library but not in the package). No issues means the library matches the package for the compared fields.

## References

- [Actual-state CSV format](references/sharepoint-actual-state-csv-format.md): read before exporting or loading the CSV.
- [Executors, gates and constraints](references/publication-executors-and-gates.md): read for how this differs from the
  post-deployment presence check.
