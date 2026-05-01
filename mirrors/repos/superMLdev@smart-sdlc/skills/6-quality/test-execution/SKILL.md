# Skill: Test Execution

> **Activation**: `#file:_superml/skills/6-quality/test-execution/SKILL.md`

---

## Purpose

Execute the test plan systematically, record results for every test case, capture evidence, and produce a test execution report. Identify and log all defects found during execution.

---

## Inputs

Load before starting:
- Test plan: `{output_path}/qa/test-plan.md`
- Implementation context (source, PR links, build number)

---

## Deliverable

**`{output_path}/qa/test-execution.md`**

---

## Test Execution Report Structure

```markdown
# Test Execution Report — {project_name}

## Summary
| Metric | Value |
|--------|-------|
| Total test cases | N |
| Passed | N |
| Failed | N |
| Blocked | N |
| Not executed | N |
| Pass rate | % |

## Execution Details

| TC-ID | Description | Status | Notes / Evidence | Defect Ref |
|-------|-------------|--------|-----------------|-----------|
| TC-001 | ... | PASS | ... | — |
| TC-002 | ... | FAIL | Steps 3–4 fail on Firefox | BUG-001 |

## Defects Raised

| Bug-ID | TC-ID | Summary | Severity | Status |
|--------|-------|---------|----------|--------|
| BUG-001 | TC-002 | ... | P2 | Open |

## Environment & Build
- Environment: ...
- Build / version: ...
- Date: {date}
- Executed by: {qa_name}

## Blockers & Notes
- ...
```

---

## During Execution

- Execute test cases in priority order (P1 first).
- For each failure: document exact steps that failed, actual vs expected result, and link to evidence (screenshot, log snippet).
- Log each defect immediately in the bug triage log.
- Mark test cases as Blocked only if a prerequisite failure prevents execution.

---

## Validation Checklist

- [ ] All P1 test cases executed
- [ ] All P2 test cases executed (or explicitly deferred with reason)
- [ ] Every failure has a linked defect in the bug log
- [ ] Summary statistics are accurate
- [ ] Report includes environment and build information

---

## Next Skill

If defects found → run **Bug Triage** (`#file:_superml/skills/6-quality/bug-triage/SKILL.md`)  
When all P1/P2 defects resolved → run **QA Sign-off** (`#file:_superml/skills/6-quality/qa-signoff/SKILL.md`)
