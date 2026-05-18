---
description: "Safe-start pass 3: architecture decisions derived from data flow"
argument-hint: "[stack preference / constraints]"
---
Use `/skill:safe-start` Pass 3 — Architecture Decisions.

Stack preference or constraints: $ARGUMENTS

Read first when present:
- `docs/agent/PROJECT_INTENT.md`
- `docs/agent/DATA_FLOW.md`
- `docs/agent/DATA_MODEL.md`
- `docs/agent/INVARIANTS.md`

Derive module boundaries from data flow and side-effect boundaries. Choose framework/libraries after boundaries are clear.

Produce/update:
- `docs/agent/ARCHITECTURE.md`
- `docs/agent/DEPENDENCY_RULES.md`
- `docs/agent/RISK_REGISTER.md`
- `docs/agent/adr/0001-initial-architecture.md`

Required output:
- Architecture overview
- Module boundaries and ownership
- Dependency direction
- Side-effect boundaries
- Stack/framework/library decisions and alternatives considered
- Configuration/secrets approach
- Error handling strategy
- Security/privacy basics
- Key risks and mitigations
- ADR: context, decision, alternatives, consequences
- Approval gate: confirm whether to proceed to contract docs or scaffold plan
