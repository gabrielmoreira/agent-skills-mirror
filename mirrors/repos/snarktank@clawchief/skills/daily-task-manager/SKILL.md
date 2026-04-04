---
name: daily-task-manager
description: "Manage {{OWNER_NAME}}'s day-to-day task list using a single canonical workspace file that stays synced across sessions and heartbeats. Use when {{OWNER_NAME}} asks to add, remove, complete, defer, reprioritize, summarize, or review current tasks/todos; when a heartbeat or check-in should reference the live task list; or when task state was mentioned in another session and must be reflected centrally. Prefer this skill whenever current live task state is involved instead of relying on memory files or stale conversation context."
---

# Daily Task Manager

Use `~/.openclaw/workspace/tasks/current.md` as the canonical live task list.

## Gotchas

- Do not use memory files or old chat context as the live source of task truth.
- Do not ask again about tasks already marked done in `tasks/current.md`.
- When {{OWNER_NAME}} changes task state, update `tasks/current.md` in the same turn whenever practical.
- If a task is promoted from a backlog section into `## Today`, remove the old backlog copy in the same edit.
- Heartbeat task check-ins should reference only the current file state.

## Core rules

1. Read `tasks/current.md` before answering questions about {{OWNER_NAME}}'s current tasks or composing proactive task check-ins.
2. Treat `tasks/current.md` as the source of truth across all sessions.
3. When {{OWNER_NAME}} says a task is done, added, blocked, canceled, or moved, update `tasks/current.md` in the same turn whenever practical.
4. When {{OWNER_NAME}} gives {{ASSISTANT_NAME}} a task with a due date or a clear time horizon, add an `{{ASSISTANT_NAME}}:` task in the same turn using the canonical due-date format.
5. When that task depends on an outside reply, delivery, or future check-in, add a separate `{{ASSISTANT_NAME}}:` follow-up task with its own due date instead of relying on memory or inbox state.
6. When using this skill, scan for overdue and due-today `{{ASSISTANT_NAME}}:` tasks before deciding what needs attention.
7. Keep long-term preferences in memory files, but keep live operational task state in `tasks/current.md`.
8. If a task change materially affects heartbeat behavior, update the heartbeat instructions or ensure they already point to `tasks/current.md`.
9. Prefer concise, plain-English task phrasing.
10. Use `YYYY-MM-DD` for all-day due dates and `YYYY-MM-DD HH:MM TZ` for timed due dates.
11. Preserve completion timestamps when known.

## Canonical file structure

Follow the format documented in [references/task-file-format.md](references/task-file-format.md).

At minimum, maintain these sections:
- `## Today`
- `## Next up after today`
- `## Rules`

Optional sections when useful:
- `## Every weekday`
- `## Backlog with due date`
- `## Recurring reminders`
- `## Backlog`

Within `## Today`, keep tasks split into:
- open tasks as `- [ ] ...`
- completed tasks as `- [x] ...`

## Update workflow

### When {{OWNER_NAME}} adds a task
- Add it to `## Today` unless he clearly assigns it to another time horizon.
- If {{OWNER_NAME}} gives the task a due date beyond today, prefer `## Backlog with due date` unless he explicitly wants it on `## Today` now.
- Keep the newest urgent tasks near the top.
- If the task already exists in `## Backlog` or `## Backlog with due date`, remove that older copy when adding it to `## Today`.
- If the task is assigned to me, use `{{ASSISTANT_NAME}}:` in the task text.
- If the task will likely need a later nudge or status check, add a separate follow-up task at the same time.

### When {{OWNER_NAME}} completes a task
- Change it to `- [x]`.
- Add a completion timestamp if known from the message or existing notes.

### When {{OWNER_NAME}} changes priority
- Reorder the open tasks so the current highest-priority work is first.

### When {{OWNER_NAME}} asks what is left
- Read the file and report only the open tasks unless he asks for completed work too.

### When {{OWNER_NAME}} asks to prepare today's tasks
- Use the `## Every weekday` section as the template when the founder wants today's task list prepared from the recurring baseline.
- Treat `## Today` as the committed instance for the current day, even if some items also appear in `## Every weekday`.
- Do not treat overlap between `## Today` and `## Every weekday` as an error by itself.

### When all current open tasks are done
- Read and execute the instruction in `## Next up after today` if the founder asked for proactive help or the heartbeat needs a next action.

## Heartbeat behavior

When a heartbeat includes task follow-up:
- read `tasks/current.md`
- ask about open tasks only
- do not ask again about tasks already marked done
- keep the message short and direct

## Notes

- Use memory files for durable workflow preferences, not for the canonical live task list.
- Do not rely on memory or inbox state alone for future follow-ups; write the follow-up into `tasks/current.md`.
- {{OWNER_NAME}}-specific preference: when he asks to prepare his tasks for the day, use `## Every weekday` as the template unless he says otherwise.
- `## Today` may intentionally duplicate recurring items because it represents the explicit plan for that day.
- Use `{{ASSISTANT_NAME}}:` as the formal ownership marker for tasks assigned to me.
- `## Recurring reminders` is a parked source section for recurring reminders; do not treat those items as active `## Today` tasks unless they have been explicitly promoted.
- When adding meetings to `## Today`, include only {{OWNER_NAME}}-owned meetings/calls. Do not add personal calendar blocks, lunch/walk holds, or family appointments unless {{OWNER_NAME}} explicitly asks.
- If the task list format needs to evolve, update the reference file first, then keep `tasks/current.md` consistent with it.
