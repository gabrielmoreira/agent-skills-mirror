---
name: sharepoint-restore-sharepoint-agents
description: Restores .agent files from a local backup back to their tenant locations, dry-run by default with an explicit confirmation gate.
---

# restore-sharepoint-agents

## Purpose

Restores files previously saved by `backup-sharepoint-agents` back to their tenant locations.
New build — no prior implementation existed in this repository.

## Input boundaries

- `-ConfigFile` — connection/authentication context only.
- `-Items` (required) — explicit list of `{LocalPath, Url}` hashtables. Fails before any
  connection attempt if any `LocalPath` doesn't exist.
- `-Execute` + `-ConfirmExactTarget "CONFIRM-RESTORE"` — both required for any write; dry-run by
  default.

## Prohibited scope

- No default target list.
- No write without exact two-part confirmation, matching `rollback-sharepoint-native-skill`'s
  and `restore-sharepoint-native-skills`'s safety-gate pattern.

## Troubleshooting & Permissions Note

> [!IMPORTANT]
> **SharePoint Copilot UI Permissions**:
> Even if PnP PowerShell restores and writes the `.agent` file successfully using Site Collection Admin credentials, running/launching the `.agent` inside SharePoint Copilot UI requires the user to be an explicit member of the **Site Owners** group. Without explicit Site Owner permissions, the Copilot panel will fail with *"Something went wrong with this agent. Please try again later or select a different agent"*.

## Scripts

- `../../scripts/restore-sharepoint-agents.ps1`

## Tests

`../../tests/unit/test_restore_sharepoint_agents.py` — 3 executable tests via `pwsh` (dry-run
performs zero writes, missing-confirmation rejection writes evidence before failing, missing
local backup file fails before any tenant connection is attempted). Written with the
evidence-before-`Write-Error` ordering fix already applied (see `restore-sharepoint-native-
skills`'s SKILL.md for the bug this avoids).

