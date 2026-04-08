---
name: daily-task-prep
description: "Prepare Ryan Carson's due-soon Todoist work using program sections plus due dates and his calendars. Use when a cron or direct request asks to prepare today's work before Ryan starts, when due-today and overdue items need to be surfaced, or when follow-up timing should be cleaned up without rebuilding a markdown task file."
---

# Daily Task Prep

Use Todoist as the canonical task system.

Command surface:
- `python3 ~/.openclaw/workspace/clawchief/scripts/todoist_cli.py ...`
- `~/.openclaw/workspace/clawchief/location-awareness.md`
- `~/.openclaw/workspace/clawchief/priority-map.md`

## Goal

Quietly prepare Todoist so due dates and follow-up timing reflect the real day.

## Core rules

- Read `~/.openclaw/skills/task-system-contract/SKILL.md` at the start of every run. Treat it as the shared Todoist contract for follow-ups, blockers, and no-legacy-markdown behavior.
- If `TODOIST_API_TOKEN` is missing, stop and ask Ryan for it.
- Bootstrap the Todoist schema before the first live prep run in a new account.
- Read `~/.openclaw/workspace/clawchief/location-awareness.md` before pulling place-dependent tasks forward.
- Keep due-soon work small and actually actionable.
- Prefer adjusting due dates or completing/recreating follow-up tasks over using workflow-state sections.
- Do not rebuild or recreate a live `clawchief/tasks.md` markdown task file as part of prep.
- Use recurring tasks natively in Todoist rather than cloning markdown reminders.
- Add Ryan-owned meetings/calls only when they are useful to track as tasks because they need prep, follow-up, or active attention.
- Exclude personal/family calendar blocks unless Ryan explicitly asks for them in Todoist.
- Review Business development partnerships and Executive assistant sections for reply-dependent follow-ups that should surface today.

## Preparation workflow

1. Run `doctor` or `bootstrap` if the account/project state is uncertain.
2. Read Todoist for overdue tasks, due-today tasks, and the current program sections.
3. Make sure genuinely active work has the right due date or deadline.
4. Push out tasks that are blocked, waiting on others, or future-only.
5. Review each major program section for tasks that should surface now because of urgency or date.
6. Add meeting prep or follow-up tasks when the calendar implies real work, not merely presence.
7. Leave quiet days quiet. If nothing needs to move, do nothing.
8. If a partner or EA follow-up is due today or overdue, do not leave it buried only in inbox or CRM state.

## Useful commands

Overdue work:

```bash
python3 ~/.openclaw/workspace/clawchief/scripts/todoist_cli.py list-tasks --overdue
```

Ryan work due today:

```bash
python3 ~/.openclaw/workspace/clawchief/scripts/todoist_cli.py list-tasks --owner ryan --due-today
```

Current customer-program tasks:

```bash
python3 ~/.openclaw/workspace/clawchief/scripts/todoist_cli.py list-tasks --section "First 10 paying customers"
```

Promote or retune a task:

```bash
python3 ~/.openclaw/workspace/clawchief/scripts/todoist_cli.py update-task \
  --metadata-key some-stable-key \
  --section "Business development partnerships" \
  --due-date 2026-04-08 \
  --priority 2
```

Create a meeting-prep task:

```bash
python3 ~/.openclaw/workspace/clawchief/scripts/todoist_cli.py upsert-task \
  --content "Prepare for Colleen ONeil intro" \
  --owner ryan \
  --section "Business development partnerships" \
  --priority 2 \
  --due-datetime 2026-04-08T14:30:00 \
  --due-timezone America/New_York \
  --metadata-key meeting-prep-colleen-oneil \
  --meta program="Business development partnerships" \
  --meta source=clawchief \
  --meta kind=meeting_prep
```

## Cron vs heartbeat boundary

Use this prep flow as the precise scheduled morning reset.

Heartbeat should:
- read Todoist as already prepared
- handle changed reality
- surface blockers or needed decisions
- avoid redoing morning prep unless Ryan explicitly asks

## Safety

- Do not flood due-today work with backlog or every recurring task.
- Do not create a Todoist task for every harmless calendar event.
- If calendar access fails, still do Todoist-only prep and notify Ryan only if the miss matters.
- If nothing needs to change, do nothing.
