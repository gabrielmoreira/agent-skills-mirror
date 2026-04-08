---
name: task-system-contract
description: "Shared Todoist-backed task contract for clawchief. Use when any workflow creates, updates, blocks, completes, or relies on live task state so the behavior stays consistent across executive-assistant, business-development, and daily task flows."
---

# Task System Contract

Use this skill as the shared Todoist contract for clawchief.

Todoist is the only live task system for clawchief. Archived markdown files may exist for history or migration reference, but no active workflow should depend on `clawchief/tasks.md` or recreate it.

Command surface:
- `python3 ~/.openclaw/workspace/clawchief/scripts/todoist_cli.py ...`

## Shared rules

- If `TODOIST_API_TOKEN` is missing, stop and ask Ryan for it before attempting live task management.
- Read `~/.openclaw/workspace/clawchief/priority-map.md` when program mapping, urgency, or routing is unclear.
- When Ryan assigns R2 a task with a due date or a clear time horizon, create or update the Todoist task in the same turn.
- When work depends on an external reply, delivery, approval, or later check-in, create a separate Todoist follow-up task instead of relying on inbox, calendar, CRM, or memory state alone.
- Use stable metadata keys for automation-created Todoist tasks whenever a recurring identity is obvious, especially for partner follow-ups, blockers, meeting-note access issues, and review reminders.
- If missing Gmail, Calendar, Docs, Sheets, or Slack access could hide real work or prevent delivery, create or update an explicit Todoist blocker task instead of silently degrading.
- If Slack delivery is unavailable, do not fail the run just because the DM channel or tool is missing. Preserve the blocked escalation in the run summary and record future work in Todoist when needed.
- If meeting notes create work, update Todoist and any other affected live source of truth in the same turn.
- If travel or location changes whether a task is actionable, update the Todoist task in the same turn so Ryan is not shown impossible work as active.
- Daily prep, heartbeats, and task summaries must read Todoist, not a shadow markdown list.
- Never update or recreate `clawchief/tasks.md`; Todoist is the only live task sink.

## Shared acceptance criteria

- Potential partner email:
  - if an email comes in from a potential partner, referral partner, or warm prospect, the workflow checks `~/.openclaw/workspace/clawchief/priority-map.md`
  - if future work remains, a Todoist follow-up task is created or updated in the same turn

- Ryan-to-R2 assignment:
  - if Ryan assigns R2 a task by email, Slack, or meeting note with a due date or a clear time horizon, that task is added to Todoist in the same turn

- Waiting on external reply:
  - if a thread is waiting on someone else and needs a later check-in, the system creates a separate Todoist follow-up task with an explicit due date

- Meeting-note ingestion:
  - if a meeting note creates work, the system updates Todoist and any other affected live source of truth in the same turn
  - if a Gemini doc is visible from calendar/thread context but access is denied, the system creates or updates a Todoist blocker task instead of treating the note as checked

- Default prospecting batch:
  - if the recurring default prospecting batch sends an initial outreach email, the system creates or updates a Ryan follow-up task for that contact in the same turn
  - the default task title pattern for those follow-ups is `Follow up with <FirstName> about Untangle outreach`

- Daily prep:
  - the morning prep flow reads Todoist, not legacy markdown
  - due-today and overdue follow-up tasks are surfaced, retuned, or left visible intentionally

- Blockers and delivery resilience:
  - if a required workflow surface is inaccessible, the system records the blocker explicitly in Todoist instead of declaring the domain fully checked
  - if Slack delivery is unavailable, the run does not fail just because the DM channel is missing

## Role-specific extensions

- `executive-assistant/SKILL.md` owns thread discipline, inbox handling, all-calendar availability checks, Family calendar requirements, and EA-side tracker updates.
- `business-development/SKILL.md` owns outreach-tracker updates, lead verification, CRM note discipline, schema verification, and prospecting policy.
- `daily-task-manager/SKILL.md` owns direct task CRUD behavior and user-facing task queries.
- `daily-task-prep/SKILL.md` owns the morning prep pass that retunes due work without rebuilding a markdown planning layer.
