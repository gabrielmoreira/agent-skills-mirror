---
name: backend-test-plan
description: Create backend test plans for APIs, services, databases, auth, integrations, and background jobs. Use when Codex is asked to define unit, integration, contract, migration, security, performance, or regression tests for backend changes.
license: MIT
---

# Backend Test Plan

## Core Workflow

1. Identify changed behavior, risk areas, data stores, external integrations,
   auth boundaries, and production impact.
2. Define coverage across unit, integration, contract, database/migration,
   authorization, error, performance, and regression tests.
3. Specify fixtures, test data, mocks/fakes, environments, and cleanup needs.
4. Tie each test to an acceptance criterion or failure mode.
5. Include non-happy paths: denied access, invalid input, dependency failure,
   concurrency, retries, and rollback.
6. Recommend what must pass before merge, release, or rollback.

## Safety Rules

- Do not claim tests passed unless output is available.
- Do not use real production data or credentials in test plans.
- Escalate testing gaps for auth, payments, migrations, customer data,
  background jobs, and public APIs.

## Deliverable Shape

For backend test plans, provide:

- Change and risk summary
- Test matrix
- Fixtures and environments
- Contract and integration coverage
- Data/migration coverage
- Auth and security coverage
- Performance or load checks when relevant
- Merge/release gates

## References

- Read `references/backend-test-plan-checklist.md` when creating or reviewing
  backend test coverage.
