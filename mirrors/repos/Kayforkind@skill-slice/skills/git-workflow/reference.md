# Git Workflow — Reference Encyclopedia

Advanced topics companion to [SKILL.md](SKILL.md). The hard rules there
(no config writes, no unconfirmed destructive ops, no hook skipping) apply to
everything below.

## Contents

- [git bisect](#git-bisect)
- [Cherry-picking](#cherry-picking)
- [Worktrees](#worktrees)
- [Submodules (light)](#submodules-light)
- [Git LFS](#git-lfs)
- [Signed commits](#signed-commits)
- [Monorepo / multi-project awareness](#monorepo--multi-project-awareness)
- [Google Drive / OneDrive path quirks](#google-drive--onedrive-path-quirks)
- [PowerShell git gotchas](#powershell-git-gotchas)
- [Reflog internals](#reflog-internals)
- [Stash internals](#stash-internals)

## git bisect

Binary search over history to find the commit that introduced a regression.
O(log n): ~1,000 commits ≈ 10 test runs.

Manual session:

```powershell
git bisect start
git bisect bad                     # current HEAD is broken
git bisect good v2.3.0             # last known-good tag/SHA
# git checks out the midpoint; build + test, then verdict:
git bisect good                    # midpoint works → bug is later
git bisect bad                     # midpoint broken → bug is earlier
# repeat until: "<sha> is the first bad commit"
git bisect log > bisect-session.txt   # keep the evidence
git bisect reset                   # ALWAYS: return to the original HEAD
```

Automated with a test script — exit code contract: `0` = good,
`1–124` / `126` / `127` = bad, `125` = skip this commit (unbuildable):

```powershell
# test.ps1 must set the process exit code explicitly:
#   if ($failed) { exit 1 } else { exit 0 }
git bisect start HEAD v2.3.0
git bisect run pwsh -NoProfile -File .\test.ps1
git bisect reset
```

Notes:

- A **flaky test poisons the whole search** — one wrong verdict sends bisect
  into the wrong half. Stabilize or re-run the test per commit.
- `git bisect skip` for commits that don't build; if the culprit hides among
  skipped commits, bisect reports a range instead of one SHA.
- Bisect works on any predicate, not just bugs: "when did bundle size cross
  5 MB", "when did this string disappear".
- You are in detached HEAD throughout — normal; do not commit during a
  bisect. `git bisect reset` cleans up.

## Cherry-picking

Copy an existing commit onto the current branch (new SHA, same patch).

```powershell
git cherry-pick abc1234                    # single commit
git cherry-pick abc1234 def5678            # several, in the order given
git cherry-pick "abc1234..def5678"         # range: EXCLUDES abc1234 itself
git cherry-pick "abc1234^..def5678"        # range including abc1234 (quote the ^)
git cherry-pick -x abc1234                 # append "(cherry picked from ...)" — use for backports
git cherry-pick -n abc1234                 # --no-commit: stage only, review, commit yourself
git cherry-pick -m 1 <merge-sha>           # picking a merge commit: -m 1 = diff vs first parent
git cherry-pick --continue                 # after resolving conflicts
git cherry-pick --abort                    # restore pre-pick state
```

Guidance:

- Use `-x` whenever the source branch is public (release backports) — the
  trailer is how future readers trace the origin.
- Prefer picking onto release/hotfix branches over re-implementing the fix.
- Chained picks that each conflict usually mean the branches have diverged
  too far — consider a real merge instead.
- Cherry-picked commits are **not** deduplicated by later merges; the same
  change may appear twice in `git log` (different SHAs). `git log --cherry-pick`
  and rebase can suppress patch-identical duplicates, but review merges of
  backported branches carefully.

## Worktrees

Multiple working directories sharing one `.git` — review a PR or build a
hotfix without stashing your current state.

```powershell
git worktree add ..\repo-hotfix hotfix/rollback-webhook   # existing branch
git worktree add ..\repo-review -b review/pr-482 origin/feat/csv-export
git worktree list
git worktree remove ..\repo-hotfix
git worktree prune                                        # clean up stale entries
```

Rules and Windows notes:

- A branch can be checked out in **only one** worktree at a time; git refuses
  the second checkout (this protects you).
- Place worktrees as **siblings** of the main clone (`..\repo-x`), never
  inside it, and never inside a cloud-synced folder (see the Drive section).
- Each worktree has its own index and HEAD but shares refs, objects, and
  stash. `git stash` from any worktree lands in the shared stash list.
- Hooks run from the shared `.git`; per-worktree hook behavior differs only
  if the repo uses `core.hooksPath` (do not set it — config).
- Deep worktree paths can hit the Windows 260-char `MAX_PATH` limit; symptom
  is `Filename too long`. Fix belongs to the user (`git config core.longpaths true`
  and/or the Windows `LongPathsEnabled` registry policy) — hand them the
  command; do not run it.

## Submodules (light)

Enough to not break repos that use them — deep submodule surgery should be
escalated to the user.

```powershell
git clone --recurse-submodules <url>            # correct initial clone
git submodule update --init --recursive         # fix a clone that forgot
git submodule status                            # SHAs + state per submodule
git pull; git submodule update --init --recursive   # pull does NOT update submodules
git diff --submodule=log                        # what a submodule bump actually changes
```

Pitfalls:

- `git status` showing `modified: libs/foo (new commits)` means the
  **pointer** changed, not the files. Committing that line pins the
  superproject to a different submodule SHA — only do it deliberately.
- Submodules check out in **detached HEAD** by design. To change one:
  `cd` in, `git switch -c branch`, commit, push the submodule, then commit
  the new pointer in the superproject — in that order, or collaborators get
  a pointer to a commit that only exists on your machine.
- Never `git add libs/foo/` with a trailing slash-and-contents intent —
  the submodule is a single gitlink entry, not a directory of files.

## Git LFS

Large File Storage replaces big binaries with small pointer files.

Detection and daily use (safe — no config writes):

```powershell
git lfs ls-files                    # what LFS tracks in this repo
Get-Content .gitattributes          # look for: *.psd filter=lfs diff=lfs merge=lfs
git lfs pull                        # fetch real content if you see pointer stubs
```

- **Symptom of missing LFS**: a "binary" file is ~130 bytes of text starting
  with `version https://git-lfs.github.com/spec/v1`. Do not commit "fixes"
  to pointer files.
- **Config boundary**: `git lfs install` writes filter entries to the user's
  global git config. That violates the no-config rule — if LFS is not set up,
  give the user the command (`git lfs install`) instead of running it.
- Track new patterns only on user request: `git lfs track "*.onnx"` edits
  `.gitattributes` (a normal repo file — commit it), and requires LFS to be
  installed already.
- LFS objects don't travel with a plain `git bundle`/mirror; migrations need
  `git lfs fetch --all` first — escalate migrations to the user.

## Signed commits

Read and respect signing; never configure it (config writes).

```powershell
git log --show-signature -1         # verify signature on HEAD
git verify-commit abc1234           # explicit verification
git commit -S -F - ...              # sign one commit ad hoc IF user asks and keys exist
```

- If the repo/org **requires** signed commits and signing fails (no key, no
  agent, expired key), report the exact error and stop — do not disable
  `commit.gpgsign`, do not retry with `--no-gpg-sign` unless the user says so.
- Rebase and amend **re-create** commits: previously signed commits lose
  their signatures unless re-signed. Mention this whenever rewriting signed
  history.
- SSH-based signing (`gpg.format ssh`) behaves the same for our purposes:
  presence of signing is config-owned; we only consume it.

## Monorepo / multi-project awareness

In a monorepo, unscoped commands lie: `git log` mixes every project,
`git add .` sweeps unrelated services. Scope everything with pathspecs.

```powershell
git log --oneline -n 20 -- services/api/         # history of ONE project
git diff origin/main -- packages/ui/              # what changed here vs main
git add services/api/ ':(exclude)services/api/testdata/big.json'
git log --oneline -- ':(top)docs/'                # :(top) = repo root even from subdir
git blame -L 40,60 -- services/api/handler.cs
```

- Branch names should carry the project: `feat/api-rate-limits`,
  `fix/ui-482-modal-focus`.
- Commit scope = project: `feat(api): ...` vs `feat(ui): ...` keeps
  `git log --grep` and changelog tooling usable.
- **Sparse checkout** (`git sparse-checkout set services/api`) speeds up huge
  repos but flips repo-local config under the hood — get user consent first,
  like any config change.
- CI path filters mean an innocent root-level edit can trigger every
  pipeline; prefer keeping commits inside one project directory.
- Cross-project refactors: one commit per project is kinder to reviewers and
  to future bisects than one mega-commit, unless atomicity is required to
  keep the build green — then say so in the commit body.

## Google Drive / OneDrive path quirks

Repos living inside synced folders (`YOUR_DRIVE\...`,
`C:\Users\<u>\OneDrive\...`) misbehave in specific ways:

| Symptom | Cause | Response |
|---|---|---|
| `Unable to create '.git/index.lock': File exists` with no git running | Sync client held/duplicated the lock | Verify no git process, then delete only `index.lock`; suggest pausing sync during git ops |
| `git status` takes 30+ s | Virtual/streamed files force hydration on every stat | Suggest marking the repo folder "available offline"; keep repos out of synced dirs long-term |
| Files like `handler (1).cs` or `SKILL (conflicted copy).md` appear | Sync conflict duplicates | Never commit them; reconcile manually, delete the duplicate |
| Random `error: unable to write sha1 filename` | Sync client locked an object file mid-write | Retry after pausing sync |
| Repo corruption after two machines sync simultaneously | `.git` internals are not merge-safe | Escalate; recover by re-cloning, salvage work via `git fsck` / bundle |

Practical rules:

- **Always quote** these paths — `"YOUR_DRIVE\project"` has a space by
  construction.
- Advise (don't enforce): keep the repo outside the synced tree and sync
  release artifacts instead; or at minimum exclude `.git/` from sync if the
  client supports it.
- Before any heavy operation (rebase, large checkout) in a synced repo,
  suggest pausing sync; resume after.

## PowerShell git gotchas

The ones that actually bite agents:

1. **`@{...}` is hashtable syntax.** `git rev-parse @{u}` fails or
   misparses — always quote: `git rev-parse "@{u}"`,
   `git diff "HEAD@{1}"`, `git log "main@{yesterday}"`.
2. **Here-string terminators are column-sensitive.** The closing `"@` of a
   `@"..."@` block must be at the start of the line — leading spaces break it.
3. **No bash heredoc.** `git commit -F - <<EOF` is a syntax error in
   PowerShell; the equivalent is the here-string pipe:
   `@"..."@ | git commit -F -`.
4. **Check `$LASTEXITCODE`, not just output.** Native commands don't throw;
   after every git call that matters:
   `if ($LASTEXITCODE -ne 0) { <handle> }`. (PowerShell 7.4+ can auto-throw
   via `$PSNativeCommandUseErrorActionPreference` — a preference variable you
   may set per-session, not git config.)
5. **Built-in aliases shadow classic git shortcuts.** `gc` = `Get-Content`,
   `gl` = `Get-Location`, `gp` = `Get-ItemProperty`, `sc` = `Set-Content` —
   never define or rely on two-letter git aliases; spell commands out.
6. **`2>&1` turns stderr into ErrorRecords** in Windows PowerShell 5.1, which
   can make *successful* git commands (git chats on stderr) look like errors.
   Prefer checking `$LASTEXITCODE`; use `--porcelain`/`--quiet` flags where
   available.
7. **Variable expansion in double quotes.** `git commit -m "fix $bug"`
   interpolates `$bug`; use single quotes for literal `$`, or here-strings
   with `@'...'@` (single-quoted = no interpolation).
8. **Encoding of piped text.** Windows PowerShell 5.1 pipes to native
   programs in the console codepage — non-ASCII commit messages can mangle.
   In-session remedy (env/pref, not config):
   `$OutputEncoding = [Text.Encoding]::UTF8`, or write the message with
   `Set-Content -Encoding utf8 msg.txt` and use `git commit -F msg.txt`.
   PowerShell 7+ defaults to UTF-8 and is fine.
9. **`&&` / `||` require PowerShell 7+.** In 5.1 use `;` plus explicit
   `$LASTEXITCODE` checks — `;` does NOT short-circuit on failure.
10. **Stop-parsing token `--%`** passes the rest of the line raw — last
    resort for arguments PowerShell keeps eating:
    `git log --% --pretty=format:"%h %s"` (note: `%` is also cmd-special,
    and PowerShell format strings otherwise need doubled quoting care).
11. **Paths with spaces** — quote them everywhere, including pathspecs after
    `--`. Tab-completion habits don't exist in agent shells.
12. **Pager hangs.** Set `$env:GIT_PAGER = "cat"` (or use `git --no-pager`)
    at session start; `less` waiting for a keypress looks like a frozen tool
    call.

## Reflog internals

`git reflog` is the journal of every HEAD/branch movement in **this clone**:
commits, checkouts, resets, rebases, merges, amends.

```powershell
git reflog                                  # HEAD's journal
git reflog show feat/csv-export             # a branch's journal
git log -g --date=iso                       # reflog with full metadata
git diff "HEAD@{2}" HEAD                    # what changed across two moves (quote it)
git branch rescue "HEAD@{5}"                # resurrect a state as a branch
```

- Reflog entries expire: 90 days for reachable, 30 for unreachable
  (defaults). `git gc` prunes expired entries — recover sooner, not later.
- Reflog does **not** exist on the remote and does not transfer on clone.
- The recovery move is always the same: find the SHA, `git branch rescue <sha>`
  immediately, then investigate at leisure.
- What reflog cannot bring back: uncommitted worktree changes, untracked
  files, unstaged hunks. Only committed (or stashed) states have refs.

## Stash internals

A stash entry is a real commit (plus parents for index/untracked state) on
the `refs/stash` stack — which is why `git stash branch` works.

```powershell
git stash push -u -m "wip: half-done cursor pagination"   # -u = include untracked
git stash list                                            # stash@{0} is newest
git stash show -p "stash@{1}"                             # inspect before applying (quote it)
git stash apply "stash@{1}"                               # apply, keep entry
git stash pop                                             # apply newest, drop on success
git stash branch feat/from-stash "stash@{0}"              # branch from where it was stashed
git stash drop "stash@{2}"                                # gated: user sees show -p first
```

- **`pop` keeps the entry if applying conflicts** — resolve, then drop
  manually. Never assume pop consumed the stash.
- `-u` matters: plain stash ignores untracked files, the classic source of
  "stash lost my new file" (it never had it).
- Stashes are per-clone, unpushed, and invisible to teammates — long-lived
  work belongs on a branch, not in `stash@{7}`.
- A dropped stash's commit is briefly recoverable:
  `git fsck --unreachable | Select-String commit`, inspect candidates with
  `git show <sha>`.
