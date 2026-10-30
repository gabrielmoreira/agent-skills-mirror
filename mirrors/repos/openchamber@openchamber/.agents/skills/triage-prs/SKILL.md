---
name: triage-prs
description: Load when asked to triage, clean up, batch-process, or work through the open PR queue or backlog — covers the mechanical sweep (stale, conflicts, duplicates), fan-out verdict reviews, and approved batch actions.
---

Turn an unbounded PR queue into a short list of maintainer decisions. The pipeline has three phases; **no GitHub write happens in any phase without the maintainer approving that specific batch** — present verdicts and drafted messages first, act on their word.

Companion: each substantive review inside phase 3 applies the `pr-review` skill; this skill owns only the batch mechanics around it.

**The timeline outranks the snapshot.** Before any verdict or comment on a PR, read its issue comments, reviews (`gh pr view --json comments,reviews` or `gh api repos/{owner}/{repo}/pulls/N/reviews`; a maintainer's *Changes requested* is a review and never appears in the comments list), and commits since the last human event. Never post the generic rebase-request on a PR that already carries a substantive review comment; the author already has their instructions.

**Pickup mode.** PRs with human activity beyond the bot go into their own bucket ("Розмова триває"); each entry runs in pickup mode (`pr-review`, *Process* step 1).

## Phase 1 — Mechanical sweep (no judgment, no LLM verdicts)

Fetch all open PRs with `gh` (the repo is `openchamber/openchamber`):

- **Staleness is the last commit date on the branch, never `updatedAt`** — bots bump `updatedAt` with every comment and label. Fetch last-commit dates with batched GraphQL (`commits(last: 1)`), ~50 PRs per query.
- `gh pr list` silently defaults to 30 rows — always pass `--limit` above the real queue size and print the resulting count.

Bucket every non-draft PR:

| Bucket | Condition | Action template |
|---|---|---|
| Dead | merge conflict AND no author commit in >30 days | close with **stale-close** |
| Conflicted-active | merge conflict, author committed within 30 days | phase 3 review pool; a PR worth taking we rebase and finish ourselves (see *Landing a PR ourselves*). **rebase-request** only when the author has something to decide, or `maintainerCanModify` is false |
| Waiting on author | the last substantive event is a request for changes — a maintainer review with `CHANGES_REQUESTED`, a maintainer push-back comment, or a bot `review:blocked` / `review:needs-evidence` — and the author has neither pushed nor replied since | one line in the report ("чекає автора: <what was asked>"); no re-review, no new comment — the ball is theirs |
| Clean | mergeable and not waiting on the author | phase 3 review pool |
| Draft | `isDraft` | untouched while the author committed within 14 days, and always for the team's own drafts (`btriapitsyn`, `yulia-ivashko`, `deatheros`, `AlexKutas`); otherwise close with **stale-draft** |

Then detect **duplicate clusters** across the survivors: pairs with high title-token overlap or high changed-file overlap. For each cluster recommend one keeper (prefer: mergeable over conflicted, references an issue, smaller diff, earlier author — a later near-identical body is likely a regenerated copy of the earlier PR, and the earlier author keeps the credit); the rest close with **duplicate-close**.

Deliver the sweep as one report (counts per bucket, per-bucket tables with number/title/author/size/last-commit-age/areas, clusters with keeper recommendations) and stop for approval.

## Phase 2 — Approved batch actions

Execute the approved closes/comments with retries and ~1–2s spacing between calls. Log every result; report exact ok/fail counts and re-verify the open-PR total afterwards. Branch protection may reject merges — `--admin` is available and accepted for maintainer-approved merges; a merge that becomes conflicted mid-batch, usually because two PRs touch the same file, can be resolved in a temporary worktree and pushed to the contributor's branch when `maintainerCanModify` is true.

## Phase 3 — Verdict reviews

**Trusted community reviewers.** `yulia-ivashko` is a core maintainer with merge rights — her review decisions carry maintainer weight (a PR she approved or merged needs no re-verdict; her open questions are the maintainer's questions). Comments and reviews from `patrick-motard` and `mattv8` are strong human signals: during any sweep, collect the PRs/issues they weighed in on, read their assessment, and carry it into the verdict — an approval from them upgrades confidence like a passing verifier; a concern from them is a finding to verify, never to ignore. They write free-form; map their conclusion onto the verdict ladder rather than expecting the format.

PRs closed by the contribution gate (label `needs-accepted-issue`, `.github/scripts/pr-checks.cjs`) are not in the queue: they reopen on their own once they link a bug report or an accepted feature request. PRs labeled `evidence-in-branch` or `needs-visual-evidence` are *waiting on author*, one line each in the report; the label comes off on its own once fixed, and removing it by hand waives the check for that PR. The retired `needs-discussion` label from the earlier parking rule is size information only; such a PR is an ordinary review pool entry.

The review bot's `review:*` labels are a pre-sort, not a verdict: `review:ready` PRs go first (the bot found no code defects — likely MERGE/MERGE-THEN-FIX), `review:blocked` ones carry a bot comment whose findings the verdict review verifies rather than rediscovers. Bot labels never replace the pr-review pass — the bot cannot judge product fit or maintainability scope.

Split the clean pool smallest-first (tiny diffs are fast wins and most likely mergeable). Fan out the `review` subagent (`.opencode/agent/review.md`, which loads the `pr-review` skill and carries the hard rules). It takes one PR or several per call — group related PRs together when one context can serve them, give a large or contentious PR its own call; fall back to a general subagent that receives the full `pr-review` skill text when `review` is unavailable. Never hand verdicts to a smaller model to save quota — a verdict from a small model is a pre-sort, not a decision. Each returns per-PR verdict blocks in the skill's output format.

**Report format.** The consolidated report is what the maintainer decides from — calibrate each entry so no follow-up question is needed, without ballooning:

- One entry per PR, 2–4 sentences: what it does for the user, whether the problem is real, why this verdict, the main risk or the thing the decision turns on. "Closes #N" links included.
- A "needs your hands" line appears only when the check gates the merge (per the pr-review skill), and lives INSIDE the PR's own entry as its final line — never as a separate section repeating the numbers. A plain MERGE entry carries no checklist.
- Thread-state line first for pickup-mode entries.
- A one-line entry ("точковий фікс") is fine only for genuinely trivial diffs; a verdict the maintainer must weigh (product calls, larger features) gets the full 4 sentences.

Consolidate into a single report grouped by verdict — MERGE, MERGE-THEN-FIX, PUSH-BACK (with the drafted lists), DECLINE (with the drafted close comments), plus every "needs your hands" line — and stop for approval. **Each entry carries the subagent's Ready action verbatim** — the comment or follow-up list exactly as it will be posted or executed, in a quote block under the entry. The consolidation summarizes the reasoning, never the artifact: a paraphrased push-back item loses the file, the cause, and the "done means" the subagent already found, and the maintainer approves what they can read, not a description of it. After approval: post/merge per verdict, and queue MERGE-THEN-FIX follow-ups as in-house work the same day.

If a batch subagent skips a PR, notice (count outputs against inputs) and re-dispatch the gap.

A PR whose verdict needs more than a review — deep investigation of a core path, a rework against code `main` has rewritten, or a live check — can go to its own session with the PR linked to it. Keep it the exception: most PRs, including fix-then-merge ones, are finished inside the triage session.

### Landing a PR ourselves

The default for a PR we want is fix-then-merge in the author's branch, with the author keeping the credit. `scripts/prep.sh <N>` puts the whole PR on current `main` as one staged change in a throwaway worktree (conflicts resolved once, not per commit); after fixing and validating there, `scripts/finish.sh <N> "<subject>" "<comment>" ["Closes #M"]` commits as the author, pushes to their branch, posts the comment and squash-merges.

- **Take the essence.** When `main` has moved under a PR, or the PR bundles extras, land the part that fixes the problem and leave the rest: the 6-line fix out of 250 lines of instrumentation, the concurrency cap without the profiler scenario, the bug fix without the limit bump. A PR that mixes a fix with a change to how the app looks lands the fix; the look goes to the maintainer as a decision. The comment to the author names what was left out and why.
- **A dropped concern is checked in the whole diff.** Conflict hunks are not the whole PR: auto-merged hunks of a concern you decided to leave out still land. Before finishing, grep the staged diff for that concern by its own terms.
- **Review findings on the branch are verified, not obeyed.** Read every unresolved bot and reviewer comment against the current head: one a later push fixed or made moot is done, the rest stand however old they are. Answer each finding the way `openchamber-change-discipline` (*Answering Review Findings*) says, and a finding you decline gets a written reason in the PR, so the next reader does not raise it again.
- **A red check is read before it is believed.** Find which check failed: the review bot's `automation` job failing means the bot did not run, and a test that fails on the PR but passes on current `main` is a stale run, not the PR.
- **Renovate PRs that touch the same file conflict with each other once one lands.** Merge them one at a time; for the rest tick the rebase checkbox in the PR body (`gh pr edit --body-file`) and come back.

### Optional: decision rounds through the question tool

When the batch holds more than a handful of verdicts, offer this alongside the consolidated report: "I can walk you through them as cards instead, a few at a time." Use it only if the maintainer says yes; a large report is otherwise read in one go.

A round is one call to the question tool with 4–6 cards. Each card is one decision:

- **Header**: `#N` plus two or three words naming the behavior (`#3640 Cmd+Enter`), within 30 characters.
- **Body**: the PR as a markdown link (`[#N](https://github.com/openchamber/openchamber/pull/N)`; the cards render markdown) with a plain title on the first line, then 3–4 sentences about what the user sees in the app today, what changes after the PR, and what it costs (risk, a new surface, a dependency, a support burden). Describe behavior, never file names; spell out jargon the maintainer would not use.
- **Options**: 2–3, the recommended one first with `(Recommended)`. Each option says its consequence ("Close: /btw stays a command"), not only a verb. When our own follow-up is part of the verdict, the option says so ("Merge, then we fix the 1px offset").

Order the rounds by how much the maintainer is needed: product decisions first, then plain bug-fix merges, then fix-before-merge, then merge-then-fix, and last one card that confirms all mechanical closes (duplicates, superseded, stale) as a list. A group of trivial, uncontested merges (translations, one-line fixes) shares one card with a one-line description per PR.

Between rounds:

- A free-text answer is read for what it is. When it states a decision (often with how to word the reply), act on it; when it asks or doubts, answer that before moving on and re-ask the PR in the next round with the corrected facts.
- When the maintainer doubts a claim ("are you sure that's still broken?", "that sounds fragile"), check the code and the current `main` yourself before replying; a reviewer's verdict is a lead, not proof. Report what you found in plain words, then re-ask.
- A product decision the maintainer states during the rounds is binding: record it where it will be found next time (memory, or the owning skill) as soon as it is given.

When every card is answered, show one summary grouped by outcome, list what will need the maintainer's own hands (a live check on a device or a packaged app), and get one explicit go before any GitHub write. Comments to people the maintainer works with closely (team members, regular volunteers) are shown as drafts before posting; the rest go out in the maintainer's voice without a separate review.

After a batch of merges:

1. Run the full type-check and every package's test suite on current `main`. `main` has no CI of its own, and PRs validated one by one were never validated together.
2. Write a symptom map of what landed (area, PR, merge sha, which part we wrote) to `docs/personal/pr-triage/pr-triage-<date>-merged.md`, so a later regression can be traced to its PR quickly.
3. Write the testing list for the maintainer to `docs/personal/pr-triage/pr-triage-<date>-what-changed.md`, in Ukrainian: grouped by area of the app, each entry a linked PR (or commit) and two or three sentences on what the user sees change, marking single-platform changes and the parts we rewrote.

## Message templates

Canonical texts. Reuse verbatim, adjusting only bracketed parts.

**stale-close**
> Closing this as stale: the branch has merge conflicts with `main` and hasn't been updated in over a month. The codebase has moved on significantly since this was opened, so this change would need to be redone against the current state anyway.

**rebase-request**
> Sorry for the review backlog. The queue is currently far beyond what I can get through. This PR has merge conflicts with `main`, and I can only review PRs that merge cleanly. If you're still interested in landing this, please rebase. Conflicted PRs without activity will eventually be closed as stale.

**stale-draft**
> Closing this as stale: it's been a draft with no new commits for a while, and `main` has moved on a lot since, so it would need redoing against the current code anyway. Thanks for the work on it.

**duplicate-close**
> Closing as a duplicate of #[N], which will be reviewed instead[: one-clause reason it was kept].

**oversized-split** (single PR bundling several concerns)
> Closing this one. It bundles several unrelated concerns, [list], into a single [size] change across [n] files, which isn't reviewable in this form.

**russian-locale** (any PR adding Russian localization: a standing decision, applied without re-asking; the maintainer's own words, "we" included)
> We're not accepting Russian localization for OpenChamber.
>
> This is an intentional maintainership decision due to Russia's ongoing war against Ukraine. We don't want to ship or maintain Russian UI support.
>
> Closing.
