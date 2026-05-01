---
name: commit-msg-gen
description: "Generate conventional commit messages without scope from staged changes. Use when: preparing commits with #git_diff_staged to create concise commit messages following conventional commits format."
argument-hint: "Optional: specify commit type (fix, feat, refactor, docs, etc.) or leave empty for auto-detection"
---

# Conventional Commit Message Generator

Generate conventional commit messages following the [Conventional Commits](https://www.conventionalcommits.org/) specification, without scope prefix.

## When to Use

- You have staged changes and need a properly formatted commit message
- You want commit messages that follow conventional commits format
- You need concise messages without scope (e.g., `fix: description` instead of `fix(scope): description`)

## Procedure

1. Stage your changes using git add
2. Invoke this skill in chat
3. The skill will:
   - Fetch staged changes using `#git_diff_staged`
   - Analyze the changes to determine commit type (fix, feat, refactor, etc.)
   - Extract the primary file name from changes
   - Generate a conventional commit message in format: `type: description in \`FileName\``

## Commit Message Format

```
type: description in `FileName`
```

### Supported Types

- `fix` - Bug fixes
- `feat` - New features
- `refactor` - Code refactoring
- `docs` - Documentation changes
- `style` - Code style changes (formatting, etc.)
- `test` - Test additions or updates
- `chore` - Build, dependencies, tooling

## Examples

```
fix: improve form initialization and modal state handling based on fetch completion in `QualityCheckResultsModal`
feat: add authentication guard to protected routes in `AuthGuard`
refactor: simplify data validation logic in `FormValidator`
```