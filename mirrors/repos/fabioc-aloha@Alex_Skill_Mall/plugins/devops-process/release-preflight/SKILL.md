---
type: skill
lifecycle: stable
inheritance: inheritable
name: release-preflight
description: Pre-checks, version consistency, and deployment discipline.
tier: standard
applyTo: '**/*release*,**/*preflight*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Release Preflight Skill


> Pre-checks, version consistency, and deployment discipline.

## The Golden Rule

> **NEVER publish without running the preflight checklist.**

## Quick Start

```bash
# Full preflight check
node scripts/release-preflight.cjs

# With packaging test
node scripts/release-preflight.cjs

# Skip time-consuming tests
node scripts/release-preflight.cjs
```

## Version Locations (Must Stay Synchronized)

| #   | Location                                                     | Field               | Example                   |
| --- | ------------------------------------------------------------ | ------------------- | ------------------------- |
| 1   | `heir/platforms/vscode-extension/package.json` | `version`      | `"8.2.1"`                 |
| 2   | `heir/CHANGELOG.md`                            | Latest heading | `## [8.2.1] - 2026-04-22` |
| 3   | `BUILD-MANIFEST.json` (if present)             | `version`      | `"8.2.1"`                 |
| 4   | Git tag                                        | Tag name       | `v8.2.1`                  |

## Preflight Gates

| Gate | Check                          | Script Flag |
| ---- | ------------------------------ | ----------- |
| 0    | PAT configured                 | Always      |
| 1    | Version sync (all 7 locations) | Always      |
| 2    | VSIX exists                    | Always      |
| 3    | Git clean                      | Always      |
| 4    | Git tag available              | Always      |
| 5    | VSCE_PAT available             | Always      |
| 6    | Heir sync drift                | Always      |

## Full Release Workflow

```bash
# VS Code Extension release
node scripts/release-vscode.cjs

# M365 Agent release
node scripts/release-m365.cjs --validate
```

## Version Bump Only

```powershell
# 1. Bump
npm version patch --no-git-tag-version

# 2. Get version
$v = (Get-Content package.json | ConvertFrom-Json).version

# 3. Update CHANGELOG, commit, tag, push
git add -A; git commit -m "release: v$v"; git tag "v$v"; git push --tags
```

## Common Mistakes

| Mistake                        | Prevention                       |
| ------------------------------ | -------------------------------- |
| Published without version bump | Run preflight first              |
| CHANGELOG not updated          | Script checks this               |
| Forgot to push tags            | Script does this                 |
| Version mismatch               | Grep entire repo for old version |
| PAT 401 error                  | Refresh PAT before release       |

## Go / No-Go Decision Table (RP3)

After preflight runs, classify each finding to decide whether to proceed:

| Finding | Severity | Decision | Rationale |
|---------|----------|----------|-----------|
| Version mismatch across locations | **Block** | Fix before publish | Silent version drift = wrong artifact on marketplace |
| VSIX file missing or wrong version in filename | **Block** | Rebuild VSIX | Publishing a stale or misnamed artifact is irreversible |
| Git working tree dirty | **Block** | Commit or stash | Tagged release must match a clean commit |
| Git tag already exists for target version | **Block** | Bump version or delete tag | Duplicate tag = ambiguous release provenance |
| VSCE_PAT missing or expired | **Block** | Refresh token | Publish will 401; partial state is worse than no-op |
| Heir sync drift detected | **Warning** | Review diff, then decide | Drift may be intentional (master-only changes) or accidental |
| CHANGELOG entry missing for version | **Warning** | Add entry, or proceed if patch-only fix | Users and future-you need the audit trail |
| Test failures in extension | **Block** | Fix tests | Shipping known-broken code violates trust |
| Brain-qa score below threshold | **Warning** | Review findings; proceed if cosmetic-only | Brain health affects heirs on next upgrade |
| Frontmatter audit failures | **Warning** | Fix if quick; track as debt if not | New files may lack frontmatter; not a ship-blocker unless systemic |

**Rule**: Any **Block** finding = hard stop. Fix first, re-run preflight, then proceed.
**Warning** findings require explicit operator acknowledgment — the LLM should list them and ask "proceed despite these warnings?"

## Changelog Voice QA Decision Table (RP2)

After preflight passes, review `CHANGELOG.md` entries for the release version against these voice standards:

| Condition | Verdict | Action |
|-----------|---------|--------|
| Entry uses past tense ("Added", "Fixed", "Removed") | Pass | Standard changelog convention |
| Entry uses present/future tense ("Adds", "Will fix") | Fail | Rewrite to past tense |
| Entry describes user-visible impact ("Users can now...") | Pass | Preferred framing |
| Entry describes internal implementation ("Refactored the parser loop") | Warning | Rewrite to user impact; move internal detail to commit message |
| Entry uses internal jargon ("brain-qa", "trifecta", "sidecar") | Fail | Replace with user-facing language ("health checks", "skill set", "config") |
| Entry is a single vague line ("Bug fixes and improvements") | Fail | Expand to specific items |
| Entry references a PLAN task ID ("FM4", "RP2") only | Fail | Add human-readable description alongside |
| Entry groups related changes under a category header | Pass | Use: Added, Changed, Fixed, Removed, Security |
| Breaking change is clearly marked with `**BREAKING**` | Pass | Required for major bumps |
| Entry length proportional to change significance | Pass | One-liners for patches, paragraphs for features |
| Links to related docs/issues included for complex changes | Pass | Helps users understand context |
| Duplicate entries from cherry-pick or merge | Fail | Deduplicate; keep most descriptive version |

## Related Scripts

| Script                                        | Purpose                                |
| --------------------------------------------- | -------------------------------------- |
| `scripts/release-preflight.cjs`               | Pre-release validation                 |
| `scripts/release-vscode.cjs`                  | Full VS Code release                   |
| `scripts/release-m365.cjs`                    | M365 agent packaging                   |

## Triggers

- "release", "publish", "deploy"
- "preflight", "pre-release check"
- "version bump", "version sync"

---

_Scripts: `scripts/release-preflight.cjs`, `scripts/release-vscode.cjs`_
