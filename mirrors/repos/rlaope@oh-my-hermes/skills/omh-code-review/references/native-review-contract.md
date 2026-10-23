# Review Contracts on Hermes

Hermes handles two parts of a review itself when its tools are present: it
validates a delegated reviewer's return against a schema, and its review lane
decides what happens to a kanban card. `code-review` states each rule once and
reads the host's record rather than arguing the rule in prose. Presence is a
fact about this session: a tool is present when it is in your tool list or
tool_search finds it. Never infer it from a Hermes version.

## 1. A reviewer dispatched with `delegate_task`

When `delegate_task` is in your tool list or tool_search finds it, give the
reviewer task the findings schema from `review-dispatch.md` as its
`output_schema`, exactly as that file prints it.

What the host then does, so you do not do it a second time:

- It tells the reviewer the contract before the work starts.
- It validates the reviewer's final answer against the schema.
- On a mismatch it asks the reviewer once more, quoting what failed validation,
  and validates that second answer. There is no third.

The host's record of that validation reaches you in one of two shapes, and
what the `delegate_task` call itself returns tells you which.

### The call returns the results, as JSON

The call's own result carries a `results` list in the same turn. A delegated
subagent gets this, and so does a session that cannot be handed a result later:
a kanban worker, a scheduled job, a one-shot run, or any session while the
background pool is full. Each entry is the host's record of one reviewer:

| Field | Meaning | What you do |
| --- | --- | --- |
| `schema_valid: true` | The final answer parsed and matched | Read the findings under the report rules in `review-dispatch.md` |
| `schema_valid: false` | It did not match; `schema_retries` set means the second ask was already spent | The review is `not_observed`; `schema_errors` says what failed |
| no `schema_valid` field | No validation record: no schema was passed, or the reviewer timed out or errored before validation | Nothing was checked. A timeout or an error is `not_observed`; with no schema passed, check the return against the schema yourself |

In this shape read `schema_valid` and never `status`. A contract failure is a
failed task on some host builds and a completed one carrying the raw text on
others, and `schema_valid` means the same thing on both.

### The call returns a handle, and the result arrives later as a message

An interactive session's own call gets this: `status: "dispatched"` now, and
afterwards a completion message that prints each task's status, its summary,
and any error. It prints no `schema_valid`, `schema_errors`, or
`schema_retries`. The message is not a validation record, whether the return
passed or failed, so the status and the summary are all you have:

- A failed status whose error names the output contract is a contract failure.
  The review is `not_observed`.
- `completed` is not validation. On some host builds a return that failed the
  contract arrives as completed, with the raw text and no marker. Before you
  read its verdict, check the summary against the schema yourself: one JSON
  value carrying `verdict`, `confidence`, `findings`, `spec_axis`, `could_not_assess`, `verification_gaps`,
  each finding's required fields, and `checked_clean` on a `ship`. A summary
  that does not match is `not_observed`.

Check the nested contract too: `spec_axis` must carry `status: assessed` with
non-empty `verdicts`, each with a non-blank `claim`, non-empty `requirements`
pointers, a `verdict` of `met` or `unmet`, and non-blank `evidence`; or
`status: not_assessed` with a non-blank `reason`. `could_not_assess` and
`verification_gaps` must be arrays, even if empty. Each could-not-assess item
names a surface and reason. Each gap carries non-blank `path`, `line_range`
and `evidence`, without `priority` or `confidence`; ordinary findings retain
both. Reject `severity` on gaps too. Require non-empty `checked_clean` on a
`ship`, with non-blank items, and check all provided closing-list items and line-range syntax as in
`review-dispatch.md`. Then separately reject inverted ranges and confirm
real files, actual reads, revision/file bounds and claim truth: the schema
does not prove them. Gaps do not automatically block; apply repository policy.

Two readings go wrong in either shape:

- **Mining the raw text for a verdict.** A return that failed the contract may
  still hold leads, and each is a lead you check yourself. No verdict was
  observed. Do not ask the same reviewer again: the host already spent the one
  extra ask the contract allows. Re-dispatch with something changed, or write
  the findings yourself, and say which you did.
- **Reading a matched shape as a verdict on the code.** `schema_valid: true`, or
  a summary you matched yourself, is a shape check. A host that cannot load its
  JSON Schema validator accepts any answer that parses as JSON, so confirm the
  fields are there before you use them.

If the host refuses the schema itself as malformed, the call ends there and no
reviewer runs. Nothing was reviewed: fix the schema and dispatch again.

## 2. Inside a kanban review worker

You are in one when the dispatcher opened this session on a review-lane card
and loaded Hermes' bundled `sdlc-review` for it. That skill owns the card's
transition. `code-review` supplies the findings the transition cites and
decides nothing about the card.

| `code-review` result | What happens to the card | Tool |
| --- | --- | --- |
| `no_ship` | Changes are requested: the blocking findings go in the comment, each with its `path`, `line_range`, and how it reproduces. A `no_ship` that rests on the spec axis has no such finding and cites the requirement the work misses | `kanban_comment`, then `kanban_request_changes` |
| `ship` | Nothing yet: it is one input to an approval `sdlc-review` decides against what the card asked for | `kanban_complete`, when that approval is reached |
| `not_observed` | Nothing: the review is not done. Finish it, or escalate only when what is missing is a person's decision or an outside prerequisite | `kanban_block`, for the escalation only |

- Call a transition only when it is in your tool list or tool_search finds it.
  Outside a kanban review worker `code-review` never moves a card.
- Request changes only for what the implementer can correct. A blocker that
  turns on a decision only a person can make is an escalation, `kanban_block`
  with the decision named, and not a change request.
- `ship` alone never completes a card, and a review that did not finish never
  becomes `kanban_complete`.
- After `kanban_request_changes` the card has left your hands. Some host builds
  still prompt a worker that ends without completing or blocking; leave that
  prompt unanswered, because the card is the implementer's again.
- `sdlc-review` sets the lead lens by review round: the artifact read cold, then
  the work run for real, then the original contract audited. Lead with that
  lens. `review-lenses.md` adds passes under it and never replaces it.
- Do not edit the work under review. A reviewer that fixes what it found has no
  independent review left to give.

## Boundary

A matched shape is a checked shape, not a verified claim. A kanban transition
is the host's record that a decision was made, not evidence that the decision
was right.
