---
name: sharepoint-configure-library-settings
plugin: sharepoint-provisioning
description: Configures advanced SharePoint document library version limits, content approval, and draft visibility settings. Dry-run by default; real writes require -Execute and confirmation token CONFIGURE-SPO-LIBRARY-SETTINGS.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-configure-library-settings.ps1 -PlanPath plan.json"
  - "pwsh -File scripts/spo-configure-library-settings.ps1 -PlanPath plan.json -Execute -ConfirmToken CONFIGURE-SPO-LIBRARY-SETTINGS"
---

# Configure SharePoint Library Settings

## Overview

Use this skill to execute real SharePoint Online **Configure SharePoint Library Settings** operations using PnP.PowerShell (\$vb\).

### Safety Contract

- **Dry-run by default**: Running without \-Execute\ outputs a structured JSON action plan detailing the operations that would occur without modifying tenant state.
- **Confirmation Gated**: Real execution requires passing \-Execute\ alongside \-ConfirmToken CONFIGURE-SPO-LIBRARY-SETTINGS\.
- **Connection Resolution**: Resolves credentials interactively or from \config.psd1\ via \Get-WorkbenchConnectionConfig.ps1\.

## Usage

### 1. Preview Actions (Dry-Run)

\\\ash
pwsh -File scripts/spo-configure-library-settings.ps1 -PlanPath path/to/plan.json
\\\

### 2. Execute Real Tenant Write

\\\ash
pwsh -File scripts/spo-configure-library-settings.ps1 -PlanPath path/to/plan.json -Execute -ConfirmToken CONFIGURE-SPO-LIBRARY-SETTINGS
\\\

## Script Reference

- \scripts/spo-configure-library-settings.ps1\ — Primary PnP.PowerShell executor.
- \scripts/Get-WorkbenchConnectionConfig.ps1\ — Shared connection helper.