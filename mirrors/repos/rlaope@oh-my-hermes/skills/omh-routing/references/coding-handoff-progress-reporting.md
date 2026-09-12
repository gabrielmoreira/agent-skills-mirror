# OMH Coding Handoff Progress Reporting

Use this reference when coding work is delegated, attached to an executor
session, or running in the background.

## Active Narration

Hermes must remain an active status narrator after it prepares or observes a
coding handoff. Immediately report the observed executor handle when available:
process/session id, PID, branch or PR target, and the prepared-vs-observed
boundary. Do not silently wait for a final result after saying an executor is
running.

## Narration Ceiling

Active does not mean continuous. Unsolicited narration is capped at roughly one
status message per meaningful transition, and at most a few per fix/verify
cycle. Report a transition, not a step.

- If nothing observable changed since the last update, say nothing.
- If an observe surface returns `unchanged_since_last_emission`, that is the
  answer; do not restate the previous update in new words.
- Do not re-list findings that were already reported. Report only what is new,
  and reference the earlier list instead of repeating it.
- Do not narrate individual tool calls, file reads, or searches.

This ceiling applies to unsolicited push narration only. When the user asks for
detail, give the full detail: an explicit request, or an explicit `--full` on an
observe surface, is never throttled.

## Progress Cadence

For long-running executor work, use an event-triggered status loop or bounded
watchdog when the wrapper exposes one, and remove it when work completes. Each
update should separate:

- prepared handoff
- dispatch or attached session
- running process
- changed files or affected area
- tests/checks started, passed, failed, or still missing
- commit, push, PR, CI, review, and merge evidence

Separate them within an update; do not send one message per bullet.

## Never Suppressed

The ceiling never applies to these. Report them the first time they occur, even
if an update was just sent:

- a blocker, failure, or failing verification
- a claim that the observed state contradicts, such as an edit reported applied
  while no file changed, or a success report alongside a non-zero exit
- the first occurrence of any new kind of event

## Parent-Owned Clarification

A delegated fanout unit never contacts the user. When one user decision blocks
it, the child preserves its work and returns `process_status: input_required`
with an `input_required` object: `decision_id` (slug), `question` and
`blocking_reason` (300 chars each), `answer_shape` (`options` with 1..8 unique
entries or `text` with `max_chars` up to 300), `affected_unit_ids` (its own
unit only), and up to 8 `redacted_context` strings. Secrets, transcripts, and
executable text are rejected at intake, and a request naming sibling units is
refused.

The dispatcher journals that unit as `blocked`, records unit status
`input_required`, skips its verification, and keeps completed siblings
completed; a dependent unit waits instead of failing. The supervising root
session is the only user surface:

```sh
omh coding fanout clarifications <fanout-id>
omh coding fanout answer <fanout-id> --unit <unit> --decision <decision-id> --attempt-id <attempt> --round <n> --answer <value>
omh coding fanout answer <fanout-id> --unit <unit> --decision <decision-id> --attempt-id <attempt> --round <n> --cancel
```

`clarifications` renders at most one question and lists the units queued
behind it. `answer` validates the value against the answer shape, records it
against the exact decision, attempt, and round, and reports `dispatch:
not_observed`; only a depth-zero root session may answer, and an answer changes
no scope or approval authority. Resuming is a separate explicit act:
`omh coding fanout dispatch ... --resume-journal <journal> --unit <unit>` reuses
the same worktree, requires unchanged lineage (run, attempt, base SHA, contract
digest, goal attempt), and appends the answer as a `[Parent decision]` block.

Terminal states are deterministic: `cancelled`, `exhausted` after two rounds,
`expired` after 24 hours, and stale answers rejected as `stale_decision_id`,
`stale_attempt_id`, or `stale_round`. Report the request as prepared, the
answer as observed only when its journal event exists, the redispatch as
observed only when its event exists, and execution and verification separately.

## Completion Verification

After completion, verify the executor self-report against local git status/log,
remote branch SHA, PR metadata, and required checks before claiming anything
landed. If a PR was already merged before follow-up commits landed, open or
prepare a follow-up PR instead of implying the merged PR contains the new fix.

## Boundary

Progress narration is not execution proof by itself. Only observed runtime
events, git state, PR metadata, checks, review records, and merge records can
satisfy their matching evidence states. Revert or follow-up commits still need
the repository's DCO and commit trailers when required.
