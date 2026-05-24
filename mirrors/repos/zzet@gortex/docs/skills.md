# Per-community skills & agent usage

## Usage with Claude Code

After `gortex install` (once per machine) and `gortex init` (once per repo), Claude Code automatically starts Gortex via `.mcp.json`. The agent gets:

- **Slash commands (19):** installed to `~/.claude/commands/` by `gortex install`. Three groups:
  - *Discovery & analysis (8)* — `/gortex-guide`, `/gortex-explore`, `/gortex-debug`, `/gortex-impact`, `/gortex-dataflow-trace`, `/gortex-cross-repo-usage`, `/gortex-co-change`, `/gortex-onboarding`
  - *Refactor & edit (enforce tool-call order) (6)* — `/gortex-refactor`, `/gortex-safe-edit`, `/gortex-rename`, `/gortex-extract-function`, `/gortex-fix-all`, `/gortex-add-test`. These wrap the speculative-execution (`preview_edit` / `simulate_chain`) and LSP code-actions (`get_code_actions` / `apply_code_action` / `fix_all_in_file`) paths so the agent does not bypass the safety steps by calling `Edit` / `Write` directly.
  - *Review & operate (graph-grounded playbooks) (5)* — `/gortex-pr-review`, `/gortex-architecture-review`, `/gortex-quality-audit`, `/gortex-incident-investigation`, `/gortex-episode-replay`. These wrap the discovery + impact + memory surfaces into ordered playbooks so postmortems, audits, and PR reviews are graph-grounded.
- **Tool-usage skills:** the same 19 are installed as model-invoked skills to `~/.claude/skills/` by `gortex install` — one copy per user, used across every repo
- **Sub-agents (2):** installed to `~/.claude/agents/` by `gortex install`. Claude Code auto-routes matching prompts to them; each runs in a fresh context window and returns a single summary, keeping the parent's context clean. Tool allowlists are pinned to gortex graph tools only — Bash / Grep / Glob are unavailable to the sub-agent by construction.
  - `gortex-search` — locate code, trace call paths, explore architecture
  - `gortex-impact` — assess blast radius before editing (`verify_change`, `simulate_chain`, `check_guards`, `get_test_targets`)
- **PreToolUse hook:** automatic graph context + graph-tool suggestions on Read/Grep/Glob. The posture is selectable via `gortex install --hook-mode` — `deny` (default), `enrich`, `consult-unlock` (deny fallback reads only until the graph has been queried once this session), or `nudge` (a rate-limited soft reminder instead of a hard deny). Gortex's own MCP tools are auto-approved under the host's permissive permission modes
- **PreCompact hook:** condensed orientation snapshot injected before context compaction so the agent resumes without re-exploring
- **Stop hook:** post-task diagnostics — tests to run, guard violations, dead code, and contract issues on the changed symbols — injected as context before the agent hands off
- **CLAUDE.md:** per-repo codebase overview (via `--analyze`) plus a marker-guarded community routing block written by `gortex init --skills`

## Usage with other agents

`gortex install` (user-level) and `gortex init` (repo-level) together auto-detect and configure 14 other AI coding assistants — Kiro, Cursor, VS Code / Copilot, Windsurf, Continue.dev, Cline, OpenCode, Antigravity, Codex CLI, Gemini CLI, Zed, Aider, Kilo Code, OpenClaw. Each adapter writes only when its host is present on the machine, and every re-run is idempotent.

Tool-usage guidance for agents that have a user-level surface (Claude Code, Antigravity) lives once per user; for the rest, MCP tool descriptions carry the teaching and `gortex init` adds only a per-repo community-routing block — no more duplicated instructions blocks in every repo.

- **Adapter matrix + per-agent schema notes:** [`agents.md`](agents.md)
- **Audit what's currently configured:** `gortex init doctor` (zero-op; `--json` for CI consumers)
- **Constrain setup:** `gortex init --agents=claude-code,cursor` or `--agents-skip=antigravity` (same flags accepted by `gortex install`)
- **CI / scripted install:** `gortex install --yes --json` then `gortex init --yes --json --dry-run`

## Per-community skills

`gortex init --skills` (default on) analyzes your codebase, detects functional communities via Louvain clustering, and generates targeted SKILL.md files that Claude Code auto-discovers:

```bash
# Runs as part of `gortex init` by default — community generation is folded in
gortex init

# Tune or disable:
gortex init --skills-min-size 5 --skills-max 10
gortex init --no-skills
```

Each generated skill includes:

- **Community metadata** — size, file count, cohesion score
- **Key files table** — files and their symbols
- **Entry points** — main functions, handlers, controllers detected via process analysis
- **Cross-community connections** — which other areas this community interacts with
- **MCP tool invocations** — pre-written `get_communities`, `smart_context`, `find_usages` calls

For Claude Code, skills are written to `.claude/skills/generated/<DirName>/SKILL.md`, and a routing table is inserted into `CLAUDE.md` between `<!-- gortex:communities:start/end -->` markers. Every other detected agent gets the same routing table inside its per-repo instructions surface (`AGENTS.md` for Codex/OpenCode, `.windsurfrules` for Windsurf, `GEMINI.md` for Gemini CLI, `.cursor/rules/gortex-communities.mdc` for Cursor, etc.) — so the routing is consistent across tools on the same repo.
