---
name: tdd-workflow
description: ''
---

# Skill: Test-Driven Development (TDD) Workflow

This skill ensures software development follows a test-first pattern, ensuring modularity, reliability, and regression proofing.

## Steps
1. **Define Interface & Contracts:** Specify standard parameter types, output structures, and Zod boundaries before writing any execution logic.
2. **Write a Failing Test:** Draft unit/component tests in the testing suite under `__tests__` using Vitest or RTL. Run the tests via `pnpm test` to verify they fail for the correct reason.
3. **Write Minimal Code:** Implement the simplest possible structural execution to make the test pass. Avoid adding extra logic not specified in the test.
4. **Pass & Refactor:** Confirm that the test suite passes. Immediately refactor the code (abstractions, function sizes, type clarity) in accordance with the `clean-code.md` rules. Verify tests still pass after refactoring.
