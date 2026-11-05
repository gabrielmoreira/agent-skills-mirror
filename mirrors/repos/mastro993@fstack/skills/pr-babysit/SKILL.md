---
name: pr-babysit
description: Use when the user asks to monitor, watch, babysit, or keep an eye on a pull request through CI, review, and merge, or to get a PR green, mergeable, or landed.
compatibility: Needs the gh CLI (authenticated), git, python3, and a checkout of the PR's repository to push fixes from.
---

# PR babysit

Stay with the PR until it is merged or closed, or the user tells you to stop. Ready to merge (open, checks green, approved or no review required, mergeable and up to date, no thread waiting on a reply) is a milestone, not the end: tell the user, then keep watching. A ready PR can stop being mergeable without anyone touching it, for example when another PR lands on the base branch and leaves it conflicting or behind, or when a late review arrives. "CI is green, now waiting on review" is not a stopping point either. If the user only asked to be told ("let me know when CI finishes"), report and change nothing.

## Watching

`scripts/pr_watch.py` (in this skill's directory) reads everything in one command:

- `python3 <skill-dir>/scripts/pr_watch.py snapshot [PR]`: state, failing checks, threads awaiting reply, and a `READY:` line with the blockers. Start with it; anything already failing or unanswered is your first work.
- `python3 <skill-dir>/scripts/pr_watch.py wait [PR]`: polls every 15 s and exits on the next new event (check failed, checks passed, review or comment, conflict, branch behind base, PR merged or closed) with a fresh snapshot, or after 25 min with `NO CHANGE`. It never repeats what it already printed, and ignores comments from the gh account, which are your own.

To wait, prefer a host PR-watch tool if you have one (for example `watch_pull_request`). Otherwise run `wait` as a background command and end your turn, so waiting costs no tokens and the user can still talk to you; handle its notification, then start it again. Without background commands, run it in the foreground. On `NO CHANGE`, re-arm without messaging the user; a ready PR can sit for hours before someone merges it.

## Acting

Fix failures and review comments as you normally would. These are the points that are easy to get wrong:

- **The user's checkout.** If it has uncommitted changes or another branch checked out, don't switch, stash, or commit there. Work in `git worktree add --detach ../<repo>-pr-<n> origin/<head branch>` (after `git fetch`) and push with `git push origin HEAD:<head branch>`.
- **Base moved.** On `MERGE CONFLICT` or `BEHIND`, bring the base into the PR branch with a merge, never a rebase, so the shared branch keeps its history: `git fetch origin && git merge origin/<base>` in your checkout or worktree, resolve keeping what both sides meant, run the tests, commit, push. With no conflict, `gh pr update-branch <n>` does the same on GitHub. If the two sides change the same behavior in incompatible ways, ask the user instead of picking one. If the push dismissed approvals, re-request review from those reviewers.
- **CI.** A failure that also happens on the base branch isn't this PR's to fix: report it. Infra failures (runner lost, network timeouts) get one `gh run rerun <id> --failed`. Stop and ask after two failed attempts at the same check.
- **Not yours to decide.** Design changes, scope growth, and disagreeing with a human reviewer go to the user. Don't reply on their behalf.
- **Bots.** Check a bot's claim against the code before acting; if it's wrong, reply briefly with why.
- **Commits.** Stage only the files you changed (`git add <paths>`): tests and builds leave artifacts like `__pycache__/` that a broad add pushes into the PR for good. Never force-push a shared branch.
- **Replies.** Reply on each thread you addressed with what changed and the short SHA:
  ```bash
  gh api graphql -f query='mutation($id: ID!, $body: String!) {
    addPullRequestReviewThreadReply(input: {pullRequestReviewThreadId: $id, body: $body}) { comment { url } }
  }' -f id=<thread id from the snapshot> -f body='<reply>'
  ```
  Leave threads unresolved: resolving is how the reviewer says they're satisfied.
- **Re-review.** Once every thread from a human reviewer has a reply, `gh pr edit <n> --add-reviewer <login>`. Not while one of their questions is waiting on the user.
- **Merging.** Only if the user asked. Don't mark a draft ready.

After each push, tell the user in a line what changed, then go back to waiting.

## Finishing

When the PR becomes ready, tell the user in a line, with the link, and keep waiting. Say it again only if it became ready again after something changed.

If you're blocked on the user, ask, and say you'll resume once they answer. Leave a background `wait` running meanwhile, so other events still reach you.

Once the PR is merged or closed, or the user tells you to stop, report the outcome with the PR link, stop any background `wait` (or unwatch with the host tool), and remove any worktree you created.
