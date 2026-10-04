---
name: sharepoint-add-list-column
plugin: sharepoint-site-build-and-publish
description: Adds a column directly to an existing SharePoint list or library. Use when a column belongs to one list only. Dry-run by default; real writes require -Execute and confirmation token ADD-SPO-LIST-COLUMN.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-add-list-column.ps1 -PlanPath plan.json"
  - "pwsh -File scripts/spo-add-list-column.ps1 -PlanPath plan.json -Execute -ConfirmToken ADD-SPO-LIST-COLUMN"
---

# Add SharePoint List Column

Add a column to one existing list or library with Add-PnPField.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Dry run by default: without `-Execute` it prints a structured JSON action summary and changes nothing.
- A real write needs `-Execute -ConfirmToken ADD-SPO-LIST-COLUMN`, exactly. The plan's own `confirmation_token` field is a different value. A real run is a live tenant write that the user runs.
- The target list or library must already exist; this adds a column, not a list.
- Read the "Plan JSON shape" block in `scripts/spo-add-list-column.ps1`'s header and do not invent plan keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Quick start

```bash
pwsh -File scripts/spo-add-list-column.ps1 -PlanPath path/to/plan.json
```

## Workflow

1. Get or build the plan JSON for this operation.
2. Dry run (above) and review the action summary with the user.
3. After the user confirms, rerun with `-Execute -ConfirmToken ADD-SPO-LIST-COLUMN`.
4. Report the result and check it as described below.

## Verification

The dry-run summary lists the column(s) and the target list; afterwards the column exists on that list.

## References

- [Executor contract](references/provisioning-executor-contract.md): read for the safety contract, the two kinds of token, connection and config, plan shapes, and the full executor table.
