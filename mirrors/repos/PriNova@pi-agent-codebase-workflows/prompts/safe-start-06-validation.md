---
description: "Safe-start pass 6: establish green validation baseline for new project"
argument-hint: "[validation focus]"
---
Use `/skill:safe-start` Pass 6 — Validation Baseline.

Validation focus: $ARGUMENTS

Run the most relevant checks for the scaffolded project. Prefer project-local commands and wrappers.

Validate when applicable:
- install/bootstrap works
- format/lint command works
- typecheck/build works
- tests run
- app starts
- one smoke test proves runtime path

Produce/update `docs/agent/VALIDATION_BASELINE.md` with:
- Commands run
- Results
- Known warnings
- Blockers and exact errors if any
- Next best check when a command cannot run
- Baseline status: green / partial / blocked

Do not proceed to feature depth until baseline is green or blockers are explicitly accepted by user.
