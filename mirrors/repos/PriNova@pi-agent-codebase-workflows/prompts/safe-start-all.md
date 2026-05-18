---
description: "Safe-start all-in-one greenfield workflow for small/simple projects"
argument-hint: "[project idea / constraints]"
---
Use `/skill:safe-start` all-in-one mode.

Project idea or constraints: $ARGUMENTS

Only use all-in-one mode if the project appears small/simple enough. Otherwise recommend starting with `/safe-start-01-intent`.

Workflow:
1. Determine guidance level: Freshman, Standard, or Expert. Default Standard if unclear.
2. Capture intent and assumptions.
3. Produce data-first design: inputs -> transformations -> outputs, data model, invariants.
4. Propose architecture decisions derived from data flow.
5. Propose contract docs and scaffold plan.
6. Stop for approval before writing files unless user explicitly requested implementation now.
7. If approved/requested, scaffold minimal baseline, run validation, implement one thin vertical slice, and hand off to `safe-change`.

Required final output:
- Files created/changed
- Validation run and result
- Handoff status: ready / partial / blocked
- Next safe-change-sized work items
