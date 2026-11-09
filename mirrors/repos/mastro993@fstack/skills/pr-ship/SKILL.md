---
name: pr-ship
description: Use when the user asks to ship, land, or merge a change or pull request ("ship it", "get this into main", "merge #42"). Opens the PR or marks a draft ready, babysits CI, keeps automated reviewers (CodeRabbit, Pullfrog, Claude, Copilot, ...) reviewing until a round comes back clean, then merges.
compatibility: Needs the gh CLI (authenticated), git, python3, and the pr-babysit skill from the same plugin.
---

# PR ship

The user asked for the change to land: get it merged through every gate the repo has, once the automated reviewers have nothing new to say.

## 1. Get a PR that's ready for review

Look up the PR the user named, or the current branch's: `gh pr view --json number,url,state,isDraft,headRefName,baseRefName`. Work not yet on the remote (`git status -sb`) ships too: commit its files, asking if it's unclear which belong to it, and push them to the PR's branch.

- **No PR.** On the base branch, move the work to a new branch first. Push with `-u`, then `gh pr create` against the default branch, ready for review. Fill in the repo's PR template if it has one (`.github/pull_request_template.md` or `.github/PULL_REQUEST_TEMPLATE/`), and add `Closes #<n>` when the change resolves an issue.
- **Draft.** `gh pr ready <n>`.
- **Merged already.** With newer commits on the branch, ship those as a new PR from the updated base; otherwise report it with the link and stop. **Closed:** ask before reopening.

## 2. Babysit it

Load the pr-babysit skill and run it to the end: it does the watching, fixing, replying, re-requesting, progress lines, and finishing. Shipping is the go-ahead it otherwise waits for: the PR leaves draft (step 1), and you merge it once step 4's gate holds, which ends the babysit. Steps 3 and 4 run inside that loop.

## 3. Review rounds

A **round** is one review of the current head from each automated reviewer on the repo. A round is **clean** when none of those reviews raises a new finding you change code for: a new thread, `CHANGES_REQUESTED`, or an actionable item in a review or summary body. A finding you answered without a code change, because the bot was wrong, keeps the round clean.

1. **Find the reviewers**: bots that reviewed or commented on this PR or recent ones, and bots whose config or workflow is in the repo. [references/review-bots.md](references/review-bots.md) has, per common bot, its trigger, whether it re-reviews each push on its own, and what clean looks like; for an unlisted bot, its earlier comments show the trigger.
2. **Get a review of the current head from each.** Bots that review on open or push need nothing from you but a few minutes' wait; ask the others once per head with their trigger. If a bot hasn't answered 15 minutes after it should have, ask once more, then leave it out of the round and tell the user.
3. **Handle the findings** as pr-babysit's Acting section says. When a bot answers your reply with nothing new (a thanks), resolve its thread; unlike a human, the bot never will:
   ```bash
   gh api graphql -f query='mutation($id: ID!) { resolveReviewThread(input: {threadId: $id}) { thread { isResolved } } }' -f id=<thread id>
   ```
4. **Repeat** for the new head. Count the rounds whose findings you pushed fixes for. If the review after your third round of fixes still raises a new finding, stop: tell the user what is still being raised and that three rounds already ran, and ask whether to fix and continue, merge as is, or stop. Reviewers can produce new nits forever; the user decides when it's enough.

With no automated reviewer on the repo, the gate is CI plus the reviews the repo requires.

## 4. Merge

Merge when both hold for the same head:

- `pr_watch.py snapshot` prints `READY: yes`. On a repo with no CI at all, set aside its `no checks reported yet` blocker;
- the latest round on that head is clean, with no bot review still pending on it.

Use squash when the repo allows it, otherwise the method it does allow (merge commit over rebase if both): `gh repo view --json squashMergeAllowed,mergeCommitAllowed,rebaseMergeAllowed`. Pin the merge to the head you checked, by its full SHA from `gh pr view <n> --json headRefOid -q .headRefOid`, so a push that lands in between stops it:

```bash
gh pr merge <n> --squash --match-head-commit <full head sha>
```

If GitHub refuses, read why. For a merge queue or a pending requirement, add `--auto` and keep watching until it lands; auto-merge would also take a later push before its round ran, so `gh pr merge <n> --disable-auto` before pushing again and re-enable once the gate holds on the new head. For a required approval or check you can't satisfy, tell the user what's blocking and keep waiting. Merge through the repo's rules, never around them with `--admin`.
