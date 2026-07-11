# Node Types

Read this file only when adding or classifying task-forest nodes.

## Classification Order

Classify new content in this order:

- `global_task`: a long-running user goal that does not naturally belong under an existing global task.
- `task` / `subtask`: concrete work needed to complete an existing task.
- `requirement`: a new or corrected acceptance requirement that is not standalone work.
- `decision`: a design choice, boundary, or tradeoff settled in the session.
- `risk`: a blocker, safety issue, data risk, accuracy risk, or execution deviation.
- `question`: something the user must answer before progress can continue.
- `follow_up`: a small item to handle after the session.

When one piece of work serves multiple goals, keep one primary `child_of` parent and use `contributes_to` for other goals.

## Important Fields

Record these fields for important tasks when evidence supports them:

- `purpose`: the user's real goal served by the task.
- `desired_outcomes`: concrete results the user expects.
- `success_metrics`: how success will be recognized.
- `non_goals`: explicit exclusions.
- `assumptions`: assumptions required by the current plan.
- `alignment`: why the task fits the goal, remaining gaps, and how fit will be verified.
