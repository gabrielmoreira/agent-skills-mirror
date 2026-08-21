---
name: github-pr-workflow
description: "Drives the GitHub pull-request lifecycle with gh or git+curl: publish the branch, open or update the PR, watch checks, patch failing CI, then squash/merge and delete the branch. Use when the user needs a GitHub PR opened, monitored, or merged. Never a local-only git chair (git-workflow) and not a GitHub issue drafter (github-issue-creator)."
version: 1.1.1
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Pull-Requests, CI/CD, Git, Automation, Merge]
    related_skills: [github-auth, github-code-review]
---

## When to Use

Use this skill when you need to:
- Create a feature or fix branch and open a pull request on GitHub
- Monitor CI check status for an open PR
- Diagnose and auto-fix CI failures
- Merge a PR (squash, merge commit, or rebase) and clean up the branch
- Perform any PR lifecycle operation (branch → commit → push → PR → CI → merge)

Trigger keywords: PR, pull request, merge, CI check, gh pr, branch, commit and push, open a PR, review request.

## Prerequisites

- Authenticated with GitHub (see `github-auth` skill)
- Inside a git repository with a GitHub remote (`origin`)
- `gh` CLI installed and authenticated, **or** a `GITHUB_TOKEN` environment variable available for `curl` fallback

### Quick Auth Detection

Determine which method to use throughout this workflow.

**PowerShell (Windows host — primary):**

```powershell
if (Get-Command gh -ErrorAction SilentlyContinue) {
    $authStatus = gh auth status 2>&1
    if ($LASTEXITCODE -eq 0) { $script:AUTH = "gh" }
}
if (-not $script:AUTH) {
    $script:AUTH = "git"
    if (-not $env:GITHUB_TOKEN) {
        Write-Host "No gh auth and GITHUB_TOKEN is unset. Stop and ask the user to run gh auth login."
    }
}
Write-Host "Using: $script:AUTH"
```

**Bash (Linux/macOS):**

```bash
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"
  if [ -z "$GITHUB_TOKEN" ]; then
    echo "No gh auth and GITHUB_TOKEN is unset. Stop and ask the user to run gh auth login."
  fi
fi
echo "Using: $AUTH"
```

### Extracting Owner/Repo from the Git Remote

Many `curl` commands need `owner/repo`. Extract it from the git remote:

**PowerShell:**

```powershell
$remoteUrl = git remote get-url origin
$ownerRepo = $remoteUrl -replace '.*github\.com[:/]','' -replace '\.git$',''
$OWNER = ($ownerRepo -split '/')[0]
$REPO = ($ownerRepo -split '/')[1]
Write-Host "Owner: $OWNER, Repo: $REPO"
```

**Bash:**

```bash
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
echo "Owner: $OWNER, Repo: $REPO"
```

## Procedure

### 1. Branch Creation

This part is pure `git` — identical on all platforms:

```bash
# Make sure you're up to date
git fetch origin
git checkout main && git pull origin main

# Create and switch to a new branch
git checkout -b feat/add-user-authentication
```

Branch naming conventions:
- `feat/description` — new features
- `fix/description` — bug fixes
- `refactor/description` — code restructuring
- `docs/description` — documentation
- `ci/description` — CI/CD changes

### 2. Making Commits

Use the agent's file tools (`write_file`, `patch`) to make changes, then commit:

```bash
# Stage specific files
git add src/auth.py src/models/user.py tests/test_auth.py

# Commit with a conventional commit message
git commit -m "feat: add JWT-based user authentication

- Add login/register endpoints
- Add User model with password hashing
- Add auth middleware for protected routes
- Add unit tests for auth flow"
```

Commit message format (Conventional Commits):
```
type(scope): short description

Longer explanation if needed. Wrap at 72 characters.
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `ci`, `chore`, `perf`

### 3. Pushing and Creating a PR

#### Push the Branch (same either way)

```bash
git push -u origin HEAD
```

#### Create the PR — With gh

```bash
gh pr create \
  --title "feat: add JWT-based user authentication" \
  --body "## Summary
- Adds login and register API endpoints
- JWT token generation and validation

## Test Plan
- [ ] Unit tests pass

Closes #42"
```

Options: `--draft`, `--reviewer user1,user2`, `--label "enhancement"`, `--base develop`

#### Create the PR — With git + curl

```bash
BRANCH=$(git branch --show-current)

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/$OWNER/$REPO/pulls \
  -d "{
    \"title\": \"feat: add JWT-based user authentication\",
    \"body\": \"## Summary\nAdds login and register API endpoints.\n\nCloses #42\",
    \"head\": \"$BRANCH\",
    \"base\": \"main\"
  }"
```

The response JSON includes the PR `number` — save it for later commands.

To create as a draft, add `"draft": true` to the JSON body.

### 4. Monitoring CI Status

#### Check CI Status — With gh

```bash
# One-shot check
gh pr checks

# Watch until all checks finish (polls every 10s)
gh pr checks --watch
```

#### Check CI Status — With git + curl

```bash
# Get the latest commit SHA on the current branch
SHA=$(git rev-parse HEAD)

# Query the combined status
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/status \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Overall: {data['state']}\")
for s in data.get('statuses', []):
    print(f\"  {s['context']}: {s['state']} - {s.get('description', '')}\")"

# Also check GitHub Actions check runs (separate endpoint)
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/check-runs \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
for cr in data.get('check_runs', []):
    print(f\"  {cr['name']}: {cr['status']} / {cr['conclusion'] or 'pending'}\")"
```

#### Poll Until Complete (git + curl)

```bash
# Simple polling loop — check every 30 seconds, up to 10 minutes
SHA=$(git rev-parse HEAD)
for i in $(seq 1 20); do
  STATUS=$(curl -s \
    -H "Authorization: token $GITHUB_TOKEN" \
    https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/status \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['state'])")
  echo "Check $i: $STATUS"
  if [ "$STATUS" = "success" ] || [ "$STATUS" = "failure" ] || [ "$STATUS" = "error" ]; then
    break
  fi
  sleep 30
done
```

### 5. Auto-Fixing CI Failures

When CI fails, diagnose and fix. This loop works with either auth method.

#### Step 1: Get Failure Details

**With gh:**

```bash
# List recent workflow runs on this branch
gh run list --branch $(git branch --show-current) --limit 5

# View failed logs
gh run view <RUN_ID> --log-failed
```

**With git + curl:**

```bash
BRANCH=$(git branch --show-current)

# List workflow runs on this branch
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/actions/runs?branch=$BRANCH&per_page=5" \
  | python3 -c "
import sys, json
runs = json.load(sys.stdin)['workflow_runs']
for r in runs:
    print(f\"Run {r['id']}: {r['name']} - {r['conclusion'] or r['status']}\")"

# Get failed job logs (download as zip, extract, read)
RUN_ID=<run_id>
curl -s -L \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID/logs \
  -o /tmp/ci-logs.zip
cd /tmp && unzip -o ci-logs.zip -d ci-logs && cat ci-logs/*.txt
```

#### Step 2: Fix and Push

After identifying the issue, use file tools (`patch`, `write_file`) to fix it:

```bash
git add <fixed_files>
git commit -m "fix: resolve CI failure in <check_name>"
git push
```

#### Step 3: Verify

Re-check CI status using the commands from Section 4 above.

#### Auto-Fix Loop Pattern

When asked to auto-fix CI, follow this loop:

1. Check CI status → identify failures
2. Read failure logs → understand the error
3. Use `read_file` + `patch`/`write_file` → fix the code
4. `git add . && git commit -m "fix: ..." && git push`
5. Wait for CI → re-check status
6. Repeat if still failing (up to 3 attempts, then ask the user)

### 6. Merging

#### With gh

```bash
# Squash merge + delete branch (cleanest for feature branches)
gh pr merge --squash --delete-branch

# Enable auto-merge (merges when all checks pass)
gh pr merge --auto --squash --delete-branch
```

#### With git + curl

```bash
PR_NUMBER=<number>

# Merge the PR via API (squash)
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/merge \
  -d "{
    \"merge_method\": \"squash\",
    \"commit_title\": \"feat: add user authentication (#$PR_NUMBER)\"
  }"

# Delete the remote branch after merge
BRANCH=$(git branch --show-current)
git push origin --delete $BRANCH

# Switch back to main locally
git checkout main && git pull origin main
git branch -d $BRANCH
```

Merge methods: `"merge"` (merge commit), `"squash"`, `"rebase"`

#### Enable Auto-Merge (curl)

```bash
# Auto-merge requires the repo to have it enabled in settings.
# This uses the GraphQL API since REST doesn't support auto-merge.
PR_NODE_ID=$(curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['node_id'])")

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/graphql \
  -d "{\"query\": \"mutation { enablePullRequestAutoMerge(input: {pullRequestId: \\\"$PR_NODE_ID\\\", mergeMethod: SQUASH}) { clientMutationId } }\"}"
```

## Examples

### Complete End-to-End Workflow

```bash
# 1. Start from clean main
git checkout main && git pull origin main

# 2. Branch
git checkout -b fix/login-redirect-bug

# 3. (Agent makes code changes with file tools)

# 4. Commit
git add src/auth/login.py tests/test_login.py
git commit -m "fix: correct redirect URL after login

Preserves the ?next= parameter instead of always redirecting to /dashboard."

# 5. Push
git push -u origin HEAD

# 6. Create PR (picks gh or curl based on what's available)
# ... (see Procedure Section 3)

# 7. Monitor CI (see Procedure Section 4)

# 8. Merge when green (see Procedure Section 6)
```

### Useful PR Commands Reference

| Action | gh | git + curl |
|--------|-----|-----------|
| List my PRs | `gh pr list --author @me` | `curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/$OWNER/$REPO/pulls?state=open"` |
| View PR diff | `gh pr diff` | `git diff main...HEAD` (local) or `curl -H "Accept: application/vnd.github.diff" ...` |
| Add comment | `gh pr comment N --body "..."` | `curl -X POST .../issues/N/comments -d '{"body":"..."}'` |
| Request review | `gh pr edit N --add-reviewer user` | `curl -X POST .../pulls/N/requested_reviewers -d '{"reviewers":["user"]}'` |
| Close PR | `gh pr close N` | `curl -X PATCH .../pulls/N -d '{"state":"closed"}'` |
| Check out someone's PR | `gh pr checkout N` | `git fetch origin pull/N/head:pr-N && git checkout pr-N` |

## Pitfalls

- **Missing GITHUB_TOKEN in curl fallback**: If `gh` is not installed, every `curl` command requires `GITHUB_TOKEN` already in the environment. Do not scrape token files. If unset, stop and ask the user to run `gh auth login`.
- **Owner/Repo extraction fails on non-standard remotes**: The sed-based extraction assumes the remote URL contains `github.com`. If you use a GitHub Enterprise instance with a different hostname, adjust the regex accordingly.
- **CI status endpoints are split**: The REST combined status endpoint (`/commits/$SHA/status`) and the check-runs endpoint (`/commits/$SHA/check-runs`) are separate. A green status does not guarantee all check runs have completed. Query both.
- **Auto-merge requires repo settings**: `gh pr merge --auto` and the GraphQL `enablePullRequestAutoMerge` mutation only work if the repository has auto-merge enabled in Settings → General. Otherwise you get an error.
- **Draft PR via curl needs `"draft": true`**: The `gh pr create --draft` flag maps to a JSON field. If using curl and you forget it, the PR is created as ready-for-review immediately.
- **Branch deletion after merge**: `gh pr merge --delete-branch` deletes both remote and local branches. With curl, you must delete the remote branch (`git push origin --delete`) and local branch (`git branch -d`) manually.
- **Auto-fix loop limit**: Do not exceed 3 auto-fix attempts. After 3 failed attempts, stop and ask the user for guidance to avoid infinite loops.
- **PowerShell quoting**: Multi-line commit messages with `-m` work in PowerShell but may require different quoting. Prefer using `git commit -F <file>` for complex messages on Windows.
- **`python3` not available on Windows**: The curl fallback uses `python3` for JSON parsing. On Windows, the executable may be `python` instead of `python3`. Adjust accordingly.

## Verification

After completing each stage, verify success:

1. **Branch created**:
   ```bash
   git branch --show-current
   # Expected: feat/add-user-authentication
   ```

2. **Commit created**:
   ```bash
   git log --oneline -1
   # Expected: <sha> feat: add JWT-based user authentication
   ```

3. **Branch pushed**:
   ```bash
   git status -sb
   # Expected: ## feat/add-user-authentication...origin/feat/add-user-authentication
   ```

4. **PR created**:
   ```bash
   gh pr view --json number,title,state
   # Expected: {"number": 123, "title": "feat: ...", "state": "OPEN"}
   ```

5. **CI passing**:
   ```bash
   gh pr checks
   # Expected: all checks show "pass" with no failures
   ```

6. **PR merged**:
   ```bash
   gh pr view --json state
   # Expected: {"state": "MERGED"}
   ```

7. **Branch cleaned up**:
   ```bash
   git branch -a | grep feat/add-user-authentication
   # Expected: no output (branch deleted locally and remotely)
   ```

## Related skills

- `github-auth` — GitHub authentication setup and token management
- `github-code-review` — Reviewing PRs, adding comments, and requesting changes
