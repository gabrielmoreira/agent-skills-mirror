---
name: unit-test-generation
description: Generate or plan focused unit tests for functions, modules, components, and services. Use when Codex is asked to add unit tests, improve unit coverage, define test cases, create fixtures, or guard logic changes with small deterministic tests.
license: MIT
---

# Unit Test Generation

## Core Workflow

1. Identify the unit under test, behavior changed, dependencies, inputs,
   outputs, and edge cases.
2. Read existing tests and local test patterns before proposing new tests.
3. Define test cases for normal behavior, boundaries, invalid inputs, errors,
   and regressions.
4. Prefer deterministic tests with minimal mocking and clear assertions.
5. Include fixture needs, setup/teardown, and test command.
6. State what remains untested and whether integration or E2E coverage is
   needed.

## Safety Rules

- Do not claim tests pass without command output.
- Do not add brittle tests that assert implementation details unless that is
  the contract.
- Do not use production data, real credentials, or live external services.

## Deliverable Shape

For unit test work, provide:

- Unit and behavior under test
- Test case list
- Fixtures and mocks
- Edge and regression cases
- Test file or command
- Coverage gaps
- Validation notes

## References

- Read `references/unit-test-generation-checklist.md` when planning or adding
  unit tests.
