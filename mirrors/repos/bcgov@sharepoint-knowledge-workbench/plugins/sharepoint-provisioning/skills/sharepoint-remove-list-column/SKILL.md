---
name: sharepoint-remove-list-column
plugin: sharepoint-provisioning
description: Removes a list-scoped column from a SharePoint list or library. Dry-run by default; real writes require -Execute and confirmation token REMOVE-SPO-LIST-COLUMN.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-remove-list-column.ps1 -PlanPath plan.json"
  - "pwsh -File scripts/spo-remove-list-column.ps1 -PlanPath plan.json -Execute -ConfirmToken REMOVE-SPO-LIST-COLUMN"
---

# Remove SharePoint List Column

## Overview

Use this skill to execute real SharePoint Online **Remove SharePoint List Column** operations using PnP.PowerShell (\$vb\).

### Safety Contract

- **Dry-run by default**: Running without \-Execute\ outputs a structured JSON action plan detailing the operations that would occur without modifying tenant state.
- **Confirmation Gated**: Real execution requires passing \-Execute\ alongside \-ConfirmToken REMOVE-SPO-LIST-COLUMN\.
- **Connection Resolution**: Resolves credentials interactively or from \config.psd1\ via \Get-WorkbenchConnectionConfig.ps1\.

## Usage

### 1. Preview Actions (Dry-Run)

\\\ash
pwsh -File scripts/spo-remove-list-column.ps1 -PlanPath path/to/plan.json
\\\

### 2. Execute Real Tenant Write

\\\ash
pwsh -File scripts/spo-remove-list-column.ps1 -PlanPath path/to/plan.json -Execute -ConfirmToken REMOVE-SPO-LIST-COLUMN
\\\

## Script Reference

- \scripts/spo-remove-list-column.ps1\ — Primary PnP.PowerShell executor.
- \scripts/Get-WorkbenchConnectionConfig.ps1\ — Shared connection helper.