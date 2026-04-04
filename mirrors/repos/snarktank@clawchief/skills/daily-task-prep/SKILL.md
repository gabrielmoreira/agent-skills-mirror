---
name: daily-task-prep
description: "Prepare {{OWNER_NAME}}'s task list for the day using `~/.openclaw/workspace/tasks/current.md` plus his calendars. Use when a cron or direct request asks to prepare today's tasks before {{OWNER_NAME}} starts work; when recurring weekday tasks, due-today backlog items, and {{OWNER_NAME}}-owned meetings/calls should be added to `## Today`; or when the task list needs a safe early-morning refresh without overwriting {{OWNER_NAME}}'s manual priorities."
---

# Daily Task Prep

Use `~/.openclaw/workspace/tasks/current.md` as the canonical live task file.

## Goal

Quietly prepare today's `## Today` section before {{OWNER_NAME}} wakes up.

## Core rules

- Preserve existing manually added open tasks in `## Today` unless they are obviously stale past meetings.
- On weekdays, treat `## Every weekday` as the recurring seed list.
- On weekends, do **not** auto-add `## Every weekday` items unless {{OWNER_NAME}} explicitly asked.
- Promote items due today from `## Backlog with due date` into `## Today`, and remove the backlog copy in the same edit.
- Scan `## Recurring reminders` and add any reminder that is due today into `## Today` without deleting the recurring source item.
- Add {{OWNER_NAME}}-owned meetings and calls for today to `## Today`.
- Exclude personal or family calendar blocks, lunch/walk holds, travel holds, and appointments that belong to another household member or the family unless {{OWNER_NAME}} explicitly asks for them.
- Do not duplicate tasks that already exist with equivalent wording.
- Keep the `{{ASSISTANT_NAME}}:` ownership marker for tasks assigned to me.
- Update the file's `Last updated` timestamp.
- Stay silent unless something needs human attention.

## Preparation workflow

1. Read `tasks/current.md`.
2. Determine whether today is a weekday.
3. Build the candidate `## Today` list from:
   - current open `## Today` tasks worth carrying forward
   - weekday recurring items from `## Every weekday` if today is Monday-Friday
   - items in `## Backlog with due date` that are due today
   - items in `## Recurring reminders` whose recurrence makes them due today
   - today's {{OWNER_NAME}}-owned meetings/calls from calendar
4. Remove duplicates by normalized task text while keeping the most specific wording already present in the file.
5. Reorder the open tasks in this order:
   - existing explicit priority tasks
   - due-today items
   - recurring operating tasks
   - meetings/calls in time order
6. Keep completed items untouched unless a cleanup is obviously safe.
7. Write back only the minimal necessary edits.

## Calendar workflow

Use `gog` via shell to inspect {{OWNER_NAME}}'s visible calendars before adding meeting tasks.

Check these calendars when visible:
- `{{PERSONAL_EMAIL}}`
- `{{SECONDARY_CALENDAR_EMAIL_1}}`
- `{{PRIMARY_WORK_EMAIL}}`
- `{{SECONDARY_CALENDAR_EMAIL_2}}`
- `{{SECONDARY_CALENDAR_EMAIL_3}}`
- Family calendar only as a conflict source, not as a source of {{OWNER_NAME}} tasks

Only add calendar items that {{OWNER_NAME}} himself is expected to attend.

Useful shell pattern:

```bash
gog calendar events --all -a {{ASSISTANT_EMAIL}} --days=1 --max=100 --json --results-only
```

## Task text rules

- Use concise one-line tasks.
- Keep the existing task wording when it is already good.
- Use `YYYY-MM-DD` for all-day due dates and `YYYY-MM-DD HH:MM TZ` for timed due dates.
- Meeting task format should match the live file's existing style.
- If a backlog due-date item is promoted into `## Today`, remove the backlog copy immediately.
- For recurring reminders, keep the recurring source entry in place and only add the due instance into `## Today`.
- Use recurring reminder lines in this shape when present: `- [ ] Task — due YYYY-MM-DD[ HH:MM TZ] — recurs <period> every <n>`.

## Safety

- Do not wipe `## Today` just to rebuild it.
- Treat recurring reminders as due when the stored due timestamp lands on the current local date, or when the recurrence rule implies an occurrence on the current local date from that stored anchor date.
- For all-day reminders, compare by local date only.
- If calendar access fails, still do file-based prep and only notify {{OWNER_NAME}} if the failure matters.
- If the file structure has drifted, adapt to the live file instead of forcing a full reformat.
- If nothing needs to change, do nothing.
