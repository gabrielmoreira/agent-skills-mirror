---
name: land-pr
description: Land lossless-claw pull requests safely; use when asked whether a PR is ready, whether CI passes, to merge or land a PR, or to perform maintainer closeout after review.
---

# Lossless PR Landing

Use this skill when landing a `lossless-claw` pull request or answering whether it is ready to merge.

## Workflow

1. Read repository instructions first.
   - Follow `AGENTS.md`, especially data-preservation, changeset, compatibility, and command-reporting rules.
   - If a deterministic merge wrapper exists for this repo, prefer it. Otherwise use the manual fallback below.

2. Identify and pin the PR head.
   - Fetch the real PR metadata:
     ```bash
     gh pr view <PR> --json number,title,state,isDraft,baseRefName,headRefName,headRefOid,mergeable,mergeStateStatus,reviewDecision,statusCheckRollup,author,files,closingIssuesReferences,url
     ```
   - Treat `headRefOid` as the merge pin. Re-read it immediately before merge.

3. Verify readiness.
   - PR must be open, non-draft, mergeable, and clean.
   - All required/current checks must be complete and successful on the pinned head:
     ```bash
     gh pr checks <PR> --json name,state,bucket,workflow,link,startedAt,completedAt
     ```
   - If checks are pending, failing, missing, or tied to a different head SHA, do not merge.
   - If the PR changes package-visible behavior, user-facing behavior, docs-visible behavior, compatibility metadata, config surface, or release behavior, answer the changeset question before merge.
   - Do not expect external contributors to add Changesets metadata. Maintainers own it.

4. Run or confirm final review.
   - Prefer the repo's actual PR base:
     ```bash
     head=$(gh pr view <PR> --json headRefOid --jq .headRefOid)
     base=$(gh pr view <PR> --json baseRefName --jq .baseRefName)
     gh pr checkout <PR>
     test "$(git rev-parse HEAD)" = "$head"
     /Users/phaedrus/Projects/prompts/skills/autoreview/scripts/autoreview --mode branch --base "origin/$base"
     ```
   - Run branch review only from a checkout whose `HEAD` exactly matches the pinned PR `headRefOid`.
   - Verify every accepted finding against the code before acting on it.
   - Do not merge with unresolved actionable findings.

5. Search open issues before merge closeout.
   - Inspect explicit closing references:
     ```bash
     gh pr view <PR> --json closingIssuesReferences --jq '.closingIssuesReferences'
     ```
   - Search open issues for likely duplicates or covered reports using the PR title, key error strings, feature names, changed behavior, and issue numbers mentioned in commits/body:
     ```bash
     gh issue list --state open --limit 50 --search "<keyword terms> repo:Martian-Engineering/lossless-claw"
     ```
   - Read candidate issues before deciding they are covered:
     ```bash
     gh issue view <ISSUE> --json number,title,state,body,url,labels,comments
     ```
   - If an issue is clearly fixed by the PR and not auto-closed by GitHub, close it after merge with a concise comment linking the merged PR.
   - If unsure, leave a comment on the issue noting the PR may help and ask for confirmation instead of closing.

6. Merge deterministically.
   - Preferred wrapper, if present:
     ```bash
     scripts/pr-merge verify <PR>
     scripts/pr-merge run <PR>
     ```
   - Manual fallback:
     ```bash
     head=$(gh pr view <PR> --json headRefOid --jq .headRefOid)
     title=$(gh pr view <PR> --json title --jq .title)
     gh pr merge <PR> --squash --match-head-commit "$head" --subject "$title"
     ```
   - Never use `--auto` for this workflow.
   - Do not merge if the head SHA changed between verification and merge.

7. Post-merge verification and maintainer follow-through.
   - Confirm the PR is `MERGED` and capture the merge commit:
     ```bash
     gh pr view <PR> --json state,mergeCommit,mergedAt,mergedBy,url
     ```
   - Leave a brief thank-you comment for external contributors after merge:
     ```bash
     gh pr comment <PR> --body "Thanks for the contribution, @<login>. This is landed now."
     ```
   - Close any verified covered issues that remain open, with a comment linking the PR and merge.
   - If a required changeset was not included before merge, immediately create a small follow-up PR that adds only the missing `.changeset/*.md`.

8. Final report.
   - State whether the PR was ready and whether it was merged.
   - Include PR number/title, pinned head SHA, check summary, review command/result, merge command, merge commit SHA, contributor thank-you comment URL, issue-search outcome, closed/commented issues, and changeset outcome.
   - Include the commands run and their results in a code block, per `AGENTS.md`.

## Do Not

- Do not delete, purge, truncate, or otherwise discard persisted user data as part of landing.
- Do not bypass failing or pending required checks.
- Do not merge without head-SHA pinning.
- Do not assume no related issues exist just because the PR body lacks `Fixes #...`.
- Do not close ambiguous issues. Comment or report uncertainty instead.
