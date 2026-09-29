---
name: sharepoint-add-list-item
plugin: sharepoint-provisioning
description: Creates new list items in a SharePoint list with field values. Dry-run by default; real writes require -Execute and confirmation token ADD-SPO-LIST-ITEM.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-add-list-item.ps1 -PlanPath plan.json"
  - "pwsh -File scripts/spo-add-list-item.ps1 -PlanPath plan.json -Execute -ConfirmToken ADD-SPO-LIST-ITEM"
---

# Add SharePoint List Item

## Overview

Use this skill to execute real SharePoint Online **Add SharePoint List Item** operations using PnP.PowerShell (\$vb\).

### Safety Contract

- **Dry-run by default**: Running without \-Execute\ outputs a structured JSON action plan detailing the operations that would occur without modifying tenant state.
- **Confirmation Gated**: Real execution requires passing \-Execute\ alongside \-ConfirmToken ADD-SPO-LIST-ITEM\.
- **Connection Resolution**: Resolves credentials interactively or from \config.psd1\ via \Get-WorkbenchConnectionConfig.ps1\.

## Usage

### 1. Preview Actions (Dry-Run)

\\\ash
pwsh -File scripts/spo-add-list-item.ps1 -PlanPath path/to/plan.json
\\\

### 2. Execute Real Tenant Write

\\\ash
pwsh -File scripts/spo-add-list-item.ps1 -PlanPath path/to/plan.json -Execute -ConfirmToken ADD-SPO-LIST-ITEM
\\\

## Script Reference

- \scripts/spo-add-list-item.ps1\ — Primary PnP.PowerShell executor.
- \scripts/Get-WorkbenchConnectionConfig.ps1\ — Shared connection helper.