---
name: agentic-tool-integration
description: >
  Wiring a new tool the AI agent can call (not the recon pipeline): the tool
  registry, the phase map, the hardcoded dispatch chokepoint, and the duplicated
  execution paths that make a tool work in single mode but silently break in
  parallel plans.
  Trigger: adding or editing a tool the agent invokes; editing
  agentic/prompts/tool_registry.py, PhaseAwareToolExecutor in agentic/tools.py,
  agentic/orchestrator_helpers/nodes/execute_tool_node.py or execute_plan_node.py,
  TOOL_PHASE_MAP / DANGEROUS_TOOLS in agentic/project_settings.py, or a new MCP
  server in mcp/servers/.
license: MIT
metadata:
  author: redamon
  version: "1.0.0"
  scope: [agentic]
  auto_invoke:
    - "Adding a tool the agent can call"
    - "Editing the agent tool registry, phase map, or PhaseAwareToolExecutor dispatch"
    - "Adding or editing an MCP server the agent uses"
---

## When to Use

- Adding any tool the agent uses during a chat session (CLI wrapper, MCP tool, or API tool).

For a recon-pipeline tool (runs during a scan, writes the graph), use
`recon-tool-integration` instead. For the
per-setting/default multi-layer wiring, use
`project-settings-cascade`. For a whole
new attack *skill* (not a tool), use `builtin-agent-skill`.

---

## Critical Rules

- **NEVER `import` a package not already in the agent image.** `agentic/` is
  baked into the `redamon-agent` image; a missing import **crash-loops** the
  container. Confirm it is in [agentic/requirements.txt](../../agentic/requirements.txt)
  or the [Dockerfile](../../agentic/Dockerfile) first.
- **NEVER add a tool without a `TOOL_REGISTRY` entry** in
  [agentic/prompts/tool_registry.py](../../agentic/prompts/tool_registry.py). The
  registry is the single source of truth the LLM reads; an unregistered tool is
  invisible to the agent. All four fields (`purpose`, `when_to_use`,
  `args_format`, `description`) are required, and the description must clear the
  100-char minimum in [agentic/tests/test_tool_registry_completeness.py](../../agentic/tests/test_tool_registry_completeness.py),
  which fails on any unregistered or stub entry.
- **NEVER forget the dispatch branch for a non-MCP / API tool.**
  `PhaseAwareToolExecutor.execute()` at [agentic/tools.py:2070](../../agentic/tools.py#L2070)
  has hardcoded `if`/`elif` dispatch. A Type D (API) tool or an MCP tool needing
  key injection MUST add an `elif`; without it the tool is registered but never
  dispatched. MCP tools with no key injection go through the `else` branch automatically.
- **NEVER edit `execute_tool_node.py` without mirroring it in `execute_plan_node.py`.**
  [execute_tool_node.py](../../agentic/orchestrator_helpers/nodes/execute_tool_node.py)
  (single tool) and [execute_plan_node.py](../../agentic/orchestrator_helpers/nodes/execute_plan_node.py)
  (parallel plans) **duplicate** long-running detection and session/listener
  handlers. Update one only and the tool works interactively but silently
  misbehaves in parallel plan execution.
- **NEVER rely on the Prisma default to reach existing projects.** The
  `agentToolPhaseMap` default applies to NEW projects only. Existing projects
  need a jsonb `UPDATE` or the agent never sees the tool there. See
  `project-settings-cascade`.
- **ALWAYS add the tool to `TOOL_PHASE_MAP`** in [agentic/project_settings.py](../../agentic/project_settings.py).
  If it sends attack traffic: also add it to `DANGEROUS_TOOLS` (frozenset,
  [project_settings.py:22](../../agentic/project_settings.py#L22)), a per-tool
  section in [agentic/prompts/stealth_rules.py](../../agentic/prompts/stealth_rules.py),
  and the right list in `CATEGORY_TOOL_MAP` (`_check_roe_blocked`,
  [execute_plan_node.py:47](../../agentic/orchestrator_helpers/nodes/execute_plan_node.py#L47)).

---

## Pick the integration type (simplest that fits)

| Type | Use when | Core files beyond the registry |
| --- | --- | --- |
| **A** kali_shell | tool is in Kali, 300s timeout OK, no parsing | Dockerfile + `kali_shell` description only (no registry entry) |
| **B** MCP tool on existing server | CLI tool, custom timeout/parsing, fire-and-forget | `@mcp.tool()` in an existing `mcp/servers/*.py` (auto-discovered) |
| **C** new MCP server | stateful/interactive, own port | new `mcp/servers/*_server.py` + `SERVERS` in [run_servers.py](../../mcp/servers/run_servers.py) + URL in `MCPToolsManager` |
| **D** API/HTTP tool | external API, key-gated | `ToolManager` class + `elif` dispatch in `tools.py` + orchestrator key hot-reload |

Naming is uniform across every layer: MCP fn / registry key / phase-map key =
`execute_<tool>`; Prisma field `camelCase`; Python setting `SCREAMING_SNAKE`; DB
column `snake_case` via `@map()`.

## Commands

```bash
docker compose build agent && docker compose up -d agent   # mandatory: agentic/ is baked
docker compose exec webapp npx prisma db push              # if you added a Prisma field (NEVER prisma migrate)
./agentic/run_tests.sh                                     # gate; includes the registry completeness test
```

## Resources

- [docs/readmes/coding_agent_prompts/PROMPT.ADD_AGENTIC_TOOL.md](../../docs/readmes/coding_agent_prompts/PROMPT.ADD_AGENTIC_TOOL.md) - the full per-type file checklist and worked references
- Related skills: `project-settings-cascade`, `builtin-agent-skill`, `recon-tool-integration`
