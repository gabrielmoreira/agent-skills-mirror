---
name: sharepoint-configure-column-formatting
plugin: sharepoint-provisioning
description: Applies JSON custom column formatting and custom renderers to SharePoint fields. Dry-run by default; real writes require -Execute and confirmation token CONFIGURE-SPO-COLUMN-FORMATTING.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-configure-column-formatting.ps1 -PlanPath plan.json"
  - "pwsh -File scripts/spo-configure-column-formatting.ps1 -PlanPath plan.json -Execute -ConfirmToken CONFIGURE-SPO-COLUMN-FORMATTING"
---

# Configure SharePoint Column Formatting

## Overview

Use this skill to execute real SharePoint Online **Configure SharePoint Column Formatting** operations using PnP.PowerShell (\$vb\).

### Safety Contract

- **Dry-run by default**: Running without \-Execute\ outputs a structured JSON action plan detailing the operations that would occur without modifying tenant state.
- **Confirmation Gated**: Real execution requires passing \-Execute\ alongside \-ConfirmToken CONFIGURE-SPO-COLUMN-FORMATTING\.
- **Connection Resolution**: Resolves credentials interactively or from \config.psd1\ via \Get-WorkbenchConnectionConfig.ps1\.

## Usage

### 1. Preview Actions (Dry-Run)

\\\ash
pwsh -File scripts/spo-configure-column-formatting.ps1 -PlanPath path/to/plan.json
\\\

### 2. Execute Real Tenant Write

\\\ash
pwsh -File scripts/spo-configure-column-formatting.ps1 -PlanPath path/to/plan.json -Execute -ConfirmToken CONFIGURE-SPO-COLUMN-FORMATTING
\\\

## Script Reference

- \scripts/spo-configure-column-formatting.ps1\ — Primary PnP.PowerShell executor.
- \scripts/Get-WorkbenchConnectionConfig.ps1\ — Shared connection helper.