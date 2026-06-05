---
mode: agent
description: "Git workflow: branch | commit | pr | status. Subcommand-dispatched version control assistant — scope locking, conventional commits, governance-gated PRs."
---

# /ai-git

Single-verb entry point for all version-control workflows in this template. Dispatches on the first argument.

| Subcommand | Purpose |
|---|---|
| `branch <args>` | Create / list / switch / release feature branches with scope locks |
| `commit` (default) | Refresh dates, validate, draft Conventional Commits message, optionally push |
| `pr <args>` | Pre-merge validation, governance-gated PR generation, merge-check, rebase-and-merge |
| `status` | Quick repo state: current branch, lock holders, ahead/behind, validator status |

**Dispatch rule**: if the user invokes `/ai-git` with no subcommand, default to `commit` (the most common path). If the user invokes `/ai-git <unknown>`, list the table above and ask which they meant.

All subcommands route through [`pds-man-versioncontrol`](../agents/pds-man-versioncontrol.agent.md) (and [`pds-meta-router`](../agents/pds-meta-router.agent.md) for governance). Hard rules below apply to **every** subcommand.

---

## Hard rules (apply to every subcommand)

- **Never** use `--no-verify`.
- **Never** use `git push --force`, `--force-with-lease`, or amend already-pushed commits.
- **Never** merge with failing validators or while `.ai/PAUSE` exists.
- **Never** release another developer's lock (admin `--release-stale` only after timeout).
- **Never** commit files the user did not stage.
- **Always** consult [`pds-man-naming`](../agents/pds-man-naming.agent.md) before introducing a new identifier (scope name, branch name component, etc.).

---

## Subcommand: `branch`

Team-aware branch management with scope locks.

### Usage

```
/ai-git branch --new <scope> <issue>      # Create feature branch + lock
/ai-git branch --list                     # Active locks & branches
/ai-git branch --switch <branch>          # Switch + acquire lock
/ai-git branch --release [--force]        # Release current scope lock
/ai-git branch --release-stale            # Admin: release locks > 72h
/ai-git branch --detect-strategy          # Detect GitHub Flow / Git Flow / Trunk-Based
```

### Steps

1. **Detect strategy** (run on first use, or when `--detect-strategy` is passed):
   ```
   git branch -a
   git show-ref | grep develop
   git show-ref | grep release
   ```
   Classify:
   - **Git Flow** — `develop` + `release/*` branches exist
   - **GitHub Flow** — only `main`; PR protection enforced
   - **Trunk-Based** — direct commits to `main`; no PR requirement
   If uncertain, defer to the value in [`.github/dev-specs.md`](../dev-specs.md) or guide the user to set it via `/ai-onboard`.

2. **Create feature branch (`--new`)**:
   - Prompt: scope name (alphanumeric, ≤20 chars), issue number, brief description.
   - Validate scope name against modules listed in [`.ai/instruct.md`](../../.ai/instruct.md) and [`.github/dev-specs.md`](../dev-specs.md). Reject otherwise.
   - Check existing branches for the same scope: `git branch -a | grep <scope>`. If a lock exists, list the holder and ask whether to coordinate or pick a different scope.
   - Construct branch name: `feature/<scope>-<issue>` (or per detected strategy).
   - Create + push:
     ```
     git checkout -b feature/<scope>-<issue>
     git push -u origin feature/<scope>-<issue>
     ```
   - Write lock file `.ai/locks/<scope>.lock` (YAML metadata: developer, started, branch).
   - Report: branch created, scope locked, target branch, suggested next step (`/ai-git pr`).

3. **List (`--list`)**: show active locks (scope, developer, age, branch) and the user's local branches with their push state and ahead/behind counts.

4. **Switch (`--switch <branch>`)**:
   - `git checkout feature/<branch>`
   - If the scope is already locked by the same developer on a different branch, ask whether this is intentional reassignment; release the old lock first if confirmed.
   - Acquire lock on the new scope.
   - If `.ai/knowledge/` was updated on `main` since branch creation, offer to rebase.

5. **Release (`--release`)**:
   - Verify the current developer owns the lock for the current branch.
   - If uncommitted changes are present, warn and require confirmation.
   - Delete `.ai/locks/<scope>.lock`. Report.

6. **Release stale (`--release-stale`)** — admin only:
   - List locks > 72h old. For each, alert the developer who holds it and require confirmation before deletion. Log to audit trail.

### Failure modes

| Error | Action |
|---|---|
| Scope already locked | Report holder; ask to coordinate or pick a different scope |
| Invalid scope name | List valid scopes from `.ai/instruct.md`; reject and re-prompt |
| Remote push fails | Retry with diagnostic output; suggest network/auth check |
| Lock file write fails | Warn (not mandatory, but coordination risk increases) |
| Uncommitted changes on release | Warn; require explicit confirmation |

---

## Subcommand: `commit` (default)

Stage-aware commit assistant — refreshes dates, validates, drafts a Conventional Commits message, optionally pushes.

### Steps

1. **Inspect staged state**:
   ```
   git status --porcelain=v1
   git diff --cached --stat
   ```
   If nothing is staged, stop and tell the user to stage first. **Do not** run `git add` on the user's behalf.

2. **Refresh `Last Updated`** on staged instruction files. For each staged file matching:
   - `.ai/*.md`
   - `**/.ai/*.md`
   - `.github/copilot-instructions.md`
   - `.ai/instruct.md`

   Read the file. If `**Last Updated**:` is present and not today, update to today (`YYYY-MM-DD`) and re-stage. See [`.ai/conventions.md#versioning`](../../.ai/conventions.md#versioning).

3. **Detect structural / template changes.** If any staged path is one of:
   - `.github/copilot-instructions.md`
   - `.github/prompts/*.prompt.md`
   - `.github/agents/*.agent.md`
   - `.github/skills/**/SKILL.md`
   - `.github/scripts/validate-instructions.ps1`
   - `.ai/conventions.md`, `.ai/maintenance.md`, `.ai/credentials.md`

   Ask the user to bump `Template Version` in [`.github/copilot-instructions.md`](../copilot-instructions.md) and add a CHANGELOG release block. If yes:
   - Propose patch / minor / major (default minor for additions, patch for fixes).
   - Update `Template Version: V<old>` → `V<new>`.
   - In [`CHANGELOG.md`](../../CHANGELOG.md): rename `## [Unreleased]` to `## [<new>] — <today>`, insert a fresh `## [Unreleased]` above it, generate Added/Changed/Fixed bullets from the diff.
   - Re-stage.

4. **Validate.** Invoke `/ai-check rules` (or run [`.github/scripts/validate-instructions.ps1`](../scripts/validate-instructions.ps1) directly). On failure: stop and report. **Never bypass.**

5. **Draft Conventional Commits message**:
   ```
   <type>(<optional scope>): <imperative summary, ≤72 chars>

   <optional body — what & why, ~72 col wrap>
   ```
   Pick `<type>` from: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `ci`. If unclear, ask.

6. **Confirm** with the user:
   1. Commit only
   2. Commit and push (requires upstream branch; if missing, ask for remote/branch)
   3. Cancel

7. **Execute**:
   - Commit only: `git commit -m "<subject>" -m "<body>"`
   - Commit + push: commit, then `git push` (no force flags). On non-fast-forward rejection, **stop**; recommend `git pull --rebase` and re-run.

8. **Report** the commit hash and (if pushed) the remote ref.

### Failure modes

| Error | Action |
|---|---|
| Validator failed | Stop. Show failing checks. Do not commit. |
| Nothing to commit after step 2 | Tell the user; date refresh produced no diff |
| Push rejected | Stop. Do not retry, do not force. Recommend rebase or merge. |
| Pre-commit hook blocked | Relay output. Do not bypass. |

---

## Subcommand: `pr`

Pre-merge validation, governance-gated PR generation, merge-check, and rebase-and-merge.

### Usage

```
/ai-git pr                              # Validate current branch & generate PR
/ai-git pr --draft                      # Generate PR but don't push
/ai-git pr --target <branch>            # Validate against specific target
/ai-git pr --merge-check                # Gate validation only; no PR creation
/ai-git pr --rebase-and-merge           # Execute merge (requires approvals)
```

### Steps

1. **Inspect current state**:
   ```
   git status
   git branch --show-current
   git log --oneline <branch>..origin/main --stat
   git diff origin/main --stat
   ```
   Capture: current branch, scope (extracted from `feature/<scope>-<issue>`), commits ahead, modified files (categorized: source / docs / governance / registries).

2. **Scope validation & lock check**:
   - Read scope authority `<scope_path>/.ai/instruct.md`.
   - Verify lock is still held by the current developer. If a different developer holds it: **BLOCK** and report.
   - If scope name is not in [`.ai/instruct.md`](../../.ai/instruct.md) modules list: **BLOCK** and suggest valid scopes.

3. **Pre-merge validation** (governance gates — run in parallel where possible):

   - **Ports**: `python .ai/engine/port_validator.py . --scope <scope_path> --strict` — any ERROR/WARN ⇒ **BLOCK**; suggest `/ai-check ports`.
   - **Naming registries**: diff `.ai/coding-prefixes.md`, `.ai/error-codes.md`, `.ai/config-vars.md` between branch and `origin/main`; any new identifier that already exists in main ⇒ **BLOCK**; require [`pds-man-naming`](../agents/pds-man-naming.agent.md) reconciliation.
   - **Instruction drift**: invoke [`pds-pipe-reviewer`](../agents/pds-pipe-reviewer.agent.md). If Reviewer blocks, require [`pds-man-curator`](../agents/pds-man-curator.agent.md) approval to proceed.
   - **Governance rules**: walk all governance refs from the scope authority. Any violation ⇒ **BLOCK**; allow override with explicit explanation.
   - **Knowledge sync**: if `.ai/knowledge/` is newer on `main`, ⚠️ warning (not blocking); suggest `git rebase origin/main`.
   - **CI/CD**: query latest workflow run for the branch. Failing ⇒ **BLOCK**.

4. **Generate PR metadata** (description body):

   ```markdown
   ## Scope & Changes
   **Scope Path**: `<scope_path>`
   **Branch**: `feature/<scope>-<issue>`
   **Target**: `main` (GitHub Flow)
   **Issue**: #<issue>

   **Modified Files**:
   - Source: <count>
   - Governance: <count>
   - Registries: <count>
   - Docs: <count>

   ## Governance & Validation
   | Check | Status | Details |
   |---|---|---|
   | Ports | ✓ PASS | … |
   | Naming | ✓ PASS | … |
   | Instructions | ✓ PASS | … |
   | Governance | ✓ PASS | … |
   | Knowledge Sync | ⚠ REBASE SUGGESTED | … |
   | CI/CD | ✓ PASSING | … |

   ## Auto-Suggested Reviewers
   - [ ] @<scope-owner>
   - [ ] @curator-team (if instruction changes)
   - [ ] @governance-lead (if governance changes)
   ```

5. **User confirmation**:
   1. Create PR (push + open via `gh pr create` if available)
   2. Review locally first (`--draft`)
   3. Cancel

6. **Create PR**:
   ```
   git push -u origin feature/<scope>-<issue>
   gh pr create \
     --title "<conventional-commit-summary>" \
     --body "<generated-body>" \
     --base main \
     --head feature/<scope>-<issue> \
     --reviewer <auto-suggested> \
     --label governance,<scope>
   ```
   Report the PR number, target, reviewers, labels.

7. **Merge-check (`--merge-check`)** — runs gates without creating a PR:
   - Is `main` ahead of the feature branch? Suggest rebase.
   - Re-run all validators (1 min timeout).
   - `.ai/PAUSE` exists? **BLOCK**.
   - All required reviewers approved? Else **BLOCK**.
   - CI still passing? Else **BLOCK**.

8. **Execute merge (`--rebase-and-merge`)** — only after all approvals:
   - `git fetch origin`
   - `git rebase origin/main` (if needed)
   - Merge per detected strategy:
     - GitHub Flow: `git merge --ff-only` (or UI button)
     - Git Flow: `git merge --no-ff` into `develop`
   - Post-merge: delete `.ai/locks/<scope>.lock`, delete the local branch, trigger Curator post-merge tasks (index update, KB sync), alert team.

### Failure modes

| Failure | Action |
|---|---|
| Port collision | Report; suggest `/ai-check ports`; require Ports manager reconciliation |
| Naming collision | Report; require Naming Mode 4 reconciliation |
| Instruction drift | Require Curator approval; explain in PR comment |
| Governance violation | Report rule + source; allow override with explanation |
| Main ahead of feature | Suggest rebase; re-run validation |
| CI failing | Report failures; do not proceed |
| PAUSE file present | Merge blocked; report who set it (if documented) |
| Missing approval | List outstanding reviewers; show approval status |

---

## Subcommand: `status`

Quick read-only repo overview. Useful as a fast pre-flight before any other subcommand.

### Steps

1. `git status -s -b` — branch, ahead/behind, dirty state.
2. List active locks: read `.ai/locks/*.lock`, show scope, holder, age.
3. If on a feature branch, show: scope name extracted, validator quick-status (cached if recent), CI status (if `gh` available).
4. Print one-line recommendation: e.g., *"Stage your changes and run `/ai-git commit`."* or *"All gates passing — `/ai-git pr` is safe."*

This subcommand **never** mutates anything.

---

## Routing

- All `/ai-git *` invocations route through [`pds-meta-router`](../agents/pds-meta-router.agent.md), which forwards to [`pds-man-versioncontrol`](../agents/pds-man-versioncontrol.agent.md) with the parsed subcommand.
- `pds-man-versioncontrol` is the single source of truth for version-control logic. This prompt file is the **user-facing surface**; the agent is the **executor**.
