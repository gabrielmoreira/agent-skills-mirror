---
name: benchmarking
description: Run runtime benchmark evaluations on enabled simulation targets, aggregate session artifacts, and write experiment reports.
metadata: {"PhyAgentOS":{"always":false,"available":true,"requires":{"runtime":{"enabled":true,"target_kind":"simulation","skillruntime_kind":"policy"}}}}
---

# Benchmarking

Use this skill when the user asks to evaluate a policy on a runtime simulation benchmark, run a benchmark sweep, compute success rates, or produce an experiment report from runtime sessions.

This is an agent skill. It does not define a runtime skillruntime. Runtime execution still belongs to `TARGETS.md`, `SKILLRUNTIME.md`, `SESSIONS.md`, and the watchdog/session runner.

## Preconditions

Before creating sessions:

- Read `RUNTIME.md`, `TARGETS.md`, `SKILLRUNTIME.md`, `SESSIONS.md`, and `LOG.md` when present.
- Use only targets with `enabled: true` and `target_kind: simulation`.
- Use only skillruntimes listed by the selected target's `supported_skillruntimes`.
- Use only supported skillruntimes whose `runtime_kind` is `policy`.
- Prefer endpoints already declared in `TARGETS.md`; override endpoints only when the user explicitly provides them.
- Preserve all existing sessions and results in `SESSIONS.md`.

If no enabled simulation target supports a policy skillruntime, stop and explain which runtime requirement is missing.

## Task Discovery

Prefer live benchmark metadata when a remote target endpoint is configured:

- Use TargetWS `target.describe` when available.
- Extract `benchmark_name`, `num_tasks`, `task_list`, task language, and any action or observation contract metadata.
- Treat `task_list` entries as the authoritative task source for session generation.

When live discovery is unavailable, fall back to `TARGETS.md`:

- Use `config.benchmark_name`, `config.task_id`, `config.init_state_id`, and any task description already present.
- Record in the report that task discovery used static target config rather than live target metadata.

## Session Construction

Append one pending session per selected task and init-state pair to `SESSIONS.md`.

Each session must use the existing runtime session schema:

- `session_id`: stable, unique, benchmark-readable id.
- `target_ref`: `target://<target_id>`.
- `skillruntime_ref`: `skillruntime://<policy_skillruntime_id>`.
- `task_description`: task language from `target.describe` when available.
- `status`: `pending`.
- `routing`: target and policy endpoints from target config or explicit user override.
- `execution`: benchmark-appropriate `max_steps`, `replan_every_steps`, and `action_chunk_mode`.
- `timeouts`: long enough for the selected simulation benchmark.
- `safety_profile.profile`: simulation-specific profile such as `default_simulation`.
- `result`: `{}`.

Do not instantiate `SessionRunner` directly for normal benchmark work. Let the watchdog claim and execute pending sessions so results are written through the standard runtime path.

## Result Aggregation

After sessions finish, read:

- `SESSIONS.md` for final session status and `result`.
- `LOG.md` for runtime session history.
- `artifacts/runtime/<session_id>/episode.json` for benchmark episode details.

Compute at least:

- total episodes, successful episodes, and success rate.
- per-task success rate when task ids are available.
- mean steps and median steps for completed episodes.
- mean return or reward when present.
- timeout, rejected, failed, and cancelled counts.
- common `error_code` values and representative failure messages.

Use `episode.json["benchmark"]` first for benchmark-specific fields, then fall back to `result.metadata.final_status` and session-level fields.

## Report Writing

Write a Markdown experiment report in the workspace. Use a filename that includes the benchmark and date or run id, for example `BENCHMARK_REPORT_libero_spatial.md`.

Match the report style to the simulation benchmark when recognizable. For LIBERO-style benchmarks, include:

- title with benchmark name, target, policy skillruntime, and run timestamp.
- experimental setup.
- benchmark suite and task split.
- policy and runtime configuration.
- metrics.
- aggregate results table.
- per-task results table.
- failure analysis with error-code summary.
- reproducibility notes, including endpoints, session ids, max steps, replan settings, and artifact locations.

Keep raw logs in their original runtime files. The report should summarize and link to artifacts instead of duplicating full traces.
