# Kanban Lane Recipe

Load this reference when an accepted `ultrawork` plan has a lane that cannot stay inside this chat session. Everything here is prepared through `omh_agent_board`; OMH calls no native tool itself, writes nothing to the board, and a prepared row is still not dispatch, execution, verification, review, CI, or merge evidence.

## When a Lane Goes to the Board

A lane is a board task instead of a `delegate_task` lane only when at least one of these holds:

- it must outlive this session (a worker that keeps going after the chat ends or the gateway restarts);
- it must run under another Hermes profile (a different permission envelope, credential set, or model chain);
- it needs a Hermes-managed worktree of its own (`workspace_kind=worktree`).

Every other lane stays a `delegate_task` lane routed by `omh_delegate_route`. Ordering alone is not a reason: the dependency-topology discipline already orders in-session lanes. A board lane starts only when the gateway dispatcher claims it and cannot be steered once claimed, so the default is the in-session lane.

## The Create Recipe

One `omh_agent_board` `prepare` per lane, with `coordination` set to `durable` and `operation` set to `create`. State the lane's role once and fill the rest from the lane definition, never from memory of the plan:

| Argument | Source |
| --- | --- |
| `title` | the lane's one-line `TASK` |
| `assignee` | an existing Hermes profile name (the permission envelope the worker runs under) |
| `lane_role` | the lane's role: `builder`, `verifier`, `reviewer`, `docs`, or `qa` |
| `body` | the standalone node prompt: `TASK`, `DELIVERABLE`, `SCOPE`, `VERIFY`, `STOP WHEN`, in that order |
| `parents` | every dependency edge the lane consumes, declared on this create |
| `max_runtime_seconds` | the lane's time budget, so a stuck worker ends instead of holding the row |
| `model`, `provider` | the lane's route category from `omh_delegate_route`, when the category pins one |

The role is a contract, not an instruction. OMH fills the lane fields the role implies and refuses a create that contradicts them:

| `lane_role` | fills `skills` with | fills `workspace_kind` with | checks |
| --- | --- | --- | --- |
| `builder` | `ulw-work` | `worktree` | — |
| `verifier` | `omh-verification-gate` | `worktree` | `parents` present and non-empty |
| `reviewer` | `omh-code-review` | nothing (a read-only lane) | `parents` present and non-empty |
| `docs` | `omh-docs` | `worktree` | — |
| `qa` | `ulw-qa` | `worktree` | — |

Pass `skills` or `workspace_kind` yourself when the lane needs something else, and the explicit value wins, with one exception: a `skills` list must still contain the role's own skill. Extra skills ride along under the same ceiling of eight; dropping the role's own skill is refused as `lane_role_skills_mismatch`. An unknown role is refused as `invalid_lane_role`, and a fan-in lane that declares no inputs as `verifier_requires_parents` or `reviewer_requires_parents`. The role itself never reaches the board: OMH removes it before the native action, because `kanban_create` has no such argument.

Declare `parents` on the create call, never as a later `link`. The gateway dispatcher can claim a parentless `ready` row within one tick, so a row created first and linked second may already be running under a worker that never saw its inputs. Do not pass `initial_status`; the host places the row and promotes it when every parent is `done` or `archived`. `prepare` sets `idempotency_key` to the `request_id`, so repeating a create with the same `request_id` returns the already observed task instead of a duplicate.

Then invoke the returned `native_action` through the ordinary Hermes tool loop. The request state is `prepared` until the bridge correlates the native call; `unavailable` names the missing capability and means zero native calls were made.

## Main Session Only

`kanban_*` tools are visible only to a chat session whose profile enables the `kanban` toolset. `delegate_task` children never see them, so only the main session prepares board actions. A board worker is itself a main-style session and may run in-session `delegate_task` lanes, but it does not create further board rows: lanes nest to depth one, and a plan that needs deeper nesting is a plan that needs re-splitting.

## Readback Discipline

- At most one `kanban_list` per turn boundary, scoped by `assignee` or `status`, never a polling loop.
- One `kanban_show` per lane whose row changed state in that list.
- One `omh_todo` item per board lane, updated from the readback pass and from nothing else; the item's text is the lane title plus the last observed status.
- Results arrive bounded and labelled by the readback pass. A `result` field is a worker's report, quoted as such; the parent never restates it as its own finding.

The parent ends its turn after preparing lanes and re-enters on the next user turn or scheduled check. There is no wait, attach, retry, or amend verb for a board row: a row whose prompt was wrong is completed with a blocker summary and a new row is created with the corrected prompt.

## Worked Example

An accepted plan with two builder components, one verification fan-in, and a docs lane that must survive the session prepares four rows in this order, each with its own `request_id`:

```text
prepare  coordination=durable operation=create
  title="Builder: storage adapter"   assignee=<profile> lane_role=builder
  max_runtime_seconds=3600 body=<TASK/DELIVERABLE/SCOPE/VERIFY/STOP WHEN>
prepare  coordination=durable operation=create
  title="Builder: CLI surface"       assignee=<profile> lane_role=builder
  max_runtime_seconds=3600 body=<...>
prepare  coordination=durable operation=create
  title="Verifier: full suite"       assignee=<profile> lane_role=verifier
  parents=[<storage task id>, <cli task id>] body=<...>
prepare  coordination=durable operation=create
  title="Docs: adapter setup page"   assignee=<profile> lane_role=docs
  parents=[<storage task id>] body=<...>
```

The verifier's `parents` are the observed task ids from the two builder receipts, so the builders are prepared, invoked, and read back before the verifier is prepared. Four `omh_todo` items exist after the fourth receipt, one per row, each carrying its observed task id.

## Closing the Run

The run closes in the main session, never in a worker. Read back once, confirm the verifier row is `done` with a `result` naming the command and its pass/fail output, re-run the integration verification in this session when the workspace is reachable, and record the run through `omh_run_summary`. A verifier row that is `done` without pasted output is `worker reported done` and the closing brief says so.

## Provenance Words

- `prepared`: the create was prepared; nothing on the board exists yet.
- `observed`: the bridge correlated a native receipt; the task id in that receipt is the only id the parent may cite.
- `worker reported done`: the row reached `done`. This is the worker's claim about its own lane. The closing brief still needs the integration verification fan-in and the `omh_run_summary` receipt before it may say the run is complete.
- `dispatcher not observed`: a `ready` row nobody claimed. This is not a failure and not a stall; it means the gateway tick has not been observed picking it up, and the operator preconditions below are the first place to look.

A board `done` is never review approval, CI, or merge evidence.

## What Is Not Provided

- No native `kanban_dispatch`: dispatch stays `unavailable`, and a running worker is an observed claim by the host dispatcher, never an OMH act.
- No wait, attach, retry, or amend verb; see the readback discipline.
- No token usage: the board records elapsed time and outcomes, not cost, so a board lane never appears in a cost tally.
- No OMH steering verb: a prepared `comment` on the task is the only mid-run input. Whether the worker reads it is the host's comment bridge, not observed by OMH; brief the lane as if `body` were all it will see.

## Operator Preconditions

Check these before preparing the first board lane; a missing one is reported as the blocker, not worked around.

1. The `kanban` toolset is enabled for the platform in use, and the chat is a fresh session started after enabling it.
2. `kanban.db` is initialised under the Hermes root (or the board named by `board`).
3. The gateway is running with `kanban.dispatch_in_gateway` enabled; without it rows sit in `ready` forever.
4. The `assignee` profile exists.
5. Every skill the lane carries is installed in that profile: the role's own skill, plus anything extra the create names in `skills`.

## Role Table

Profile is the permission envelope; role is the per-task overlay stated as `lane_role` and filled into `skills` by the create recipe above. One profile is the default; use a second profile only when a lane needs different authority (a write credential, a production connector, a stricter model chain), never to label a specialty.

| Lane | `lane_role` | `parents` | Notes |
| --- | --- | --- | --- |
| Main session | none (this chat) | none | planner and operator; prepares every row, owns the todo, closes the run |
| Builder | `builder` | its upstream builders, if any | one per component |
| Verifier | `verifier` | every builder | exactly one; runs the repository's real test or build command |
| Reviewer | `reviewer` | the builders it reviews | findings first; a review claim is not merge evidence |
| Docs | `docs` | the builders whose behaviour it documents | only when behaviour, setup, commands, or public claims changed |
| QA probe | `qa` | the builders it probes | only for checks a unit suite cannot make from inside the code |

Specialist titles such as backend, SRE, or data are lane titles only. They name the component a builder owns; they are never new catalog roles, and they never change which role a lane carries.
