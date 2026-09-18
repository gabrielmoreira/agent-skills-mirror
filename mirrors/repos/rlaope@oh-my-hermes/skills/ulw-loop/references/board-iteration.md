# Board Iteration Recipe

Load this reference when a `loop` iteration cannot stay inside this chat session. Everything here is prepared through `omh_agent_board`. The create recipe, the main-session-only rule, the readback bounds, the provenance words, and the role table are in `ulw-work/references/kanban-lane.md` and are not repeated here. OMH calls no native tool itself, writes nothing to the board, and a prepared row is not an iteration that ran.

## When an Iteration Goes to the Board

An iteration is a board row instead of an in-session lane only when at least one of these holds:

- the loop must outlive this session (iterations that keep going after the chat ends or the gateway restarts);
- the iteration must run under another Hermes profile (a different permission envelope, credential set, or model chain);
- the iteration needs a Hermes-managed worktree of its own (`workspace_kind=worktree`).

Every other iteration stays in-session under the existing loop discipline: assess, act, verify, decide. A loop whose iterations are short and whose session is stable gains nothing from the board and loses the ability to steer mid-iteration, because a board lane cannot be steered once the dispatcher claims it.

## The Iteration Chain

Each iteration is two rows, prepared with the kanban-lane create recipe:

| Row | `skills` | `parents` |
| --- | --- | --- |
| builder for iteration N | `ulw-work` | the verifier row of iteration N-1 (none for the first iteration) |
| verifier for iteration N | `omh-verification-gate` | the builder row of iteration N |

The `parents` edge is what orders the loop. The host promotes a row only when every parent is `done` or `archived`, so the builder of iteration N cannot be claimed before the verifier of N-1 reports, and the verifier of N cannot be claimed before its builder reports. Nothing runs out of order and nothing in OMH has to enforce the order; the board does. Declare `parents` on the create, never as a later `link`.

Prepare one iteration at a time. The next builder's `body` is written from the previous verifier's `result`, read back through `kanban_show`, so it cannot be prepared before that result exists. Preparing several iterations ahead would mean writing a `TASK` from a prediction instead of an observed result, which the loop discipline forbids in-session as well.

Each body carries the iteration's own `TASK`, `DELIVERABLE`, `SCOPE`, `VERIFY`, and `STOP WHEN`. A builder's `STOP WHEN` is its verifier; a verifier's `STOP WHEN` is the pasted pass/fail output of the named command.

## The Stop Rule

The loop's `loop_constraint_assessment/v1` block still decides what the next iteration is; the board only carries it. When that assessment says the loop must stop for the user (a permission gate, a missing input, an evidence gap only the user can resolve, an unresolved tradeoff), the main session prepares `block` on the current row with `kind=needs_input` and the stop reason as `reason`. The row stays `blocked` until the operator prepares `unblock`. The loop never retries a blocked row silently and never prepares the next builder around it.

`needs_input` is the only block kind the loop prepares on its own judgement. `dependency`, `capability`, and `transient` describe facts about the host, not decisions of the loop, and are read back rather than declared.

## Resume

A new session does not resume the loop from memory, from the previous session's narration, or from the loop artifacts alone. It reads back:

1. one `kanban_list` scoped by `assignee` or `status`: the rows of this loop and their states;
2. one `kanban_show` per row whose state changed since the last known readback.

The chain continues from the last verifier row that is `done`: its `result` is the input to the next builder's `body`. A verifier that is `running` is waited for by ending the turn, not by polling. A builder that is `done` with no verifier row after it means the previous session ended between the two creates; the verifier is prepared now, with `parents` set to that builder.

## No Goal-Mode Root Row

The loop does not create a root row for the goal and hang the iterations under it. The loop's real gate is the in-session verification the existing loop discipline already requires, closed through linked `goal_ledger/v1` completion evidence. A root row that reached `done` would be a second completion claim with no evidence behind it. The chain of builder and verifier rows is the whole board footprint of one loop.

## Todo and Closing

One `omh_todo` item per open board row, its text the row title plus the last observed status, updated from the readback pass and from nothing else. A row that reaches `done` closes its item; a row that is `blocked` carries the block reason as the item's `blocked_reason`.

The loop closes in the main session. A verifier `done` is `worker reported done` until this session re-runs the verification where the workspace is reachable, and the goal closes only through the loop's own completion gate. A board row is never goal completion evidence.

## Worked Example

A loop whose first iteration ran in-session and whose second iteration must survive the session prepares, in this order, each with its own `request_id`:

```text
prepare  coordination=durable operation=create
  title="Builder: iteration 2 - retry budget"   assignee=<profile> skills=["ulw-work"]
  workspace_kind=worktree max_runtime_seconds=3600
  body=<TASK/DELIVERABLE/SCOPE/VERIFY/STOP WHEN written from the in-session iteration 1 verification result>
prepare  coordination=durable operation=create
  title="Verifier: iteration 2 - full suite"    assignee=<profile> skills=["omh-verification-gate"]
  parents=[<iteration 2 builder id>] workspace_kind=worktree body=<...>
```

The first board builder has no `parents`, because iteration 1 left no verifier row to cite; from here on the chain is on the board. The verifier's `parents` is the observed task id from the builder receipt, so the builder is prepared, invoked, and read back before the verifier is prepared. Two `omh_todo` items exist after the second receipt, one per row. The third iteration is not prepared until the iteration 2 verifier reads back `done` with a `result`.
