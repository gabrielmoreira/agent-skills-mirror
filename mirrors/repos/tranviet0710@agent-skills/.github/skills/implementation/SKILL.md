---
name: implementation
description: "Implement a feature based on a plan file. Use when: implementing a plan, execute a plan, build from plan, start working on plan, implement PLAN.md. Reads the plan, asks clarifying questions, creates TASKS.md with subtasks in the same folder, then implements each task and marks it done."
argument-hint: "Path to the PLAN.md file (e.g. multibuy-national-campaign/PLAN.md)"
---

# Implement From Plan

## When to Use

Invoke this skill when the user says:
- "implement based on the plan"
- "execute the plan"
- "build from PLAN.md"
- "start working on [feature] plan"
- "implement [folder]/PLAN.md"

## Procedure

### Step 1 — Locate & Review the Plan

1. Find the `PLAN.md` (or any `*PLAN*.md`) in the referenced folder or the currently open file.
2. Read the entire plan carefully.
3. Note: the plan's folder is the **working directory** for this skill — all output files go there.

### Step 2 — Ask Clarifying Questions

Before doing anything else:
- List every ambiguity, assumption, or missing detail you found while reading the plan.
- Present them as a numbered question list to the user.
- If the plan is fully clear with zero ambiguities, explicitly state: "The plan is clear — no questions. Proceeding to create TASKS.md."
- **Wait for the user's answers before continuing.**

### Step 3 — Create TASKS.md

Create a `TASKS.md` file **in the same folder as the plan file**, structured as follows:

```markdown
# Tasks

> Auto-generated from [PLAN.md](./PLAN.md) on <date>

## Task List

- [ ] **Task 1 — <short title>**
  - Description: <what needs to be done and why>
  - Subtasks:
    - [ ] <subtask a>
    - [ ] <subtask b>

- [ ] **Task 2 — <short title>**
  - Description: ...
  - Subtasks:
    - [ ] ...

...
```

Rules for task decomposition:
- Each task maps to one logical, independently testable unit of work.
- Subtasks are concrete, atomic steps (a single file edit, a single function, etc.).
- Include enough description so anyone can pick up the task cold.
- Do **not** include tasks that are already done in the plan.

### Step 4 — Implement Tasks One by One

For each task in `TASKS.md`:

1. **Mark the task as in-progress** by updating the checkbox to `[-]` (or add `_(in progress)_` inline) in `TASKS.md`.
2. Implement the task — write code, create files, make edits as needed.
3. Validate the change compiles / passes linting if applicable.
4. **Mark the task as done** by changing `[ ]` → `[x]` for the task and all its completed subtasks in `TASKS.md`.
5. Move to the next task.

### Step 5 — Final Summary

After all tasks are marked `[x]`:
- Add a `## Summary` section at the bottom of `TASKS.md` listing what was built.
- Report to the user that implementation is complete.

## Important Rules

- **Never skip Step 2.** Always surface questions before writing code.
- Always write `TASKS.md` before writing any implementation code.
- Keep `TASKS.md` up to date in real time — update it before and after each task.
- If a new task is discovered mid-implementation, add it to `TASKS.md` before starting it.
- Do not mark a task `[x]` unless it is truly complete (code written, no errors).
