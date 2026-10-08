---
name: sharepoint-create-document-library
plugin: sharepoint-site-build-and-publish
description: Creates a new SharePoint document library (Template 101) using PnP.PowerShell. Use to add a document library to a site. Dry-run by default; real writes require -Execute and confirmation token PROVISION-SPO-LIST.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-provision-list.ps1 -PlanPath plan.json"
  - "pwsh -File scripts/spo-provision-list.ps1 -PlanPath plan.json -Execute -ConfirmToken PROVISION-SPO-LIST"
---

# Create SharePoint Document Library

Create a document library (Template 101) with New-PnPList.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Dry run by default: without `-Execute` it prints a structured JSON action summary and changes nothing.
- A real write needs `-Execute -ConfirmToken PROVISION-SPO-LIST`, exactly. The plan's own `confirmation_token` field is a different value. A real run is a live tenant write that the user runs.
- Shares spo-provision-list.ps1 with sharepoint-create-list and sharepoint-remove-list, which applies a duplicate-title gate on the plan's blocking_findings.
- Read the "Plan JSON shape" block in `scripts/spo-provision-list.ps1`'s header and do not invent plan keys. When running an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Quick start

```bash
pwsh -File scripts/spo-provision-list.ps1 -PlanPath path/to/plan.json
```

## Workflow

1. Get or build the plan JSON for this operation.
2. Dry run (above) and review the action summary with the user.
3. After the user confirms, rerun with `-Execute -ConfirmToken PROVISION-SPO-LIST`.
4. Report the result and check it as described below.

## Create a folder inside a library

Use `scripts/spo-create-folder.ps1` to create a nested folder path in an existing library. It verifies the library, then creates and confirms each missing segment parent first. Dry run by default; a real write needs `-Execute -ConfirmToken CREATE-SPO-FOLDER`.

```bash
pwsh -File scripts/spo-create-folder.ps1 -LibraryName sheriff -FolderPath "administrative documents/awards"
```

## Verification

The dry-run summary lists the library; afterwards a Get-PnPList re-check finds it.

## References

- [Executor contract](references/provisioning-executor-contract.md): read for the safety contract, the two kinds of token, connection and config, plan shapes, and the full executor table.
