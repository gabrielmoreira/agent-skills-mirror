# Task file format

Use this structure for `clawchief/tasks.md`.

```md
# Current Tasks

Last updated: YYYY-MM-DD HH:MM TZ
Canonical file: use this file as the source of truth across sessions

## Today

### Principal
#### Program or person name
- [ ] Principal task

### Assistant
#### Program or person name
- [ ] Assistant task

## Every weekday
#### Program or person name
- Recurring weekday operating task

## Backlog with due date
- Important task — due YYYY-MM-DD

## Recurring reminders
- [ ] Reminder task — due YYYY-MM-DD HH:MM TZ — recurs weekly every 1

## Backlog
- Someday / undated task

## Rules
- Update this file when task state changes.
- Heartbeats should read from this file instead of repeating stale task text.
- Prior-day completed tasks should be moved to `clawchief/tasks-completed.md` during daily prep.
```

Use this structure for `clawchief/tasks-completed.md`.

```md
# Completed Tasks

Last updated: YYYY-MM-DD HH:MM TZ
Archive file: completed tasks moved out of `tasks.md`

## YYYY-MM-DD

### Principal
- [x] Completed task — completed YYYY-MM-DD HH:MM TZ

### Assistant
- [x] Completed task — completed YYYY-MM-DD HH:MM TZ
```

Guidelines:
- prefer one line per task
- use `YYYY-MM-DD` for all-day due dates and `YYYY-MM-DD HH:MM TZ` for timed due dates
- keep `tasks.md` focused on live/open work plus same-day completions that have not yet been archived
- use active-task grouping headers that match your priority map when there is a clear fit
