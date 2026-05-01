---
name: azure-devops-create-pr
description: "Create an Azure DevOps pull request for the current story branch. Use when the user says 'create ADO PR', 'open a pull request in Azure DevOps', or 'ready for review in ADO'."
---

# Azure DevOps — Create Pull Request

## Goal

Create a well-structured Azure DevOps pull request that links to the work item, summarises the story, lists verified ACs, and assigns the correct reviewer.

---

## Prerequisite Check

Check `integrations.azure_devops` in `_superml/config.yml`. If missing: "Run `azure-devops-connect` first."

Check current branch:
```bash
git branch --show-current
```

Ensure it's a feature branch (not `main` or `develop`).

---

## Step 1: Load Story Context

Extract from current branch name or ask:
- ADO work item ID: `{ado_id}`
- Story S-ID: `{S-ID}`

Load story file from `{implementation_artifacts}/stories/S-{id}-*.md`.

---

## Step 2: Pre-PR Checks

Run:
```bash
git status
git log origin/{default_branch}..HEAD --oneline
```

If there are uncommitted changes or no commits ahead of default branch, warn and ask to confirm.

---

## Step 3: Build PR Description

Use this format:
```markdown
## Summary
{story_title}

Closes #{ado_id}

## What changed
{brief_description}

## Acceptance Criteria Verified
- [x] AC-1: {description}
- [x] AC-2: {description}

## Test Notes
{testing_approach}

## Screenshots / Evidence
{if_applicable}
```

---

## Step 4: Create PR

```bash
az repos pr create \
  --title "{story_title}" \
  --description "{pr_description}" \
  --source-branch "{feature_branch}" \
  --target-branch "{default_branch}" \
  --work-items {ado_id} \
  --auto-complete false \
  --output table
```

---

## Step 5: Output

> ✅ PR created: {pr_url}
>
> Linked to work item #{ado_id}. Assign reviewers in the PR before requesting review.
