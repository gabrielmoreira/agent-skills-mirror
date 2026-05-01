# Step 03 — Review and Finalize

**Previous step:** `step-02-draft.md`
**Next step:** (none — this is the final step)

---

## 1. Completeness Check

Run through this checklist against the drafted PRD:

| Check | Status |
|-------|--------|
| Overview is clear and non-technical | ✅ / ❌ |
| Goals are measurable | ✅ / ❌ |
| Non-goals explicitly listed | ✅ / ❌ |
| Every persona has a clear goal | ✅ / ❌ |
| Every FR has a user story | ✅ / ❌ |
| Every FR has at least 2 acceptance criteria | ✅ / ❌ |
| Acceptance criteria are testable (Given/When/Then) | ✅ / ❌ |
| NFRs cover performance, security, scale | ✅ / ❌ |
| All open questions are captured | ✅ / ❌ |
| No ambiguous language ("fast", "easy", "simple") | ✅ / ❌ |

For each ❌, flag it to the user and ask for resolution or explicit acknowledgment as a known gap.

⏸️ **STOP** — present the checklist results and resolve issues.

---

## 2. Ambiguity Scan

Scan each requirement for:
- Vague adjectives: "fast", "scalable", "easy", "modern", "clean"
- Missing actors: "the system should" without saying who triggers it
- Missing error paths: requirements that only describe the happy path
- Unmeasurable outcomes: "users will be satisfied"

Flag each instance and ask the user to clarify or accept the ambiguity as a known risk.

---

## 3. Dependency Validation

Review each listed dependency:
- Is the dependency owner identified?
- Is the dependency's readiness known?
- Is there a risk if the dependency slips?

If any dependency is unresolved, add it to Open Questions with an owner assigned.

---

## 4. Finalize PRD

Update the PRD frontmatter:
```yaml
status: "approved"
version: 1
approvedBy: {user_name}
approvedDate: {date}
stepsCompleted: ["step-01-requirements", "step-02-draft", "step-03-finalize"]
```

---

## 5. Offer Integration Actions

Present options:

> "Your PRD is finalized. What would you like to do next?"

| # | Action |
|---|--------|
| 1 | Push PRD to Confluence (`confluence-push-doc`) |
| 2 | Talk to Rex (Architect) to design the system architecture |
| 3 | Have Rex create epics and stories from this PRD |
| 4 | Done — I'll come back to this later |

⏸️ **STOP** — wait for user choice.

---

## 6. Completion

> "✅ PRD saved at `{planning_artifacts}/prd/{project_name}-prd.md` (v1, approved).
>
> **Suggested next step:** Rex (System Architect) can use this PRD to design the architecture and break it into epics and stories."
