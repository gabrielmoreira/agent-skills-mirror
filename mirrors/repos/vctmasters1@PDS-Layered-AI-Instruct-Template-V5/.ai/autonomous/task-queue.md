# Autonomous Task Queue — Schema & Lifecycle

**Status**: Scaffold, opt-in
**Backing file**: `.ai/autonomous/queue.jsonl` (gitignored; see [`.gitignore`](../../.gitignore))
**Configured by**: [`autonomy-config.yaml`](autonomy-config.yaml) → `queue:` block

> The queue is the orchestrator's only persistent state. One JSON line per goal. Last write wins for any given `goal_id`. A separate **append-only** step log lives at `.ai/logs/autonomous-YYYY-MM-DD.jsonl` — that file is **not** mutated by the queue.

---

## Contents

| Section | Purpose |
|---|---|
| [Why JSONL, not YAML](#why-jsonl-not-yaml) | Format rationale |
| [Goal Row Schema](#goal-row-schema) | Fields and types |
| [Status Lifecycle](#status-lifecycle) | State transitions |
| [Write Rules](#write-rules) | Append-only semantics |
| [Reading the Queue](#reading-the-queue) | Human and agent access |
| [Compaction](#compaction) | Archive-first cleanup |
| [Hard Rules](#hard-rules) | Non-negotiables |
| [See Also](#see-also) | Related files |

---

## Why JSONL, not YAML

- One row per line → atomic append, easy to diff, no parser ambiguity on partial writes.
- Trivially streamable by the [Observer](../../.github/agents/pds-meta-observer.agent.md).
- Crash-safe: a torn write at most corrupts the last line, recoverable by truncation.

---

## Goal Row Schema

Every line in `queue.jsonl` is a single JSON object:

```json
{
  "goal_id": "01HZX9K3M7QF2VABCDE0123456",
  "created_at": "2026-05-29T14:22:01Z",
  "updated_at": "2026-05-29T14:38:47Z",
  "user": "local",
  "goal": "Add a /healthz endpoint to the api/ module with tests.",
  "scope_path": "api/",
  "scope_authority_file": "api/.ai/instruct.md",
  "governance_refs": [".ai/governance/security.md"],
  "workflow": "feature-implementation",
  "status": "in_progress",
  "step_index": 7,
  "failure_streak": 0,
  "approval_pending": null,
  "files_modified": ["api/healthz.py", "api/tests/test_healthz.py"],
  "stats": {
    "agents_invoked": 5,
    "tokens_used_estimate": 18420,
    "wall_clock_started": "2026-05-29T14:22:05Z",
    "wall_clock_ms": 1006000
  },
  "last_step_summary": "pds-pipe-validator: PASS (2 warnings, 0 blockers)",
  "stop_reason": null,
  "lock_held": "api/"
}
```

### Field reference

| Field | Type | Required | Notes |
|---|---|---|---|
| `goal_id` | string (ULID) | yes | Lexicographically sortable; primary key |
| `created_at` | ISO 8601 UTC | yes | Set once on enqueue |
| `updated_at` | ISO 8601 UTC | yes | Refreshed on every write |
| `user` | string | yes | `"local"` for solo dev; git username when `pds-man-versioncontrol` is active |
| `goal` | string ≤500 | yes | Verbatim user prompt, sanitised of shell metacharacters |
| `scope_path` | string | yes | From [Router](../../.github/agents/pds-meta-router.agent.md) |
| `scope_authority_file` | string | yes | The deepest `.ai/instruct.md` that won |
| `governance_refs` | string[] | yes | May be empty `[]` |
| `workflow` | string \| null | no | Key from `autonomy-config.yaml.workflows`, or null for ad-hoc |
| `status` | enum | yes | See [Status Lifecycle](#status-lifecycle) |
| `step_index` | int ≥0 | yes | Mirrors the step log; monotonic per goal |
| `failure_streak` | int 0–3 | yes | Resets on success; halts run at 3 |
| `approval_pending` | object \| null | yes | `{ agent, planned_input, requested_at }` when `status == awaiting_approval` |
| `files_modified` | string[] | yes | Workspace-relative paths; archive entries excluded |
| `stats` | object | yes | See subfields below |
| `last_step_summary` | string ≤200 | yes | Human-readable trailer |
| `stop_reason` | string \| null | yes | Populated only when `status` is terminal |
| `lock_held` | string \| null | yes | Scope path locked via `pds-man-versioncontrol`, if any |

`stats` subfields: `agents_invoked` (int), `tokens_used_estimate` (int), `wall_clock_started` (ISO 8601), `wall_clock_ms` (int).

---

## Status Lifecycle

```
                  ┌──────────────┐
       enqueue →  │   pending    │
                  └──────┬───────┘
                         │ pre-flight passes
                         ▼
                  ┌──────────────┐  approval needed   ┌────────────────────┐
                  │ in_progress  │ ─────────────────► │ awaiting_approval  │
                  └──┬─────┬─────┘ ◄───── approved ── └────────┬───────────┘
                     │     │                                   │ denied / timeout
       success ──────┘     └──── stop condition                ▼
           ▼                                          ┌────────────────┐
     ┌──────────┐    ┌──────────┐    ┌─────────┐      │ paused_timeout │
     │ completed│    │ aborted  │    │ paused  │      │     denied     │
     └──────────┘    └──────────┘    └────┬────┘      └────────────────┘
                                          │ /ai-autonomous-resume
                                          ▼
                                    in_progress
```

| Status | Terminal? | Meaning |
|---|---|---|
| `pending` | no | Enqueued, pre-flight not yet run |
| `in_progress` | no | Loop is iterating |
| `awaiting_approval` | no | Paused on a human gate |
| `paused` | no | Halted by user or sentinel; resumable |
| `paused_timeout` | no | Approval timer expired; resumable |
| `completed` | yes | All planned stages succeeded |
| `aborted` | yes | Stop condition fired (failure streak, safety, budget) |
| `denied` | yes | User explicitly rejected an approval gate |

Terminal rows are kept for audit. Cleanup is a manual user task; the orchestrator never deletes queue rows.

---

## Write Rules

1. **Append on enqueue.** New goals are added as a fresh line. Never edit existing lines to insert.
2. **Update by re-append.** Any state change appends a new line with the same `goal_id`. Readers reduce by `goal_id` taking the **last** occurrence — same model as the audit log.
3. **One write per loop iteration.** The orchestrator persists exactly once per step, after the agent invocation completes (or fails).
4. **No multi-goal transactions.** Each `goal_id` is independent.
5. **Never write secrets.** `goal`, `last_step_summary`, and `approval_pending.planned_input` are sanitised: no `password=`, no `Bearer `, no `-----BEGIN`. The orchestrator drops the run with `safety_violation` if a sanitiser regex matches.

---

## Reading the Queue

For humans:

```pwsh
# Latest state of every goal
Get-Content .ai/autonomous/queue.jsonl `
  | ConvertFrom-Json `
  | Group-Object goal_id `
  | ForEach-Object { $_.Group | Select-Object -Last 1 } `
  | Format-Table goal_id, status, step_index, last_step_summary
```

For agents: invoke `pds-meta-observer` with `source: queue` — it returns the reduced view plus a streak/anomaly digest.

---

## Compaction

The queue is **not auto-compacted**. When it grows uncomfortable:

1. Run `/ai-archive .ai/autonomous/queue.jsonl` — archive-first, never-delete.
2. Start a fresh `queue.jsonl` containing only **non-terminal** rows from the archive.

The archive path follows the standard mirror rule: `.ai/.old/autonomous/queue-YYYY-MM-DD-HHMMSS.jsonl`.

---

## Hard Rules

- The queue is the **only** mutable state file the orchestrator writes (besides the append-only step log).
- Terminal rows are immutable. A re-run produces a **new** `goal_id`, never reuses an old one.
- The file is gitignored. Do not commit it; do not check in machine-specific run history.
- A missing `queue.jsonl` is fine — the orchestrator creates it on first enqueue.
- A corrupt last line is recoverable: drop it. A corrupt earlier line halts the orchestrator (it cannot prove which goal is current).

---

## See Also

- [`orchestrator.md`](orchestrator.md) — how the queue is read/written each iteration
- [`safety-guardrails.md`](safety-guardrails.md) — what halts a run
- [`autonomy-config.yaml`](autonomy-config.yaml) — `queue:` configuration block
- [Maintenance: archive-first](../maintenance.md) — governs the compaction step
