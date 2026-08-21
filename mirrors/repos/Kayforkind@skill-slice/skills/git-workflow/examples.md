# Git Workflow — Worked Scenarios

Seven end-to-end transcripts applying [SKILL.md](SKILL.md). Commands are
PowerShell; outputs are representative. Every scenario respects the hard
rules: no config writes, no unconfirmed destructive ops, no `--no-verify`,
commits only on user request.

## Scenario 1 — Feature branch, staged commit, push

**User:** "Add the CSV export helper, then commit and push it on a new branch."

```powershell
# Preflight
$env:GIT_PAGER = "cat"
git status
# On branch main
# Your branch is up to date with 'origin/main'.
# nothing to commit, working tree clean

git fetch origin
git switch -c feat/csv-export origin/main
# branch 'feat/csv-export' set up to track 'origin/main'.
# Switched to a new branch 'feat/csv-export'

# ... (code written: src/export/CsvWriter.cs, tests/CsvWriterTests.cs) ...

# Review before staging — never skip
git status
# Untracked files:
#   src/export/CsvWriter.cs
#   tests/CsvWriterTests.cs
git diff                      # nothing unstaged-but-tracked; new files shown by status
git log --oneline -n 5        # confirm house style: conventional commits in use

# Stage by explicit pathspec
git add src/export/CsvWriter.cs tests/CsvWriterTests.cs
git diff --staged             # final read of exactly what will be committed
```

The user asked for the commit, so commit — message explains *why*:

```powershell
@"
feat(export): add CsvWriter with RFC 4180 quoting

Support asked for spreadsheet-friendly exports; JSON dumps were being
hand-converted and silently corrupting fields containing commas.
CsvWriter escapes per RFC 4180 (double-quote wrapping, embedded quote
doubling) so Excel and Sheets import without data loss.

Refs: #391
"@ | git commit -F -
# [feat/csv-export 3f2a9c1] feat(export): add CsvWriter with RFC 4180 quoting
#  2 files changed, 148 insertions(+)

git push -u origin HEAD
# branch 'feat/csv-export' set up to track 'origin/feat/csv-export'.
```

**Done when:** commit exists with passing hooks, branch pushed with tracking,
working tree clean.

## Scenario 2 — Commit blocked by a failing pre-commit hook

**User:** "Commit the parser fix."

```powershell
git add src/parser/Tokenizer.cs
git diff --staged             # reviewed: one-line fix + a debug WriteLine left in

@"
fix(parser): treat CRLF as single newline token

Windows-authored files produced double blank-line tokens because \r\n
was tokenized as two newlines, breaking paragraph detection downstream.

Refs: #402
"@ | git commit -F -
# lint........................................Failed
# - hook id: lint
# - exit code: 1
#   src/parser/Tokenizer.cs(88): error LNT004: Console.WriteLine in library code
```

**Wrong move:** `git commit --no-verify` — forbidden unless the user asks.
**Right move:** fix what the hook found, restage, retry:

```powershell
# remove the stray Console.WriteLine at Tokenizer.cs:88, then:
git add src/parser/Tokenizer.cs
git diff --staged             # re-review: now only the intended fix
@"
fix(parser): treat CRLF as single newline token

Windows-authored files produced double blank-line tokens because \r\n
was tokenized as two newlines, breaking paragraph detection downstream.

Refs: #402
"@ | git commit -F -
# lint........................................Passed
# [fix/402-crlf-token 9b8e2d4] fix(parser): treat CRLF as single newline token
```

If the hook is a **formatter that rewrites files**, it typically fails once
after modifying the tree; check `git status`, `git add` the reformatted
files, and commit again — same message, no bypass.

**Done when:** hook passes on its own merits; the bypass flag was never used.

## Scenario 3 — Rebase onto main hits a conflict

**User:** "Rebase my branch onto latest main." (Branch `feat/rate-limits`
was pushed, but the user confirms they are the only one on it.)

```powershell
git fetch origin
git rebase origin/main
# Auto-merging src/api/Middleware.cs
# CONFLICT (content): Merge conflict in src/api/Middleware.cs
# error: could not apply 5c1d3aa... feat(api): add sliding-window limiter

git status
# interactive rebase in progress; onto 8d92f11
# Unmerged paths:
#   both modified:   src/api/Middleware.cs
```

Orientation — this is a **rebase**, so the meanings invert: `--ours` is
`origin/main` (the base), `--theirs` is *my own commit* being replayed.
Open the file:

```text
<<<<<<< HEAD
        app.UseAuthentication();
        app.UseAuthorization();
=======
        app.UseAuthentication();
        app.UseRateLimiter(SlidingWindow(100, TimeSpan.FromMinutes(1)));
>>>>>>> 5c1d3aa (feat(api): add sliding-window limiter)
```

Main added `UseAuthorization()`; my commit added the limiter. Both intents
must survive — hand-merge, don't whole-file take:

```csharp
        app.UseAuthentication();
        app.UseAuthorization();
        app.UseRateLimiter(SlidingWindow(100, TimeSpan.FromMinutes(1)));
```

```powershell
git add src/api/Middleware.cs
git grep -nE "^(<{7} |={7}$|>{7} )" -- .    # no leftover markers
git rebase --continue
# Successfully rebased and updated refs/heads/feat/rate-limits.

# Branch was previously pushed → history rewritten → lease-protected push,
# already approved by the user's rebase request for this solo branch:
git push --force-with-lease
```

**Bail-out at any point before continue:** `git rebase --abort` restores the
exact pre-rebase state.

**Done when:** rebase completes, markers grep is clean, tests pass, remote
updated via `--force-with-lease` (never bare `--force`).

## Scenario 4 — Open a PR with gh

**User:** "Open a PR for this branch against main."

```powershell
gh auth status
# github.com: Logged in to github.com account user (keyring)

git status                       # clean tree, on feat/csv-export
git log --oneline origin/main..HEAD    # exactly the commits the PR will carry
# 3f2a9c1 feat(export): add CsvWriter with RFC 4180 quoting

git push -u origin HEAD          # idempotent if already pushed

$body = @"
## Summary
- Add `CsvWriter` with RFC 4180-compliant quoting
- Cover comma, quote, and newline fields in unit tests

## Why
Support was hand-converting JSON dumps to CSV and silently corrupting
comma-containing fields. Closes #391.

## Testing
- [x] `dotnet test tests/CsvWriterTests.cs` — 12/12 passing
- [x] Manual import of generated CSV into Excel and Google Sheets

## Notes for reviewers
Quoting logic is in one pure function (`Escape`), start there.
"@
gh pr create --title "feat(export): add CsvWriter with RFC 4180 quoting" `
             --body $body --base main
# https://github.com/acme/exporter/pull/412
```

Report the URL to the user. Follow-up changes: push more commits to the same
branch — the PR updates itself; never open a duplicate PR.

**Done when:** PR exists with structured body, correct base, title matching
the head commit.

## Scenario 5 — Undo the last commit safely (soft reset)

**User:** "I committed too early — the test file is missing. Undo it but
keep my work, then recommit with everything."

Preflight decides the method — soft reset is only clean while unpushed:

```powershell
git status -sb
# ## feat/csv-export...origin/feat/csv-export [ahead 1]     ← NOT pushed: safe
git log --oneline -n 2
# 3f2a9c1 feat(export): add CsvWriter with RFC 4180 quoting
# 8d92f11 chore: bump analyzers

git reset --soft HEAD~1
# No output. Nothing is lost: the commit's changes are now staged again.
git status
# On branch feat/csv-export
# Changes to be committed:
#   new file:   src/export/CsvWriter.cs

git add tests/CsvWriterTests.cs        # the missing piece
git diff --staged                      # re-review the full, corrected commit
@"
feat(export): add CsvWriter with RFC 4180 quoting

Support asked for spreadsheet-friendly exports; JSON dumps corrupted
comma-containing fields. Includes unit tests for comma, quote, and
newline fields.

Refs: #391
"@ | git commit -F -
```

Why `--soft` and not `--hard`: `--soft` moves only the branch pointer;
index and worktree are untouched, so it is **not** a gated operation.
If the commit **had been pushed**, this becomes history rewriting —
stop and walk [safety-checklist.md](safety-checklist.md) instead.

**Done when:** single corrected commit contains all intended files;
`git log` shows no leftover partial commit.

## Scenario 6 — Recover a deleted branch via reflog

**User:** "I deleted feat/import-v2 yesterday and it wasn't merged. Get it back."

```powershell
git branch --list "feat/import-v2"
# (empty — it's gone locally)

git reflog | Select-String "moving from feat/import-v2"
# 1c2d3e4 HEAD@{38}: checkout: moving from feat/import-v2 to main
```

**Gotcha:** the SHA shown on a `checkout:` line is the **destination**
(`main`'s tip), not the branch you left. The deleted branch's tip is where
HEAD sat just *before* leaving — the next-older entry, `HEAD@{39}`:

```powershell
git rev-parse "HEAD@{39}"          # quote the @{} in PowerShell
# e4b7a21
git log --oneline -n 3 e4b7a21     # verify before resurrecting
# e4b7a21 feat(import): validate header row before mapping
# c9d0f83 feat(import): map legacy column aliases
# 8d92f11 chore: bump analyzers

git branch feat/import-v2 e4b7a21
git log --oneline feat/import-v2 -n 2     # confirm restoration
```

If the local reflog has expired but the branch was ever pushed:
`git branch feat/import-v2 origin/feat/import-v2` (or re-fetch). If neither
exists, `git fsck --lost-found` is the last resort — escalate before
declaring the work lost.

**Done when:** branch ref exists again and its tip log matches what the user
remembers.

## Scenario 7 — Committed on the wrong branch (main) — not pushed

**User:** "I just realized my last two commits landed on main instead of a
feature branch. Fix it."

```powershell
git status -sb
# ## main...origin/main [ahead 2]        ← ahead only: NOT pushed. Recoverable cleanly.
git log --oneline -n 3
# 71acd02 feat(report): weekly digest email
# 4f0b9ee feat(report): digest data query
# 1c2d3e4 (origin/main) chore: release 2.4.1

# 1. Preserve the work on a correctly named branch (cheap, zero risk):
git branch feat/weekly-digest

# 2. Moving main back to origin/main requires reset --hard → GATED.
```

`NEEDS_CONFIRMATION`-style stop, then after explicit user approval:

```powershell
git rev-parse HEAD                        # record: 71acd02 (recovery anchor)
git switch main
git reset --hard origin/main              # approved; work is safe on feat/weekly-digest
git log --oneline -n 1
# 1c2d3e4 chore: release 2.4.1            ← main matches remote again

git switch feat/weekly-digest
git log --oneline -n 2                    # both commits intact here
```

Had main **already been pushed**, the fix changes entirely: never rewrite
remote main — instead `git revert` the commits on main and cherry-pick the
originals onto the feature branch.

**Done when:** main equals `origin/main`, the feature branch holds both
commits, and the recovery SHA was recorded in the response before the reset.
