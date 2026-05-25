---
name: azure-devops-pr-review
description: "Structured code review for Azure DevOps pull requests with multi-pass analysis and inline comment posting. Use this skill whenever the user mentions reviewing a PR, code review, pull request, ADO PR, wants feedback posted to DevOps, or asks to look at someone's changes — even if they don't say 'code review' explicitly."
author: "Christian Fleishmann Silva (Oglaf)"
version: "1.0.0"
---

# `review-pr`

Code review an Azure DevOps pull request.

---

## Inputs

| Input            | Required | Description                                              |
| ---------------- | -------- | -------------------------------------------------------- |
| `prUrl`          | ✅*       | Full PR URL (e.g. `https://dev.azure.com/org/project/_git/repo/pullrequest/12345`) |
| `prId`           | ✅*       | Pull request ID (e.g. `12345`)                           |
| `organization`   | ✅*       | Azure DevOps organization name (e.g. `myorg`)            |
| `project`        | ✅*       | Project name or ID                                       |
| `repo`           | ✅*       | Repository name or ID                                    |

\* Either provide `prUrl` (all inputs will be extracted from it), or provide all of `prId`, `organization`, `project`, and `repo` individually.

If any required input cannot be determined, ask the user before proceeding.

---

## Priority Ordering

PRIORITY 1: Only report issues with confidence ≥ 75 — never surface false positives or stylistic concerns. PRIORITY 2: Always confirm findings with the user before posting inline comments. PRIORITY 3: Use parallel multi-model analysis (gpt-5.4 + claude-sonnet-4.6) and deduplicate overlapping findings. When these conflict, prefer fewer high-confidence findings over comprehensive low-confidence coverage.

---

## Overview

Provide a structured code review for a given Azure DevOps PR, including validation, multi-pass analysis, and inline feedback posting.

---

## Workflow

### 0. Parse Inputs

If the user provides a full PR URL (e.g. `https://dev.azure.com/myorg/My%20Project/_git/my-repo/pullrequest/12345`), extract:

* `organization` — the first path segment after `dev.azure.com` (e.g. `myorg`)
* `project` — the second path segment, **URL-decoded** (e.g. `My Project` from `My%20Project`)
* `repo` — the path segment after `_git/` (e.g. `my-repo`)
* `prId` — the path segment after `pullrequest/` (e.g. `12345`)

Then configure the CLI defaults so every subsequent command uses these values without relying on auto-detection:

```powershell
az devops configure --defaults `
  organization="https://dev.azure.com/{organization}" `
  project="{project}"
```

Use `--detect false` on every `az` command from this point on. Never rely on `--detect true` — it fails when the working directory is not a clone of that exact repository.

---

### 1. Check Eligibility

Run:

```powershell
az repos pr show --id {prId} --detect false
```

Ensure the PR:

* Is **open**
* Is **not a draft**
* Has **not already been reviewed by you** — check with:

```powershell
az repos pr reviewer list --id {prId} --detect false
```

If `isRequired: false` and the reviewer entry has `vote != 0`, a review has already been cast. Skip if so.

Skip if any condition fails.

---

### 2. Get Context

#### Instruction Files

Locate relevant guidance files:

* `.github/copilot-instructions.md` (root-level, if present)
* `AGENTS.md`
* `CLAUDE.md`

Search in:

* Modified directories
* Their ancestor directories

#### Retrieve PR Diff

1. Get target branch:

```powershell
az repos pr show --id {prId} --detect false --query "targetRefName" -o tsv
```

2. Checkout PR branch:

```powershell
az repos pr checkout --id {prId}
```

3. Generate diff:

```bash
git diff origin/{targetBranch}...HEAD
```

#### Optional: Check Policy Status

```powershell
az repos pr policy list --id {prId} --detect false --output table
```

Note any failing required policies in your review summary. Do not block or abort the review due to policy failures — just surface them to the user.

---

### 3. Review the Changes

#### Review Strategy

Spawn specialist subagents for the languages/domains in the diff (e.g. React, security, SQL, infrastructure). For each specialist and general reviewer, provide:

* The full diff output from Step 2
* The content of any instruction files found
* The task: "Review this diff for issues in your domain. Return a list of findings with file path, line number, description, and confidence score 0–100."

Always include two general-purpose passes:

  * One pass with `gpt-5.4`
  * One pass with `claude-sonnet-4.6`

Spawn all agents in parallel, then collect and deduplicate overlapping findings before proceeding.

#### Review Focus Areas

* Compliance with instruction files
* Functional correctness
* Git history / blame insights
* Violations of code comments or guidance

---

### 4. Validate Issues

Assign confidence scores:

| Score | Meaning                    |
| ----: | -------------------------- |
|  0–25 | False positive / stylistic |
|    50 | Minor issue                |
|    75 | Important issue            |
|   100 | Definite problem           |

**Only include issues with confidence ≥ 75**

---

### 5. Post Review

#### a. Confirm with User

* Present summary of findings
* Ask for confirmation before posting
* Skip confirmation only if explicitly requested

---

#### b. Post Inline Comments (Required)

**One issue per thread**

Example:

```bash
cat > /tmp/review-thread.json << 'REVIEW_EOF'
{
  "comments": [
    {
      "parentCommentId": 0,
      "content": "<Issue summary + why it matters + actionable fix>",
      "commentType": "text"
    }
  ],
  "status": "active",
  "threadContext": {
    "filePath": "/src/path/to/file.ext",
    "rightFileStart": { "line": 42, "offset": 0 },
    "rightFileEnd": { "line": 42, "offset": 0 }
  }
}
REVIEW_EOF
```

Post:

```powershell
az devops invoke --area git --resource pullRequestThreads `
  --route-parameters project="{project}" repositoryId="{repo}" pullRequestId="{prId}" `
  --http-method POST --api-version 7.1-preview `
  --detect false --in-file /tmp/review-thread.json
```

#### Line Number Rules

* Use **right-side (new file)** line numbers
* From diff: `@@ -35,3 +39,7 @@` → use `39`
* Verify with:

```bash
grep -n '<text>' <file>
```

#### Valid Thread Status

* `active`
* `fixed`
* `wontFix`
* `closed`
* `byDesign`
* `pending`

---

### 6. Tag PR as AI-Reviewed

#### Labels to Add

* `ai-reviewed`
* `ai-model-gpt-5.4`
* `ai-model-claude-sonnet-4.6`

#### Script

```powershell
$modelIds = @("gpt-5.4", "claude-sonnet-4.6")
$labels = @("ai-reviewed") + ($modelIds | ForEach-Object { "ai-model-$_" })
```

Retrieve IDs:

```powershell
$prInfo    = az repos pr show --id {prId} --detect false | ConvertFrom-Json
$projectId = $prInfo.repository.project.id
$repoId    = $prInfo.repository.id
```

Get token:

```bash
TOKEN=$(az account get-access-token \
  --resource 499b84ac-1321-427f-aa17-267ca6975798 \
  --query accessToken -o tsv)
```

Fetch existing labels:

```bash
curl -sS -H "Authorization: Bearer ${TOKEN}" \
"https://dev.azure.com/{organization}/${PROJECT_ID}/_apis/git/repositories/${REPOSITORY_ID}/pullRequests/{prId}/labels?api-version=7.1"
```

Add missing labels via POST.

---

### 7. If No Issues Found

Post:

```md
### Code review

No issues found. Checked for bugs and instruction file compliance.

🤖 Generated with AI
```

Then proceed to **Step 6** to tag the PR as AI-reviewed.

---

## Avoid False Positives

Do **not** report:

* Pre-existing issues
* CI/linter/type errors
* Minor stylistic concerns (unless mandated)
* Intentional changes
* Issues in unmodified lines
* Missing tests/docs (unless required)

---

## Inline Comment Format

Each thread:

```
<brief issue title>

<why this is a problem in this specific code path>

<clear, actionable suggestion>

🤖 Generated with AI
```

---

## Azure DevOps Code Links

Format:

```
https://dev.azure.com/{org}/{project}/_git/{repo}?path=/{file-path}&version=GC{commit}&lineStart={start}&lineEnd={end}
```

Rules:

* Include full commit hash
* Include surrounding context
* File path must start with `/`

---

## Notes

* Do not run builds or CI checks
* Keep comments concise and actionable
* Always deduplicate findings across models