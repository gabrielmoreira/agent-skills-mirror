---
name: gh-fix-ci
description: Debug failing GitHub Actions CI checks on the current branch's PR using the gh CLI — inspect logs, summarize root cause, and propose a focused fix plan before implementing.
argument-hint: "[PR number or URL (optional; defaults to current branch PR)]"
user-invocable: true
---

# Fix Failing CI Checks

Use `gh` to locate failing PR checks, fetch GitHub Actions logs, summarize the failure, then propose a fix plan and implement only after explicit user approval.

## Prerequisites

Verify `gh` authentication before doing anything else:

```
gh auth status
```

If unauthenticated, ask the user to run `gh auth login` (repo + workflow scopes required), then stop.

## Workflow

### 1. Resolve the PR

```
# if the user specified a PR number or URL:
gh pr view <number-or-url> --json number,url,headRefName

# otherwise (current branch):
gh pr view --json number,url,headRefName
```

Extract `owner` and `repo` from the returned `url` field — PR URLs have the form `https://github.com/<owner>/<repo>/pull/<number>`, so split on `/` to get the 4th and 5th segments. These are the base (target) repository coordinates where GitHub Actions checks run, and are reliable even for cross-fork PRs.

### 2. Inspect failing checks

```
gh pr checks <pr-number> -R <owner>/<repo> --json name,state,bucket,link,startedAt,completedAt,workflow
```

If a field is rejected, rerun with the available fields reported by `gh`. Scope only to **GitHub Actions** checks. If `link` is not a GitHub Actions run URL, label it as external, report the URL only, and do not investigate further (e.g. Buildkite, CircleCI are out of scope).

### 3. Fetch failure logs

For each failing GitHub Actions check:

1. Extract the run ID from `link` (the numeric segment in the URL).
2. Fetch run metadata:
   ```
   gh run view <run-id> -R <owner>/<repo> --json name,workflowName,conclusion,status,url,event,headBranch,headSha
   ```
3. Fetch logs:
   ```
   gh run view <run-id> -R <owner>/<repo> --log
   ```
4. If the run is still in progress, get the job IDs and fetch logs directly:
   ```
   gh run view <run-id> -R <owner>/<repo> --json jobs
   ```
   Then for each relevant job:
   ```
   gh api "/repos/<owner>/<repo>/actions/jobs/<job-id>/logs"
   ```

Extract a concise failure snippet (relevant error lines and stack traces only).

### 4. Summarize failures

Present a short summary for the user:

- Check name and run URL
- Root cause (1–2 sentences with supporting log snippet)
- Note if logs are missing or truncated

### 5. Plan and get approval

Draft a concise fix plan covering:

- Which files to change and why
- Any tests that need updating
- Expected outcome

**Ask the user for explicit approval before implementing.**

### 6. Implement

Apply the approved plan. Show a summary of diffs and note any tests run.

### 7. Recheck

After changes, suggest:

```
gh pr checks <pr-number> -R <owner>/<repo> --watch
```

to confirm the checks pass.
