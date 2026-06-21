---
name: skillopt-sleep
description: Validate and refine agent skills through nightly sleep cycles with held-out gates. Wraps Microsoft's SkillOpt-Sleep engine for the OpenClaw/DeepSeek stack.
---

# skillopt-sleep — OpenClaw Adaptation of Microsoft SkillOpt-Sleep

A nightly self-improvement loop that reads our session transcripts, mines recurring workflow patterns, replays them with proposed skill edits, and gates the proposals against a held-out test set. Only improvements that beat baseline are staged for human adoption.

## When To Use

- After Hermes's Weekly Skill Review (or as its replacement)
- When a skill is being used 10+ times/week and could be tighter
- Before promoting a new skill from `skill-proposals/` to `skills/`
- When a skill regresses in observed quality

## What It Does (One Cycle)

```
harvest session transcripts  ->  mine recurring task patterns
                              ->  replay each pattern (current skill vs proposed)
                              ->  GATE: must improve held-out score
                              ->  stage proposal
                              ->  Ethan adopts (manual)
```

Nothing live changes until Ethan adopts. Every adopt backs up first.

## Architecture

```
skills/skillopt-sleep/
├── SKILL.md                          # this file
├── config.json                       # engine config (backend, budgets, etc.)
├── run_sleep.py                      # entry point
└── skillopt_sleep_openclaw.py        # DeepSeek/Ollama backend
```

The engine itself is at `~/.openclaw/workspace/SkillOpt/skillopt_sleep/` (cloned from microsoft/SkillOpt).

## Usage

```bash
# Run one cycle with current config
cd ~/.openclaw/workspace/skills/skillopt-sleep
python3 run_sleep.py

# Dry run (report only, no staging)
python3 run_sleep.py --dry-run

# Use a pre-built task set (recommended for testing)
python3 run_sleep.py --tasks tests/research-cron-tasks.json
```

## Scheduling

```bash
python3 slash_sleep.py schedule --hour 3 --minute 17
python3 slash_sleep.py unschedule
python3 slash_sleep.py unschedule --all
```

Installs a nightly cron entry using the shared SkillOpt-Sleep scheduler. This is an alternative to the external `run_sleep_cron.sh` script.

## Alternative backends

While OpenClaw defaults to `openclaw-deepseek` (DeepSeek V4 Pro + Ollama), the shared engine also supports:
- `--backend mock` — deterministic, no API spend (for testing)
- `--backend claude` — uses the Claude CLI
- `--backend codex` — uses the Codex CLI
- `--backend copilot` — uses the GitHub Copilot CLI

These can be used via the engine directly (`python -m skillopt_sleep`).

## Shared-engine flags

When invoking the engine directly, all standard flags are available:
- `--source codex` / `--source auto` — harvest from Codex Desktop sessions
- `--tasks-file PATH` — use a pre-built task set
- `--target-skill-path PATH` — explicit SKILL.md target
- `--max-tasks N` / `--max-sessions N` — cap workload
- `--progress` — print phase progress
- `--json` — machine-readable output
- `--auto-adopt` — auto-adopt if gate passes

Config keys: `preferences`, `gate_mode`, `gate_metric`, `dream_rollouts`, `recall_k`, `evolve_memory`, `evolve_skill`.

## Config (config.json)

Key knobs:
- `backend: "openclaw-deepseek"` — our custom backend
- `model: "deepseek-v4-pro"` — optimizer model
- `edit_budget: 3` — max bounded edits per night
- `gate_mode: "on"` — validation-gated (rejects regressions)
- `auto_adopt: false` — require Ethan to adopt manually
- `max_tasks_per_night: 12` — cap to control cost

## Cost Estimate

Per night: 12 tasks × (1 attempt + 1 judge + 1 reflect) × ~$0.005/1K tokens × ~3K tokens/call ≈ **$0.50-2.00/night**.

## Outputs

- Report: `~/.skillopt-sleep/state.json` (running totals)
- Staging: `~/.skillopt-sleep/staging/<night>/`
  - `report.md` — readable summary
  - `best_skill.md` — proposed skill
  - `edits.json` — bounded edit list
  - `before.md` / `after.md` — diffs

## Held-Out Test Sets (Phase 2)

Located at `tests/<category>-tasks.json`. Each task has:
- `prompt` — the recurring task
- `reference` — exact-match gold answer
- `rubric` — soft score rubric (0-1)
- `domain` — research/devops/wiki/etc.

Currently building for 3 categories:
- research-cron-output
- devops-infrastructure-check
- wiki-canonical-guide

## When NOT To Use

- For a one-off workflow (not a recurring pattern)
- During a crisis/incident (humans must lead)
- When session transcripts are < 24h old (not enough signal)
- For skills < 300 tokens (over-optimization risk)
