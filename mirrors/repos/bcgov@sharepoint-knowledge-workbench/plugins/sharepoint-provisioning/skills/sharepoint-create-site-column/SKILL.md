---
name: sharepoint-create-site-column
plugin: sharepoint-provisioning
description: Creates new SharePoint site columns across standard or complex types (Text, Choice, Lookup, User, Calculated via Field XML). Dry-run by default; real writes require -Execute and confirmation token PROVISION-SPO-SITE-COLUMNS.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-provision-site-columns.ps1 -PlanPath plan.json"
  - "pwsh -File scripts/spo-provision-site-columns.ps1 -PlanPath plan.json -Execute -ConfirmToken PROVISION-SPO-SITE-COLUMNS"
---

# Create SharePoint Site Column

## Overview

Use this skill to execute real SharePoint Online **Create SharePoint Site Column** operations using PnP.PowerShell (\$vb\).

### Safety Contract

- **Dry-run by default**: Running without \-Execute\ outputs a structured JSON action plan detailing the operations that would occur without modifying tenant state.
- **Confirmation Gated**: Real execution requires passing \-Execute\ alongside \-ConfirmToken PROVISION-SPO-SITE-COLUMNS\.
- **Connection Resolution**: Resolves credentials interactively or from \config.psd1\ via \Get-WorkbenchConnectionConfig.ps1\.

## Usage

### 1. Preview Actions (Dry-Run)

\\\ash
pwsh -File scripts/spo-provision-site-columns.ps1 -PlanPath path/to/plan.json
\\\

### 2. Execute Real Tenant Write

\\\ash
pwsh -File scripts/spo-provision-site-columns.ps1 -PlanPath path/to/plan.json -Execute -ConfirmToken PROVISION-SPO-SITE-COLUMNS
\\\

## Script Reference

- \scripts/spo-provision-site-columns.ps1\ — Primary PnP.PowerShell executor.
- \scripts/Get-WorkbenchConnectionConfig.ps1\ — Shared connection helper.