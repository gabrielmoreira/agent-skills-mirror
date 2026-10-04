---
name: sharepoint-remove-publication
plugin: sharepoint-site-build-and-publish
description: Builds a rollback plan reversing a prior publication's exact actions, scoped to one document, then a real PnP executor removes each target (Remove-PnPPage or Remove-PnPFile) with fail-loud removal verification. Use to undo a publication. Dry-run by default.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from sharepoint_publish_plan import build_rollback_plan; print(build_rollback_plan('doc-1', previous_plan))\""
  - "pwsh -File scripts/spo-rollback-publication.ps1 -PlanPath rollback.json -SiteUrl \"https://tenant.sharepoint.com/sites/Test\""
---

# Roll Back SharePoint Publication

Given a prior `PublishPlan`, produce a `RollbackPlan` (the exact targets to remove) and remove them with the real executor.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Package-scoped: only reverse the named `document_id`'s own actions. A `document_id` that does not match the supplied plan's
  own raises `PlanError`; never roll back the wrong document.
- Planning performs zero tenant I/O. The executor `scripts/spo-rollback-publication.ps1` is dry-run by default and deletes nothing
  without `-Execute -ConfirmToken ROLLBACK-SPO-PLAN`. A real run is a destructive live tenant write that the user runs.
- Verify each removal. The executor throws if a target is still present afterwards; never report an unverified delete as success.
- When running from an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Quick start

```python
import sys; sys.path.insert(0, "scripts")
from sharepoint_publish_plan import build_rollback_plan
rollback = build_rollback_plan(document_id, previous_publish_plan)
```

## Workflow

1. Build the rollback plan from the original `PublishPlan` and its `document_id`.
2. Save it as JSON and dry run: `pwsh -File scripts/spo-rollback-publication.ps1 -PlanPath rollback.json`.
3. After the user confirms, rerun with `-Execute -ConfirmToken ROLLBACK-SPO-PLAN`. `Remove-PnPPage` handles a `SitePages` target and
   `Remove-PnPFile` a document-library target.

## Verification

Confirm the dry run lists exactly the targets the original plan created, then that every target reports absent after the real run.

## References

- [Executors, gates and constraints](references/publication-executors-and-gates.md): read for the executor table, config note and
  the corrections history.
