---
name: integration-test-plan
description: Plan integration tests across modules, APIs, databases, queues, services, and external dependencies. Use when Codex is asked to test interactions, persistence, contracts, adapters, or dependency boundaries beyond unit tests.
license: MIT
---

# Integration Test Plan

## Core Workflow

1. Identify interacting components, data stores, external services, queues,
   auth, and contracts under test.
2. Define test environment, fixtures, dependency fakes, seeded data, and cleanup
   strategy.
3. Cover success, failure, retry, permission, persistence, and contract-change
   cases.
4. Decide which dependencies should be real, fake, mocked, or containerized.
5. Include test commands, CI fit, and data isolation needs.
6. Record gaps that need E2E, load, or manual verification.

## Safety Rules

- Do not use production systems, production data, or real customer credentials.
- Do not run destructive integration tests without isolated test resources.
- Do not hide flaky dependency risks.

## Deliverable Shape

For integration test plans, provide:

- Components and boundaries
- Environment and fixtures
- Dependency strategy
- Test matrix
- Data setup and cleanup
- CI and command notes
- Gaps and follow-up tests

## References

- Read `references/integration-test-plan-checklist.md` when designing
  integration test coverage.
