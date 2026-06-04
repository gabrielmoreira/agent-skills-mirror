---
mode: agent
description: Run foresight gap-and-risk analysis on the current task before making any changes. Reports findings and asks whether to proceed.
---

# /ai-foresight

Run the foresight engine against the current working context before making changes. Surfaces gaps, risks, and proactive suggestions. Does **not** apply any changes.

> **→ [Foresight Engine](../../.ai/engine/foresight_engine.py)** — gap detection and risk forecasting logic.
> **→ [Runtime Config](../../.ai/agent-config.yaml)** — `foresight.enabled` and `gap_analysis` settings.

---

## Steps

### 1. Collect context

- Identify the **current working path** from the user's task description or session context.
- Collect **task context**: what is being asked, what files are involved, what kind of change is planned.
- Collect **recent staged changes**: run `git diff --cached --stat` for a summary, and `git diff --cached --unified=2` for meaningful hunks (truncate at ~4000 chars).

### 2. Run foresight analysis

Apply the logic from `.ai/engine/foresight_engine.py` for the current path and combined context (task + staged diff):

**Gap detection** — flag each as `high`, `medium`, or `low` severity:
- Error handling: are `try/except` / `catch` / `.catch()` patterns present or referenced?
- Observability: is structured logging present or referenced?
- Test coverage: are tests referenced or included for the changed behaviour?

**Risk forecasting** — flag each with a probability:
- SQL injection / credential exposure: database, query, or SQL keywords present?
- Credential exposure: secret, password, token, or key terms in the change context?
- Destructive operation: delete, remove, or drop terms present? → archive-first rule applies.

**Proactive suggestions** — note patterns worth addressing regardless of gaps found.

### 3. Report findings

Group by type, ordered by severity (high → medium → low):

```
## Foresight Report
### Gaps
- [HIGH] Error handling: ...recommendation...
- [MEDIUM] Test coverage: ...recommendation...

### Risks
- [MEDIUM/security] SQL injection: ...recommendation...

### Proactive Suggestions
- ...
```

### 4. Decision prompt

Ask the user: **"Proceed with the task, address gaps first, or adjust the plan?"**

Do not continue with the original task until the user responds.

### 5. Append to knowledge base (optional)

Only if the user confirms: append the analysis result to `.ai/knowledge/anticipated-gaps.md` using the schema documented in `.ai/knowledge/.gitkeep`.

---

## Notes

- This is an advisory command — it never modifies files on its own.
- If `foresight.enabled` is `false` in `agent-config.yaml`, report that and skip analysis.
- Adjust detection keywords to the project's primary language (e.g. `catch` for JS/TS, `except` for Python, `CATCH` for SQL stored procedures).
