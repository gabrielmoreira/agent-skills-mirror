---
name: pr-babysit
description: Use when the user asks to monitor, watch, babysit, or keep an eye on a pull request through CI, review, and merge, or to get a PR green or mergeable.
compatibility: Needs the gh CLI (authenticated), git, python3, and a checkout of the PR's repository to push fixes from.
---

# PR babysit

Stay with the PR until it is merged or closed, or the user says stop. Green CI and **ready** (open, checks green, approved or no review required, no review request or requested changes outstanding, mergeable and up to date, no thread awaiting a reply) are milestones, not the end: a late review or another PR landing on the base can break a ready PR without anyone touching it. If the user only asked to be told ("let me know when CI finishes"), report and change nothing.

## Watching

`scripts/pr_watch.py` (in this skill's directory) reads everything in one command:

- `python3 <skill-dir>/scripts/pr_watch.py snapshot [PR]`: state, failing checks, threads awaiting reply, and a `READY:` line with the blockers. Start with it; anything already failing or unanswered is your first work.
- `python3 <skill-dir>/scripts/pr_watch.py wait [PR]`: polls every 15 s and exits on the next new event (check failed or passed, review or comment, conflict, branch behind base, merged or closed) with a fresh snapshot, or after 25 min with `NO CHANGE`. It skips your own comments.

Wait with a host PR-watch tool if you have one (e.g. `watch_pull_request`). Otherwise run `wait` as a background command and end your turn; handle its notification, then start it again. Without background commands, run it in the foreground. On `NO CHANGE`, re-arm silently: a ready PR can sit for hours before someone merges it.

## Acting

Fix failures and review comments as you normally would, minding these:

- **The user's checkout.** If it has uncommitted changes or another branch checked out, leave it untouched (no switch, stash, or commit). Work in `git worktree add --detach ../<repo>-pr-<n> origin/<head branch>` (after `git fetch`) and push with `git push origin HEAD:<head branch>`.
- **Base moved.** On `MERGE CONFLICT` or `BEHIND`, merge the base into the PR branch (never rebase: the shared branch keeps its history): `git fetch origin && git merge origin/<base>`, resolve keeping what both sides meant, run the tests, commit, push. With no conflict, `gh pr update-branch <n>` does the same on GitHub. If the sides change the same behavior incompatibly, ask the user. If the push dismissed approvals, re-request those reviewers.
- **CI.** A failure that also happens on the base branch isn't this PR's to fix: report it. Infra failures (runner lost, network timeouts) get one `gh run rerun <id> --failed`. Stop and ask after two failed attempts at the same check.
- **The user's calls.** Design changes, scope growth, and disagreeing with a human reviewer go to the user, and the reply stays theirs to post.
- **Bots.** Check a bot's claim against the code before acting; if it's wrong, reply briefly with why.
- **Commits.** Stage only the files you changed (`git add <paths>`): tests and builds leave artifacts like `__pycache__/` that a broad add pushes into the PR for good. Never force-push a shared branch.
- **Replies.** Reply on each thread you addressed with what changed and the short SHA:
  ```bash
  gh api graphql -f query='mutation($id: ID!, $body: String!) {
    addPullRequestReviewThreadReply(input: {pullRequestReviewThreadId: $id, body: $body}) { comment { url } }
  }' -f id=<thread id from the snapshot> -f body='<reply>'
  ```
  Leave threads unresolved: resolving is how the reviewer says they're satisfied.
- **Re-review.** Once every thread from a human reviewer has a reply, `gh pr edit <n> --add-reviewer <login>`; hold off while one of their questions waits on the user.
- **Merging.** Only if the user asked. Leave a draft a draft.

After each push, tell the user in a line what changed, then go back to waiting.

## Finishing

When the PR becomes ready, tell the user in a line, with the link, and keep waiting. Say it again only if it became ready again after something changed.

If you're blocked on the user, ask, say you'll resume once they answer, and leave a background `wait` running so other events still reach you.

Once the PR is merged or closed, or the user says stop, report the outcome with the PR link, stop any background `wait` (or unwatch with the host tool), and remove any worktree you created.
