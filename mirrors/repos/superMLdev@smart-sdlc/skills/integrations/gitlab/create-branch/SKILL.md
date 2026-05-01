---
name: gitlab-create-branch
description: "Create a GitLab feature branch for a story. Use when the user says 'create a branch', 'start a branch for story X', or 'create feature branch' in a GitLab project."
---

# GitLab — Create Feature Branch

## Goal

Create a feature branch for a story using the configured naming pattern. Always checks if a branch already exists first before creating.

---

## Prerequisite Check

Check `integrations.gitlab` in `_superml/config.yml`. If missing: "Run `gitlab-connect` first."

---

## Step 1: Identify Story

Ask: "Which story is this branch for?" (accept S-ID, title, or GitLab issue number)

Load the story and extract:
- Issue or ticket reference: `{ref}`
- Story title slug: lowercase, hyphens, max 40 chars

---

## Step 2: Compute Branch Name

Apply the configured branch pattern:

```
branch_name = "feature/{ref}-{slug}"
e.g., "feature/42-add-user-authentication"
```

---

## Step 3: Conflict Check

```bash
git fetch --all --quiet
git branch -a | grep -i "{branch_name}"
```

Or via CLI:
```bash
glab api "projects/:fullpath/repository/branches/{branch_name}" 2>/dev/null | jq '.name'
```

If found:
> "⚠️ Branch `{branch_name}` already exists. Confirm before proceeding."

⏸️ **STOP** — ask for confirmation.

---

## Step 4: Create Branch

Ensure default branch is up to date:
```bash
git checkout {default_branch}
git pull origin {default_branch}
```

Create and push:
```bash
git checkout -b {branch_name}
git push -u origin {branch_name}
```

Or via CLI:
```bash
glab api -X POST "projects/:fullpath/repository/branches" \
  -F "branch={branch_name}" \
  -F "ref={default_branch}"
```

---

## Step 5: Update Story File

Add branch reference to story frontmatter:
```yaml
gitlab_branch: "{branch_name}"
branch_created: "{date}"
```

---

## Done

> ✅ Branch `{branch_name}` created and pushed to GitLab.
