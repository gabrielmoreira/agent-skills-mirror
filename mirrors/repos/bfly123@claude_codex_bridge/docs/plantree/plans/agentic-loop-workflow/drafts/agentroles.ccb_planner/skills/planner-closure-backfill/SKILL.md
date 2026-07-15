---
name: planner-closure-backfill
description: Produce one revision-fenced Planner backfill proposal for either a Detailer replan or task-set closure, with compact Frontdesk status evidence.
---

# Planner Closure Backfill

Use this output contract only when the controller activation mode is exactly
one of `detailer_replan` or `task_set_closure`. Initial intake remains owned by
`planner-task-packet`. Return one proposal for one activation; never combine
the two modes or substitute one mode for the other.

## Activation Modes

### `detailer_replan`

Use only the controller-provided task identity and task revision, expected
PlanTree revision, closure evidence digest, accepted facts, and supplied
Detailer/user macro-adjustment evidence. Copy those authority fields and
evidence refs exactly; do not read or infer unsupplied state.

Preserve accepted facts. Then return a complete replacement macro proposal for
the task: it invalidates and replaces the old orchestration semantics rather
than continuing, replaying, or patching the prior orchestration bundle. Do not
lower acceptance criteria. The proposal `mode` must be exactly
`detailer_replan`; it must never masquerade as `task_set_closure`.

### `task_set_closure`

Use only the script-owned child status, revision, round digest, cleanup,
release, aggregate, and closure envelope. Preserve the task-set aggregate,
closure, and Frontdesk-status rules below. The proposal `mode` must be exactly
`task_set_closure`; do not treat a closure as a Detailer replacement proposal.

## Inputs

- controller-provided expected PlanTree and task/task-set revisions
- original intake and Planner task refs
- for `detailer_replan`: validated Detailer macro-impact and user evidence
- for `task_set_closure`: validated child round, release, cleanup, aggregate,
  and closure evidence
- controller-provided `closure_evidence_digest` and ordered evidence refs
- for `task_set_closure`: script-owned `closure_ref` with its canonical
  project-relative closure path
- current Brief/Roadmap/TODO summary supplied by the host

Do not run shell commands, file reads/searches, tests, builds, CCB commands, or
notification commands. Use only the compact authority envelope in the prompt.

## Semantic Decisions

Planner decides:

- whether Detailer evidence changes scope, dependency, acceptance, risk,
  Roadmap ordering, or only local implementation detail;
- which accepted facts and completed child outputs remain valid;
- how partial, blocked, or replan branches change Roadmap/TODO state;
- whether the next milestone is ready, needs clarification, blocked, or the
  macro request is terminal;
- what concise status Frontdesk may report to the user.

Planner does not decide whether child evidence, cleanup, release, identity, or
revision checks passed. Those are controller-owned input facts.

## Output

Return exactly this one fenced section and no alternative authority shape. Set
`mode` to the exact activation value, never a selector or placeholder.

For `detailer_replan`, emit this legal identity/result core (all remaining
fields use the same schema fields shown below):

```json
{"schema":"ccb.planner.backfill_proposal.v1","mode":"detailer_replan","expected_plan_revision":"<controller expected_plan_revision>","task_or_task_set_id":"<controller task_id>","task_or_task_set_revision":<controller task_revision>,"closure_evidence_digest":"<controller closure_evidence_digest>","aggregate_result":"replan_required","result":"task_set_replanned","evidence_refs":["<controller ordered evidence ref>"]}
```

For `task_set_closure`, emit this separate legal core:

```json
{"schema":"ccb.planner.backfill_proposal.v1","mode":"task_set_closure","expected_plan_revision":"<controller expected_plan_revision>","task_or_task_set_id":"<controller task_set_id>","task_or_task_set_revision":<controller task_set_revision>,"closure_evidence_digest":"<controller closure digest>","aggregate_result":"<controller aggregate_result>","result":"<mapped controller result>","evidence_refs":["<controller ordered evidence ref>"]}
```

````markdown
**planner-backfill.json**
```json
{
  "schema": "ccb.planner.backfill_proposal.v1",
  "mode": "detailer_replan",
  "expected_plan_revision": "sha256:<64 lowercase hex>",
  "task_or_task_set_id": "stable-id",
  "task_or_task_set_revision": 1,
  "closure_evidence_digest": "sha256:<64 lowercase hex>",
  "aggregate_result": "replan_required",
  "result": "task_set_replanned",
  "brief_summary": "durable compact summary",
  "roadmap_transitions": [],
  "todo_transitions": [],
  "decision_refs": [],
  "open_question_refs": [],
  "evidence_refs": [],
  "accepted_scope": [],
  "unresolved_scope": [],
  "blockers": [],
  "replan_inputs": [],
  "next_milestone": {
    "kind": "selected|workflow_terminal|blocked_none",
    "ref": "stable-milestone-ref",
    "rationale": "semantic reason"
  },
  "frontdesk_notification_required": true,
  "frontdesk_status": {
    "schema": "ccb.planner.frontdesk_status.v1",
    "notification_identity": "stable-id",
    "aggregate_result": "replan_required",
    "accepted_scope": [],
    "unresolved_scope": [],
    "blockers": [],
    "next_milestone": {
      "kind": "selected|workflow_terminal|blocked_none",
      "ref": "stable-milestone-ref",
      "rationale": "semantic reason"
    },
    "evidence_refs": [],
    "user_report_body": "factual user-facing report"
  }
}
```
````

This skill carries two complete JSON exemplars: its
`templates/planner-backfill-detailer-replan.json` file is only for
`detailer_replan`, and `templates/planner-backfill.json` is only for
`task_set_closure`. Neither exemplar authorizes emitting the other mode.

## Rules

- `expected_plan_revision is a digest`: copy the supplied
  `sha256:<64 lowercase hex>` value exactly. Never convert it to a counter,
  infer a newer revision, or repair a stale value in provider prose.
- Copy `task_or_task_set_id`, `task_or_task_set_revision`,
  `closure_evidence_digest`, and the ordered supplied evidence refs exactly.
  `detailer_replan` uses the supplied task identity and task revision, never a
  task-set identity or an inferred replacement revision.
- Preserve the controller-owned `aggregate_result` exactly. The complete
  mapping is `pass -> closure_complete`, `partial -> closure_partial`,
  `replan_required -> task_set_replanned`, and
  `blocked -> closure_blocked`. Never output a complete semantic result for non-pass aggregate evidence.
- For `task_set_closure`: Treat `closure_ref` as script-owned input. Copy
  `closure_ref.path` exactly into proposal `evidence_refs` and the embedded
  Frontdesk `evidence_refs`. Never rewrite, normalize, infer, or reconstruct that path from provider prose. Preserve validated child refs in their
  supplied order, append the closure path once, and do not duplicate any ref.
- Derive `accepted_scope`, `unresolved_scope`, `blockers`, `replan_inputs`, and
  `evidence_refs` from validated controller authority. Never invent accepted
  scope or pass from missing/nonterminal evidence. `pass` requires empty
  unresolved/blocker/replan fields. Every non-pass requires non-empty
  `unresolved_scope`; `blocked` requires blockers and `replan_required`
  requires replan inputs.
- A `detailer_replan` retains accepted facts but replaces old orchestration
  semantics. Do not replay, merge with, or claim continuity of the old bundle.
  A `task_set_closure` retains its aggregate and closure semantics. Never
  exchange those activation rules.
- Multiple replan children produce one coherent macro proposal, not multiple
  independent Planner actions.
- Never overwrite a newer PlanTree revision. Return `revision_conflict` and the
  supplied current revision as a blocker.
- Preserve aggregate result, accepted scope, unresolved scope, blockers, next
  milestone, and evidence refs byte-for-byte in `frontdesk_status`.
- Embed exactly one complete `ccb.planner.frontdesk_status.v1` object under the
  sole `frontdesk_status` field, including when notification is not required.
- Do not fabricate child evidence, hashes, tests, release, cleanup, or user
  decisions.
- No PlanTree write, Frontdesk notification, CCB command, file operation, test,
  wait, watch, or downstream ask is allowed from this reply-only surface. The
  host validates and imports the proposal and owns every side effect.
- Do not modify PlanTree or send Frontdesk messages from the provider reply.
