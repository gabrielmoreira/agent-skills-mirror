# SkillOpt-Sleep integrations

**SkillOpt-Sleep** reviews recent agent sessions, mines recurring tasks, replays
them, and proposes bounded updates to memory and skills. A held-out validation
gate decides whether a proposal is worth staging, and nothing live changes until
the user explicitly adopts it.

The shared engine lives in [`skillopt_sleep/`](../skillopt_sleep) and has no
runtime dependency on the paper's `skillopt/` experiment package.

## Available integrations

Four integrations wrap the shared `skillopt_sleep` CLI. OpenClaw is a separate
reference adaptation with its own backend and setup assumptions.

| Platform | Folder | Mechanism | Status |
|---|---|---|---|
| **Claude Code** | [`claude-code/`](claude-code) | marketplace plugin, commands, skill, and hooks | installable shared-engine integration |
| **Codex** | [`codex/`](codex) | user-level skill and shared runner | installable shared-engine integration |
| **GitHub Copilot** | [`copilot/`](copilot) | MCP server exposing seven `sleep_*` tools | shared-engine MCP integration |
| **Devin** | [`devin/`](devin) | MCP server plus Devin transcript conversion | shared-engine MCP integration |
| **OpenClaw** | [`openclaw/`](openclaw) | custom DeepSeek/Ollama wrapper | independent reference adaptation; review and adapt before use |

## Install

Clone the repository first unless an installed `skillopt-sleep` CLI is sufficient
for your workflow.

| Platform | Install | Then |
|---|---|---|
| **Claude Code** | from the repository root, `/plugin marketplace add ./plugins/claude-code`, then `/plugin install skillopt-sleep@skillopt-sleep` | `/skillopt-sleep status` |
| **Codex** | `bash plugins/codex/install.sh` | ask Codex to use the `skillopt-sleep` skill |
| **Copilot** | register `plugins/copilot/mcp_server.py` using its example MCP config | ask Copilot to run `sleep_status` |
| **Devin** | register `plugins/devin/mcp_server.py` using its example MCP config | ask Devin to run `sleep_status` |
| **OpenClaw** | follow and adapt [`openclaw/README.md`](openclaw/README.md) | validate paths, credentials, and tasks locally |

Python 3.10 or newer is required. Real CLI backends also require the selected
agent CLI to be installed and authenticated.

The shared [`run-sleep.sh`](run-sleep.sh) supports both source checkouts and
installed packages. If it cannot find the repository, it tries the
`skillopt-sleep` executable on `PATH` (including `uv tool`/`pipx` installs), then
an importable `skillopt_sleep` module. Install with `uv tool install skillopt` or
`pip install skillopt` when using that fallback.

> **Version note.** This integration reference tracks `main`. PyPI 0.2.0
> supports the base Sleep CLI, while handoff, Sleep support for non-Azure
> OpenAI-compatible endpoints, and `--preferences` require a source checkout
> from `main` until the next release.

## One sleep cycle

```text
harvest supported local sessions → mine recurring tasks → replay tasks
  → reflect and propose bounded edits → validate on held-out real tasks
  → stage proposal → (you) review and adopt
```

The default backend is `mock`: it makes no provider calls and is useful for
checking plumbing. A real backend is required for model-driven mining and genuine
optimization.

## Data boundary

- Harvesting is local and read-only. The `mock` backend has no model-provider
  data path and no API spend.
- A real backend sends truncated transcript excerpts and derived task content to
  the provider selected for mining, replay, judging, and reflection.
- Outbound prompts are not currently guaranteed to be free of secrets. Do not
  use a third-party provider on sensitive transcripts without reviewing the data
  source and the provider's retention policy.
- For a reviewable workflow, export tasks first, inspect and redact the JSON, set
  its top-level `"reviewed"` field to `true`, and then use the task file with a
  real backend:

  ```bash
  python -m skillopt_sleep harvest --project "$(pwd)" --output reviewed-tasks.json
  python -m skillopt_sleep dry-run --project "$(pwd)" --backend codex \
    --tasks-file reviewed-tasks.json --progress
  ```

  Real backends reject task files that are still marked unreviewed.

For the separate API-key and Azure managed-identity transport boundaries, see
[OpenAI-compatible endpoints](../docs/sleep/openai-compatible-endpoints.md).

## Supported CLI surface

Actions:

| Action | Behavior |
|---|---|
| `status` | show state and the latest staged proposal |
| `dry-run` | harvest, mine, replay, and report; stage nothing |
| `run` | run the full cycle and stage a proposal |
| `adopt` | apply the latest staged proposal, with backups |
| `harvest` | inspect or export mined tasks |
| `schedule` / `unschedule` | install or remove the managed nightly cron entry |

Common implemented flags include:

| Flag | Default | Purpose |
|---|---|---|
| `--backend mock\|claude\|codex\|copilot\|handoff\|azure_openai` | `mock` | select who performs model calls |
| `--model NAME` | backend default | select a backend-specific model |
| `--source claude\|codex\|auto` | `claude` | select the transcript source |
| `--project PATH` | current directory | select the project and invoked harvest scope |
| `--scope invoked\|all` | `invoked` | limit transcript harvesting |
| `--target-skill-path PATH` | managed skill | select a specific `SKILL.md` to stage/adopt |
| `--tasks-file PATH` | none | replay a reviewed task file instead of harvesting |
| `--max-sessions N` / `--max-tasks N` | unset → `3 × tasks` / `40` tasks | bound harvested work; these are not hard token or wall-clock budgets |
| `--edit-budget N` | `4` | cap bounded edits per cycle |
| `--preferences "..."` | empty | add house rules to the reflection prior |
| `--progress` | off | print phase progress to stderr |
| `--auto-adopt` | off | adopt an accepted proposal without a separate command |
| `--json` | off | emit machine-readable output where supported |

The nightly CLI does **not** currently expose `--gate`, `--rollouts-k`,
`--optimizer-model`, `--target-model`, `--budget-tokens`, or `--budget-minutes`.
Do not pass experiment-harness flags to the main CLI.

### Preferences

`--preferences` is the main user-facing steering knob:

```bash
python -m skillopt_sleep run --backend codex --project "$(pwd)" \
  --preferences "Prefer pytest. Keep commit subjects imperative and concise."
```

Preferences guide reflection but remain subject to the validation gate.

### Advanced config

The JSON/YAML config under `~/.skillopt-sleep/` supports additional engine keys,
including `gate_mode`, `gate_metric`, `dream_rollouts`, `dream_factor`, `recall_k`,
`evolve_memory`, and `evolve_skill`. These are config keys, not aliases for the
unsupported CLI flags listed above. Shipping defaults are conservative:
`gate_mode="on"`, `dream_rollouts=1`, `dream_factor=0`, and `recall_k=0`.

### Handoff backend

`--backend handoff` keeps model subprocesses out of the engine. It writes pending
model calls to `.skillopt-sleep-handoff/PROMPTS.md` and `pending.json`, exits with
code 3, and resumes after answers are placed in `answers/<id>.md`:

```bash
python -m skillopt_sleep run --backend handoff --project "$(pwd)"
# answer each prompt in a fresh context, then run the same command again
```

Answering held-out prompts from a context that has already seen their references
contaminates the validation gate. Claude Code's `/skillopt-sleep-handoff` command
automates the loop with isolated fresh-context subagents.

## Validation

The deterministic no-provider check exercises consolidation and the gate:

```bash
python -m skillopt_sleep.experiments.run_experiment \
  --persona researcher --assert-improves
```

Real-model benchmark results and their limitations are documented in
[`docs/sleep/RESULTS.md`](../docs/sleep/RESULTS.md). The benchmark recipes are not
the shipping CLI defaults.

## Safety summary

- Session harvesting is read-only.
- `mock` replay makes no provider calls.
- `run` stages proposals; `adopt` is the normal live-change boundary.
- Adoption backs up existing target files.
- `--max-sessions` and `--max-tasks` bound work, but the main CLI does not yet
  enforce a hard token or elapsed-time budget.
- Treat real-backend transcript excerpts as data shared with the selected
  provider.
