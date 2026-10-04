---
name: sharepoint-validate-publication
plugin: sharepoint-site-build-and-publish
description: Offline pre-upload schema validation of an UploadPackage against the target library schema, plus a read-only post-deployment presence check (Get-PnPPage or Get-PnPFile) confirming that a PublishPlan's targets landed on the tenant. Use before uploading and again after publishing.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from sharepoint_dry_run import validate_upload_package; print(validate_upload_package(pkg))\""
  - "pwsh -File scripts/spo-validate-publication-deployment.ps1 -PlanPath plan.json -SiteUrl \"https://tenant.sharepoint.com/sites/Test\""
---

# Validate SharePoint Publication

Two checks: an offline pre-upload validation, and a read-only post-deployment presence check.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Pre-upload validation is entirely offline (`validate_upload_package`), with zero tenant I/O.
- The post-deployment check is read-only and always live: it never writes, so it has no `-Execute` or token. It checks presence only,
  not field-level content (use `sharepoint-compare-publication-state` for identity-field reconciliation).
- When running from an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).
- Run Python from this skill's root with `scripts/` on `sys.path`.

## Quick start

```python
import sys; sys.path.insert(0, "scripts")
from sharepoint_dry_run import validate_upload_package
report = validate_upload_package(pkg)
```

## Workflow

1. Before upload: call `validate_upload_package(pkg)` and fix any issues (for example title length against the library schema).
2. After upload: run `scripts/spo-validate-publication-deployment.ps1 -PlanPath plan.json`. `Get-PnPPage` checks a `SitePages` target
   and `Get-PnPFile` a library target.

## Verification

The offline report has no blocking issues; the post-deployment run reports `OBSERVED` for every target and an overall `PASS`. An
`EMPTY` target means it is not on the tenant.

## References

- [Executors, gates and constraints](references/publication-executors-and-gates.md): read for the executor table and the config note.
