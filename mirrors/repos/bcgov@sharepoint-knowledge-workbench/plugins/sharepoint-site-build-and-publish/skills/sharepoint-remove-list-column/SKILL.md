---
name: sharepoint-remove-list-column
plugin: sharepoint-site-build-and-publish
description: Removes a list-scoped column from a SharePoint list or library. Use to drop a column from one list only. Dry-run by default; real writes require -Execute and confirmation token REMOVE-SPO-LIST-COLUMN.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-remove-list-column.ps1 -PlanPath plan.json"
  - "pwsh -File scripts/spo-remove-list-column.ps1 -PlanPath plan.json -Execute -ConfirmToken REMOVE-SPO-LIST-COLUMN"
---

# Remove SharePoint List Column

Remove a list-scoped column with Remove-PnPField.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Dry run by default: without `-Execute` it prints a structured JSON action summary and changes nothing.
- A real write needs `-Execute -ConfirmToken REMOVE-SPO-LIST-COLUMN`, exactly. The plan's own `confirmation_token` field is a different value. A real run is a live tenant write that the user runs.
- Destructive for that column's data on that list only; remove a site column with sharepoint-remove-site-column instead. The script does not check whether the column is in use.
- Read the "Plan JSON shape" block in `scripts/spo-remove-list-column.ps1`'s header and do not invent plan keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Quick start

```bash
pwsh -File scripts/spo-remove-list-column.ps1 -PlanPath path/to/plan.json
```

## Workflow

1. Get or build the plan JSON for this operation.
2. Dry run (above) and review the action summary with the user.
3. After the user confirms, rerun with `-Execute -ConfirmToken REMOVE-SPO-LIST-COLUMN`.
4. Report the result and check it as described below.

## Verification

The dry-run summary names the list and column; afterwards the column is gone from that list.

## References

- [Executor contract](references/provisioning-executor-contract.md): read for the safety contract, the two kinds of token, connection and config, plan shapes, and the full executor table.
