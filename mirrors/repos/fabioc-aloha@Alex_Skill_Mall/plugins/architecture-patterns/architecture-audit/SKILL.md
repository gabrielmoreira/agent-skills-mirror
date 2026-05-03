---
type: skill
lifecycle: stable
inheritance: inheritable
name: architecture-audit
description: Comprehensive project consistency review across code, documentation, diagrams, and configuration
tier: standard
applyTo: '**/*architecture*,**/*audit*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Architecture Audit


> Comprehensive **project** consistency review across code, documentation, diagrams, and configuration

## Overview

Systematic audit process to ensure all **project** artifacts stay synchronized. Catches version drift, terminology inconsistencies, outdated diagrams, broken references, and code-to-docs mismatches.

⚠️ **IMPORTANT**: This skill audits the **user's project code**, NOT the the AI assistant cognitive architecture in `.github/`. Ignore `.github/` folder contents when performing audits - focus on the actual source code, documentation, and configuration in the project root and subdirectories.

## Triggers

- "audit", "comprehensive review", "fact-check"
- "consistency check", "project health"
- "pre-release audit", "documentation review"
- Before major releases or after significant refactoring

## Audit Checklist

### 1. Version Consistency

```powershell
# Find version references in common locations
# EXCLUDE: .github/** (the AI assistant cognitive architecture - not project code)
$patterns = @(
    'package.json',           # "version": "x.y.z"
    'src/**/config*.json',    # Version in config files (not .github)
    '*.md',                   # Root documentation only
    'docs/**/*.md',           # Project docs (not .github)
    'src/**/constants.ts',    # Hardcoded versions
    'CHANGELOG.md'            # Version headers
)

# Grep for version patterns
Get-ChildItem -Recurse -Include $patterns |
    Select-String -Pattern 'v?\d+\.\d+\.\d+' |
    Group-Object -Property Line
```

**Check:** All version references match the canonical version (usually package.json)

### 2. Terminology Consistency

Build a deprecated terms list for your project:

| Deprecated Term | Current Term | Migration Pattern |
|-----------------|--------------|-------------------|
| `DK-*.md` | `skills/*/SKILL.md` | File format change |
| `domain-knowledge/` | `skills/` | Folder rename |
| (project-specific) | (project-specific) | (document here) |

```powershell
# Search for deprecated terms (exclude .github/)
$deprecated = @('OLD_TERM_1', 'OLD_TERM_2')
foreach ($term in $deprecated) {
    Get-ChildItem -Recurse -Include "*.md","*.ts","*.json" -Exclude ".github" |
        Where-Object { $_.FullName -notmatch '\\.github\\' } |
        Select-String -Pattern $term
}
```

### 3. Fact Inventory

Maintain a facts file or section with current counts:

```markdown
## Current Facts (Update on Audit)
- Skills: 46 folders
- Commands: 16 total
- Tools: 11 MCP tools
- Agents: 5 custom agents
- Instructions: 19 files
- Prompts: 7 files
```

**Check:** All documentation referencing these counts matches actual values

### 4. Diagram Validation

For each diagram (Mermaid/ASCII):

- [ ] Node labels match current terminology
- [ ] Counts in labels are accurate
- [ ] Flow directions reflect actual data flow
- [ ] Subgroup names are current
- [ ] No references to deprecated concepts

```powershell
# Find all diagrams in project (exclude .github/)
Get-ChildItem -Recurse -Include "*.md" |
    Where-Object { $_.FullName -notmatch '\\.github\\' } |
    Select-String -Pattern '```mermaid|```ascii|┌|╔' |
    Group-Object -Property Path
```

### 5. Cross-Reference Validation

- [ ] Internal links resolve (`[text](path)` → file exists)
- [ ] Anchor links work (`#section-name` → heading exists)
- [ ] Image references valid
- [ ] Import/require statements resolve

```powershell
# Find markdown links in project (exclude .github/)
Get-ChildItem -Recurse -Include "*.md" |
    Where-Object { $_.FullName -notmatch '\\.github\\' } |
    Select-String -Pattern '\[.*?\]\((?!http)[^)]+\)' |
    ForEach-Object {
        # Extract path and verify existence
    }
```

### 6. Code-to-Docs Sync

| Code Artifact | Documentation Location | Check |
|---------------|----------------------|-------|
| Exported functions | API docs | Signatures match |
| Config options | README/User Manual | All options documented |
| CLI commands | Help text / docs | Commands listed |
| Error messages | Troubleshooting | Errors explained |

### 7. Configuration Alignment

- [ ] TypeScript constants match documentation
- [ ] JSON schemas match actual structure
- [ ] Environment variables documented
- [ ] Feature flags documented

## Audit Report Template

```markdown
# Architecture Audit Report
**Date:** YYYY-MM-DD
**Version Audited:** x.y.z
**Auditor:** [name/AI]

## Summary
| Category | Status | Issues Found |
|----------|--------|--------------|
| Version Consistency | ✅/⚠️/❌ | N |
| Terminology | ✅/⚠️/❌ | N |
| Fact Accuracy | ✅/⚠️/❌ | N |
| Diagrams | ✅/⚠️/❌ | N |
| Cross-References | ✅/⚠️/❌ | N |
| Code-Docs Sync | ✅/⚠️/❌ | N |

## Issues Found
### [Category]
- **File:** path/to/file
- **Line:** N
- **Issue:** Description
- **Fix:** Suggested correction

## Actions Taken
- [ ] Issue 1 fixed
- [ ] Issue 2 fixed
```

## Automation Opportunities

### Pre-commit Hook

```bash
# .husky/pre-commit or similar
npm run audit:quick  # Fast checks only
```

### CI Pipeline

```yaml
# GitHub Actions
- name: Architecture Audit
  run: npm run audit:full
  if: github.event_name == 'pull_request'
```

### Scheduled Audit

```yaml
# Weekly full audit
on:
  schedule:
    - cron: '0 9 * * 1'  # Monday 9am
```

## Anti-Patterns

❌ **Skipping audits before release** — Drift accumulates silently

❌ **Manual-only audits** — Automate what you can

❌ **Fixing without documenting** — Record the pattern for next time

❌ **Ignoring "cosmetic" issues** — They signal deeper drift

❌ **Auditing only changed files** — Drift affects unchanged files too

## Best Practices

✅ **Run full audit before major releases**

✅ **Add new deprecated terms as you migrate**

✅ **Update fact inventory after structural changes**

✅ **Document audit findings for patterns**

✅ **Automate repetitive checks**

✅ **Time-box manual review (don't boil the ocean)**

## Integration with Other Skills

- `release-preflight` → Trigger audit before release
- `brain-qa` → Connection validation and architecture health
- `code-review` → Audit as part of PR review
- `refactoring-patterns` → Audit after major refactoring

---

## your AI assistant Extensions

> your AI assistant-specific audit procedures that extend the generic project audit above. These leverage knowledge of exact folder structure, heir relationships, safety imperatives, and build/release workflows.

### Audit Philosophy (Semantic + Structural)

| Dimension | Script (Automated) | the AI assistant (With This Skill) |
|-----------|-------------------|------------------------|
| **Structural** | File existence, counts, format | ✅ Automated |
| **Semantic** | — | Do files describe concepts consistently? |
| **Logic** | — | Are documented workflows achievable? |
| **Code** | Compile, lint, bundle | Does code match documented claims? |
| **Architectural** | Version alignment, heir sync | Is memory architecture reflected accurately? |

### Master-Only Sections (1-9)

| # | Section | What It Checks |
|---|---------|----------------|
| 1 | Version Alignment | package.json ↔ CHANGELOG ↔ copilot-instructions |
| 2 | Heir Folder Sync | Master → heir file counts |
| 3 | Skill Inheritance | SKILL_EXCLUSIONS in sync-architecture.cjs |
| 4 | Safety Imperatives | Kill switch, protection markers |
| 5 | Build Artifacts | dist/extension.js exists and recent |
| 6 | Documentation Cross-Refs | Required links between docs |
| 7 | Connection Health | Valid links, no orphans |
| 8 | alex_docs Audit | Version refs, deprecated terms |
| 9 | Skill Network Diagram | Node count matches actual skills |

### Inheritable Sections (10-22)

| # | Section | What It Checks |
|---|---------|----------------|
| 10 | Extension UI | Dead buttons |
| 11 | Dependency Health | npm audit vulnerabilities |
| 12 | TypeScript & Lint | Compile errors, lint warnings |
| 13 | Security | Secrets in code, CSP compliance |
| 14 | Bundle Size | extension.js size |
| 15 | Git Hygiene | Uncommitted changes, branch status |
| 16 | Changelog | Format, version alignment |
| 17 | API Compatibility | Deprecated VS Code APIs |
| 18 | Test Coverage | Test file count vs source files |
| 19 | Accessibility | ARIA labels, CSS variables |
| 20 | Localization | l10n configuration |
| 21 | Asset Integrity | Icon exists, no missing assets |
| 22 | Configuration Files | launch.json, tsconfig.json, .vscodeignore |

### Production Scripts

```powershell
# Full audit (all 22 sections)
node .github/muscles/brain-qa.cjs

# Quick audit (sections 1-9)
node .github/muscles/brain-qa.cjs --mode quick

# Specific sections
node .github/muscles/brain-qa.cjs --mode quick --quiet
```

### Semantic Review Checklist (Manual — Not Scriptable)

- [ ] Cross-heir semantic parity: M365 system prompt matches copilot-instructions
- [ ] Deprecated terminology: No "DK files" / "domain-knowledge/" in active files
- [ ] Claim vs. reality: README features match package.json commands
- [ ] Process logic: Heir evolution, meditation, dream workflows internally consistent
- [ ] Architectural model: Memory architecture described consistently everywhere
- [ ] Code behavior: TypeScript handlers match instruction file docs
- [ ] Version source of truth: package.json is canonical
