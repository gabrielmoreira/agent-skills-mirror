---
name: sharepoint-create-content-type
plugin: sharepoint-provisioning
description: Creates new SharePoint content types, binds field links, and attaches content types to target lists. Dry-run by default; real writes require -Execute and confirmation token PROVISION-SPO-CONTENT-TYPES.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-provision-content-types.ps1 -PlanPath plan.json"
  - "pwsh -File scripts/spo-provision-content-types.ps1 -PlanPath plan.json -Execute -ConfirmToken PROVISION-SPO-CONTENT-TYPES"
---

# Create SharePoint Content Type

## Overview

Use this skill to execute real SharePoint Online **Create SharePoint Content Type** operations using PnP.PowerShell (\$vb\).

### Safety Contract

- **Dry-run by default**: Running without \-Execute\ outputs a structured JSON action plan detailing the operations that would occur without modifying tenant state.
- **Confirmation Gated**: Real execution requires passing \-Execute\ alongside \-ConfirmToken PROVISION-SPO-CONTENT-TYPES\.
- **Connection Resolution**: Resolves credentials interactively or from \config.psd1\ via \Get-WorkbenchConnectionConfig.ps1\.

## Usage

### 1. Preview Actions (Dry-Run)

\\\ash
pwsh -File scripts/spo-provision-content-types.ps1 -PlanPath path/to/plan.json
\\\

### 2. Execute Real Tenant Write

\\\ash
pwsh -File scripts/spo-provision-content-types.ps1 -PlanPath path/to/plan.json -Execute -ConfirmToken PROVISION-SPO-CONTENT-TYPES
\\\

## Script Reference

- \scripts/spo-provision-content-types.ps1\ — Primary PnP.PowerShell executor.
- \scripts/Get-WorkbenchConnectionConfig.ps1\ — Shared connection helper.