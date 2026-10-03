---
name: sharepoint-detach-content-type
plugin: sharepoint-provisioning
description: Detaches and unlinks a content type from a specific SharePoint list or library. Use to stop a list using a content type without deleting it. Dry-run by default; real writes require -Execute and confirmation token DETACH-SPO-CONTENT-TYPE.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-detach-content-type-from-list.ps1 -PlanPath plan.json"
  - "pwsh -File scripts/spo-detach-content-type-from-list.ps1 -PlanPath plan.json -Execute -ConfirmToken DETACH-SPO-CONTENT-TYPE"
---

# Detach SharePoint Content Type

Unlink a content type from one list with Remove-PnPContentTypeFromList.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Dry run by default: without `-Execute` it prints a structured JSON action summary and changes nothing.
- A real write needs `-Execute -ConfirmToken DETACH-SPO-CONTENT-TYPE`, exactly. The plan's own `confirmation_token` field is a different value. A real run is a live tenant write that the user runs.
- Detaches from one list only; the site content type stays. Use sharepoint-remove-content-type to delete it from the site collection.
- Read the "Plan JSON shape" block in `scripts/spo-detach-content-type-from-list.ps1`'s header and do not invent plan keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Quick start

```bash
pwsh -File scripts/spo-detach-content-type-from-list.ps1 -PlanPath path/to/plan.json
```

## Workflow

1. Get or build the plan JSON for this operation.
2. Dry run (above) and review the action summary with the user.
3. After the user confirms, rerun with `-Execute -ConfirmToken DETACH-SPO-CONTENT-TYPE`.
4. Report the result and check it as described below.

## Verification

The dry-run summary names the list and content type; afterwards the list no longer offers the content type.

## References

- [Executor contract](references/provisioning-executor-contract.md): read for the safety contract, the two kinds of token, connection and config, plan shapes, and the full executor table.
