# AGENTS.md

Evaluated system implementations live here.

- Register packages with `@register_system("<name>")` and implement `ContinualLearningSystem.respond`, `reset`, and `name`.
- Set `supports_baseline` and `parallel_safe` deliberately.
- Use `systems/utils/` for provider calls, structured output, token budgets, and refusal handling.
- Isolate filesystem, Docker, memory, and provider state per run unless the system is explicitly not parallel-safe.
- Record usage events for billable calls and expose run artifacts through `get_run_artifacts` or registered exporters.
