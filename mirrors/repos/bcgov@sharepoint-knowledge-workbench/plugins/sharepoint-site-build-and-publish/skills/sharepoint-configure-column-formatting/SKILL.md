---
name: sharepoint-configure-column-formatting
plugin: sharepoint-site-build-and-publish
description: Applies JSON custom column formatting and custom renderers to SharePoint fields. Use to change how a column displays. Dry-run by default; real writes require -Execute and confirmation token CONFIGURE-SPO-COLUMN-FORMATTING.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-configure-column-formatting.ps1 -PlanPath plan.json"
  - "pwsh -File scripts/spo-configure-column-formatting.ps1 -PlanPath plan.json -Execute -ConfirmToken CONFIGURE-SPO-COLUMN-FORMATTING"
---

# Configure SharePoint Column Formatting

Apply JSON column formatting (CustomFormatter) to fields.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Dry run by default: without `-Execute` it prints a structured JSON action summary and changes nothing.
- A real write needs `-Execute -ConfirmToken CONFIGURE-SPO-COLUMN-FORMATTING`, exactly. The plan's own `confirmation_token` field is a different value. A real run is a live tenant write that the user runs.
- Apply the formatting JSON the plan supplies; do not author or alter it.
- Read the "Plan JSON shape" block in `scripts/spo-configure-column-formatting.ps1`'s header and do not invent plan keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Quick start

```bash
pwsh -File scripts/spo-configure-column-formatting.ps1 -PlanPath path/to/plan.json
```

## Workflow

1. Get or build the plan JSON for this operation.
2. Dry run (above) and review the action summary with the user.
3. After the user confirms, rerun with `-Execute -ConfirmToken CONFIGURE-SPO-COLUMN-FORMATTING`.
4. Report the result and check it as described below.

## Verification

The dry-run summary names the fields; afterwards each column renders with its formatter.

## References

- [Executor contract](references/provisioning-executor-contract.md): read for the safety contract, the two kinds of token, connection and config, plan shapes, and the full executor table.
