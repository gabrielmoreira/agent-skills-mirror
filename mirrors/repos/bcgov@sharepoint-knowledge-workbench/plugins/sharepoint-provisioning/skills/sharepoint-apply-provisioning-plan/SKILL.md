---
name: sharepoint-apply-provisioning-plan
plugin: sharepoint-provisioning
description: The real PnP.PowerShell executors for sharepoint-provisioning's plan JSON, covering create, update and delete of lists, libraries, site columns and content types, content-type attach and detach, and the granular and site-level operations (views, items, pages, web parts, permissions, navigation, term sets, branding, hub sites, re-index). Use once a plan has been approved, to pick the right executor script. Dry-run by default; every write is gated behind -Execute and an operation-specific -ConfirmToken.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-update-site-column.ps1 -PlanPath update-plan.json -Execute -ConfirmToken UPDATE-SPO-SITE-COLUMNS -ConfigPath config.psd1"
---

# Apply Provisioning Plan

Choose and run the right real executor for an approved plan. This is the "injected executor" counterpart to the Python planning modules.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Nothing is written to the tenant unless both `-Execute` and the script's exact `-ConfirmToken` are passed. Without `-Execute` every script prints a dry-run JSON summary, including the exact PnP cmdlet it would run.
- A real run is a live tenant write that the user runs. Never pass a token the user has not confirmed, and never reuse one script's token for another (each token is operation-specific; see the table).
- The plan's own `confirmation_token` field is not the `-ConfirmToken` value.
- Read the "Plan JSON shape" block in the chosen script's header and do not invent keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).
- `Get-WorkbenchConnectionConfig.ps1` is a shared helper, not an executor.

## Quick start

```bash
pwsh -File scripts/spo-provision-list.ps1 -PlanPath plan.json
```

## Workflow

1. Identify the operation and pick the script from the executor table. The Python planning modules feed three of them directly: `list_provisioning` to `spo-provision-list.ps1`, `content_type_provisioning` to `spo-provision-content-types.ps1`, `field_provisioning` to `spo-provision-site-columns.ps1`. The rest take a custom or manual plan JSON.
2. Dry run and review the action summary with the user.
3. After the user confirms, rerun with `-Execute -ConfirmToken <that script's token>`.
4. Report the result. Prefer the dedicated skill for an operation when one exists (for example `sharepoint-create-list`).

## Verification

The dry run names the intended PnP calls and targets; after a real run, check the outcome the script reports and confirm the object on the tenant. Deletions are not all re-checked by the scripts, so verify them.

## References

- [Executor contract](references/provisioning-executor-contract.md): read for the full executor and token table (28 scripts), the safety contract, connection and config, and plan shapes.
