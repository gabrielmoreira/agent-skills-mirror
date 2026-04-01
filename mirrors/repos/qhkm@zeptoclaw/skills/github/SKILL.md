---
name: github
description: Interact with GitHub using the gh CLI for pull requests, issues, and runs.
metadata: {"zeptoclaw":{"emoji":"🐙","requires":{"bins":["gh"]}}}
---

# GitHub Skill

Use the `gh` CLI for repository operations.

## Pull Requests

Check CI status:
```bash
gh pr checks 55 --repo owner/repo
```

List workflow runs:
```bash
gh run list --repo owner/repo --limit 10
```

## Issues

List issues:
```bash
gh issue list --repo owner/repo --json number,title,state
```

Create issue:
```bash
gh issue create --repo owner/repo --title "Bug" --body "Description"
```
