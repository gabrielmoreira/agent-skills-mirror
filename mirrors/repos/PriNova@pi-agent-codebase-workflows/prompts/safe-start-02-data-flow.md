---
description: "Safe-start pass 2: data-first input/transformation/output design"
argument-hint: "[focus or project notes]"
---
Use `/skill:safe-start` Pass 2 — Data Flow Design.

Focus or notes: $ARGUMENTS

Read `docs/agent/PROJECT_INTENT.md` if present. Do not choose modules before data shape is clear.

Produce/update:
- `docs/agent/DATA_FLOW.md`
- `docs/agent/DATA_MODEL.md`
- `docs/agent/INVARIANTS.md`

Required output:
- External inputs
- User inputs
- Files/events/API payloads
- Core entities/value objects
- Identifiers and relationships
- Lifecycle/state transitions
- Validation and normalization
- Transformation pipeline: input -> validation -> normalization -> domain operation -> output
- Outputs: UI states, API responses, reports, side effects
- Error states
- Invariants and forbidden states
- Persistence/serialization draft if needed
- Open questions and risks
- Approval gate: confirm whether to proceed to architecture decisions
