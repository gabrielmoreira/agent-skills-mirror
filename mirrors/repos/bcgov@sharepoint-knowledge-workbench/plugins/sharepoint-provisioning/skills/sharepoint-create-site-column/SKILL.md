---
name: sharepoint-create-site-column
plugin: sharepoint-provisioning
description: Creates new SharePoint site columns across standard or complex types (Text, Choice, Lookup, User, Calculated via Field XML). Use to define a reusable site column. Dry-run by default; real writes require -Execute and confirmation token PROVISION-SPO-SITE-COLUMNS.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-provision-site-columns.ps1 -PlanPath plan.json"
  - "pwsh -File scripts/spo-provision-site-columns.ps1 -PlanPath plan.json -Execute -ConfirmToken PROVISION-SPO-SITE-COLUMNS"
---

# Create SharePoint Site Column

Create site columns with Add-PnPField, or Add-PnPFieldFromXml for complex types.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Dry run by default: without `-Execute` it prints a structured JSON action summary and changes nothing.
- A real write needs `-Execute -ConfirmToken PROVISION-SPO-SITE-COLUMNS`, exactly. The plan's own `confirmation_token` field is a different value. A real run is a live tenant write that the user runs.
- Supports standard and complex types, including Calculated via Field XML; use Field XML as supplied and do not rewrite formulas.
- Read the "Plan JSON shape" block in `scripts/spo-provision-site-columns.ps1`'s header and do not invent plan keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Quick start

```bash
pwsh -File scripts/spo-provision-site-columns.ps1 -PlanPath path/to/plan.json
```

## Workflow

1. Get or build the plan JSON for this operation.
2. Dry run (above) and review the action summary with the user.
3. After the user confirms, rerun with `-Execute -ConfirmToken PROVISION-SPO-SITE-COLUMNS`.
4. Report the result and check it as described below.

## Verification

The dry-run summary lists each column and type; afterwards the site column exists.

## References

- [Executor contract](references/provisioning-executor-contract.md): read for the safety contract, the two kinds of token, connection and config, plan shapes, and the full executor table.
