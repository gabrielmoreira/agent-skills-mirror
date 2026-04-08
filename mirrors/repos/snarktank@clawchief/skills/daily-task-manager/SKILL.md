---
name: daily-task-manager
description: "Manage Ryan Carson's live tasks in Todoist, not markdown. Use when Ryan asks to add, remove, complete, defer, block, reprioritize, summarize, or review current tasks; when a heartbeat or check-in should reference live task state; or when task changes need to be reflected centrally in the same turn."
---

# Daily Task Manager

Use Todoist as the canonical live task system.

Command surface:
- `python3 ~/.openclaw/workspace/clawchief/scripts/todoist_cli.py ...`
- `python3 ~/.openclaw/workspace/clawchief/scripts/todoist_cli.py schema`

Legacy files:
- `~/.openclaw/workspace/clawchief/archive/legacy-tasks-2026-04-07.md` is the archived migration snapshot, not the live task database.
- `~/.openclaw/workspace/clawchief/archive/legacy-tasks-completed-2026-04-07.md` is markdown-era archive residue, not the live completion ledger.

## Gotchas

- Read `~/.openclaw/skills/task-system-contract/SKILL.md` at the start of every run. Treat it as the shared Todoist contract for follow-ups, blockers, and no-legacy-markdown behavior.
- If `TODOIST_API_TOKEN` is missing, stop and ask Ryan for it before trying to manage live tasks.
- Run the Todoist bootstrap once in a new account before relying on the project structure.
- Do not recreate a hidden markdown mirror of live tasks.
- Never update or recreate `clawchief/tasks.md`; Todoist is the only live task sink.
- Use `upsert-task` for automation-created tasks whenever a stable key is obvious.
- Keep long-term preferences in memory files, and keep live operational task state in Todoist.
- Read `~/.openclaw/workspace/clawchief/priority-map.md` when domain or urgency is unclear.
- Read `~/.openclaw/workspace/clawchief/location-awareness.md` when travel or location changes actionability.

## Core rules

1. Read Todoist before answering questions about Ryan's current tasks.
2. When Ryan changes task state, update Todoist in the same turn whenever practical.
3. When Ryan gives R2 a task with a due date or clear time horizon, create the R2 task in Todoist in the same turn.
4. When a task depends on an outside reply, delivery, or future check-in, create a separate Todoist follow-up task.
5. Use Todoist native due/deadline fields instead of markdown date conventions.
6. Use sections for program grouping, assignees for owner, due dates/deadlines for timing, and labels only for secondary context.
7. If Todoist and any archived markdown task file disagree, Todoist wins unless Ryan explicitly says otherwise.
8. When a partner / prospect / referral thread creates future work, use a stable metadata key so repeated sweeps update one follow-up task instead of creating duplicates.

## Canonical Todoist shape

- Project: `Clawchief`
- Sections: the program names from `~/.openclaw/workspace/clawchief/priority-map.md`, plus `General / uncategorized` when no clear program exists
- Assignees: `ryan`, `r2`
- Context labels when needed: `blocked`, `travel`, or a small number of useful domain hints

## Common commands

Bootstrap:

```bash
python3 ~/.openclaw/workspace/clawchief/scripts/todoist_cli.py bootstrap
```

List open Ryan tasks due today:

```bash
python3 ~/.openclaw/workspace/clawchief/scripts/todoist_cli.py list-tasks --owner ryan --due-today
```

List overdue R2 tasks:

```bash
python3 ~/.openclaw/workspace/clawchief/scripts/todoist_cli.py list-tasks --owner r2 --overdue
```

Create or update a task:

```bash
python3 ~/.openclaw/workspace/clawchief/scripts/todoist_cli.py upsert-task \
  --content "Follow up with Rebecca Tydeman" \
  --owner r2 \
  --section "Business development partnerships" \
  --priority 2 \
  --due-date 2026-04-08 \
  --metadata-key partner-followup-rebecca \
  --meta program="Business development partnerships" \
  --meta source=clawchief \
  --meta kind=followup
```

Update an existing task:

```bash
python3 ~/.openclaw/workspace/clawchief/scripts/todoist_cli.py update-task \
  --metadata-key partner-followup-rebecca \
  --section "Business development partnerships" \
  --priority 1
```

Complete a task:

```bash
python3 ~/.openclaw/workspace/clawchief/scripts/todoist_cli.py complete-task \
  --metadata-key partner-followup-rebecca \
  --comment "Handled during EA sweep."
```

Recent completions:

```bash
python3 ~/.openclaw/workspace/clawchief/scripts/todoist_cli.py completed-tasks --days 7
```

Partner follow-up pattern:

```bash
python3 ~/.openclaw/workspace/clawchief/scripts/todoist_cli.py upsert-task \
  --content "Follow up with Jane Doe on partner reply" \
  --owner r2 \
  --section "Business development partnerships" \
  --priority 2 \
  --due-date 2026-04-08 \
  --metadata-key partner-followup-jane-doe \
  --meta program="Business development partnerships" \
  --meta source=email \
  --meta kind=partner_followup
```

## Update workflow

### When Ryan adds a task

- Put it in the right Todoist section.
- Assign it to exactly one owner unless there is a compelling exception.
- Put it in the matching program section from the priority map when that mapping is clear.
- If the task will need a later nudge or status check, add a separate follow-up task immediately.

### When Ryan completes a task

- Complete it in Todoist.
- Add a comment first only if the completion context matters later.

### When Ryan changes priority or actionability

- Update section, priority, due/deadline, labels, or wording so Todoist matches reality.
- If travel/location blocks the task, change the due date if needed and mark the constraint clearly.

### When Ryan asks what is left

- Read Todoist and report the actually actionable open tasks unless he asks for blocked or waiting work too.

### When Ryan asks what got done

- Read Todoist recent completed-task history.

### When Ryan asks to prepare the day

- Use Todoist recurring tasks, due dates, deadlines, and current sections.
- Do not rebuild a second daily markdown planning layer.

## Heartbeat behavior

When a heartbeat includes task follow-up:
- read Todoist, not `clawchief/tasks.md`
- ask about open tasks only
- keep the message short and direct
- do not try to re-plan the whole day unless Ryan asked for prep

## Migration note

If Ryan explicitly wants the old markdown tasks imported, use:

```bash
python3 ~/.openclaw/workspace/clawchief/scripts/todoist_cli.py import-markdown
python3 ~/.openclaw/workspace/clawchief/scripts/todoist_cli.py import-markdown --apply
```
