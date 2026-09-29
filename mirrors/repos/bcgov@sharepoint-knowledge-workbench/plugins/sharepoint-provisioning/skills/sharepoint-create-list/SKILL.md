---
name: sharepoint-create-list
plugin: sharepoint-provisioning
description: Creates a new SharePoint custom list (Template 100) using PnP.PowerShell. Dry-run by default; real writes require -Execute and confirmation token PROVISION-SPO-LIST.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-provision-list.ps1 -PlanPath plan.json"
  - "pwsh -File scripts/spo-provision-list.ps1 -PlanPath plan.json -Execute -ConfirmToken PROVISION-SPO-LIST"
---

# Create SharePoint List

## Overview

Use this skill to execute real SharePoint Online **Create SharePoint List** operations using PnP.PowerShell (\$vb\).

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

\\\ ash
pwsh -File scripts/spo-provision-list.ps1 -PlanPath path/to/plan.json -Execute -ConfirmToken PROVISION-SPO-LIST
\\\

## Script Reference

- `scripts/spo-provision-list.ps1` — Primary PnP.PowerShell executor.
- `scripts/Get-WorkbenchConnectionConfig.ps1` — Shared connection helper.

## Architectural Best Practice: The Default `Title` Column Rule
When provisioning custom join tables, lookup mappings, or user preference lists (like `My Favourite Apps`):
- Standard generic lists automatically create a default `Title` column set to `Required = $true`.
- Always explicitly set `$titleField.Required = $false` on join lists during provisioning so that REST API writes from client-side web parts are never rejected if `Title` is omitted or empty.