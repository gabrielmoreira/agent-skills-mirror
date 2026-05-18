---
description: "Safe-start pass 7: implement first thin vertical slice"
argument-hint: "[slice goal]"
---
Use `/skill:safe-start` Pass 7 — Thin Vertical Slice.

Slice goal: $ARGUMENTS

Read first when present:
- `docs/agent/PROJECT_INTENT.md`
- `docs/agent/DATA_FLOW.md`
- `docs/agent/DATA_MODEL.md`
- `docs/agent/INVARIANTS.md`
- `docs/agent/ARCHITECTURE.md`
- `docs/agent/DEPENDENCY_RULES.md`
- `docs/agent/VALIDATION_BASELINE.md`

Implement one small end-to-end feature only. Include:
- Input adapter: UI/API/CLI/event/file as relevant
- Validation/schema if relevant
- Domain/core operation
- Output adapter/rendering/API response
- Persistence adapter or explicit in-memory/mock choice if persistence is deferred
- Tests around core invariant and runtime path
- Docs update only if durable semantics change

Before editing, state slice boundary, touched files, invariants at risk, and validation plan. Stop for approval unless user explicitly requested implementation now.

After editing, run focused validation and update validation/risk docs if needed.
