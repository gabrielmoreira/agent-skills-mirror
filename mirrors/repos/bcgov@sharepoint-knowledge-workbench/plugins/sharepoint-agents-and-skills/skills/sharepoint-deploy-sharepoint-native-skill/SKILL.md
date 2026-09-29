---
name: sharepoint-deploy-sharepoint-native-skill
description: Deploys a native SharePoint SKILL.md to a tenant's AgentAssets library with SHA-256 readback verification, dry-run by default.
---

# deploy-sharepoint-native-skill

## Purpose

Deploys a repository-authored native SharePoint skill's `SKILL.md` to
`AgentAssets/Skills/<skill-name>/SKILL.md` on a target tenant, with byte-for-byte SHA-256
readback verification. Distinct from `create-sharepoint-native-skill`: this skill deploys an
already-built skill package, it does not author one.

## Capabilities

- **Deploy + verify** (`deploy-and-verify-skill.ps1`): dry-run by default (zero tenant writes
  unless `-Execute` is explicitly passed). Reads a deployment manifest (skill name, repository
  source path, target library/folder/filename), computes the local file's SHA-256, uploads it,
  downloads it back, and confirms a 100% hash match. Fails loudly on mismatch.
- **Native-skill inventory** (`inventory-skills.ps1`): read-only inventory of deployed `SKILL.md`
  assets and (site-pages-hosted) knowledge content on a target site, for confirming what's already
  deployed before/after a deployment.

## Input boundaries

- `-ConfigFile` — connection/authentication context only.
- `-ManifestFile` — a JSON manifest naming the skill, its repository source path, and its exact
  target library/folder/filename (see `deployment-manifest.example.json` at the plugin root).
- `-Execute` — required to perform any tenant write; omitted by default (preflight-only mode,
  displays the exact resolved target with zero writes).

## Prohibited scope

- Does not create the `AgentAssets` library or `Skills/` folder if missing — that's
  `inventory-and-validate-agentassets`'s `provision-agentassets.ps1` responsibility. This skill
  fails closed (does not create the library) if the target doesn't exist.
- Does not author or validate a skill's content — that's `create-sharepoint-native-skill`'s
  responsibility.

## Scripts

- `../../scripts/deploy-and-verify-skill.ps1`
- `../../scripts/inventory-skills.ps1`

