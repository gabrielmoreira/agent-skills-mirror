---
name: sharepoint-configure-library-settings
plugin: sharepoint-provisioning
description: Configures advanced SharePoint document library version limits, content approval and draft visibility settings. Use to tune versioning and approval on a library. Dry-run by default; real writes require -Execute and confirmation token CONFIGURE-SPO-LIBRARY-SETTINGS.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-configure-library-settings.ps1 -PlanPath plan.json"
  - "pwsh -File scripts/spo-configure-library-settings.ps1 -PlanPath plan.json -Execute -ConfirmToken CONFIGURE-SPO-LIBRARY-SETTINGS"
---

# Configure SharePoint Library Settings

Set library version limits, content approval and draft visibility with Set-PnPList.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Dry run by default: without `-Execute` it prints a structured JSON action summary and changes nothing.
- A real write needs `-Execute -ConfirmToken CONFIGURE-SPO-LIBRARY-SETTINGS`, exactly. The plan's own `confirmation_token` field is a different value. A real run is a live tenant write that the user runs.
- Limited to version limits, content approval and draft visibility; use sharepoint-update-list-settings for a list's title, description or general versioning.
- Read the "Plan JSON shape" block in `scripts/spo-configure-library-settings.ps1`'s header and do not invent plan keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Quick start

```bash
pwsh -File scripts/spo-configure-library-settings.ps1 -PlanPath path/to/plan.json
```

## Workflow

1. Get or build the plan JSON for this operation.
2. Dry run (above) and review the action summary with the user.
3. After the user confirms, rerun with `-Execute -ConfirmToken CONFIGURE-SPO-LIBRARY-SETTINGS`.
4. Report the result and check it as described below.

## Verification

The dry-run summary lists the settings; afterwards the library reports them.

## References

- [Executor contract](references/provisioning-executor-contract.md): read for the safety contract, the two kinds of token, connection and config, plan shapes, and the full executor table.
