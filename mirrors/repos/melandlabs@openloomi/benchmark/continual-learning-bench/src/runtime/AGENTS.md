# AGENTS.md

This package owns the single task-system loop.

- Preserve the order: build query, system responds, task steps, system observes feedback, trace records state.
- Require stable `Query.instance_id` and `Query.instance_index` for benchmark outcomes.
- Keep `TaskResult.instance_outcomes` synchronized with streamed step outcomes.
- Let provider refusals and task contract errors keep their cause chains; only use fallback actions in the intended LLM-failure path.
