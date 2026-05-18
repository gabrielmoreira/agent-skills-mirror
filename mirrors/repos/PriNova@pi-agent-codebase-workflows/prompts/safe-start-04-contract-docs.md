---
description: "Safe-start pass 4: create project contract docs for humans and future agents"
argument-hint: "[docs focus]"
---
Use `/skill:safe-start` Pass 4 — Project Contract Docs.

Docs focus: $ARGUMENTS

Read first when present:
- `docs/agent/PROJECT_INTENT.md`
- `docs/agent/DATA_FLOW.md`
- `docs/agent/DATA_MODEL.md`
- `docs/agent/INVARIANTS.md`
- `docs/agent/ARCHITECTURE.md`
- `docs/agent/DEPENDENCY_RULES.md`
- `docs/agent/RISK_REGISTER.md`

Create compact operational docs. Freshman mode may include short teaching notes and command explanations. Expert mode should be terse and contract-oriented.

Produce/update:
- `README.md`
- `AGENTS.md`
- `docs/agent/CHANGE_GUIDE.md`
- `docs/agent/TESTING_STRATEGY.md`
- optional `docs/agent/CONTRACTS.md`, `docs/agent/SECURITY.md`, `docs/agent/DEPLOYMENT.md`

Required output:
- Project overview
- Architecture rules
- Data model rules
- Invariants not to violate
- How to add/modify features
- How to validate changes
- Documentation update rules
- Forbidden shortcuts
- Approval gate: confirm whether to proceed to scaffold planning
