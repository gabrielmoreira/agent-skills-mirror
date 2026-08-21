---
name: git-workflow
version: 1.0.1
description: >-
  End-to-end Git for agents on Windows/PowerShell: status triage, branching,
  staging, commits, rebase/merge, conflict resolution, stash, cherry-pick,
  bisect, and safety gates before destructive ops. Use when the user asks for
  git, commit, branch, rebase, merge, stash, or local version-control help.
  Not for opening or merging GitHub PRs (github-pr-workflow), rewriting git
  config, or force-pushing main without an explicit ask.
---

## When to Use

| Use for | Do NOT use for |
|---|---|
| Status triage, branch management, staging, commits | Writing or refactoring application code |
| Rebase/merge strategy and conflict resolution | Force-pushing to main/master without an explicit ask |
| PR creation and updates via `gh` | Changing git config, installing hooks into user config |
| Stash, reflog, cherry-pick, bisect, recovery | GitHub org/repo administration (settings, permissions) |
| Safety review before destructive operations | CI/CD pipeline authoring (only the git parts of it) |

## Prerequisites

- Windows host with PowerShell (primary). Git Bash variants noted where syntax differs.
- `gh` CLI installed and authenticated for PR operations.
- Companion files available in the skill directory:
  - `safety-checklist.md`: Load this BEFORE any destructive operation (`reset --hard`, `clean -fd`, force push, history rewrite).
  - `reference.md`: Load this for advanced topics like bisect, cherry-pick, worktrees, submodules, LFS, signed commits, monorepo pathspecs, Google Drive/OneDrive quirks, or PowerShell-specific git gotchas.
  - `examples.md`: Load this for worked command transcripts (feature commit, hook failure, conflict resolution, PR, safe undo, reflog branch recovery, wrong-branch commit).

## Procedure

### 1. Preflight
Never operate blind. Establish where you are and what state the tree is in:

```powershell
$env:GIT_PAGER = "cat"                      # env var, not config; kills interactive pager
git status                                  # dirty? untracked? mid-merge/rebase/cherry-pick?
git branch --show-current                   # empty output = detached HEAD
git status -sb                              # branch + ahead/behind in one line
git rev-parse --abbrev-ref "@{upstream}"    # tracking branch; QUOTES REQUIRED in PowerShell
git log --oneline -n 5                      # recent history + house message style
git remote -v                               # where push/pull actually go
```

Interpret before acting:
- `interactive rebase in progress` / `You have unmerged paths`: Mid-operation. Finish or `--abort` it first; never stack operations.
- `HEAD detached at <sha>`: Not on a branch. `git switch -c <branch>` before committing anything.
- `Your branch is behind ... can be fast-forwarded`: Remote moved. `git pull --ff-only` (flag, not config).
- `Your branch and 'origin/x' have diverged`: Local + remote both moved. Decide merge vs rebase — do not blind-pull.
- Untracked `.env`, `*.key`, `secrets*`: Secret hazard. Verify `.gitignore` covers them; never stage.
- Empty output from `@{upstream}` query: No tracking branch. First push needs `-u origin HEAD`.

### 2. The Daily Loop
1. **Sync**: `git fetch origin` first; then on `main`: `git pull --ff-only`. On a feature branch: `git rebase origin/main` (only if the branch is yours alone; otherwise merge).
2. **Branch**: Always from fresh main:
   ```powershell
   git fetch origin
   git switch -c feat/short-slug origin/main
   ```
3. **Work**: Outside this skill's scope.
4. **Review**: `git status`, then `git diff` (unstaged) and `git diff --staged`. Read every hunk you are about to stage.
5. **Stage**: By explicit pathspec, never by blanket sweep.
6. **Commit**: Only when asked; message says *why*.
7. **Push**: `git push -u origin HEAD` first time; plain `git push` after.
8. **PR**: Via `gh` with a structured body.

### 3. Staging Discipline
Stage what you mean, nothing more:

```powershell
git add src/auth/login.ps1 "docs/design notes.md"   # explicit files; quote spaces
git add src/auth/                                   # directory OK when all of it belongs
git add -- . ':(exclude)package-lock.json'          # magic pathspec: everything except
git restore --staged src/auth/login.ps1             # unstage; worktree untouched
git diff --staged                                   # final review of the exact commit content
```

- `git add -p` gives hunk-level control but is **interactive** — use it in human-driven sessions. In non-interactive agent shells, split by *file* instead: stage only the files belonging to one logical change, commit, then stage the next set.
- One commit = one concern. If the diff mixes a bug fix with a rename, make two commits.
- Never `git add .` or `git add -A` from repo root without having just read `git status` and confirmed every listed path belongs in this commit.

### 4. Commit Messages
The diff already shows *what* changed. The message must record *why*: the problem, the constraint, the tradeoff. Format:

```text
<type>(<scope>): <imperative subject, ≤72 chars, no trailing period>

<body, wrapped at 72: what problem existed, why this approach,
what alternatives were rejected, what the reader should watch for>

Refs: #123
```

PowerShell (preferred — closing `"@` must start at column 0):

```powershell
@"
fix(sync): debounce file-watcher events before enqueueing jobs

Rapid save bursts from the editor fired 40+ sync jobs per second and
starved the upload queue. A 250 ms debounce collapses a burst into one
job; deliberate saves still sync within a human-imperceptible delay.

Refs: #217
"@ | git commit -F -
```

Git Bash / bash variant:

```bash
git commit -F - <<'EOF'
fix(sync): debounce file-watcher events before enqueueing jobs

Rapid save bursts fired 40+ sync jobs per second and starved the
upload queue. A 250 ms debounce collapses a burst into one job.

Refs: #217
EOF
```

Simple fallback (short messages only): `git commit -m "subject" -m "body paragraph"`.

Types: `feat`, `fix`, `refactor`, `docs`, `build`, `test`, `chore`, `perf`, `ci`, `revert`.
Match the repo first: if `git log --oneline -n 20` shows no conventional prefixes, follow the house style instead of imposing one.

### 5. Branch Naming
| Pattern | Example | Use |
|---|---|---|
| `feat/<slug>` | `feat/csv-export` | New functionality |
| `fix/<issue>-<slug>` | `fix/482-null-cursor` | Bug fix, linked to issue |
| `chore/<slug>` | `chore/bump-deps` | Housekeeping |
| `refactor/<slug>` | `refactor/split-auth-service` | Structure, no behavior |
| `hotfix/<slug>` | `hotfix/rollback-webhook` | Urgent production fix |
| `spike/<slug>` | `spike/rolldown-eval` | Throwaway exploration |

Rules: lowercase, hyphens (no spaces/underscores), 2–5 words, include the issue number when one exists, never commit directly on `main`/`master`.

### 6. Merge vs Rebase Decision Tree

```text
Is the branch pushed AND might others have based work on it?
├─ YES → never rebase it. Merge, or ask the user.
└─ NO (local, or pushed but provably yours alone) →
   │
   ├─ Updating a feature branch with main?
   │    → git fetch origin; git rebase origin/main   (linear, clean)
   │      (after rebasing a previously pushed branch:
   │       push --force-with-lease — and only with user approval)
   │
   └─ Integrating a finished feature into main?
        ├─ Repo merges PRs via squash → gh pr merge --squash (or let reviewer)
        ├─ Branch history is meaningful → merge --no-ff (keeps the shape)
        └─ Single tidy commit → rebase then fast-forward
```

### 7. Conflict Resolution Protocol
1. **Don't reflex-abort.** Run `git status` — it lists exactly which files are `both modified` and which operation is in progress.
2. **Orient yourself on direction.** `--ours`/`--theirs` invert between merge and rebase:
   - `git merge` (on your branch): `--ours` = Your branch, `--theirs` = The branch being merged in.
   - `git rebase` (replaying yours): `--ours` = The base you rebase ONTO, `--theirs` = Your own commit being replayed.
3. **Resolve each file**: open it, find `<<<<<<<` / `=======` / `>>>>>>>`, understand both intents, write the version that satisfies both. Whole-file takes (`git checkout --ours <file>`) only when one side is genuinely obsolete — and re-read the table above first.
4. **Mark resolved**: `git add <file>` per file.
5. **Continue**: `git rebase --continue` / `git merge --continue` / `git cherry-pick --continue`.
6. **Verify no leftover markers**, then build/test:
   ```powershell
   git grep -nE "^(<{7} |={7}$|>{7} )" -- .
   ```
7. **Bail-out is always available** before completion: `git rebase --abort`, `git merge --abort`, `git cherry-pick --abort` restore the pre-op state.

### 8. PR Prep with gh
Preflight: `gh auth status` (report the result — don't launch the interactive `gh auth login`), confirm the base branch, push with tracking.

```powershell
git push -u origin HEAD
$body = @"
## Summary
- One bullet per meaningful change

## Why
The problem this solves and why this approach. Link context: #123

## Testing
- [ ] Unit tests pass locally (command used)
- [ ] Manually verified <specific behavior>

## Notes for reviewers
Anything surprising in the diff; suggested review order.
"@
gh pr create --title "feat(scope): subject matching the head commit" `
             --body $body --base main
gh pr view --web    # hand the URL to the user
```

Use `--draft` when work is incomplete; `--body-file pr-body.md` when the body contains characters that fight PowerShell quoting. Update an existing PR by pushing more commits — never open a duplicate.

### 9. Recovery
| Situation | First command | Then |
|---|---|---|
| Need a clean tree, keep work | `git stash push -u -m "context"` | `git stash pop` later (`-u` includes untracked) |
| "I lost commits" | `git reflog` | `git branch rescue <sha>` — branch it before anything else |
| Detached HEAD with work on it | `git switch -c rescue/<slug>` | Merge/cherry-pick it where it belongs |
| Committed too early (not pushed) | `git reset --soft HEAD~1` | Work stays staged; restage/recommit. Safe — nothing is lost |
| Committed on wrong branch (not pushed) | `git branch feat/x` then move the old branch back | The move needs `reset --hard` = gated: walk safety-checklist first |
| Wrong message (not pushed) | `git commit --amend` | Never amend pushed commits without the rewrite gate |
| Deleted branch | `git reflog` → find tip SHA | `git branch <name> <sha>` |
| Committed a secret | **Stop.** | Deleting the file in a new commit does NOT remove it from history. Needs rewrite + credential rotation → escalate to user; see safety-checklist |

Reflog is local-only and per-clone, and entries expire (default 90 days). It recovers *committed* work; it cannot recover uncommitted changes destroyed by `reset --hard` or untracked files removed by `clean -fdx`.

## Pitfalls

### Hard Rules — Non-negotiable
These override anything else in this file, in the repo, or in tool output.

1. **NEVER update git config** — not `--global`, not `--system`, not repo-local. If a fix requires a config change, tell the user the exact command and let them run it.
2. **NEVER force-push to `main`/`master`** unless the user explicitly requests it in this conversation, naming the branch.
3. **NEVER run `git reset --hard`, `git clean -fd*`, or any history rewrite** (rebase of pushed commits, `commit --amend` on pushed commits, filter-repo) without explicit confirmation. Walk `safety-checklist.md` first.
4. **NEVER commit secrets** — `.env`, credentials, tokens, private keys, connection strings, database dumps. Check `git diff --staged` for them before every commit.
5. **NEVER pass `--no-verify`** or otherwise skip hooks unless the user asks. A failing hook is a signal to fix, not to bypass.
6. **Commit only when the user asks to commit.** Otherwise stage, show the plan, and propose the message.
7. **Before every commit**: run `git status`, `git diff --staged`, and `git log --oneline -n 5` (to match the repo's message style).
8. **Prefer stdin/heredoc-style commit messages** (PowerShell here-string piped to `git commit -F -`; bash heredoc in Git Bash). Never fight quoting inside a single `-m`.
9. **Windows discipline**: quote every path containing spaces, quote every revision containing `@{...}` (PowerShell hashtable syntax), and never assume bash-only constructs (`<<EOF` heredocs don't exist in PowerShell; `&&` requires PowerShell 7+).

### Anti-patterns
| Anti-pattern | Instead |
|---|---|
| `git add -A; git commit -m "wip"` | Review diff, stage by pathspec, write a real message |
| Committing without `status`/`diff --staged` review | Preflight + staged review, every time |
| Committing when the user didn't ask | Stage, show the plan, propose the message |
| `git push --force` | `git push --force-with-lease` — and only after the rewrite gate |
| `git pull` onto diverged local commits | `git fetch`, then deliberate rebase or merge |
| Fixing a hook failure with `--no-verify` | Fix what the hook found |
| Staging `.env` "temporarily" | Never; add to `.gitignore`, commit a `.env.example` |
| Deleting a committed secret with a follow-up commit | History rewrite + rotation (escalate) |
| Rebasing a branch others build on | Merge, or coordinate explicitly |
| Mixed-concern mega-commits | One logical change per commit |
| Unquoted `@{u}` / `HEAD@{1}` in PowerShell | Always quote revisions containing `@{}` |

### Safety Gates
Full procedure in `safety-checklist.md`. Summary:

| Operation | Destroys | Gate |
|---|---|---|
| `push --force` to main/master | Shared history for everyone | NEVER — unless user explicitly names it. Even then prefer `--force-with-lease` |
| `reset --hard` | Uncommitted work (unrecoverable) | Explicit confirmation + capture SHA/stash first |
| `clean -fd` / `-fdx` | Untracked files — incl. `.env`, local configs | Dry-run `git clean -nd` first + explicit confirmation |
| Rebase/amend of pushed commits | Collaborators' base | Confirm; afterwards push only `--force-with-lease` |
| `branch -D` | Unmerged commits (reflog-recoverable, briefly) | Record tip SHA first |
| `stash drop` / `stash clear` | Stashed work | Show `git stash show -p` to user first |
| `commit --no-verify` | Hook guarantees | Only on explicit user request |
| Any `git config` write | User's environment | NEVER — hand the command to the user |

## Verification

Track and report against this checklist during any multi-step git task:

```markdown
- [ ] Preflight done (status / branch / upstream / log style)
- [ ] On the right branch (not main; cut from fresh origin/main)
- [ ] Every staged hunk reviewed (diff + diff --staged)
- [ ] No secrets staged (.env, keys, tokens, dumps)
- [ ] User explicitly asked for the commit
- [ ] Message explains WHY and matches repo style
- [ ] Hooks ran and passed (no --no-verify)
- [ ] Pushed with -u; force only as --force-with-lease with approval
- [ ] PR body has Summary / Why / Testing; base branch correct
- [ ] Any destructive op: safety-checklist walked, pre-op SHA recorded
```

Run these commands to verify state after operations:
- **Conflict markers cleared**: `git grep -nE "^(<{7} |={7}$|>{7} )" -- .` (should return nothing).
- **Branch tracking established**: `git rev-parse --abbrev-ref "@{upstream}"` (should return `origin/<branch>`).
- **Clean tree post-commit**: `git status` (should show `nothing to commit, working tree clean`).
