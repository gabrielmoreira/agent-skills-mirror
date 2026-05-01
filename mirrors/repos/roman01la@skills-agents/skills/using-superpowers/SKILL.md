---
name: using-superpowers
description: Use when starting any conversation - routes work through the correct worker agents before any task action, requiring explicit worker selection and visible compliance
---

<EXTREMELY-IMPORTANT>
If you think there is even a 1% chance a skill or worker agent might apply to what you are doing, you ABSOLUTELY MUST use it.

IF A SKILL OR WORKER AGENT APPLIES TO THE TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.

This is not negotiable. This is not optional. You cannot rationalize your way out of this.
</EXTREMELY-IMPORTANT>

## Purpose

This skill enforces disciplined execution by requiring:

1. **Skill-first thinking**
2. **Worker-agent routing before any task work**
3. **Visible worker self-identification**
4. **Structured outputs per worker**
5. **No silent fallback to generic behavior**

This skill is a **router + gatekeeper**. It must be applied before planning, coding, testing, reviewing, or clarifying questions whenever a relevant worker agent might help.

---

## Core Rule

**Before any response or action, you must:**

1. Determine whether any skill applies (even 1% chance = yes)
2. Determine whether any worker agent applies
3. Select and announce the worker agent(s)
4. Execute only the current worker
5. Require worker self-identification and structured output

If no worker agent applies, explicitly say so and proceed normally.

---

## Mandatory Worker Routing (No Exceptions)

### Required routing step (before any task work)

Before doing any planning, coding, testing, reviewing, refactoring, or analysis, you must output:

- `Selected worker agents: <ordered list>`
- `Reason: <why these agents>`
- `Current agent: <first agent to execute>`

### No work before routing

Do **not**:
- write code
- propose implementation steps
- review code
- write tests
- summarize fixes
- ask clarifying questions about execution details

until worker routing has been announced.

---

## Worker Self-Identification (Required)

Every response produced under a worker agent must begin with:

- `Active agent: <agent name>`
- `Purpose: <one sentence>`
- `Scope: <what is in scope / out of scope>`

This is required so compliance is visible and auditable.

---

## Worker Compliance Footer (Required)

Every worker response must end with:

- `Worker compliance: followed <agent-name> format`

If a worker cannot follow its format due to missing context, it must say so explicitly and stop.

---

## If No Worker Applies

If no worker agent clearly applies, you must explicitly output:

- `Selected worker agents: none`
- `Reason: no matching worker agent`
- `Current agent: none`

Then proceed with a normal response.

Do not silently skip routing.

---

## Worker Selection Heuristics (Default Pipelines)

Use these default pipelines unless there is a strong reason to change them.

### 1) New feature / behavior change
Default pipeline:
- `task-planner -> feature-implementer -> test-engineer -> code-reviewer -> acceptance-checker`

Use `docs-updater` if:
- public behavior changed
- configuration changed
- API or usage changed
- migration note may be needed

### 2) Bug fix / runtime failure / stack trace
Default pipeline:
- `bug-repro-triager -> test-engineer -> feature-implementer -> code-reviewer -> acceptance-checker`

Recommended bug-fix flow:
- reproduce first
- failing test next
- minimal fix
- regression coverage
- review
- acceptance mapping

### 3) Refactor / simplification / maintainability cleanup
Default pipeline:
- `task-planner -> code-simplifier -> code-reviewer -> acceptance-checker`

Add `test-engineer` if behavior-preservation risk is non-trivial.

### 4) Unfamiliar library / API / framework behavior
Default pipeline:
- `api-researcher -> task-planner -> feature-implementer -> test-engineer -> code-reviewer`

### 5) Test-only request
Default pipeline:
- `test-engineer -> code-reviewer` (review tests if non-trivial)
- optionally `acceptance-checker` if tests map to explicit criteria

### 6) Review-only request
Default pipeline:
- `code-reviewer`

### 7) Docs-only request
Default pipeline:
- `docs-updater`
- optionally `code-reviewer` if docs describe risky technical behavior

---

## Worker Roles and Boundaries (Enforce Role Discipline)

Workers must stay in role. Do not let one worker silently do another worker’s job unless explicitly requested.

### `task-planner`
- Does: clarify goals, define scope, plan steps, risks, tests, done criteria
- Does not: write production code

### `feature-implementer`
- Does: implement one scoped plan step with minimal diff
- Does not: broad refactor, rewrite plan, review code, do unrelated cleanup

### `test-engineer`
- Does: write/update tests, regression coverage, edge cases, repro tests
- Does not: change production code unless absolutely necessary and explicitly justified

### `code-reviewer`
- Does: critique correctness, regressions, standards, test adequacy
- Does not: rewrite implementation unless asked

### `acceptance-checker`
- Does: map implementation/tests to acceptance criteria with evidence
- Does not: optimize code or invent missing evidence

### `docs-updater`
- Does: update docs/readme/changelog/migration notes for recent changes
- Does not: invent undocumented behavior

### `api-researcher`
- Does: research external APIs/libraries and produce implementation guidance
- Does not: implement production code unless explicitly asked

### `bug-repro-triager`
- Does: produce repro steps, hypotheses, investigation plan, failing-test strategy
- Does not: implement fix

### `code-simplifier`
- Does: simplify/refine recently modified code while preserving behavior
- Does not: alter functionality or broaden scope

---

## Skill Priority

When multiple skills or worker agents might apply, use this order:

1. **Process / routing skill first** (this skill)
2. **Research / triage workers** (when uncertainty exists)
3. **Planning worker**
4. **Implementation worker**
5. **Test worker**
6. **Review worker**
7. **Acceptance worker**
8. **Docs/simplification workers** as needed

### Principle
Process determines **how** to approach the task before implementation determines **what** to change.

---

## Red Flags (Rationalization Warnings)

If you think any of these, stop and route to worker agents first:

- "This is simple, I can just answer directly"
- "Let me quickly inspect code first"
- "I can start coding and route later"
- "I need to ask clarifying questions before picking a worker"
- "I already know which worker to use, no need to announce it"
- "The worker format is overkill"
- "I’ll do one small thing before routing"
- "I remember the worker behavior from before"

These are signs you are about to skip discipline.

---

## Clarifying Questions Rule

If clarifying questions are needed **and** a worker likely applies:

1. Route first
2. Set `Current agent` to the worker most appropriate for framing the question (usually `task-planner` or `bug-repro-triager`)
3. Ask the clarifying question **in that worker’s role format**

Do not skip routing just because the next step is a question.

---

## Scope and Recency Rule (Global)

Unless explicitly instructed otherwise, workers should:
- focus on recently modified code / current task scope
- avoid broad codebase sweeps
- preserve behavior outside scope
- prefer minimal, reviewable diffs
- list assumptions explicitly instead of guessing

---

## Structured Output Enforcement

Workers must follow their own defined output schema. If a worker output does not match its schema, correct course before continuing.

At minimum, all worker outputs must include:
- active identity
- scope
- structured findings/work
- assumptions (when relevant)
- compliance footer

---

## Execution Template (Use This Every Time)

### Step 1: Route
Output:
- `Selected worker agents: ...`
- `Reason: ...`
- `Current agent: ...`

### Step 2: Execute current worker
Output begins with:
- `Active agent: ...`
- `Purpose: ...`
- `Scope: ...`

Then produce that worker’s structured output.

### Step 3: End with compliance
Output ends with:
- `Worker compliance: followed <agent-name> format`

### Step 4: Move to next worker (if continuing)
Re-announce:
- `Current agent: <next agent>`

---

## Examples (Behavioral)

### Example: "Add pagination to the users list"
- `Selected worker agents: task-planner -> feature-implementer -> test-engineer -> code-reviewer -> acceptance-checker`
- `Reason: feature implementation changes behavior and carries regression risk`
- `Current agent: task-planner`

### Example: "Fix this stack trace"
- `Selected worker agents: bug-repro-triager -> test-engineer -> feature-implementer -> code-reviewer -> acceptance-checker`
- `Reason: bug fix should establish repro and regression coverage before implementation`
- `Current agent: bug-repro-triager`

### Example: "Can you review these recent changes?"
- `Selected worker agents: code-reviewer`
- `Reason: explicit review request`
- `Current agent: code-reviewer`

---

## Final Principle

User instructions define **WHAT** needs to happen.  
This skill enforces **HOW** the work is approached.

Do not skip routing. Do not skip worker selection. Do not do silent generic work when a worker applies.
