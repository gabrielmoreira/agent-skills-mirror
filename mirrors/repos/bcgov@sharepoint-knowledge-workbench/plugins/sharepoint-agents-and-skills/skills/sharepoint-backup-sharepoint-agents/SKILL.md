---
name: sharepoint-backup-sharepoint-agents
plugin: sharepoint-agents-and-skills
description: Read-only backup of named .agent files from a SharePoint site to a local directory. Use as a precaution before any tenant cleanup or agent change. Makes no tenant changes.
allowed-tools: Bash, Read
---

# Backup SharePoint Agents

Download named `.agent` files to a local directory. Idempotent: it always writes to the same output directory and overwrites in place.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Read-only: no tenant write of any kind.
- `-SitePath` and `-AgentFileNames` are required. There is no hardcoded default list; the caller names exactly what to back up.
- `-ConfigFile` carries connection context only. When running an installed copy, pass it explicitly.

## Quick start

```powershell
pwsh -File scripts/backup-sharepoint-agents.ps1 -ConfigFile config.psd1 -SitePath "<site-relative folder>" -AgentFileNames @('agent-one.agent') -OutputDir ./backup
```

## Workflow

1. Confirm the site-relative folder and the exact `.agent` file names.
2. Run the script with `-OutputDir`.
3. Keep the backup for `sharepoint-restore-sharepoint-agents`.

## Verification

Every named file exists in `-OutputDir`. A missing file is reported, not skipped.

## References

- [Safety, config and permissions](references/agents-and-skills-safety-and-config.md): read for the gate model of every script, the `-ConfigFile` default caveat and the Copilot permission note.
- [Backup and restore](references/agent-backup-restore-details.md): read for the backup parameters and the matching restore.
