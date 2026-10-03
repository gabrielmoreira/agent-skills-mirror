---
name: sharepoint-rollback-sharepoint-native-skill
plugin: sharepoint-agents-and-skills
description: Human-authorized rollback of a deployed native SharePoint skill, recycling (not permanently deleting) the target SKILL.md, dry-run by default. Use to take a deployed skill out of service recoverably.
allowed-tools: Bash, Read
---

# Rollback SharePoint Native Skill

Remove a deployed native skill's `SKILL.md` by moving it to the Recycle Bin, which is recoverable.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Dry run by default (zero tenant writes). `-Execute` additionally requires `-ConfirmExactTarget "CONFIRM-REMOVE"` (exact match); a single `-Execute` is rejected. A real run is a live tenant write that the user runs.
- Never permanent deletion: it recycles (`Move-PnPFileToRecycleBin`), never `Remove-PnPFile`. Roll back only the exact named target; no bulk or pattern removal.
- Pass `-ConfigFile` and `-ManifestFile` explicitly when installed (the manifest names the exact library, folder and filename, same shape as the deploy skill's).

## Quick start

```powershell
pwsh -File scripts/rollback-skill-deployment.ps1 -ConfigFile config.psd1 -ManifestFile deployment-manifest.json
```

## Workflow

1. Confirm the exact target in the manifest with the user.
2. Dry run and review the resolved target.
3. After explicit authorization, rerun with `-Execute -ConfirmExactTarget "CONFIRM-REMOVE"`.

## Verification

The script verifies afterward that the item is no longer in active site content. Restore from the Recycle Bin if rolled back in error.

## References

- [Safety, config and permissions](references/agents-and-skills-safety-and-config.md): read for the gate model of every script, the `-ConfigFile` default caveat and the Copilot permission note.
- [Native skill lifecycle](references/native-skill-lifecycle-details.md): read for the rollback details.
