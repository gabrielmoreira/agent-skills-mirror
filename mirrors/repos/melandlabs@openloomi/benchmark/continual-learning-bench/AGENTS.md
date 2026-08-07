# AGENTS.md

## Repo
Continual Learning Bench is a Python 3.13 benchmark framework for evaluating systems that adapt from feedback across ordered task instances. The `clbench` CLI is the primary entrypoint.

## Map
- `src/interface.py`: task/system contracts, query/response/result dataclasses, and standard evaluation helpers.
- `src/cli.py` and `src/commands/`: CLI parsing, scaffolding, validation, setup, and user-facing errors.
- `src/runtime/` and `src/runs/`: interaction loops, baselines, repeated runs, aggregation, and trace plumbing.
- `src/tasks/`: benchmark task packages discovered from `src/tasks/<name>/task.py`.
- `src/systems/`: evaluated system packages discovered from `src/systems/<name>`.
- `src/vendors/`: vendored third-party code kept behind adapters.
- `agent_docs/`: longer agent-facing notes; keep this file high-level.

## Contracts
- Preserve public CLI flags, schemas, trace/artifact formats, task interfaces, and system interfaces unless explicitly approved.
- Let CLI/config boundaries parse and normalize input; keep core task, runtime, and scoring logic typed and strict.
- Tasks must be deterministic from `self.seed`, set stable `Query.instance_id` and `Query.instance_index`, and report `InstanceOutcome` values.
- Systems must isolate state across runs unless marked `parallel_safe = False`, and must record usage events for billable calls.
- Do not store secrets, benchmark answers, raw datasets, large results, or copied traces in agent docs.

## Workflow
- Start with `git status --short` and inspect the relevant local `AGENTS.md` or `README.md` guidance before editing.
- Identify public surfaces before touching code: CLI flags, task/system names, schemas, trace fields, artifacts, schedules, variants, and defaults.
- Keep changes focused; avoid unrelated refactors, generated artifacts, cache files, and benchmark data churn.
- Prefer red-green-refactor for behavior changes: add or update focused tests first, implement the smallest fix, then clean up.
- Verify with the narrowest useful command first, then run formatter and linter before handing off.
- Document longer agent notes in `agent_docs/`; keep this file concise and stable.

## Commands
- Setup: `uv sync --all-extras`
- Test: `uv run pytest`
- Lint: `uv run ruff check .`
- Format: `uv run ruff format .`
