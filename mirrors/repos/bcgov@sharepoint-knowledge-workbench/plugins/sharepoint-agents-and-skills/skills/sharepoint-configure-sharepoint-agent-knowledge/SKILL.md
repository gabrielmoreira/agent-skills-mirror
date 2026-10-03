---
name: sharepoint-configure-sharepoint-agent-knowledge
plugin: sharepoint-agents-and-skills
description: Read-only report of a deployed SharePoint agent's current knowledge-source bindings, plus resolution of the exact site_id, web_id, list_id and unique_id a new binding needs. Use to inspect what an agent is grounded on or to get correct identifiers for site isolation.
allowed-tools: Bash, Read
---

# Configure SharePoint Agent Knowledge

Two read-only capabilities: inspect a deployed agent's bindings, and resolve the resource identifiers a new binding needs.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Read-only: neither script performs a tenant write.
- Targets are explicit (`-AgentPath`, `-FolderSiteRelativePath`); there is no default.
- This inspects a deployed agent; editing a local package is `sharepoint-update-sharepoint-agent`.
- When running an installed copy, pass `-ConfigFile` explicitly.

## Quick start

```powershell
pwsh -File scripts/get-agent-resource-identifiers.ps1 -ConfigFile config.psd1 -FolderSiteRelativePath "<site-relative folder>"
```

## Workflow

1. To inspect an agent: `configure-sharepoint-agent-knowledge.ps1 -ConfigFile ... -AgentPath ...`.
2. To bind a new source: `get-agent-resource-identifiers.ps1` for the folder, then use its `site_id`, `web_id`, `list_id` and `unique_id` in the agent's `items_by_url`.
3. Report the bindings or identifiers with the exact values returned.

## Verification

Identifiers are non-empty and match the live resource; a folder gets its real `unique_id`, never another folder's GUID or the zero GUID (zeros only for a top-level library). There are no executable tests (a pure read has no dry-run mode).

## References

- [Safety, config and permissions](references/agents-and-skills-safety-and-config.md): read for the gate model of every script, the `-ConfigFile` default caveat and the Copilot permission note.
- [Knowledge binding details](references/agent-knowledge-binding-details.md): read for the two capabilities and the Phase 6 plan correction.
- [Agent package authoring](references/agent-package-authoring-details.md): read for `items_by_url` identifier rules.
