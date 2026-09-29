---
name: sharepoint-update-list-settings
plugin: sharepoint-provisioning
description: Updates SharePoint list or library title, description, and versioning settings using Set-PnPList. Dry-run by default; real writes require -Execute and confirmation token UPDATE-SPO-LIST.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-update-list.ps1 -PlanPath plan.json"
  - "pwsh -File scripts/spo-update-list.ps1 -PlanPath plan.json -Execute -ConfirmToken UPDATE-SPO-LIST"
---

# Update SharePoint List Settings

## Overview

Use this skill to execute real SharePoint Online **Update SharePoint List Settings** operations using PnP.PowerShell (\$vb\).

### Safety Contract

- **Dry-run by default**: Running without \-Execute\ outputs a structured JSON action plan detailing the operations that would occur without modifying tenant state.
- **Confirmation Gated**: Real execution requires passing \-Execute\ alongside \-ConfirmToken UPDATE-SPO-LIST\.
- **Connection Resolution**: Resolves credentials interactively or from \config.psd1\ via \Get-WorkbenchConnectionConfig.ps1\.

## Usage

### 1. Preview Actions (Dry-Run)

\\\ash
pwsh -File scripts/spo-update-list.ps1 -PlanPath path/to/plan.json
\\\

### 2. Execute Real Tenant Write

\\\ash
pwsh -File scripts/spo-update-list.ps1 -PlanPath path/to/plan.json -Execute -ConfirmToken UPDATE-SPO-LIST
\\\

## Script Reference

- \scripts/spo-update-list.ps1\ — Primary PnP.PowerShell executor.
- \scripts/Get-WorkbenchConnectionConfig.ps1\ — Shared connection helper.