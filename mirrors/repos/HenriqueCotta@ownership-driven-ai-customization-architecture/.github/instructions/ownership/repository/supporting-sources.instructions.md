---
applyTo: "**"
---

# Supporting Sources

Use these sources only when the active owner needs deeper evidence about ODA or this repository's Copilot customization.

## Conflict Handling

The docs own the ODA model for this branch.

The `oda-copilot-customization` skill owns the workflow for maintaining that model in a repository.

When consulting these sources, treat disagreement between the live `.github/` customization and the docs as drift to reconcile unless the task explicitly asks to change the architecture.

## oda-docs

Where: `docs/en/`, `docs/pt-BR/`

Use for: the current ODA model and its teaching material in this branch.

## oda-copilot-customization-skill

Where: `.github/skills/oda-copilot-customization/SKILL.md`

Use for: repeatable review or maintenance of this repository's Copilot customization.

## oda-board

Where: GitHub Project `ODA Board`, owner `HenriqueCotta`, project number `4`, `https://github.com/users/HenriqueCotta/projects/4`.

Access: GitHub project tooling when available.

Use for: planned work, accepted follow-ups, explicit carry-forward, and board-backed task status.

Do not use for: current repository behavior unless the board item links to merged code, tests, or accepted docs.

If unavailable: do not invent board state. Use repository evidence that is available, and surface board verification as blocked when planning state could change the result.

Details: use `ownership/repository/oda-board.instructions.md` when board interpretation could change the decision. Use skill `oda-task-tracking` for operational issue or board changes.
