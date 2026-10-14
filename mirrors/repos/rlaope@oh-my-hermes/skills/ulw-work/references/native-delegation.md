# Native Delegation

Load this before a `delegate_task` dispatch in an `ultrawork` run. Three host mechanisms decide what the parent may read from a delegated lane: Hermes can check the shape of a lane's answer, give each lane a git worktree of its own, and cap how many lanes a one-shot run may delegate. Each applies only while `delegate_task` is in your tool list or tool_search finds it. A lane's answer stays the lane's report whatever the host checked; the run is complete only on the verification fan-in this session runs (`references/dependency-topology.md`).

## 1. A fixed shape for the lane's answer

For a lane you write yourself, pass an `output_schema` holding only the fields the integration step reads, for example:

```json
{
  "type": "object",
  "required": ["status", "changed_files"],
  "properties": {
    "status": {"enum": ["done", "blocked"]},
    "changed_files": {"type": "array", "items": {"type": "string"}},
    "verify": {
      "type": "object",
      "required": ["command", "exit_code"],
      "properties": {"command": {"type": "string"}, "exit_code": {"type": "integer"}}
    },
    "blocked_reason": {"type": "string"}
  }
}
```

A `done` with no `verify` is a lane that ran no check of its own. An `omh_team` entry is the exception to all of this section: dispatch it unchanged (`references/team-lane.md`), because its acceptance is the check OMH runs.

The host tells the lane the shape before it starts, checks the final answer against it, and asks once more on a mismatch. Its `schema_valid` record reaches you only when the call returns its results in the same turn; a result that arrives later as a completion message carries none, so check that summary against the schema yourself and never read `completed` as validated. `omh-code-review/references/native-review-contract.md` describes both kinds of return, and a lane's return reads the same way.

A matched shape is a checked shape, not a checked claim. `changed_files` and `verify.exit_code` are what the lane says it did: the manifest comparison reads the diff, and the fan-in runs the command again on the integrated tree. A lane whose answer did not match is `not_observed`; its text holds leads, not a result.

## 2. Lanes in worktrees of their own

`delegation.worktree_isolation` is the user's Hermes setting and is off unless they turned it on. OMH never writes it: when lanes would collide in one checkout, propose the one-line change for the user to apply. With it on, in a git repository, with Hermes' terminal running locally, each lane gets `<repo>/.worktrees/subagent-<id>` on branch `hermes-subagent/subagent-<id>`, created from the commit your checkout is on. Anywhere else the host skips isolation without saying so, and the lanes write into the shared checkout.

What changes for the parent:

- A lane starts from the last commit, not from your working tree: uncommitted edits in your checkout are not in its worktree.
- A lane's edits are not in your checkout. They are commits on its branch, or uncommitted changes left in its worktree. Integration is a merge you perform: merge each lane's branch in dependency order, then run the verification fan-in on the merged tree. A check before that merge tests a tree without the lane's work.
- A worktree left dirty (`dirty: true`, or `git -C <path> status --porcelain` non-empty) is committed on its branch before the merge; find lanes with `git worktree list`, and a branch with no commits is not an empty lane until its worktree is checked.
- Only after a lane has returned, and in the completion-message case only once every lane whose worktree `git worktree list` shows has returned (the message does not say which worktree is whose), commit a dirty worktree on its branch, merge it, and remove it. A worktree whose lane may still be running is not committed, merged, or removed.
- A same-turn result carries a `worktree` entry for each lane with `path`, `branch`, `commits`, `dirty`, and `pruned`. The host deletes a worktree only when its lane made no commits and left it clean (`pruned: true`). `inspection_failed: true` means the host could not count the commits or read the status; it kept the worktree, and nothing about the lane's work is known until you look.
- A completion message carries no `worktree` entry. Find the lanes yourself before integrating, and remove each worktree and branch once it is merged.
- The first isolated lane makes the host add `.worktrees/` to the repository's `.gitignore` when it is missing: an uncommitted change in your checkout that is the host's, not a lane's.
- Isolation moves a collision from the working tree to the merge; it does not remove it. The file-ownership manifest still decides which lanes may run together.

## 3. The one-shot delegation budget

A one-shot run (`hermes chat -q`, which is also how a kanban worker runs) may cap how many children it delegates in total. When `delegate_task` refuses with an error that names `delegation.oneshot_max_children`, treat this run's budget as spent, even when the refusal counts fewer used than the cap:

- Do not retry the call, and do not split it smaller to fit under the cap.
- Run each remaining lane yourself in this session, one at a time in dependency order, each with its own `VERIFY`.
- The closing brief names each such lane as run inline: it was not delegated and has no helper of its own.

The rule follows the refusal, not a version: a host without the cap never sends it.
