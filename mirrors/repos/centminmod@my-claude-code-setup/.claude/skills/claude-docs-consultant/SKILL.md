---
name: claude-docs-consultant
description: Consult official Claude Code documentation from code.claude.com using selective fetching. Use when working on hooks, skills, subagents, plugins, agent teams, MCP servers, permissions, settings, CI/CD (GitHub Actions, GitLab), IDE extensions (VS Code, JetBrains), desktop/web app features, scheduling, memory/CLAUDE.md, deployment (Bedrock, Vertex, Foundry), sandboxing, monitoring, or any Claude Code feature requiring official docs. Fetches only the specific docs needed per task.
metadata:
  version: 2.0.0
---

# Claude Docs Consultant

Fetch official Claude Code documentation on-demand from code.claude.com. Uses progressive disclosure: resolve the topic to a filename, then fetch only that doc. Never fetch documentation speculatively.

## URL Pattern

All docs follow this pattern — substitute the filename:

```
https://code.claude.com/docs/en/{filename}.md
```

## Quick Routing (Common Topics)

For these high-frequency topics, fetch directly without consulting the full index:

| Topic | Filename(s) to fetch |
| --- | --- |
| Hooks (creating, events, lifecycle) | `hooks-guide.md` (guide + examples), `hooks.md` (API reference + all events) |
| Skills (creating, SKILL.md format, triggers) | `skills.md` |
| Subagents (types, config, delegation) | `sub-agents.md` |
| Agent Teams (multi-agent, teammates, cowork) | `agent-teams.md` |
| Plugins (creating, marketplace, installing) | `plugins.md` (creating), `discover-plugins.md` (marketplace + installing) |
| MCP Servers (setup, config, scopes) | `mcp.md` |
| Settings (settings.json, config scopes) | `settings.md` |
| Permissions (rules, modes, auto mode) | `permissions.md` (rules + syntax), `permission-modes.md` (plan/auto/dontAsk modes) |
| Memory (CLAUDE.md, auto memory, rules) | `memory.md` |
| GitHub Actions (CI/CD, @claude PR) | `github-actions.md` |

## Full Routing

For topics not listed above, consult `references/docs-index.md` for the complete routing table covering all 60+ documentation pages across platforms, deployment, security, configuration, administration, and reference.

## Workflow

1. **Identify topic** — determine which Claude Code feature the task involves
2. **Route to filename** — use quick routing above, or consult `references/docs-index.md`
3. **Fetch with WebFetch** — use the URL pattern with the resolved filename

Fetch multiple docs in parallel when the task spans multiple topics.

## Fallback: Discovery via Docs Map

If routing does not match any known filename, fetch the documentation map to discover available pages:

```
https://code.claude.com/docs/en/claude_code_docs_map.md
```

Identify the relevant doc from the map, then fetch it using the URL pattern.

## Rules

- Fetch only the docs actually needed for the current task
- Fetch multiple docs in parallel if the task requires 2+ sources
- Always fetch live from code.claude.com — do not use cached or memorized content
- Do not fetch docs "just in case" — fetch when required by the task

## Examples

### Example 1: Creating a Hook

**Task:** "Help me create a pre-tool-use hook to log tool calls"

1. Route: hook creation -> `hooks-guide.md` + `hooks.md`
2. Fetch both in parallel via WebFetch
3. Apply: create hook using guide examples and API reference for PreToolUse event

### Example 2: Installing a Plugin

**Task:** "How do I install plugins from a marketplace?"

1. Route: plugin installing -> `discover-plugins.md`
2. Fetch via WebFetch
3. Apply: follow marketplace and installation instructions

### Example 3: Unknown Feature

**Task:** "How do I configure Claude Code output styles?"

1. Route: not in quick routing table
2. Consult `references/docs-index.md` -> find `output-styles.md` under Configuration
3. Fetch `output-styles.md` via WebFetch
4. Apply: configure output styles per documentation
