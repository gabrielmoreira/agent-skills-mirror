---
name: sharepoint-update-site-column
plugin: sharepoint-provisioning
description: Updates existing SharePoint site column properties (display name, description, required, choices) using Set-PnPField. Dry-run by default; real writes require -Execute and confirmation token UPDATE-SPO-SITE-COLUMNS.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-update-site-column.ps1 -PlanPath plan.json"
  - "pwsh -File scripts/spo-update-site-column.ps1 -PlanPath plan.json -Execute -ConfirmToken UPDATE-SPO-SITE-COLUMNS"
---

# Update SharePoint Site Column

## Overview

Use this skill to execute real SharePoint Online **Update SharePoint Site Column** operations using PnP.PowerShell (\$vb\).

### Safety Contract

- **Dry-run by default**: Running without \-Execute\ outputs a structured JSON action plan detailing the operations that would occur without modifying tenant state.
- **Confirmation Gated**: Real execution requires passing \-Execute\ alongside \-ConfirmToken UPDATE-SPO-SITE-COLUMNS\.
- **Connection Resolution**: Resolves credentials interactively or from \config.psd1\ via \Get-WorkbenchConnectionConfig.ps1\.

## Usage

### 1. Preview Actions (Dry-Run)

\\\ash
pwsh -File scripts/spo-update-site-column.ps1 -PlanPath path/to/plan.json
\\\

### 2. Execute Real Tenant Write

\\\ash
pwsh -File scripts/spo-update-site-column.ps1 -PlanPath path/to/plan.json -Execute -ConfirmToken UPDATE-SPO-SITE-COLUMNS
\\\

## Script Reference

- \scripts/spo-update-site-column.ps1\ — Primary PnP.PowerShell executor.
- \scripts/Get-WorkbenchConnectionConfig.ps1\ — Shared connection helper.