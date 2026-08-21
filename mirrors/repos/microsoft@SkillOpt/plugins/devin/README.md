# SkillOpt-Sleep — Devin integration

Give **Devin** (Cognition) a nightly **sleep cycle** via a tiny **MCP server**
that exposes the `skillopt_sleep` engine as tools. MCP is Devin's supported way
to add custom tooling, so this works in Devin's CLI and IDE.

Devin doesn't write transcripts in the format the engine consumes, so this
plugin adds a **Devin-specific harvester** that converts every locally available
source into the Claude Code-compatible JSONL the engine reads.

## What's here

| File | Purpose |
|---|---|
| `mcp_server.py` | stdlib-only MCP (stdio) server exposing `sleep_*` tools |
| `harvest_devin.py` | converts Devin ATIF-v1.7 transcripts + agentmemory + `.devin/skills` into JSONL, with `taskKey` + outcome envelopes |
| `judge.py` | reference judge for the deferred/judge branch of the validation gate |
| `mcp-config.example.json` | drop-in MCP server config |
| `install.sh` | copies hooks + rules into a project's `.devin/` and prints the MCP registration command |
| `devin-rules.snippet.md` | copied to `.devin/rules/skillopt-sleep.md` by `install.sh` |
| `hooks/hooks.v1.json` | SessionEnd hook config — installed/merged at `.devin/hooks.v1.json` by `install.sh` |
| `hooks/on-session-end.sh` | best-effort activity marker script (called by the hook) |

## What it harvests

| Source | Where |
|---|---|
| Devin transcripts (ATIF-v1.7) | `~/.local/share/devin/cli/transcripts/*.json` |
| agentmemory | `~/.agentmemory/standalone.json` |
| Skill files | `.devin/skills/*/SKILL.md` |

Workspaces are auto-detected from `~/.config/Devin/User/workspaceStorage/*/workspace.json`.
The adapter performs no post-adoption copy. The core engine applies a reviewed
proposal directly to its selected target and owns backup/rollback behavior.

## Install

Requires Python ≥ 3.10. No third-party packages — the server is pure stdlib.

1. **Install hooks + rules into your project.** From the repo root:

   ```bash
   bash plugins/devin/install.sh /path/to/your/project
   ```

   This copies the SessionEnd hook and rules snippet into the project's
   `.devin/` directory and prints the MCP registration command. The hook is
   on by default — it logs a cheap activity marker for local inspection or
   external automation when each session ends. The current engine harvests by
   transcript timestamps and does not consume this marker directly. The hook
   is non-blocking and spends no API budget. Re-run the script to update; the
   installer preserves existing hooks and does not duplicate its own entry.

2. **Register the MCP server.** Use `mcp-config.example.json` as a template, or
   run the command printed by `install.sh`:

   ```bash
   devin mcp add skillopt-sleep \
     --env "SKILLOPT_DEVIN_CLAUDE_HOME=$HOME/.skillopt-sleep-devin" \
     -- python3 /abs/path/to/SkillOpt/plugins/devin/mcp_server.py
   ```

3. Ask Devin: *"run the sleep cycle"*, *"what did the last sleep propose?"*, *"adopt it"*.

## Tools

| Tool | What it does |
|---|---|
| `sleep_status` | nights run so far + latest staged proposal |
| `sleep_dry_run` | preview cycle — no staging; a real backend still makes provider calls |
| `sleep_run` | full cycle; stages a proposal for review |
| `sleep_adopt` | apply a reviewed legacy or per-skill proposal (with backup) |
| `sleep_harvest` | debug: list the recurring tasks mined |
| `sleep_schedule` | install a nightly cron entry (`--hour` / `--minute`) |
| `sleep_unschedule` | remove the nightly cron entry |

Before `sleep_adopt`, inspect `sleep_status` and use the controls that match the
reviewed staging manifest:

- `staging` — exact staging directory to adopt instead of the latest night
- `skills` — array of skill names to adopt; each is forwarded as one repeated
  `--skill` argument without shell interpolation
- `all_skills` — adopt every staged per-skill proposal
- `legacy` — adopt only the legacy managed `SKILL.md`/`CLAUDE.md` pair

Choose one selection mode (`skills`, `all_skills`, or `legacy`) and do not
combine them. A bare call remains compatible with legacy-only staging; fan-out
staging requires an explicit selection. To operate on a specific Devin skill,
pass its `SKILL.md` as `target_skill_path`; the adapter never performs a second
copy after the core engine returns.

Tool results preserve the engine's `exit_code` in `structuredContent`.
Ordinary nonzero exits set `isError: true`; exit 3 is the expected
`handoff_pending` state and is not an MCP tool error. With `json: true`, text
content is the engine's parseable JSON stdout, while harvest and engine
diagnostics remain separate in `structuredContent`.

Default backend is `mock` (no API spend); the `claude`, `codex`, and `copilot`
backends use the corresponding authenticated CLI and budget. The `handoff`
backend runs the cycle with no model subprocess or API key — the engine writes
pending model calls to `.skillopt-sleep-handoff/PROMPTS.md` + `pending.json`
(exit code 3) and resumes after answers are placed in `answers/<id>.md`; re-run
`sleep_run` with the same arguments to resume. The seven tools call the same
`python -m skillopt_sleep` actions as the other shared-engine integrations.

## Data boundary

The Devin harvester reads local ATIF transcripts, agentmemory, and skill files
and converts them into the engine's session format. The `mock` backend keeps
that workflow local. A real backend sends truncated excerpts and derived tasks
to the selected provider for mining, replay, judging, and reflection. The
conversion step is not a guarantee that outbound prompts contain no secrets;
review sensitive sources and provider policy before enabling a real backend.
See the [shared data-boundary guidance](../README.md#data-boundary) and
[implemented CLI reference](../README.md#supported-cli-surface).
