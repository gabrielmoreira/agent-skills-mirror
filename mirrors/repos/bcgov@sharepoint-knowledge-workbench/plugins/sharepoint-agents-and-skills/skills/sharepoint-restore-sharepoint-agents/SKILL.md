---
name: sharepoint-restore-sharepoint-agents
plugin: sharepoint-agents-and-skills
description: Restores .agent files from a local backup back to their tenant locations, dry-run by default with an explicit confirmation gate. Use to recover agents saved by the backup skill.
allowed-tools: Bash, Read
---

# Restore SharePoint Agents

Restore files saved by `sharepoint-backup-sharepoint-agents` to their tenant locations.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Dry run by default (zero tenant writes). Any write needs both `-Execute` and `-ConfirmExactTarget "CONFIRM-RESTORE"`; a single `-Execute` is rejected. A real run is a live tenant write that the user runs.
- `-Items` is a required explicit list of `{LocalPath, Url}` hashtables; it fails before any connection if a `LocalPath` does not exist. No default target list.
- Running a restored agent in the Copilot UI needs the user to be an explicit Site Owner, even if the restore succeeded.
- When running an installed copy, pass `-ConfigFile` explicitly.

## Quick start

```powershell
pwsh -File scripts/restore-sharepoint-agents.ps1 -ConfigFile config.psd1 -Items @(@{LocalPath='./backup/agent-one.agent'; Url='<server-relative url>'})
```

## Workflow

1. Build `-Items` from the backup.
2. Dry run and review what would be restored.
3. After the user confirms, rerun with `-Execute -ConfirmExactTarget "CONFIRM-RESTORE"`.

## Verification

The dry run lists exactly the items to restore; after a real run, each `.agent` is present at its `Url`.

## References

- [Safety, config and permissions](references/agents-and-skills-safety-and-config.md): read for the gate model of every script, the `-ConfigFile` default caveat and the Copilot permission note.
- [Backup and restore](references/agent-backup-restore-details.md): read for the restore parameters and tests.
