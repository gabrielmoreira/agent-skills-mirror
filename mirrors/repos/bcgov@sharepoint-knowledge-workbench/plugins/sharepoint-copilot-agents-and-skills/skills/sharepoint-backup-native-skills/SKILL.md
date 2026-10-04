---
name: sharepoint-backup-native-skills
plugin: sharepoint-copilot-agents-and-skills
description: Read-only backup of named AgentAssets native-skill and template files from a SharePoint tenant to a local directory. Use as a precaution before tenant cleanup or a redeploy. Makes no tenant changes.
allowed-tools: Bash, Read
---

# Backup SharePoint Native Skills

Download named `AgentAssets` skill and template files to a local directory. Idempotent: same output directory, overwritten in place.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Read-only: no tenant write of any kind.
- `-Items` is a required explicit list of `{Url, Dest}` hashtables. No hardcoded target list.
- `-ConfigFile` carries connection context only. When running an installed copy, pass it explicitly.

## Quick start

```powershell
pwsh -File scripts/backup-sharepoint-native-skills.ps1 -ConfigFile config.psd1 -Items @(@{Url='AgentAssets/Skills/my-skill/SKILL.md'; Dest='my-skill.md'}) -OutputDir ./backup
```

## Workflow

1. Confirm the exact `Url` and local `Dest` for each file.
2. Run the script with `-OutputDir`.
3. Keep the backup for `sharepoint-restore-native-skills`, which consumes the same shape.

## Verification

Every listed file exists locally under `-OutputDir`.

## References

- [Safety, config and permissions](references/agents-and-skills-safety-and-config.md): read for the gate model of every script, the `-ConfigFile` default caveat and the Copilot permission note.
- [Backup and restore](references/agent-backup-restore-details.md): read for the backup parameters and the matching restore.
