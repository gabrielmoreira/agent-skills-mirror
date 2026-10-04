---
name: sharepoint-update-content-type
plugin: sharepoint-site-build-and-publish
description: Updates SharePoint content type name, description, group or hidden properties. Use to rename or reclassify a content type. Dry-run by default; real writes require -Execute and confirmation token UPDATE-SPO-CONTENT-TYPES.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-update-content-type.ps1 -PlanPath plan.json"
  - "pwsh -File scripts/spo-update-content-type.ps1 -PlanPath plan.json -Execute -ConfirmToken UPDATE-SPO-CONTENT-TYPES"
---

# Update SharePoint Content Type

Change a content type's name, description, group or hidden flag with Set-PnPContentType.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Dry run by default: without `-Execute` it prints a structured JSON action summary and changes nothing.
- A real write needs `-Execute -ConfirmToken UPDATE-SPO-CONTENT-TYPES`, exactly. The plan's own `confirmation_token` field is a different value. A real run is a live tenant write that the user runs.
- Changes name, description, group and hidden only; adding or removing field links is sharepoint-create-content-type's job.
- Read the "Plan JSON shape" block in `scripts/spo-update-content-type.ps1`'s header and do not invent plan keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Quick start

```bash
pwsh -File scripts/spo-update-content-type.ps1 -PlanPath path/to/plan.json
```

## Workflow

1. Get or build the plan JSON for this operation.
2. Dry run (above) and review the action summary with the user.
3. After the user confirms, rerun with `-Execute -ConfirmToken UPDATE-SPO-CONTENT-TYPES`.
4. Report the result and check it as described below.

## Verification

The dry-run summary shows each property change; afterwards the content type carries the new values.

## References

- [Executor contract](references/provisioning-executor-contract.md): read for the safety contract, the two kinds of token, connection and config, plan shapes, and the full executor table.
