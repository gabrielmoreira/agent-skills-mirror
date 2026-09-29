---
name: sharepoint-backup-sharepoint-native-skills
description: Read-only backup of named AgentAssets native-skill/template files from a SharePoint tenant to a local directory.
---

# backup-sharepoint-native-skills

## Purpose

Downloads named `AgentAssets` skill/template files to a local directory as a precaution before
any tenant cleanup is considered. Makes no changes to the tenant. Idempotent — always writes to
the same fixed output directory and overwrites in place on every run.

## Input boundaries

- `-ConfigFile` — connection/authentication context only.
- `-Items` (required) — explicit list of `{Url, Dest}` hashtables. No hardcoded target list —
  the caller supplies exactly what to back up.
- `-OutputDir` — local destination directory.
- **Read-only** — no tenant write of any kind.

## Scripts

- `../../scripts/backup-sharepoint-native-skills.ps1`

## Related

- `restore-sharepoint-native-skills` — the corresponding restore skill, consumes the same
  `{Url, Dest}`/`{LocalPath, Url}` shape.

