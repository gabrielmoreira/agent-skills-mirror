---
name: benchmarking
description: Select and run a declared Target benchmarking path, then aggregate its canonical artifacts.
metadata: {"PhyAgentOS":{"always":false,"available":true,"requires":{"runtime":{"enabled":true,"target_kind":"simulation","benchmark":true}}}}
---

# Benchmarking

Use this skill for policy evaluation, benchmark sweeps, success metrics, and experiment reports. Benchmarking always runs through a PAOS Session, Watchdog, SessionRunner, and a concrete SkillRuntime.

## Capability discovery

Read `RUNTIME.md`, `TARGETS.md`, `SKILLRUNTIME.md`, `SESSIONS.md`, and `LOG.md` before compiling a Session.

1. Select an enabled Target whose `benchmark_capabilities[].benchmark_id` and `suites` match the request.
2. Read that capability's `execution_modes`.
3. Intersect the Target's `supported_skillruntimes` with SkillRuntimes whose structured `benchmark` declaration matches the same benchmark, execution mode, Target interface, result schema, and reset owner.
4. Select one complete `(Target, execution_mode, SkillRuntime)` tuple. Never infer a mode from `runtime_kind` and never switch modes after Session creation.

Stop when no exact tuple exists. Do not call a raw Target RPC, substitute another benchmark runtime, or downgrade to a different execution mode.

## Path selection

- Select `policy_loop` when the request requires the standard PAOS observation-policy-action loop, one root Session per logical episode, or SessionVerifier evidence.
- Select `target_native` when the request requires the Target's native suite scheduler, high-throughput execution, or episode-boundary recovery. Use the benchmark-specific builtin selected above; LIBERO uses `LiberoBenchmarkSkillRuntime`, while another benchmark must declare its own concrete runtime.

`agent_exposure` only controls interactive TargetTool exposure. It does not grant or deny a builtin's typed access through `TargetSessionHandle`.

## Session construction

Every benchmark Session records `target_ref`, `skillruntime_ref`, top-level `verification_profile`, and benchmark metadata containing `benchmark_id`, `suite_id`, `execution_mode`, `policy_id`, and `run_id`.

Preserve evaluation parameters declared by the benchmark or user. Put policy
refresh cadence in `execution.replan_every_steps` (and the matching preferred
runtime hint when required by the runtime); this is the number of action steps
consumed before requesting a new policy response, not a verification retry.
Keep environment seed, control mode, and `retry_instruction_mode` in Target
configuration. `retry_instruction_mode` is `original` by default; select
`verifier_rewrite` only when recovery attempts should use the verifier's
nonempty `replan_task_description` as their policy instruction.

For `policy_loop`:

- append one root Session per task/init-state;
- set `execution.reset_policy: session_runner`;
- use a policy SkillRuntime and a policy endpoint.

For `target_native`:

- append one root Session for the complete suite/run;
- set `execution.reset_policy: skillruntime_managed`;
- use the benchmark-specific BuiltinSkillRuntime;
- put the selected task/init-state ranges in the runtime hints expected by that concrete runtime.

Verification profiles are `strict`, `audit`, and `recovery`. Do not copy provider, endpoint, timeout, retention, or budget settings into the Session; those are Agent-global configuration. Policy-loop SessionVerifier and target-native episode verification both use the Agent-owned Verification Service, but a target-native root Session is not verified again by SessionVerifier.

Append pending Sessions without modifying existing Session history. Execution must be claimed by the Watchdog; never instantiate SessionRunner or call `target.benchmark.*` directly from the Agent.

## Results

Wait for the canonical terminal Session state, then use the benchmark artifact manifest and summary. Report official `first_attempt_score` separately from `assisted_final_score`. Include configured/effective/consumed verifier budget, episode and attempt counts, recovery counts, latency, failures, and artifact references. Do not reconstruct compacted episode arrays from `SESSIONS.md`.

Write the experiment report in the workspace with the benchmark id and run id in its filename. Keep full task, episode, attempt, verifier, and failure records in their canonical artifacts rather than duplicating them into the report.
