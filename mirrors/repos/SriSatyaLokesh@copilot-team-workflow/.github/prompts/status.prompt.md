---
description: 'Use when a developer needs to check their current progress on an Issue — when they say "where am I?", "what phase am I on?", "what should I do next?", "show status", "check progress", or "what is the current state?". Shows which phases are complete, which is in progress, and what the next step should be.'
agent: 'ask'
---
# Status — Check Current Issue Progress

Shows you where you are in the 5-phase workflow and what to do next.

**Issue doc**: ${input:issue-doc:Path to Issue doc (e.g., docs/issues/ISSUE-042-name.md) or leave blank to search}

---

## What This Command Does

1. **If you provide an Issue doc path**: Reads that specific Issue doc
2. **If left blank**: Searches `docs/issues/` for the most recently modified Issue doc

Then displays:
- ✅ Which phases are complete
- 🔄 Which phase is currently in progress
- ⬜ Which phases are not started
- 🎯 What your **next action** should be
- ⚠️ Any blockers or missing prerequisites

---

## Status Report Format

```
📊 Issue Status Report
─────────────────────────────────────────────────

Issue ID: ISSUE-042
Title: Login Rate Limiting
Branch: issue/042-login-rate-limiting
Status: execute
Owner: [Developer Name]
Last Updated: 2026-03-02

─────────────────────────────────────────────────

Phase Progress:
  ✅ Phase 1: Discuss      (requirements confirmed)
  ✅ Phase 2: Research     (codebase context gathered)
  ✅ Phase 3: Plan         (tasks defined)
  🔄 Phase 4: Execute      (5/8 tasks complete)
  ⬜ Phase 5: Verify       (not started)

─────────────────────────────────────────────────

Current Phase: Execute (Phase 4)

Tasks Remaining:
  - [ ] Test: admin bypass for rate limit
  - [ ] Implement: admin role check
  - [ ] Update API docs for login endpoint

─────────────────────────────────────────────────

🎯 NEXT STEP:
   Continue TDD implementation of remaining tasks
   Run: /execute
   or
   Select the TDD Implementer agent and say:
   "Continue implementing ISSUE-042"

─────────────────────────────────────────────────
```

---

## If No Issue Doc Found

If you don't provide a path and no Issue docs exist in `docs/issues/`, the status shows:

```
📊 No Active Issues Found

No Issue documents found in docs/issues/

🎯 NEXT STEP:
   Start a new Issue with: /start-issue
```

---

## Checking Activity Log

Optionally, you can also check the activity log to see historical progress:

```bash
# Show all activity for this Issue
cat logs/copilot/agent-activity.log | jq 'select(.issueId == "ISSUE-042")'

# Show today's activity
cat logs/copilot/agent-activity.log | jq 'select(.timestamp | startswith("2026-03-03"))'
```

---

## Use Cases

- **Starting your day**: Check which Issue you were working on yesterday
- **After a break**: Quickly remember where you left off
- **Switching contexts**: See what needs to be done before you can merge
- **Handoff to teammate**: Share current progress
- **Standup prep**: Quick summary of yesterday's progress

---

## Related Commands

- `/start-issue` — Begin new work
- `/execute` — Continue TDD implementation
- `/verify` — Check if ready to merge
- `/finish-branch` — Wrap up and merge/PR
