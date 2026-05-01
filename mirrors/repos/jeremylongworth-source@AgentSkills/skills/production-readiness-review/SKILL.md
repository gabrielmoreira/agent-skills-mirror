---
name: production-readiness-review
description: Review whether an app, service, feature, or workflow is ready for production. Use when Codex is asked for launch readiness, operational readiness, release gates, observability, support, security, rollback, or go/no-go assessment.
license: MIT
---

# Production Readiness Review

## Core Workflow

1. Identify release scope, users affected, business criticality, dependencies,
   and owner.
2. Review readiness across functionality, tests, observability, security,
   performance, reliability, data, support, docs, deployment, and rollback.
3. Classify blockers, warnings, and acceptable risks.
4. Define go/no-go criteria and owner approvals.
5. Include launch, monitoring, incident, and support handoff steps.
6. Recommend ship, ship with conditions, defer, or block.

## Safety Rules

- Do not approve production release without evidence for required gates.
- Do not downplay missing rollback, monitoring, auth, data, or support gaps.
- Escalate high-risk production changes involving customer data, payments,
  auth, migrations, regulated workflows, or broad availability.

## Deliverable Shape

For production readiness reviews, provide:

- Scope and owner
- Readiness checklist
- Blockers and warnings
- Evidence reviewed
- Go/no-go criteria
- Rollback and incident plan
- Support handoff
- Recommendation

## References

- Read `references/production-readiness-review-checklist.md` when reviewing
  production readiness.
