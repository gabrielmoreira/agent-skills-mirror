# Cursor CLI Provider Configuration

This file contains Cursor-specific instructions for Claude Octopus workflows.

## Provider Information

- **Provider**: Cursor CLI (optional) — binary `agent`, registry ID `cursor-agent`, alias `cursor`
- **Emoji**: 🟪
- **API Key**: Optional — `CURSOR_API_KEY`; otherwise the `agent login` session
- **CLI Command**: `agent -p` (headless print mode, prompt on stdin)
- **Agent Types**: `cursor-agent`, `cursor-agent:<model>`
- **Cost**: Included in the Cursor subscription (pricing rows are `0.00`); each prompt consumes Cursor plan usage

## Detection

- Binary identity: `agent --version` must print a CalVer string (`2026.06.24-…`).
  `agent` is a generic name, so a semver-style output is rejected. The probe is
  bounded by `OCTOPUS_CURSOR_AGENT_PROBE_TIMEOUT` (default 3s).
- Auth check (precedence order), owned by `scripts/lib/cursor-agent.sh`:
  1. `CURSOR_API_KEY` env var
  2. An `authInfo` block in `~/.cursor/cli-config.json` (cheap, offline)
  3. That block can be missing while the CLI is still logged in (seen on build
     2026.06.24 until the CLI persisted its session); `agent status --format json`
     must then report `"isAuthenticated": true`. The call is network-bound (3–12s),
     so it is bounded by `OCTOPUS_CURSOR_AGENT_STATUS_TIMEOUT` (default 15s)
     and its yes/no verdict is cached per process and on disk in the user
     cache directory (`${XDG_CACHE_HOME:-~/.cache}/claude-octopus/cursor-agent-auth-verdict`,
     never inside the workspace; symlinks are refused and the file is replaced
     atomically; `OCTOPUS_CURSOR_AGENT_AUTH_CACHE_TTL` default 600s, negative
     verdicts `OCTOPUS_CURSOR_AGENT_AUTH_NEGATIVE_TTL` default 60s, TTL `0`
     disables, `OCTOPUS_CURSOR_AGENT_AUTH_CACHE_FILE` overrides the path).
     The JSON carries the account email and is never echoed or cached.

If the CLI is not installed or not authenticated, silently skip — no errors, no warnings.

## Authentication Setup

### Option 1: Interactive Login (recommended)
```bash
agent login
```

### Option 2: API Key (CI/automation)
```bash
export CURSOR_API_KEY="..."
```

## Dispatch Pattern

```bash
agent --trust --output-format text --mode ask --model auto -p ""   # prompt arrives on stdin
```

`--trust` skips the workspace-trust prompt. `-p ""` is appended by
spawn/workflows/agent-sync so the prompt travels on stdin (no ARG_MAX limit).

### Execution mode (safety)

`agent -p` has full tool access (write + shell) in the working directory, so
Octopus opts down by role. `OCTOPUS_CURSOR_AGENT_MODE` overrides the table.

| Role | Mode | Flag |
|------|------|------|
| research, review, council, verifier, synthesizer, anything else | `ask` | `--mode ask` (read-only Q&A) |
| `planner`, `architect`, `strategist` | `plan` | `--mode plan` (read-only planning) |
| `implementer`, `developer`, `implementer-heavy` | `agent` | `--force` (full unattended tool access) |

An invalid override logs an error and keeps the role default.

## Model Selection

Default is `auto` (Cursor's service-side pick; always valid). Pin with
`OCTOPUS_CURSOR_AGENT_MODEL`, `providers.json` (`providers.cursor-agent.default`),
or a model-qualified seat such as `cursor-agent:composer-2.5`.

Use flat IDs exactly as printed by `agent models` (for example
`composer-2.5`, `cursor-grok-4.6-high`, `gpt-5.6-sol-high`,
`claude-sonnet-5-thinking-high`, `gemini-3.7-flash-high`). Cursor's bracket
override syntax (`claude-opus-4-8[context=1m,effort=high]`) is rejected by the
model-name validator.

Vendor family for independence checks follows the pinned model
(`claude-*` → Anthropic, `gpt-*` → OpenAI, `cursor-grok-*` → xAI,
`composer-*`/`auto` → Cursor).

## Environment Isolation

Dispatch runs under `env -i` with `PATH`, `HOME` (session state lives in
`~/.cursor`), `TERM`, `TMPDIR`, `CURSOR_API_KEY` when set, and the
`OCTOPUS_CURSOR_AGENT_*` controls. Set `OCTOPUS_ALLOW_FULL_CURSOR_AGENT_ENV=true`
to inherit the full parent environment.

## Role Assignment

Cursor serves as:
- **Council / review / debate seat** — registry `council` capability; fills
  logic, security, or diversity review seats and the debate slot when
  Antigravity or Codex is unavailable
- **Research perspective** — "Cursor Perspective" in dynamic research fleets
- **Implementer** — only when the role is implementer/developer (`--force`)

## Timeouts

- `OCTOPUS_CURSOR_AGENT_TIMEOUT` — per-dispatch wall clock (default 120s)
- `OCTOPUS_CURSOR_AGENT_PROBE_TIMEOUT` — `agent --version` identity probe (default 3s)
- `OCTOPUS_CURSOR_AGENT_STATUS_TIMEOUT` — `agent status` session probe (default 15s)
