# Skill: QA Sign-off

> **Activation**: `#file:_superml/skills/6-quality/qa-signoff/SKILL.md`

---

## Purpose

Conduct a formal QA sign-off — a structured gate review that confirms all quality criteria are met and the product is ready for release. This is the final QA deliverable.

---

## Inputs

Load before starting:
- Test plan: `{output_path}/qa/test-plan.md`
- Test execution report: `{output_path}/qa/test-execution.md`
- Bug triage log: `{output_path}/qa/bug-triage.md`

---

## Deliverable

**`{output_path}/qa/qa-signoff.md`**

After completing, update `_superml/config.yml`:
```yaml
artifacts:
  qa_signed_off: true
```

---

## Sign-off Document Structure

```markdown
# QA Sign-off — {project_name}

**Date**: {date}
**QA Lead**: {qa_name}
**Release**: {version / sprint / milestone}

## Sign-off Decision

> ✅ APPROVED FOR RELEASE  /  ❌ NOT APPROVED — see blockers below

## Sign-off Checklist

### Test Coverage
- [ ] All P1 test cases passed
- [ ] All P2 test cases passed (or explicitly accepted by stakeholders)
- [ ] Regression test suite passed
- [ ] Exploratory testing complete

### Defect Status
- [ ] Zero open P1 bugs
- [ ] Zero open P2 bugs (or written exception signed by Product)
- [ ] All resolved bugs verified by QA re-test

### Documentation
- [ ] Test plan complete and up to date
- [ ] Test execution report complete
- [ ] Bug triage log complete and all entries resolved or accepted

### Non-Functional
- [ ] Performance acceptable (if tested)
- [ ] Security checks passed (if applicable)
- [ ] Accessibility tested (if applicable)

## Outstanding Items (if any)

| Item | Severity | Owner | Resolution Plan |
|------|----------|-------|-----------------|
| — | — | — | — |

## Approval

| Role | Name | Decision | Date |
|------|------|----------|------|
| QA Lead | {qa_name} | Approved / Rejected | {date} |
| Product Owner | | Approved / Rejected | |
| Tech Lead | | Approved / Rejected | |

## Notes

{Any additional context, known limitations, or conditions on sign-off}
```

---

## Validation Checklist

- [ ] All checklist items assessed (not just ticked)
- [ ] Any exceptions documented with stakeholder sign-off
- [ ] Decision is clear: APPROVED or NOT APPROVED
- [ ] `artifacts.qa_signed_off` updated in `_superml/config.yml`

---

## Next Phase

After QA sign-off is set, hand over to **Release Manager** (`#file:_superml/skills/7-release/agent-release/SKILL.md`).
