---
name: subagent-driven-development
description: "Executes an implementation plan by dispatching a fresh subagent per 2-5 minute task, then two-stage review (spec compliance, then code quality) before the next task. Use when a written plan exists, tasks are mostly independent, and quality gates matter. Not for work with no plan, tightly coupled sequential edits, or a trivial one-file change."
version: 1.1.1
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [delegation, subagent, implementation, workflow, parallel, review, tdd]
    related_skills: [plan, requesting-code-review, test-driven-development, systematic-debugging]
---

# Subagent-Driven Development

## Overview

Execute implementation plans by dispatching fresh subagents per task with a systematic two-stage review pipeline: **spec compliance first, code quality second**. Each task gets its own implementer subagent with clean context, followed by two independent reviewer subagents that gate progression.

**Core principle:** Fresh subagent per task + two-stage review (spec then quality) = high quality, fast iteration, no context pollution.

## When to Use

Use this skill when **any** of the following are true:

- You have an implementation plan (from the `plan` skill, a plan file, or user requirements broken into tasks)
- Tasks are mostly independent and can be executed sequentially or in parallel
- Quality and spec compliance are important — you need gates, not just "it ran"
- You want automated review between tasks to catch issues before they compound

**Do NOT use when:**
- You have no plan or task breakdown — create one with the `plan` skill first
- Tasks are deeply interdependent and cannot be reviewed in isolation
- The work is a single trivial change (just do it directly)

**vs. manual execution in a single session:**
- Fresh context per task — no confusion from accumulated state across tasks
- Automated review process catches issues early, before they propagate
- Consistent quality checks across all tasks
- Subagents can ask clarifying questions before starting work

## Prerequisites

1. **An implementation plan** — either a plan file (e.g., `docs/plans/feature-plan.md`) or a structured task list. If you don't have one, use the `plan` skill first.
2. **Task granularity of 2–5 minutes each.** If a task is larger, split it before starting.
3. **Project context available** — language, framework, test runner, existing file structure, dependencies.
4. **`delegate_task` capability** — the controller agent must be able to dispatch subagents with specified toolsets.

## Procedure

### Step 1 — Read and Parse the Plan (Once)

Read the plan file **once** in the controller session. Extract ALL tasks with their full text and context upfront. Do not make subagents re-read the plan file — you will provide full task text directly in each subagent's context.

Create a todo list capturing every task:

```python
# Read the plan
read_file("docs/plans/feature-plan.md")

# Create todo list with all tasks
todo([
    {"id": "task-1", "content": "Create User model with email field", "status": "pending"},
    {"id": "task-2", "content": "Add password hashing utility", "status": "pending"},
    {"id": "task-3", "content": "Create login endpoint", "status": "pending"},
])
```

**Key rule:** Read the plan ONCE. Extract everything. Each subagent receives the full task text inline — never instruct a subagent to read the plan file itself.

### Step 2 — Per-Task Workflow (Repeat for Every Task)

For EACH task in the plan, execute the four-phase loop below. Do not advance to the next task until the current task passes both reviews.

#### Phase 2a — Dispatch Implementer Subagent

Use `delegate_task` with complete context including: the task spec, TDD instructions, and project context (scene-setting).

```python
delegate_task(
    goal="Implement Task 1: Create User model with email and password_hash fields",
    context="""
    TASK FROM PLAN:
    - Create: src/models/user.py
    - Add User class with email (str) and password_hash (str) fields
    - Use bcrypt for password hashing
    - Include __repr__ for debugging

    FOLLOW TDD:
    1. Write failing test in tests/models/test_user.py
    2. Run: pytest tests/models/test_user.py -v (verify FAIL)
    3. Write minimal implementation
    4. Run: pytest tests/models/test_user.py -v (verify PASS)
    5. Run: pytest tests/ -q (verify no regressions)
    6. Commit: git add -A && git commit -m "feat: add User model with password hashing"

    PROJECT CONTEXT:
    - Python 3.11, Flask app in src/app.py
    - Existing models in src/models/
    - Tests use pytest, run from project root
    - bcrypt already in requirements.txt
    """,
    toolsets=['terminal', 'file']
)
```

**If the subagent asks questions:** Answer clearly and completely before letting it proceed. Provide additional context if needed. Do not rush it into implementation.

#### Phase 2b — Dispatch Spec Compliance Reviewer

After the implementer completes, verify the implementation against the **original spec** — not against what the implementer thought they were asked to do.

```python
delegate_task(
    goal="Review if implementation matches the spec from the plan",
    context="""
    ORIGINAL TASK SPEC:
    - Create src/models/user.py with User class
    - Fields: email (str), password_hash (str)
    - Use bcrypt for password hashing
    - Include __repr__

    CHECK:
    - [ ] All requirements from spec implemented?
    - [ ] File paths match spec?
    - [ ] Function signatures match spec?
    - [ ] Behavior matches expected?
    - [ ] Nothing extra added (no scope creep)?

    OUTPUT: PASS or list of specific spec gaps to fix.
    """,
    toolsets=['file']
)
```

**If spec issues found:** Dispatch a fix subagent (or re-dispatch the implementer) with specific instructions about the gaps. Then re-run the spec review. Continue only when the reviewer outputs `PASS`.

**HARD RULE:** Never start code quality review before spec compliance returns `PASS`. The order is non-negotiable: spec first, quality second.

#### Phase 2c — Dispatch Code Quality Reviewer

Only after spec compliance passes:

```python
delegate_task(
    goal="Review code quality for Task 1 implementation",
    context="""
    FILES TO REVIEW:
    - src/models/user.py
    - tests/models/test_user.py

    CHECK:
    - [ ] Follows project conventions and style?
    - [ ] Proper error handling?
    - [ ] Clear variable/function names?
    - [ ] Adequate test coverage?
    - [ ] No obvious bugs or missed edge cases?
    - [ ] No security issues?

    OUTPUT FORMAT:
    - Critical Issues: [must fix before proceeding]
    - Important Issues: [should fix]
    - Minor Issues: [optional]
    - Verdict: APPROVED or REQUEST_CHANGES
    """,
    toolsets=['file']
)
```

**If quality issues found:** Fix critical and important issues (minor are optional), then re-review. Continue only when the reviewer returns `APPROVED`.

**HARD RULE:** Never let the implementer self-review replace either of these review stages. Both spec and quality reviews must be independent subagents.

#### Phase 2d — Mark Task Complete

```python
todo([{"id": "task-1", "content": "Create User model with email field", "status": "completed"}], merge=True)
```

### Step 3 — Final Integration Review

After ALL tasks are complete, dispatch a final integration reviewer to check cross-task consistency:

```python
delegate_task(
    goal="Review the entire implementation for consistency and integration issues",
    context="""
    All tasks from the plan are complete. Review the full implementation:
    - Do all components work together?
    - Any inconsistencies between tasks?
    - All tests passing?
    - Ready for merge?
    """,
    toolsets=['terminal', 'file']
)
```

For the final integration review, use the review dimensions from the `requesting-code-review` skill.

### Step 4 — Verify and Commit

Run the full test suite and review all changes before the final commit:

**Windows (PowerShell):**
```powershell
# Run full test suite
pytest tests/ -q

# Review all changes
git diff --stat

# Final commit if needed
git add -A; git commit -m "feat: complete [feature name] implementation"
```

**Linux/macOS:**
```bash
# Run full test suite
pytest tests/ -q

# Review all changes
git diff --stat

# Final commit if needed
git add -A && git commit -m "feat: complete [feature name] implementation"
```

## Task Granularity

**Each task = 2–5 minutes of focused work.**

| Too big | Right size |
|---|---|
| "Implement user authentication system" | "Create User model with email and password fields" |
| | "Add password hashing function" |
| | "Create login endpoint" |
| | "Add JWT token generation" |
| | "Create registration endpoint" |

If a task feels larger than 5 minutes, split it into sub-tasks before dispatching.

## Handling Issues

### If a Subagent Asks Questions
- Answer clearly and completely
- Provide additional context if needed
- Do not rush them into implementation — unanswered questions lead to wrong implementations

### If a Reviewer Finds Issues
- Dispatch a fix subagent (or re-dispatch the implementer) with specific instructions about what went wrong
- Re-run the same review stage after the fix
- Repeat until that stage passes
- **Never skip the re-review** — a fix without re-review is an unverified fix

### If a Subagent Fails a Task
- Dispatch a new fix subagent with specific instructions about what went wrong
- **Do not try to fix manually in the controller session** — this causes context pollution and defeats the purpose of fresh subagents

## Pitfalls — Never Do These

1. **Start implementation without a plan.** Always have a task breakdown first.
2. **Skip reviews** — neither spec compliance nor code quality may be skipped.
3. **Proceed with unfixed critical or important issues.** Fix and re-review first.
4. **Dispatch multiple implementation subagents for tasks that touch the same files** in parallel — this causes conflicts. Run them sequentially.
5. **Make subagents read the plan file.** Provide full task text directly in context instead.
6. **Skip scene-setting context.** Subagents need to understand where the task fits in the project.
7. **Ignore subagent questions.** Answer before letting them proceed.
8. **Accept "close enough" on spec compliance.** Either it matches the spec or it doesn't.
9. **Skip review loops.** Reviewer found issues → implementer fixes → review again. Always.
10. **Let implementer self-review replace actual review.** Both spec and quality reviews must be independent subagents.
11. **Start code quality review before spec compliance is PASS.** Wrong order — spec first, quality second.
12. **Move to the next task while either review has open issues.** Both must be cleared.

## Verification

After the full workflow completes, verify the outcome:

```bash
# All tests pass
pytest tests/ -q
# Expected: all tests pass, 0 failures

# No uncommitted changes left behind (or intentional final commit)
git status
# Expected: clean working tree (or only expected untracked files)

# Review the full diff
git diff --stat
# Expected: only files from the plan, no unexpected changes

# Verify each task has a commit
git log --oneline -10
# Expected: commits matching each task's commit message
```

**Checklist before declaring done:**
- [ ] Every task in the todo list is marked `completed`
- [ ] Every task passed spec compliance review (`PASS`)
- [ ] Every task passed code quality review (`APPROVED`)
- [ ] Final integration review completed with no open issues
- [ ] Full test suite passes
- [ ] All changes committed

## Efficiency Notes

**Why fresh subagent per task:**
- Prevents context pollution from accumulated state
- Each subagent gets clean, focused context
- No confusion from prior tasks' code or reasoning

**Why two-stage review (spec then quality):**
- Spec review catches under-building (missing requirements) and over-building (scope creep) early
- Quality review ensures the implementation is well-built
- Catches issues before they compound across tasks

**Cost trade-off:**
- More subagent invocations (implementer + 2 reviewers per task)
- But catches issues early — far cheaper than debugging compounded problems later

## Integration with Other Skills

### With `plan`
This skill **executes** plans created by the `plan` skill:
1. User requirements → `plan` → implementation plan
2. Implementation plan → `subagent-driven-development` → working code

### With `test-driven-development`
Implementer subagents should follow TDD. Include TDD instructions in every implementer context:
1. Write failing test first
2. Implement minimal code
3. Verify test passes
4. Commit

### With `requesting-code-review`
The two-stage review process IS the code review for each task. For the final integration review, use the `requesting-code-review` skill's review dimensions.

### With `systematic-debugging`
If a subagent encounters bugs during implementation:
1. Follow the `systematic-debugging` process
2. Find root cause before fixing
3. Write a regression test
4. Resume implementation

## Example Workflow

```
[Read plan: docs/plans/auth-feature.md]
[Create todo list with 5 tasks]

--- Task 1: Create User model ---
[Dispatch implementer subagent]
  Implementer: "Should email be unique?"
  You: "Yes, email must be unique"
  Implementer: Implemented, 3/3 tests passing, committed.

[Dispatch spec reviewer]
  Spec reviewer: ✅ PASS — all requirements met

[Dispatch quality reviewer]
  Quality reviewer: ✅ APPROVED — clean code, good tests

[Mark Task 1 complete]

--- Task 2: Password hashing ---
[Dispatch implementer subagent]
  Implementer: No questions, implemented, 5/5 tests passing.

[Dispatch spec reviewer]
  Spec reviewer: ❌ Missing: password strength validation (spec says "min 8 chars")

[Dispatch fix subagent]
  Fix subagent: Added validation, 7/7 tests passing.

[Dispatch spec reviewer again]
  Spec reviewer: ✅ PASS

[Dispatch quality reviewer]
  Quality reviewer: Important — magic number 8, extract to constant
  Fix subagent: Extracted MIN_PASSWORD_LENGTH constant
  Quality reviewer: ✅ APPROVED

[Mark Task 2 complete]

... (continue for all tasks)

[After all tasks: dispatch final integration reviewer]
[Run full test suite: all passing]
[Done!]
```

## References (Load When Relevant)

When orchestration involves significant context usage, long review loops, or complex validation checkpoints, load these reference files for the specific discipline:

- **`references/context-budget-discipline.md`** — Four-tier context degradation model (PEAK / GOOD / DEGRADING / POOR), read-depth rules that scale with context window size, and early warning signs of silent degradation. **Load when** a run will clearly consume significant context (multi-phase plans, many subagents, large artifacts).

- **`references/gates-taxonomy.md`** — The four canonical gate types (Pre-flight, Revision, Escalation, Abort) with behavior, recovery, and examples. **Load when** designing or reviewing any workflow that has validation checkpoints — use the vocabulary explicitly so each gate has defined entry, failure behavior, and resumption rules.

Both references adapted from gsd-build/get-shit-done (MIT © 2025 Lex Christopherson).

## Remember

```
Fresh subagent per task
Two-stage review every time
Spec compliance FIRST
Code quality SECOND
Never skip reviews
Catch issues early
```

**Quality is not an accident. It's the result of systematic process.**
