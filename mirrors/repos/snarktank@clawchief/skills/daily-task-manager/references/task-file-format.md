# Task file format

Use this structure for `~/.openclaw/workspace/tasks/current.md`.

```md
# Current Tasks

Last updated: YYYY-MM-DD HH:MM TZ
Owner: {{OWNER_NAME}}
Canonical file: use this file as the source of truth across sessions

## Today

### Open
- [ ] Task 1
- [ ] Task 2

### Done
- [x] Task 3 — completed YYYY-MM-DD HH:MM TZ

## Next up after today
- Next action to take once all open items in `## Today` are done

## Every weekday
- Recurring weekday operating task

## Backlog with due date
- Due-soon one-off task — due 2026-04-07

## Recurring reminders
- [ ] Reminder task — due 2026-04-03 15:00 EDT — recurs weekly every 1

## Backlog
- Someday / undated task

## Rules
- Update this file when {{OWNER_NAME}} adds, completes, defers, blocks, or cancels a task.
- Heartbeats should read from this file instead of repeating stale task text.
- Keep wording short and operational.
```

Guidelines:
- Prefer one line per task.
- Use `YYYY-MM-DD` for all-day due dates and `YYYY-MM-DD HH:MM TZ` for timed due dates.
- Use `— completed ...` for known completion timestamps.
- Reorder open tasks when {{OWNER_NAME}} changes priority.
- Remove canceled tasks instead of leaving them as clutter unless the cancellation matters for context.
- If a task is deferred to another day, move it out of `## Today` and reflect the new timing in plain English.
- `## Recurring reminders` is for reminders that stay parked in the file with recurrence metadata until a prep flow promotes the due instance into `## Today`.
- Overlap between `## Today` and source sections like `## Every weekday` or `## Recurring reminders` is acceptable when today's explicit plan has been prepared.
