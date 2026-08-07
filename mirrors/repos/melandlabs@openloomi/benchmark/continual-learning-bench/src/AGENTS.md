# AGENTS.md

## Scope
This is the source package for `clbench`.

## Map
- `interface.py`: public task/system contracts and shared result models.
- `registry.py`: lazy discovery and registration for tasks and systems.
- `cli.py` and `commands/`: CLI boundary, config loading, scaffolding, setup, and validation.
- `runtime/`: one task-system interaction loop.
- `runs/`: baseline, repeated-run, and aggregate benchmark orchestration.
- `tasks/`: task framework support plus task packages.
- `systems/`: evaluated systems and provider utilities.
- `vendors/`: pinned third-party snapshots used through adapters.

## Guidance
- Treat dataclasses, Pydantic schemas, CLI flags, trace fields, artifact shapes, and registry names as public surfaces.
- Keep coercion and user-facing parsing at boundaries; keep runtime, scoring, and task logic strict.
- Prefer extending existing contracts over adding new abstractions.
- Update focused tests for behavior that changes runs, traces, scoring, task schedules, provider calls, or CLI output.
