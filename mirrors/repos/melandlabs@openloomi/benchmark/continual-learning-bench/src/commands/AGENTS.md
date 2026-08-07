# AGENTS.md

CLI subcommands live here.

- Keep argument parsing, config normalization, scaffolding, setup, validation, and friendly error reporting at this boundary.
- Preserve argparse contracts, exit behavior, and user-facing error text unless a behavior change is approved.
- Keep templates aligned with `src/interface.py` and `src/registry.py`.
- Do not move benchmark execution logic into commands; delegate to `runtime/`, `runs/`, tasks, and systems.
