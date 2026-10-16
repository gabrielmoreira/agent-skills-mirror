# Board Fan-In Recipe

Load this reference when `ultraqa` probes cannot stay inside this chat session: a probe is destructive enough to need a Hermes-managed worktree, or the QA pass must outlive the session. Everything here is prepared through `omh_agent_board`. The create recipe, the main-session-only rule, the readback bounds, the provenance words, and the role table are in `ulw-work/references/kanban-lane.md` and are not repeated here. OMH calls no native tool itself, writes nothing to the board, and a prepared probe is not a probe that ran.

## When QA Goes to the Board

- A probe mutates state the chat session's workspace cannot afford to lose: it deletes or corrupts files, rewrites config, exhausts a resource, or kills processes. It runs in a worktree of its own so the main workspace is never the test subject.
- The QA pass must outlive this session, because the probes are long or the session ends before they report.
- A probe must run under another Hermes profile, because it needs authority or a credential set the main session does not carry.

An adversarial scenario that only reads, asserts, and reports stays an in-session lane routed by `omh_delegate_route`.

## Probe Rows

One prepared create per adversarial scenario, N in total, each with its own `request_id`:

| Argument | Value |
| --- | --- |
| `title` | `Probe: <scenario>` |
| `skills` | `["ulw-qa"]` |
| `workspace_kind` | `worktree`, so destructive QA runs in Hermes-owned isolation and never in the main workspace |
| `max_runtime_seconds` | the probe's time budget, so a stuck worker ends instead of holding the row |
| `parents` | none; probes are independent of each other and start when the dispatcher claims them |
| `body` | the scenario as `TASK`, `DELIVERABLE`, `SCOPE`, `VERIFY`, `STOP WHEN` |

A probe's `DELIVERABLE` is its pass/fail evidence: the command run, the expected signal, the observed signal, and the verdict, carried in the `result` of its completion. Its `STOP WHEN` is that evidence pasted, or the runtime budget. A probe never fixes what it finds; a fix inside a probe row turns evidence into a claim about a workspace nobody else can see.

## The Fan-In

Exactly one fixer row, prepared after every probe receipt is observed:

| Argument | Value |
| --- | --- |
| `title` | `Fixer: <changed behaviour>` |
| `skills` | `["ulw-work"]` |
| `parents` | every probe row's observed task id |
| `workspace_kind` | `worktree` |
| `body` | the findings to fix, each quoted from the probe `result` it came from; its `STOP WHEN` ends the run with `kanban_request_review` |

Because `parents` lists every probe, the host promotes the fixer only after every probe is `done` or `archived`. A probe whose run reads back `timed_out` is neither: the budget ended the worker, not the row, so that probe is completed with a blocker summary or archived before the fixer can promote. One fixer, not one per probe: findings from separate probes often share a cause, and N fixers would race in N worktrees over the same files. The fixer's `body` is written from read-back probe results, so it cannot be prepared before the last probe reports.

## Re-Verification Through the Review Lane

The fixer asks for its own review: its run ends with `kanban_request_review` instead of `kanban_complete`, with a `summary` naming the probes the fix claims to address. Hermes moves a row to `review` only from `running` or `ready`, so the request has to come from the fixer's own run while its row is `running`. The main session never prepares `request_review` on a fixer row: once the row reads back `done`, Hermes refuses the move. A fixer that completed instead skipped the review lane; re-verify it in this session where its worktree is reachable, or report it as not re-verified.

Re-verification is the probes run again against the fixer's worktree. Unless the operator set `kanban.review_dispatch` off, the host's dispatcher claims the `review` row for a review run, and that run either requests changes, which returns the row to the fixer and repeats the cycle, or completes it. Hermes takes `request_changes` only from inside that review run, so the main session never prepares it. Where no review run claims the row, this session runs the probes again where the worktree is reachable. A failed re-check is then a prepared `comment` on the fixer row carrying the failing probe's evidence, and the closing brief reports the fix as failing its re-check; sending the row back to the fixer is the operator's `hermes kanban reopen-review`, not a step of the QA pass.

A row in `review` is a request (the observed fact is `review_requested`), and a review claim is not merge evidence.

## Findings Come Back Through Readback Only

- One `kanban_list` per turn boundary scoped by `assignee` or `status`, one `kanban_show` per row that changed, no polling.
- Each probe's `result` is the worker's report, bounded and labelled by the readback pass, and quoted as such in the closing brief: `probe <title> reported: <result>`. The main session never restates a probe result as its own observation.
- Pass/fail evidence stays separate from proposed fixes, as the in-session QA discipline already requires; the fixer row is a proposed fix until it is re-verified.
- One item per open row in the plan's one checklist tool (`todo_list` or `omh_todo`, never both), updated from the readback pass and from nothing else.

## Cleanup

The preserved worktree is the cleanup receipt. Each probe's worktree holds the state its scenario left behind, which is what a reader needs to reproduce the finding, and the fixer's worktree holds the change. The closing brief names every preserved worktree as the rows' readback reports it; a worktree the readback cannot name is a probe whose evidence cannot be located. Removing a worktree is the operator's decision after the brief, not a step of the QA pass.

## Worked Example

Three destructive scenarios against a changed installer prepare four rows, in this order, each with its own `request_id`:

```text
prepare  coordination=durable operation=create
  title="Probe: stale config survives upgrade"   assignee=<profile> skills=["ulw-qa"]
  workspace_kind=worktree max_runtime_seconds=1800 body=<TASK/DELIVERABLE/SCOPE/VERIFY/STOP WHEN>
prepare  coordination=durable operation=create
  title="Probe: PATH missing at first run"       assignee=<profile> skills=["ulw-qa"]
  workspace_kind=worktree max_runtime_seconds=1800 body=<...>
prepare  coordination=durable operation=create
  title="Probe: interrupted install, rerun"      assignee=<profile> skills=["ulw-qa"]
  workspace_kind=worktree max_runtime_seconds=1800 body=<...>
prepare  coordination=durable operation=create
  title="Fixer: installer upgrade path"          assignee=<profile> skills=["ulw-work"]
  parents=[<probe 1 id>, <probe 2 id>, <probe 3 id>] workspace_kind=worktree
  body=<findings quoted from the three probe results; STOP WHEN ends with kanban_request_review>
```

The fixer's `parents` are the observed task ids from the three probe receipts, so the probes are prepared, invoked, and read back before the fixer is prepared. Four `omh_todo` items exist after the fourth receipt, one per row. The fixer's own run requests the review, so once the fix is in its row reads back `review`, not `done`; the main session prepares no transition on it.
