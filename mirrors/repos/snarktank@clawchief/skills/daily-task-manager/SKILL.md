---
name: daily-task-manager
description: "Manage {{OWNER_NAME}}'s day-to-day task list using a single canonical workspace file that stays synced across sessions and heartbeats. Use when the user asks to add, remove, complete, defer, reprioritize, summarize, or review current tasks / todos; when a heartbeat or check-in should reference the live task list; or when task state was mentioned in another session and must be reflected centrally."
---

# Daily Task Manager

Use `clawchief/tasks.md` as the canonical live task list and `clawchief/tasks-completed.md` as the completed-task archive.

## Core rules

1. read `clawchief/tasks.md` before answering questions about current tasks or composing proactive task check-ins
2. treat `clawchief/tasks.md` as the source of truth across all sessions
3. when task state changes, update `clawchief/tasks.md` in the same turn whenever practical
4. when the assistant gets a task with a due date or a clear time horizon, add an assistant-owned task in the same turn using the canonical due-date format
5. when that task depends on an outside reply, delivery, or future check-in, add a separate follow-up task with its own due date instead of relying on memory or inbox state
6. scan for overdue and due-today assistant tasks before deciding what needs attention
7. keep long-term preferences in memory files, keep live operational state in `clawchief/tasks.md`, and keep prior-day completed task history in `clawchief/tasks-completed.md`
8. if a task change materially affects heartbeat behavior, update the heartbeat instructions or ensure they already point to `clawchief/tasks.md`
9. use `YYYY-MM-DD` for all-day due dates and `YYYY-MM-DD HH:MM TZ` for timed due dates

## Structure expectations

At minimum, maintain these sections:
- `## Today`
- `## Every weekday` when useful
- `## Backlog with due date` when useful
- `## Recurring reminders` when useful
- `## Backlog` when useful
- `## Rules`

Within `## Today`, prefer owner sections:
- `### Principal`
- `### Assistant`

Within active owner sections, prefer grouping under:
- `#### <program or person from priority-map.md>`
- `#### Other / uncategorized`

## Update workflow

### When a task is added
- add it to `## Today` unless it clearly belongs to another time horizon
- if it has a due date beyond today, prefer `## Backlog with due date` unless it must be active now
- if it already exists in backlog, remove the older copy when promoting it into `## Today`
- if it likely needs a later nudge or status check, add a separate follow-up task at the same time

### When a task is completed
- change it to `- [x]`
- preserve a completion timestamp when known
- leave same-day completions in `clawchief/tasks.md` until the next daily prep run unless the user wants immediate archive cleanup

### When priority changes
- reorder the open tasks so the current highest-priority work is first

### When the user asks what is left
- report only the open tasks unless they ask for completed work too

## Heartbeat behavior

When a heartbeat includes task follow-up:
- read `clawchief/tasks.md`
- ask about open tasks only
- do not ask again about tasks already marked done
- keep the message short and direct
