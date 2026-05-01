---
name: github-connect
description: "Set up and verify GitHub integration using the GitHub CLI. Use when the user says 'connect to GitHub', 'set up GitHub', or 'configure GitHub'."
---

# GitHub — Connect and Verify

## Goal

Verify GitHub CLI authentication and store repository details in config so branch creation, PR creation, and other GitHub skills work seamlessly.

---

## Step 1: Check GitHub CLI is Available

```bash
which gh && gh --version
```

If not found:
> "GitHub CLI (`gh`) is not installed. Install it from https://cli.github.com or run:
> - macOS: `brew install gh`
> - Ubuntu: `sudo apt install gh`
> - Windows: `winget install GitHub.cli`"

⏸️ **STOP** — `gh` must be installed.

---

## Step 2: Check Authentication Status

```bash
gh auth status
```

If not authenticated:
```bash
gh auth login
```

Follow the interactive prompts (browser-based OAuth — no token needed manually).

⏸️ **STOP** — must be authenticated before proceeding.

---

## Step 3: Identify Repository

Ask: "What is the GitHub repository? (format: `owner/repo` or paste the URL)"

Verify the repo exists and is accessible:
```bash
gh repo view {owner}/{repo} --json name,defaultBranchRef,visibility | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('Repo:', d['name'])
print('Default branch:', d['defaultBranchRef']['name'])
print('Visibility:', d['visibility'])
"
```

---

## Step 4: Configure Branch Naming Pattern

Ask: "What branch naming pattern should be used?"

Options:
- `feature/{JIRA-KEY}-{slug}` (recommended — links branch to JIRA ticket)
- `{JIRA-KEY}-{slug}`
- `feature/{slug}`
- Custom pattern

---

## Step 5: Save to Config

```yaml
integrations:
  github:
    owner: "{owner}"
    repo: "{repo}"
    default_branch: "{branch}"
    branch_pattern: "feature/{jira_key}-{slug}"
```

---

## Completion

> "✅ GitHub connected.
> Repo: {owner}/{repo}
> Default branch: {branch}
> Branch pattern: {pattern}
>
> Available skills:
> - `github-create-branch` — create feature branch for a story
> - `github-create-pr` — create pull request with JIRA link and ACs"
