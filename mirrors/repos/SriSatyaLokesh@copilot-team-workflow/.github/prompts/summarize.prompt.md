---
description: 'Use when ending a work session or switching context — when a developer says "summarize this session", "save my progress", "capture context", "end of day summary", or before closing the chat. Captures current context, decisions, blockers, and next steps to the Issue doc so the next session can continue seamlessly.'
agent: 'ask'
---
# Summarize Session — Preserve Context for Next Session

Capture the current session's context so you (or a teammate) can pick up exactly where you left off.

**Issue doc**: ${input:issue-doc:Path to Issue doc (e.g., docs/issues/ISSUE-042-name.md) or leave blank to auto-detect}

---

## What This Command Does

1. **Detects the current Issue** (from branch name or most recent Issue doc)
2. **Analyzes the session**:
   - What was discussed/decided
   - What code was changed
   - What tests were written/run
   - Any blockers encountered
   - Questions that came up
3. **Creates a session summary** with:
   - Timestamp
   - Current phase and progress
   - Key decisions made
   - Files changed
   - Next steps
   - Open questions
4. **Appends to Issue doc** in a "Session Notes" section

---

## Step 1 — Identify the Issue

If no Issue doc path provided:
```bash
# Get current branch
git branch --show-current
```

Expected output: `issue/ISSUE-042-login-rate-limiting`

Extract the Issue ID and find the corresponding doc in `docs/issues/`.

If not on an issue branch, search for the most recently modified Issue doc:
```bash
Get-ChildItem docs/issues/*.md | Sort-Object LastWriteTime -Descending | Select-Object -First 1
```

---

## Step 2 — Analyze Current Session

### A) Check what was changed
```bash
# Staged and unstaged changes
git status --short

# Recent commits on this branch
git log --oneline -5
```

### B) Check test status
```bash
# Try to run tests (don't fail if no tests exist)
npm test 2>&1 | Select-Object -First 20
```

### C) Review conversation context

From our conversation in this chat session, identify:
- What problem were we solving?
- What approach did we decide on?
- What's currently working vs. broken?
- What questions remain unanswered?

---

## Step 3 — Create Session Summary

Generate a structured summary:

```markdown
### Session Summary — [YYYY-MM-DD HH:MM UTC]

**Developer**: [Name or "Unknown"]
**Duration**: [Approximate session length]
**Current Phase**: [Phase X: Name]

#### What We Did
- [Action 1 — e.g., "Implemented rate limiting middleware"]
- [Action 2 — e.g., "Wrote 4 unit tests for admin bypass"]
- [Action 3 — e.g., "Debugged Redis connection timeout"]

#### Decisions Made
- [Decision 1 — e.g., "Use sliding window algorithm instead of fixed window"]
- [Decision 2 — e.g., "Store rate limit state in Redis, not in-memory"]

#### Files Changed
- `src/middleware/rate-limit.ts` (created, 150 lines)
- `src/api/auth/route.ts` (modified, +10 lines)
- `tests/middleware/rate-limit.test.ts` (created, 80 lines)

#### Current Status
- ✅ Middleware tests passing (8/8)
- 🔄 Integration tests in progress (2/4 passing)
- ⬜ Admin bypass not yet implemented

#### Blockers / Open Questions
- ❓ Should we rate limit by IP or by email? (Decision needed from product)
- ⚠️ Redis connection times out in test environment (need to investigate)

#### Next Steps
1. Resolve Redis timeout issue
2. Implement admin role bypass
3. Complete integration tests
4. Run `/verify` before creating PR

#### Notes
- [Any other context worth preserving]
```

---

## Step 4 — Update the Issue Doc

**Find or create the "Session Notes" section** in the Issue doc.

If the section doesn't exist, add it at the end of the document:

```markdown
---

## 📝 Session Notes

*(Chronological log of work sessions — newest first)*

### Session Summary — 2026-03-03 16:45 UTC
...
```

If the section exists, **prepend** the new summary to the top (newest first).

---

## Step 5 — Show the Summary

Display the summary to the user and confirm:

```
✅ Session context saved to docs/issues/ISSUE-042-login-rate-limiting.md

Next time you (or a teammate) continue this work, they can:
- Read the Session Notes section for full context
- Run /status to see current phase
- Pick up from the Next Steps list

Session Summary:
──────────────────────────────────────────────────
[Display the summary here]
──────────────────────────────────────────────────

Would you like to:
1. Continue working
2. Commit and close (run auto-commit hook)
3. Just close (no commit)
```

---

## Use Cases

### End of Day
```
Developer: "It's 5pm, I need to wrap up. /summarize"
Copilot: [Saves context]
→ Tomorrow morning: Open Issue doc, read Session Notes, continue exactly where you left off
```

### Context Switch
```
Developer: "Emergency bug, need to switch Issues. /summarize"
Copilot: [Saves current Issue context]
Developer: [Works on emergency]
Developer: [Comes back] "Read #docs/issues/ISSUE-042.md Session Notes"
Copilot: [Loads context, resumes work]
```

### Handoff to Teammate
```
Developer A: "Handing this off to Sarah. /summarize"
Copilot: [Saves summary with blockers and next steps]
Developer B (Sarah): "Continue ISSUE-042"
Copilot: [Reads Session Notes] "I see Alex left off at step 3. The Redis issue is blocking. Here's what we need to do..."
```

### After Long Break
```
Developer: [After 3 days] "What was I doing on ISSUE-042?"
Copilot: [Reads Session Notes] "Last session was on March 1st. You implemented rate limiting middleware, 8 tests passing. Next step: implement admin bypass."
```

---

## What Gets Captured

| Category | What's Included |
|----------|----------------|
| **Actions** | Code written, tests added, bugs fixed, docs updated |
| **Decisions** | Technical choices made, approaches selected, why alternatives were rejected |
| **Status** | What's working, what's broken, what's in progress |
| **Files** | Which files changed, how many lines, created vs modified |
| **Blockers** | What's preventing progress, what needs external input |
| **Questions** | Unresolved decisions, unclear requirements, missing information |
| **Next Steps** | Prioritized list of what to do next session |

---

## Integration with Other Commands

- **Before `/summarize`**: Run `/status` to confirm what phase you're in
- **After `/summarize`**: Can run `/finish-branch` if ready to merge, or just close chat
- **Next session start**: Run `/status` to see current state, or just read Session Notes
- **Before handoff**: Always run `/summarize` so teammate has full context

---

## Example Output

```markdown
✅ Session context saved to docs/issues/ISSUE-042-login-rate-limiting.md

Session Summary — 2026-03-03 16:45 UTC
──────────────────────────────────────────────────
Developer: Alex Chen
Current Phase: Phase 4 (Execute)

What We Did:
- Implemented sliding window rate limiter in Redis
- Created 8 unit tests (all passing)
- Applied middleware to POST /auth/login
- Started integration test suite (2/4 passing)

Decisions Made:
- Using sliding window (not fixed) to prevent burst at window boundary
- Rate limit by email address, not IP (avoids shared IP issues)
- 15-minute window with 5 attempt limit

Files Changed:
- src/middleware/rate-limit.ts (created, 150 lines)
- src/api/auth/route.ts (modified, +10 lines)
- tests/middleware/rate-limit.test.ts (created, 80 lines)

Blockers:
❓ Redis connection timing out in test env (need to check config)

Next Steps:
1. Fix Redis timeout (check TEST_REDIS_URL env var)
2. Implement admin bypass (check user.role before rate limit)
3. Finish integration tests (2 remaining)
4. Run /verify before PR
──────────────────────────────────────────────────

Resume next session with: "Continue ISSUE-042"
```

---

## Related Commands

- `/status` — Quick phase check before summarizing
- `/finish-branch` — After summarizing, decide to merge or keep working
- `/verify` — Full verification before marking Issue done
- `/sync-docs` — If you changed multiple docs during session

---

## Pro Tips

1. **Summarize frequently** — After each major milestone, not just end of day
2. **Be specific in blockers** — "Redis timeout" is less useful than "Redis connection times out after 5s in test env, need to check if TEST_REDIS_URL is set"
3. **Link decisions to requirements** — "Used sliding window to meet requirement: prevent burst attacks"
4. **Include commit SHAs** — Makes it easy to review what code changed
5. **Tag teammates** — "@sarah-smith needs to review Redis config before we proceed"
