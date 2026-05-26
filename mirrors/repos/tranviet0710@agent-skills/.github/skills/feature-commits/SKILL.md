---
name: commits
description: "Analyze git changes and split them into multiple focused commits grouped by feature. Use when: dividing changes into commits, organizing staged/unstaged changes, writing conventional commits, splitting work into atomic commits, commit best practices, multi-feature commit plan."
argument-hint: "Optional: describe the overall goal or feature names to guide grouping"
---

# Feature Commits

Split all current git changes into multiple atomic commits, each scoped to one feature or concern, following conventional commits best practices.

## When to Use

- You have changes spanning multiple features or concerns in a single working tree
- You want to produce a clean, reviewable commit history before pushing or opening a PR
- You need commit messages that follow the Conventional Commits specification

## Procedure

### Step 1 — Gather All Changes

Use `get_changed_files` to retrieve every staged and unstaged file with its diff. Also run `git status` in the terminal to get a complete picture of new/deleted/renamed files.

### Step 2 — Analyze and Group by Feature

Read each diff and assign every file to a **logical group**. Apply these rules:

| Signal | Rule |
|--------|------|
| Same feature folder or module | Group together |
| Only docs / README changes | Separate `docs` commit |
| Only config / tooling files (`.gitignore`, `package.json`, CI files) | Separate `chore` or `build` commit |
| Style-only changes (whitespace, formatting) | Separate `style` commit |
| Test files only | Separate `test` commit |
| Bug fix in one module | Separate `fix` commit |
| New capability in one module | Separate `feat` commit |
| Refactor with no behavior change | Separate `refactor` commit |

If a file touches multiple concerns, assign it to the **dominant** concern. Flag ambiguous files for user confirmation before committing.

### Step 3 — Draft Commit Plan

Present a numbered commit plan in this format:

```
Proposed commit plan
────────────────────
1. feat(cart-freeship-bar): add free shipping progress bar UI
   Files: cart_freeship_bar/main-display-and-settings.html

2. feat(cart-freeship-bar): handle language change event
   Files: cart_freeship_bar/event-change-lang.html

3. fix(cart): handle remove-item and clear-cart edge cases
   Files: cart_freeship_bar/event-remove-item-from-cart.html
          cart_freeship_bar/event-clear-cart.html

4. docs(cart-freeship-bar): update README and project overview
   Files: cart_freeship_bar/README.md
          cart_freeship_bar/cart_freeship_bar.md
          cart_freeship_bar/project-overview.md
```

Ask the user to confirm, merge, reorder, or rename commits before proceeding.

### Step 4 — Execute Commits

For each commit in the approved plan:

1. Stage only the files in that group:
   ```
   git add <file1> <file2> ...
   ```
2. Commit with the drafted message:
   ```
   git commit -m "<type>(<scope>): <subject>"
   ```
3. Confirm the commit was created (`git log --oneline -1`).
4. Move to the next group.

Never stage files from a different group during a commit step.

### Step 5 — Verify

After all commits:
- Run `git status` — working tree should be clean (or show only intentionally untracked files).
- Run `git log --oneline -<N>` (where N = number of commits made) to display the final history for the user to review.

---

## Conventional Commits Quick Reference

```
<type>(<scope>): <subject>          ← max 72 chars
<blank line>
[optional body]                     ← wrap at 72 chars; explain *why*, not *what*
<blank line>
[optional footer]                   ← e.g. Closes #123, BREAKING CHANGE: ...
```

**Types:**

| Type | When |
|------|------|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, whitespace, no logic change |
| `refactor` | Code restructure, no behavior change |
| `test` | Adding or updating tests |
| `chore` | Build process, tooling, dependencies |
| `perf` | Performance improvement |
| `ci` | CI/CD configuration |
| `revert` | Reverts a previous commit |

**Rules:**
- Subject line: imperative mood ("add", not "added" or "adds"), no period at end
- Scope: lowercase, reflects the module or folder (e.g., `cart`, `email-collector`)
- Breaking changes: add `!` after type/scope (`feat!:`) **and** a `BREAKING CHANGE:` footer

---

## Decision Points

**Mixed concern in one file?**
→ If the diff is small and inseparable, include it in the most relevant group and note it in the commit body.

**Unclear feature boundary?**
→ Ask the user: *"Should [file X] be part of commit #2 (feat: cart step) or a separate commit?"*

**Many small files in one folder?**
→ Group into one commit unless they serve clearly distinct purposes.

**Untracked new files?**
→ Include them in the commit that introduces the feature they belong to.
