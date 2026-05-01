# Skill: Test Plan

> **Activation**: `#file:_superml/skills/6-quality/test-plan/SKILL.md`

---

## Purpose

Create a comprehensive test plan that maps every acceptance criterion in the epics to at least one test case, identifies risk areas, and defines the test strategy and scope.

---

## Inputs

Load before starting:
- Epic/story backlog: `{output_path}/planning/epics.md` or equivalent
- Architecture doc: `{output_path}/planning/architecture.md` (for system boundaries)
- PRD: `{output_path}/planning/prd.md` (for functional scope)
- Any existing test strategy in `_superml/reference/qa/`

---

## Deliverable

**`{output_path}/qa/test-plan.md`**

---

## Test Plan Structure

Generate the test plan with these sections:

```markdown
# Test Plan — {project_name}

## 1. Scope & Objectives
- What is in scope for this test cycle
- What is explicitly out of scope
- Quality objectives and exit criteria

## 2. Test Strategy
- Testing levels: unit / integration / system / UAT
- Test types: functional, regression, exploratory, performance (if applicable)
- Test environment(s) and data requirements

## 3. Test Cases

### {Epic / Feature Name}
| TC-ID | Story | Description | Test Steps | Expected Result | Priority |
|-------|-------|-------------|-----------|-----------------|----------|
| TC-001 | US-001 | ... | 1. ... 2. ... | ... | P1 |

## 4. Risk Register
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|

## 5. Entry & Exit Criteria
### Entry (before testing starts)
- [ ] Implementation signed off
- [ ] Test environment ready
- [ ] Test data prepared

### Exit (before sign-off)
- [ ] All P1/P2 test cases pass
- [ ] No open P1/P2 bugs
- [ ] Test execution report complete
```

---

## Validation Checklist

Before saving the test plan:
- [ ] Every acceptance criterion maps to at least one test case
- [ ] All test cases have a priority (P1/P2/P3)
- [ ] Risk areas identified and mitigated
- [ ] Entry and exit criteria defined
- [ ] Environment and data requirements documented

---

## Next Skill

After test plan is approved → run **Test Execution** (`#file:_superml/skills/6-quality/test-execution/SKILL.md`)
