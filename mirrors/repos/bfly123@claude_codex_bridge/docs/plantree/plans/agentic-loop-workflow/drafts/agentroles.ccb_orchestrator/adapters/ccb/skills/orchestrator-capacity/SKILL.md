---
name: orchestrator-capacity
description: Private CCB orchestrator skill for requesting, inspecting, using, and releasing dynamic loop capacity through `ccb loop capacity` only.
---

# Orchestrator Capacity

Use this skill when a loop round needs temporary execution nodes, when
capacity state is unclear, or when loop-owned nodes should be released after
round drain.

The skill is a permission boundary and capacity requests are advisory until
the CCB command returns concrete generated agent names. It lets the
orchestrator request configured capacity without granting authority over
`.ccb/ccb.config`, `.ccb/runtime`, tmux, provider processes, daemon
supervision, or raw reload/kill commands.

Use this skill only from an execution-ready loop round. If the task packet,
review, verification contract, or loop id is missing, return `replan_required`
or `blocked` instead of requesting capacity.

## Inputs

Required:

- loop id
- requested profile counts, for example `worker=1` and `code_reviewer=1`
- task/work graph or task-packet reference
- acceptance and verification references
- lifetime expectation, normally `current_round`

Optional:

- current capacity summary reference
- planner policy for serial fallback
- previous capacity command JSON

## Ensure Capacity

Call exactly the narrow CCB surface:

```bash
ccb loop capacity ensure --loop-id <id> --profile worker=1 --profile code_reviewer=1 --json
```

For different ready plans, replace only profile counts that are declared in
`[loop.role_profiles]`. Total requested nodes must stay within the configured
`[loop.capacity].max_nodes` limit and must never exceed four.

After ensure:

- parse JSON output;
- require `loop_capacity_status = "ensured"`;
- require `apply.apply_status = "applied"` for live capacity, or
  `apply.apply_status = "deferred_until_start"` only when reporting planned
  capacity without dispatching;
- use returned agent names as the only dynamic ask targets;
- treat returned `node_id`, `window_name`, `resolved_window_name`, or
  `placement` fields as CCB-owned evidence only, not as values to select,
  rewrite, or hand off to raw layout commands;
- if rejected, blocked, retained, or failed fields exist, report them as loop
  blockers instead of continuing as success.

Do not invent names from `name_template`. Returned JSON is the source of truth.
Do not invent node windows such as `node-<loop-id>-<node-id>` yourself. The CCB
runtime layout manager owns window naming, pane placement, and any overflow or
cleanup behavior.
Do not use `ccb loop run-once`; that is an external deterministic runner, not
the autonomous orchestrator path.

## Dispatch With Returned Targets

Only after ensure returns concrete names, create bounded asks.

Worker ask requirements:

- one clear goal;
- exact scope and non-goals;
- referenced task packet and acceptance criteria;
- forbidden fallback/degradation list;
- expected artifacts and verification evidence;
- explicit response schema: `done`, `blocked`, or `needs_rework`.

Checker ask requirements:

- worker result or artifact reference;
- acceptance criteria and verification reference;
- check plan;
- fallback/degradation audit;
- explicit response schema: `pass`, `rework_required`, `blocked`, or
  `non_converged`.

Use `ask` targets from ensure output. Do not target static default names unless
the JSON explicitly reports a pinned or reused agent with that name.

When the child result is needed to continue the round, submit with callback and
then stop until CCB resumes the task:

```bash
command ask --callback "$WORKER_AGENT" <<'EOF'
<bounded worker request>
EOF
```

After the worker callback resumes the orchestrator, submit the reviewer ask the
same way:

```bash
command ask --callback "$REVIEWER_AGENT" <<'EOF'
<bounded reviewer request with worker result/artifact refs>
EOF
```

## Status

When progress is unclear or before release, inspect capacity:

```bash
ccb loop capacity status --loop-id <id> --json
```

Use status to report generated agents, profile, provider, role, lifetime,
state, blockers, retained agents, and whether the loop can release.

For visual/runtime diagnosis only, you may inspect the read-only layout view:

```bash
ccb layout status --json
```

Use it to confirm loop-owned panes are reported with `source=loop` and the
expected `loop_id`/`node_id`. Do not use layout status to choose agent names,
write placement, or repair tmux state.

For non-loop temporary helpers, brokers, planner/frontdesk companions, or
diagnostic agents, use the `dynamic-agent-lifecycle` skill instead of this
loop-capacity skill.

## Release

After the worker/checker branch is drained, release only idle loop-owned
capacity:

```bash
ccb loop capacity release --loop-id <id> --policy auto --json
```

If release reports retained agents, treat them as active blockers or handoff
items. Do not force unload busy nodes.

## Forbidden

Never:

- edit `.ccb/ccb.config`;
- write `.ccb/runtime`, `.ccb/agents`, lifecycle, lease, socket, pid, mailbox,
  pane, or provider-state files directly;
- call `ccb agent add --window`, `ccb agent add --window-class`, or other raw
  agent placement commands for loop execution capacity;
- call raw `ccb reload`;
- call raw `ccb kill`;
- run `tmux` commands;
- start, stop, kill, or respawn provider processes directly;
- invent provider/model/thinking/workspace values outside configured
  `loop.role_profiles`;
- request undeclared profiles;
- exceed `max_nodes`, profile `max_instances`, or four total nodes;
- silently run fewer nodes and call the round successful;
- bypass checker or round-checker gates;
- convert partial, blocked, or non-converged work into done.

## Failure Handling

If ensure, status, dispatch, review, or release cannot converge:

1. stop local escalation;
2. summarize the blocker, command output, returned agent names, and affected
   work items;
3. return `blocked`, `partial`, or `replan_required` to planner/frontdesk through
   the loop runner;
4. keep unrelated drained branches separate from the failed branch.
