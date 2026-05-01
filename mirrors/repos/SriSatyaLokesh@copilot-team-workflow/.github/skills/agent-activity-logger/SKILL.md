---
name: agent-activity-logger
description: 'Background reference skill defining the structured JSON log format written to logs/copilot/agent-activity.log by each phase agent on completion. Auto-loaded by Discuss, Research, Planner, TDD Implementer, and Verify agents when they append their completion log entry. Defines all required fields (timestamp, issueId, phase, agent, developer, status, summary, decisions, outputFile, nextPhase) and optional phase-specific fields (filesChanged for execute, testResults for verify). Also provides jq query examples for filtering logs by Issue, date, or status. Loads when log format, activity log, or agent logging is mentioned.'
---

# Agent Activity Log — Format Reference

Every phase agent appends one JSON entry to `logs/copilot/agent-activity.log`
when it completes its work. This creates a full audit trail of every Issue's lifecycle.

---

## Log File Location

```
logs/copilot/agent-activity.log     ← JSON Lines format (one JSON object per line)
```

> Add `logs/` to `.gitignore` — these are local audit files, not committed to git.

---

## Log Entry Format

```json
{
  "timestamp": "2026-03-02T16:45:00Z",
  "issueId": "ISSUE-042",
  "issueName": "login-rate-limiting",
  "phase": "discuss",
  "agent": "Discuss",
  "developer": "sri-lokesh",
  "status": "complete",
  "summary": "Defined rate limiting requirements: 5 attempts per 15 min, admin exemption",
  "decisions": [
    "Rate limit window: 15 minutes (not 5 — to reduce friction for legitimate users)",
    "Admin role is exempt from rate limiting",
    "Lockout applies per email, not per IP (to avoid shared IP issues)"
  ],
  "outputFile": "docs/issues/ISSUE-042-login-rate-limiting.md",
  "nextPhase": "research"
}
```

---

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `timestamp` | ISO 8601 | ✅ | When the phase completed |
| `issueId` | string | ✅ | e.g., `ISSUE-042` |
| `issueName` | string | ✅ | kebab-case name of the Issue |
| `phase` | string | ✅ | `discuss` \| `research` \| `plan` \| `execute` \| `verify` |
| `agent` | string | ✅ | Which agent completed this |
| `developer` | string | ✅ | Who ran the session |
| `status` | string | ✅ | `complete` \| `blocked` \| `partial` |
| `summary` | string | ✅ | 1-2 sentence summary of what was accomplished |
| `decisions` | string[] | ✅ | Key decisions made in this phase |
| `outputFile` | string | ✅ | Path to the Issue doc updated |
| `nextPhase` | string | ✅ | What phase comes next |
| `blockers` | string[] | ❌ | Any blockers (if `status: blocked`) |
| `testResults` | object | ❌ | For execute/verify phases |
| `filesChanged` | string[] | ❌ | For execute phase |

---

## Phase-Specific Fields

### Execute Phase
```json
{
  "phase": "execute",
  "filesChanged": [
    "src/middleware/rate-limit.ts (created)",
    "src/api/auth/route.ts (modified)"
  ],
  "commits": [
    "abc1234 - test: ISSUE-042 rate limit middleware tests",
    "def5678 - feat: ISSUE-042 apply rate limiting to login endpoint"
  ]
}
```

### Verify Phase
```json
{
  "phase": "verify",
  "testResults": {
    "unit": { "passed": 12, "failed": 0 },
    "integration": { "passed": 4, "failed": 0 },
    "e2e": { "passed": 2, "failed": 0 }
  },
  "requirementsMet": "3/3",
  "verdict": "ready"
}
```

---

## How to Read the Log

```bash
# All activity for a specific Issue
grep "ISSUE-042" logs/copilot/agent-activity.log | jq .

# All completed phases today
cat logs/copilot/agent-activity.log | jq 'select(.timestamp | startswith("2026-03-02"))'

# All blocked sessions
cat logs/copilot/agent-activity.log | jq 'select(.status == "blocked")'

# What Issues are in progress?
cat logs/copilot/agent-activity.log | jq '{issueId, phase, status}'
```