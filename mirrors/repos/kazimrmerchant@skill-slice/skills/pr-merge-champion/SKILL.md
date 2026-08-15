---
name: pr-merge-champion
description: "Hardens a feature branch for reviewer speed: rebase-clean diffs, leftover-debug sweeps, local test evidence, and a why-plus-verification PR writeup. Use when the goal is fewer review cycles before a human merge. Not a GitHub lifecycle chair for gh pr create, CI watch, or squash-merge (github-pr-workflow) and not a local-only git chair (git-workflow)."
version: 1.0.1
category: workflow
risk: safe
source: self
source_type: self
date_added: "2026-06-16"
tags: [git, github, pull-request, code-review, workflow]
tools: [claude, cursor, gemini, antigravity]
---

## Overview

A systematic playbook for preparing, reviewing, and documenting pull requests to ensure they are high-quality, free of common oversights, and optimized for instant maintainer approval and merging.

## When to Use

- Use when preparing to open a new pull request on GitHub or any Git hosting platform.
- Use when self-auditing a feature or bug-fix branch for code cleanliness and consistency.
- Use when trying to minimize review cycles and speed up the integration of your changes.

## Prerequisites

- Git installed and configured.
- A local feature branch with committed changes.
- Access to the target repository's `CONTRIBUTING.md` and PR templates.

## Procedure

1. **Pre-Flight Clean Up & Rebase**
   Before presenting your code to reviewers, clean up any workspace noise and ensure your branch is up to date.
   - Rebase your feature branch on top of the latest target branch (e.g., `main` or `master`) to resolve conflicts early.
     ```powershell
     git fetch origin
     git rebase origin/main
     ```
   - Clean up untracked, temp, or swap files from your repository.
     ```powershell
     git clean -fd
     ```
   - Run local linters, formatters, and compilers to ensure no stylistic or syntax errors exist.

2. **Critical Self-Review**
   Review your own diff line-by-line as if you were the reviewer. Look out for:
   - Leftover debugging statements (e.g., `console.log`, `print`, breakpoints, or custom debug flags).
     ```powershell
     git diff | Select-String -Pattern "(console\.log|debugger|print\(|var_dump|binding\.pry)"
     ```
   - Unnecessary changes, white-space only diffs, or commented-out code blocks.
   - Incomplete `TODO` comments that should be resolved or turned into tracked issues.
   - Correctness of error handling and edge cases.

3. **Local Verification & Test Suite**
   Verify that all changes work as expected:
   - Run the project's automated test suite locally to verify no regressions are introduced.
   - Check test coverage for any new code blocks you added.
   - Manually test the critical paths and edge cases of your feature or bug fix.

4. **Crafting the Pull Request Description**
   Write a high-signal, structured PR description. A great description tells the story of the changes:
   - **Summary**: A concise explanation of the changes.
   - **Context / Why**: Why this change is necessary and what problem it solves.
   - **Verification**: Explicit details on how you tested it (test commands, screenshots, or step-by-step reproduction).
   - **Checklist**: Conform to the repository's contributing guidelines and checklist requirements.

## Examples

### Example 1: Creating a Clean PR Description

```markdown
# Pull Request: Implement Rate Limiting on Authentication Endpoint

## Summary
Introduces an IP-based rate limiter on the `/api/v1/auth/login` endpoint using Redis to prevent brute-force attacks.

## Why
We identified a high volume of login attempts targeting single accounts. This rate limiting window slows down attackers while keeping the system responsive for genuine users.

## Verification
- Ran unit tests: `npm run test tests/auth.test.js` (all green)
- Manually verified using Postman: sending 15 requests in under 60 seconds returns `429 Too Many Requests`.

## Checklist
- [x] Code follows the style guide
- [x] Unit tests added/updated
- [x] Documentation updated
```

## Pitfalls

- **Problem:** A PR is left open for a long time due to minor formatting or style comments.
  **Solution:** Always run the repository's local formatter (e.g., Prettier, ESLint, Black) before committing.
- **Problem:** Merge conflicts occur immediately after opening the PR.
  **Solution:** Pull the latest main branch and rebase or merge it into your branch daily.
- **Problem:** Unrelated changes bundled into a feature PR.
  **Solution:** Avoid sneaking refactoring or unrelated bug fixes into a feature PR. Create separate PRs instead.
- **Problem:** Ignoring CI failures.
  **Solution:** Always fix failing tests, linters, or security scans on your branch before requesting a review.

## Verification

- Ensure no unwanted files are staged:
  ```powershell
  git status --porcelain
  ```
- Ensure no leftover debug statements in the diff:
  ```powershell
  git diff | Select-String -Pattern "(console\.log|debugger|print\(|var_dump|binding\.pry)"
  ```
- Verify local tests pass before pushing.

## Related skills

- `@pr-writer` - For Sentry-specific PR writing guidelines.
- `@clean-code` - To ensure code quality before submitting.
