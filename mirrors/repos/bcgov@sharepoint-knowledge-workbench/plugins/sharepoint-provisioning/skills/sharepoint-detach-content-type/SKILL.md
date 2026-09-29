---
name: sharepoint-detach-content-type
plugin: sharepoint-provisioning
description: Detaches and unlinks a content type from a specific SharePoint list or library. Dry-run by default; real writes require -Execute and confirmation token DETACH-SPO-CONTENT-TYPE-FROM-LIST.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-detach-content-type-from-list.ps1 -PlanPath plan.json"
  - "pwsh -File scripts/spo-detach-content-type-from-list.ps1 -PlanPath plan.json -Execute -ConfirmToken DETACH-SPO-CONTENT-TYPE-FROM-LIST"
---

# Detach Content Type from List

## Overview

Use this skill to execute real SharePoint Online **Detach Content Type from List** operations using PnP.PowerShell (\$vb\).

### Safety Contract

- **Dry-run by default**: Running without \-Execute\ outputs a structured JSON action plan detailing the operations that would occur without modifying tenant state.
- **Confirmation Gated**: Real execution requires passing \-Execute\ alongside \-ConfirmToken DETACH-SPO-CONTENT-TYPE-FROM-LIST\.
- **Connection Resolution**: Resolves credentials interactively or from \config.psd1\ via \Get-WorkbenchConnectionConfig.ps1\.

## Usage

### 1. Preview Actions (Dry-Run)

\\\ash
pwsh -File scripts/spo-detach-content-type-from-list.ps1 -PlanPath path/to/plan.json
\\\

### 2. Execute Real Tenant Write

\\\ash
pwsh -File scripts/spo-detach-content-type-from-list.ps1 -PlanPath path/to/plan.json -Execute -ConfirmToken DETACH-SPO-CONTENT-TYPE-FROM-LIST
\\\

## Script Reference

- \scripts/spo-detach-content-type-from-list.ps1\ — Primary PnP.PowerShell executor.
- \scripts/Get-WorkbenchConnectionConfig.ps1\ — Shared connection helper.