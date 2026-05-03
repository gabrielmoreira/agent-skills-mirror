---
type: skill
lifecycle: stable
name: release-process
description: Complete release automation for VS Code Marketplace publishing
tier: standard
applyTo: '**/*release*,**/*publish*,**/*.vsix,**/CHANGELOG*'
inheritance: master-only
currency: 2026-04-22
lastReviewed: 2026-01-01
---

# Release Process Skill

**Inheritance**: master-only (contains PAT handling, marketplace credentials)

---

## Purpose

Comprehensive knowledge for releasing Alex Cognitive Architecture to VS Code Marketplace and managing version lifecycle.

---

## Quick Reference

### Release Commands

```bash
# From repo root
node scripts/release-vscode.cjs                           # Stable release
node scripts/release-vscode.cjs --pre-release              # Pre-release
node scripts/release-vscode.cjs --dry-run                  # Test without publishing
```

### Manual Publishing

```bash
cd platforms/vscode-extension
npx vsce publish --pre-release  # Pre-release
npx vsce publish                # Stable release
```

---

## PAT (Personal Access Token) Setup

> ⚠️ **IMPORTANT**: PATs expire frequently and may only work for a single publish session.
> Always create a fresh PAT before each release to avoid 401 errors.

### Creating a New PAT

1. **Via Marketplace** (Recommended):
   - Go to: <https://marketplace.visualstudio.com/manage/publishers/>
   - Click your publisher name
   - Click "..." menu → "Generate new token"
   - Copy the token immediately (shown only once)

2. **Via Azure DevOps**:
   - Go to: <https://dev.azure.com/>
   - Click User Settings (gear icon) → Personal Access Tokens
   - Click "New Token"
   - Name: `vsce-marketplace` (or similar)
   - Organization: `All accessible organizations`
   - Expiration: Set appropriate duration (max 1 year)
   - Scopes: Select `Marketplace` → `Manage`
   - Click Create, copy token

### Storing the PAT

**Option 1: Environment Variable** (Session only)

```powershell
$env:VSCE_PAT = "your-token-here"
```

**Option 2: .env File** (Persistent, gitignored)

```
# Root .env (AlexMaster/.env)
VSCE_PAT=your-token-here
```

> The release scripts read `VSCE_PAT` from the environment or from root `.env`.

**Option 3: System Environment** (Persistent)

```powershell
[Environment]::SetEnvironmentVariable("VSCE_PAT", "your-token", "User")
```

### PAT Troubleshooting

| Error            | Cause                  | Solution                                               |
| ---------------- | ---------------------- | ------------------------------------------------------ |
| 401 Unauthorized | PAT expired or invalid | Create new PAT                                         |
| 401 Unauthorized | Wrong scope            | Ensure "Marketplace (Manage)" scope                    |
| 401 Unauthorized | `.env` not found       | Ensure root `.env` has the token                       |
| 403 Forbidden    | Not publisher owner    | Check publisher membership                             |
| Token not found  | .env not loaded        | Check file path, run preflight                         |

### Retry After PAT Fix

When publish fails with 401 and you've already built a valid `.vsix`, skip the full prepublish cycle:

```powershell
# Set new PAT and publish pre-built package (skips sync/quality-gate/compile)
$env:VSCE_PAT = "new-token"; npx vsce publish --packagePath alex-cognitive-architecture-X.Y.Z.vsix
```

This saves ~2 minutes vs a full `npx vsce publish` which re-runs the entire prepublish pipeline.

---

## Version Strategy

### Semantic Versioning

```
MAJOR.MINOR.PATCH
  │     │     └── Bug fixes, docs
  │     └──────── New features, non-breaking
  └────────────── Breaking changes
```

### Pre-Release vs Stable

| Type        | Flag            | Visibility  | Use Case         |
| ----------- | --------------- | ----------- | ---------------- |
| Pre-release | `--pre-release` | Opt-in only | Beta testing     |
| Stable      | (none)          | Everyone    | Production ready |

**VS Code Marketplace Rule**: Pre-release versions must use the `--pre-release` flag, NOT semver suffixes like `-beta.1`.

### Version Files to Update

When bumping version, these files need synchronization:

1. `platforms/vscode-extension/package.json` → `version` field
2. `platforms/vscode-extension/.github/copilot-instructions.md` → `**Version**:` line
3. `CHANGELOG.md` → New `## [X.Y.Z]` section

The `release-vscode.cjs` script handles all of these automatically.

### Version Bump Decision Table

| Condition | Bump Type | Rationale |
|-----------|-----------|-----------|
| Breaking API change (removed command, renamed setting, changed data format) | **Major** | Users must adapt their workflows |
| New user-facing feature (command, setting, UI element) | **Minor** | Additive capability, no breakage |
| Bug fix for existing behavior | **Patch** | Same features, better quality |
| Documentation-only changes (README, wiki, CHANGELOG wording) | **Patch** | No runtime behavior change |
| Internal refactor with no user-visible change | **Patch** | Ship quality improvements incrementally |
| New brain skill / instruction / prompt (no extension change) | **Minor** | New cognitive capability available |
| Brain file content update (currency stamps, decision tables, typos) | **Patch** | Maintenance, no new capability |
| Security fix (dependency bump, input validation) | **Patch** | Ship ASAP, minimize version noise |
| Deprecation of existing feature (still works, marked for removal) | **Minor** | Users need warning before removal |
| Multiple features + fixes in same release | **Minor** | Highest-impact change determines bump |
| Heir sync format change (breaks older upgrade-brain.cjs) | **Major** | Fleet-breaking change |
| Pre-release / beta testing | **Minor + `--pre-release`** | Use marketplace pre-release flag, not semver suffix |

---

## Release Workflow

### Automated (Recommended)

```
┌─────────────────────────────────────────────────────────────────┐
│  node scripts/release-vscode.cjs --pre-release                   │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ 0. PAT Check    │───▶│ 1a. Sync Heir   │───▶│ 1b. Preflight   │
│ - Load .env     │    │ - build-pkg.ps1 │    │ - Version sync  │
│ - Validate      │    │ - Master→Heir   │    │ - Build/Lint    │
│                 │    │                 │    │ - Manifest check│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ 2. Version Bump │───▶│ 3. CHANGELOG    │───▶│ 4. Git Commit   │
│ - package.json  │    │ - Add entry     │    │ - Commit        │
│ - heir version  │    │ - Date stamp    │    │ - Tag           │
│                 │    │                 │    │ - Push          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐
│ 5. Publish      │
│ - vsce publish  │
│ - --pre-release │
└─────────────────┘
```

### Definition of Done Verification

**Before publishing**, verify ALL 8 criteria from ROADMAP.md:

| #   | Criterion                  | Validation Method                                                 |
| --- | -------------------------- | ----------------------------------------------------------------- |
| 1   | Builds clean               | `npm run compile` exits 0 with zero errors                        |
| 2   | No dead code               | All imports resolve, no orphaned modules                          |
| 3   | Counts match reality       | Slash commands, tools, skills, trifectas in docs = actual code    |
| 4   | F5 smoke test passes       | Extension activates, welcome view renders, 3 random commands work |
| 5   | Version aligned            | package.json = CHANGELOG = copilot-instructions                   |
| 6   | Heir sync clean            | `sync-architecture.cjs` runs with 0 errors, no contamination      |
| 7   | No non-functional features | If in UI/command palette, it works. If broken, removed.           |
| 8   | CHANGELOG documents delta  | Every user-visible change has a line item                         |

**Pattern**: Use regression checklist as DoD tracker:

- Create a regression checklist (e.g., `VXXX-REGRESSION-CHECKLIST.md`)
- Track verification status for each criterion
- Document evidence (commit hashes, test counts, sync output)
- Automated tests provide objective quality signal (test count = confidence metric)

**Quality Gate**: If ANY criterion fails, DO NOT publish. Fix first.

### Manual Checklist

If not using the script:

- [ ] Run preflight: `node scripts/release-preflight.cjs`
- [ ] Bump version in `package.json`
- [ ] Update heir `copilot-instructions.md` version
- [ ] Add CHANGELOG entry
- [ ] Commit: `git commit -m "chore: release vX.Y.Z"`
- [ ] Tag: `git tag vX.Y.Z`
- [ ] Push: `git push && git push --tags`
- [ ] Publish: `npx vsce publish [--pre-release]`

---

## Preflight Checks

The `release-preflight.cjs` script validates:

| Check              | What It Does                                                       |
| ------------------ | ------------------------------------------------------------------ |
| PAT                | Verifies VSCE_PAT is available in env or .env                      |
| Version Sync       | package.json = CHANGELOG = Master instructions = heir instructions |
| BUILD-MANIFEST     | Checks heir was synced recently (warns if > 24h old)               |
| README Skill Count | Verifies documented skill count matches actual                     |
| ROADMAP Version    | Warns if ROADMAP.md version differs                                |
| Build              | `npm run compile` succeeds                                         |
| Lint               | `npm run lint` passes                                              |
| Tests              | `npm test` passes (can skip with `-SkipTests`)                     |
| Git Status         | Shows uncommitted changes                                          |
| Git Tags           | Warns if tag already exists                                        |
| Package            | Creates VSIX (with `-Package` flag)                                |

---

## File Structure

```
Alex_Plug_In/
├── scripts/
│   ├── release-preflight.cjs    # Pre-release validation
│   ├── release-vscode.cjs       # Full release automation
│   └── build-extension-package.ps1  # Heir sync
├── platforms/vscode-extension/
│   ├── package.json             # Version source of truth
│   ├── .env                     # PAT storage (gitignored)
│   ├── .github/
│   │   └── copilot-instructions.md  # Heir version
│   └── *.vsix                   # Built packages
└── CHANGELOG.md                 # Version history
```

---

## Common Issues

### "The pre-release version is not valid"

**Cause**: Used semver suffix like `3.7.4-beta.1`

**Solution**: Use plain version `3.7.4` with `--pre-release` flag

### "401 Unauthorized"

**Cause**: PAT expired, invalid, or wrong scope

**Solution**:

1. Create new PAT at marketplace.visualstudio.com/manage/publishers
2. Ensure "Marketplace (Manage)" scope
3. Update .env or environment variable

### "Version already exists"

**Cause**: Trying to publish same version twice

**Solution**: Bump version first, or delete existing version from marketplace

### Build succeeds but publish fails

**Cause**: Often network or auth issues

**Solution**:

1. Check internet connection
2. Verify PAT is valid
3. Try `npx vsce login <publisher-name>` first

---

## Post-Publish Verification Decision Table (RP4)

After `vsce publish` or `release-full.cjs` succeeds mechanically, the listing must be verified semantically. This table separates "did the CLI succeed?" (mechanical) from "does the marketplace represent what we shipped?" (semantic).

| # | Check | Pass | Fail | Action on Fail |
|---|-------|------|------|----------------|
| 1 | **Version match** — marketplace version matches `package.json` version | Versions are identical | Mismatch (stale cache or publish failure) | Wait 5 min for CDN propagation; if still mismatched, investigate publish logs |
| 2 | **README rendering** — marketplace README renders without broken images or layout | All images load; headings, tables, badges display correctly | Broken images, raw markdown visible, or layout collapse | Fix image URLs (must be absolute `https://` for marketplace); republish |
| 3 | **Changelog current** — marketplace changelog shows the new version's entry | Latest entry matches shipped version | Missing entry or shows prior version | Update CHANGELOG.md; republish |
| 4 | **Feature list accuracy** — listed features match what's actually in this version | All advertised features are functional | Feature listed but not yet shipped, or shipped but unlisted | Update README feature section; republish if misleading |
| 5 | **Activation events** — extension activates on documented events without errors | Clean activation, no console errors | Activation fails or throws on documented trigger | Debug activation; file hotfix release if blocking |
| 6 | **Dependencies declared** — `extensionDependencies` in package.json matches actual runtime needs | All required extensions listed; no phantom deps | Extension fails because a dependency isn't declared | Add missing dependency; republish |
| 7 | **Min VS Code version** — `engines.vscode` matches features used | Extension works on declared minimum version | Uses API unavailable in declared minimum | Bump `engines.vscode` or remove the newer API call |
| 8 | **No credential leak** — published VSIX contains no tokens, keys, or `.env` files | `.vscodeignore` excludes sensitive files; VSIX contents verified | Sensitive file found in VSIX | Yank the release immediately; rotate credentials; republish |
| 9 | **Size sanity** — VSIX size is within expected range (not bloated) | Size within 2x of previous release | Size doubled or more without explanation | Check for accidentally bundled `node_modules`, test fixtures, or media |
| 10 | **Install + activate smoke test** — fresh install from marketplace activates cleanly | Install from marketplace → activate → no errors in Output channel | Crash, missing dependency, or activation timeout | Debug with `--verbose`; file hotfix if blocking |

**Automation note**: Rows 1, 3, 7, 8, 9 can be checked mechanically (add to `release-smoke.test.cjs`). Rows 2, 4, 5, 6, 10 require human or LLM review.

## Links

- [VS Code Publishing Guide](https://code.visualstudio.com/api/working-with-extensions/publishing-extension)
- [Marketplace Publisher Portal](https://marketplace.visualstudio.com/manage/publishers/)
- [Azure DevOps PAT Docs](https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate)
- [VSCE CLI Reference](https://github.com/microsoft/vscode-vsce)
