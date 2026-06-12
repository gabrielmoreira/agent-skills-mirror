---
name: ccb-comm-reply-recover
description: Diagnose and recover CCB communication and reply delivery stalls. Use when a user reports a missing CCB_REPLY, stuck ask, agent stuck busy/delivering, queued work behind an active job, cancelled/incomplete reply, empty artifact, callback not continuing, duplicate retry after success, or a CCB mailbox/communication backend that appears stuck.
---

# CCB Comm Reply Recover

## Overview

Use this skill for user-visible "I did not receive the reply" incidents. It
combines message lineage repair with mailbox and provider-pane evidence, then
hands off to runtime recovery only when the chain evidence proves the provider
process or pane must be replaced.

Mutations must go through CCB control-plane commands. Do not directly edit
mailbox, lifecycle, lease, runtime, provider-session, artifact, or tmux
authority files.

## Core Workflow

1. Identify the target from the user's evidence:
   - `job_id`, `message_id`, `attempt_id`, `reply_id`, inbound event id, or
     artifact path when provided.
   - agent name when the user only says a target is stuck.
   - `ccb queue --detail all` when neither id nor agent is clear.
2. Trace lineage first:
   - `ccb trace <id>`
   - record message, attempt, reply, event, callback, and job states.
   - read the full artifact file before acting when a request or reply is
     artifact-backed.
3. Inspect mailbox head-of-line state:
   - `ccb queue --detail <agent>`
   - `ccb pend --inbox --detail <agent>`
   - if the requested job is queued behind an active event, trace the active
     job before touching the queued job.
4. Cross-check runtime evidence when a job is `running` or `delivering` longer
   than expected:
   - `ccb ps`
   - `ccb ping <agent>`
   - `ccb doctor logs <agent>` when provider/pane failure is plausible.
   - read-only tmux pane capture only from the socket and pane id reported by
     `ccb ps`, and only as evidence.
5. Classify the incident, choose the least disruptive repair, then re-run
   trace and queue checks.

## Incident Classes

- `normal_running`: the active job is visible in the provider pane and making
  progress. Report that it is running; do not restart or duplicate-submit.
- `head_of_line_blocked`: an active job is `running`/`delivering`, later jobs
  are queued behind it, and pane/log evidence shows stale, dead, mismatched, or
  non-progressing provider state.
- `queued_behind_active`: the user's job is not lost; it is queued behind an
  active event. Repair the active event only if evidence proves it is blocked.
- `provider_pane_stale`: CCB reports the runtime healthy, but pane text/logs
  show an old prompt, a dead/update prompt, or a request that does not match
  the active lineage.
- `empty_cancel_artifact_expected`: trace shows terminal `cancelled` with
  `cancel_info`, and the empty artifact came from an intentional cancel.
- `empty_bad_artifact`: a completed, failed, or required artifact-backed reply
  is absent, zero bytes, truncated, or unreadable without a valid cancel
  reason.
- `duplicate_retry_after_success`: a later retry or resubmission of the same
  work is still queued/running after another attempt already completed and the
  user received the needed reply.
- `callback_or_ack_stalled`: a reply exists and is acceptable, but callback or
  inbox progress did not advance.

## Repair Rules

- If trace shows the blocking job is still in flight, run
  `ccb cancel <job_id>` first when the user supplied maintenance intent. If
  cancel fails or reports a blocker, stop.
- Prefer `ccb repair retry <job_id|attempt_id>` when the same work should run
  again and the original lineage remains valid.
- Prefer `ccb repair resubmit <message_id>` when the old execution lineage is
  stale, context-corrupted, semantically wrong, or no longer suitable.
- Use `ccb repair ack <agent_name> [inbound_event_id]` only when the reply is
  already accepted and progress state is wrong.
- Cancel `duplicate_retry_after_success` jobs rather than letting an agent run
  the same review or repair twice.
- Hand off to `ccb-self-recover` for `ccb restart <agent>` only after chain
  repair clears or cancels active work and the target remains stale, dead, or
  unusable. Restart is not the first repair for a communication stall.

## Verification

After every repair:

- `ccb trace <old_job_or_message>` proves the old path is terminal, completed,
  or intentionally cancelled.
- `ccb queue --detail <agent>` and `ccb pend --inbox --detail <agent>` show no
  unexpected active head-of-line blockage.
- the desired job is completed, or a fresh valid job is queued/running with no
  duplicate path.
- artifact-backed replies are read from the full artifact file when needed.
- report intentional cancelled empty artifacts as expected maintenance output,
  not as missing user replies.

## Example Pattern

In an `archi` incident, the user reported that no architecture review reply
arrived. Trace showed one old active job stuck in `running`/`delivering`, while
later asks were queued behind it. Provider logs showed a Codex update and pane
death, but `ccb ps` still showed a bound pane. The correct repair was:

1. cancel the stale active job;
2. verify the next queued job entered the provider pane and was progressing;
3. avoid restart while valid work was running;
4. accept the completed new reply;
5. cancel the duplicate old retry that remained after success;
6. verify the target mailbox returned to idle.

## Red Lines

- Do not restart, clear, reload, or kill before tracing the message lineage.
- Do not submit a second concurrent path for the same work while the original
  path is still active unless the user explicitly retargets or duplicates the
  task.
- Do not treat observer snapshots as terminal authority; use `ccb trace`.
- Do not infer from artifact preview text when the full artifact is required.
- Do not mutate tmux directly or write CCB runtime authority files.
- Do not read provider secrets, credentials, API keys, or unrelated private
  provider state.
