---
name: sharepoint-validate-publication
description: Offline pre-upload schema validation of an UploadPackage against the target library schema, plus a real read-only post-deployment presence check (Get-PnPPage/Get-PnPFile) confirming a PublishPlan's targets actually landed on the tenant.
---

# validate-sharepoint-publication

## Purpose

**Pre-upload validation (existing, real):** `sharepoint_dry_run.py`'s `validate_upload_package`
runs entirely offline — zero tenant I/O — checking an `UploadPackage`'s fields against the
target library schema (e.g. title length) before any human upload happens.

**Post-deployment validation (real, added 2026-08-17):**
`scripts/spo-validate-publication-deployment.ps1` reads a `PublishPlan` and confirms each target
actually exists on the tenant — `Get-PnPPage` for a `SitePages` target, `Get-PnPFile` for a
document-library target — reporting `OBSERVED`/`EMPTY` per target and an overall `PASS`/`FAIL`.
Read-only, so it always runs live (no `-Execute`/confirmation token — there is nothing to
confirm, this script never writes). Checks presence only, not field-level content match;
`reconcile-sharepoint-publication` covers identity-field reconciliation against a CSV export from
a different angle.

## Input boundaries

- Pre-upload: an `UploadPackage`, checked entirely offline.
- Post-deployment: a `PublishPlan`, checked against live tenant state (read-only).

## Scripts

- `../../scripts/sharepoint_dry_run.py` (existing, pre-upload only).
- `../../scripts/spo-validate-publication-deployment.ps1` — real, read-only post-deployment
  presence check.

## Tests

- `../../tests/unit/test_sharepoint_dry_run.py` (existing).

