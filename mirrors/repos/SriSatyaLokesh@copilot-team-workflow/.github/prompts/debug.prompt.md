---
description: 'Use when a bug, test failure, or unexpected behavior is found — when a developer says "this test is failing", "this is broken", "I found a bug", "something is wrong with X", or when debugging any unexpected output. Requires systematic 4-phase root cause analysis — never guess at a fix.'
agent: 'TDD Implementer'
---
# Systematic Debugging — 4-Phase Root Cause Analysis

**Never guess.** Every change must be backed by a hypothesis proven by a test.

---

## Phase 1 — Reproduce

Create a minimal, reliable reproduction of the failure:

```bash
npm test -- --testNamePattern="<failing test name>"
```

- Confirm the failure is deterministic (fails every run)
- If intermittent: add logging to catch timing issues
- Document exact error message and stack trace

> **Do NOT attempt a fix before you can reproduce it reliably.**

---

## Phase 2 — Isolate

Trace the code path to find where expectation and reality diverge:

1. Follow the stack trace upward — which function is the root?
2. Add temporary `console.log` at key checkpoints to trace state
3. Ask: *"At what exact point does the value/state become wrong?"*
4. Narrow to the smallest possible reproduction (one function, one call)

```bash
# Run only the failing test with verbose output
npm test -- --verbose --testPathPattern="path/to/test"
```

---

## Phase 3 — Identify

Form a hypothesis and verify it with a targeted test:

1. State your hypothesis: *"I believe X is wrong because Y"*
2. Write a minimal test that proves/disproves the hypothesis:
   ```typescript
   test('hypothesis: X should return Y when given Z', () => {
     expect(suspectedFunction(Z)).toBe(Y);
   });
   ```
3. Run the test — does it fail in the expected way?
4. If yes: you've found the root cause. Proceed to Phase 4.
5. If no: revise hypothesis and repeat Phase 3.

---

## Phase 4 — Resolve

Fix the root cause (not the symptom):

1. Write a **regression test** that reproduces the bug before fixing:
   ```typescript
   test('bug: [description of the bug]', () => {
     // This test MUST FAIL before the fix, PASS after
   });
   ```
2. Confirm the regression test **fails** now (watch it fail = RED)
3. Implement the minimal fix
4. Confirm the regression test **passes** (GREEN)
5. Run full test suite — confirm no regressions
6. Commit: `git commit -m "fix: [root cause description] (fixes #issue)"`

---

## ⚠️ The 3-Strikes Rule

If your fix fails 3 times in a row:

```
STOP. Do not keep trying random changes.

1. Dump the current state to a file: what you tried, what happened, what you expected
2. Step back completely — question your Phase 2 isolation
3. Start Phase 2 again with fresh eyes, different approach
```

**Three failures means your hypothesis was wrong.** Go back to isolation.

---

## Anti-Patterns to Reject

| What developer suggests | Why it's wrong | Correct approach |
|:---|:---|:---|
| "Just increase the timeout" | Hides the real timing issue | Find why it's slow and fix that |
| "Add a retry loop" | Masks intermittent failures | Find and fix the flakiness root cause |
| "Comment out the assertion" | Removes the test's value entirely | Fix the code to meet the assertion |
| "Maybe it'll fix itself" | It won't | Reproduce and trace it now |

---

## After the Bug is Fixed

- [ ] Regression test exists and is green
- [ ] Full test suite passes (`npm test`)
- [ ] Root cause (not symptom) was fixed
- [ ] Commit message explains the root cause
- [ ] Consider: could this bug exist elsewhere in similar code?
