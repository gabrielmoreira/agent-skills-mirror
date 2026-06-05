---
mode: agent
description: "[deprecated -> /ai-git pr] Pre-merge validation, PR generation with governance metadata, conflict detection, and team review coordination."
---

# /ai-pr (DEPRECATED)

> **Superseded by `/ai-git pr`.** See [.github/prompts/ai-git.prompt.md](ai-git.prompt.md).
> This file is commented out during verification and will be removed after sign-off.

<!-- DEPRECATED-CONTENT-BEGIN

Team-aware merge assistant. Validates changes don't break governance, generates PR with auto-suggested reviewers, detects registry conflicts, and gates merge on validation.

## Usage

```
/ai-pr                              # Validate current branch & generate PR
/ai-pr --draft                      # Generate PR but don't push
/ai-pr --target <branch>            # Validate against specific target (main/develop/etc)
/ai-pr --merge-check                # Check if ready to merge (gate validation)
/ai-pr --rebase-and-merge           # Execute merge (requires approval)
```

## Steps

### 1. Inspect Current State

Run:
```bash
git status
git branch --show-current
git log --oneline <current-branch>..origin/main --stat
git diff origin/main --stat
```

Capture:
- Current branch name (e.g., `feature/api-versioning-456`)
- Extract scope from branch name: `<scope>` from `feature/<scope>-<issue>`
- Commits on current branch (vs. target: `main` or `develop`)
- Modified files (categorize: source, docs, governance, registries)
- File counts

### 2. Scope Validation & Lock Check

1. **Extract scope** from branch name
2. **Read scope authority**: `<scope_path>/.ai/instruct.md`
3. **Check lock**: Is scope still locked by current developer?
   - If yes: lock is valid; continue
   - If no but branch exists: warn "Lock not found; recreate with /ai-branch --switch"
   - If different developer: **BLOCK**; report conflict
4. **Validate scope exists**: Check `.ai/instruct.md` modules list
   - If invalid: **BLOCK**; suggest valid scopes

### 3. Pre-Merge Validation (Governance Checks)

Run all validators in parallel:

#### 3a. Port Collision Check

```bash
python .ai/engine/port_validator.py . --scope <scope_path> --strict
```

- If ERROR or WARN: **BLOCK merge**; report findings; suggest running `/ai-ports-check`
- If PASS: ✓ port registry clean

#### 3b. Naming Registry Collision Check

```bash
# Diff registries: feature branch vs. main
git diff origin/main -- .ai/coding-prefixes.md .ai/error-codes.md .ai/config-vars.md
```

For each registry:
1. Extract identifiers added on feature branch
2. Check if any already exist in main's version
3. If collision: **BLOCK merge**; list conflicts; require Naming manager reconciliation

#### 3c. Instruction Drift Check

Call `pds-pipe-reviewer` agent:
- Diff `.ai/instruct.md` on feature branch vs. main
- If changes found: run Reviewer validation
- If Reviewer blocks: **BLOCK merge**; require Curator approval to proceed

#### 3d. Governance Rule Check

For each file modified:
1. Walk all governance refs from scope authority
2. Check if change violates any rule (from `.ai/governance/` or linked rules)
3. If violation: **BLOCK merge**; list rule + source; ask if intentional (can override with explanation)

#### 3e. Knowledge Sync Status

Check if `.ai/knowledge/` modified on main after branch creation:
```bash
git log origin/main -1 --format="%ai" -- .ai/knowledge/ > main_kb_date
git log <branch> -1 --format="%ai" -- .ai/knowledge/ > feature_kb_date
```

If main is newer:
- ⚠️ WARNING (not blocking): "Knowledge base updated on main; consider rebase"
- Suggest: `git rebase origin/main` (to sync KB before merge)

#### 3f. CI/CD Status

If GitHub/GitLab Actions configured:
- Query latest workflow run for this branch
- If failing: **BLOCK merge**; report failures
- If passing: ✓ CI clean

### 4. Generate PR Metadata

Create PR description with:

```markdown
## Scope & Changes

**Scope Path**: `<scope_path>`
**Branch**: `feature/<scope>-<issue>`
**Target**: `main` (GitHub Flow)
**Issue**: #<issue> (link to GitHub/GitLab issue if available)

**Modified Files**:
- Source: <count> files
- Governance: <count> files (.ai/*.md, .github/*)
- Registries: <count> files (naming/port registries)
- Docs: <count> files

---

## Governance & Validation

| Check | Status | Details |
|-------|--------|---------|
| **Ports** | ✓ PASS | No collisions detected |
| **Naming** | ✓ PASS | 2 new identifiers: ep_v2_health, ep_v2_status |
| **Instructions** | ✓ PASS | .ai/instruct.md updated per Maintenance Rule |
| **Governance** | ✓ PASS | No violations detected |
| **Knowledge Sync** | ⚠ REBASE SUGGESTED | .ai/knowledge/ updated on main; rebase to sync |
| **CI/CD** | ✓ PASSING | 45/45 tests pass |

---

## Instruction Changes

If `.ai/instruct.md` or governance files modified:

```
**Governance Files Modified**:
- .ai/instruct.md: Updated API v2 section
- .ai/ports.md: Added port 8001 for api-v2

**Requires Approval From**:
- Curator (pds-man-curator) — .ai/instruct.md changes
- Naming Manager (pds-man-naming) — port registry entries
```

---

## Auto-Suggested Reviewers

Extract from `.ai/instruct.md` + governance files:

```markdown
**Required Approvals**:
- [ ] @alice (scope owner: api)
- [ ] @curator-team (instruction changes)
- [ ] @governance-lead (governance rule validation)

**Code Review** (min 1):
- @bob (familiar with api module)
- @charlie (last author of validation.py)
```

---

## Merge Strategy & Instructions

Based on branch strategy:

**GitHub Flow** (recommended):
```bash
# When approved, run:
git checkout main
git pull origin main
git merge --squash feature/api-versioning-456
git commit -m "<conventional-commit-message>"
git push origin main
git branch -d feature/api-versioning-456
```

**Git Flow** (if detected):
```bash
# When approved, run:
git checkout develop
git pull origin develop
git merge --no-ff feature/api-versioning-456
git commit -m "merge: feature/api-versioning-456"
git push origin develop
git branch -d feature/api-versioning-456
```

---

### 5. User Confirmation

Present summary:

```
✓ Pre-merge validation passed (6/6 checks)
✓ Auto-suggested reviewers loaded

Ready to create PR?

Options:
1. Create PR (push to origin, create PR on GitHub/GitLab)
2. Review PR locally first (--draft)
3. Cancel

Your choice: _
```

### 6. Create or Show PR

If user confirms:

1. **Draft PR**:
   ```bash
   git push -u origin feature/api-versioning-456
   ```

2. **Open PR** (manual on GitHub/GitLab, or auto via GitHub CLI if available):
   ```bash
   gh pr create \
     --title "<conventional-commit-summary>" \
     --body "<generated-pr-body>" \
     --base main \
     --head feature/api-versioning-456 \
     --reviewer <auto-suggested-reviewers> \
     --label governance,<scope>
   ```

3. **Report**:
   ```
   ✓ PR created: #789
   ✓ Target: main
   ✓ Reviewers notified: @alice, @curator-team, @governance-lead
   ✓ Labels: governance, api

   → Merge when all required approvals given.
   → Run /ai-pr --merge-check before merging.
   ```

### 7. Merge Gate Check (--merge-check)

Before merge, validate:

```bash
git log origin/main -1 --format="%ai" > main_tip_date
git log --oneline feature/api-versioning-456..origin/main
```

1. **Is main ahead of feature branch?**
   - If yes: suggest rebase + re-validate
   - If no: proceed
2. **All gates still passing?**
   - Re-run validators (1 min timeout)
3. **PAUSE file exists?** (`.ai/PAUSE`)
   - If yes: **BLOCK merge**; CI/CD blocks automatically
4. **PR approved by all required reviewers?**
   - Check GitHub/GitLab approval status
   - If not: **BLOCK** (governance requires approval)
5. **CI still passing?**
   - Query latest workflow
   - If failed since PR created: re-run or fail

If all pass: ✓ **Ready to merge**

### 8. Execute Merge (--rebase-and-merge)

User command (after all approvals):

```
/ai-pr --rebase-and-merge
```

1. **Fetch latest**:
   ```bash
   git fetch origin
   ```
2. **Rebase** (if needed):
   ```bash
   git rebase origin/main
   ```
3. **Merge**:
   - GitHub Flow: `git merge --ff-only origin/feature`
   - Or push button on GitHub/GitLab UI
4. **Post-merge**:
   - Release lock: delete `.ai/locks/<scope>.lock`
   - Delete branch: `git branch -d feature/api-versioning-456`
   - Trigger Curator post-merge tasks (index update, KB sync)
   - Alert team: "Scope `api` merged; lock released"

---

## Hard Rules

- **Never merge with failing validators.** All gates must PASS before merge.
- **Never merge governance file conflicts without manual review.** Conflicts in `.ai/instruct.md`, registries, or governance rules require explicit agent approval.
- **Never bypass PAUSE file.** If `.ai/PAUSE` exists, merge is blocked by CI/CD.
- **Never allow force-merge.** Use rebase-and-merge (linear history) or squash-and-merge, never force-push to main.
- **Always validate registries before merge.** Port and naming collisions must be resolved; Naming/Ports managers must approve.

---

## Failure Modes

| Failure | Action |
|---------|--------|
| **Port collision** | Report findings; suggest `/ai-ports-check` for details; require Port manager reconciliation |
| **Naming collision** | Report conflicts; require Naming manager Mode 4 reconciliation |
| **Instruction drift** | Require Curator approval; explain changes in PR comment |
| **Governance violation** | Report rule + source; ask if intentional; allow override with explanation |
| **Main ahead of feature** | Suggest rebase: `git rebase origin/main`; re-run validation |
| **CI failing** | Report failures; suggest re-running or fixing issues |
| **PAUSE file present** | Merge blocked; report who set PAUSE and why (if documented) |
| **Missing required approval** | List outstanding reviewers; show approval status |

---

## Integration

Called by:
- User: `/ai-pr`
- Supervisor: Pre-merge gate validation (calls version control agent)
- CI/CD: GitHub Actions / GitLab Pipeline pre-merge job

Calls:
- `pds-man-versioncontrol.agent.md` (pre-merge logic)
- `pds-pipe-reviewer.agent.md` (instruction drift check)
- `pds-man-naming.agent.md` (naming collision detection)
- `pds-man-ports.agent.md` (port collision detection)
- Git CLI (`git`, `gh` if available)

Reads:
- Git branch, commits, diffs
- `.ai/instruct.md` and governance files
- `.ai/locks/*` (scope metadata)
- `.ai/coding-prefixes.md`, `.ai/ports.md`, etc.
- GitHub/GitLab PR status (via API if available)

Creates:
- GitHub/GitLab PR (via UI or CLI)
- PR description with auto-generated metadata

---

## Examples

### Example 1: Simple Feature (GitHub Flow)

```
User: /ai-pr

AI: ✓ Pre-merge validation: 6/6 checks pass
    ✓ Ports: clean
    ✓ Naming: 2 new identifiers (no collision)
    ✓ Instructions: updated
    ✓ Governance: satisfied
    ✓ Knowledge: up-to-date
    ✓ CI/CD: passing

    Auto-suggested reviewers: @alice, @bob

    Create PR? (yes/no)

User: yes

AI: ✓ PR created: #789 (feature/api-versioning-456 → main)
    ✓ Reviewers notified

    → Wait for approvals, then run: /ai-pr --merge-check
```

### Example 2: Governance Files (Requires Curator)

```
User: /ai-pr

AI: ⚠️  Pre-merge validation: 5/6 checks pass

    ⚠️  INSTRUCTION DRIFT DETECTED
    - .ai/instruct.md: Added "API v2" section
    - Requires Curator approval

    Auto-suggested reviewers: @alice, @curator-team, @governance-lead

    Create PR? (yes/no)

User: yes

AI: ✓ PR created: #790
    ⚠️  Marked: [governance], [requires-curator-approval]
    ✓ @curator-team notified

    → Merge when all required approvals given (Curator approval required).
```

### Example 3: Naming Collision (Conflict)

```
User: /ai-pr

AI: ✗ Pre-merge validation: FAILED (4/6 checks)

    ✗ NAMING COLLISION DETECTED
    - Identifiers in feature branch: ep_health, ep_status
    - Already in main: ep_status (registered by @bob 2 days ago)
    - Collision: ep_status

    Resolution:
    1. Coordinate with Naming manager (@naming-team)
    2. Rename: feature branch's ep_status → ep_v2_status
    3. Update .ai/coding-prefixes.md
    4. Commit & push changes
    5. Re-run /ai-pr

    Create PR anyway (will block on merge)? (yes/no/resolve-first)

User: resolve-first

AI: Suggested fix:
    1. Run: /ai-audit-registries --scope api
    2. Naming manager will reconcile and suggest renaming
    3. Apply suggestions
    4. Retry /ai-pr
```

---

## See Also

- [`.ai/version-control.md`](../../.ai/version-control.md) — Branch strategies, merge policy
- [`/ai-branch`](ai-branch.prompt.md) — Create/manage feature branches
- [`/ai-commit`](ai-commit.prompt.md) — Local commit validation
- [`.github/agents/pds-man-versioncontrol.agent.md`](../../.github/agents/pds-man-versioncontrol.agent.md) — Core logic
- [`.github/agents/pds-pipe-reviewer.agent.md`](../../.github/agents/pds-pipe-reviewer.agent.md) — Instruction drift check

DEPRECATED-CONTENT-END -->
