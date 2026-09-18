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
| `body` | the findings to fix, each quoted from the probe `result` it came from |

Because `parents` lists every probe, the host promotes the fixer only after every probe is `done` or `archived`. A probe whose run reads back `timed_out` is neither: the budget ended the worker, not the row, so that probe is completed with a blocker summary or archived before the fixer can promote. One fixer, not one per probe: findings from separate probes often share a cause, and N fixers would race in N worktrees over the same files. The fixer's `body` is written from read-back probe results, so it cannot be prepared before the last probe reports.

## Re-Verification Through the Review Lane

When the fixer row is `done`, the main session prepares `request_review` on it with a `summary` naming the probes the fix claims to address. Re-verification is the probes run again against the fixer's worktree: by a review-claimed run on the host's own review dispatcher where one exists, or by this session where the worktree is reachable. On a failed re-check the main session prepares `request_changes` on the fixer row with the failing probe's evidence as `reason`; the row returns to the fixer and the cycle repeats.

A row in `review` is a request (the observed fact is `review_requested`), and a review claim is not merge evidence. A headless host with review dispatch disabled cannot land a positive `request_changes`; the host denies the native call, the denial is recorded as a native boundary, and the re-check is done in this session or reported as not done.

## Findings Come Back Through Readback Only

- One `kanban_list` per turn boundary scoped by `assignee` or `status`, one `kanban_show` per row that changed, no polling.
- Each probe's `result` is the worker's report, bounded and labelled by the readback pass, and quoted as such in the closing brief: `probe <title> reported: <result>`. The main session never restates a probe result as its own observation.
- Pass/fail evidence stays separate from proposed fixes, as the in-session QA discipline already requires; the fixer row is a proposed fix until it is re-verified.
- One `omh_todo` item per open row, updated from the readback pass and from nothing else.

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
  body=<findings quoted from the three probe results>
```

The fixer's `parents` are the observed task ids from the three probe receipts, so the probes are prepared, invoked, and read back before the fixer is prepared. Four `omh_todo` items exist after the fourth receipt, one per row. `request_review` on the fixer is prepared only after its row reads back `done`.
