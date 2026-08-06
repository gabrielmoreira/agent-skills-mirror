---
name: copilot-session-report
description: "Generate a detailed report of a Copilot CLI session — tools, skills, MCPs used, problem/solution narrative, files modified, testing results, key learnings, tool assessments, and pending work. Use when asked to create a session report, summarize a session, document what was done, or generate a session writeup."
---

# Copilot Session Report — Domain Knowledge

## Purpose

Generate a comprehensive per-session report after completing significant work. The report documents what was done, how it was done, what tools were involved, and lessons learned. Useful for PR descriptions, knowledge sharing, and self-review.

## When to Generate

- After multi-hour implementation sessions
- Before sharing session exports
- When attaching session context to ADO work items
- When the user asks to "summarize this session" or "create a report"

## Gathering Data

### 1. Session Metadata

```sql
SELECT id, summary, repository, branch, cwd, created_at, updated_at
FROM sessions
WHERE id = '<session_id>'
```

If querying the current session, use the session ID from the workspace context.

### 2. User Messages (for narrative)

```sql
SELECT turn_index, substr(COALESCE(user_message, ''), 1, 300) as msg
FROM turns
WHERE session_id = '<session_id>'
AND user_message IS NOT NULL
AND length(COALESCE(user_message, '')) > 5
ORDER BY turn_index
```

### 3. Tool Call Counts

```sql
SELECT tool_start_name as tool, COUNT(*) as calls
FROM events
WHERE session_id = '<session_id>'
AND type = 'tool.execution_complete'
AND tool_start_name IS NOT NULL
GROUP BY tool_start_name
ORDER BY calls DESC
```

### 4. Skill Invocations

Search user messages for `skill-context` patterns:

```sql
SELECT turn_index, substr(COALESCE(user_message, ''), 1, 300) as msg
FROM turns
WHERE session_id = '<session_id>'
AND user_message ILIKE '%skill-context%'
ORDER BY turn_index
```

### 5. Subagent Invocations

```sql
SELECT tool_start_name, substr(COALESCE(tool_complete_result_content, ''), 1, 500) as result
FROM events
WHERE session_id = '<session_id>'
AND type = 'tool.execution_complete'
AND tool_start_name = 'task'
LIMIT 10
```

### 6. Files Created/Edited

```sql
SELECT file_path, tool_name, turn_index
FROM session_files
WHERE session_id = '<session_id>'
ORDER BY turn_index
```

### 7. PR/Commit/Work Item References

```sql
SELECT ref_type, ref_value, turn_index
FROM session_refs
WHERE session_id = '<session_id>'
ORDER BY turn_index
```

### 8. Models Used

```sql
SELECT usage_model as model, COUNT(*) as turns
FROM events
WHERE session_id = '<session_id>'
AND usage_model IS NOT NULL
GROUP BY usage_model
ORDER BY turns DESC
```

### 9. Session Duration

```sql
SELECT
  created_at,
  updated_at,
  date_diff('minute', created_at, updated_at) as duration_min
FROM sessions
WHERE id = '<session_id>'
```

## Report Template

```markdown
# Copilot Session Report: <Title>

**Session ID**: `<id>`
**Date**: <date range>
**Work Item**: [#NNN](url) — "<title>"
**PR**: [#NNN](url)
**Model**: <primary model>

---

## Tools, Skills, MCP Servers, and Plugins Used

### Skills Invoked (N)

| Skill | Purpose |
|-------|---------|
| `skill-name` | Why it was activated |

### MCP Server: <Name> (N calls)

| Tool | Calls | Purpose |
|------|-------|---------|
| `server-tool_name` | N | What it was used for |

### Subagent: <Type> (N invocations)

- **Model**: <model>
- **Purpose**: <what was validated/explored>
- **Key finding**: <most impactful insight>

### Built-in Tools (N calls)

| Tool | Calls | Purpose |
|------|-------|---------|
| `powershell` | N | Building, deploying, testing |
| `view` | N | Reading source files |
| ... | | |

### Session Statistics

- **Total tool calls**: N
- **User messages**: N
- **Duration**: ~N hours

## Problem

<What was being solved — derived from user messages and context>

## Solution

<Approach taken, key design decisions, why alternatives were rejected>

## Files Modified

| File | Lines | Change |
|------|-------|--------|
| `path/to/file` | +N/−N | Description |

## Testing

### Unit Tests — N/N Passed

| Test | Result |
|------|--------|
| `TestName` | ✅/❌ |

### E2E Testing

<Describe end-to-end test scenarios and results>

### Regression

<Pre-existing failures vs new failures>

## Key Learnings

### <Learning Title>
<Description of gotcha, workaround, or discovered pattern>

## Tool Assessment

Evaluate tools that were considered, used, or deliberately not used.

### <Tool Name>: Assessment

| Requirement | Tool Capability | What Was Used Instead |
|---|---|---|
| <requirement> | ✅/❌/⚠️ <capability> | <alternative> |

**Recommendation**: <When this tool is/isn't appropriate for this type of work>

Use this section for:
- UI automation feasibility for the test scenario
- VM vs local testing tradeoffs
- Local vs remote execution tradeoffs
- Any tool that was expected to be used but wasn't

## Pending

- <Unfinished work items>
- <Follow-up tasks>
- <PR merge conflicts to resolve>
```

## Output

Save the report to `~/.copilot/session-state/<session-id>/files/session-report.md`.

Open in VS Code for review:
```powershell
code "~\.copilot\session-state\<session-id>\files\session-report.md"
```

## Tips

- **Reconstruct the narrative** from user messages — they tell the story of what was asked and in what order
- **Group tool calls by purpose**, not just raw counts — "179 powershell calls" is less useful than "building (45), deploying (30), testing (60), git (20), VM management (24)"
- **Highlight design decisions** — especially where a subagent (rubber-duck) or user correction changed the approach
- **Include specific error messages** and workarounds in Key Learnings — these are the most reusable parts
- **Tool Assessment** should be honest — if a tool wasn't used, explain why with a requirements comparison table
- **Cross-reference work items and PRs** — link them in the header for traceability
