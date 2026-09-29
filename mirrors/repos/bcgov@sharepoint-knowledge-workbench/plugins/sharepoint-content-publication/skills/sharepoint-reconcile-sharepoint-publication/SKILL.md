---
name: sharepoint-reconcile-sharepoint-publication
description: Read-only comparison of an expected upload package against actual observed SharePoint library state (missing, duplicate, mismatched, or unexpected items).
---

# reconcile-sharepoint-publication

## Purpose

Diffs an `UploadPackage` (expected state, from `sharepoint_package.py`) against
`ActualLibraryItem` evidence (currently: CSV export — the only Phase 3.0-confirmed evidence-
capture mechanism; a future Graph/PnP-based reader is left open by resolved decision #10 in
`docs/superpowers/specs/phase-3-unresolved-decisions.md`). Zero tenant I/O — package-only,
matching the plugin's existing scope.

## Input boundaries

- An `UploadPackage` (built by `build_upload_package`) and a CSV path of actual observed state.
- Comparison is scoped to the package's own entries — reports `MISSING_IN_LIBRARY`,
  `DUPLICATE_IN_LIBRARY`, `FIELD_MISMATCH`, and `UNEXPECTED_IN_LIBRARY` (an actual-state item not
  in the expected package).

## Prohibited scope

- Read-only — no tenant write of any kind.

## Scripts

- `../../scripts/sharepoint_reconcile.py` (existing, real implementation).

## Tests

- `../../tests/unit/test_sharepoint_reconcile.py` (existing).

