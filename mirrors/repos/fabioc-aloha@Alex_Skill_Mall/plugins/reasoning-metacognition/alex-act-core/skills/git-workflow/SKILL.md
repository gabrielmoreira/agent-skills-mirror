---
name: git-workflow
description: Apply consistent git practices for branch hygiene, safe commits, and recovery from common mishaps (lost commits, bad merges, accidental pushes). Use when authoring or reviewing a git workflow, recovering broken local state, or sequencing a commit/push that needs explicit user approval before destructive steps.
lastReviewed: 2026-05-31
---

# Git Workflow Skill

> Consistent git practices, recovery patterns, and safe operations.

## ⚠️ Staleness Warning

Git core is stable, but GitHub features (Actions, CLI, Copilot integration) evolve.

**Refresh triggers:**

- GitHub CLI major updates
- GitHub Actions runner changes
- New git features (e.g., `git switch`, `git restore`)
- GitHub Copilot CLI integration

**Last validated:** May 2026 (Git 2.45+, GitHub CLI 2.x)

**Check current state:** [Git Release Notes](https://git-scm.com/docs/git/RelNotes), [GitHub CLI](https://cli.github.com/)

---

## Decision Table

| Scenario | Command | Notes |
|----------|---------|-------|
| Undo last commit, keep changes | `git reset --soft HEAD~1` | Safe, preserves work |
| Restore single file | `git checkout HEAD -- path/to/file` | Discards file changes |
| Restore entire folder | `git checkout HEAD -- .github/` | Discards folder changes |
| Before risky operation | `git add -A; git commit -m "checkpoint"` | Always checkpoint first |
| Discard all uncommitted | `git reset --hard HEAD` | Destructive, no recovery |
| Reset to remote state | `git reset --hard origin/main` | Destructive, syncs to remote |
| Save work temporarily | `git stash` → `git stash pop` | For quick context switch |
| Isolated experimental work | `git worktree add ../feature branch` | Agent-friendly isolation |

---

## Commit Message Convention

```text
type(scope): brief description

- Detail 1
- Detail 2
```

**Types**: `feat`, `fix`, `refactor`, `docs`, `chore`, `test`, `style`

**Examples**:

```text
feat(skills): add git-workflow skill
fix(sync): resolve race condition in background sync
refactor(skills): migrate domain-knowledge to skills architecture
docs(readme): update installation instructions
chore(deps): bump typescript to 5.3
```

## Before Risky Operations

```bash
# ALWAYS commit before risky operations
git add -A; git commit -m "checkpoint: before [risky thing]"

# For extra safety, tag it
git tag "safe-point-$(date +%Y-%m-%d-%H%M)"
```

Three rules that hold regardless of the operation:

1. **Never force-push to a shared branch** (`main`, `develop`, any branch someone else tracks). Rewriting history under a collaborator is not recoverable by them.
2. **Commit or tag before rebase, reset, or filter operations.** A checkpoint you did not need costs nothing; one you needed and skipped costs the work.
3. **Run `--dry-run` first when unsure.** `git clean`, `git push`, and `git rm` all support it. Read the output before dropping the flag.

## Tag-Move-Forward (Pre-Push Only)

When a small follow-on change lands after a release tag but **before the tag is pushed**, move the tag forward rather than cutting a redundant patch release. Two requirements: (1) the tag must not yet exist on `origin`, (2) the follow-on belongs in the same release narrative (typo, doc fix, orphan removal — not new behaviour).

```bash
# Verify tag is local-only first
git ls-remote --tags origin v3.2.1   # must return empty

# Force-move the annotated tag to the new HEAD
git tag -d v3.2.1
git tag -a v3.2.1 -m "release notes..."
git log -4 --oneline                 # confirm tag now on HEAD

# Push main + tag together
git push origin main
git push origin v3.2.1
```

**Never** force-move a pushed tag. Once `git push origin v<x>` succeeded, the only safe move is a new patch (`v<x>+1`). Heir clones may already have fetched the old SHA; rewriting under them breaks reproducibility and CI provenance.

## Recovery Patterns

### Undo Last Commit (keep changes)

```bash
git reset --soft HEAD~1
```

### Restore Single File

```bash
git checkout HEAD -- path/to/file
```

### Restore Folder

```bash
git checkout HEAD -- .github/
```

### Hard Reset to Known Good State

```bash
git reset --hard HEAD           # Discard all uncommitted changes
git reset --hard origin/main    # Reset to remote state
git reset --hard <tag-name>     # Reset to tagged state
```

### Find Last Good Commit

```bash
git log --oneline -20           # Recent history
git log --oneline .github/ -10  # History for specific folder
```

### Recover an Unreachable Commit

`git log` only walks commits reachable from a ref. A commit orphaned by `reset --hard`, a bad rebase, or a deleted branch is invisible to it. `reflog` records where `HEAD` has actually been:

```bash
git reflog                      # Every HEAD position, newest first
git reflog show <branch>        # Movements of one branch
git reset --hard <sha-from-reflog>   # Return to that state
git cherry-pick <sha-from-reflog>    # Or lift just that commit
```

Reflog is local-only and expires (90 days by default for reachable entries, 30 for unreachable). It cannot recover work that was never committed.

### Undo a Pushed Commit

```bash
git revert <sha>    # New commit that inverts the change; safe on shared branches
```

Prefer `revert` over `reset` once a commit is on `origin` — see the force-push rule above.

## Branching Strategy

```text
main
 └── feature/short-description
 └── fix/issue-number
 └── release/v3.7.0
```

**Rules**:

- `main` is always deployable
- Feature branches for experimental work
- Merge via PR when possible, direct commit for small fixes
- Delete branches after merge

## Conflict Resolution

1. **Pull before push**: `git pull --rebase origin main`
2. **If conflicts**: Resolve in editor, then `git add .` + `git rebase --continue`
3. **If stuck**: `git rebase --abort` to start over

## Stashing

```bash
git stash                       # Save work-in-progress
git stash pop                   # Restore and delete stash
git stash list                  # See all stashes
git stash drop                  # Delete top stash
```

## Worktrees (Agent Isolation)

VS Code background agents use `git worktree` to isolate changes. Understanding worktrees is useful when debugging agent sessions.

```bash
# Create a worktree for isolated work
git worktree add ../project-feature feature-branch

# List all worktrees
git worktree list

# Remove a worktree (prune stale links)
git worktree remove ../project-feature
git worktree prune
```

**VS Code integration** (1.109+):

- `git.worktreeIncludeFiles` — copy gitignored files (e.g., `.env`) into agent worktrees
- Background agents auto-commit at end of each turn within their worktree
- Check Agent Sessions view to see which worktree an agent is using

## Anti-Patterns

- ❌ `git push --force` on shared branches
- ❌ Committing secrets or credentials
- ❌ Giant commits with unrelated changes
- ❌ Vague messages like "fix stuff" or "update"

## Would Revise If

Revise if the recovery patterns produce data loss in a real recovery scenario, or if the 'safe operations' classification labels a destructive op as safe and that op runs without confirmation.
