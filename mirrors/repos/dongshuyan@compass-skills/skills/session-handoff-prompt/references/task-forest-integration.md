# Task-Forest Integration

Task-forest is an extra source. It does not replace the session, transcript, or workspace evidence.

## Read Locations

When the current workspace has task-forest exports, read these files only:

```text
.agent-workbench/task-forest/exports/task-forest.graph.json
.agent-workbench/task-forest/exports/task-forest.todos.json
.agent-workbench/task-forest/exports/task-forest.timeline.json
```

Use `scripts/read_task_forest_exports.py --workspace <workspace>` for a bounded summary.

## Boundaries

- Read exports only.
- Do not modify `.agent-workbench/task-forest/`.
- Do not save proposals.
- Do not call `proposal-apply`.
- Do not infer that a missing export means no tasks exist.

## Merge Rules

- Current session or transcript answers: "what just happened?"
- Task-forest answers: "where does this work fit in the long-running structure?"
- Workspace evidence answers: "what is true on disk now?"

If task-forest and the latest session conflict, include the conflict as an item to verify. Do not turn it into a verified fact.

## Prompt Section

When task-forest exports were read, include a compact task state section:

```text
Task-forest state:
- Related goal: ...
- Current node or todo: ...
- Dependencies / blockers: ...
- Possible sync risk: ...
```

If exports were not found, omit the section or write one sentence saying that the handoff is based on the session and workspace evidence only.
