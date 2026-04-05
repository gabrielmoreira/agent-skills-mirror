---
name: daily-task-prep
description: "Prepare {{OWNER_NAME}}'s task list for the day using `clawchief/tasks.md` plus their calendars. Use when a cron or direct request asks to prepare today's tasks before the day starts; when recurring weekday tasks, due-today backlog items, and principal-owned meetings / calls should be added to `## Today`; or when the task list needs a safe early-morning refresh without overwriting manual priorities."
---

# Daily Task Prep

Use `clawchief/tasks.md` as the canonical live task file and `clawchief/tasks-completed.md` as the completed-task archive.

## Core rules

- read `clawchief/priority-map.md` before regrouping or inserting active tasks
- preserve existing manually added open tasks in `## Today` unless they are obviously stale past meetings
- on weekdays, treat `## Every weekday` as the recurring seed list
- on weekends, do not auto-add `## Every weekday` items unless explicitly asked
- promote items due today from `## Backlog with due date` into `## Today`, and remove the backlog copy in the same edit
- scan `## Recurring reminders` and add any reminder that is due today into `## Today` without deleting the recurring source item
- add principal-owned meetings and calls for today to `## Today`
- exclude personal or family calendar blocks that are only conflict sources, not principal-owned tasks
- keep assistant tasks clearly separate from principal tasks
- archive tasks completed yesterday out of `clawchief/tasks.md` into `clawchief/tasks-completed.md`
- keep tasks completed today in `clawchief/tasks.md` until the next morning's prep run unless the user explicitly wants earlier cleanup
- update the file's `Last updated` timestamp
- stay silent unless something needs human attention

## Preparation workflow

1. read `clawchief/tasks.md`
2. read `clawchief/priority-map.md`
3. read `clawchief/tasks-completed.md` if it exists
4. determine whether today is a weekday
5. archive tasks completed yesterday from `clawchief/tasks.md` into `clawchief/tasks-completed.md`
6. build the candidate `## Today` list from:
   - current open `## Today` tasks worth carrying forward
   - weekday recurring items from `## Every weekday` if today is Monday-Friday
   - items in `## Backlog with due date` that are due today
   - items in `## Recurring reminders` whose recurrence makes them due today
   - today's principal-owned meetings / calls from calendar
7. remove duplicates by normalized task text while keeping the most specific wording already present in the file
8. preserve or assign each active task to the best matching owner section plus program / person grouping header
9. reorder the open tasks in priority-first order within each owner section
10. write back only the minimal necessary edits

## Calendar workflow

Use `gog` via shell to inspect the principal's visible calendars before adding meeting tasks.

Useful pattern:

```bash
gog calendar events --all -a {{ASSISTANT_EMAIL}} --days=1 --max=100 --json --results-only
```

Only add calendar items that the principal is actually expected to attend.

## Task text rules

- use concise one-line tasks
- keep existing wording when it is already good
- use `YYYY-MM-DD` for all-day due dates and `YYYY-MM-DD HH:MM TZ` for timed due dates
- if a backlog due-date item is promoted into `## Today`, remove the backlog copy immediately
- for recurring reminders, keep the recurring source entry in place and only add the due instance into `## Today`

## Safety

- do not wipe `## Today` just to rebuild it
- do not archive recurring source items from `## Recurring reminders`
- do not archive tasks completed today during the same day's prep run
- if calendar access fails, still do file-based prep and only notify the user if the failure matters
- if nothing needs to change, do nothing
