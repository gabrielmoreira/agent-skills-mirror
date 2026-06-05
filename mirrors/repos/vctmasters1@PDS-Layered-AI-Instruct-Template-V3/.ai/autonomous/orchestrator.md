# Autonomous Orchestrator — Scaffold

**Status**: Experimental, opt-in, **disabled by default**
**Configured by**: [`autonomy-config.yaml`](autonomy-config.yaml)
**Slash command**: [`/ai-autonomous-start`](../../.github/prompts/ai-autonomous-start.prompt.md)

> The orchestrator is **not a new agent persona**. It is a thin loop that composes the **existing 19 agents** (pipe → man → meta) into a bounded autonomous run. It owns no new authority; it only sequences calls and gates them.

---

## Contents

| Section | Purpose |
|---|---|
| [Role & Boundaries](#role--boundaries) | What the orchestrator does and refuses to do |
| [Pre-Flight Contract](#pre-flight-contract) | Mandatory checks before step 0 |
| [The Loop](#the-loop) | Step-by-step execution model |
| [Agent Selection](#agent-selection) | How to pick the next agent from `allowed_agents` |
| [Approval Gates](#approval-gates) | Human-in-the-loop semantics |
| [State & Persistence](#state--persistence) | How runs survive interrupts |
| [Stop & Resume](#stop--resume) | Halt conditions and `/ai-autonomous-resume` |
| [Logging Contract](#logging-contract) | What every step must record |
| [Hard Rules](#hard-rules) | Non-negotiables |
| [Failure Modes](#failure-modes) | What to do when things go wrong |

---

## Role & Boundaries

The orchestrator is a **bounded conductor**.

It MAY:

- Read [`autonomy-config.yaml`](autonomy-config.yaml) and treat it as authoritative for limits, safety, and the agent palette.
- Resolve a user goal into a sequence of agent invocations drawn **only** from `allowed_agents`.
- Call the [Router](../../.github/agents/pds-meta-router.agent.md) first to obtain `scope_path` + governance refs.
- Call the [Supervisor](../../.github/agents/pds-pipe-super.agent.md) to run the SDLC pipeline within that scope.
- Persist progress to the [task queue](task-queue.md) and the autonomous step log.
- Stop on any condition listed in [`safety-guardrails.md`](safety-guardrails.md).

It MUST NOT:

- Edit any source file directly. **Only the agents it dispatches edit files.**
- Edit `.ai/instruct.md`, `.ai/index.md`, or anything under `.ai/governance/`. Those changes go through `pds-man-curator` driven by a human.
- Bypass `human_approval.mode`. If the mode says `always`, every hand-off pauses.
- Exceed any limit in `autonomy-config.yaml.limits`.
- Invoke an agent not present in `autonomy-config.yaml.allowed_agents`.
- Author secrets, modify `.env`, run destructive DB operations, or force-push.
- Continue while [`.ai/PAUSE`](../PAUSE.example) exists.

If the user asks for something outside these boundaries, the orchestrator REPORTS the constraint and stops. It never silently broadens its own permissions.

---

## Pre-Flight Contract

Before step 0, run this checklist. **Failure of any item aborts the run.**

1. **Master switch**: `autonomy-config.yaml.enabled == true`. If false → emit a one-line refusal pointing the user to this file and exit.
2. **Pause sentinel**: `.ai/PAUSE` does not exist.
3. **Goal validity**: the goal string is non-empty and ≤500 characters; contains no shell metacharacters that would survive into a tool call.
4. **Queue capacity**: pending goals < `queue.max_pending_goals`.
5. **Scope resolution**: invoke `pds-meta-router` once with the goal. Capture `scope_path`, `scope_authority_file`, `governance_refs[]`. If no scope can be resolved, **stop** and ask the user to narrow the goal.
6. **Safety profile**: load `.ai/agent-config.yaml` safety block plus this file's `safety:` block. The **stricter** of the two wins for every field.
7. **Branch/lock check** (when version control is in use): call `pds-man-versioncontrol` to verify the current branch is appropriate and no other developer holds the scope lock.
8. **Allocate `goal_id`**: ULID written to the queue with `status: "pending"`.
9. **Emit step 0 log entry** with `outcome: "preflight_passed"`.

Only after all 9 succeed does the loop start.

---

## The Loop

Pseudocode (the orchestrator is markdown, but a future Python engine would follow this exactly):

```text
state = load_or_create(goal_id)
while state.step_index < limits.max_steps:
    if any stop_condition triggered: persist(state); halt
    if heartbeat_due: run heartbeat (re-read scope authority + safety)

    next_agent = select_next_agent(state, allowed_agents)
    if next_agent is None: persist(state, status="completed"); halt

    if requires_approval(next_agent, state):
        outcome = request_human_approval(next_agent, planned_input)
        if outcome != "approved": persist(state, status="paused"); halt

    result = invoke(next_agent, planned_input)
    log_step(state, next_agent, result)

    if result.outcome == "BLOCK":
        if state.failure_streak >= 2: persist(state, status="aborted"); halt
        state.failure_streak += 1
        continue

    state.failure_streak = 0
    state.step_index += 1
    persist(state)
```

Key properties:

- **Single-threaded** while `max_parallel_workers == 1` (the default). The loop never fans out.
- **Idempotent persistence**: every iteration writes state before requesting the next agent. A crash mid-step never loses the queue.
- **Heartbeat-aware**: every `heartbeat_interval` steps (from `.ai/agent-config.yaml`), re-read `scope_authority_file` and `safety-guardrails.md` before continuing. Drift triggers a stop.

---

## Agent Selection

The orchestrator does not improvise. It picks the next agent from a small decision table:

| State of the run | Next agent | Why |
|---|---|---|
| Step 0 just passed pre-flight | `pds-meta-router` | resolve scope (already done in pre-flight, but re-confirm if goal mutated) |
| Scope resolved, no plan yet | `pds-pipe-super` | the supervisor decides the worker pipeline |
| Supervisor handed back a stage request | the requested `pds-pipe-*` worker | follow the supervisor's plan |
| New identifier needed (file, endpoint, table, error code, config var) | `pds-man-naming` | mandatory consultation before creation |
| Port allocation needed | `pds-man-ports` | registry consultation |
| Branch/PR/merge needed | `pds-man-versioncontrol` | scope lock + merge gates |
| Pure read-only Q&A from the user mid-run | `pds-meta-explorer` | non-mutating |
| End-of-run summary | `pds-meta-observer` | emit metrics digest |

If no row matches, **stop** and ask the user. Do not invent a new agent.

---

## Approval Gates

Approval semantics follow `human_approval.mode` in `autonomy-config.yaml`:

| Mode | When the loop pauses |
|---|---|
| `always` | Before every hand-off |
| `on_medium` | Before any agent whose planned action is `safety_level: medium` or `high` |
| `on_high` | Before any agent whose planned action is `safety_level: high` |
| `never` | Only on the hard stop conditions |

When pausing, the orchestrator:

1. Persists state with `status: "awaiting_approval"`.
2. Emits a structured prompt to the user with: agent name, planned input summary (≤200 chars), affected paths, safety level.
3. Waits up to `approval_timeout_minutes`. On timeout → halt with `status: "paused_timeout"`. The user resumes with `/ai-autonomous-resume <goal_id>`.

A denied approval is **terminal** for the run. The user must restart with a refined goal.

---

## State & Persistence

State is one row in [`task-queue.md`](task-queue.md)'s JSONL file plus the running step log. The orchestrator writes:

- `queue.jsonl` — goal-level state (one line per goal, last write wins).
- `logs/autonomous-YYYY-MM-DD.jsonl` — append-only step log.

Crash recovery: on restart, `/ai-autonomous-resume` reads the queue, finds the row whose `status ∈ {paused, awaiting_approval, paused_timeout}`, replays the last logged step's outcome, and continues from there.

The orchestrator NEVER edits a step log entry retroactively. To correct a record, append a new entry with `outcome: "correction"` and a `corrects_step_index` field.

---

## Stop & Resume

Halt is graceful. Every halt path:

1. Sets the queue row's `status` to one of: `completed | aborted | paused | paused_timeout | denied`.
2. Writes a final step log entry with `outcome` matching the halt reason.
3. Emits a one-screen summary: total steps, files modified, agents invoked, next user action.
4. Releases any scope locks acquired by `pds-man-versioncontrol` IF `status ∈ {completed, aborted, denied}`. Paused runs keep their lock so the user's branch state is preserved.

`/ai-autonomous-resume <goal_id>` reloads state, runs pre-flight again (the pause sentinel may have appeared, the user may have committed since), and re-enters the loop.

---

## Logging Contract

Every step log entry MUST satisfy `autonomy-config.yaml.logging.required_fields`. Missing fields are treated as a logging failure → orchestrator halts with `outcome: "log_failure"`.

The observer agent reads these files under `/ai-metrics` and `/ai-observe`; broken schema breaks observability, hence the hard halt.

---

## Hard Rules

- **Disabled by default.** `enabled: false` is the shipped state. Refusing to run is the correct behavior.
- **No new authority.** The orchestrator's authority is the **intersection** of `autonomy-config.yaml`, `.ai/agent-config.yaml`, and the resolved `scope_authority_file`.
- **No silent expansion.** Adding to `allowed_agents` requires a code edit, a `/ai-reflect` entry, and a human commit.
- **Heartbeat is non-negotiable.** Skipping a heartbeat is a halt condition.
- **PAUSE sentinel beats everything.** If `.ai/PAUSE` appears mid-run, the next iteration halts before any agent invocation.
- **Single goal at a time.** `max_parallel_workers == 1` until a future revision proves multi-goal safe.
- **Logs are append-only.** No mutation, no deletion. Rotation is the user's responsibility.

---

## Failure Modes

| Failure | Action |
|---|---|
| Pre-flight check fails | Refuse to start; emit one-line reason |
| Agent returns `BLOCK` | Increment `failure_streak`; halt at 3 |
| Agent attempts forbidden write | Halt immediately; log `outcome: "safety_violation"` |
| `.ai/PAUSE` appears mid-run | Halt at next iteration; status `paused_sentinel` |
| Approval timeout | Halt with `paused_timeout`; queue row preserved |
| Step log write fails | Halt with `log_failure`; do NOT continue blind |
| Heartbeat detects drift in `scope_authority_file` | Halt with `scope_drift`; ask user to re-run |
| Token/time/file budget exceeded | Halt with `budget_exceeded`; report which budget |
| Three consecutive failed steps | Halt with `failure_streak`; report last three errors |

---

## See Also

- [`autonomy-config.yaml`](autonomy-config.yaml) — limits, safety, agent palette
- [`safety-guardrails.md`](safety-guardrails.md) — full stop-condition spec
- [`task-queue.md`](task-queue.md) — queue schema and lifecycle
- [`workflow-examples/feature-implementation.md`](workflow-examples/feature-implementation.md) — worked example
- [Router](../../.github/agents/pds-meta-router.agent.md) | [Supervisor](../../.github/agents/pds-pipe-super.agent.md) | [Observer](../../.github/agents/pds-meta-observer.agent.md)
