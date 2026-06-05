---
mode: ask
description: Show runtime observability and knowledge base system. Display metrics, logs, cheat sheets. Understand what the framework learned.
---

# /ai-observe — Runtime Observability & Learning

Get visibility into what the AI framework has learned and discovered.

## What This Shows

This command aggregates and displays:

1. **Foresight Analysis Logs** — What gaps and risks were anticipated before tasks
2. **Memory Hygiene Status** — Stale entries, duplicates, knowledge base health
3. **Metrics Dashboard** — Patterns, anomalies, task breakdown
4. **Module Cheat Sheets** — Quick reference for each module

## How to Use

```powershell
# Show metrics dashboard (last 7 days)
python .ai/engine/show_metrics.py . --window 7d

# Show all knowledge base entries
python .ai/engine/memory_hygiene.py . --list

# Search knowledge base by keyword
python .ai/engine/memory_hygiene.py . --search "auth flow"

# Find stale entries (older than 180 days)
python .ai/engine/memory_hygiene.py . --older-than 180 --dry-run

# Show foresight findings from a specific task
cat .ai/logs/foresight-YYYYMMDD_HHMMSS.jsonl | python -m json.tool
```

## Understanding the Logs

### Foresight Logs (`.ai/logs/foresight-*.jsonl`)

When the AI analyzes a task, it logs anticipated gaps and risks:

```json
{
  "timestamp": "2026-06-04T06:39:04Z",
  "task_description": "add new API endpoint for user creation",
  "scope": "api",
  "gaps_count": 6,
  "risks_count": 2,
  "gaps": [
    {
      "category": "error_handling",
      "title": "Error handling not implemented",
      "severity": "warning"
    },
    ...
  ],
  "risks": [
    {
      "level": "error",
      "title": "Potential security issue",
      "mitigation": "Review for hardcoded secrets..."
    },
    ...
  ],
  "recommendation": "PROCEED WITH CAUTION: Fix all [ERROR] items before shipping"
}
```

**What to look for**:
- **recommendation**: Should say PROCEED, not CAUTION or ERROR
- **gaps_count**: High gap count = complex task (expect more review)
- **risks_count**: Any ERROR-level risks? Those are blockers
- **task breakdown by scope**: Are most tasks in api/ or gui/? Good signal for module maturity

### Memory Hygiene Status

```
[OK] Knowledge Base Entries (24)
  cheat-sheets/ (6)
    - api-cheat.md (15 days old)
    - gui-cheat.md (45 days old) [OK]
    - database-cheat.md (200 days old) [STALE]

  patterns/ (12)
  risks/ (6)
  .old/ (archived entries)

[Duplicates] None found
[Stale] 1 entry (> 180d) — consider archival
```

**What to fix**:
- Stale entries (>180d): Review if still relevant, or archive
- Duplicates (>60% similar): Merge and archive the duplicate

### Metrics Dashboard

Example output:

```
[SUMMARY]
  Foresight analyses: 42
  Heartbeat checks: 156
  Knowledge captures: 8

[FORESIGHT ANALYSIS]
  Total gaps found: 267
  Total risks identified: 84
  Avg gaps per task: 6.4
  Tasks by scope:
    api: 18
    gui: 15
    database: 9

[TOP RISKS IDENTIFIED]
   8x Potential security issue
   7x Potential performance problem
   4x Input validation missing

[TOP GAPS ANTICIPATED]
  12x Error handling not implemented
  11x Tests not written
   9x Documentation missing
```

**Interpretation**:
- If "security issues" dominates: Need more security review in API
- If "tests not written" is high: Testing culture needs improvement
- If "performance problem" recurs: Profile common bottlenecks

---

## Integration with Framework

### Before You Code: `/ai-foresight`

```powershell
/ai-foresight
```

AI reads authoritative rules, runs foresight analysis, logs to `.ai/logs/foresight-*.jsonl`, then recommends GO/NO-GO.

### During Development: Check Cheat Sheets

```powershell
# Your module's quick reference
cat .ai/knowledge/cheat-sheets/api-cheat.md
```

Shortcut to common patterns + gotchas for your module. Not authoritative rules; rather team experience.

### After Task: `/ai-reflect`

```powershell
/ai-reflect
```

AI learns what worked, what failed, and proposes new KB entries or updates to `.ai/instruct.md`.

### Monthly: Run Hygiene

```powershell
# Check KB health
python .ai/engine/memory_hygiene.py . --older-than 180 --dry-run

# If entries are stale, review and archive
python .ai/engine/memory_hygiene.py . --older-than 180 --archive
```

---

## Cheat Sheet Examples

Each module can maintain a quick reference in `.ai/knowledge/cheat-sheets/`:

**API Cheat Sheet** (`api-cheat.md`):
```markdown
# API Module Cheat Sheet

## Common Pattern: Creating an Endpoint

POST /api/v1/{resource}_{action}
- resource: user, product, order, etc.
- action: create, list, update, delete, etc.
- Full list: .ai/api-conventions.md

## Known Gotcha: Auth Flow

Don't forget the Authorization header!
See auth-api example in .examples/
```

**GUI Cheat Sheet** (`gui-cheat.md`):
```markdown
# GUI Module Cheat Sheet

## Element IDs Must Have Prefixes

All interactive elements need 2-letter prefixes:
- bu_ for buttons
- in_ for inputs
- dd_ for dropdowns
See .ai/coding-prefixes.md

## Common Form Pattern

Use Formik + Yup for validation
```

These are **not** authoritative rules. Rather: team shortcuts, common mistakes, registry links.

---

## See Also

- [`.ai/knowledge/README.md`](../../.ai/knowledge/README.md) — Knowledge base overview
- [`.ai/knowledge/.cleanup-policy.md`](../../.ai/knowledge/.cleanup-policy.md) — KB hygiene rules
- [`.ai/engine/show_metrics.py`](../../.ai/engine/show_metrics.py) — Metrics dashboard
- [`.ai/engine/memory_hygiene.py`](../../.ai/engine/memory_hygiene.py) — KB maintenance tool
- [`.ai/engine/foresight_engine_observable.py`](../../.ai/engine/foresight_engine_observable.py) — Foresight analysis
- `/ai-foresight` — Before-task analysis
- `/ai-reflect` — After-task learning
- `/ai-check-yourself` — Reset to baseline rules
