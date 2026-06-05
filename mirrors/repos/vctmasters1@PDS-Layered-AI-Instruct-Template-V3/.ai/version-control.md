# Version Control — Branch Strategy, Scope Locking, Merge Policy

**Version**: 1.0.0
**Last Updated**: 2026-06-04
**Scope**: Team collaboration, branch coordination, merge governance

---

## Contents

| Section | Purpose |
|---------|---------|
| [Branch Strategy](#branch-strategy) | Detect and apply team's convention |
| [Scope Locking](#scope-locking) | Prevent concurrent modifications |
| [Merge Validation](#merge-validation) | Govern-aware pre-merge checks |
| [Registry Merge Strategy](#registry-merge-strategy) | Prevent naming collisions |
| [PR / Merge Request Workflow](#pr--merge-request-workflow) | Team review & coordination |
| [Conflict Resolution](#conflict-resolution) | Manual-first for governance files |

---

## Branch Strategy

The project supports three branch strategies. **Detect the team's convention** from repository configuration, then apply consistently.

### Detection Logic

Check (in order):
1. **GitHub Flow**: If only `main` branch exists with PR review requirement (GitHub Actions or branch protection) → use GitHub Flow
2. **Git Flow**: If `develop` branch exists + release branches (`release/*`) exist → use Git Flow
3. **Trunk-Based**: If commits go directly to `main` from `main` (no PR requirement) + short-lived feature branches → use Trunk-Based

### Strategy: GitHub Flow (Default for Open Source / Small Teams)

```
main ← (only via PR, requires approval)
  ↑
  └─ feature/* ← (short-lived, one per developer/task)
```

**Rules**:
- Feature branches: `feature/<scope>-<issue>` or `feature/<issue>-<brief-name>` (max 50 chars)
- Always PR to `main`; never direct push
- Require minimum 1 review before merge
- Delete branch after merge
- Link scope governance refs in PR description

**When to use**: Most teams, especially with distributed developers or code review requirements.

### Strategy: Git Flow (For Coordinated Releases)

```
main (production releases only)
  ↑
  ├─ release/* (release prep, versioning)
  │   ↑
  │   └─ hotfix/* (production bugs)
  │
develop (integration branch)
  ↑
  └─ feature/* (feature development)
```

**Rules**:
- Feature branches: `feature/<scope>-<issue>` from `develop`
- Release branches: `release/v<version>` from `develop`; merges back to `main` + `develop`
- Hotfix branches: `hotfix/v<version>-<brief>` from `main`; merges to `main` + `develop`
- Require CI pass before merge
- Versioning: Semantic (major.minor.patch) in `package.json`, `version.txt`, or similar

**When to use**: Projects with scheduled releases, documentation coordination, or multiple stable versions.

### Strategy: Trunk-Based Development (High Velocity)

```
main (always production-ready)
  ↑
  └─ short-lived feature branches (max 2-3 days)
```

**Rules**:
- Feature branches live < 72 hours
- Merge to `main` via simple commit (can use feature flags in code)
- No separate release branch; releases cut from `main` tags
- Requires strong CI/CD and automated rollback capability

**When to use**: Microservices, rapid iteration teams, or continuous deployment.

---

## Scope Locking

**Prevent concurrent modifications to the same scope** by the same or different developers/agents.

### Lock Mechanism

Use lightweight metadata-based locking (not file system locks):

1. **Branch-based detection** (lightweight):
   - Parse current branch name: `feature/<scope>-<issue>`
   - Extract `<scope>` (e.g., `api`, `db`, `validation`)
   - Query: `git branch -r | grep <scope>` → list branches working on that scope
   - If multiple branches found (not current), alert: "Scope `api` is already in progress on `feature/api-caching-#123`; coordinate before proceeding"

2. **Git metadata-based locking** (optional, stronger):
   - Create `.ai/locks/<scope>.lock` file (gitignored)
   - Format: `{ scope, branch, developer, timestamp, status: "in-progress" }`
   - Before entering Supervisor pipeline on a scope, create lock (developer-scoped)
   - After merge or cancel, delete lock
   - Read lock before proceeding: if stale (>24h), warn and offer to release; if fresh, block

3. **GitHub / GitLab Issues integration** (optional, strongest):
   - Create linked issue: `Lock: <scope>` with developer assignment
   - Query API before proceeding; if assigned to someone else, block
   - Auto-close when PR merged

**Recommendation**: Start with (1) branch-based detection; upgrade to (2) for teams > 5; use (3) for distributed teams.

### Lock Metadata Schema (`.ai/locks/<scope>.lock`)

```yaml
scope: "api"
branch: "feature/api-versioning-#456"
developer: "alice@example.com"
started: "2026-06-04T10:30:00Z"
status: "in-progress"  # in-progress | waiting-review | ready-to-merge
pipeline_stage: "3-validate"  # Stage name if in pipeline
```

---

## Merge Validation

**Pre-merge checks** that must pass before a PR/merge is allowed:

| Check | Trigger | Severity |
|-------|---------|----------|
| **Instruction drift** | Any `.ai/instruct.md` or governance file changed | BLOCK if unresolved |
| **Naming registry collisions** | Any two branches register same identifier | BLOCK |
| **Port collisions** | Any two branches claim same port | BLOCK |
| **Governance ref violations** | Change violates a governance rule from shallower scope | BLOCK |
| **Index staleness** | `.ai/index.md` not updated with new files | WARN (not blocking) |
| **Knowledge sync** | `.ai/knowledge/` diverged from main during branch | WARN (suggest rebase) |
| **CI/CD status** | Build, lint, test failures | BLOCK (per GitHub/GitLab config) |

### Validation Flow

```
1. Pre-commit validation (local, before push)
   ├─ Port collision check
   ├─ Naming registry check
   └─ Governance violation check

2. Pre-merge validation (in PR/MR, before approval)
   ├─ Instruction drift check (automatic)
   ├─ Naming registry reconciliation (if conflicts)
   ├─ Knowledge sync status (warning)
   └─ CI/CD status (GitHub/GitLab native)

3. Pre-merge conflict resolution
   ├─ Rebase check: `git merge-base` against target branch
   ├─ Conflict summary: files affected
   └─ Governance file conflicts: require manual merge + review
```

---

## Registry Merge Strategy

**Never silently overwrite naming or port registries.**

### Strategy: Collaborative Merge (for registries)

When merging branches that both modified `.ai/coding-prefixes.md`, `.ai/ports.md`, etc.:

1. **Identify conflict regions** (lines added on both sides)
2. **Check for collisions**:
   - Same identifier registered twice → CONFLICT (manual review required)
   - Same port registered twice → CONFLICT (manual review required)
   - Additions in different parts → OK, merge as-is
3. **Merge strategy**:
   ```bash
   git merge -X theirs <branch>  # Accept incoming, then verify manually
   ```
4. **Validation**: Curator runs `naming Mode 4 (audit-registries)` post-merge to reconcile; flags collisions

### Merge Commit Message

For registry merges, require explicit message:

```
merge: reconcile naming registries from feature/<scope>

Resolved conflicts in:
- .ai/coding-prefixes.md: added endpoints ep_v2_*, conflict with ep_* from main
- .ai/ports.md: no conflicts

Naming Mode 4 reconciliation performed; see curator log.
```

---

## PR / Merge Request Workflow

### PR Checklist (Template)

Auto-generate in PR description:

```markdown
## Scope & Governance
- [ ] Scope path: `<scope_path>`
- [ ] Governance refs applied: `<list>`
- [ ] Instruction files updated: `<list>`
- [ ] Breaking changes: None / Yes (describe)

## Validation Status
- [✓/✗] Port registry clean (auto-checked)
- [✓/✗] Naming registries reconciled (auto-checked)
- [✓/✗] Governance rules satisfied (auto-checked)
- [✓/✗] CI/CD passing (auto-checked)
- [✓/✗] Knowledge sync current (auto-checked)

## Reviewers
- Scope owners: `@alice, @bob` (auto-suggested)
- Governance custodians: `@charlie` (auto-suggested from governance refs)
- Code reviewers: `<manual>`

## Merge Strategy
- Branch strategy: GitHub Flow (auto-detected)
- Rebase and merge recommended: `true`
- Delete branch after merge: `true`
```

### PR Approval Rules

| Condition | Rule |
|-----------|------|
| **Template infrastructure** (`.github/`, `.ai/`) | Requires approval from **Curator** |
| **Governance-affected** (scope has governance ref) | Requires approval from **governance custodian** |
| **Naming registry modified** | Requires approval from **naming agent** (pds-man-naming) |
| **Instruction drift detected** | **Reviewer** (pds-pipe-reviewer) must approve resolution |
| **Port/naming collision** | **Port/naming managers** must approve reconciliation |
| **All other changes** | Requires min 1 code review (GitHub/GitLab standard) |

### Merge Gates

| Gate | Check | Action |
|------|-------|--------|
| **Pre-merge** | PAUSE file exists | BLOCK merge; CI blocks automatically |
| **Pre-merge** | Conflicts in governance files | BLOCK; require manual resolution + review |
| **Pre-merge** | Naming collision unresolved | BLOCK; require Curator approval |
| **Post-merge** | Index staleness detected | Auto-trigger `/ai-update-index` in next commit |
| **Post-merge** | KB divergence detected | Auto-rebase KB from main; alert developer |

---

## Conflict Resolution

### Conflict Types & Handling

| Conflict Type | Files | Strategy | Resolution |
|---|---|---|---|
| **Non-governance code** | `src/**`, `api/**`, `db/**` | Rebase or 3-way merge | Developer resolves; bot can suggest trivial merges |
| **Governance files** | `.ai/instruct.md`, `.ai/*-conventions.md` | Manual merge + review | Reviewer (pds-pipe-reviewer) must approve |
| **Naming registries** | `.ai/coding-prefixes.md`, `.ai/ports.md`, etc. | Collision check + manual reconciliation | Naming/Port managers must reconcile + approve |
| **Knowledge base** | `.ai/knowledge/**` | Last-write-wins + rebase | Auto-merge favoring main; alert KB custodian |
| **Index** | `.ai/index.md` | Rebase + rebuild | Auto-trigger `/ai-update-index` post-merge |

### Rebase vs. Merge

| Scenario | Preferred | Why |
|----------|-----------|-----|
| Feature branch (GitHub Flow) | **Rebase** | Linear history, clean |
| Integration branch (Git Flow) | **Merge** | Preserves feature history |
| Hotfix to main | **Rebase** | Linear, auditable |
| Release prep | **Merge** | Intentional integrations |
| Conflict resolution | **Rebase** (if possible) | Cleaner than merge commits |

**Default**: Rebase + squash for feature branches; preserve merge commits for integration branches.

---

## Lock Release & Timeout

- **Manual lock release**: After merge, lock deleted automatically
- **Timeout-based release**: If lock.started > 24h old and status != "ready-to-merge", warn developer; offer to release after confirmation
- **Stale lock cleanup**: `/ai-git branch --release-stale` removes locks older than 72h (with audit log)

---

## Team Communication

### Lock Notification

When scope locked by another developer:

```
⚠️  Scope 'api' is in progress on feature/api-versioning-#456 (alice@example.com, started 2h ago).

Options:
1. Coordinate with alice; rebase to avoid conflicts
2. Wait for PR to merge (alice's PR: #789, awaiting review)
3. Force-release lock (requires permission; leaves audit trail)
```

### Pre-Merge Notification

When merging with governance implications:

```
✓ PR #789 ready to merge
  - Scope: api
  - Governance: strict (requires Curator + Compliance approval)
  - Reviewers needed: @curator, @compliance-lead
  - Estimated review time: 2-4 hours
```

---

## Integration with Agent System

### Agents Involved

| Agent | Role |
|-------|------|
| `pds-man-versioncontrol` | Coordinates branch strategy, lock mgmt, merge validation |
| `pds-pipe-reviewer` | Validates instruction drift before merge |
| `pds-man-naming` | Reconciles naming registry conflicts |
| `pds-man-ports` | Reconciles port registry conflicts |
| `pds-man-curator` | Applies post-merge cleanup (index, KB sync) |
| GitHub / GitLab CI | Runs tests, blocks on PAUSE file |

### Hooks

- **Pre-push**: Call version control agent to validate (no force-push allowed)
- **Pre-merge** (PR approval): Validate all gates; block if failed
- **Post-merge**: Curator syncs `.ai/knowledge/`, rebases KB, updates index if needed

---

## Configuration

### `.github/dev-specs.md` Additions

```yaml
branch_strategy: github-flow  # github-flow | git-flow | trunk-based
scope_locking: branch-detection  # branch-detection | metadata | github-issues
lock_timeout_hours: 24
require_pr_approval: true
require_scope_owner_review: true  # for scope-specific changes
rebase_preferred: true  # true for GitHub Flow; false for Git Flow
squash_on_merge: true  # squash commits for cleaner history
```

### `.ai/locks/.gitkeep`

Directory for scope locks (gitignored by default).

---

## Related Files

- [`.ai/maintenance.md`](maintenance.md) — Archive & cleanup rules
- [`.ai/environment.md`](environment.md) — Host isolation; relevant for CI/deploy gates
- [`.ai/conventions.md`](conventions.md) — Naming rules; relevant for branch naming
- [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) — Meta rules
- [`.github/prompts/ai-git.prompt.md`](../.github/prompts/ai-git.prompt.md) — Version control workflow (subcommands: `branch | commit | pr | status`)

---

## Examples

### Example 1: GitHub Flow — Two Developers

**Alice** on `feature/api-versioning-#456`:
- Locks scope `api` (branch detection)
- Modifies `.ai/ports.md` (adds `8001` for v2)
- Creates PR → Requires Curator approval (instruction file modified)

**Bob** starts feature `feature/db-migration-#457`:
- Tries to lock scope `db`
- Lock succeeds (different scope)
- No conflict with Alice

**When Alice's PR merges**:
- Lock auto-released
- Curator runs post-merge KB sync
- Curator auto-updates `.ai/index.md` if needed

### Example 2: Git Flow — Release Prep

**Alice** on `develop`:
- Coordinates: "I'm cutting release/v2.0.0"
- Creates `release/v2.0.0` from `develop`
- Modifies version in `package.json`, `CHANGELOG.md`
- PR to `main` + `develop`; requires Curator approval
- Merge: `--no-ff` to preserve release history

---

## References

- **GitHub Flow**: https://guides.github.com/introduction/flow/
- **Git Flow**: https://nvie.com/posts/a-successful-git-branching-model/
- **Trunk-Based Development**: https://trunkbaseddevelopment.com/
- **Conventional Commits**: https://www.conventionalcommits.org/
