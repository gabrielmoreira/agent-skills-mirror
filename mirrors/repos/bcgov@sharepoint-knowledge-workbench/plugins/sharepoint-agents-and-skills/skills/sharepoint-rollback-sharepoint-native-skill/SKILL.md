---
name: sharepoint-rollback-sharepoint-native-skill
description: Human-authorized rollback of a deployed native SharePoint skill, recycling (not permanently deleting) the target SKILL.md, dry-run by default.
---

# rollback-sharepoint-native-skill

## Purpose

Removes a deployed native skill's `SKILL.md` from `AgentAssets/Skills/<skill-name>/` by moving it
to the SharePoint Recycle Bin (recoverable), not permanent deletion. Requires explicit,
two-part authorization before any tenant write.

## Capabilities

- **Guarded rollback** (`rollback-skill-deployment.ps1`): dry-run by default — displays the exact
  resolved target with zero tenant writes unless `-Execute` is passed. When `-Execute` is passed,
  additionally requires `-ConfirmExactTarget "CONFIRM-REMOVE"` (exact string match) before
  performing the recycle. Verifies post-action that the item no longer exists in active site
  content.

## Input boundaries

- `-ConfigFile` — connection/authentication context only.
- `-ManifestFile` — names the exact target library/folder/filename (same manifest shape as
  `deploy-sharepoint-native-skill`).
- `-Execute` + `-ConfirmExactTarget "CONFIRM-REMOVE"` — both required for any write; a single
  `-Execute` without the exact confirmation string is rejected, not treated as sufficient
  authorization.

## Prohibited scope

- Never performs permanent deletion (`Remove-PnPFile`) — always recycles
  (`Move-PnPFileToRecycleBin`), preserving recoverability.
- Does not roll back anything beyond the exact named target — no bulk or pattern-based removal.

## Scripts

- `../../scripts/rollback-skill-deployment.ps1`

