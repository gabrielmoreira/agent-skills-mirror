# AGENTS.md

Task framework support and task packages live here.

- Individual tasks are discovered from `src/tasks/<task_name>/task.py`; do not add per-task AGENTS files unless requested.
- Tasks must implement the `ContinualLearningTask` lifecycle and register with `@register_task("<name>")`.
- Generate instances deterministically with `random.Random(self.seed)`; never use global random state for benchmark fixtures.
- Set stable `Query.instance_id` and `Query.instance_index`, and emit `InstanceOutcome` values for scoring.
- Keep schedule and variant JSON ids matched to filenames; every run-all task needs `schedules/default.json`.
- Do not put raw datasets, hidden labels, benchmark answers, or copied traces in agent docs.
