---
name: sharepoint-remove-site-column
plugin: sharepoint-site-build-and-publish
description: Deletes a SharePoint site column and reports each column as removed or failed. Use to remove an obsolete site column. Dry-run by default; real writes require -Execute and confirmation token REMOVE-SPO-SITE-COLUMNS.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-remove-site-column.ps1 -PlanPath plan.json"
  - "pwsh -File scripts/spo-remove-site-column.ps1 -PlanPath plan.json -Execute -ConfirmToken REMOVE-SPO-SITE-COLUMNS"
---

# Remove SharePoint Site Column

Delete site columns with Remove-PnPField -Force.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Dry run by default: without `-Execute` it prints a structured JSON action summary and changes nothing.
- A real write needs `-Execute -ConfirmToken REMOVE-SPO-SITE-COLUMNS`, exactly. The plan's own `confirmation_token` field is a different value. A real run is a live tenant write that the user runs.
- Destructive and site-wide. The script does not check dependents and does not re-check afterwards (it records each column as removed or failed); confirm no content types or lists use the column and verify it is gone.
- Read the "Plan JSON shape" block in `scripts/spo-remove-site-column.ps1`'s header and do not invent plan keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Quick start

```bash
pwsh -File scripts/spo-remove-site-column.ps1 -PlanPath path/to/plan.json
```

## Workflow

1. Get or build the plan JSON for this operation.
2. Dry run (above) and review the action summary with the user.
3. After the user confirms, rerun with `-Execute -ConfirmToken REMOVE-SPO-SITE-COLUMNS`.
4. Report the result and check it as described below.

## Verification

The result lists each column under removed or failed with an outcome of OBSERVED, PARTIAL or FAILED.

## References

- [Executor contract](references/provisioning-executor-contract.md): read for the safety contract, the two kinds of token, connection and config, plan shapes, and the full executor table.
