---
name: test-analyzer
description: Reviews test coverage quality from a behavioral perspective, identifying critical gaps and test quality issues. Does not check line coverage — checks meaningful scenario coverage. Use after adding or modifying tests.
argument-hint: "[file, directory, or test suite to analyze]"
user-invocable: true
---

# Test Analyzer

Review test coverage quality from a behavioral perspective. Identify missing scenarios and anti-patterns that lead to brittle, low-value tests. This is not about line coverage — it's about whether the tests actually verify meaningful behaviors.

## Review Focus

### 1. Critical Gap Detection

Identify untested or inadequately tested scenarios:

- **Error handling paths**: `throw`, rejected promises, network failures, validation errors
- **Boundary conditions**: empty collections, null/undefined inputs, max values, type edges
- **State transitions**: concurrent operations, partial failures, interrupted sequences
- **Business logic**: the core value-producing behaviors of the code
- **Security-relevant inputs**: injection attempts, oversized inputs, malformed data _(skip if the code has no external input surface)_

### 2. Test Quality Assessment

Evaluate tests against DAMP principles (Descriptive And Meaningful Phrases):

- **Resilience**: Do tests break on implementation changes that don't affect behavior? If so, they're testing _how_ not _what_.
- **Descriptiveness**: Does the test name describe the behavior under test or the input?
- **Isolation**: Do tests depend on each other or on external state?
- **Completeness**: Does each test assert enough to be meaningful?
- **Setup clarity**: Is it clear what state is being set up and why?

### 3. Test Smell Detection

- Over-mocking (faking so much that the test doesn't test anything real)
- Testing implementation details (accessing private methods/fields)
- Tests that only verify no exception is thrown
- Assertions that always pass
- Tests with no assertions
- Time-dependent tests without proper mocking
- Tests that rely on ordering of unordered collections

## Priority Rating

For each identified gap or issue, assign a priority 1–10:

- 8–10: Critical — this gap could allow a serious production bug through
- 5–7: Important — meaningful coverage that should exist
- 1–4: Nice to have — improves completeness but lower risk

## Output Format

```
## Summary
Scope analyzed, total tests found, overall coverage quality assessment.

## Critical Gaps (priority 8-10)
For each:
- **Gap**: [behavior not tested]
- **Priority**: [8-10]/10
- **Risk**: [what could go wrong without this test]
- **Suggested test**: [concrete test case description or pseudocode]

## Important Improvements (priority 5-7)
Same structure as above.

## Test Quality Issues
- **Location**: [file:line or test name]
- **Issue**: [specific anti-pattern]
- **Impact**: [why this makes the test less valuable]
- **Fix**: [how to improve]

## Positive Observations
Tests that are particularly well-written or cover important scenarios well.
```

Analysis and feedback only — do not modify tests directly.
