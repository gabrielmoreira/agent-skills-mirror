---
name: code-review
description: "Review code against story acceptance criteria and quality standards. Use when the user says 'review this code', 'review my PR', or 'check this implementation'."
---

# Code Review Workflow

## Goal

Evaluate code for correctness (meets ACs), quality, security, and maintainability. Produce a structured review with actionable feedback.

---

## Activation

Ask:
1. What is being reviewed? (PR, branch, file, or paste)
2. Which story / ACs does it implement? (load story if given ID)
3. Review depth: Quick / Standard / Deep-dive

---

## Review Dimensions

Evaluate across 5 dimensions:

### 1. Correctness — Does it meet the ACs?

For each AC in the story:
- [ ] AC-1: Implemented? How verified?
- [ ] AC-2: Implemented? How verified?
- [ ] Edge case coverage (error/failure paths from AC-3+)

**Blockers**: Any unmet AC is a blocker — cannot ship.

---

### 2. Tests

- [ ] Tests exist for every AC
- [ ] Test names clearly describe what they test
- [ ] Tests would catch real regressions (not just happy path)
- [ ] No tests that only test mocks (test the implementation, not the test doubles)
- [ ] Coverage: all branches tested

**Blockers**: Missing AC tests, or tests that always pass regardless of code.

---

### 3. Security (OWASP Top 10 scan)

- [ ] Input validation on all external inputs
- [ ] No SQL/NoSQL injection vulnerabilities
- [ ] No XSS vulnerabilities (if applicable)
- [ ] Authentication checks present
- [ ] Authorization: users can only access their own data
- [ ] No secrets or credentials in code
- [ ] Error messages don't leak stack traces or internal paths
- [ ] Sensitive data not logged

**Any finding here is a blocker.**

---

### 4. Code Quality

- [ ] Functions/methods have single responsibilities
- [ ] Naming is clear and consistent
- [ ] No duplicated logic (DRY violations)
- [ ] Complexity: any function with cyclomatic complexity > 10 should be flagged
- [ ] No dead code
- [ ] Error handling: errors are caught, logged appropriately, and propagated correctly

---

### 5. Architecture Conformance

- [ ] Follows the component boundaries defined in architecture doc
- [ ] Uses the agreed-upon tech stack (no unapproved new dependencies)
- [ ] Data flows through correct layers
- [ ] No direct cross-module coupling that bypasses defined interfaces

---

## Review Output Format

```markdown
## Code Review — {story_id} / {branch_name}

**Overall Status:** ✅ Approved | ⚠️ Approved with Comments | 🔴 Needs Work | 🚫 Blocked

### Blockers (must fix before merge)
- [BLOCKER] {specific issue + location + how to fix}

### Required Changes
- [REQUIRED] {issue + location + suggested fix}

### Suggestions (optional but recommended)
- [SUGGEST] {improvement + rationale}

### Positives
- {things done well — always include at least 2}

### AC Coverage
| AC | Implemented | Test Exists | Notes |
|----|-------------|-------------|-------|
| AC-1 | ✅ | ✅ | |
| AC-2 | ✅ | ⚠️ | Partial coverage |

### Security Scan
| Check | Status |
|-------|--------|
| Input validation | ✅ |
| No hardcoded secrets | ✅ |
| Auth checks | ✅ |
```

---

## Completion

- **If Approved**: Ask if they want to create a PR (`github-create-pr`) or update JIRA
- **If Needs Work**: List top 3 priorities to fix, then offer to re-review
- **If Blocked**: Clearly name the blocker and what must change — do not soften
