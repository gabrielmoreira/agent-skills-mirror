# Testing Orchestration Patterns

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   Confidence through verification.                          │
│   Generate, execute, analyze — all in parallel.             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

> **Load when**: Test generation, test execution, coverage analysis, test maintenance, E2E testing
> **Common patterns**: Coverage-Driven Generation, Parallel Test Suites, Broken Test Triage

## Table of Contents

1. [Test Generation](#test-generation)
2. [Test Execution](#test-execution)
3. [Coverage Analysis](#coverage-analysis)
4. [Test Maintenance](#test-maintenance)
5. [E2E Testing](#e2e-testing)

---

## Test Generation

### Pattern: Coverage-Driven Generation

```
User Request: "Add tests for the UserService"

Phase 1: EXPLORE
└─ Explore agent: Understand UserService methods, dependencies

Phase 2: FAN-OUT (Parallel test writing)
├─ Agent A: Unit tests for method group 1
├─ Agent B: Unit tests for method group 2
├─ Agent C: Integration tests for external dependencies
└─ Agent D: Edge cases and error scenarios

Phase 3: PIPELINE
└─ General-purpose agent: Verify tests pass, check coverage
```

### Pattern: Behavior-First

```
User Request: "Test the checkout flow"

Phase 1: EXPLORE
└─ Explore agent: Map checkout flow steps and branches

Phase 2: PIPELINE (Generate by behavior)
├─ General-purpose agent: Happy path tests
├─ General-purpose agent: Error path tests
└─ General-purpose agent: Edge case tests

Phase 3: BACKGROUND
└─ Background agent: Run tests, report results
```

---

## Test Execution

### Pattern: Parallel Test Suites

```
User Request: "Run all tests"

Phase 1: FAN-OUT (Parallel suites)
├─ Background agent: Unit tests
├─ Background agent: Integration tests
├─ Background agent: E2E tests
└─ Background agent: Performance tests

Phase 2: REDUCE
└─ General-purpose agent: Aggregate results, identify failures
```

### Pattern: Targeted Execution

```
User Request: "Test the changes I made"

Phase 1: EXPLORE
└─ Explore agent: Identify changed files and affected tests

Phase 2: FAN-OUT
├─ Background agent: Run directly affected tests
└─ Background agent: Run dependent module tests

Phase 3: PIPELINE
└─ General-purpose agent: Report results, suggest additional tests
```

---

## Coverage Analysis

### Pattern: Gap Identification

```
User Request: "Improve test coverage"

Phase 1: BACKGROUND
└─ Background agent: Run coverage report

Phase 2: EXPLORE
└─ Explore agent: Identify critical uncovered paths

Phase 3: FAN-OUT (Prioritized gap filling)
├─ Agent A: Tests for critical uncovered module 1
├─ Agent B: Tests for critical uncovered module 2
└─ Agent C: Tests for error handlers

Phase 4: PIPELINE
└─ General-purpose agent: Re-run coverage, verify improvement
```

---

## Test Maintenance

### Pattern: Broken Test Triage

```
User Request: "Fix failing tests"

Phase 1: BACKGROUND
└─ Background agent: Run tests, capture failures

Phase 2: FAN-OUT (Parallel diagnosis)
├─ Agent A: Diagnose failure group 1
├─ Agent B: Diagnose failure group 2
└─ Agent C: Diagnose failure group 3

Phase 3: FAN-OUT (Parallel fixes)
├─ Agent A: Fix test group 1
├─ Agent B: Fix test group 2
└─ Agent C: Fix test group 3

Phase 4: PIPELINE
└─ Background agent: Verify all tests pass
```

### Pattern: Test Refactoring

```
User Request: "Clean up test duplication"

Phase 1: EXPLORE
└─ Explore agent: Find duplicate test patterns

Phase 2: PLAN
└─ Plan agent: Design shared fixtures, helpers, patterns

Phase 3: FAN-OUT
├─ Agent A: Extract shared fixtures
├─ Agent B: Refactor test file group 1
└─ Agent C: Refactor test file group 2

Phase 4: PIPELINE
└─ Background agent: Verify tests still pass
```

---

## E2E Testing

### Pattern: User Journey Testing

```
User Request: "Add E2E tests for user registration"

Phase 1: EXPLORE
└─ Explore agent: Map registration flow, identify test scenarios

Phase 2: PIPELINE (Sequential scenarios)
├─ General-purpose agent: Happy path registration
├─ General-purpose agent: Validation error scenarios
├─ General-purpose agent: Duplicate email handling
└─ General-purpose agent: Email verification flow

Phase 3: BACKGROUND
└─ Background agent: Run E2E suite, capture screenshots
```

---

## Task Management for Testing

Structure testing work as tasks with clear dependencies:

```bash
# Create testing tasks
npx cc-mirror tasks create --subject "Identify testing scope" --description "Analyze what needs testing..."
npx cc-mirror tasks create --subject "Generate unit tests" --description "Tests for module A..."
npx cc-mirror tasks create --subject "Generate integration tests" --description "Tests for API endpoints..."
npx cc-mirror tasks create --subject "Run test suite" --description "Execute all tests, capture results..."
npx cc-mirror tasks create --subject "Fix failures" --description "Address any failing tests..."
npx cc-mirror tasks create --subject "Verify all pass" --description "Final test run to confirm..."

# Dependencies
npx cc-mirror tasks update 2 --add-blocked-by 1
npx cc-mirror tasks update 3 --add-blocked-by 1
npx cc-mirror tasks update 4 --add-blocked-by 2,3
npx cc-mirror tasks update 5 --add-blocked-by 4
npx cc-mirror tasks update 6 --add-blocked-by 5
```

```python
# Parallel test generation (sonnet for well-structured work)
Task(subagent_type="general-purpose", prompt="Task 2: Generate unit tests...",
     model="sonnet", run_in_background=True)
Task(subagent_type="general-purpose", prompt="Task 3: Generate integration tests...",
     model="sonnet", run_in_background=True)
```

## Test Execution Best Practices

1. **Always run in background** for long test suites
2. **Parallelize independent suites** (unit, integration, e2e)
3. **Fail fast** - stop on first failure for quick feedback
4. **Capture artifacts** - screenshots, logs, coverage reports
5. **Report actionable results** - file:line for failures

---

```
─── ◈ Testing ───────────────────────────
```
