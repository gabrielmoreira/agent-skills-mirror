---
name: sharepoint-update-list-column
plugin: sharepoint-site-build-and-publish
description: Updates a list-scoped column's properties on a specific SharePoint list. Use to change one list's column. Dry-run by default; real writes require -Execute and confirmation token UPDATE-SPO-LIST-COLUMN.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-update-list-column.ps1 -PlanPath plan.json"
  - "pwsh -File scripts/spo-update-list-column.ps1 -PlanPath plan.json -Execute -ConfirmToken UPDATE-SPO-LIST-COLUMN"
---

# Update SharePoint List Column

Update a list-scoped column with Set-PnPField.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Dry run by default: without `-Execute` it prints a structured JSON action summary and changes nothing.
- A real write needs `-Execute -ConfirmToken UPDATE-SPO-LIST-COLUMN`, exactly. The plan's own `confirmation_token` field is a different value. A real run is a live tenant write that the user runs.
- List-scoped: changes one list's column only. Treat a column type change as risky and confirm it with the user.
- Read the "Plan JSON shape" block in `scripts/spo-update-list-column.ps1`'s header and do not invent plan keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Quick start

```bash
pwsh -File scripts/spo-update-list-column.ps1 -PlanPath path/to/plan.json
```

## Workflow

1. Get or build the plan JSON for this operation.
2. Dry run (above) and review the action summary with the user.
3. After the user confirms, rerun with `-Execute -ConfirmToken UPDATE-SPO-LIST-COLUMN`.
4. Report the result and check it as described below.

## Verification

The dry-run summary shows each property change; afterwards that list's column carries the new values.

## References

- [Executor contract](references/provisioning-executor-contract.md): read for the safety contract, the two kinds of token, connection and config, plan shapes, and the full executor table.
