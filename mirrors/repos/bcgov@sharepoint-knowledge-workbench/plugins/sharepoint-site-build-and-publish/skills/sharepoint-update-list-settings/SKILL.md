---
name: sharepoint-update-list-settings
plugin: sharepoint-site-build-and-publish
description: Updates SharePoint list or library title, description and versioning settings using Set-PnPList. Use to rename or reconfigure a list. Dry-run by default; real writes require -Execute and confirmation token UPDATE-SPO-LIST.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-update-list.ps1 -PlanPath plan.json"
  - "pwsh -File scripts/spo-update-list.ps1 -PlanPath plan.json -Execute -ConfirmToken UPDATE-SPO-LIST"
---

# Update SharePoint List Settings

Change a list's title, description and versioning with Set-PnPList.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Dry run by default: without `-Execute` it prints a structured JSON action summary and changes nothing.
- A real write needs `-Execute -ConfirmToken UPDATE-SPO-LIST`, exactly. The plan's own `confirmation_token` field is a different value. A real run is a live tenant write that the user runs.
- Title, description and versioning only. To recreate a list use sharepoint-remove-list then sharepoint-create-list; to tune approval and draft visibility use sharepoint-configure-library-settings.
- Read the "Plan JSON shape" block in `scripts/spo-update-list.ps1`'s header and do not invent plan keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Quick start

```bash
pwsh -File scripts/spo-update-list.ps1 -PlanPath path/to/plan.json
```

## Workflow

1. Get or build the plan JSON for this operation.
2. Dry run (above) and review the action summary with the user.
3. After the user confirms, rerun with `-Execute -ConfirmToken UPDATE-SPO-LIST`.
4. Report the result and check it as described below.

## Verification

The dry-run summary shows each setting change; afterwards the list reports the new values.

## References

- [Executor contract](references/provisioning-executor-contract.md): read for the safety contract, the two kinds of token, connection and config, plan shapes, and the full executor table.
