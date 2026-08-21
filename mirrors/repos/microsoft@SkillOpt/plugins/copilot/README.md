# SkillOpt-Sleep — GitHub Copilot integration

Give **Copilot** (CLI or VS Code) a nightly **sleep cycle** via a tiny **MCP
server** that exposes the `skillopt_sleep` engine as tools. MCP is GitHub's
supported way to extend Copilot, so this works across Copilot CLI, VS Code, and
other MCP clients with the same server.

## What's here

| File | Purpose |
|---|---|
| `mcp_server.py` | stdlib-only MCP (stdio) server exposing `sleep_*` tools |
| `mcp-config.example.json` | drop-in MCP server config |
| `copilot-instructions.snippet.md` | paste into `.github/copilot-instructions.md` |

## Install

Requires Python ≥ 3.10. No third-party packages — the server is pure stdlib.

1. **Register the MCP server.** Add the server to your Copilot MCP config
   (Copilot CLI: `~/.copilot/mcp-config.json`; VS Code: your MCP settings).
   Use `mcp-config.example.json` as a template — set `SKILLOPT_SLEEP_REPO` to
   this repo's path:

   ```json
   {
     "mcpServers": {
       "skillopt-sleep": {
         "command": "python3",
        "args": ["/abs/path/SkillOpt/plugins/copilot/mcp_server.py"],
        "env": { "SKILLOPT_SLEEP_REPO": "/abs/path/SkillOpt" }
       }
     }
   }
   ```

2. **(Optional) Tell Copilot about it.** Append
   `copilot-instructions.snippet.md` to your repo's
   `.github/copilot-instructions.md` so Copilot reaches for the tools when the
   user asks to "run the sleep cycle".

## Use

Ask Copilot things like *"run the sleep cycle"*, *"what did the last sleep
propose?"*, *"adopt the staged sleep proposal"*. The server exposes seven MCP
tools: `sleep_status`, `sleep_dry_run`, `sleep_run`, `sleep_adopt`,
`sleep_harvest`, `sleep_schedule`, and `sleep_unschedule`.

Each tool takes optional `project`, `backend`
(`mock`/`claude`/`codex`/`copilot`/`handoff`), and `scope` arguments. For
`sleep_adopt`, first inspect `sleep_status`, then use the adoption controls that
match the reviewed staging manifest:

- `staging` — exact staging directory to adopt instead of the latest night
- `skills` — array of skill names to adopt; each is passed as one repeated
  `--skill` argument without shell interpolation
- `all_skills` — adopt every staged per-skill proposal
- `legacy` — adopt only the legacy managed `SKILL.md`/`CLAUDE.md` pair

Choose one selection mode (`skills`, `all_skills`, or `legacy`) and do not
combine them. A bare `sleep_adopt` remains compatible with legacy-only staging;
fan-out staging requires an explicit selection.

Tool results preserve the engine's `exit_code` in `structuredContent`.
Ordinary nonzero exits set `isError: true`; exit 3 is the expected
`handoff_pending` state and is not an MCP tool error. With `json: true`, text
content is the engine's parseable JSON stdout, while diagnostics remain
separate in `structuredContent`.

Default backend is `mock` (no API spend). The `copilot` backend drives the
GitHub Copilot CLI (`copilot -p ... --output-format json`) and requires the
`copilot` CLI to be installed and authenticated.

Harvesting is local and read-only, and the default `mock` backend makes no
provider calls. A real backend sends truncated transcript excerpts and derived
tasks to the selected provider. Outbound prompts are not currently guaranteed
to be secret-free; review sensitive data and provider policy first. See the
[shared data-boundary guidance](../README.md#data-boundary).

For speed, the `copilot` backend runs each call against an isolated
`COPILOT_HOME` with built-in MCP servers and custom instructions disabled, so
your user MCP servers (including this project's own) are not spawned per call
(~5x faster). Override with `SKILLOPT_SLEEP_COPILOT_HOME=<dir>`, pick a model
with `SKILLOPT_SLEEP_COPILOT_MODEL`, or set `SKILLOPT_SLEEP_COPILOT_FULL_ENV=1`
to use your real Copilot environment instead.

## Verify the server directly (no Copilot needed)

```bash
printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
  | SKILLOPT_SLEEP_REPO="$(pwd)" python3 plugins/copilot/mcp_server.py
```
You should see the server info and all seven `sleep_*` tools.

## Notes / status

- MCP is the stable, official Copilot extension surface, so this is the most
  portable shared-engine integration (one server → CLI + IDE).
- The MCP schema exposes the main CLI's implemented controls, including task and
  session caps, target-skill selection, scheduling, and staged adoption. It does
  not add experiment-only gate, rollout, token/time-budget, or optimizer/target
  split flags. See the [shared CLI reference](../README.md#supported-cli-surface).
