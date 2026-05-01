# Test Planning Reference

Consolidated reference for coverage-driven prioritization and structured test plan creation. Used during Stage 3 (Plan).

---

## Coverage-Driven Prioritization

Test planning starts with **measured coverage gaps**, not guesswork. Parse coverage data from Stage 2 and classify each gap:

### P0 -- Critical (MUST test)
- **Core business logic methods**: main algorithm, calculation, decision logic
- **Exception handlers** (`catch` blocks): error recovery is critical
- **Error return paths**: methods that throw or return error objects
- **Retry logic**: retry counters, exponential backoff, circuit breakers
- **Validation logic**: input validation, authorization checks, permission guards


### P1-- High (SHOULD test)
- **Security-sensitive code**: authentication, sanitization, encryption
- **State transitions**: methods that change state based on conditions
- **Data transformation**: methods that convert, map, or filter data
- **Integration points**: surrounding logic for external service calls (mock the service)

### P2 -- Medium (GOOD to test)
- **Utility/helper methods with branching logic** (not simple one-liners)
- **Configuration parsing**: reading and interpreting config values
- **Caching logic**: cache hit/miss, eviction, invalidation

### P3 -- Low (NICE to test)
- **Branch coverage gaps** in already-covered methods (uncovered `else` clause)
- **Edge cases** in tested methods (untested null/empty/boundary inputs)

### Mapping Gaps to Test Cases

For each gap, create a test case with a concrete mapping:

```
Coverage Gap: src/OrderService.cs lines 45-52 (catch block for PaymentException)
Priority: P0
Test: ProcessOrder_WhenPaymentFails_ReturnsErrorResult
  Arrange: Mock payment service to throw PaymentException
  Act: Call ProcessOrder with valid order
  Assert: Result.IsSuccess == false, Result.Error contains payment message
```

### Anti-Patterns
- AVOID: targeting already-covered code (redundant)
- AVOID: counting DTO property access as "coverage" (theater)
- AVOID: prioritizing simple code over complex code
- AVOID: targeting already-fully-covered files where no gap remains
- AVOID: planning tests that duplicate scenarios already validated by existing tests (even if coverage lines differ due to mocking). Read existing tests for the same class before planning.
- DO: prioritize exception handlers first
- DO: prioritize code with high cyclomatic complexity
- DO: verify coverage actually increased after generation

---

## Test Plan Format

### Use-Case Awareness

| Use Case | Focus |
|----------|-------|
| Bug Fix | Regression tests reproducing the bug + boundary tests. Regression test MUST fail on pre-fix code. |
| New Feature | Contract/API tests, unit tests, negative tests. Derive from spec, not just code. |
| Refactoring | Behavioral equivalence -- identical outputs for identical inputs. |
| New Service | Full scaffold -- unit, integration, contract, E2E, smoke tests. |

### Required Categories

Every plan must cover:
- **Happy Path**: normal/expected usage, valid inputs, expected outputs
- **Error Path**: exceptions, invalid inputs, service failures, timeouts
- **Edge Cases**: null, empty, single element, max values, unicode, special chars
- **Boundary Conditions**: off-by-one, max int, empty collection, exactly-at-limit

### Rules

- Each test case: **ID** (`TP-<SourceFile>-<ShortName>`), **Name**, **Category**, **Priority (P0-P3)**, **Coverage Target** (file:lines), **Description**, **Arrange**, **Act**, **Assert**
  - `<SourceFile>` = short source file name, no extension, no path (e.g., `OrderService`)
  - `<ShortName>` = ≤5-word camel-case scenario (e.g., `PaymentFailurePath`, `NullInputReturnsError`)
  - Example: `TP-OrderService-PaymentFailurePath`
- Test names: `MethodName_Scenario_ExpectedBehavior`
- Match the repository's existing test framework and mocking library; do not override it.
- For C# only: if the repo uses MSTest+Moq, keep that stack and follow existing version/API patterns.
- Error paths and edge cases are REQUIRED, not optional
- Flag potential latent bugs with **WARNING**
- Think from specification/intent first, then code. Avoid tautological designs.
- Do NOT generate test code in this stage -- only the plan
- In subsequent iterations, rebuild the plan from the refreshed Stage 2 remaining-target inventory, not from the previous iteration's language choice.
- If the previously targeted language/module is stalled but another language/module still has actionable targets, the next plan MUST shift to those remaining actionable targets.

### Plan Output Template

```markdown
### Test Plan: <ComponentName>

#### Summary
<1-2 sentence summary and key risks>

#### Happy Path
| ID (TP-File-Scenario) | Test Name | Priority | Coverage Target | Description | Arrange | Act | Assert |
|-----------------------|-----------|----------|-----------------|-------------|---------|-----|--------|

#### Error Path
| ID (TP-File-Scenario) | Test Name | Priority | Coverage Target | Description | Arrange | Act | Assert |
|-----------------------|-----------|----------|-----------------|-------------|---------|-----|--------|

#### Edge Cases
| ID (TP-File-Scenario) | Test Name | Priority | Coverage Target | Description | Arrange | Act | Assert |
|-----------------------|-----------|----------|-----------------|-------------|---------|-----|--------|

#### Boundary Conditions
| ID (TP-File-Scenario) | Test Name | Priority | Coverage Target | Description | Arrange | Act | Assert |
|-----------------------|-----------|----------|-----------------|-------------|---------|-----|--------|

#### Coverage Summary
- Happy Path: N tests | Error Path: N tests | Edge Cases: N tests | Boundary: N tests | Total: N
```
