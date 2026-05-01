---
name: github-create-branch
description: "Create a feature branch for a story, checking for conflicts first. Use when the user says 'create a branch', 'start a branch for story X', or 'create feature branch'."
---

# GitHub — Create Feature Branch

## Goal

Create a feature branch for a story using the configured naming pattern. Always checks if a branch already exists first (conflict layer 2 check).

---

## Prerequisite Check

Check `integrations.github` in config. If missing: "Run `github-connect` first."

---

## Step 1: Identify Story

Ask: "Which story is this branch for?" (accept S-ID, JIRA key, or title)

Load the story and extract:
- JIRA key: `{JIRA-KEY}`
- Story title slug: lowercase, hyphens, max 40 chars

---

## Step 2: Compute Branch Name

Apply the configured branch pattern from config:

```
branch_name = "feature/{JIRA-KEY}-{slug}"
e.g., "feature/PROJ-42-add-user-authentication"
```

---

## Step 3: Conflict Check — Branch Already Exists?

```bash
git fetch --all --quiet
git branch -a | grep -i "{branch_name}"
```

If found:
> "⚠️ Branch `{branch_name}` already exists. This means someone may have already started this story. Run `jira-conflict-detect` for a full check before proceeding."

⏸️ **STOP** if conflict found. Ask: "Are you sure you want to proceed anyway?"

---

## Step 4: Create Branch

Ensure we're on the default branch and up to date:
```bash
git checkout {default_branch}
git pull origin {default_branch}
```

Create the branch:
```bash
git checkout -b {branch_name}
```

Push to remote:
```bash
git push -u origin {branch_name}
```

---

## Step 5: Update Local Story

Add to story frontmatter:
```yaml
branch: "{branch_name}"
branch_created: "{date}"
branch_created_by: "{user_name}"
```

---

## Completion

> "✅ Branch created: `{branch_name}`
> Pushed to origin.
>
> You're now on `{branch_name}`. Ready to implement with `dev-story`."

Ask: "Would you like me to update the JIRA ticket to 'In Progress' as well?"

If yes:
```bash
curl -s -X POST \
  "{jira_url}/rest/api/3/issue/{JIRA-KEY}/transitions" \
  -u "{email}:{api_token}" \
  -H "Content-Type: application/json" \
  -d '{"transition": {"id": "21"}}'
```
(Transition ID `21` is the standard "In Progress" transition. If it fails, list available transitions and ask user to pick.)
