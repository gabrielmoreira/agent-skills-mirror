---
name: create-plugin
description: Scaffold a new Claude Code plugin with proper directory structure, plugin.json, skills, commands, and agents
argument-hint: "<plugin-name>"
allowed-tools: mcp__claude-flow__transfer_plugin-info mcp__claude-flow__transfer_plugin-search mcp__claude-flow__transfer_store-search Bash Read Write Edit
---

# Create Plugin

Scaffold a new Claude Code plugin from scratch.

## When to use

When you want to create a new plugin that extends Claude Code with skills, commands, and agents. This generates the correct directory structure and wires up MCP tools.

## Steps

1. **Get plugin name and description** from the user
2. **Check for conflicts** — call `mcp__claude-flow__transfer_plugin-search` to ensure the name isn't taken
3. **Create directory structure** (follows the canonical plugin contract from sibling plugins' ADR-0001s):
   ```
   plugins/<name>/
   ├── .claude-plugin/
   │   └── plugin.json
   ├── skills/
   │   └── <skill-name>/
   │       └── SKILL.md
   ├── commands/
   │   └── <command-name>.md
   ├── agents/
   │   └── <agent-name>.md
   ├── docs/
   │   └── adrs/
   │       └── 0001-<name>-contract.md     # Plugin-level ADR (Proposed)
   ├── scripts/
   │   └── smoke.sh                         # Structural contract (10+ checks)
   └── README.md                            # Compatibility + Namespace coordination + Verification + ADR sections
   ```
4. **Generate plugin.json** with name, description, version, author (do NOT include `skills`, `commands`, or `agents` arrays — Claude Code auto-discovers these from directory structure)
5. **Generate SKILL.md files** with proper frontmatter:
   ```yaml
   ---
   name: skill-name
   description: What this skill does
   allowed-tools: mcp__claude-flow__tool1 mcp__claude-flow__tool2 Bash
   ---
   ```
6. **Generate command files** with name and description frontmatter
7. **Generate agent files** with name, description, and `model: sonnet`
8. **Generate README.md** with install instructions, features, commands, skills, AND the canonical plugin-contract sections:
   - **Compatibility** — pin to `@claude-flow/cli` v3.6 major+minor
   - **Namespace coordination** — claim a kebab-case `<plugin-stem>-<intent>` namespace; defer to ruflo-agentdb ADR-0001 §"Namespace convention"
   - **Verification** — `bash plugins/<name>/scripts/smoke.sh`
   - **Architecture Decisions** — link to ADR-0001
9. **Generate ADR-0001 (Proposed)** at `docs/adrs/0001-<name>-contract.md` documenting: pinning, namespace coordination, MCP-tool surface count if applicable, smoke contract scope. Status: `Proposed`.
10. **Generate scripts/smoke.sh** — at minimum 8 structural checks: version + keywords; skills/agents/commands present with valid frontmatter; v3.6 pin in README; namespace coordination block in README; ADR exists with status `Proposed`; no wildcard tools in skills.
11. **Update marketplace.json** if adding to the ruflo marketplace.

## MCP-tool drift to avoid (per sibling-ADR lessons learned)

Several plugins shipped with subtle MCP bugs the loop has been finding. Don't replicate them:

- **`embeddings_embed` does not exist.** Real tool is `embeddings_generate`. Don't reference `embeddings_embed` in any `allowed-tools` line.
- **`agentdb_hierarchical-*` does NOT route by namespace.** It routes by tier (`working|episodic|semantic`). Pass `tier`, not `namespace`. For namespaced reads/writes, use `memory_*` instead.
- **`agentdb_pattern-*` does NOT route by namespace.** It routes through ReasoningBank. Don't pass a `namespace` arg — fallback writes to the reserved `pattern` namespace via `memory-store-fallback`.
- **`pattern` (singular) and `patterns` (plural) are different namespaces.** ReasoningBank fallback writes to `pattern`; `hooks_pretrain` writes to `patterns`. Don't conflate them.

## Plugin.json schema

Required fields:
- `name` — plugin identifier (kebab-case)
- `description` — what the plugin does
- `version` — semver

Recommended fields:
- `author` — `{ "name": "...", "url": "..." }`
- `homepage`, `license`, `keywords`

**Do NOT include** `skills`, `commands`, or `agents` arrays in plugin.json — these are auto-discovered from the directory structure by Claude Code and will cause validation errors if present.

## Available MCP tools to wire

Browse available tools: `mcp__claude-flow__transfer_plugin-info`

Common tool categories:
- `memory_*` — storage, search, retrieval
- `agentdb_*` — 15 controller-bridge tools (do NOT pass `namespace` arg — they route by tier or ReasoningBank); call `agentdb_controllers` at runtime for the canonical list
- `neural_*` — neural training and prediction
- `hooks_*` — lifecycle hooks and intelligence
- `browser_*` — browser automation
- `workflow_*` — workflow management
- `aidefence_*` — safety scanning
- `embeddings_*` — 10 vector-embedding tools (use `embeddings_generate`, NOT `embeddings_embed` which does not exist)
