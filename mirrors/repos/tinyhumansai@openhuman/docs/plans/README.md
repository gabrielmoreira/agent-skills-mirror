# `docs/plans/`

Cross-repository work plans for the agent-runtime migration, plus one dated
measurement that was filed here by mistake. The normative boundary these plans
implement is [`../specs/agent-runtime-upstream-boundary.md`](../specs/agent-runtime-upstream-boundary.md).

A plan here exists because the work spans OpenHuman and one or more vendored
submodules and cannot be owned accurately by a single source directory. Durable
architecture belongs in [`gitbooks/developing/architecture/`](../../gitbooks/developing/architecture/README.md) and in the
beside-code `crates/openhuman-core/src/<domain>/README.md` (see [`crates/README.md`](../../crates/README.md)), not here.

## Status, verified 2026-10-07

Checked against the tree rather than against each plan's own status line,
because several of those lines no longer hold.

| Plan | Status |
| --- | --- |
| [`extract-remaining-harness-session-and-subagent-runner.md`](./extract-remaining-harness-session-and-subagent-runner.md) | **Landed.** `agent/harness/{session,subagent_runner,run_queue}/` and `agent/task_dispatcher/` are all deleted; `agent/session_host/` and `agent/subagent_host/` replaced them. |
| [`migrate-agent-sessions-to-tinyagents-session.md`](./migrate-agent-sessions-to-tinyagents-session.md) | **Landed.** The transcript model and JSONL codec live in `vendor/tinyagents/crates/tinyagents-session/src/transcript/`. |
| [`migrate-agent-runtime-helper-packages.md`](./migrate-agent-runtime-helper-packages.md) | **Landed.** All four slices are complete; what remains host-side is what the plan prescribes keeping. |
| [`migrate-agent-orchestration-to-tinyagents.md`](./migrate-agent-orchestration-to-tinyagents.md) | **Landed except O6.** `tinyagents-orchestration/src/` holds `subagent/`, `teams/` and `workflow/`; there is no `parallel/`. |
| [`migrate-agent-runtime-to-tinyagents.md`](./migrate-agent-runtime-to-tinyagents.md) | **Live.** Tasks 4, 10 and 11 are outstanding: 25 `task_local!` declarations remain in the core, and `agent/tinyagents/harness_assembly.rs` and `agent/tinyagents/turn_runner.rs` both still exist with live callers. |
| [`migrate-agent-runtime-waves.md`](./migrate-agent-runtime-waves.md) | **Live.** Gate 4 is unmet: [`scripts/ci/agent-runtime-boundary-baseline.json`](../../scripts/ci/agent-runtime-boundary-baseline.json) is still checked in, with 213 baselined violations, and the gate requires it deleted. |
| [`jev-tool-search-baseline.md`](./jev-tool-search-baseline.md) | **Not a plan.** A dated measurement report (2026-09-22) for `tool_search` ranking. It is linked from the root [`README.md`](../../README.md), [`crates/openhuman-tinyhumans/src/jev/README.md`](../../crates/openhuman-tinyhumans/src/jev/README.md) and [`gitbooks/developing/jev.md`](../../gitbooks/developing/jev.md), so its path is a contract; leave it where it is. |

Delete the four landed plans, and the spec with them, once Task 4, Tasks 10 and
11, Gate 4 and O6 are closed. Until then they are the record of what was moved
and why, and the two live plans point at them.

## Reproducing the status check

```bash
# landed trees are gone, their replacements are present
ls crates/openhuman-core/src/agent/harness/            # no session/ subagent_runner/ run_queue/
ls crates/openhuman-core/src/agent/session_host/ crates/openhuman-core/src/agent/subagent_host/

# O6
ls vendor/tinyagents/crates/tinyagents-orchestration/src/

# Task 4
grep -rn 'task_local!' crates/openhuman-core/src --include='*.rs' | grep -v _tests | wc -l

# Tasks 10 and 11
ls crates/openhuman-core/src/agent/tinyagents/harness_assembly.rs \
   crates/openhuman-core/src/agent/tinyagents/turn_runner.rs

# Gate 4
python3 -c "import json;print(len(json.load(open('scripts/ci/agent-runtime-boundary-baseline.json'))))"
```

## Further reading

- [Agent harness](../../gitbooks/developing/architecture/agent-harness.md) and the [`agent` domain](../../crates/openhuman-core/src/agent/README.md).
- [`vendor/tinyagents/`](../../vendor/tinyagents) and its repo, [tinyhumansai/tinyagents](https://github.com/tinyhumansai/tinyagents).
- [`AGENTS.md`](../../AGENTS.md) for the submodule ownership rules these plans follow.
