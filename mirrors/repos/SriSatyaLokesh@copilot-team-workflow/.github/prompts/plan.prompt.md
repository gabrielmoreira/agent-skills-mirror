---
description: 'Use after research is complete, before writing any code — when a developer says "create a plan", "plan this feature", "break down the tasks", "what are the implementation steps?", or "how should I approach this?". Creates an ordered implementation checklist with architecture decisions, tasks, tests, and acceptance criteria. Requires Phase 1 (requirements) and Phase 2 (research) to be complete.'
agent: 'Planner'
---
# Plan — Break Down Implementation Tasks

Create a structured implementation plan before writing any code.

**Issue doc**: ${input:issue-doc:Path to Issue doc (e.g., docs/issues/ISSUE-042-name.md)}

---

## Step 1 — Verify Prerequisites

The Planner agent will check:
- ✅ Phase 1 (Discuss) is complete — requirements are confirmed
- ✅ Phase 2 (Research) is complete — codebase context is gathered

If either phase is incomplete, the agent will stop and ask you to complete the missing phase first.

---

## Step 2 — Create the Plan

The Planner will:
1. Review the requirements from Phase 1
2. Review the research findings from Phase 2
3. Ask 2-3 clarifying questions if anything is ambiguous
4. Draft an implementation plan with:
   - Architecture decisions (and rationale)
   - Ordered task checklist (backend, frontend, infrastructure, tests, docs)
   - Test coverage plan
   - Acceptance criteria
   - Open questions requiring human input

---

## Step 3 — Review and Approve

The Planner presents the plan for your review. Provide feedback if needed:
- Are the tasks in the right order?
- Are there any missing steps?
- Do the architecture decisions make sense?

Once approved, the plan is written to Phase 3 of the Issue doc.

---

## What Happens Next

After the plan is approved:
- The Planner marks Phase 3 as `[x] complete`
- Logs the planning activity to `logs/copilot/agent-activity.log`
- Offers execution routing guidance:
   - Run `/execute` with this work folder
   - Choose **Mode A (Agent Mode)** or **Mode B (TDD Agent)**
   - For Mode A, reselect agent mode before implementation begins

Use `/execute` to begin implementation with the selected mode.

---

## Example Plan Output

```markdown
## Architecture Decision
Use the existing Redis `rate:${type}:${identifier}` key pattern.
Window: 15 min. Max attempts: 5.

## Tasks
- [ ] Test: rate limit middleware (unit)
- [ ] Implement: rate-limit.ts middleware
- [ ] Test: admin bypass behavior
- [ ] Implement: admin role check
- [ ] Test: login route integration
- [ ] Apply: middleware to POST /auth/login

## Acceptance Criteria
- [ ] User locked out after 5 failed attempts
- [ ] Lockout expires after 15 minutes
- [ ] Admin users never rate-limited
- [ ] 429 response includes Retry-After header
```
