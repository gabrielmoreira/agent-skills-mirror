# Subagent host

OpenHuman adapters over the neutral TinyAgents sub-agent lifecycle. Given an
`AgentDefinition` and a task prompt, the runner reads the parent's task-local
`ParentExecutionContext`, resolves the child's model, filters the parent's
tool registry per the definition's `tools`, `disallowed_tools`, and
`skill_filter` (or inherits the parent's tools verbatim in fork mode), builds
a narrowed system prompt, runs the child turn on the TinyAgents harness, and
mirrors its transcript and progress back to the parent as one compact tool
result.

This module owns product policy and effects: definition resolution, prompt
assembly, tool narrowing, model selection, workspace and sandbox setup,
artifacts, checkpoints, and progress. `tinyagents_orchestration::subagent`
owns lifecycle ordering, task-key coalescing, and mutually exclusive pause or
terminal persistence; this crate does not duplicate that state machine.

## Layout

| File | Role |
| --- | --- |
| `types.rs` | `SubagentRunOptions`, `SubagentRunOutcome`, `SubagentRunError`, `SubagentMode`, `SubagentCheckpointData`, `SubagentUsage` |
| `ops/` | `run_subagent`, the typed and fork execution modes, and the TinyAgents graph route |
| `lifecycle.rs` | `run_subagent`, `run_subagent_with_parent`, `continue_subagent`, checkpoint load/save, `OpenHumanSubagentHost` |
| `handoff.rs` | Oversized tool-result cache and hygiene, shared with `extract_tool.rs` |
| `extract_tool.rs` | The `extract_from_result` tool for direct provider extraction over a cached handoff |
| `tool_prep.rs` | Tool filtering, prompt loading, and the text-mode protocol block |
| `autonomous.rs` | Iteration-cap policy for autonomous (non-interactive) sub-agent runs |

`SubagentRunOptions::run_context` carries the child's `OpenHumanRunContext`
explicitly; recursive execution passes this value rather than snapshotting
task-local scopes after a `tokio::spawn`, since task-local state does not
survive that boundary on its own.

## Handoff

A sub-agent's tool result can be large enough that returning it verbatim
would blow the parent's context. `HandoffMiddleware` (in TinyAgents)
intercepts an oversized result through `apply_handoff` and stores it in a
per-spawn `ResultHandoffCache`; the parent gets a small reference back, and
`extract_from_result` lets a later turn pull a specific piece of the cached
result out on demand instead of resending the whole thing.

## Where next

- `crate::agent::harness::definition` for `AgentDefinition`, `AgentTier`,
  `SandboxMode`, and the other archetype shapes this module resolves against.
- `crate::agent::orchestration` for `spawn_subagent` and the other
  user-facing tools that call into this runner.
- `crate::agent::session_host` for the parent turn that sets up the
  `ParentExecutionContext` a sub-agent reads.
- `vendor/tinyagents` (`tinyagents-orchestration::subagent`,
  `tinyagents-graph`) for the lifecycle and delegation-graph mechanics this
  module adapts rather than reimplements.
