---
name: sharepoint-restore-sharepoint-native-skills
description: Restores AgentAssets native-skill/template files from a local backup back to their tenant locations, dry-run by default with an explicit confirmation gate.
---

# restore-sharepoint-native-skills

## Purpose

Restores files previously saved by `backup-sharepoint-native-skills` back to their `AgentAssets`
tenant locations. New build — no prior implementation existed in this repository.

## Input boundaries

- `-ConfigFile` — connection/authentication context only.
- `-Items` (required) — explicit list of `{LocalPath, Url}` hashtables. Fails before any
  connection attempt if any `LocalPath` doesn't exist.
- `-Execute` + `-ConfirmExactTarget "CONFIRM-RESTORE"` — both required for any write; dry-run by
  default (zero tenant writes, displays exactly what would be restored).

## Prohibited scope

- No default target list — every restore target is explicit.
- No write without exact two-part confirmation, matching
  `rollback-sharepoint-native-skill`'s safety-gate pattern.

## Scripts

- `../../scripts/restore-sharepoint-native-skills.ps1`

## Tests

`../../tests/unit/test_restore_sharepoint_native_skills.py` — 4 executable tests via `pwsh`
(dry-run performs zero writes, missing confirmation is rejected, wrong confirmation string is
rejected, missing local backup file fails before any tenant connection is attempted).

**Real bug found and fixed while writing these tests:** the original implementation wrote its
`-JsonOutputPath` evidence *after* calling `Write-Error`, which is a terminating statement under
`$ErrorActionPreference = "Stop"` — the JSON write was dead code. Fixed here, and the same
pre-existing bug was found and fixed in `rollback-sharepoint-native-skill`'s
`rollback-skill-deployment.ps1` too (same copied pattern, same defect).

