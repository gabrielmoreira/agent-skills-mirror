# Implement Story — Workflow (TDD)

**Goal:** Implement one approved story to completion using Red → Green → Refactor discipline.

---

## Activation

1. Ask: "Which story are we implementing?" (accept JIRA key, S-ID, or title)
2. Load the story from `{implementation_artifacts}/stories/` or fetch from JIRA
3. Run `jira-conflict-detect` — if story is claimed by someone else, STOP and report
4. Verify story has `status: approved` in frontmatter — if Draft, warn and ask if they want to proceed anyway

---

## Phase 1: Story Comprehension

Read the story completely. Then verify understanding by restating:

```
Story: {S-ID} — {title}
AC count: {n}
Key behaviors to implement:
  - [AC-1 restated in dev terms]
  - [AC-2 restated in dev terms]
  - ...
Questions before I start: [any ambiguities]
```

⏸️ **STOP** — wait for confirmation or answers to questions.

---

## Phase 2: Branch Setup

Before writing any code:

1. Check if a branch for this story already exists:
   ```bash
   git branch -a | grep {JIRA-KEY or S-ID}
   ```
2. If no branch exists, create one:
   ```bash
   git checkout -b feature/{JIRA-KEY}-{story-slug}
   ```
3. If branch exists, check it out — warn if it has uncommitted changes

⏸️ **STOP** — confirm branch is clean and ready.

---

## Phase 3: Red — Write Failing Tests

For each acceptance criterion, write a test FIRST — before any implementation.

Rules:
- One test per AC (minimum)
- Test names must reference the AC: `test_AC1_user_can_login_with_valid_credentials`
- Tests must FAIL before any implementation — that's the point
- Show the failing test output

```
RED phase:
  ✗ AC-1: test_AC1_{description} — FAILED (expected)
  ✗ AC-2: test_AC2_{description} — FAILED (expected)
  ✗ AC-3: test_AC3_{description} — FAILED (expected)
```

⏸️ **STOP** — confirm all tests are red before proceeding.

---

## Phase 4: Green — Implement to Pass

Write the minimum code required to make the failing tests pass. No more than needed.

Do NOT:
- Pre-optimize
- Add features not covered by a test
- Abstract prematurely

After each AC implementation, run tests:
```
GREEN progress:
  ✓ AC-1: PASSED
  ✗ AC-2: still failing
  ...
```

When ALL tests pass:
```
✅ ALL GREEN
  ✓ AC-1: PASSED
  ✓ AC-2: PASSED
  ✓ AC-3: PASSED
```

⏸️ **STOP** — confirm all green before refactoring.

---

## Phase 5: Refactor — Improve Without Breaking

With all tests green, clean up:
- Remove duplication
- Clarify naming
- Extract meaningful abstractions (only if used in 3+ places)
- Ensure consistent error handling

Rules:
- Run tests after EVERY refactoring change
- Never introduce new behavior during refactor
- Any test that turns red = undo last change

After refactor:
```
POST-REFACTOR — all tests still green ✅
Changes made:
  - {what was refactored and why}
```

---

## Phase 6: Security Check

Before marking done, verify:
- [ ] All user inputs validated and sanitized
- [ ] No credentials or secrets hardcoded
- [ ] Error messages don't leak internal details
- [ ] Authorization checks in place (if applicable)
- [ ] SQL/NoSQL injection impossible (if applicable)

---

## Phase 7: Story Completion

Update the story file:
```yaml
status: "completed"
branch: "feature/{JIRA-KEY}-{slug}"
tests_written: {n}
completed_date: {date}
completed_by: {user_name}
```

Present completion summary:
```
✅ Story {S-ID} Complete
  Tests: {n} written, {n} passing
  Branch: feature/{JIRA-KEY}-{slug}
  ACs verified: {list}
  Ready for PR
```

Ask:
> "What's next?"

| # | Action |
|---|--------|
| 1 | Create a pull request (`github-create-pr`) |
| 2 | Update JIRA ticket to Done (`jira-update-status`) |
| 3 | Request code review (`code-review`) |
| 4 | Start the next story |

⏸️ **STOP** — wait for choice.
