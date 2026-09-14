# skills/runtime

`crate::skills::runtime` owns execution of installed `SKILL.md` skills.
`skill_runtime` is the stable RPC/CLI namespace (registered through
`all_skill_runtime_registered_controllers()` in `core/all.rs`); the
directory rename did not change it.

Responsibilities:

- Start a skill run in the background and cancel an in-flight one.
- List recent runs and read run-log slices.
- Resolve the reusable Node/Python runtimes before script-backed skills run.
- Define the built-in `skill_executor` delegate agent.

A run is an `orchestrator` `Agent` built per run
(`Agent::from_config_for_agent_with_profile(&config, "orchestrator", ..)`),
given the skill body as its task prompt, capped at
`WORKFLOW_RUN_MAX_ITERATIONS`, and raced against the cancellation token
registered in `run_log`. Progress events drain to the run log; the footer
records `DONE`, `FAILED`, `CANCELLED`, or `DEGENERATE`.

The same `spawn_workflow_run_background` / `await_run_outcome` pair backs the
`skills_run` / `skills_cancel` / `skills_recent_runs` / `skills_read_run_log`
controllers in `skills/schemas/` and the `run_workflow` / `await_workflow`
agent tools in `agent/tools/run_workflow.rs`, so RPC and tool callers share
one spawn path.

It reuses, rather than duplicates:

- `crate::runtime::node` (`NodeBootstrap`) and `crate::runtime::python`
  (`PythonBootstrap`) for interpreter resolution.
- `crate::skills::registry` for skill lookup and required-input checks,
  `crate::skills::preflight` for the `[github]` gate, `crate::skills::run_log`
  for log paths, cancellation tokens, and run scanning, and
  `crate::skills::schemas::resolve_workspace_dir`.

## Key files

| File | Purpose |
| --- | --- |
| `mod.rs` | Facade: gates the real modules behind the `skills` feature, re-exports the run machinery and controller aggregators, or pulls in `stub` |
| `ops.rs` | `RuntimeRequirement` (`all` / `node` / `python`) and `resolve_runtimes` returning `ResolveRuntimesOutcome` |
| `run_machinery.rs` | `spawn_workflow_run_background[_with_profile]`, `WorkflowRunStarted`, `await_run_outcome` |
| `schemas.rs` | `skill_runtime` controllers: `run`, `cancel`, `recent_runs`, `read_run_log`, `resolve_runtimes`, `schemas` |
| `tools.rs` | `SkillRuntimeResolveRuntimesTool` (`skill_runtime_resolve_runtimes`), re-exported through `tools/mod.rs` under the `skills` gate |
| `stub.rs` | Disabled-feature facade: only the two controller aggregators, both returning empty vectors |
| `agent/skill_executor/` | `agent.toml`, `prompt.md`, and `prompt.rs` for the `skill_executor` agent (delegate name `run_skill`); registered in `agent/registry/agents/loader.rs` and listed as an orchestrator delegate |

## Compile-time gate (`skills` feature)

`pub mod runtime;` in `skills/mod.rs` stays ungated because it is a facade.
`agent`, `ops`, `run_machinery`, `schemas`, and `tools` are compiled only
with the default-on `skills` Cargo feature (the same gate as `skills` and
`skills::catalog`). With the feature off, `stub.rs` supplies
`all_skill_runtime_registered_controllers` and
`all_skill_runtime_controller_schemas` as empty lists, so the namespace is
absent from `/schema` and unknown over `/rpc`. Every other caller of the run
machinery is behind the same feature, so the stub owes nothing else;
`cargo check --no-default-features` is what catches signature drift.

Smoke examples:

```bash
openhuman-core skill_runtime schemas
openhuman-core skill_runtime resolve_runtimes --runtime all
openhuman-core skill_runtime run --skill_id git-helper --inputs '{}'
openhuman-core skill_runtime recent_runs --limit 10
```
