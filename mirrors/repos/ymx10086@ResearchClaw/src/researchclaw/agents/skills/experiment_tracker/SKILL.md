---
name: experiment-tracker
description: "Log experiments, list past runs, and compare experiment metadata or metrics. Use when the user wants lightweight experiment tracking inside ResearchClaw."
emoji: "🧪"
triggers:
  - experiment
  - ablation
  - metrics
  - compare runs
---

# Experiment Tracking

Use this skill when the user wants to record experiment parameters, results, notes, or compare multiple runs.

## Tools

- `log_experiment`: append a structured experiment record
- `list_experiments`: filter and inspect previous runs
- `compare_experiments`: compare selected runs side by side

## Guidance

- Normalize names, tags, and metric keys when the user provides loose wording.
- Use `log_experiment` after the user shares a concrete run or result.
- Use `compare_experiments` when the user explicitly asks for differences across runs.
