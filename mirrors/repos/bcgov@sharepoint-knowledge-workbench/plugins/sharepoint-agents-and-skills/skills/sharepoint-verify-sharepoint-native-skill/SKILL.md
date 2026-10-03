---
name: sharepoint-verify-sharepoint-native-skill
plugin: sharepoint-agents-and-skills
description: Read-only reconciliation of a deployed native SharePoint skill's SKILL.md against its repository source by exact SHA-256 comparison. Use to check whether a deployment happened and whether it has drifted.
allowed-tools: Bash, Read
---

# Verify SharePoint Native Skill

Verify that the `SKILL.md` deployed to `AgentAssets/Skills/<skill-name>/` matches its repository source exactly.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Read-only: no upload, overwrite or delete.
- Claim nothing beyond a SHA-256 comparison of the exact bytes retrieved: nothing about canonical package identity or structural-anchor completeness.
- `-TargetSkillName` and `-RepoSkillPath` are explicit; there is no hardcoded target. When running an installed copy, pass `-ConfigFile`.

## Quick start

```powershell
pwsh -File scripts/verify-agentassets-artifact.ps1 -ConfigFile config.psd1 -TargetSkillName my-skill -RepoSkillPath ./my-skill/SKILL.md
```

## Workflow

1. Run `verify-agentassets-artifact.ps1` for the disposition.
2. For frontmatter alongside the hash, run `reconcile-deployed-skill.ps1` (expected hash computed from `-RepoSkillPath`).
3. Report the disposition and any drift.

## Verification

The disposition is `ARTIFACT_ALREADY_PRESENT` (match), `DEPLOYED_ARTIFACT_DRIFT_DETECTED` (mismatch) or `DEPLOYMENT_CANDIDATE_NOT_YET_PRESENT`.

## References

- [Safety, config and permissions](references/agents-and-skills-safety-and-config.md): read for the gate model of every script, the `-ConfigFile` default caveat and the Copilot permission note.
- [Native skill lifecycle](references/native-skill-lifecycle-details.md): read for both scripts and the dispositions.
