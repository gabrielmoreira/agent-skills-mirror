---
name: git-specialist
description: "Deep Git command-line expertise covering the full spectrum from everyday workflows to advanced power-user techniques. Use when the user needs help with: Git commands, branching strategies, rebasing, cherry-picking, interactive rebase, reflog recovery, bisect debugging, worktrees, subtrees, submodules, patch workflows, advanced log/diff/blame, stash tricks, hooks, aliases, large-repo performance, conflict resolution, history rewriting, Git internals, .gitattributes/.gitignore patterns, sparse checkout, or any Git CLI question. Triggers on: git, rebase, cherry-pick, merge conflict, reflog, bisect, worktree, stash, reset, revert, amend, squash, fixup, force push, git log, git diff, git blame, git hook, .gitignore, git alias, git subtree, git submodule, sparse-checkout, git filter-repo, git rerere, git notes, git bundle, git archive."
---

# Git Specialist

Complete Git CLI mastery -- from daily workflows to deep internals.

## Workflow

1. **Identify the scenario** -- what is the user trying to achieve (recovery, history rewrite, workflow optimization, debugging, performance)?
2. **Choose the safest approach** -- prefer non-destructive commands; warn before any destructive operation (`--force`, `filter-repo`, `reset --hard`)
3. **Explain with concrete examples** -- show exact commands with realistic output
4. **Offer alternatives** -- show both the quick way and the "proper" way when they differ

## Safety Rules

- Always warn before history-rewriting commands on shared branches
- Prefer `--force-with-lease` over `--force`
- Suggest creating a backup branch before destructive operations: `git branch backup/before-rewrite`
- Recommend `git stash` or `git worktree` before risky operations

## Core Topics Quick Reference

| Area | Key Commands | Notes |
|------|-------------|-------|
| **Branching** | `branch`, `switch`, `checkout -b` | Prefer `switch`/`restore` over `checkout` (Git 2.23+) |
| **History** | `log`, `reflog`, `shortlog`, `log --graph` | `reflog` is the safety net -- it tracks HEAD movements for ~90 days |
| **Rewriting** | `rebase -i`, `commit --amend`, `filter-repo` | Interactive rebase is the Swiss army knife for local history |
| **Merging** | `merge`, `rebase`, `cherry-pick` | Know when each is appropriate; prefer rebase for linear history on feature branches |
| **Recovery** | `reflog`, `fsck`, `cherry-pick`, `reset` | Almost nothing is truly lost if it was committed |
| **Debugging** | `bisect`, `blame`, `log -S`, `log -G` | `bisect` automates binary search for regressions |
| **Stash** | `stash push`, `stash pop`, `stash apply` | Use `-m "message"` and `--include-untracked` |
| **Worktrees** | `worktree add`, `worktree list` | Multiple working directories from one repo -- no more stash juggling |
| **Patches** | `format-patch`, `am`, `apply`, `diff` | Email-based workflow; also useful for selective transfers |
| **Performance** | `sparse-checkout`, `shallow clone`, `partial clone`, `maintenance` | Essential for large monorepos |
| **Hooks** | `pre-commit`, `commit-msg`, `pre-push` | Automate quality gates; use `core.hooksPath` for shared hooks |
| **Config** | `config`, `alias`, `.gitattributes` | Three scopes: `--system`, `--global`, `--local` |
| **Subprojects** | `submodule`, `subtree` | Subtree is simpler; submodule gives exact version pinning |
| **Internals** | `cat-file`, `rev-parse`, `ls-tree`, `hash-object` | Understand the object model: blob, tree, commit, tag |

## Power-User Tricks

### History Navigation & Search

```bash
# Find which commit introduced/removed a string (pickaxe)
git log -S "functionName" --oneline
git log -G "regex_pattern" --oneline

# Show commits that touched a specific function (requires language support)
git log -L :functionName:path/to/file.cs

# Compact graph view with author and relative date
git log --graph --oneline --decorate --all --date=relative --format="%C(yellow)%h%Creset %C(cyan)%ad%Creset %s %C(green)(%an)%Creset"

# Find all commits by a coauthor
git log --all --grep="Co-authored-by:.*Name"

# Commits on branch-a but not on main
git log main..branch-a --oneline

# Find the merge commit that brought a commit into main
git log --ancestry-path --merges <commit>..main | tail -1
```

### Interactive Rebase Mastery

```bash
# Rebase last N commits interactively
git rebase -i HEAD~5

# Autosquash: combine fixup commits automatically
git commit --fixup=<target-sha>
git rebase -i --autosquash main

# Reword the root commit
git rebase -i --root

# Rebase onto a different base (transplant a branch)
git rebase --onto new-base old-base feature-branch

# Abort a rebase safely
git rebase --abort
```

### Recovery & Undo

```bash
# Undo last commit, keep changes staged
git reset --soft HEAD~1

# Undo last commit, keep changes unstaged
git reset --mixed HEAD~1

# Recover a dropped stash
git fsck --unreachable | grep commit | cut -d' ' -f3 | xargs git show --stat

# Recover deleted branch
git reflog | grep "branch-name"
git checkout -b branch-name <sha-from-reflog>

# Undo a rebase (find pre-rebase HEAD in reflog)
git reflog
git reset --hard HEAD@{n}

# Revert a merge commit (undo merge without rewriting history)
git revert -m 1 <merge-commit-sha>

# Restore a single file from another commit
git restore --source=<commit> -- path/to/file
```

### Stash Power Moves

```bash
# Stash only specific files (interactive)
git stash push -p -m "partial stash"

# Stash including untracked files
git stash push --include-untracked -m "with untracked"

# Apply stash to a new branch
git stash branch new-branch-name stash@{0}

# Show stash diff without applying
git stash show -p stash@{0}

# Drop all stashes
git stash clear
```

### Worktree Workflow

```bash
# Add a worktree for parallel work (no stash needed)
git worktree add ../hotfix-branch hotfix/issue-123

# List all worktrees
git worktree list

# Remove a worktree after merging
git worktree remove ../hotfix-branch

# Bare repo + worktrees pattern (useful for multiple long-lived branches)
git clone --bare repo.git .bare
echo "gitdir: ./.bare" > .git
git worktree add main
git worktree add develop
```

### Bisect (Automated Bug Hunting)

```bash
# Manual bisect
git bisect start
git bisect bad               # current commit is broken
git bisect good v1.0.0       # this tag was working
# Git checks out a middle commit -- test it, then:
git bisect good  # or  git bisect bad
# Repeat until the culprit is found

# Fully automated bisect with a test script
git bisect start HEAD v1.0.0
git bisect run dotnet test --filter "TestName"

# Bisect with a custom script
git bisect run bash -c 'grep -q "expected" output.txt'

# Reset after bisect
git bisect reset
```

### Advanced Diff & Blame

```bash
# Word-level diff (great for prose/docs)
git diff --word-diff

# Diff between branches, only file names
git diff main..feature --name-only

# Diff of staged changes only
git diff --cached

# Ignore whitespace in diff
git diff -w

# Blame with line range
git blame -L 10,20 path/to/file

# Blame ignoring whitespace and move detection
git blame -w -M -C path/to/file

# Blame ignoring specific revisions (e.g., formatting commits)
echo "<formatting-sha>" > .git-blame-ignore-revs
git config blame.ignoreRevsFile .git-blame-ignore-revs
git blame path/to/file
```

### Aliases (Productivity Boosters)

```bash
# Set up useful aliases
git config --global alias.st "status -sb"
git config --global alias.co "checkout"
git config --global alias.sw "switch"
git config --global alias.last "log -1 --stat"
git config --global alias.unstage "restore --staged"
git config --global alias.graph "log --graph --oneline --decorate --all"
git config --global alias.amend "commit --amend --no-edit"
git config --global alias.undo "reset --soft HEAD~1"
git config --global alias.wip "!git add -A && git commit -m 'WIP [skip ci]'"
git config --global alias.unwip "reset --soft HEAD~1"
git config --global alias.cleanup "!git branch --merged main | grep -v main | xargs -r git branch -d"
git config --global alias.fresh "!git fetch --prune && git rebase origin/main"
git config --global alias.who "shortlog -sne"
git config --global alias.find "log --all -S"
```

### Large Repo Performance

```bash
# Sparse checkout (only check out what you need)
git sparse-checkout init --cone
git sparse-checkout set src/my-service tests/my-service

# Partial clone (skip blobs until needed)
git clone --filter=blob:none <url>

# Shallow clone (limited history)
git clone --depth=1 <url>
git fetch --deepen=10    # get more history later

# Enable filesystem monitor for large repos
git config core.fsmonitor true
git config core.untrackedcache true

# Run background maintenance
git maintenance start

# Commit graph for faster log/merge-base
git commit-graph write --reachable
```

### Patches & Selective Transfer

```bash
# Create patch files from commits
git format-patch main..feature -o patches/

# Apply patches
git am patches/*.patch

# Apply a diff as patch (without commit metadata)
git diff main..feature -- src/ | git apply

# Create a bundle (portable repo snapshot)
git bundle create repo.bundle --all
git clone repo.bundle restored-repo

# Archive a specific ref
git archive --format=zip -o release.zip HEAD src/
```

### Hooks & Automation

```bash
# Share hooks via core.hooksPath (team-wide)
git config core.hooksPath .githooks

# Pre-commit: lint staged files only
# .githooks/pre-commit
#!/bin/sh
git diff --cached --name-only --diff-filter=d | grep '\.cs$' | xargs dotnet format --include

# Commit-msg: enforce conventional commits
# .githooks/commit-msg
#!/bin/sh
if ! grep -qE "^(feat|fix|build|chore|docs|style|refactor|test)\(.+\): .+" "$1"; then
  echo "Commit message must follow: type(scope): description"
  exit 1
fi
```

### Rerere (Reuse Recorded Resolution)

```bash
# Enable rerere globally (remember conflict resolutions)
git config --global rerere.enabled true

# After resolving a conflict, Git remembers the resolution
# Next time the same conflict occurs, it's resolved automatically

# Review recorded resolutions
git rerere status
git rerere diff
```

## Anti-Patterns

| Anti-Pattern | Do Instead |
|-------------|------------|
| `git push --force` on shared branches | `git push --force-with-lease` or `git revert` |
| `git add .` blindly | `git add -p` or review with `git diff` first |
| Giant monolithic commits | Small, atomic commits with clear messages |
| Merging main into feature branch repeatedly | Rebase feature branch onto main |
| Deleting branches without checking merge status | `git branch -d` (safe) not `-D` (force) |
| Using `git checkout` for everything | `git switch` (branches) + `git restore` (files) |
| Storing secrets in Git history | Use `.gitignore`, `git-crypt`, or environment variables |
| `git reset --hard` without backup | Create a backup branch first, or use `reflog` |
| Ignoring `.gitattributes` | Set `text=auto`, define merge drivers for lock files |
| Manual conflict resolution every time | Enable `rerere` for repeated resolutions |

## Troubleshooting Checklist

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| "detached HEAD" | Checked out a commit/tag directly | `git switch -` or `git switch branch-name` |
| Merge conflicts on every rebase | Diverged significantly from base | Rebase in smaller steps or use `rerere` |
| "refusing to merge unrelated histories" | Repos with no common ancestor | `--allow-unrelated-histories` if intentional |
| Push rejected (non-fast-forward) | Remote has commits you don't have | `git pull --rebase` then push |
| `.gitignore` not working | File already tracked | `git rm --cached <file>` then commit |
| Huge repo, slow operations | Too many files/large blobs | `sparse-checkout`, `partial clone`, `git-lfs` |
| Lost commits after rebase | History rewritten | `git reflog` to find pre-rebase SHA |
| Wrong author on commits | Misconfigured user | `git commit --amend --author="Name <email>"` or `rebase -i` with `exec` |
| Binary files causing merge conflicts | No merge driver defined | Set binary merge strategy in `.gitattributes` |
| Submodule not updating | Submodule pointer stale | `git submodule update --init --recursive` |

## Advanced Reference

For in-depth coverage of specific topics, load [references/advanced-topics.md](references/advanced-topics.md). Topics include:

- Git internals (object model, packfiles, refs)
- `git filter-repo` for history surgery
- Signing commits and tags with GPG/SSH
- Git LFS setup and migration
- Monorepo strategies (sparse-checkout, worktrees, CODEOWNERS)
- Advanced merge strategies and custom merge drivers
- Git notes for metadata without changing history
- Shallow clone workflows for CI/CD
- Multi-remote workflows (fork + upstream)
