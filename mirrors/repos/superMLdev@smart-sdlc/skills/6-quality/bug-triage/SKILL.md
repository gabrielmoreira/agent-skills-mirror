# Skill: Bug Triage

> **Activation**: `#file:_superml/skills/6-quality/bug-triage/SKILL.md`

---

## Purpose

Log, classify, prioritise, and track defects found during test execution. Produce a structured bug triage log that drives resolution and feeds into the QA sign-off decision.

---

## Inputs

- Test execution report: `{output_path}/qa/test-execution.md`
- Developer contact: `@sml-agent-developer` for fix ownership

---

## Deliverable

**`{output_path}/qa/bug-triage.md`**

---

## Bug Triage Log Structure

```markdown
# Bug Triage Log — {project_name}

## Summary
| Severity | Open | In Progress | Resolved | Won't Fix |
|----------|------|------------|----------|-----------|
| P1 — Blocker | N | N | N | N |
| P2 — Critical | N | N | N | N |
| P3 — Major | N | N | N | N |
| P4 — Minor | N | N | N | N |

## Bug Log

### BUG-001 — {short summary}
- **Severity**: P1 / P2 / P3 / P4
- **Status**: Open / In Progress / Resolved / Won't Fix
- **Found in TC**: TC-XXX
- **Summary**: Brief one-line description
- **Steps to Reproduce**:
  1. Step 1
  2. Step 2
- **Expected**: What should happen
- **Actual**: What happened instead
- **Evidence**: Link to screenshot / log
- **Assigned to**: Developer / Team
- **Resolution**: (filled when resolved)
- **Verified by QA**: Yes / No
```

---

## Severity Definitions

| Severity | Definition | Example |
|----------|-----------|---------|
| **P1 — Blocker** | System crash, data loss, security breach, prevents core functionality | Login broken for all users |
| **P2 — Critical** | Major feature broken, significant impact, no workaround | Payment processing fails |
| **P3 — Major** | Feature works partially, workaround available | Report exports wrong format |
| **P4 — Minor** | Cosmetic, low-impact, good-to-fix | Button text has typo |

---

## Triage Process

1. For each failure in the test execution report, create a bug entry.
2. Assign severity using the table above.
3. Assign ownership — P1/P2 → developer immediately; P3/P4 → sprint backlog.
4. Track resolution — re-test when developer marks as fixed.
5. Update `status` field and set `Verified by QA: Yes` when confirmed resolved.

---

## Validation Checklist

- [ ] All test failures have a bug entry
- [ ] All bugs have severity, steps, and expected/actual
- [ ] All P1/P2 bugs have an assigned owner
- [ ] Resolved bugs verified by QA re-test

---

## Next Skill

When all P1/P2 bugs resolved → **QA Sign-off** (`#file:_superml/skills/6-quality/qa-signoff/SKILL.md`)
