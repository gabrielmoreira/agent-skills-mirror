---
name: plan
description: "Writes a bite-sized, copy-pasteable implementation plan to .hermes/plans/ with no code execution. Use when the user says plan, /plan, break down, or wants a roadmap before coding. Not for GOAL.md autonomous loops (goal) or immediate implementation. Do not run mutating commands, commits, or installs while planning."
version: 2.0.1
author: Hermes Agent (writing-craft adapted from obra/superpowers)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [planning, plan-mode, implementation, workflow, design, documentation]
    related_skills: [subagent-driven-development, test-driven-development, requesting-code-review]
---

# Plan Mode

## When to Use

Use this skill when the user wants a **plan instead of execution**. Trigger keywords and situations:

- User says "plan", "design", "break this down", "how should we approach", "roadmap", "spec it out".
- User invokes `/plan` or asks for an implementation plan before coding.
- A multi-step feature needs decomposition before any code is written.
- You are about to delegate work to subagents via `subagent-driven-development` — always plan first.
- The task seems simple but hidden assumptions could cause bugs.

**Do NOT use when:** the user wants immediate implementation, a quick fix, or a one-line answer. If the user says "just do it," execute, don't plan.

## Prerequisites

- An active workspace / working directory where `.hermes/plans/` can be created.
- Read-only access to the codebase (file search, file read) so you can explore before planning.
- No code execution, mutation, commits, or pushes are permitted during planning.

## Procedure

### Core Behavior — Planning Only

For this turn, you are **planning only**.

1. **Do not implement code.**
2. **Do not edit project files** except the plan markdown file itself.
3. **Do not run mutating terminal commands**, commit, push, or perform external actions.
4. You **may** inspect the repo or other context with read-only commands/tools when needed.
5. Your deliverable is a markdown plan saved inside the active workspace under `.hermes/plans/`.

### Step 1 — Understand Requirements

Read and understand:
- Feature requirements and acceptance criteria.
- Design documents or the user's description.
- Constraints (time, dependencies, platform).

If the request is genuinely underspecified, ask **one brief clarifying question** instead of guessing. If it is clear enough, proceed directly.

### Step 2 — Explore the Codebase

Use read-only tools to understand the project before writing anything:

```powershell
# PowerShell (Windows host — primary)
Get-ChildItem -Path src -Recurse -Filter *.py
Get-ChildItem -Path tests -Recurse -Filter *.py
Select-String -Path src\app.py -Pattern "similar_pattern"
```

```bash
# Bash (macOS / Linux)
find src -name "*.py" -type f
find tests -name "*.py" -type f
grep -rn "similar_pattern" src/
```

Read key files to understand existing patterns, conventions, and test structure.

### Step 3 — Design the Approach

Decide:
- Architecture pattern and file organization.
- Dependencies needed (or not needed — YAGNI).
- Testing strategy (TDD preferred).
- Task ordering: setup → core → edge cases → integration → cleanup/docs.

### Step 4 — Write the Plan Document

Save the plan with `write_file` under:

```
.hermes/plans/YYYY-MM-DD_HHMMSS-<slug>.md
```

Treat this as **relative to the active working directory**. Hermes file tools are backend-aware, so this relative path keeps the plan with the workspace on local, Docker, SSH, Modal, and Daytona backends.

If the runtime provides a specific target path, use that exact path. Otherwise, create a sensible timestamped filename yourself.

**Windows path note:** On a Windows host the saved path may render as `.hermes\plans\2025-01-15_143022-add-auth.md`. Both slash styles are acceptable; the file tool resolves them.

### Step 5 — Plan Document Structure

Every plan **MUST** start with this header:

```markdown
# [Feature Name] Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

Then include, when relevant:
- Goal
- Current context / assumptions
- Proposed approach
- Step-by-step plan (bite-sized tasks)
- Files likely to change
- Tests / validation
- Risks, tradeoffs, and open questions

### Step 6 — Write Bite-Sized Tasks

**Each task = 2–5 minutes of focused work.** Every step is one action.

Each task follows this format:

````markdown
### Task N: [Descriptive Name]

**Objective:** What this task accomplishes (one sentence)

**Files:**
- Create: `exact/path/to/new_file.py`
- Modify: `exact/path/to/existing.py:45-67` (line numbers if known)
- Test: `tests/path/to/test_file.py`

**Step 1: Write failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

**Step 2: Run test to verify failure**

Run: `pytest tests/path/test.py::test_specific_behavior -v`
Expected: FAIL — "function not defined"

**Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

**Step 4: Run test to verify pass**

Run: `pytest tests/path/test.py::test_specific_behavior -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

**Too big (avoid):**

```markdown
### Task 1: Build authentication system
[50 lines of code across 5 files]
```

**Right size:**

```markdown
### Task 1: Create User model with email field
[10 lines, 1 file]

### Task 2: Add password hash field to User
[8 lines, 1 file]

### Task 3: Create password hashing utility
[15 lines, 1 file]
```

### Step 7 — Add Complete Details

For each task, include:
- **Exact file paths** — not "the config file" but `src/config/settings.py`.
- **Complete code examples** — not "add validation" but the actual, copy-pasteable code.
- **Exact commands** with expected output.
- **Verification steps** that prove the task works.

### Step 8 — Review the Plan

Check:
- [ ] Tasks are sequential and logical
- [ ] Each task is bite-sized (2–5 min)
- [ ] File paths are exact
- [ ] Code examples are complete (copy-pasteable)
- [ ] Commands are exact with expected output
- [ ] No missing context
- [ ] DRY, YAGNI, TDD principles applied

### Step 9 — Reply and Hand Off

After saving the plan, reply briefly with what you planned and the saved path. Then offer execution:

> "Plan complete and saved to `.hermes/plans/YYYY-MM-DD_HHMMSS-slug.md`. Ready to execute using subagent-driven-development — I'll dispatch a fresh subagent per task with two-stage review (spec compliance then code quality). Shall I proceed?"

## Principles

### DRY (Don't Repeat Yourself)

**Bad:** Copy-paste validation in 3 places.
**Good:** Extract validation function, use everywhere.

### YAGNI (You Aren't Gonna Need It)

**Bad:** Add "flexibility" for future requirements.

```python
# Bad — YAGNI violation
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.preferences = {}  # Not needed yet!
        self.metadata = {}     # Not needed yet!
```

**Good:** Implement only what's needed now.

```python
# Good — YAGNI
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
```

### TDD (Test-Driven Development)

Every task that produces code should include the full TDD cycle:
1. Write failing test
2. Run to verify failure
3. Write minimal code
4. Run to verify pass

See the `test-driven-development` skill for details.

### Frequent Commits

Commit after every task:

```bash
git add [files]
git commit -m "type: description"
```

## Pitfalls

- **Vague tasks.** "Add authentication" is not a task. "Create User model with email and password_hash fields" is.
- **Incomplete code.** "Step 1: Add validation function" without the actual function code forces the implementer to guess. Always include complete, copy-pasteable code.
- **Missing verification.** "Step 3: Test it works" is useless. Use "Step 3: Run `pytest tests/test_auth.py -v`, expected: 3 passed."
- **Missing file paths.** "Create the model file" is ambiguous. Use `Create: src/models/user.py`.
- **Skipping the plan for "simple" features.** Assumptions cause bugs. Always plan, even when it seems trivial.
- **Planning alone and skipping documentation.** Future you needs guidance just as much as a delegate does.
- **Running mutating commands during planning.** This is plan mode — no edits, no commits, no pushes, no installs. Read-only only.
- **Guessing when underspecified.** If the request is genuinely ambiguous, ask one brief clarifying question rather than fabricating requirements.

## Verification

After the plan is saved, verify:

1. **File exists:**

```powershell
# Windows (PowerShell)
Test-Path .hermes\plans\*.md
Get-ChildItem .hermes\plans\*.md | Select-Object Name, Length, LastWriteTime
```

```bash
# macOS / Linux
ls -la .hermes/plans/*.md
```

2. **Header is present** — open the file and confirm it starts with `# [Feature Name] Implementation Plan` and includes the `> **For Hermes:**` handoff line.

3. **Tasks are bite-sized** — scan the plan; no single task should span more than ~5 files or ~50 lines of new code.

4. **Every code-producing task has a TDD cycle** — failing test → run → implement → run → commit.

5. **Every task has exact file paths and exact commands with expected output.**

6. **Reply includes the saved path** so the user can open and review the plan.

## Related Skills

- **subagent-driven-development** — use to execute the plan task-by-task with fresh subagents and two-stage review.
- **test-driven-development** — the testing methodology embedded in every code-producing task.
- **requesting-code-review** — use after implementation to review the completed work against the plan.

## Remember

```
Bite-sized tasks (2-5 min each)
Exact file paths
Complete code (copy-pasteable)
Exact commands with expected output
Verification steps
DRY, YAGNI, TDD
Frequent commits
```

**A good plan makes implementation obvious. If someone has to guess, the plan is incomplete.**
