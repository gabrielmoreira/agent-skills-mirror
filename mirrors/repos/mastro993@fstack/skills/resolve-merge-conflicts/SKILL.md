---
name: resolve-merge-conflicts
description: Use when a merge, rebase, cherry-pick, or revert stops on conflicts, when a pull request is blocked by conflicts with its base, or when the user asks to resolve conflicts or bring a branch up to date with its base.
compatibility: Needs git 2.45+ (for `git log --merge` during a rebase or cherry-pick). Works best with the gh CLI and the issue tracker's CLI or MCP, where the reasons behind each side live.
---

# Resolve merge conflicts

A conflict is two changes that each had a reason. Git shows the lines; your job is to recover both reasons and write code that serves both. When they can't both hold, the landing side wins, and the report says what the other side loses.

- **Sides**: name each by what it is ("PR #42", "main") in everything you write. Git's *ours* is the checked-out branch during a merge, but the base being replayed onto during a rebase; *theirs* is the incoming branch, or the commit being replayed.
- **Landing side**: the change the user is trying to get in. It's the PR's branch when the base is merged into it or it is rebased onto the base, and the incoming branch when it is merged into the base. Its intent breaks ties.
- **Intent**: what a side meant to change about how the software behaves, and why, in one sentence with its source (PR, issue, ticket, test).
- **Mechanical conflict**: one whose hunk alone shows both intents, such as both sides adding an entry to the same list, an import, or a changelog line.
- **Semantic conflict**: two changes that merge without a marker and break together. One side renames a function; the other adds a call to the old name.
- **Provenance**: every line of the resolution serves one side's intent, or is glue that makes both hold (a renamed call, a moved import, an argument passed through). A merge commit is the one change nobody reviews, so a line without provenance lands unseen.

## 1. Start

`git status` names an operation already in progress (merge, rebase, cherry-pick, revert); if there is one, go to step 2. Otherwise `git fetch` and start it:

- **Which operation**: the one the user named. Without one, the repo's documented convention (CONTRIBUTING, AGENTS.md, CLAUDE.md). Without that, merge into a branch that's already pushed: a rebase rewrites commits others pulled or reviewed, and ends in a force-push, so it needs the user's or the repo's ask.
- **Ancestor in every hunk**: start it with `-c merge.conflictStyle=zdiff3` (`git -c merge.conflictStyle=zdiff3 merge origin/main`, same for `rebase`). The ancestor is what both sides started from, the only way to tell who changed what. For an operation that already stopped, `git checkout --conflict=zdiff3 -- <file>` rewrites a file's markers, as long as you haven't edited it yet.
- **The user's checkout**: with uncommitted changes or a different branch checked out, leave it exactly as it is. Work in `git worktree add --detach ../<repo>-conflicts origin/<branch>`, push with `git push origin HEAD:<branch>`, and remove the worktree at the end.

Record `git rev-parse HEAD` before starting: it's how the user gets back.

Done when the operation has stopped on conflicts, or has finished without any. In that case go to step 5, since semantic conflicts still need the checks.

## 2. List

`git diff --name-only --diff-filter=U` lists the conflicted files. Lockfiles, generated files, binaries, and files one side deleted or renamed need handling of their own: when any is in the list, read [references/special-files.md](references/special-files.md).

Then list the files both sides changed since the merge base (`git diff --name-only <merge-base>...<side>` for each side, intersected). That's where semantic conflicts hide.

Done when every conflicted file is either a content conflict or handled per special-files.md, and you hold the both-sides list.

## 3. Recover intent

For every hunk that isn't mechanical, work out each side's intent from the evidence around the diff. A hunk that looks like a typo fix can be a security fix; one that looks like a refactor can change behavior on purpose.

1. **Commits**: `git log --merge -p -- <file>` lists both sides' commits that touched the file since the merge base, during any of the four operations. During a rebase, `git show REBASE_HEAD` is the commit being replayed.
2. **Pull requests**: each commit's PR (`gh api repos/{owner}/{repo}/commits/<sha>/pulls`), then its title, body, and review discussion (`gh pr view <n> --json title,body,comments,reviews,closingIssuesReferences`).
3. **Issues and tickets**: the issues the PR closes or links, and ticket keys in commit messages, PR titles, and branch names (`ENG-123`), through the tracker's CLI or MCP. The ticket usually holds the why.
4. **Tests and callers**: the tests each side added or changed are the most precise statement of intent there is.

Read both sides' PRs and issues. The side you're not on is the one whose reasons you don't already know. Look up each commit and PR once, however many hunks it touches.

Write each intent down before editing:

> `src/cart.js` `lineTotal`: **PR #42** (closes #40) applies the discount to each line, because per-order rounding drifted from the invoice. **main**, from PR #45 (fixes #44), rejects quantities below 1, because a negative quantity produced a refund.

Done when every non-mechanical hunk has both sides' intent written with its source. If a side's intent can't be recovered (no PR, a one-word message, no ticket, no test), note that instead and read the intent from the code as narrowly as you can.

## 4. Resolve

Hunk by hunk, from the intents:

- **Both can hold**: write code that does what both meant, adapting one side to the other's structure. If main renamed `calcTotal` to `lineTotal` and the PR added a branch to `calcTotal`, the branch goes into `lineTotal`. Keep both sides' tests.
- **They can't both hold** (one behavior, changed two ways): take the landing side. Change the other side's tests only where they assert the behavior you dropped, and name the loss in the report. When the side you'd drop fixes a security hole or data loss, ask the user before dropping it.

Every line keeps its provenance. A bug or improvement you notice along the way goes in the report, as a change of its own.

`git add` each file as it's done. Done when `git diff --name-only --diff-filter=U` is empty and `git diff --cached --check` finds no leftover markers.

## 5. Check

Run what CI runs, as far as it runs locally. Its config (`.github/workflows/` or the repo's equivalent) names the commands, typically install, typecheck, lint, tests, and build. Run the full set: a semantic conflict breaks files that neither side's hunks touched.

- **Caused by the resolution**: fix it and rerun.
- **A semantic conflict**: resolve it like step 4, from the intents, and report it.
- **Also fails on the base** (run the same command on the base, in a worktree): it isn't yours; report it.

During a rebase, run the fast checks (typecheck or build, and the tests of the files you touched) at each stop, then the full set once the rebase finishes.

Done when every check passes, or fails identically on the base.

## 6. Verify the app

When the conflicting code changes what a user sees or does and the project runs locally (dev server, CLI, simulator), start it with the harness's run or preview tool or the documented start command. Exercise both sides' behavior: the landing side's feature, and the base change it was combined with.

Done when you've seen both behaviors work, or can name what you couldn't run and why (secrets, services, hardware).

## 7. Finish

- **Merge**: `git commit --no-edit`, adding a body line for each non-mechanical hunk: what was combined or dropped, and why.
- **Rebase**: `GIT_EDITOR=true git rebase --continue` keeps each commit's message. Repeat steps 2–5 at every stop until git reports the rebase done, so every commit is replayed with its resolution. `git rebase --skip` would drop the commit's other changes along with its conflict.
- **Cherry-pick or revert**: `--continue`, the same way.

Confirm that nothing was lost. After a rebase, `git log --oneline <base>..HEAD` should list as many commits as before, less any that git dropped as already upstream (it names them). After a merge, `git log -1 --format=%P` should show two parents.

When the conflict was a PR's, push: `git push` after a merge, `git push --force-with-lease` after a rebase. A local merge or rebase the user asked for stays local.

Done when no operation is in progress and the result is either pushed or deliberately left local.

## 8. Report

For each non-mechanical conflict, give the file, each side's intent with its source (as links), and the resolution: combined, or the side taken and what the other loses. Cover all mechanical conflicts in one line. Then list:

- the semantic conflicts found;
- the checks run, with their results;
- what you exercised in the app;
- anything you couldn't recover or verify;
- bugs you noticed that are out of scope;
- after a rebase, the starting SHA.
