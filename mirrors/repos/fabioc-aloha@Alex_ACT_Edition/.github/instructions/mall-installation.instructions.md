---
description: "How heirs install plugins from the Alex ACT Plugin Mall into local/ paths so Edition upgrades don't clobber them"
applyTo: "**/.github/skills/local/**,**/.github/instructions/local/**,**/.github/scripts/local/**,**/.github/prompts/local/**,**/.github/agents/local/**,**/.mcp.json,**/mcp.json,**/.vscode/mcp.json"
lastReviewed: 2026-07-28
---

# Mall Installation

The [Alex ACT Plugin Mall](https://github.com/fabioc-aloha/Alex_Skill_Mall) (canonical repo name `Alex_Skill_Mall`) is a curated catalog of optional plugins. This file is the source of truth for legacy heir install, refresh, and removal behavior.

## Scope and source resolution

1. Resolve plugin metadata from `catalog/index.json` and a selected catalog entry's `source_url`.
2. The install source must be either:
   - a `source_url` pinned to a SHA or tag, or
   - a sibling Mall clone path that resolves to the same plugin root.
3. Do not use unpinned floating source paths for installation decisions.

## Allowed targets and protections

### Allowed heir-local targets

- `.github/skills/local/**`
- `.github/instructions/local/**`
- `.github/prompts/local/**`
- `.github/agents/local/**`
- `.github/scripts/local/**`
- workspace-root `.mcp.json`

### Non-negotiable safeguards

1. Before writes, inventory source components and build a write plan.
2. Validate every source path stays under the plugin root.
3. Validate every target path stays under allowed heir-local roots.
4. Show the plan and obtain explicit user approval.
5. Refuse unsupported components before any write.
6. On failure, restore `.mcp.json` from backup if changed and remove only paths created during this attempt.
7. Never delete pre-existing or user-owned content.

## Version detection

Detect layout before mapping:

- **Mall 3** when `.mall-metadata.json` exists, or nested component directories exist (`skills/`, `agents/`, `commands/`, `hooks/`, `extensions/`, `lspServers/`).
- **Mall 2 fallback** when root `SKILL.md` or root artifact files (`*.instructions.md`, `*.prompt.md`, `*.agent.md`) represent the plugin bundle.

## Mapping contract

### Mall 3 mapping (primary)

1. Recursively copy each `skills/<skill-name>/` directory to `.github/skills/local/<skill-name>/`.
2. Copy `agents/*.agent.md` to `.github/agents/local/`.
3. Process `commands/*.md` only as prompt candidates:
   - convert to `.github/prompts/local/<name>.prompt.md` only when YAML frontmatter keys are prompt-compatible (`description` and optional `lastReviewed` only),
   - otherwise classify as CLI-only and do not install as prompt.
4. Merge `plugin.json#mcpServers` additively into workspace-root `.mcp.json` using parsed JSON:
   - preserve unrelated existing servers,
   - write byte-valid backup `.mcp.json.bak` before write.
5. `hooks`, `extensions`, `lspServers`, and unknown components are unsupported in legacy mode. Refuse installation before any write. Do not claim partial success.

### Mall 2 fallback mapping (transition)

Use only when Mall 3 markers are absent.

1. Map root `SKILL.md` bundle to `.github/skills/local/<plugin-name>/`.
2. Map root prompt, instruction, agent, and script artifacts to established local destinations:
   - `*.instructions.md` -> `.github/instructions/local/`
   - `*.prompt.md` -> `.github/prompts/local/`
   - `*.agent.md` -> `.github/agents/local/`
   - `scripts/*` -> `.github/scripts/local/`

This is a compatibility fallback, not the Mall 3 layout.

## Install manifest requirement

Every successful install writes `.github/skills/local/<plugin-name>/.install.json`, including agent-only and multi-skill plugins.

- A metadata-only directory without `SKILL.md` is valid.
- Required fields:
  - `plugin`
  - `store`
  - `source_url`
  - `version_at_install`
  - `installed_at`
  - `mall_major` (2 or 3)
  - `component_paths` (exact workspace-relative created or updated files/directories)
- Optional fields may include `trust_score_at_install` and `frontmatter_at_install`.

Do not report success unless all planned supported components and `.install.json` are written and verified.

## Refresh and removal contract

1. Refresh uses the same version-aware mapping and rewrites `component_paths` only after successful verification.
2. Removal deletes only recorded `component_paths` and requires explicit consent.
3. If `component_paths` is absent or malformed, require manual review. Do not guess delete targets.

## Post-install verification (required)

1. Every recorded path in `component_paths` exists.
2. Each installed skill folder name matches `name` frontmatter in `SKILL.md` when present.
3. Prompt and agent discovery roots are configured for local paths.
4. Parsed `.mcp.json` preserves prior servers and includes newly merged servers.
5. Re-run drift audit:

```bash
node .github/scripts/audit-mall-drift.cjs
```

## Related prompts

- `/mall-install` executes this workflow.
- `/mall-refresh` applies this same mapping contract for upgrades/removals.
- `/mall-search` and `/mall-show` are the discovery and trust-report inputs.

## Would Revise If

Revisit by **2026-10-28** if any trigger fires:

1. Two distinct Mall 3 shape failures.
2. One `component_paths` deletion of user-owned or unrecorded path.
3. Mall 2 fallback break.
4. Any assumption in docs or rollout communication that 3.x heirs are protected without upgrade.
