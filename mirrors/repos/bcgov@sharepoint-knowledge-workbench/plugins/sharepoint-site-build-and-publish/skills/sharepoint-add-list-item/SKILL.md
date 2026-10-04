---
name: sharepoint-add-list-item
plugin: sharepoint-site-build-and-publish
description: Creates new list items in a SharePoint list with given field values. Use to seed or load items into an existing list. Dry-run by default; real writes require -Execute and confirmation token ADD-SPO-LIST-ITEM.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-add-list-item.ps1 -PlanPath plan.json"
  - "pwsh -File scripts/spo-add-list-item.ps1 -PlanPath plan.json -Execute -ConfirmToken ADD-SPO-LIST-ITEM"
---

# Add SharePoint List Items

Create items in an existing list with Add-PnPListItem.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Dry run by default: without `-Execute` it prints a structured JSON action summary and changes nothing.
- A real write needs `-Execute -ConfirmToken ADD-SPO-LIST-ITEM`, exactly. The plan's own `confirmation_token` field is a different value. A real run is a live tenant write that the user runs.
- Creates items only; it does not create the list or its columns. Use only field values the plan supplies.
- Read the "Plan JSON shape" block in `scripts/spo-add-list-item.ps1`'s header and do not invent plan keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Quick start

```bash
pwsh -File scripts/spo-add-list-item.ps1 -PlanPath path/to/plan.json
```

## Workflow

1. Get or build the plan JSON for this operation.
2. Dry run (above) and review the action summary with the user.
3. After the user confirms, rerun with `-Execute -ConfirmToken ADD-SPO-LIST-ITEM`.
4. Report the result and check it as described below.

## Verification

The dry-run summary lists the items; afterwards the items exist with the supplied values.

## References

- [Executor contract](references/provisioning-executor-contract.md): read for the safety contract, the two kinds of token, connection and config, plan shapes, and the full executor table.
