---
name: report
description: Print the dashboard's dot chart (score over experiment order, status colors, best-path stair) inline in the terminal for every run in the workspace. Use when the user invokes /evo:report, asks for a quick score chart without opening the dashboard, or wants the scatter plot in chat output.
evo_version: 0.5.2
---

# Report

Render the dashboard's scatter plot as a colored terminal block, one chart per run, sized to the current terminal.

## What it shows

Mirrors the web dashboard's score scatter (left rail of `evo dashboard`):

- X = experiment creation order, Y = score
- Dot color by status: green = committed, red = failed, purple = active, grey = pending / evaluated / discarded / pruned
- ★ marks the current best committed experiment
- Yellow ring on dots that sit on the best-path spine (root → best)
- Yellow stair line traces cumulative-best across committed experiments
- ○ at the baseline for experiments that have no score yet (active / pending)

Every run in the workspace is rendered, stacked top-to-bottom, with a header line showing `run_id · target · metric`.

## How to invoke

Run:

```bash
evo report
```

That is it. Print the output verbatim in your reply so the user sees the chart. Do not summarize the chart in prose — the visual is the point.

Flags:

- `--color always|never|auto` — force or suppress ANSI color. Default `auto` (color when stdout is a TTY). Pass `--color always` if you are piping through a host that strips TTY but renders ANSI in chat.
- `--watch [SECONDS]` — live-refresh mode (like `nvidia-smi -l`). Re-reads the workspace every N seconds (default 2) and redraws in place. Ctrl-C to exit. Use this when you want to babysit a running optimization without manually re-invoking the report.

## When not to use

- For one-off score lookups, `evo status` or `evo show <id>` is faster.
- For navigating the tree shape, `evo tree` is the right command.
- For interactive exploration (click a dot, open a drawer), point the user at `evo dashboard` instead.
