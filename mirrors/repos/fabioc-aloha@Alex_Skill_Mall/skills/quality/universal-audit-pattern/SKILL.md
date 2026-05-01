---
type: skill
lifecycle: stable
inheritance: inheritable
name: universal-audit-pattern
description: Systematic project audit pattern — version consistency, terminology, fact inventory, cross-references
tier: standard
applyTo: '**/*universal*,**/*audit*,**/*pattern*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Universal Audit Pattern

**Category**: Quality
**Time Saved**: 4+ hours per audit
**Battle-tested**: Yes — applied to docs, code, security, architecture

---

## The Problem

You need to audit something — documentation accuracy, code quality, security compliance, architectural drift. You start checking things randomly, fix some issues, get distracted, lose track of what you've reviewed.

## Why Ad-Hoc Audits Fail

- No systematic coverage — you miss things
- No severity ranking — you fix minor issues while critical ones wait
- No completion criteria — you don't know when you're done
- No reproducibility — next audit starts from scratch

## The Rule

**Inventory → Compare to Ground Truth → Severity-Classify → Fix All**

This four-step pattern works for any domain where claims can drift from reality.

## The Pattern

### Step 1: Inventory

Create a complete list of items to audit. Be exhaustive.

```markdown
## Inventory

| # | Item | Location | Status |
|---|------|----------|--------|
| 1 | Test count claim | README.md:45 | Pending |
| 2 | API endpoint list | docs/api.md | Pending |
| 3 | Version requirement | package.json | Pending |
| ... | ... | ... | ... |
```

### Step 2: Compare to Ground Truth

For each item, verify against the authoritative source.

```markdown
## Ground Truth Comparison

| # | Claim | Ground Truth | Match? |
|---|-------|--------------|--------|
| 1 | "47 tests" | `npm test` shows 89 | ❌ |
| 2 | "5 endpoints" | OpenAPI spec has 7 | ❌ |
| 3 | "Node 16+" | engines: ">=20" | ❌ |
```

### Step 3: Severity-Classify

Prioritize by impact, not discovery order.

| Severity | Criteria | Example |
|----------|----------|---------|
| **Critical** | Breaks functionality, security risk | Wrong API URL |
| **High** | Misleads users significantly | Wrong version requirements |
| **Medium** | Inaccurate but not harmful | Outdated feature list |
| **Low** | Cosmetic, minor | Typos in comments |

```markdown
## Classified Findings

### Critical (fix immediately)
- [ ] #12: Security config example has hardcoded secret

### High (fix this sprint)
- [ ] #3: Version requirement mismatch
- [ ] #7: Deprecated API still documented

### Medium (fix when touched)
- [ ] #1: Test count outdated
- [ ] #2: Endpoint count wrong

### Low (backlog)
- [ ] #15: Typo in contributing guide
```

### Step 4: Fix All

Work through findings by severity. Mark each as done.

```markdown
## Resolution Log

| # | Finding | Fix | Commit |
|---|---------|-----|--------|
| 12 | Hardcoded secret | Replaced with env var | abc123 |
| 3 | Wrong Node version | Updated to >=20 | def456 |
| ... | ... | ... | ... |
```

## Domain Applications

### Documentation Audit

- **Inventory**: All claims with numbers, versions, paths
- **Ground Truth**: Code, configs, API specs, runtime output
- **Severity**: Accuracy impact on users

### Security Audit

- **Inventory**: All auth flows, data handling, dependencies
- **Ground Truth**: OWASP checklist, CVE database
- **Severity**: Exploitability × Impact

### Architecture Audit

- **Inventory**: All system components, integrations
- **Ground Truth**: Actual deployed infrastructure
- **Severity**: Drift from intended design

### Code Quality Audit

- **Inventory**: All modules, functions, tests
- **Ground Truth**: Style guide, coverage targets
- **Severity**: Maintainability impact

## Template

```markdown
# [Domain] Audit Report

**Date**: YYYY-MM-DD
**Auditor**: Name
**Scope**: What's being audited

## Executive Summary

- Items audited: N
- Findings: X critical, Y high, Z medium
- Status: In progress / Complete

## Inventory

| # | Item | Location | Status |
|---|------|----------|--------|
| 1 | ... | ... | ... |

## Findings by Severity

### Critical
- [ ] ...

### High
- [ ] ...

### Medium
- [ ] ...

### Low
- [ ] ...

## Resolution Log

| # | Finding | Fix | Verified |
|---|---------|-----|----------|
| ... | ... | ... | ... |

## Recommendations

1. ...
2. ...
```

## Verification Checklist

- [ ] Inventory is complete (not just obvious items)
- [ ] Ground truth is authoritative (not another doc)
- [ ] Severity based on impact, not effort
- [ ] Every finding has resolution or explicit deferral
- [ ] Audit is reproducible (someone else could re-run it)

## Related Skills

- `docs-decay-velocity` — Why docs need auditing
- `allowlist-over-blocklist` — Audit approach for validation
