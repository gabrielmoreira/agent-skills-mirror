---
name: sharepoint-deploy-sharepoint-native-skill
plugin: sharepoint-agents-and-skills
description: Deploys a native SharePoint SKILL.md to a tenant's AgentAssets library with SHA-256 readback verification, dry-run by default. Use to publish an already-built skill. Also inventories what is deployed.
allowed-tools: Bash, Read
---

# Deploy SharePoint Native Skill

Deploy a repository-authored `SKILL.md` to `AgentAssets/Skills/<skill-name>/SKILL.md` and confirm a byte-for-byte hash match.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Dry run by default: without `-Execute` it computes the target and writes nothing. `-Execute` is a live tenant write that the user runs.
- It does not create the `AgentAssets` library or `Skills/` folder; it fails closed if they are missing (use `sharepoint-inventory-and-validate-agentassets`).
- It deploys a built skill; it does not author or validate content (`sharepoint-create-sharepoint-native-skill`).
- Pass `-ConfigFile` and `-ManifestFile` explicitly: both defaults are repo-root-relative and do not resolve when installed.

## Quick start

```powershell
pwsh -File scripts/deploy-and-verify-skill.ps1 -ConfigFile config.psd1 -ManifestFile deployment-manifest.json
```

## Workflow

1. Prepare the manifest (skill name, repository source path, target library, folder, filename).
2. Run the preflight above and review the resolved target with the user.
3. After the user confirms, rerun with `-Execute`. It uploads, downloads back and compares SHA-256.
4. Use `scripts/inventory-skills.ps1` (read-only) to confirm what is deployed.

## Verification

A 100% SHA-256 match; a mismatch fails loudly. Confirm with `sharepoint-verify-sharepoint-native-skill`.

## References

- [Safety, config and permissions](references/agents-and-skills-safety-and-config.md): read for the gate model of every script, the `-ConfigFile` default caveat and the Copilot permission note.
- [Native skill lifecycle](references/native-skill-lifecycle-details.md): read for the deploy and inventory behavior and the manifest.
