---
description: 'Use after making changes to multiple files, refactoring architecture, or when documentation is out of sync — when a developer says "update all docs", "sync documentation", "refresh API docs", "update codebase docs", "docs are stale", or "check what docs need updating". Scans changed files and updates corresponding documentation in docs/apis/, docs/codebase/, docs/flows/, and docs/external-apis/.'
agent: 'ask'
---
# Sync Docs — Update Documentation After Code Changes

Automatically updates documentation to match recent code changes.

**Scope**: ${input:scope:What to sync? (all / apis / codebase / flows / issue)}

---

## What This Command Does

Analyzes recent changes and updates the corresponding documentation:

1. **Scans for changes**: Checks `git diff` or recent commits
2. **Identifies affected docs**: Maps changed code files to their docs
3. **Updates documentation**: Syncs field names, patterns, architecture
4. **Reports drift**: Shows what was out of sync and what was updated

---

## Sync Scopes

### Scope: `all` (default)
Syncs all documentation types:
- ✅ API docs (`docs/apis/`)
- ✅ Codebase knowledge (`docs/codebase/`)
- ✅ Flow docs (`docs/flows/`)
- ✅ External API docs (`docs/external-apis/`)

### Scope: `apis`
Only syncs internal API endpoint documentation:
- Scans `src/controllers/`, `src/api/`, `src/resolvers/`
- Updates corresponding `docs/apis/[domain]/[endpoint].api.md`
- Checks for:
  - New/removed fields in request/response
  - Changed status codes
  - Updated validation rules
  - New/removed endpoints

### Scope: `codebase`
Only syncs architectural documentation:
- Scans project structure changes
- Updates `docs/codebase/architecture.md`, `stack.md`, `structure.md`
- Checks for:
  - New dependencies added
  - Folder structure changes
  - New patterns introduced
  - Cross-cutting concerns changes

### Scope: `flows`
Only syncs user flow documentation:
- Scans for changed business logic
- Updates `docs/flows/[flow-name]-flow.md`
- Checks for:
  - New steps in flows
  - Changed decision points
  - Updated error paths

### Scope: `issue`
Syncs only the current Issue doc:
- Reads current branch Issue ID
- Updates Phase 4 execution notes
- Ensures commits are logged
- Marks completed tasks

---

## How It Works

### Step 1 — Detect Changes
```bash
# Get changed files since last sync
git diff --name-only HEAD~5..HEAD

# Or get staged changes
git diff --cached --name-only
```

### Step 2 — Map Files to Docs

| Changed File | Affected Doc |
|--------------|--------------|
| `src/api/auth/login.ts` | `docs/apis/auth/login.api.md` |
| `src/services/order.service.ts` | `docs/flows/order-flow.md` |
| `src/wrappers/dynamics-wrapper.ts` | `docs/external-apis/dynamics/README.md` |
| `src/transformers/account-transformer.ts` | `docs/external-apis/dynamics/accounts.api.md` |
| New folder `src/payments/` | `docs/codebase/structure.md` |

### Step 3 — Analyze Drift

For each doc, check:
- Field names in code vs. doc
- Function signatures vs. documented endpoints
- Folder structure vs. architecture diagram
- Dependencies in `package.json` vs. `docs/codebase/stack.md`

### Step 4 — Update Documentation

Update only the **out-of-sync sections**, preserving:
- Custom explanations
- Business context notes
- Examples and use cases
- Historical decision rationale

### Step 5 — Report

```
📝 Documentation Sync Report
─────────────────────────────────────────────────

🔍 Scanned: 12 changed files (last 5 commits)
📄 Affected docs: 4 files

Updates Made:
  ✅ docs/apis/auth/login.api.md
     - Added `rateLimitExempt` field to response
     - Updated 429 error condition
  
  ✅ docs/codebase/architecture.md
     - Added Redis caching layer
  
  ⚠️ docs/flows/auth-flow.md
     - Drift detected: rate limiting step missing
     - Action required: Manual review needed
  
  ✅ docs/external-apis/dynamics/accounts.api.md
     - Updated field mapping for `emailaddress1`

─────────────────────────────────────────────────

Summary:
  ✅ 3 docs auto-updated
  ⚠️ 1 doc needs manual review
  ⏭️ 0 docs skipped (no changes needed)

─────────────────────────────────────────────────
```

---

## When to Use This

| Scenario | When to Sync |
|----------|--------------|
| **After refactoring** | Sync `codebase` after architectural changes |
| **After adding API fields** | Sync `apis` after endpoint modifications |
| **After logic changes** | Sync `flows` when business logic updates |
| **Before PR** | Sync `all` to ensure docs are up to date |
| **After external API upgrade** | Sync external API docs when 3rd-party changes |
| **After task completion** | Sync `issue` to update execution notes |

---

## Safety Features

- ✅ **Never overwrites custom content** — only updates factual data sections
- ✅ **Creates git commit after sync** — easy to revert if needed
- ✅ **Shows diff before applying** — review changes first
- ✅ **Flags manual review items** — doesn't guess complex business logic

---

## Example Usage

**Scenario**: Just merged a feature branch that added rate limiting

```
You: /sync-docs apis
Copilot: 
  🔍 Scanning changed files...
  📄 Found 2 affected API docs
  
  Updating docs/apis/auth/login.api.md:
    + Added rate limiting section
    + Updated 429 error response
  
  ✅ Sync complete. Review changes:
  git diff docs/apis/
```

---

## Related Commands

- `/update-api-doc` — Update a single API doc manually
- `/generate-api-doc` — Create a new API doc from scratch
- `/verify` — Check if docs are in sync before merging
- `/status` — Check current Issue progress

---

## Configuration

Add to `.github/copilot-instructions.md` to customize sync behavior:

```markdown
## Doc Sync Conventions

- API docs: Always sync on endpoint changes
- Flow docs: Manual review required for business logic changes
- Codebase docs: Sync on package.json changes
- External API docs: Only sync on transformer changes
```
