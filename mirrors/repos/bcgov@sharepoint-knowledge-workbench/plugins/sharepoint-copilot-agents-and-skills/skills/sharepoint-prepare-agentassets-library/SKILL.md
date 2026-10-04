---
name: sharepoint-prepare-agentassets-library
plugin: sharepoint-copilot-agents-and-skills
description: Inspects and validates the readiness of a SharePoint site's AgentAssets document library and its Skills subfolder (read-only checks), and provisions them only when explicitly requested -- the provisioning script is write-capable and has no dry-run gate -- before native-skill deployment. Use before deploying a native skill, or to troubleshoot library names and IDs.
allowed-tools: Bash, Read
---

# Inventory and Validate AgentAssets

Inspect a site's `AgentAssets` library, the library Copilot in SharePoint reads native `SKILL.md` definitions from, and provision it only when explicitly asked.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- `scripts/provision-agentassets.ps1` is the only write-capable script and has no dry-run gate: it creates the library and `Skills/` folder immediately. Run it only when explicitly requested, and the user runs it.
- `verify-agentassets-ready.ps1` and `diagnose-sharepoint-library.ps1` are strictly read-only and must never create the library as a side effect.
- Every target is an explicit parameter; a config with placeholder credentials fails closed. Pass `-ConfigFile` (`-ConfigPath` for the provision script) when installed.
- Do not deploy or verify a specific skill's content here.

## Quick start

```powershell
pwsh -File scripts/verify-agentassets-ready.ps1 -ConfigFile config.psd1
```

## Workflow

1. Run the readiness check; it reports `READY` or `BLOCKED` and lists existing `SKILL.md` files.
2. If blocked and provisioning is requested, run `provision-agentassets.ps1` (optionally `-SkillName` with `-SkillSourcePath` to upload one sample skill).
3. For library names or IDs, run `diagnose-sharepoint-library.ps1` (with `-LibraryName` for detail).

## Verification

Status is `READY`; provisioning reports what it created or found existing, with an optional JSON export (`-JsonOutputPath`).

## References

- [Safety, config and permissions](references/agents-and-skills-safety-and-config.md): read for the gate model of every script, the `-ConfigFile` default caveat and the Copilot permission note.
- [Native skill lifecycle](references/native-skill-lifecycle-details.md): read for the three capabilities and their outputs.
