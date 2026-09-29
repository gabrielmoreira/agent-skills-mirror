---
name: sharepoint-remove-list
plugin: sharepoint-provisioning
description: Safely deletes a SharePoint list or document library with fail-loud post-deletion verification. Dry-run by default; real writes require -Execute and confirmation token PROVISION-SPO-LIST.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-provision-list.ps1 -PlanPath plan.json"
  - "pwsh -File scripts/spo-provision-list.ps1 -PlanPath plan.json -Execute -ConfirmToken PROVISION-SPO-LIST"
---

# Remove SharePoint List or Library

## Overview

Use this skill to execute real SharePoint Online **Remove SharePoint List or Library** operations using PnP.PowerShell (\$vb\).

### Safety Contract

- **Dry-run by default**: Running without \-Execute\ outputs a structured JSON action plan detailing the operations that would occur without modifying tenant state.
- **Confirmation Gated**: Real execution requires passing \-Execute\ alongside \-ConfirmToken PROVISION-SPO-LIST\.
- **Connection Resolution**: Resolves credentials interactively or from \config.psd1\ via \Get-WorkbenchConnectionConfig.ps1\.

## Usage

### 1. Preview Actions (Dry-Run)

\\\ash
pwsh -File scripts/spo-provision-list.ps1 -PlanPath path/to/plan.json
\\\

### 2. Execute Real Tenant Write

\\\ash
pwsh -File scripts/spo-provision-list.ps1 -PlanPath path/to/plan.json -Execute -ConfirmToken PROVISION-SPO-LIST
\\\

## Script Reference

- \scripts/spo-provision-list.ps1\ — Primary PnP.PowerShell executor.
- \scripts/Get-WorkbenchConnectionConfig.ps1\ — Shared connection helper.