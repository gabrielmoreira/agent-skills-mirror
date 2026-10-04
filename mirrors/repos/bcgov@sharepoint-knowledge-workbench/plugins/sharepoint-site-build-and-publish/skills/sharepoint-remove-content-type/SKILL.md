---
name: sharepoint-remove-content-type
plugin: sharepoint-site-build-and-publish
description: Deletes a SharePoint content type from the site collection. Use to remove an obsolete content type. Dry-run by default; real writes require -Execute and confirmation token REMOVE-SPO-CONTENT-TYPES.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-remove-content-type.ps1 -PlanPath plan.json"
  - "pwsh -File scripts/spo-remove-content-type.ps1 -PlanPath plan.json -Execute -ConfirmToken REMOVE-SPO-CONTENT-TYPES"
---

# Remove SharePoint Content Type

Delete a content type from the site collection with Remove-PnPContentType.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Dry run by default: without `-Execute` it prints a structured JSON action summary and changes nothing.
- A real write needs `-Execute -ConfirmToken REMOVE-SPO-CONTENT-TYPES`, exactly. The plan's own `confirmation_token` field is a different value. A real run is a live tenant write that the user runs.
- Destructive. The script does not check whether the content type is still in use; detach it from lists first (sharepoint-detach-content-type) and confirm there are no dependents.
- Read the "Plan JSON shape" block in `scripts/spo-remove-content-type.ps1`'s header and do not invent plan keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Quick start

```bash
pwsh -File scripts/spo-remove-content-type.ps1 -PlanPath path/to/plan.json
```

## Workflow

1. Get or build the plan JSON for this operation.
2. Dry run (above) and review the action summary with the user.
3. After the user confirms, rerun with `-Execute -ConfirmToken REMOVE-SPO-CONTENT-TYPES`.
4. Report the result and check it as described below.

## Verification

The dry-run summary names the content type; afterwards it no longer exists in the site collection.

## References

- [Executor contract](references/provisioning-executor-contract.md): read for the safety contract, the two kinds of token, connection and config, plan shapes, and the full executor table.
