---
name: sharepoint-create-list-view
plugin: sharepoint-provisioning
description: Creates and configures custom views for SharePoint lists and document libraries. Use to add a filtered or sorted view. Dry-run by default; real writes require -Execute and confirmation token PROVISION-SPO-LIST-VIEW.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-provision-list-view.ps1 -PlanPath plan.json"
  - "pwsh -File scripts/spo-provision-list-view.ps1 -PlanPath plan.json -Execute -ConfirmToken PROVISION-SPO-LIST-VIEW"
---

# Create SharePoint List View

Create and configure a custom view with Add-PnPView.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Dry run by default: without `-Execute` it prints a structured JSON action summary and changes nothing.
- A real write needs `-Execute -ConfirmToken PROVISION-SPO-LIST-VIEW`, exactly. The plan's own `confirmation_token` field is a different value. A real run is a live tenant write that the user runs.
- A view references columns; confirm they exist on the list before a real run.
- Read the "Plan JSON shape" block in `scripts/spo-provision-list-view.ps1`'s header and do not invent plan keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Quick start

```bash
pwsh -File scripts/spo-provision-list-view.ps1 -PlanPath path/to/plan.json
```

## Workflow

1. Get or build the plan JSON for this operation.
2. Dry run (above) and review the action summary with the user.
3. After the user confirms, rerun with `-Execute -ConfirmToken PROVISION-SPO-LIST-VIEW`.
4. Report the result and check it as described below.

## Verification

The dry-run summary lists the view and its columns; afterwards the view exists on the list.

## References

- [Executor contract](references/provisioning-executor-contract.md): read for the safety contract, the two kinds of token, connection and config, plan shapes, and the full executor table.
