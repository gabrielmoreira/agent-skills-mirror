---
description: "Safe-start pass 8: hand off new project to safe-change workflow"
argument-hint: "[handoff focus]"
---
Use `/skill:safe-start` Pass 8 — Handoff to Safe Change.

Handoff focus: $ARGUMENTS

Verify project is ready for documented-codebase work.

Check:
- Root `AGENTS.md` exists and is operational
- `docs/agent/` artifacts cover architecture, data model, invariants, dependency rules, tests, risks, and change guide
- Validation baseline commands are known and recently run
- First vertical slice is implemented or explicitly deferred
- Next work items are small enough for `safe-change`

Produce/update:
- `docs/agent/CHANGE_GUIDE.md`
- `docs/agent/RISK_REGISTER.md`
- optional `docs/agent/BACKLOG.md`

Final output:
- Handoff status: ready / partial / blocked
- Validation summary
- Remaining risks
- Next recommended work items
- Explicit instruction: future feature/bug/refactor work should use `/skill:safe-change`
