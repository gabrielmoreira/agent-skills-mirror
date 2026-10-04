---
name: sharepoint-create-content-type
plugin: sharepoint-site-build-and-publish
description: Creates new SharePoint content types, binds field links and attaches content types to target lists. Use to define a reusable content type. Dry-run by default; real writes require -Execute and confirmation token PROVISION-SPO-CONTENT-TYPES.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-provision-content-types.ps1 -PlanPath plan.json"
  - "pwsh -File scripts/spo-provision-content-types.ps1 -PlanPath plan.json -Execute -ConfirmToken PROVISION-SPO-CONTENT-TYPES"
---

# Create SharePoint Content Type

Create content types, bind field links and attach them to lists in one plan.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Dry run by default: without `-Execute` it prints a structured JSON action summary and changes nothing.
- A real write needs `-Execute -ConfirmToken PROVISION-SPO-CONTENT-TYPES`, exactly. The plan's own `confirmation_token` field is a different value. A real run is a live tenant write that the user runs.
- Check that the site columns the plan references exist before a real run (create them with sharepoint-create-site-column first).
- Read the "Plan JSON shape" block in `scripts/spo-provision-content-types.ps1`'s header and do not invent plan keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Quick start

```bash
pwsh -File scripts/spo-provision-content-types.ps1 -PlanPath path/to/plan.json
```

## Workflow

1. Get or build the plan JSON for this operation.
2. Dry run (above) and review the action summary with the user.
3. After the user confirms, rerun with `-Execute -ConfirmToken PROVISION-SPO-CONTENT-TYPES`.
4. Report the result and check it as described below.

## Verification

The dry-run summary lists the content types, field links and target lists; afterwards the content type exists and is attached.

## References

- [Executor contract](references/provisioning-executor-contract.md): read for the safety contract, the two kinds of token, connection and config, plan shapes, and the full executor table.
