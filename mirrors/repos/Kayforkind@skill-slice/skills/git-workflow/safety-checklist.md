# Safety Checklist — Irreversible Operations Gate

Mandatory procedure before any destructive Git operation. Companion to
[SKILL.md](SKILL.md); scenarios 3, 5, and 7 in [examples.md](examples.md)
show the gate in action.

**The gate in one line:** classify → capture → confirm → execute narrowly →
verify → report the recovery anchor.

## Step 0 — Classify the operation

| Tier | Operations | Gate required |
|---|---|---|
| 🟢 Safe | `status`, `log`, `diff`, `fetch`, `switch`, `branch` (create), `stash push`, `add`, `restore --staged`, `reset --soft` (unpushed), `commit`, `push` (non-force), `merge --abort`, `rebase --abort` | None — these lose nothing |
| 🟡 Capture-first | `rebase` (unpushed/solo branch), `commit --amend` (unpushed), `branch -D`, `stash pop` onto dirty tree, `cherry-pick` chains | Record recovery anchor (Step 1); no user confirmation needed if the user requested the operation |
| 🔴 Confirm + capture | `reset --hard`, `clean -f*`, `push --force*`, rebase/amend of **pushed** commits, `stash drop`/`clear`, `filter-repo`/history rewrite, deleting remote branches | Steps 1–3 in full — explicit, current, verbatim user confirmation |
| ⛔ Forbidden | `git config` writes (any scope), force-push to `main`/`master` without the user naming it, `--no-verify` unasked, committing secrets | Do not perform. Hand the user the command, or refuse with the reason |

Two questions decide the tier when in doubt:

1. **Does it discard worktree/untracked state?** Uncommitted changes have no
   reflog — loss is permanent. That alone makes it 🔴.
2. **Does it rewrite history others may have?** Anything already pushed to a
   shared branch is 🔴 regardless of how small the rewrite is.

## Step 1 — Pre-op capture (🟡 and 🔴)

Record enough state to undo the undo. Paste the anchor SHA into your
response *before* executing:

```powershell
git status                                   # full picture, including untracked
git rev-parse HEAD                           # ← the recovery anchor. Report it.
git branch "backup/pre-op-$(Get-Date -Format yyyyMMdd-HHmm)"   # cheap ref insurance
git stash push -u -m "pre-op safety stash"   # ONLY if the dirty tree must survive the op
git stash show -p "stash@{0}"                # prove the stash captured what you think
```

Operation-specific captures:

| About to run | Also capture |
|---|---|
| `reset --hard` | `git diff > pre-reset.patch` if any uncommitted changes exist (they are otherwise gone forever) |
| `clean -f*` | `git clean -nd` (dry run) — paste the file list into the confirmation |
| `branch -D <b>` | `git rev-parse <b>` — the tip SHA is the whole recovery plan |
| `push --force-with-lease` | `git rev-parse origin/<branch>` — what the remote pointed to |
| `stash drop`/`clear` | `git stash show -p` output shown to the user first |
| History rewrite | Full backup branch **and** confirm every collaborator is aware |

## Step 2 — Confirmation protocol (🔴 only)

Consent must be **explicit, current, and specific**:

- The user named this operation in *this* conversation. "Clean this up" is
  **not** consent for `reset --hard`. "Yes" to a different question earlier
  is not consent for this one.
- Echo back exactly what will be destroyed, then stop and wait:

```text
NEEDS_CONFIRMATION: git reset --hard origin/main on branch 'main'
Will permanently discard:
  - 2 local commits (71acd02, 4f0b9ee) — preserved on feat/weekly-digest
  - Uncommitted changes to src/report/Digest.cs (NOT recoverable via reflog)
Recovery anchor: 71acd02 (backup branch: backup/pre-op-20260715-1430)
Proceed? (yes / no)
```

- Anything ambiguous in the reply ("I guess", "if you think so") → ask again,
  binary. Silence is a no.
- Force-push target check happens **now**, not at execution:
  `main`/`master` → forbidden unless the user explicitly named that branch
  for force-push; feature branches → `--force-with-lease` only, never bare
  `--force`.

## Step 3 — Execute narrowly

- Run **only** the confirmed command — no batching extra "while I'm here"
  operations behind one confirmation.
- Prefer the surgical variant:

| Instead of | Prefer |
|---|---|
| `git push --force` | `git push --force-with-lease` (fails if remote moved under you) |
| `git reset --hard` to unstage | `git restore --staged <path>` then `git restore <path>` per file |
| `git clean -fdx` | `git clean -fd <specific-path>` after a `-nd` dry run (`-x` also deletes ignored files: `.env`, local settings) |
| `git stash clear` | `git stash drop "stash@{n}"` one entry at a time |
| Deleting a remote branch | Confirm no open PR depends on it: `gh pr list --head <branch>` |

- If the command errors midway, **stop** — do not improvise a second
  destructive command to "finish the job". Reassess from `git status`.

## Step 4 — Post-op verification

```powershell
git status                        # expected end state? nothing extra touched?
git log --oneline -n 5            # history shape matches the plan
git stash list                    # safety stash still present (if made)
git branch --list "backup/*"      # backup ref intact
```

Report to the user: what ran, what the tree looks like now, the recovery
anchor SHA, and how long recovery stays possible (reflog defaults: ~90 days
reachable / ~30 unreachable; **zero** for discarded uncommitted work — if
`pre-reset.patch` was captured, say where it is).

## What recovery can and cannot do

| Lost via | Recoverable? | How |
|---|---|---|
| `reset --hard` (committed work) | ✅ | `git reflog` → `git branch rescue <sha>` |
| `branch -D` | ✅ | Tip SHA from Step 1, or `git reflog` |
| Botched rebase/amend | ✅ | `git reflog` — pre-rebase HEAD is right there |
| `stash drop` | ⚠️ maybe | `git fsck --unreachable \| Select-String commit`, inspect with `git show` |
| `reset --hard` (uncommitted changes) | ❌ | Only the Step-1 patch file, if captured |
| `clean -fdx` (untracked files) | ❌ | Nothing in git ever referenced them |
| Force-push over a colleague's commits | ⚠️ | Their clone still has the commits; coordinate immediately — do not force again |

## Special case — a secret was committed

1. **Stop pushing.** If unpushed, the blast radius is local.
2. A follow-up commit deleting the file does **not** help — the secret
   remains in every prior commit and pack file.
3. Unpushed: interactive rebase / soft-reset the offending commit away
   (🔴 gate applies), verify with
   `git log --all --oneline -- <path>` and `git grep <secret-fragment> $(git rev-list --all)`.
4. Pushed: escalate to the user immediately — the credential must be
   **rotated** (assume compromised), and history rewriting a shared remote
   (`git filter-repo`, force-push, teammate re-clones) is their call, walked
   through this gate.
5. Add the path to `.gitignore` and commit a sanitized `*.example`
   counterpart so it cannot recur.

## Agent self-check before any 🔴 command

```markdown
- [ ] Tier classified honestly (worktree loss? shared history?)
- [ ] Recovery anchor SHA captured AND written into my response
- [ ] Backup branch or stash created where applicable
- [ ] Dry run performed where one exists (clean -nd, push --dry-run)
- [ ] User confirmation is explicit, current, and names THIS operation
- [ ] Command is the narrowest variant that achieves the goal
- [ ] Post-op verification plan ready (status / log / stash list)
- [ ] Not touching git config; not skipping hooks; not force-pushing main
```
