---
name: sharepoint-create-document-library
plugin: sharepoint-provisioning
description: Creates a new SharePoint document library (Template 101) using PnP.PowerShell. Dry-run by default; real writes require -Execute and confirmation token PROVISION-SPO-LIST.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-provision-list.ps1 -PlanPath plan.json"
  - "pwsh -File scripts/spo-provision-list.ps1 -PlanPath plan.json -Execute -ConfirmToken PROVISION-SPO-LIST"
---

# Create SharePoint Document Library

## Overview

Use this skill to execute real SharePoint Online **Create SharePoint Document Library** operations using PnP.PowerShell (\$vb\).

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