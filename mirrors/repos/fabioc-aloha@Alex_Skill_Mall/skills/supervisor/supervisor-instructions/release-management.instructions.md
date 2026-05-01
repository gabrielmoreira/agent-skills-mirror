---
type: instruction
lifecycle: stable
description: "Release and publish workflows for versioning, changelogs, and marketplace deployment"
application: "During deployment, release preparation, or publishing workflows"
applyTo: "**/*{CHANGELOG,package,version}*,**/*.vsix"
inheritance: master-only
currency: 2026-04-22
lastReviewed: 2026-01-01
---

# Release Management Procedural Memory

---

## MANDATORY Pre-Release Assessment

**⚠️ CRITICAL**: Before ANY release action, Alex MUST automatically perform these assessments:

### Step 0: Brain QA (Cognitive Architecture Health)

```text
Action: Run `brain-qa` skill or architecture validation
Purpose: Ensure complete frontmatter, all skills indexed, Master-Heir sync
Output: 6-phase validation report
Blocker: Do NOT proceed if critical issues found
```

### Step 1: Detect Uncommitted Changes

```text
Action: Run `get_changed_files` tool
Purpose: Identify ALL modifications since last commit
Output: List of added/modified/deleted files with diffs
```

### Step 2: Assess Version Bump Requirement

**Analyze changes and recommend version bump type:**

| Change Type        | Examples                                         | Version Bump      |
| ------------------ | ------------------------------------------------ | ----------------- |
| Bug fixes only     | Fix typo, correct logic error                    | **patch** (0.0.X) |
| New features       | New command, new file, new capability            | **minor** (0.X.0) |
| Breaking changes   | API change, removed feature, incompatible update | **major** (X.0.0) |
| Documentation only | README update, comments                          | **none** or patch |

**Assessment Output Format:**

```
📊 Change Analysis:
- Files modified: X
- Files added: X
- Files deleted: X

🔄 Recommended Version Bump: [patch/minor/major]
Reason: [Brief explanation based on change types detected]

Current version: X.Y.Z
Proposed version: X.Y.Z
```

### Step 3: Generate Changelog Entry

**Automatically draft CHANGELOG entry based on changes:**

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added

- [Auto-detected from new files/features]

### Changed

- [Auto-detected from modified files]

### Fixed

- [Auto-detected from bug-fix patterns]

### Removed

- [Auto-detected from deleted files]
```

**Changelog Classification Rules:**

- New `.instructions.md` file → "Added" + "New procedural memory for X"
- New `.prompt.md` file → "Added" + "New episodic workflow for X"
- New skill folder → "Added" + "New skill for X"
- Modified existing file → "Changed" + describe the modification
- Deleted file → "Removed" + note what was removed
- Fix in code → "Fixed" + describe what was corrected

### Step 4: Present Findings to User

**Required Output:**

1. Summary table of changes
2. Recommended version bump with justification
3. Draft changelog entry for review
4. Ask: "Should I update the version and changelog, or would you like to adjust anything?"

### Step 4.5: Adversarial Validation Gate

**🔴 MANDATORY for Marketplace releases**

Before proceeding with version bump and publish:

```text
Action: Handoff to Validator agent for release review
Scope: All changes since last release + release artifacts
Deliverable: Validation report with ✅ approve / 🔴 block decision

Blocker: If Validator blocks (🔴 Critical or 🟠 High issues), resolve before proceeding.
```

**Validator Review Checklist:**

- [ ] CHANGELOG accurately reflects all changes
- [ ] Version bump matches change scope (patch/minor/major)
- [ ] No uncommitted changes or merge conflicts
- [ ] Documentation updated for user-facing changes
- [ ] No security regressions or exposed secrets
- [ ] Heir sync verified (if multi-platform release)
- [ ] Build artifacts clean (no errors, lint warnings acceptable)

**Expedited Validation** (emergency hotfix only):

- Limited to critical security OR production-down fixes
- Minimum viable scope (< 50 lines)
- Post-merge full validation scheduled
- Override documented in commit/CHANGELOG

See [.github/instructions/adversarial-oversight.instructions.md] for complete Validator integration protocol.

---

## Gate Check Questions (After Assessment)

1. "Based on the changes, I recommend version bump to X.Y.Z. Does this look right?"
2. "Here's the draft changelog entry. Any additions or corrections?"
3. "Ready to proceed with the release checklist?"

### If User Says "Just Publish" or Tries to Skip

**Response Protocol**:

> "I understand the urgency, but our release process exists to prevent issues that have bitten us before. Let me quickly run through the critical items - it'll only take 2 minutes and could save hours of rollback pain."

Then walk through the **Critical Path Items** below.

---

## Critical Path Items (Non-Negotiable)

These MUST be verified before releasing:

| Item                     | File                          | Check Command     |
| ------------------------ | ----------------------------- | ----------------- |
| Version consistency      | package.json                  | `npm version`     |
| TypeScript compiles      | -                             | `npm run compile` |
| Changelog updated        | CHANGELOG.md                  | Visual review     |
| No lint errors           | \*.md                         | `get_errors` tool |
| Temporary skills handled | .github/skills/\*/SKILL.md    | See below         |

**PowerShell replacement pitfall**:

- When using `-replace` with backreferences like `$1` and appending a version string, do not concatenate naively if the version starts with a digit.
- Prefer `${1}${version}`, a replacement callback, or `'{0}{1}' -f $matches[1], $version` style construction.
- Example failure: `'$1' + $version` can become ambiguous and produce malformed version updates.

---

## Definition of Done Verification

**⚠️ MANDATORY**: Before marking ANY version as "✅ Shipped", verify ALL 8 criteria:

| #   | Criterion                         | Verification Method                                                              | Blocker If Failed |
| --- | --------------------------------- | -------------------------------------------------------------------------------- | ----------------- |
| 1   | **Builds clean**                  | `npm run compile` exits 0 with zero errors                                       | 🔴 YES            |
| 2   | **No dead code**                  | Every import resolves, every export is consumed, no orphaned modules             | 🟡 Review         |
| 3   | **Counts match reality**          | Slash commands, tools, skills, trifectas in docs match actual code               | 🟡 Review         |
| 4   | **F5 smoke test passes**          | Extension activates in sandbox, welcome view renders, 3 random commands work     | 🟠 Recommended    |
| 5   | **Version aligned**               | package.json, CHANGELOG, copilot-instructions.md all show the same version       | 🔴 YES            |
| 6   | **Heir sync clean**               | `sync-to-heir.cjs` runs with 0 errors, heir activates independently              | 🔴 YES            |
| 7   | **No non-functional features**    | If it's in the UI or command palette, it works. If it doesn't work, it's removed | 🟠 Recommended    |
| 8   | **CHANGELOG documents the delta** | Every user-visible change has a line item                                        | 🔴 YES            |

**Principle**: Ship what works. Remove what doesn't. Document what changed.

### DoD Verification Script (Optional)

```powershell
# Quick DoD checklist
function Test-DefinitionOfDone {
  Write-Host "📋 Definition of Done Verification" -ForegroundColor Cyan

  # 1. Builds clean
  Write-Host "`n1. Build Status..." -ForegroundColor Yellow
  npm run compile 2>&1 | Tee-Object -Variable buildOutput
  if ($LASTEXITCODE -eq 0) { Write-Host "   ✅ Builds clean" -ForegroundColor Green }
  else { Write-Host "   ❌ Build errors detected" -ForegroundColor Red; return $false }

  # 5. Version aligned
  Write-Host "`n5. Version Alignment..." -ForegroundColor Yellow
  $pkgVersion = (Get-Content package.json | ConvertFrom-Json).version
  $changelogVersion = (Select-String -Path CHANGELOG.md -Pattern '\[(\d+\.\d+\.\d+)\]' | Select-Object -First 1).Matches.Groups[1].Value
  $brainVersion = (Select-String -Path .github/copilot-instructions.md -Pattern '# Alex v(\d+\.\d+\.\d+)' | Select-Object -First 1).Matches.Groups[1].Value

  if ($pkgVersion -eq $changelogVersion -and $pkgVersion -eq $brainVersion) {
    Write-Host "   ✅ Version aligned: $pkgVersion" -ForegroundColor Green
  } else {
    Write-Host "   ❌ Version mismatch: package=$pkgVersion, changelog=$changelogVersion, brain=$brainVersion" -ForegroundColor Red
    return $false
  }

  # 8. CHANGELOG updated
  Write-Host "`n8. CHANGELOG Updated..." -ForegroundColor Yellow
  $latestEntry = Select-String -Path CHANGELOG.md -Pattern '\[(\d+\.\d+\.\d+)\].*(\d{4}-\d{2}-\d{2})' | Select-Object -First 1
  if ($latestEntry) { Write-Host "   ✅ Latest entry: $latestEntry" -ForegroundColor Green }
  else { Write-Host "   ❌ No recent CHANGELOG entry" -ForegroundColor Red; return $false }

  Write-Host "`n⚠️  Manual verification required for criteria 2, 3, 4, 6, 7" -ForegroundColor Yellow
  return $true
}
```

**When to Run**: Before updating roadmap status from "📋 Planned" → "✅ Shipped"

### Temporary Skills Check

**⚠️ Before stable releases**, verify temporary skills are excluded:

```powershell
# Find temporary skills by checking SKILL.md frontmatter
Get-ChildItem .github/skills/*/SKILL.md | ForEach-Object {
  $content = Get-Content $_ -Raw
  if ($content -match 'temporary:\s*true') {
    Write-Warning "TEMPORARY SKILL: $($_.Directory.Name) - exclude from stable release"
  }
}
```

| Release Type          | Action                       |
| --------------------- | ---------------------------- |
| Beta (`X.Y.Z-beta.N`) | Include temporary skills     |
| Stable (`X.Y.Z`)      | **EXCLUDE** temporary skills |

---

## Release Workflow

### Phase 1: Pre-Flight (MANDATORY)

```text
1. Run automated assessment (Steps 1-4 above)
2. Open project pre-publish checklist (if one exists)
3. Work through EACH section systematically
4. All checkboxes must be verified (not assumed)
5. Run build/compile commands for project type
6. Verify .vscodeignore includes user-facing assets (see Packaging Pitfalls)
```

### Packaging Pitfalls (Learned 2026-02-01)

**The `.vscode/` Dual-Purpose Problem:**

The `.vscode/` folder contains both:

- **Development assets** (launch.json, tasks.json, mcp.json) — should NOT ship
- **User experience assets** (settings.json, CSS files) — SHOULD ship

**Bad:** `.vscode/**` — Excludes everything, including user assets

**Good:** Explicitly list dev files to exclude:

```ignore
.vscode/launch.json
.vscode/tasks.json
.vscode/mcp.json
# Keep .vscode/settings.json and .vscode/markdown-light.css
```

**Verification:** After packaging changes, always run:

```powershell
npx vsce ls | Select-String "\.vscode"
```

### CHANGELOG and Version Badge Pre-Flight (Learned 2026-02-16)

**Problem**: In multi-platform projects (e.g., root + platforms/vscode-extension), CHANGELOG and README badge versions can drift during rapid development, causing marketplace deployment with incorrect or incomplete documentation.

**v5.8.2 Evidence**: Extension CHANGELOG dated 5.8.1 while root CHANGELOG advanced to 5.8.2; README badge remained at 5.7.1 during 5.8.2 release preparation.

**Quality Gates** (MANDATORY before marketplace publish):

1. **CHANGELOG Synchronization**
   - **Check**: Root CHANGELOG entry matches platform CHANGELOG entry word-for-word
   - **Files**: `CHANGELOG.md` (root) → `platforms/vscode-extension/CHANGELOG.md`
   - **Automation**: `publish.ps1` validates version consistency
   - **Manual fix**: Copy latest version entry from root to platform, preserve chronological order

2. **Version Badge Consistency**
   - **Check**: README version badge matches `package.json` version
   - **Files**: `README.md` badge URL, `platforms/vscode-extension/README.md` badge URL
   - **Pattern**: `https://img.shields.io/badge/version-X.Y.Z-0078d4`
   - **Manual fix**: Update badge URL to match current version

**Verification Commands**:

```powershell
# Check CHANGELOG sync
$rootVersion = Select-String -Path CHANGELOG.md -Pattern '\[(\d+\.\d+\.\d+)\]' | Select-Object -First 1
$extVersion = Select-String -Path platforms/vscode-extension/CHANGELOG.md -Pattern '\[(\d+\.\d+\.\d+)\]' | Select-Object -First 1
if ($rootVersion -ne $extVersion) { Write-Warning "CHANGELOG mismatch!" }

# Check README badge
$pkgVersion = (Get-Content platforms/vscode-extension/package.json | ConvertFrom-Json).version
$badgeVersion = (Select-String -Path platforms/vscode-extension/README.md -Pattern 'version-(\d+\.\d+\.\d+)').Matches.Groups[1].Value
if ($badgeVersion -ne $pkgVersion) { Write-Warning "README badge outdated: $badgeVersion (should be $pkgVersion)" }
```

**Impact**: Prevents publishing with incomplete release notes or misleading version indicators that confuse users.

### Forward-Pull Pattern (Learned 2026-02-07)

**When planning a future release, check if any items can ship immediately as a patch.**

**Criteria for forward-pull candidates:**

- Pure metadata changes (package.json contribution points only)
- Zero code changes — no TypeScript modifications
- Additive — doesn't change existing behavior, only enhances
- Zero risk — worst case is a no-op, never a regression

**v5.0.1 precedent:** Pulled 4 of 31 items from v5.1.0 plan:

- A1: Declare undeclared tools in `package.json` (already registered in code)
- A2: Add `tags` to all tools (new property, ignored if unsupported)
- A6: Add `sampleRequest` to slash commands (placeholder text only)
- A7: Add disambiguation examples (more routing examples)

**Process:**

1. Review roadmap for metadata-only items
2. Implement in current version
3. Run full preflight + build pipeline
4. Publish as patch
5. Mark items completed in both roadmap AND source documents

### Phase 2: Version Bump

```bash
# Choose ONE based on change type:
npm version patch  # Bug fixes only (1.0.0 → 1.0.1)
npm version minor  # New features (1.0.0 → 1.1.0)
npm version major  # Breaking changes (1.0.0 → 2.0.0)
```

### Phase 3: Build & Package

```bash
npm run package    # Production build
vsce package       # Create .vsix
```

### Phase 4: Test Locally (RECOMMENDED)

```bash
# Install from .vsix to verify
code --install-extension alex-cognitive-architecture-<version>.vsix
```

### Phase 5: Publish

**⚠️ VSCE requires an Azure DevOps PAT, NOT a GitHub PAT!**

```bash
# RECOMMENDED: Use PAT directly (single command, no login needed)
npx vsce publish --no-dependencies --pat <AZURE_DEVOPS_PAT>
```

**Important:**

- Do NOT use `vsce login` — PATs are single-use and login prompts interactively
- Always use `--pat` flag directly with the publish command
- Use `--no-dependencies` to skip npm dependency installation (faster)

**Creating Azure DevOps PAT:**

1. Go to [dev.azure.com](https://dev.azure.com)
2. Click profile → Personal access tokens
3. Create token with:
   - Organization: `All accessible organizations`
   - Scopes: **Marketplace** → **Manage**

**Common Error:** `401 Unauthorized` = Wrong PAT type (GitHub vs Azure DevOps) or expired PAT

### Phase 6: Post-Release

1. Create git tag: `git tag v<version>`
2. Push tag: `git push origin v<version>`
3. Verify on marketplace: `vsce show fabioc-aloha.alex-cognitive-architecture`

---

## Git Workflow Integration

### Branch Strategy

| Branch      | Purpose                   | Merges To                    |
| ----------- | ------------------------- | ---------------------------- |
| `main`      | Production-ready releases | -                            |
| `develop`   | Integration branch        | `main`                       |
| `feature/*` | New features              | `develop`                    |
| `fix/*`     | Bug fixes                 | `develop` or `main` (hotfix) |
| `release/*` | Release preparation       | `main` + `develop`           |

### Commit Message Convention

```text
<type>(<scope>): <short description>

[optional body]

[optional footer]
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `refactor`: Code change that neither fixes nor adds
- `chore`: Maintenance tasks
- `release`: Version bump and release prep

**Examples:**

```text
feat(release-mgmt): add automated changelog generation
fix(dream): repair broken synapse detection logic
docs(readme): update installation instructions
release: bump version to 2.7.0
```

### Pre-Commit Checklist

Before committing, verify:

1. Code compiles: `npm run compile`
2. No unintended files staged: `git status`
3. Commit message follows convention
4. Related changes grouped logically (not everything in one commit)

### Pull Request / Merge Process

**For Solo Development:**

1. Work on feature/fix branch
2. Self-review diff before merge: `git diff develop`
3. Merge to develop: `git checkout develop && git merge feature/xyz`
4. Delete feature branch: `git branch -d feature/xyz`

**For Team Development:**

1. Push feature branch: `git push origin feature/xyz`
2. Create PR with description of changes
3. Request review if applicable
4. Squash or merge based on commit cleanliness
5. Delete remote branch after merge

---

## Deployment Scripts

**Philosophy**: Scripts > CI/CD for control and visibility. All releases run through explicit scripts.

### Script: `deploy-dev.ps1`

```powershell
# Deploy to local dev environment for testing
# Usage: .\scripts\deploy-dev.ps1

param(
    [switch]$SkipBuild,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Dev Deployment Starting..." -ForegroundColor Cyan

# Step 1: Pre-flight checks
if (-not $SkipBuild) {
    Write-Host "📦 Building..." -ForegroundColor Yellow
    npm run compile
    if ($LASTEXITCODE -ne 0) { throw "Build failed" }
}

# Step 2: Package
Write-Host "📦 Packaging extension..." -ForegroundColor Yellow
vsce package
$vsix = Get-ChildItem *.vsix | Sort-Object LastWriteTime -Descending | Select-Object -First 1

# Step 3: Install locally
Write-Host "⬇️ Installing $($vsix.Name)..." -ForegroundColor Yellow
code --install-extension $vsix.FullName --force

Write-Host "✅ Dev deployment complete!" -ForegroundColor Green
Write-Host "   Restart VS Code to load the new version." -ForegroundColor Gray
```

### Script: `deploy-prod.ps1`

```powershell
# Deploy to VS Code Marketplace (Production)
# Usage: .\scripts\deploy-prod.ps1 -BumpType patch|minor|major

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("patch", "minor", "major")]
    [string]$BumpType,

    [switch]$SkipTests,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Production Deployment Starting..." -ForegroundColor Cyan
Write-Host "   Bump Type: $BumpType" -ForegroundColor Gray

# Step 1: Ensure clean working directory
$status = git status --porcelain
if ($status -and -not $DryRun) {
    Write-Host "❌ Working directory not clean. Commit or stash changes first." -ForegroundColor Red
    git status --short
    exit 1
}

# Step 2: Ensure on correct branch
$branch = git rev-parse --abbrev-ref HEAD
if ($branch -ne "main" -and $branch -ne "develop") {
    Write-Host "⚠️ Warning: Not on main or develop branch (current: $branch)" -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -ne "y") { exit 0 }
}

# Step 3: Build and type check
Write-Host "🔨 Building and type checking..." -ForegroundColor Yellow
npm run compile
if ($LASTEXITCODE -ne 0) { throw "Build failed" }

# Step 4: Run tests (if not skipped)
if (-not $SkipTests -and (Test-Path "npm test" -ErrorAction SilentlyContinue)) {
    Write-Host "🧪 Running tests..." -ForegroundColor Yellow
    npm test
    if ($LASTEXITCODE -ne 0) { throw "Tests failed" }
}

# Step 5: Version bump
Write-Host "📝 Bumping version ($BumpType)..." -ForegroundColor Yellow
$oldVersion = (Get-Content package.json | ConvertFrom-Json).version
npm version $BumpType --no-git-tag-version
$newVersion = (Get-Content package.json | ConvertFrom-Json).version
Write-Host "   $oldVersion → $newVersion" -ForegroundColor Gray

# Step 6: Reminder to update CHANGELOG
Write-Host ""
Write-Host "📋 CHANGELOG REMINDER:" -ForegroundColor Yellow
Write-Host "   Update CHANGELOG.md with version $newVersion before continuing." -ForegroundColor Yellow
Write-Host ""
$changelogUpdated = Read-Host "Have you updated CHANGELOG.md? (y/N)"
if ($changelogUpdated -ne "y") {
    Write-Host "Please update CHANGELOG.md and run again." -ForegroundColor Red
    # Revert version bump
    npm version $oldVersion --no-git-tag-version --allow-same-version
    exit 1
}

if ($DryRun) {
    Write-Host "🏁 DRY RUN complete. Would publish version $newVersion" -ForegroundColor Cyan
    npm version $oldVersion --no-git-tag-version --allow-same-version
    exit 0
}

# Step 7: Commit version bump
git add package.json package-lock.json CHANGELOG.md
git commit -m "release: bump version to $newVersion"

# Step 8: Create tag
git tag "v$newVersion"

# Step 9: Package and publish
Write-Host "📦 Packaging for production..." -ForegroundColor Yellow
npm run package
vsce publish

# Step 10: Push to remote
Write-Host "⬆️ Pushing to remote..." -ForegroundColor Yellow
git push origin $branch
git push origin "v$newVersion"

Write-Host ""
Write-Host "✅ Production deployment complete!" -ForegroundColor Green
Write-Host "   Version: $newVersion" -ForegroundColor Gray
Write-Host "   Tag: v$newVersion" -ForegroundColor Gray
Write-Host "   Verify: vsce show fabioc-aloha.alex-cognitive-architecture" -ForegroundColor Gray
```

### Script: `rollback.ps1`

```powershell
# Rollback to a previous version
# Usage: .\scripts\rollback.ps1 -Version 2.6.1

param(
    [Parameter(Mandatory=$true)]
    [string]$Version
)

$ErrorActionPreference = "Stop"

Write-Host "⏪ Rollback to v$Version starting..." -ForegroundColor Yellow

# Step 1: Checkout the tag
git fetch --tags
git checkout "v$Version"

# Step 2: Rebuild from that version
npm install
npm run package

# Step 3: Publish the old version
Write-Host "Publishing v$Version to marketplace..." -ForegroundColor Yellow
vsce publish

# Step 4: Return to main branch
git checkout main

Write-Host ""
Write-Host "✅ Rollback complete!" -ForegroundColor Green
Write-Host "   Rolled back to: v$Version" -ForegroundColor Gray
Write-Host "   Note: Consider creating a patch release with the fix." -ForegroundColor Yellow
```

### Script Locations

Store deployment scripts in project root under `scripts/`:

```
project/
├── scripts/
│   ├── deploy-dev.ps1
│   ├── deploy-prod.ps1
│   └── rollback.ps1
├── package.json
└── ...
```

### Script Trigger Phrases

| User Says               | Alex Response                                                                                                                           |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| "deploy to dev"         | "I'll run the dev deployment script. Let me verify the build first."                                                                    |
| "deploy to prod"        | "Production deployment requires: 1) clean git status, 2) version bump type (patch/minor/major), 3) updated CHANGELOG. Which bump type?" |
| "rollback to X"         | "I'll run the rollback script to restore version X. This will republish the old version to marketplace."                                |
| "create deploy scripts" | "I'll generate deployment scripts for this project. What's your target platform?"                                                       |

---

## Team Coordination

### Release Communication Template

**Pre-Release (if team involved):**

```text
📢 Release Planned: v{version}
- Target: {date/time}
- Changes: {brief summary}
- Blockers: {any known issues}
- Owner: {who's running the release}
```

**Post-Release:**

```text
✅ Released: v{version}
- Changelog: {link}
- Known issues: {if any}
- Rollback plan: Run scripts/rollback.ps1 -Version {prev_version}
```

### Code Review Checklist (For Team Projects)

Before approving a PR:

- [ ] Code compiles without warnings
- [ ] Changes match PR description
- [ ] No unrelated changes included
- [ ] Documentation updated if needed
- [ ] Version bump appropriate for changes
- [ ] CHANGELOG entry present

---

## Multi-Platform Release Coordination

**Applies to**: Projects with multiple deployment targets (VS Code extension + M365 Copilot agent, etc.)

### Version Synchronization Protocol

When shipping a release across multiple platforms, version numbers MUST be aligned:

| Platform           | Version File    | Location                                          |
| ------------------ | --------------- | ------------------------------------------------- |
| VS Code Extension  | `package.json`  | `platforms/vscode-extension/package.json`         |
| M365 Copilot Agent | `package.json`  | `platforms/m365-copilot/package.json`             |
| M365 App Manifest  | `manifest.json` | `platforms/m365-copilot/appPackage/manifest.json` |
| Root Project       | CHANGELOG.md    | `CHANGELOG.md` (root)                             |
| Extension          | CHANGELOG.md    | `platforms/vscode-extension/CHANGELOG.md`         |

**Synchronization Order:**

1. Update VS Code extension version first (source of truth)
2. Update M365 versions to match
3. Update root CHANGELOG with release notes
4. Extension CHANGELOG auto-syncs during `vsce package` (architecture sync)

### Multi-Platform Publishing Workflow

**Step 1: VS Code Extension (Primary Platform)**

```powershell
cd platforms/vscode-extension
npm run compile           # Verify build clean
npx @vscode/vsce package  # Creates .vsix + runs architecture sync
npx @vscode/vsce publish  # Publishes to marketplace
```

**Checkpoint**: Architecture sync runs during `vsce package`, updating heir `.github/` from master.

**Step 2: M365 Copilot Agent (Secondary Platform)**

```powershell
cd platforms/m365-copilot
npm run package          # Creates appPackage.local.zip
npm run validate         # Optional - validates manifest (requires auth)
```

**Checkpoint**: Package ready for Teams Developer Portal upload or direct Teams sideload.

**Step 3: Git Tagging** (After both platforms packaged)

```powershell
cd ../..                 # Return to root
git tag vX.Y.Z -a -m "vX.Y.Z - Release Title"
git push origin vX.Y.Z
```

### Heir Architecture Sync Verification

During VS Code packaging, the `sync-to-heir.cjs` script runs automatically:

**Expected Output:**

```
✅ Copied: N skills
⏭️  Skipped (master-only): X
⏭️  Skipped (heir:m365): Y
✅ Skill sync verified!
```

**What to check:**

- Skill count matches expectations (master - master-only = heir)
- No contamination detected (heir has no master-only content)
- Synapse cleaning removed broken references

**If sync fails:** Do NOT proceed with publish. Fix sync issues first.

### Version Alignment Checklist

Before creating git tag, verify alignment:

```powershell
# VS Code extension
$vsCodeVersion = (Get-Content platforms/vscode-extension/package.json | ConvertFrom-Json).version

# M365 agent
$m365PkgVersion = (Get-Content platforms/m365-copilot/package.json | ConvertFrom-Json).version
$m365ManifestVersion = (Get-Content platforms/m365-copilot/appPackage/manifest.json | ConvertFrom-Json).version

# CHANGELOGs
$rootChangelogVersion = (Select-String -Path CHANGELOG.md -Pattern '\[(\d+\.\d+\.\d+)\]' | Select-Object -First 1).Matches.Groups[1].Value
$extensionChangelogVersion = (Select-String -Path platforms/vscode-extension/CHANGELOG.md -Pattern '\[(\d+\.\d+\.\d+)\]' | Select-Object -First 1).Matches.Groups[1].Value

Write-Host "VS Code: $vsCodeVersion"
Write-Host "M365 Package: $m365PkgVersion"
Write-Host "M365 Manifest: $m365ManifestVersion"
Write-Host "Root CHANGELOG: $rootChangelogVersion"
Write-Host "Extension CHANGELOG: $extensionChangelogVersion"

if ($vsCodeVersion -eq $m365PkgVersion -and $vsCodeVersion -eq $m365ManifestVersion -and $vsCodeVersion -eq $rootChangelogVersion) {
    Write-Host "✅ All versions aligned: $vsCodeVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Version mismatch detected!" -ForegroundColor Red
}
```

### Platform-Specific Deployment Notes

**VS Code Marketplace:**

- Published via `vsce publish` (requires PAT token)
- Propagates in 2-5 minutes
- Visible at: `https://marketplace.visualstudio.com/items?itemName=fabioc-aloha.alex-cognitive-architecture`

**M365 Copilot Agent:**

- Manual upload to Teams Developer Portal: <https://dev.teams.microsoft.com/apps>
- OR direct Teams sideload: Teams → Apps → Upload custom app
- Package file: `appPackage/build/appPackage.local.zip`

**GitHub Release:**

- Create after both platforms published
- Attach both artifacts:
  - `alex-cognitive-architecture-X.Y.Z.vsix` (VS Code)
  - `appPackage.local.zip` (M365)
- Use CHANGELOG excerpt for release notes

### Multi-Platform Release Anti-Patterns

❌ **Do NOT**:

- Publish VS Code before updating M365 versions
- Skip architecture sync verification (heir must match master)
- Create git tag before both platforms packaged
- Forget to update root CHANGELOG (only extension CHANGELOG)
- Publish M365 with different version than VS Code

✅ **Always**:

- Update ALL version files before publishing any platform
- Verify architecture sync completed successfully
- Package both platforms **before** creating git tag
- Test extension CHANGELOG synced to heir during packaging
- Maintain single source of truth (VS Code version → M365)

---

## Trigger Phrases & Responses

| User Says               | Alex Response                                                                                                                       |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| "Let's release"         | "Great! Let me open the Pre-Publishing Checklist to ensure we don't miss anything critical."                                        |
| "Publish this"          | "Before publishing, I need to verify: 1) version consistency, 2) changelog updated, 3) code compiles. Which should we check first?" |
| "Bump the version"      | "Which type of release is this? patch (bug fix), minor (new feature), or major (breaking change)?"                                  |
| "Deploy to marketplace" | "I'll walk us through the release process. First, have you completed the Pre-Publishing Checklist?"                                 |
| "Quick release"         | "I understand the time pressure, but let me do a rapid validation first - it takes 60 seconds and prevents rollback headaches."     |
| "deploy to dev"         | "Running dev deployment. I'll build, package, and install locally for testing."                                                     |
| "deploy to prod"        | "Production deployment checklist: 1) git status clean, 2) version bump type, 3) CHANGELOG updated. Ready?"                          |

---

## Anti-Patterns to Prevent

### ❌ Do NOT

- Skip the checklist because "it's a small change"
- Publish without verifying version numbers match everywhere
- Forget to update CHANGELOG.md
- Assume tests pass without running them
- Skip local testing of the .vsix
- Deploy from a dirty git working directory
- Forget to push tags after release
- Merge directly to main without testing

### ✅ Always

- Treat the checklist as a gate, not a suggestion
- Verify actual file contents, don't trust memory
- Build in production mode before packaging
- Test the packaged extension locally when possible
- Use deployment scripts for consistency
- Tag releases immediately after publish
- Keep main branch always deployable

---

## Recovery Procedures

### If Published with Errors

1. **Don't panic** - the marketplace allows updates
2. Increment patch version immediately
3. Fix the issue
4. Republish: `vsce publish`
5. Document in CHANGELOG.md what was fixed

### If Version Mismatch Discovered Post-Publish

1. Note the inconsistency in CHANGELOG.md
2. Plan corrective release
3. Add to checklist verification steps if pattern emerges

### If Need to Rollback

1. Run: `.\scripts\rollback.ps1 -Version <previous_version>`
2. Communicate rollback to stakeholders
3. Create hotfix branch: `git checkout -b fix/rollback-issue`
4. Fix the issue
5. Re-release with patch version bump

---

## Process Evolution

When release issues occur:

1. Document the issue in this file
2. Add corresponding check to PRE-PUBLISH-CHECKLIST.md
3. Update deployment scripts if issue is detectable programmatically
4. Add to anti-patterns list to prevent recurrence

_Last Updated: 2026-01-23_
_This procedural memory ensures release consistency across all deployments_
