---
name: sharepoint-restore-native-skills
plugin: sharepoint-copilot-agents-and-skills
description: Restores AgentAssets native-skill and template files from a local backup back to their tenant locations, dry-run by default with an explicit confirmation gate. Use to recover files saved by the native-skill backup skill.
allowed-tools: Bash, Read
---

# Restore SharePoint Native Skills

Restore files saved by `sharepoint-backup-native-skills` to their `AgentAssets` locations.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Dry run by default (zero tenant writes, shows exactly what would be restored). Any write needs both `-Execute` and `-ConfirmExactTarget "CONFIRM-RESTORE"`; a wrong string is rejected. A real run is a live tenant write that the user runs.
- `-Items` is a required explicit list of `{LocalPath, Url}` hashtables; a missing `LocalPath` fails before any connection. No default target list.
- When running an installed copy, pass `-ConfigFile` explicitly.

## Quick start

```powershell
pwsh -File scripts/restore-sharepoint-native-skills.ps1 -ConfigFile config.psd1 -Items @(@{LocalPath='./backup/my-skill.md'; Url='AgentAssets/Skills/my-skill/SKILL.md'})
```

## Workflow

1. Build `-Items` from the backup.
2. Dry run and review.
3. After the user confirms, rerun with `-Execute -ConfirmExactTarget "CONFIRM-RESTORE"`.

## Verification

The dry run lists exactly the items to restore; after a real run, verify with `sharepoint-verify-native-skill`.

## References

- [Safety, config and permissions](references/agents-and-skills-safety-and-config.md): read for the gate model of every script, the `-ConfigFile` default caveat and the Copilot permission note.
- [Backup and restore](references/agent-backup-restore-details.md): read for the restore parameters and the evidence-ordering bug fix.
