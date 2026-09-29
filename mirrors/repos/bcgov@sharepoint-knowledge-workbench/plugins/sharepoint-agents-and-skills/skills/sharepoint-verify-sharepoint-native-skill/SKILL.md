---
name: sharepoint-verify-sharepoint-native-skill
description: Read-only reconciliation of a deployed native SharePoint skill's SKILL.md against its repository source, by exact SHA-256 comparison.
---

# verify-sharepoint-native-skill

## Purpose

Read-only verification that a native skill deployed to `AgentAssets/Skills/<skill-name>/SKILL.md`
on a tenant matches its repository source exactly — no upload, overwrite, or delete. Distinct
from `deploy-sharepoint-native-skill`, which performs the deployment itself; this skill only
checks whether a deployment already happened and, if so, whether it drifted.

## Capabilities

- **Artifact verification** (`verify-agentassets-artifact.ps1`): lists everything in
  `AgentAssets/Skills/`, downloads and hashes any `SKILL.md` found, compares each against a named
  repository source (`-TargetSkillName`/`-RepoSkillPath`), and reports a disposition:
  `ARTIFACT_ALREADY_PRESENT` (hash match), `DEPLOYED_ARTIFACT_DRIFT_DETECTED` (hash mismatch), or
  `DEPLOYMENT_CANDIDATE_NOT_YET_PRESENT` (nothing deployed under that name yet).
- **Deployment reconciliation** (`reconcile-deployed-skill.ps1`, extracted/generalized from the
  historical `task-8a-reconcile-deployed-skill.ps1`): same read-only reconciliation, computing the
  expected SHA-256 from a live local file (`-RepoSkillPath`) rather than a hardcoded hash, and
  reporting frontmatter (`name`/`description`) alongside the hash comparison.

## Input boundaries

- `-ConfigFile` — connection/authentication context only.
- `-TargetSkillName` — the skill folder name to check (no hardcoded default target).
- `-RepoSkillPath` — the repository source `SKILL.md` to compare against.
- **Read-only** — neither script performs any tenant write.

## Prohibited scope

- No hash-recalculation claims beyond SHA-256 comparison of the exact bytes retrieved — no
  claims about canonical package identity or structural-anchor completeness.
- Does not deploy, roll back, or modify anything — pure read-only reconciliation.

## Scripts

- `../../scripts/verify-agentassets-artifact.ps1`
- `../../scripts/reconcile-deployed-skill.ps1`

