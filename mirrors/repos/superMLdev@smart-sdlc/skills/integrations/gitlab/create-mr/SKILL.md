---
name: gitlab-create-mr
description: "Create a GitLab Merge Request for the current story branch. Use when the user says 'create an MR', 'open a merge request', or 'ready for review' in a GitLab project."
---

# GitLab — Create Merge Request

## Goal

Create a well-structured GitLab Merge Request that links to the issue, summarises the story, lists verified acceptance criteria, and assigns the correct reviewer.

---

## Prerequisite Check

Check `integrations.gitlab` in `_superml/config.yml`. If missing: "Run `gitlab-connect` first."

Check current branch:
```bash
git branch --show-current
```

Ensure it's a feature branch (not `main` or `develop`).

---

## Step 1: Load Story Context

Extract from current branch name or ask:
- GitLab issue number: `{issue_id}` (if tracked)
- Story S-ID: `{S-ID}`

Load story file from `{implementation_artifacts}/stories/S-{id}-*.md`.

---

## Step 2: Pre-MR Checks

```bash
git status
git log origin/{default_branch}..HEAD --oneline
```

Warn if there are uncommitted changes or no commits ahead of default branch.

---

## Step 3: Build MR Description

```markdown
## Summary
{story_title}

Closes #{issue_id}

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

## Step 4: Create Merge Request

```bash
glab mr create \
  --title "{story_title}" \
  --description "{mr_description}" \
  --source-branch "{feature_branch}" \
  --target-branch "{default_branch}" \
  --assignee "{your_username}" \
  --no-editor
```

Or via API:
```bash
glab api -X POST "projects/:fullpath/merge_requests" \
  -F "source_branch={feature_branch}" \
  -F "target_branch={default_branch}" \
  -F "title={story_title}" \
  -F "description={mr_description}" \
  -F "remove_source_branch=true"
```

---

## Step 5: Update Story File

```yaml
gitlab_mr_id: {mr_id}
gitlab_mr_url: "{mr_url}"
```

---

## Done

> ✅ MR created: {mr_url}
>
> Assign reviewers and set the ready-for-review label before requesting review.
