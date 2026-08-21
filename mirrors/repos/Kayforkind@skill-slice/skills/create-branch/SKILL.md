---
name: create-branch
description: Creates a git branch using Sentry's username/type/short-description convention, proposing feat, fix, ref, chore, or similar from the task or local diff after user confirmation. Use when asked to create, start, or switch to a new branch. Not for commits, rebase, merge, or pull requests (git-workflow). Do not use to rename existing branches or overwrite a name that already exists.
argument-hint: '[optional description of the work]'
risk: critical
source: community
version: 1.0.1
---

# Create Branch

Create a git branch with the correct type prefix and a descriptive name following Sentry conventions. The resulting branch name follows the pattern `<username>/<type>/<short-description>`.

## When to Use

- You need to create a new git branch that follows the repository's naming convention.
- You are starting a new piece of work from the default branch and need help classifying it as `feat`, `fix`, `docs`, or another branch type.
- You want the branch name proposed from either the task description or the current local diff.
- Trigger keywords: "create a branch", "new branch", "start a branch", "make a branch", "switch to a new branch".

## Prerequisites

- A git repository with at least one commit on the default branch.
- The `gh` CLI installed and authenticated (used to fetch the GitHub username). If `gh` is unavailable or unauthenticated, the skill falls back to asking the user for a prefix.
- On Windows hosts (PowerShell), `gh` and `git` must be on `PATH`. The commands below are POSIX-style; on PowerShell, equivalents like `Select-String` may be needed for `grep`/`sed`/`tr` pipelines — see the Windows notes inline.

## Procedure

### Step 1: Get the Username Prefix

Run the following to retrieve the GitHub username:

```bash
gh api user --jq .login
```

If the command fails (e.g., not authenticated, `gh` not installed), ask the user for their preferred prefix. Do not guess or hardcode a username.

### Step 2: Determine the Branch Description

**If `$ARGUMENTS` is provided**, use it as the description of the work.

**If no arguments are provided**, inspect the working tree for local changes:

```bash
git diff
git diff --cached
git status --short
```

- **Changes exist**: read the diff content to understand what the work is about and generate a description from it.
- **No changes**: ask the user what they are about to work on. Do not proceed without a description.

### Step 3: Classify the Type

Pick the type from the table below based on the description:

| Type      | Use when                                                              |
| --------- | --------------------------------------------------------------------- |
| `feat`    | New user-facing functionality                                         |
| `fix`     | Broken behavior now works                                             |
| `ref`     | Same behavior, different structure                                    |
| `chore`   | Deps, config, version bumps, updating existing tooling — no new logic |
| `perf`    | Same behavior, faster                                                 |
| `style`   | CSS, formatting, visual-only                                          |
| `docs`    | Documentation only                                                    |
| `test`    | Tests only                                                            |
| `ci`      | CI/CD config                                                          |
| `build`   | Build system                                                          |
| `meta`    | Repo metadata changes                                                 |
| `license` | License changes                                                       |

**Tie-breakers (HARD RULES):**

- When unsure: use `feat` for new things (including new scripts, skills, or tools).
- Use `ref` for restructuring existing things.
- Use `chore` **only** when updating or maintaining something that already exists.

### Step 4: Generate and Propose the Branch Name

Build the branch name as:

```
<username>/<type>/<short-description>
```

**Rules for `<short-description>` (HARD RULES):**

- Kebab-case, lowercase.
- 3 to 6 words — concise but clear.
- Describe the change, not file names.
- Only ASCII letters, digits, and hyphens.
- No spaces, dots, colons, tildes, or other git-forbidden characters.

Present the proposed branch name to the user and ask whether they want to:

1. Use it as-is.
2. Modify the description.
3. Change the type.

Do not create the branch until the user confirms.

#### Examples

| Work description                           | Branch name                                 |
| ------------------------------------------ | ------------------------------------------- |
| Dropdown menu not closing on outside click | `priscila/fix/dropdown-not-closing-on-blur` |
| Adding search to conversations page        | `priscila/feat/add-search-to-conversations` |
| Restructuring drawer components            | `priscila/ref/simplify-drawer-components`   |
| Updating test fixtures                     | `priscila/chore/update-test-fixtures`       |
| Bumping @sentry/react to latest version    | `priscila/chore/bump-sentry-react`          |
| Adding a new agent skill                   | `priscila/feat/add-create-branch-skill`     |

### Step 5: Create the Branch

Once the user confirms the branch name, detect the current and default branch:

```bash
git branch --show-current
git remote | grep -qx origin && echo origin || git remote | head -1
git symbolic-ref refs/remotes/<remote>/HEAD 2>/dev/null | sed 's|refs/remotes/<remote>/||' | tr -d '[:space:]'
```

> **Windows / PowerShell note:** `grep`, `sed`, and `tr` are not available in vanilla PowerShell. Replace the `symbolic-ref` pipeline with:
> ```powershell
> $remote = if (git remote | Select-String -Quiet '^origin$') { 'origin' } else { (git remote | Select-Object -First 1) }
> $default = git symbolic-ref "refs/remotes/$remote/HEAD" 2>$null
> if ($default) { $default -replace "refs/remotes/$remote/", "" }
> ```

**Fallback if `symbolic-ref` fails:** Run `git branch --list main master`. Use the one that exists. If both or neither exist, ask the user which branch is the default.

**Detached HEAD handling:** If `git branch --show-current` is empty, show the current commit (`git rev-parse --short HEAD`) and ask whether to branch from it or switch to the default branch first.

**Wrong-branch warning:** If the current branch is not the default branch, warn the user and ask whether to branch from the current branch or switch to the default branch first.

**Switching to the default branch (if requested):**

1. If there are uncommitted changes, offer to stash them: `git stash push -u -m "create-branch: pre-switch stash"`.
2. Run `git checkout <default-branch>`.
3. On any failure, restore stashed changes (`git stash pop`) if applicable and **stop**. Do not leave the user in a broken state.

**Pre-creation check:** Before creating the branch, verify the name doesn't already exist locally or on the remote:

```bash
git show-ref <branch-name>
```

If it returns any match, ask the user to choose a different name. Do not overwrite or force.

**Create the branch:**

```bash
git checkout -b <branch-name>
```

**Restore stashed changes** (if any were stashed in Step 5):

```bash
git stash pop
```

If `git stash pop` conflicts, do not discard the stash — inform the user and leave the stash intact (`git stash list` to confirm).

## Pitfalls

- **Do not guess the username.** Always fetch it via `gh api user --jq .login` or ask the user. Hardcoding a username from examples will produce incorrect branch names.
- **Do not create the branch before user confirmation.** The type and description are proposals, not decisions.
- **Do not use file names in the short description.** Describe the change semantically (e.g., `add-search-to-conversations`, not `update-conversationtsx`).
- **Do not use git-forbidden characters** in the branch name: spaces, dots, colons, tildes, backslashes, or non-ASCII characters.
- **Detached HEAD is not an error.** Handle it explicitly by asking the user; do not silently branch from an unexpected commit.
- **Stash safety.** If `git checkout <default-branch>` fails after stashing, always restore the stash before stopping. Never leave stashed changes behind.
- **Existing branch name.** If `git show-ref` finds the name already exists, do not force-create or delete the existing branch. Ask for a new name.
- **Windows PowerShell.** POSIX utilities (`grep`, `sed`, `tr`, `head`) are not available by default. Use the PowerShell equivalents provided above, or run commands in a Git Bash session if available on the host.

## Verification

After creating the branch, verify the result:

```bash
# Confirm the current branch matches the created name
git branch --show-current

# Confirm the branch exists on the local refs
git show-ref --heads <branch-name>
```

**Expected output:** `git branch --show-current` prints the exact branch name (e.g., `priscila/feat/add-search-to-conversations`). `git show-ref --heads` prints a line like `<sha> refs/heads/<branch-name>`.

If stashed changes were restored, confirm no stash is left behind:

```bash
git stash list
```

**Expected output:** empty (no stashes), unless the user had pre-existing stashes unrelated to this skill.

## References

- [Sentry Branch Naming](https://develop.sentry.dev/sdk/getting-started/standards/code-submission/#branch-naming)

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
