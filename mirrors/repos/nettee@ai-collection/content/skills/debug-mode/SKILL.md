---
name: debug-mode
description: >
  Use this skill when the user explicitly invokes "/debug-mode" or says "enter debug mode",
  "start debug mode", "use debug mode". This is a token-heavy workflow — do NOT activate
  automatically for general debugging questions or simple bug fixes.
version: 0.1.0
---

# Debug Mode: Hypothesis-Driven Runtime Debugging

## Overview

Debug Mode is a structured debugging workflow inspired by Cursor's Debug Mode. Instead of guessing at fixes, you form hypotheses about root causes, instrument code with targeted logging, collect runtime evidence, then make minimal, precise fixes.

**Core principle:** Evidence first, fix second.

## When to Use

- Runtime bugs that are hard to reproduce or understand from code alone
- Race conditions, async/timing issues
- State corruption or unexpected values at runtime
- Bugs where the root cause isn't obvious from reading code
- Intermittent failures that need runtime data to diagnose

## Methodology

The workflow has 7 steps:

1. **Understand the bug** — Read the bug description and relevant code
2. **Generate hypotheses** — Form 3-5 specific theories about the root cause, labeled H1-H5
3. **Instrument code** — Add `fetch()` calls at strategic locations, each tagged with which hypothesis it tests
4. **Start debug server** — Copy and run the server that collects logs to `.debug-mode/debug.log`
5. **Reproduce** — Ask user to reproduce the bug while instrumentation collects evidence
6. **Evaluate hypotheses** — Read logs, mark each hypothesis CONFIRMED or REJECTED with evidence
7. **Fix and clean up** — Apply minimal fix for confirmed hypothesis, remove all instrumentation

If the fix doesn't work, loop back to step 3 with additional hypotheses or more instrumentation.

---

## Workflow

### Step 1: Create Task List

Use TodoWrite to create a task list:
- Understand bug and read codebase
- Generate hypotheses
- Start debug server and instrument code
- Ask user to reproduce
- Analyze logs and evaluate hypotheses
- Propose and verify fix
- Remove all instrumentation and cleanup

### Step 2: Understand the Bug

If the bug description is vague or unclear, ask the user:
- What is the unexpected behavior?
- What steps reproduce it?
- What is the expected behavior?
- What environment / runtime?

Read relevant source files to understand the suspected code paths. Use Grep and Glob to find related code.

### Step 3: Generate Hypotheses

Based on codebase reading, produce 3-5 hypotheses about the root cause.

Format each hypothesis as a one-sentence theory:

```
H1: [specific root cause theory]
H2: [specific root cause theory]
H3: [specific root cause theory]
```

Present these to the user, then proceed directly to Step 4.

### Step 4: Start Debug Server

Set up the debug infrastructure:

1. Create the debug directory and copy the server script:

```bash
mkdir -p .debug-mode && cp "$(find ~/.claude/plugins -path '*/debug-mode/server.js' -print -quit 2>/dev/null || find .claude-plugin -path '*/debug-mode/server.js' -print -quit 2>/dev/null || find plugin/skills -path '*/debug-mode/server.js' -print -quit 2>/dev/null)" .debug-mode/server.js
```

If the copy command fails, look for `server.js` in these locations (in order):
- `~/.claude/plugins/*/skills/debug-mode/server.js` (Claude Code plugin installation)
- `.cursor/skills/debug-mode/server.js` (Cursor deployment)
- `.opencode/skills/debug-mode/server.js` (OpenCode deployment)
- `plugin/skills/debug-mode/server.js` (source repo)

2. Add `.debug-mode/` to `.gitignore` if not already present:

```bash
grep -qxF '.debug-mode/' .gitignore 2>/dev/null || echo '.debug-mode/' >> .gitignore
```

3. Start the server in the background:

```bash
node .debug-mode/server.js 9742 &
```

4. Verify it is running:

```bash
curl -s http://localhost:9742/health
```

If port 9742 is taken, use a different port and update all fetch URLs accordingly.

### Step 5: Instrument Code

Add `fetch()` calls to the source files at strategic locations. **Every** call must include:

- `hypothesisId`: which hypothesis this point tests (`"H1"`, `"H2"`, etc.)
- `location`: `"functionName:entry"`, `"functionName:exit"`, `"functionName:error"`, etc.
- `message`: what this data point tells us
- `data`: the relevant runtime values at this point

Use this pattern:

```javascript
fetch("http://localhost:9742/debug", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ hypothesisId: "H1", location: "processOrder:entry", message: "checking initial state", data: { orderId, userId } }) }).catch(() => {});
```

Place instrumentation at:
- Entry/exit of suspected functions
- Branch points that distinguish hypotheses
- Error catch blocks
- State mutations (before/after values)

**Track which files you modify** — you will need to remove all instrumentation in Step 9.

Tell the user exactly how to reproduce. Be specific:

> "I've added instrumentation for H1, H2, H3. Please reproduce the bug now, then let me know when done."

### Step 6: Analyze Logs

Once user confirms they have reproduced the bug, read the log:

```bash
cat .debug-mode/debug.log
```

Evaluate each hypothesis against the evidence:

```
H1: [theory] → CONFIRMED / REJECTED — [one sentence of evidence from logs]
H2: [theory] → CONFIRMED / REJECTED — [one sentence of evidence from logs]
H3: [theory] → CONFIRMED / REJECTED — [one sentence of evidence from logs]
```

Present the evaluation to the user.

If no hypothesis is confirmed and the evidence is inconclusive:
- Generate additional hypotheses based on what the logs revealed
- Return to Step 5 to add more targeted instrumentation

### Step 7: Apply Fix

For the CONFIRMED hypothesis, implement the **minimal** fix:
- Keep it small — typically 2-3 lines
- Show exactly what was changed (file, line, change)

**Do NOT remove instrumentation yet.** Leave all `fetch()` calls in place — logs are the only truth, and the fix must be verified through them.

### Step 8: Verify Fix

Clear the log so the next reproduction is clean:

```bash
> .debug-mode/debug.log
```

Ask user to reproduce the bug again with the fix applied.

Read the log:

```bash
cat .debug-mode/debug.log
```

Evaluate the log evidence:

If the log **confirms the bug is fixed** (expected values flow correctly, error path no longer triggered, etc.):
- Proceed to Step 9 (cleanup)

If the log shows the bug **persists**:
- Return to Step 5 to add more instrumentation targeting remaining hypotheses
- Or return to Step 3 to generate additional hypotheses based on new evidence

### Step 9: Cleanup

Only remove instrumentation after the logs have confirmed the fix works.

**Remove all instrumentation** from every source file modified in Step 5. Check each file and remove every `fetch("http://localhost:9742/debug", ...)` call that was added.

Stop the debug server:

```bash
pkill -f ".debug-mode/server.js" 2>/dev/null
```

Remove the debug directory:

```bash
rm -rf .debug-mode/
```

Optionally remove the `.debug-mode/` line from `.gitignore` if you added it.

Confirm to user:

> "Fix verified via logs. All instrumentation removed, debug server stopped, `.debug-mode/` cleaned up."

---

## Reference

### Debug Server

The debug server ships as `server.js` alongside this skill file. The server listens for POST requests on `/debug` and appends structured log lines to `.debug-mode/debug.log`.

### Log Format

Each POST to `/debug` accepts a JSON body:

```json
{
  "hypothesisId": "H1",
  "location": "processOrder:entry",
  "message": "checking initial state",
  "data": { "orderId": 123, "status": "pending" }
}
```

The server writes log lines as:

```
[2026-02-26T10:00:01.234Z] [H1] processOrder:entry | checking initial state | {"orderId":123,"status":"pending"}
```

### Instrumentation Placement Guidelines

- **Function entry/exit** — Capture arguments on entry, return values on exit
- **Branch points** — Log which branch was taken to distinguish hypotheses
- **Error catch blocks** — Capture error details
- **State mutations** — Log before/after values
- **Async boundaries** — Log before await and after resolution

### Label Conventions

| Pattern | Example | Use For |
|---------|---------|---------|
| `fn-name:entry` | `processOrder:entry` | Function start |
| `fn-name:exit` | `processOrder:exit` | Function end |
| `fn-name:error` | `processOrder:error` | Caught errors |
| `fn-name:state` | `processOrder:state` | State snapshots |
| `fn-name:branch` | `processOrder:branch-early-return` | Control flow |

### Hypothesis Example

```
H1: The discount is applied after tax calculation instead of before
H2: The coupon validation returns stale cached data
H3: Concurrent cart updates cause a race condition on the total
```

### Evaluation Example

```
H1: The discount is applied after tax calculation → REJECTED — logs show discount applied at line 45 before tax calc at line 72
H2: The coupon validation returns stale cached data → CONFIRMED — cache key "coupon:SAVE10" returns expired entry from 2h ago
H3: Concurrent cart updates cause a race condition → REJECTED — no concurrent access detected in logs
```
