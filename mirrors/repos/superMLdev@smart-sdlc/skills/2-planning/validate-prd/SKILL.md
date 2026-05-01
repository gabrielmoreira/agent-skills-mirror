---
name: validate-prd
description: "Validate a PRD for completeness, consistency, and implementation readiness. Use when the user says 'validate the PRD', 'review requirements', or 'is the PRD ready for development'."
---

# Validate PRD

## Goal

Run a structured validation of an existing PRD and produce a readiness report with a clear PASS / NEEDS WORK / FAIL verdict.

## Activation

1. Read `{project-root}/_superml/config.yml`
2. Ask: "Which PRD should I validate? (path or name)" — default: latest file in `{planning_artifacts}/prd/`
3. Load the specified PRD file

## Validation Dimensions

Run checks across 5 dimensions. Score each as ✅ Pass, ⚠️ Needs Work, or ❌ Fail.

### 1. Completeness

- [ ] Overview section present and substantive
- [ ] Goals defined and measurable
- [ ] Non-goals listed
- [ ] At least one user persona defined
- [ ] All mentioned personas have acceptance flows covered
- [ ] All functional requirements have user stories
- [ ] All FRs have at least 2 acceptance criteria
- [ ] Non-functional requirements present (performance, security, scale)
- [ ] Open questions section present (even if empty)

### 2. Testability

For each acceptance criterion, verify:
- [ ] Written in Given/When/Then or equivalent testable form
- [ ] No vague adjectives: "fast", "easy", "clean", "modern", "scalable"
- [ ] Error/edge cases covered alongside happy paths
- [ ] Numbers used instead of adjectives where applicable ("< 200ms" not "fast")

### 3. Consistency

- [ ] No conflicting requirements (FR-X says A, FR-Y says not-A)
- [ ] Terminology consistent throughout (same thing isn't called different names)
- [ ] Priorities (Core/Important/Nice) are consistent with stated goals
- [ ] Dependencies match what's described in the architecture or external systems

### 4. Stakeholder Coverage

- [ ] All user personas have requirements that serve their goals
- [ ] No user type mentioned in personas but missing from requirements
- [ ] Admin/operator flows covered (not just end-user flows)
- [ ] Error handling and edge cases considered for each persona

### 5. Implementation Readiness

- [ ] A developer could start from this PRD without additional clarification sessions
- [ ] No requirements that depend on unresolved open questions
- [ ] Technical constraints are concrete enough to guide architecture decisions
- [ ] Success metrics are defined and measurable post-launch

## Validation Report

Produce a report:

```markdown
# PRD Validation Report
**PRD:** {file path}
**Validated:** {date}
**Validator:** SuperML (agent-pm)

## Verdict: {PASS | NEEDS WORK | FAIL}

## Score Summary
| Dimension | Score | Issues |
|-----------|-------|--------|
| Completeness | X/9 | ... |
| Testability | X/5 | ... |
| Consistency | X/4 | ... |
| Stakeholder Coverage | X/4 | ... |
| Implementation Readiness | X/5 | ... |

## Issues Found
[List each ⚠️ and ❌ finding with specific location and recommended fix]

## Recommended Actions
[Ordered list of actions to address issues]
```

Present the report and ask: "Would you like to fix these issues now or proceed anyway?"

⏸️ **STOP** — wait for user decision.
