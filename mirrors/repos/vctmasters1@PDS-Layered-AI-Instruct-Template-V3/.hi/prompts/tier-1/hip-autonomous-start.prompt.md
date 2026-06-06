---
mode: agent
description: Start a bounded autonomous run via the autonomous orchestrator. Refuses unless `.hi/autonomous/autonomy-config.yaml` has `enabled: true`. Disabled by default.
---

# /hip-autonomous-start

Hand a goal to the **lightweight autonomous orchestrator**. The orchestrator composes the existing 23-agent network (it adds no new authority) and runs it under hard limits, human-in-the-loop gates, and the project's standing safety contracts.

> **Disabled by default.** This command refuses to run unless `.hi/autonomous/autonomy-config.yaml` has `enabled: true`. That is intentional.

> **→ [Orchestrator](../../autonomous/orchestrator.md)** — the loop
> **→ [Config](../../autonomous/autonomy-config.yaml)** — limits, approval mode, agent palette
> **→ [Safety](../../autonomous/safety-guardrails.md)** — halt conditions
> **→ [Queue](../../autonomous/task-queue.md)** — persistent state
> **→ [Example](../../autonomous/workflow-examples/feature-implementation.md)** — worked walkthrough

---

## Contents

| Section | What's here |
|---------|-------------|
| [Usage](#usage) | Command syntax and goal rules |
| [Steps](#steps) | Pre-flight, run, approval, report |
| [Refusal Matrix](#refusal-matrix) | When the command refuses |
| [Hard Rules](#hard-rules) | Standing safety constraints |
| [See Also](#see-also) | Related commands |

---

## Usage

```text
/hip-autonomous-start "<goal in one sentence>"
```

Examples:

```text
/hip-autonomous-start "Add a /healthz endpoint to api/ with a unit test."
/hip-autonomous-start "Document the port registry workflow in docs/."
```

The goal must be:

- One sentence, ≤500 characters.
- Scoped to a single module when possible (the router will refuse ambiguous scopes).
- Free of secrets (sanitiser regexes in [`safety-guardrails.md`](../../autonomous/safety-guardrails.md) reject these).

---

## Steps

### 1. Pre-flight refusal check

- Read [`.hi/autonomous/autonomy-config.yaml`](../../autonomous/autonomy-config.yaml).
- If `enabled: false` (the default), emit:
  ```
  Autonomous mode is DISABLED. To enable, edit .hi/autonomous/autonomy-config.yaml and set `enabled: true`.
  Read first: .hi/autonomous/safety-guardrails.md, .hi/autonomous/orchestrator.md.
  ```
  Then **exit**. Do not proceed under any circumstances.

### 2. Validate the goal

- Must be non-empty and ≤500 chars.
- Run sanitiser regexes from [`safety-guardrails.md`](../../autonomous/safety-guardrails.md). Match → refuse with `safety_violation` and exit.
- Reject shell metacharacters that would survive into a tool call.

### 3. Hand to the orchestrator

Invoke the orchestrator's pre-flight contract (`orchestrator.md` → "Pre-Flight Contract"). The orchestrator will:

1. Confirm `.hi/PAUSE` is absent.
2. Check queue capacity.
3. Call [`hia-router`](../../agents/tier-1/hia-router.agent.md) once to resolve `scope_path` + governance refs.
4. Compose the strictest safety profile from `agent-config.yaml`, `autonomy-config.yaml`, and the resolved `scope_authority_file`.
5. Acquire a scope lock via [`hia-versioncontrol`](../../agents/tier-2/specialists/hia-versioncontrol.agent.md) if multi-developer mode is active.
6. Allocate a `goal_id` (ULID) and append a `pending` row to `.hi/autonomous/queue.jsonl`.
7. Emit step 0 to the autonomous step log.

Any pre-flight failure aborts. Report the exact failing check.

### 4. Run the loop

Execute the orchestrator loop per [`orchestrator.md`](../../autonomous/orchestrator.md) → "The Loop". Honour:

- `human_approval.mode` (default `always` — pause before every hand-off).
- `limits.*` ceilings (default 25 steps / 30 minutes / 20 files).
- All stop conditions in [`safety-guardrails.md`](../../autonomous/safety-guardrails.md).
- Heartbeat re-reads of the scope authority file and this guardrails file.

Agents may only be drawn from `autonomy-config.yaml.allowed_agents`. Any attempt to invoke `hia-curator`, `hia-learner`, or anything else listed under `forbidden:` is a terminal halt.

### 5. Approval gates

When the loop pauses for approval, present:

```
Goal:           <goal>
Goal ID:        <ulid>
Step:           <n>/<max>
Next agent:     <agent name>
Planned input:  <≤200 char summary>
Affected paths: <comma-separated workspace paths>
Safety level:   low | medium | high

Approve? (yes / no / details)
```

Wait up to `human_approval.approval_timeout_minutes`. Timeout → `paused_timeout`, queue preserved, exit with resume instructions.

### 6. Final report

On any terminal status (`completed | aborted | denied`) or pause (`paused | paused_timeout | awaiting_approval`):

- Print the queue row's final state (status, step_index, files_modified, stop_reason, last_step_summary).
- Print the file paths of the autonomous step log and the queue.
- Print the resume command if applicable: `/hip-autonomous-resume <goal_id>`.
- Release scope locks per [`orchestrator.md`](../../autonomous/orchestrator.md) → "Stop & Resume".

---

## Refusal Matrix

| Condition | Response |
|---|---|
| `autonomy-config.yaml.enabled == false` | Refuse with the exact message above. Exit. |
| `.hi/PAUSE` exists | Refuse: "Pause sentinel present. Remove `.hi/PAUSE` to enable autonomous runs." |
| Goal sanitiser hit | Refuse: `safety_violation` — secret pattern detected in goal. |
| Queue at `max_pending_goals` and `on_overflow: reject` | Refuse: queue full; finish or archive an existing goal first. |
| Router cannot resolve scope | Refuse: ask the user to narrow the goal to a single module path. |
| Repository has uncommitted destructive changes | Refuse: ask the user to commit or stash first. |

---

## Hard Rules

- This command **never** edits files itself. Only the agents it dispatches edit files.
- This command **never** flips `enabled: true` for the user. Enabling is a deliberate human edit.
- This command **never** invokes `hia-curator` or `hia-learner`.
- This command **never** runs in parallel with another autonomous goal — the queue rejects overflow.
- This command honours every standing contract: archive-first, never-reset-db, credential isolation, host isolation, depth-priority instructions.

---

## See Also

- [`/hip-route`](hip-route.prompt.md) — single-shot routing without the autonomous loop
- [`/hip-foresight`](hip-foresight.prompt.md) — pre-action gap analysis (recommended before enabling autonomous mode)
- [`/hip-reflect`](hip-reflect.prompt.md) — post-run reflection that proposes governance edits
- [`/hip-metrics`](hip-metrics.prompt.md) | [`/hip-observe`](hip-observe.prompt.md) — observe an autonomous run after the fact
