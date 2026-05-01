# Quality Checklist

## At a glance

- **Purpose:** Extract implementation guidance from PRs and assess risk before you implement the fix yourself.
- **Use when:** You are deciding whether a PR is a good “reference implementation,” or you’re planning tests/edge cases.
- **Output:** Risk notes + test plan + any constraints to preserve.
- **Note:** This is **not** a merge gate for external PRs.

Use this checklist to extract insights and assess risk. It is not a merge gate for external PRs.

## PR Analysis Checklist

Use this when extracting insights from PRs to inform your own implementation.

### Automated Signals

Check CI/CD results (indicates if their approach works):
- [ ] Tests pass
- [ ] Linting passes
- [ ] Build succeeds
- [ ] Coverage maintained or improved

### Code Quality

- [ ] Logic is correct (actually solves the stated problem)
- [ ] Edge cases handled appropriately
- [ ] Error handling is adequate (not silent failures)
- [ ] No obvious performance issues
- [ ] No security vulnerabilities introduced

### Style and Patterns

- [ ] Follows existing code patterns in the repo
- [ ] Consistent naming conventions
- [ ] Appropriate abstraction level (not over/under-engineered)
- [ ] Comments where logic is non-obvious

### Testing

- [ ] New functionality has tests
- [ ] Tests are meaningful (not just coverage padding)
- [ ] Tests cover both happy path and error cases
- [ ] Tests are maintainable and readable

### Documentation

- [ ] Public API changes documented
- [ ] README updated if user-facing behavior changed
- [ ] Changelog entry if needed
- [ ] Code comments for complex logic

### Relationship Quality

- [ ] PR intent matches linked issue intent
- [ ] No mismatch between reported symptoms and implemented fix
- [ ] Relationship quality noted (strong/medium/weak)

### Breaking Changes

If breaking changes present:
- [ ] Clearly documented in PR description
- [ ] Migration path provided
- [ ] Version bump appropriate (semver)

## Risk Assessment

### File Risk Levels

| Location | Risk | Reason |
|----------|------|--------|
| Core/critical paths | HIGH | Wide impact, careful review |
| User-facing features | MEDIUM | Visible bugs, moderate impact |
| Tests | LOW | Isolated, easy to fix |
| Documentation | LOW | No runtime impact |
| Configuration | VARIES | Depends on what's configured |

### Change Size

| Size | Files | Lines | Review Approach |
|------|-------|-------|-----------------|
| Small | 1-3 | <50 | Quick review |
| Medium | 4-10 | 50-200 | Careful review |
| Large | 10+ | 200+ | Consider splitting |

### Complexity Signals

Red flags requiring extra scrutiny:
- Refactoring + new features in same PR
- Changes to error handling or retry logic
- Concurrency or async changes
- Security-sensitive areas (auth, input validation)
- Database schema changes
- API contract changes

## Issue Quality Assessment

### Well-Formed Bug Report

- [ ] Clear title describing the problem
- [ ] Steps to reproduce
- [ ] Expected behavior
- [ ] Actual behavior
- [ ] Environment details (OS, version, etc.)
- [ ] Error messages/stack traces if applicable

### Well-Formed Feature Request

- [ ] Clear description of desired functionality
- [ ] Use case / motivation explained
- [ ] Consideration of alternatives
- [ ] Scope is reasonable

### Actionability Score

| Score | Criteria |
|-------|----------|
| High | All needed info present, can start work immediately |
| Medium | Most info present, minor clarification needed |
| Low | Missing critical info, needs follow-up |
| None | Too vague to act on |

## Agent Brief Quality

When creating agent briefs, ensure:

- [ ] Clear problem statement (what to solve)
- [ ] Specific acceptance criteria (how to verify)
- [ ] Relevant context links (issues, PRs, files)
- [ ] Constraints noted (don't change X, maintain compatibility with Y)
- [ ] Scope bounded (what's NOT in scope)

### Agent Brief Template

```markdown
## Task: [Title]

**Intent:** [What problem this solves]

**Context:**
- Related issue: [ISSUE:XX]
- Key files: `src/path/file.ts`

**Acceptance Criteria:**
- [ ] [Specific, testable criterion]
- [ ] [Another criterion]

**Constraints:**
- Do not change [X]
- Must maintain backwards compatibility with [Y]

**Out of Scope:**
- [Related but excluded work]
```

## Repo Health Checklist

Use during opportunity scans:

- [ ] README has a clear quickstart and examples
- [ ] Docs match current behavior
- [ ] CI is reliable and fast enough
- [ ] Tests cover critical paths
- [ ] Releases are documented and easy to follow
