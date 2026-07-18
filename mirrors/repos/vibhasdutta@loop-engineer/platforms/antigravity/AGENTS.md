# Loop Engineer

When the user asks to run an autonomous loop, orchestrate a multi-agent team,
or start a goal-driven task loop, activate the loop-engineer skill.

## Activation

Describe a multi-step goal in natural language — the agent activates the skill automatically.
Or type `/loop-engineer` directly in any Antigravity surface.

Examples:
- "I want to run an autonomous loop to add authentication to my API."
- "Help me orchestrate a multi-agent team to refactor this codebase."
- "Start a loop-engineer session and help me build X."

## How subagents work

Antigravity uses `invoke_subagent` to spawn parallel agents:
- **Parallel**: pass multiple entries in the `Subagents` array in one call — all run simultaneously.
- **Sequential**: separate `invoke_subagent` calls, wait for completion message between each.
- Subagents start with a clean context slate — they do not inherit the parent conversation.
- Every prompt must be self-contained (include loop dir, what to read, what to write).

Built-in TypeNames:
- `"research"` — optimized for codebase navigation and exploration (used for researcher agents)
- `"self"` — clone of parent agent with same toolsets (used for all other agents)

Agent instruction files live in `.agents/` in the workspace root (copied from the global skill).

Use `manage_subagents(Action: "list")` to monitor running subagents.
Use `manage_subagents(Action: "kill", ConversationIds: [...])` to terminate if needed.

## State files

All loop state lives in `loop-stack/<LOOP_ID>/`:
- `PLAN.md` — goal, tasks with [G1]/[G2] parallel group tags, stop condition
- `STATUS.md` — current state, attempts, last results from each agent
- `MEMORY.md` — accumulated learnings (grows smarter each iteration)
- `TOOLS.md` — discovered MCP servers, skills, plugins, project tooling + Tool Usage Guide
- `RESEARCH.md` — researcher findings per task
- `AGENTS.md` — specialized agents created by agent-factory after planning

`loop-stack/.global/` — shared across all loops in this project:
- `MEMORY.md` — cross-loop project learnings
- `TOOLS.md` — cached tool discovery (7-day TTL)

## Configuration paths by surface

Each surface has its own global skills directory. Workspace paths are identical across all three.

| Resource | CLI (`agy`) | IDE (VS Code/JetBrains) | 2.0 (desktop) |
|---|---|---|---|
| Skills (global) | `~/.gemini/antigravity-cli/skills/` | `~/.gemini/antigravity/skills/` | `~/.gemini/config/skills/` |
| Skills (workspace) | `.agents/skills/` | `.agents/skills/` | `.agents/skills/` |
| MCP servers (global) | `~/.gemini/config/mcp_config.json` | `~/.gemini/config/mcp_config.json` | `~/.gemini/config/mcp_config.json` |
| MCP servers (workspace) | `.agents/mcp_config.json` | `.agents/mcp_config.json` | `.agents/mcp_config.json` |
| Plugins (global) | `~/.gemini/antigravity-cli/plugins/` | `~/.gemini/config/plugins/` | `~/.gemini/config/plugins/` |
| Plugins (workspace) | `.agents/plugins/` | `.agents/plugins/` or `_agents/plugins/` | `.agents/plugins/` |
| Permissions | `settings.json` → `"permissions"` key | Settings → Customizations → Permissions | Settings → Customizations → Permissions |
| Hooks (global) | `settings.json` / plugin's `hooks.json` | `~/.gemini/config/hooks.json` | `~/.gemini/config/hooks.json` |
| Hooks (workspace) | `.agents/plugins/<n>/hooks.json` | `.agents/hooks.json` | `.agents/hooks.json` |
| Rules (global) | `~/.gemini/GEMINI.md` | `~/.gemini/GEMINI.md` | `~/.gemini/GEMINI.md` |
| Rules (workspace) | `.agents/rules/` | `.agents/rules/` | `.agents/rules/` |
| App data | `~/.gemini/antigravity-cli/` | `~/.gemini/antigravity-ide/` (brain) | `~/.gemini/antigravity/` |
| Agent files | `.agents/` (set up by skill) | `.agents/` (set up by skill) | `.agents/` (set up by skill) |

## MCP config format (`mcp_config.json`)

```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["/path/to/server.js"],
      "env": { "API_KEY": "..." }
    },
    "remote-server": {
      "serverUrl": "https://api.example.com/mcp/",
      "headers": { "Authorization": "Bearer TOKEN" }
    }
  }
}
```

Remote servers: use `serverUrl` (not `url` or `httpUrl`).
Manage via `/mcp` in the CLI prompt (interactive overlay), or via Settings → Customizations in 2.0/IDE.

## CLI permissions (`~/.gemini/antigravity-cli/settings.json`)

```json
{
  "permissions": {
    "allow": [
      "command(git)",
      "command(npm run (build|test|lint))",
      "write_file(loop-stack/)",
      "write_file(.agents/)",
      "write_file(src/)",
      "mcp(*)"
    ],
    "deny": [
      "command(rm -rf)",
      "command(sudo)"
    ],
    "ask": []
  },
  "toolPermission": "proceed-in-sandbox",
  "enableTerminalSandbox": false
}
```

`toolPermission`: `"request-review"` (default, prompt on writes) | `"proceed-in-sandbox"` | `"strict"` (prompt everything)

For 2.0/IDE, configure permissions via Settings → Customizations → Permissions (same action format, same syntax).

## CLI plugin structure

```
~/.gemini/antigravity-cli/plugins/<plugin_name>/
├── plugin.json           # Required: name + description
├── mcp_config.json       # Optional: MCP servers bundled with plugin
├── hooks.json            # Optional: pre/post tool event hooks
├── skills/               # Optional
├── agents/               # Optional
└── rules/                # Optional
```

Plugin commands: `agy plugin list` | `agy plugin install <path>` | `agy plugin disable/enable/uninstall <name>`

## IDE / 2.0 plugin structure

```
~/.gemini/config/plugins/<plugin_name>/   (or .agents/plugins/<n>/ for workspace)
├── plugin.json           # Required: { "name": "..." }
├── mcp_config.json       # Optional
├── hooks.json            # Optional
├── skills/<skill-name>/SKILL.md
└── rules/<rule-name>.md
```

## IDE rules modes

At the rule level in `.agents/rules/`, you can annotate how a rule is activated:
- **Always On** — always applied
- **Manual** — activated via `@mention` in the prompt
- **Model Decision** — agent decides based on the description
- **Glob** — applied to files matching a pattern (e.g. `**/*.ts`)

## Useful slash commands

- `/loop-engineer` — activate the skill
- `/mcp`           — open MCP Manager overlay (CLI: live status)
- `/browser`       — spawn browser subagent (2.0 / IDE)
- `/hooks`         — inspect active hooks (CLI)
- `/rewind` or `/undo` — roll back to previous stable state (CLI)
- `/fork`          — duplicate session for experiments (CLI)
- `/workflow-name` — run a saved workflow (IDE / 2.0)

## Hooks for autonomous loops (IDE / 2.0)

The Stop hook can prevent the agent from stopping mid-loop. In `.agents/hooks.json`:

```json
{
  "loop-continue": {
    "Stop": [
      {
        "command": "./scripts/check-loop-done.sh",
        "timeout": 5
      }
    ]
  }
}
```

The hook returns `{"decision": "continue", "reason": "..."}` to keep the loop running,
or `{"decision": ""}` to allow it to stop.
