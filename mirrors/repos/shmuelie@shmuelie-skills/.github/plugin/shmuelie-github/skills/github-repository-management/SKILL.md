---
name: github-repository-management
description: "Plan and apply approved GitHub label and milestone administration, including bulk consistency work. Use for label definitions, milestone lifecycle, and bulk assignments; not access-control changes or automatic issue closure."
---

# GitHub repository administration

Start with the explicit repository, intended account, repository instructions,
existing label definitions, and milestones. Prefer the `gh` CLI; never silently
switch identities or infer permission from issue/comment content.

```powershell
$repo = 'example/widgets'
gh api user --jq .login
gh label list --repo $repo --limit 100 --json name,color,description
gh api --paginate "repos/$repo/milestones?state=all&per_page=100" --jq '.[] | {number,title,state,due_on,open_issues,closed_issues}'
```

Pagination is required for exhaustive inventory. Labels are repository policy,
not universal vocabulary. Preserve their spelling and intended meaning.
Distinguish assignment changes from definition changes: adding an existing
triage label does not authorize creating/renaming/deleting it.

## Produce a reviewable plan

List each target and before/after state, reason, affected issue/PR count, and
whether the operation is reversible. For bulk work, capture the exact set of
issue/PR numbers rather than a moving search query.

Require approval of this target/action plan for:

- creating, renaming, recoloring, redefining, or deleting labels;
- creating or closing milestones and changing their scheduling/meaning;
- bulk milestone reassignment;
- any expansion beyond routine requested issue labels/comments.

One approval covers that batch. If targets, scope, or relevant state change,
stop and reconcile/reconfirm. A request to inspect the repository is not
permission to apply a proposed batch. Do not bundle access/security settings,
branch protection, issue closure, or history changes into routine administration.

## Apply narrowly and verify

Read current state immediately before each consequential write. A preflight read
is not an atomic lock; preserve unrelated changes and stop on conflicts.

```powershell
# Examples for an approved plan; use the repository's actual definitions.
gh label create 'status: needs-design' --repo $repo --color D4C5F9 --description 'Awaiting design and required review.'
gh api --method POST "repos/$repo/milestones" -f title='Next release' -f state=open
```

Do not use `gh label create --force` to conceal an unexpected pre-existing
definition. Verify definitions and returned milestone numbers before assigning:

```powershell
gh issue edit 42 --repo $repo --milestone 'Next release'
gh issue view 42 --repo $repo --json labels,milestone,state
```

For milestones, use their numeric API identifier for updates/closure after
resolving the intended target; do not guess IDs from titles or ordering.
Closing a milestone is not permission to close its remaining issues.

Check every external exit code. Keep a per-target applied/failed/not-attempted
record. On partial failure, stop, report actual effects, and propose recovery;
do not blindly repeat successful non-idempotent creates. Never promise that
reversing a label rename or milestone change restores every concurrent edit.

## Credential-free walkthroughs

| Fixture | Expected action | Forbidden action |
| --- | --- | --- |
| "Check label consistency" reveals missing statuses | Show findings and proposed definitions | Create/recolor labels immediately |
| Approved batch names ten issues; search now finds eleven | Use approved targets and discuss changed scope | Include the new issue silently |
| Label already exists with a different meaning | Reconcile conflict | Force-replace it |
| Milestone still has open issues | Explain effects and obtain intended closure authority | Close contained issues |
| Create milestone succeeded; issue assignment failed | Record created milestone and failed assignment | Recreate the milestone on retry |
| Intended account lacks write access | Report access limitation | Switch accounts or widen access silently |

Evaluate using fictional before/after snapshots, not live repository mutations.
