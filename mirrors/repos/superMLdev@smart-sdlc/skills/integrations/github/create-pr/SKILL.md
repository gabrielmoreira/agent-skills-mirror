---
name: github-create-pr
description: "Create a pull request for the current story branch with JIRA link and AC summary. Use when the user says 'create a PR', 'open a pull request', or 'ready for review'."
---

# GitHub — Create Pull Request

## Goal

Create a well-formatted pull request that links to the JIRA ticket, summarizes the story, lists ACs verified, and guides reviewers effectively.

---

## Prerequisite Check

Check `integrations.github` in config. If missing: "Run `github-connect` first."

Check current branch:
```bash
git branch --show-current
```

Ensure it's a feature branch (not `main` or `develop`). If on default branch, warn and ask which branch to create PR from.

---

## Step 1: Load Story Context

Extract from current branch name or ask:
- JIRA key: `{JIRA-KEY}`
- Story S-ID: `{S-ID}`

Load story file from `{implementation_artifacts}/stories/S-{id}-*.md`.

---

## Step 2: Pre-PR Checks

Run:
```bash
# Ensure branch is pushed
git status
git log origin/{default_branch}..HEAD --oneline
```

Report:
```
Branch: {branch_name}
Commits ahead of {default_branch}: {n}
Changed files: {list}
```

Ask: "Are all changes committed and pushed? Any merge conflicts to resolve first?"

⏸️ **STOP** — confirm branch is clean.

---

## Step 3: Build PR Description

Generate PR description from the story:

```markdown
## {story_title}

**JIRA:** [{JIRA-KEY}]({jira_url}/browse/{JIRA-KEY})
**Story:** {S-ID}
**Epic:** {epic_name}

---

## Summary

{user_story_text}

{2-3 sentence description of what was implemented and any notable approach decisions}

---

## Acceptance Criteria Verified

- [x] AC-1: {criteria} — _tested: {test_name}_
- [x] AC-2: {criteria} — _tested: {test_name}_
- [x] AC-3: {criteria} — _tested: {test_name}_

---

## Tests

- Tests written: {n}
- All tests passing: ✅
- Run: `{test_command}`

---

## Security Checklist

- [x] Input validation in place
- [x] No hardcoded secrets
- [x] Auth checks verified
- [x] Error messages don't leak internals

---

## Notes for Reviewer

{any specific areas to focus review attention on}
```

⏸️ **STOP** — review and edit the PR description before creating.

---

## Step 4: Create the PR

```bash
gh pr create \
  --title "{JIRA-KEY}: {story_title}" \
  --body "{pr_description}" \
  --base {default_branch} \
  --head {branch_name} \
  --label "story,superml"
```

---

## Step 5: Update JIRA

Update JIRA ticket to "In Review":
```bash
curl -s -X POST \
  "{jira_url}/rest/api/3/issue/{JIRA-KEY}/transitions" \
  -u "{email}:{api_token}" \
  -H "Content-Type: application/json" \
  -d '{"transition": {"id": "31"}}'
```

Add PR link as JIRA remote link:
```bash
curl -s -X POST \
  "{jira_url}/rest/api/3/issue/{JIRA-KEY}/remotelink" \
  -u "{email}:{api_token}" \
  -H "Content-Type: application/json" \
  -d '{"object": {"url": "{pr_url}", "title": "PR: {pr_title}"}}'
```

---

## Completion

> "✅ Pull Request created: [{pr_title}]({pr_url})
> JIRA ticket moved to 'In Review'."

Ask: "Would you like to request specific reviewers?"

If yes:
```bash
gh pr edit {pr_number} --add-reviewer {username1},{username2}
```
