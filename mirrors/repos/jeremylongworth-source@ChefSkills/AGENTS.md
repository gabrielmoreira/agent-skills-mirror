# ChefSkills Agent Instructions

This repository defines portable culinary Agent Skills.

When working here:

- Treat `skills/` as the source of behavior.
- Keep each skill focused and auditable.
- Prefer routing, state, tests, and references over broad recipe dumps.
- Preserve food safety as a hard gate.
- Use `router/` for task selection rules and `state/` for culinary state concepts.
- Add or update `tests/scenarios/` and `tests/expected-routing.yaml` when routing behavior changes.
- Run `.\scripts\validate-all.ps1` before finishing repository changes.

Do not add secrets, private data, or unsafe food-handling instructions.
