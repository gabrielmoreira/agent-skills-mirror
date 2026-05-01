# Code Quality Reviewer Prompt Template

Use this template when dispatching a code quality reviewer subagent.

**Purpose:** Verify implementation is well-built (clean, tested, maintainable)

**Only dispatch after spec compliance review passes.**

**Before dispatching — get SHAs from git log:**
```bash
git log --oneline -10
```
- `BASE_SHA` = the commit immediately before the implementer's first commit for this task
- `HEAD_SHA` = the latest commit (after all implementer fixes)
- If the implementer committed multiple times for this task, `BASE_SHA` is still the one before their first commit

```
Task tool (superpowers:code-reviewer):
  Use template at requesting-code-review/code-reviewer.md

  WHAT_WAS_IMPLEMENTED: [from implementer's report]
  PLAN_OR_REQUIREMENTS: Task N from [plan-file]
  BASE_SHA: [commit SHA before this task's first commit]
  HEAD_SHA: [current HEAD SHA]
  DESCRIPTION: [task summary]
```

**Code reviewer returns:** Strengths, Issues (Critical/Important/Minor), Assessment
