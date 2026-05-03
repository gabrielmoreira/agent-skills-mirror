---
type: skill
lifecycle: stable
inheritance: inheritable
name: extension-audit-methodology
description: Systematic 5-dimension audit framework for VS Code extensions — debug hygiene, dead code, performance, menu validation, dependency cleanup
tier: standard
applyTo: '**/*extension*,**/*audit*,**/*methodology*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Extension Audit Methodology


> Find quality issues standard code review misses — before release, not after deployment.

---

## Pattern Overview

A systematic 5-dimension audit framework for VS Code extensions to identify code quality issues beyond standard linting. Produces actionable recommendations with evidence-based prioritization.

**Problem Solved**: Standard code review catches logic bugs and style issues, but misses extension-specific quality problems like orphaned commands, blocking I/O in UI threads, debug noise in production, and leftover dependencies from removed features.

**When to Use**:

- Before major release (milestone versions)
- After significant refactoring
- When performance degradation suspected
- Post-feature-removal cleanup

**Time Investment**: 2-4 hours for comprehensive audit + 4-8 hours remediation

---

## 5-Dimension Audit Framework

### 1. Debug & Logging Audit

**Objective**: Identify console statements and categorize by necessity

**Method**:

```powershell
# Scan for all console statements
Select-String -Path src/*.ts -Pattern "console\.(log|debug|warn|error)" -Recurse
```

**Categorization**:

| Category | Keep? | Examples | Rationale |
| -------- | ----- | -------- | --------- |
| **Enterprise compliance** | ✅ | Audit logs, security events | Legal/regulatory requirement |
| **User feedback** | ✅ | TTS status, long-running ops | User-facing information |
| **Critical errors** | ✅ | Unrecoverable failures | Debugging user-reported issues |
| **Setup verbosity** | ❌ | "Loading CSS..." | Noise during normal operation |
| **Migration debugging** | ❌ | Version upgrade steps | Temporary development artifacts |

---

### 2. Dead Code Detection

**Commands Cross-Check**:

1. Find registered commands in `extension.ts`
2. Find command contributions in `package.json`
3. Find command invocations in UI/views
4. Identify: broken (in UI, not registered), dead (registered, never invoked)

---

### 3. Performance Profiling

**Blocking I/O Scan**:

```powershell
# Synchronous file operations (event loop blockers)
Select-String -Path src/*.ts -Pattern "fs\.(readFileSync|existsSync|readdirSync|writeFileSync)" -Recurse
```

**Refactoring Pattern**:

```typescript
// BEFORE (blocking)
const exists = fs.existsSync(path);

// AFTER (async)
import * as fs from 'fs-extra';
const exists = await fs.pathExists(path);
```

---

### 4. Menu Validation

**Test Matrix**:

- Extract all commands from `package.json` contributions
- Verify each has a registered handler
- Test in VS Code: Command Palette, buttons, context menus

---

### 5. Dependency Hygiene

**Unused Package Detection**:

```powershell
npm ls --depth=0
# For each dependency, verify it's imported
Select-String -Path src/*.ts -Pattern "from '@package-name'" -Recurse
```

---

## Audit Report Template

```markdown
# Extension Audit Report

**Date**: YYYY-MM-DD
**Version**: X.Y.Z

## Executive Summary

- **Console statements**: X remaining (Y legitimate, Z removable)
- **Dead code**: [count] commands/features
- **Performance**: [X blocking ops]
- **Menu validation**: Y/X working (Z% functional)
- **Dependencies**: W unused packages

**Code Quality Grade**: [A+/A/A-/B+/B]

---

## Recommendations

| Priority | Category | Issue | Action | Effort |
|----------|----------|-------|--------|--------|
| Critical | Dead Code | Broken command | Fix or remove | 30m |
| High | Performance | Blocking I/O | Async refactor | 2h |
| High | Logging | Removable logs | Delete | 1h |
| Medium | Dependencies | Unused package | Remove | 15m |
```

---

## Success Metrics

**Before Audit** (typical mature extension):

- Console statements: 40-80
- Dead commands: 3-8
- Blocking sync I/O: 10-30 operations
- Code quality grade: B/B+

**After Remediation**:

- Console statements: 15-25 (legitimate only)
- Dead commands: 0
- Blocking sync I/O: 0 (all async)
- Code quality grade: A/A+

**Improvement**: ~50% console reduction, 100% dead code removal, measurable performance gain

---

## Real-World Application: the AI assistant v5.7.1

**Audit Results**:

- Console statements: 46 found → 27 removed (18 legitimate kept)
- Dead code: 3 deprecated commands + 1 UI feature + 1 unused dependency
- Performance: 16 blocking sync operations in cognitiveDashboard.ts
- Menu validation: 39/41 working (95%)

**Remediation Actions**:

1. Removed 27 console statements
2. Deleted 3 deprecated Gist sync commands
3. Removed `generateImageFromSelection` UI from 3 locations
4. Refactored dashboard to async I/O (fs → fs-extra)
5. Removed `@azure/msal-node` dependency (unused)
6. Deleted 477-line obsolete MS Graph documentation

**Results**:

- Code quality: B+ → A+
- TypeScript errors: 0
- Extension size: 9.45 MB (optimized)
- Console cleanliness: 61 total removed across 2 releases

**Effort**: 8 hours audit + remediation → measurable quality improvement

---

## Post-Audit Verification Checklist

- [ ] **TypeScript compiles**: `npm run compile` → exit 0, zero errors
- [ ] **No orphaned imports**: All import statements resolve
- [ ] **Extension activates**: Test `.vsix` installation
- [ ] **Smoke test**: 3 random commands execute correctly
- [ ] **Performance**: Dashboard/views render without lag
- [ ] **Console clean**: Only intentional logs during normal operation
