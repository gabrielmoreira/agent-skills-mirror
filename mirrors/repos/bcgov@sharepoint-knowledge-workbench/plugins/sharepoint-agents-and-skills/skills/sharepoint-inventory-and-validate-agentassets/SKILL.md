---
name: sharepoint-inventory-and-validate-agentassets
description: Provisions, inspects, and validates readiness of a SharePoint site's AgentAssets document library and its Skills subfolder before native-skill deployment.
---

# inventory-and-validate-agentassets

## Purpose

Read-only (and, only when explicitly requested, provisioning) inspection of a SharePoint site's
`AgentAssets` document library — the library Copilot in SharePoint reads native `SKILL.md`
definitions from. Confirms the library and its `Skills/` subfolder exist and are accessible
before any `deploy-sharepoint-native-skill` invocation is attempted.

## Capabilities

- **Provision** (`provision-agentassets.ps1`): create `AgentAssets` as a document library and its
  `Skills/` subfolder if they don't exist yet. Optionally uploads one named sample skill when both
  `-SkillName` and `-SkillSourcePath` are supplied — does nothing skill-specific otherwise.
- **Readiness check** (`verify-agentassets-ready.ps1`): confirms `AgentAssets`/`Skills/` exist and
  are accessible, inventories existing `SKILL.md` files, reports a `READY`/`BLOCKED` status.
- **Library diagnostic** (`diagnose-sharepoint-library.ps1`): read-only inspection of any library
  on the site (not just `AgentAssets`) — lists libraries, or inspects one in detail (items,
  fields/columns). Useful for troubleshooting library names/IDs before pointing other skills at
  them.

## Input boundaries

- `-ConfigFile` (all scripts) — connection/authentication context only (`SiteUrl`, `ClientId`,
  `TenantId`). No fallback to another phase's config file — fails closed with an explicit error if
  the supplied config has placeholder credentials, per this plugin's parameterization standard.
- Provisioning (`provision-agentassets.ps1`) is the only write-capable capability here — the
  readiness check and diagnostic are strictly read-only.
- No hardcoded tenant, site, library, or skill names in any of the three scripts — every target is
  an explicit parameter.

## Prohibited scope

- Do not deploy or verify a specific native skill's content here — that's
  `deploy-sharepoint-native-skill`/`verify-sharepoint-native-skill`'s responsibility.
- Do not create the `AgentAssets` library as a side effect of a read-only readiness check or
  diagnostic call — only `provision-agentassets.ps1`, invoked explicitly, writes anything.

## Scripts

- `../../scripts/provision-agentassets.ps1`
- `../../scripts/verify-agentassets-ready.ps1`
- `../../scripts/diagnose-sharepoint-library.ps1`

(Referenced directly from the plugin root — see `review-manual-topics/SKILL.md`'s note on why
these are not yet managed file-level symlinks: `symlink_manager.py` does not exist in this
repository.)

## Output

- Provisioning: confirmation of what was created/already existed, plus an optional JSON inventory
  export (`-JsonOutputPath`).
- Readiness check: `READY` or `BLOCKED` status, plus the list of existing `SKILL.md` files found.
- Diagnostic: library metadata (title, URL, ID, item count, fields) or, with no `-LibraryName`,
  a list of every library on the site.

