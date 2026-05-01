---
name: service-boundary-design
description: Design backend service boundaries and module responsibilities. Use when Codex is asked to split services, define module boundaries, choose ownership, separate domains, design integration points, or avoid coupling in backend systems.
license: MIT
---

# Service Boundary Design

## Core Workflow

1. Identify domains, actors, data ownership, latency needs, deployment model,
   team ownership, and failure tolerance.
2. Define service or module responsibilities, owned data, public interfaces, and
   forbidden dependencies.
3. Map synchronous calls, async events, shared storage, and integration points.
4. Evaluate coupling, transaction boundaries, consistency needs, and migration
   path.
5. Prefer simpler module boundaries before distributed services unless scale,
   ownership, isolation, or reliability needs justify separation.
6. Document tradeoffs, risks, and review triggers.

## Safety Rules

- Do not split services only for abstraction if the current repo can support a
  simpler module boundary.
- Do not invent reliability, latency, scale, or team-ownership requirements.
- Escalate boundaries involving customer data isolation, payments, auth,
  compliance, or production reliability.

## Deliverable Shape

For service boundary memos, provide:

- Domains and responsibilities
- Data ownership
- Interface boundaries
- Dependency map
- Consistency and transaction model
- Migration path
- Tradeoffs and risks
- Recommendation and review triggers

## References

- Read `references/service-boundary-design-checklist.md` when defining backend
  service or module boundaries.
