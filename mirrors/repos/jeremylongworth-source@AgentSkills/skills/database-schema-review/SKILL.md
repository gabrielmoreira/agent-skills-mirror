---
name: database-schema-review
description: Review database schemas for backend applications and APIs. Use when Codex is asked to critique tables, migrations, indexes, constraints, relationships, tenant boundaries, data integrity, query fit, or schema evolution risk.
license: MIT
---

# Database Schema Review

## Core Workflow

1. Identify the domain model, queries, write patterns, data lifecycle, and
   database engine assumptions.
2. Review tables, columns, types, relationships, constraints, indexes,
   uniqueness, nullability, and migration path.
3. Check data integrity, tenant/user boundaries, privacy, auditability, and
   deletion or retention needs.
4. Compare schema design against API and product access patterns.
5. Flag migration, backfill, locking, rollback, and performance risks.
6. Recommend concrete schema changes and validation checks.

## Safety Rules

- Do not recommend destructive migrations without backup, rollback, and
  reviewer approval.
- Do not invent production data volume, query patterns, or compliance
  requirements.
- Escalate schemas involving payments, auth, personal data, regulated data, or
  multi-tenant isolation.

## Deliverable Shape

For schema reviews, provide:

- Schema scope and assumptions
- Entity and relationship review
- Constraints and index review
- Query and access-pattern fit
- Migration and rollback risks
- Data privacy and retention notes
- Recommended changes
- Validation checks

## References

- Read `references/database-schema-review-checklist.md` when reviewing schema
  design or migrations.
