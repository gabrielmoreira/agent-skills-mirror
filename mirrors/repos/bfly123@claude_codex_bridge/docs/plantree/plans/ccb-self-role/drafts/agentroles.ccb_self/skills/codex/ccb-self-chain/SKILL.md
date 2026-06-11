---
name: ccb-self-chain
description: Diagnose and repair CCB ask/job/message/reply/artifact/callback lineage. Use for missing replies, incomplete artifacts, pending callbacks, retry/resubmit/ack decisions, reply delivery problems, or work-chain resume advice.
---

# CCB Self Chain

Use this skill for message and work-lineage recovery. Do not restart or clear a
pane as the first repair for a lineage problem.

## Core Workflow

1. Identify the lineage id: `job_id`, `message_id`, `attempt_id`, `reply_id`,
   inbound event id, or artifact path.
2. Run `ccb trace <id>` and record message, attempt, reply, event, callback,
   and job state.
3. Inspect observer state as supplementary evidence:
   - `ccb queue --detail <agent|all>`
   - `ccb pend --inbox --detail <agent>`
4. If a reply or request is artifact-backed, read the full artifact file before
   acting. If the file is absent, expired, truncated, or unreadable, report a
   blocker and do not act from preview text.
5. Classify the repair:
   - retry: same job or attempt should be retried because the attempt is
     failed, incomplete, or retryable and the original lineage remains valid.
   - resubmit: original message should be submitted as fresh work because the
     old lineage is no longer appropriate.
   - ack: acknowledgement or inbox progress is wrong, but the reply is
     otherwise accepted.
6. If trace shows a job still running or in flight, run `ccb cancel <job_id>`
   first when the user intended repair, then re-run trace before choosing retry
   or resubmit. If cancel fails or reports a blocking state, stop and report
   the blocker; do not retry, resubmit, or create a second concurrent path for
   the same work.
7. Execute a repair command only when trace evidence supports it and the user
   supplied maintenance intent:
   - `ccb repair retry <job_id|attempt_id>`
   - `ccb repair resubmit <message_id>`
   - `ccb repair ack <agent_name> [inbound_event_id]`
8. After repair, re-run trace and queue/inbox checks. Success means the new or
   repaired lineage is queued/running/completed as intended, the old duplicate
   path is cancelled or terminal, and no unexpected pending reply remains. Hand
   work back to the original target agent unless the user explicitly retargets
   it.

## Decision Rules

- Prefer `repair retry` when the same target and same work should run again
  after incomplete, failed, or recoverable execution.
- Prefer `repair resubmit` when the old execution lineage is stale,
  context-corrupted, or semantically wrong but the user still wants the task
  attempted.
- Prefer `repair ack` only for bad acknowledgement/progress state after a reply
  has been accepted.
- For `project_shutdown` lineage, do not use `ack`. Explain that the project
  stopped the old execution. Prefer `repair resubmit <message_id>` when the
  user wants fresh work because `repair retry` is usually invalid after project
  shutdown. Use `repair retry <job_id|attempt_id>` only when trace explicitly
  proves the job completed before shutdown and the reply is intact.
- Handoff to `ccb-self-recover` only when trace proves process/context/pane
  replacement is required.
- Handoff to `ccb-self-diagnose` when the target id is ambiguous or runtime
  state is too uncertain to pick a lineage repair.

## Artifact Rules

Artifact-backed replies are full-text authority for the reply content. Inline
previews are hints only.

When a reply says "read the full text file above before acting":

1. Open the path.
2. Verify it is complete enough for the requested decision.
3. If expected checksum/bytes are available, compare them when cheap.
4. Only then summarize or act.

If the path is missing or expired, say that the artifact content is unavailable
and choose no mutation unless the user provides the full content again.

## Red Lines

- Do not run `ccb restart`, `ccb clear`, or `ccb reload` as the first response
  to a lineage problem.
- Do not treat queue/inbox observer snapshots as terminal authority for
  completed lineage; use `ccb trace <id>`.
- Do not repair from artifact preview text alone.
- Do not retarget work to another agent unless the user asks for that.
