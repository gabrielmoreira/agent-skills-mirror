---
applyTo: "**"
description: 'Use when 3 or more implementation tasks are independent of each other — when tasks touch different files, different subsystems, or have no shared state — to dispatch them as parallel subagents instead of working sequentially.'
---
# Parallel Agents vs Subagent-Driven Development

Understanding when to use parallel agents versus sequential subagent dispatch is critical.
**Wrong choice = wasted time or broken integrations.**

---

## The Core Distinction

| | Subagent-Driven Development | Parallel Agent Dispatch |
|:---|:---|:---|
| **When** | Complex task needing fresh context per step | Multiple independent tasks that can run simultaneously |
| **Flow** | Parent → Subagent → Review → Next Subagent (sequential) | Parent → [Subagent A + Subagent B + Subagent C] (concurrent) |
| **Dependencies** | Tasks depend on each other's output | Tasks are completely independent |
| **Integration** | Each subagent hands off to the next | Parent integrates all results at the end |
| **Example** | Create schema → Build service using schema → Write tests | Fix auth bug + Fix logging bug + Fix email bug |

---

## Decision Flowchart

```
Do you have 3+ tasks?
       │
       ▼
Are all tasks independent?
(different files / different subsystems / no shared state between them)
       │
   YES ▼                          NO → Use sequential execution (default TDD cycle)
       │
Are all tasks small enough to complete in one context window?
       │
   YES ▼                          NO → Break task further, then parallelize
       │
Use Parallel Dispatch → [Agent A] [Agent B] [Agent C] run concurrently
       │
       ▼
Collect all results → Verify no conflicts → Run full test suite → Integrate
```

---

## When to Use Parallel Dispatch

✅ **Use parallel when ALL of these are true:**
- 3 or more tasks exist
- Each task touches different files or subsystems
- No task depends on another task's output
- Agents won't write to the same files

✅ **Common parallel scenarios:**
- Fixing bugs in separate services (auth bug + logging bug + email bug)
- Implementing features in separate modules (user module + payment module + notification module)
- Writing tests for independent components
- Documentation updates across different areas

---

## When NOT to Use Parallel Dispatch

❌ **Do NOT parallelize when:**
- Task B reads outputs that Task A writes
- Tasks need to coordinate on shared state (DB schema, config, shared types)
- You're exploring unfamiliar code (understand first, then dispatch)
- Fewer than 3 independent tasks
- Tasks could conflict on the same files

❌ **Common mistakes:**
- Parallelizing "create schema → use schema" (Task 2 depends on Task 1)
- Parallelizing tasks that write to the same config file
- Parallelizing too early before understanding dependencies

---

## How to Dispatch Parallel Agents (Copilot Method)

1. **Identify independent domains** from the plan:
   ```
   Task A: Fix auth/session.service.ts — no shared state
   Task B: Fix notifications/email.service.ts — no shared state
   Task C: Fix analytics/logger.service.ts — no shared state
   ✅ All independent → parallelize
   ```

2. **Create a focused task prompt for each agent** (be specific):
   ```
   Agent A Task: "Fix the session expiry bug in auth/session.service.ts.
   - The test 'should expire sessions after timeout' is failing.
   - Root cause: refreshExpiry() not called on activity.
   - Do NOT change any other files.
   - Return: summary of what changed and which tests now pass."
   ```

3. **Run all agents concurrently** using Copilot agent handoffs or multiple chat windows.

4. **Integrate results:**
   - Review each agent's summary
   - Check for any conflicting changes
   - Run `npm test` across the full suite
   - Merge all changes

---

## Subagent-Driven Development (Sequential Pattern)

Use this when tasks are sequential or when each phase requires the previous phase's output:

```
Phase 1: Create data types and schemas
    ↓ (output: schema files)
Phase 2: Build service layer using Phase 1 types
    ↓ (output: service files)
Phase 3: Write integration tests for Phase 2 services
    ↓ (output: test files)
Phase 4: Review agent checks everything together
```

Each phase hands off to the next. Never parallelize sequential phases.

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why It's Wrong | Fix |
|:---|:---|:---|
| Parallelizing before reading all tasks | Hidden dependency caught too late | Read all tasks first, then decide |
| Using parallel for 2 tasks | Overhead not worth it | Sequential is fine for 1-2 tasks |
| No integration step | Silent conflicts | Always run full test suite after integrating |
| Vague agent prompts | Agent goes off-scope | Specify exact files, exact goal, exact output |
| Different files means independent | Not always — shared types can couple them | Check imports, not just file names |
