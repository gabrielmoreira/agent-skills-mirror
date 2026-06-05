---
mode: agent
description: "[deprecated -> /ai-git branch] Create and manage feature branches with scope locking, branch strategy awareness, and team coordination."
---

# /ai-branch (DEPRECATED)

> **Superseded by `/ai-git branch`.** See [.github/prompts/ai-git.prompt.md](ai-git.prompt.md).
> This file is commented out during verification and will be removed after sign-off.

<!-- DEPRECATED-CONTENT-BEGIN

Team-aware branch management. Detects branch strategy, creates feature branches with scope locks, detects conflicts, and coordinates multi-developer workflows.

## Usage

```
/ai-branch --new <scope> <issue>       # Create feature branch with lock
/ai-branch --list                      # Show active locks & branches
/ai-branch --switch <branch>           # Switch branch & acquire lock
/ai-branch --release [--force]         # Release current scope lock
/ai-branch --release-stale             # Admin: release stale locks
/ai-branch --detect-strategy           # Detect branch strategy (GitHub Flow / Git Flow / Trunk-Based)
```

## Steps

### 1. Detect Branch Strategy

Run:
```bash
git branch -a
git show-ref | grep develop
git show-ref | grep release
```

Classify:
- **Git Flow**: `develop` + `release/*` branches exist
- **GitHub Flow**: Only `main` (default); PR protection enforced
- **Trunk-Based**: Commits directly to `main`; no PR requirement (rare)

Report strategy. If uncertain or first run, guide user to pick preferred strategy via `/ai-onboard` or `.github/dev-specs.md`.

### 2. Create Feature Branch (--new)

Prompt user:
```
Scope name (e.g., 'api', 'db', 'validation'): _
Issue number (e.g., '456'): _
Brief description (auto-generated from issue if available): _
```

1. **Validate scope name**: alphanumeric, max 20 chars; suggest scope path from `.ai/instruct.md`
2. **Construct branch name**: `feature/<scope>-<issue>` (GitHub Flow) or from `develop` (Git Flow)
3. **Check for conflicts**:
   - Does another branch already work on this scope? → Query: `git branch -a | grep <scope>`
   - If yes: list lock holder; ask if developer wants to coordinate or use different scope
4. **Create branch**:
   ```bash
   git checkout -b feature/<scope>-<issue>
   git push -u origin feature/<scope>-<issue>
   ```
5. **Create lock file**: `.ai/locks/<scope>.lock` with YAML metadata
6. **Report**:
   ```
   ✓ Branch created: feature/api-versioning-456
   ✓ Scope locked: api (you, 2026-06-04T11:00:00Z)
   ✓ Target branch: main (GitHub Flow)
   → Start working. Run /ai-pr when ready to merge.
   ```

### 3. List Branches & Locks (--list)

Show:
```
Active Locks:
  Scope    Developer              Started           Branch
  api      alice@example.com      2h ago            feature/api-versioning-456
  db       bob@example.com        30m ago           feature/db-migration-789

Your Branches:
  feature/api-caching-#123       (local, not pushed)
  feature/ui-refactor-#456       (pushed, 3 commits ahead of main)
```

Indicate:
- Which scope each branch owns
- How old the lock is
- Branch status (local only, pushed, commits ahead)

### 4. Switch Branch (--switch)

```bash
git checkout feature/<branch>
```

Then:
1. **Check if scope already locked** (by same developer on different branch)
   - If yes: ask if intentional scope re-assignment; release old lock if yes
2. **Acquire lock** on new scope
3. **KB sync**: if `.ai/knowledge/` modified on main, offer to rebase

### 5. Release Lock (--release)

User command:
```bash
/ai-branch --release
```

1. **Verify**: current developer owns lock for current branch
2. **Delete lock file**: `.ai/locks/<scope>.lock`
3. **Git status**: check if anything uncommitted
   - If yes: warn "Uncommitted changes on `<scope>`; still releasing lock?"
   - If no: proceed
4. **Report**:
   ```
   ✓ Lock released: api (on feature/api-versioning-456)
   → Scope is now available for other developers.
   ```

### 6. Release Stale Locks (--release-stale)

**Admin only** (developer with repo admin role). Run:

```bash
ls -lh .ai/locks/
```

For each lock older than 72h:
1. Read lock file; extract developer email
2. **Alert**: "Lock `<scope>` held by `<developer>` for 3+ days; release? (requires confirmation)"
3. If confirmed: delete lock; log to audit trail

### 7. Detect Strategy (--detect-strategy)

Run automatically on first use; allow manual re-run with:
```bash
/ai-branch --detect-strategy
```

Output:
```
Branch Strategy Detected: GitHub Flow
  Main branch: main
  Integration branch: (none; GitHub Flow uses main only)
  Feature branches: feature/*
  PR required: yes
  Min reviewers: 1
  Rebase preferred: true

Recommendation for your team:
  Team size: <from dev-specs>
  Velocity: <from dev-specs>
  Distributed: <yes/no>

  → GitHub Flow is suitable. Ensure all PRs go through review before merge.
```

---

## Hard Rules

- **Lock creation is mandatory** for non-trivial changes. Even read-only scope exploration should acquire a "read" lock (optional; defaults to "in-progress").
- **Never create branches without scope locking.** Prevents concurrent modifications.
- **Never release another developer's lock** (except admin via --release-stale after timeout).
- **Scope name must be in `.ai/instruct.md` or `.github/dev-specs.md` modules list**. Reject invalid scopes.
- **Branch naming must follow strategy convention**. GitHub Flow: `feature/*`, `bugfix/*`, `hotfix/*`. Git Flow: `feature/*`, `release/*`, `hotfix/*`.

---

## Failure Modes

| Error | Action |
|-------|--------|
| **Scope already locked** | Report lock holder; ask to coordinate; offer to wait or use different scope |
| **Invalid scope name** | List valid scopes from `.ai/instruct.md`; reject and re-prompt |
| **Branch creation fails** (e.g., remote error) | Retry with diagnostic output; suggest checking network/auth |
| **Lock file creation fails** | Warn; lock creation not mandatory, but coordination risk increases |
| **Uncommitted changes on release** | Warn; require user confirmation before releasing lock |

---

DEPRECATED-CONTENT-END -->

<!-- Original integration block (also deprecated):
## Integration

Called by:
- User: `/ai-branch --new api <issue>`
- Router: Passes to `pds-man-versioncontrol` agent
- Supervisor: Pre-stage 0, validates lock (calls version control agent)

Calls:
- `pds-man-versioncontrol.agent.md` (actual logic)
- `pds-man-naming.agent.md` (if scope name validation needed)
- Git CLI (`git branch`, `git checkout`, `git push`)

Reads:
- `.ai/locks/*` (scope metadata)
- `.github/dev-specs.md` (team config, modules list)
- `.ai/instruct.md` (scope authority)

Creates:
- `.ai/locks/<scope>.lock` (YAML metadata)
- Git branch on remote

---

## Examples

### Example 1: Create Feature Branch

```
User: /ai-branch --new api versioning

AI: Scope name: api
    Issue number: 456
    Description: "Implement API v2 versioning" (from GitHub issue)

    Branch strategy detected: GitHub Flow
    Target branch: main

    ✓ Branch created: feature/api-versioning-456
    ✓ Lock acquired: scope "api" (until merge)
    ✓ Pushed to origin

    Next steps:
    1. Work on your feature (commits go to feature/api-versioning-456)
    2. When ready: /ai-pr
    3. Create PR; get review
    4. On merge: lock auto-released
```

### Example 2: Scope Conflict

```
User: /ai-branch --new api caching

AI: Scope name: api

    ⚠️  Scope 'api' is already locked!

    Lock holder: alice@example.com
    Branch: feature/api-versioning-456
    Locked for: 2 hours

    Options:
    1. Use a different scope (e.g., 'api-caching' if distinct)
    2. Coordinate with alice (message in team chat)
    3. Wait for alice's PR to merge, then rebase

    Recommended: Coordinate with alice. If combining features, rebase to latest.
```

### Example 3: Release Lock

```
User: /ai-branch --release

AI: ✓ Scope 'api' lock released
    Branch: feature/api-versioning-456

    Next: Push final commits, create PR via /ai-pr
```

---

## See Also

- [`.ai/version-control.md`](../../.ai/version-control.md) — Branch strategies, locking mechanism
- [`/ai-pr`](ai-pr.prompt.md) — Pre-merge validation & PR generation
- [`/ai-commit`](ai-commit.prompt.md) — Local commit validation
- [`.github/agents/pds-man-versioncontrol.agent.md`](../../.github/agents/pds-man-versioncontrol.agent.md) — Core logic

-->
