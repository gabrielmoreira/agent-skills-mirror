# Test Quality Reference

Consolidated reference for test auditing, review, anti-patterns, and quality gates. Used during Stage 4 (Review) and Stage 5 (Finalize).

---

## Part 1: What to Look For in Existing Tests (Audit)

When scanning existing tests before generating new ones, flag these problems:

| Category | Severity | Description |
|----------|----------|-------------|
| Coverage-Only Tests | CRITICAL | Executes code paths to increase coverage but does not validate behavior with meaningful assertions |
| Tautological Tests | CRITICAL | Re-computes expected values from the same logic as production code |
| Always-Passing Tests | CRITICAL | Assertions that can never fail: `Assert.True(true)`, asserting on hand-set values |
| Incorrect Assertions | CRITICAL | Wrong expected values, checking the wrong field, inverted conditions |
| Flaky Tests | WARNING | Non-deterministic: time-dependent, order-dependent, network calls |
| Obsolete Tests | WARNING | Referencing methods/classes that no longer exist |
| Missing Cleanup | WARNING | Resource leaks, shared mutable state between tests |
| Low-Value Tests | INFO | Only `Assert.IsNotNull` without behavioral validation |

---

## Part 2: Anti-Patterns in Generated Tests (REJECT on sight)

### Critical (REJECT immediately)
1. **Tautological Assertions** -- asserting the code does what the code does. Example: `Assert.AreEqual(input.Length * 2, result)` when the method does `input.Length * 2`. Fix: use independently-derived expected values.
2. **Assert-Free Tests** -- call a method but assert nothing meaningful. Fix: every test must assert observable behavior.
3. **Coverage-Only Tests** -- tests that only execute lines/branches with no behavioral validation. Common pattern to REJECT: bypassing constructors to trigger null-reference exceptions in catch blocks — this is a smoke test, not a behavioral test. If the only assertion is `Assert.ThrowsAsync<SomeException>()` with no validation of the exception message, state change, or side effect, REJECT.
4. **Copy-Paste Production Logic** -- duplicating production code to compute expected values. Fix: use hardcoded expected values from spec/requirements.
5. **Testing the Mock** -- set up mock to return X, then assert it returns X. Fix: assert on the CLASS UNDER TEST behavior.
6. **DTO/Entity Property Tests** -- test creates an object, sets properties, asserts properties back. This is testing the language runtime, not business logic. Also applies to config objects, data classes, and metadata containers. REJECT and remove.
7. **Behavioral Duplicates** -- test validates the same scenario already covered by an existing test for the same class. Even if line numbers differ, if the behavior under test is identical, the new test adds no value and increases maintenance burden. REJECT.
8. **Pure Delegation Methods** -- method under test just calls `await wrapper.Method()` or `return service.Call()` with no branching. Testing it only proves the mock returns what the mock was configured to return. Skip these in planning.
9. **Null-Reliant Passing** -- test passes because both actual and expected are null (e.g., unset properties), not because logic was exercised. Fix: use non-null inputs that force the code path under test.
10. **Clone/Copy Without Mutation Check** -- tests deep-copy but never mutate the copy to prove independence from the original. Fix: mutate the copy, assert original is unchanged.

### High Severity (NEEDS REVISION)
11. **Over-Mocking** -- mocking the class under test, mocking POCOs, more mock lines than assert lines. Fix: only mock interfaces and external dependencies.
12. **Implementation Coupling via Verify()** -- tests that only call `mock.Verify(x => x.SomeMethod(...), Times.Once)` without asserting the method's return value or state change. Verify() confirms a call happened, not that the behavior is correct. Fix: assert on outputs and side effects first; use Verify() only as a supplementary check.
13. **Name-Behavior Mismatch** -- test name claims a scenario the assertions don't verify (e.g., name says "MapsAllFields" but skips fields, or name says "NullProps" but the real trigger is an ID mismatch). Fix: rename to match what is actually asserted, or fix the assertions to match the name.
14. **Fragile String Coupling** -- assertions matching log-message fragments or source-generated template strings. These break on any message rewording. Fix: assert on structured output (error codes, result types, state changes) instead.
15. **Redundant Double-Assertions** -- e.g., `Verify(Times.Never)` + `Invocations.Count == 0`, or `Assert.IsInstanceOfType<BadRequestObjectResult>` + `Assert.AreEqual(400, statusCode)`. One already implies the other. Fix: keep the stronger assertion, remove the redundant one.
16. **Negative-ROI Setup** -- 10+ mock setups to assert one trivial outcome (e.g., `=> null`). If the setup cost vastly exceeds the behavioral insight gained, skip the method. Fix: drop the test or simplify the scenario.
17. **Magic Number Assertions** -- `Assert.AreEqual(42, result)` with no context. Fix: use named constants or comments.
18. **Excessive Setup** -- 50+ lines for one assertion. Fix: extract builders/helpers.
19. **Multi-Class Test Files** -- multiple unrelated test classes crammed into a single file. Fix: one test class per file, matching the source class name (`OrderService.cs` → `OrderServiceTests.cs`).
20. **Tool-Prefixed File/Class Names** -- file or class names that embed the generation tool or iteration number. Traceability belongs in attributes/comments, not names. Fix: rename to `<SourceClass>Tests.cs` or `<SourceClass>ExtendedTests.cs`.

### Medium Severity (Flag)
13. **Testing Framework Plumbing** -- testing DI resolution, middleware pipeline. Fix: test YOUR logic.
14. **Private Method Testing via Reflection** -- Fix: test through the public API.
15. **Time-Dependent Tests** -- using `DateTime.Now`, `DateTimeOffset.Now`, `DateTimeOffset.UtcNow`. Fix: inject time provider or use fixed values like `new DateTimeOffset(2025, 1, 1, 0, 0, 0, TimeSpan.Zero)`.
16. **Non-Deterministic Tests** -- using `Random`, `Guid.NewGuid()` in test setup or assertions. Fix: use fixed values like `Guid.Parse("00000000-0000-0000-0000-000000000001")` or `new Guid(1,0,0,0,0,0,0,0,0,0,0)`.
17. **Hash/Equality Smoke Tests** -- asserting `GetHashCode() != 0` or `Equals(other) == true` without testing the hash contract (equal objects produce equal hashes, different objects produce different hashes). Fix: test with at least 2 equal and 2 different inputs.
18. **Flakiness-Prone Patterns** -- any of: `Thread.Sleep()`, `Task.Delay()`, `await Task.Delay()`, polling loops with timeouts, race conditions from `Task.WhenAny`, environment-dependent paths, or uncontrolled concurrency. These produce tests that pass locally but fail intermittently in CI. Fix: remove sleeps/delays entirely (unit tests should be synchronous or use controlled async); replace polling with direct state assertions; eliminate concurrency unless the test explicitly validates concurrent behavior.
19. **Unbounded Loop / Async Stream Tests** -- tests targeting methods with unbounded `while` loops or gRPC/async stream consumers (`IAsyncStreamReader`, `ChannelReader`, `IAsyncEnumerable` read loops). These deadlock test runners. REJECT and skip the method in planning.

---

## Part 3: Review Checklist (Per-Test Evaluation)

For EACH generated test, evaluate:

| Check | What to Look For |
|-------|-----------------|
| Plan Alignment | Does the test implement the corresponding plan item? |
| Assertion Presence | At least one meaningful behavioral assertion exists (not just execution/no-throw) |
| Assertion Quality | HIGH: specific expected output, business logic. MEDIUM: structural (not null, count). LOW: no exception only. |
| Coverage-Only | Is the test only increasing coverage without validating outcomes? REJECT. |
| Tautological | Re-implements production logic in assertion? |
| Edge Cases | Null, empty, boundary, overflow tested? |
| Error Paths | Exceptions/error conditions tested? |
| Independence | Shared mutable state or ordering dependency? |
| Naming | Follows `MethodName_Scenario_ExpectedBehavior`? Name matches what is actually asserted? |
| Determinism | Time, randomness, network reliance? |
| Flakiness | Any sleep/delay, polling loop, race condition, or environment dependency? NEEDS REVISION. |
| Mock Correctness | Proper setup, meaningful verification? |
| Framework | Uses correct framework (MSTest+Moq for C#)? |
| File Organization | One test class per file, file named after source class? |
| Behavioral Duplicate | Does an existing test already cover this same scenario? |
| Exclusions | Tests constants, DTOs, constructors, properties, logging? REJECT. |

### Review has TWO mandatory parts

**Part A -- Build Verification**: Build and run all tests. Fix compilation errors first. Do NOT proceed to Part B with broken code.

**Part B -- Quality Review**: Produce per-test verdict table. "All tests pass" is NOT a completed review.

### Verdicts
- **APPROVED** -- no issues
- **NEEDS REVISION** -- fixable; provide exact fix instructions
- **REJECT** -- fundamentally flawed (tautological, always-passing, exclusion violation)

### Review Output

```markdown
### Test Review Report

**Tests Reviewed**: N | **Approved**: N | **Needs Revision**: N | **Rejected**: N

| Test Name | Plan Item | Assertion Quality | Issues | Verdict |
|-----------|-----------|-------------------|--------|---------|
| Method_Scenario_Expected | TP-SourceFile-ShortName | HIGH/MEDIUM/LOW | (list or "None") | APPROVED/NEEDS REVISION/REJECT |
```

---

## Part 4: Quality Gate (Pass/Fail Evaluation)

Applied after finalization. Each dimension gets PASS or FAIL:

| Dimension | Target | How to Evaluate |
|-----------|--------|-----------------|
| Assertion Density | >= 1.5 per test avg | Count assert statements per test |
| Assertion Quality | >= 60% HIGH | Score each as HIGH/MEDIUM/LOW |
| Coverage Increase | > 0% | Compare baseline vs final measurement |
| Error Path Coverage | 100% | Every exception/error has a test |
| Test Independence | 100% | No shared state, no ordering |
| Determinism | 100% | No time, random, network deps |
| Flakiness | 0 patterns | No sleep/delay, no polling loops, no race conditions, no environment deps |
| Naming Compliance | 100% | `MethodName_Scenario_ExpectedBehavior` |
| Tautological Tests | 0% | No production logic in assertions |
| Behavioral Duplicates | 0% | No tests duplicating scenarios from existing tests |
| File Organization | 100% | One test class per file, named after source class |
| Exclusion Compliance | 0% violations | No tests for constants, DTOs, constructors, properties, logging |

**Overall**: PASS (all met) | CONDITIONAL PASS (1-2 below target) | FAIL (3+ below or critical failure)

---

## What Should Be Tested (Priority Order)

| Priority | What to Test | Why |
|----------|-------------|-----|
| P0 | Business logic methods | Core value of the application |
| P1 | Exception handlers and catch blocks | Critical error recovery paths |
| P1 | Input validation logic | Security and correctness boundary |
| P1 | Error return paths | User-facing error behavior |
| P1 | Retry/fallback logic | Resilience under failure |
| P2 | Complex conditionals (3+ branches) | High cyclomatic complexity |
| P2 | Data transformation methods | Correctness of data flow |
| P3 | Utility/helper methods with logic | Supporting functionality |

## What Should NOT Be Tested

| Category | Why Not |
|----------|---------|
| Constants and constant fields | Compile-time fixed; no behavior |
| Default value assignments | No logic to test |
| Auto-properties (get/set) | Language feature, not business logic |
| DTO/POCO classes and records | Data containers with no behavior |
| Logging conventions, logger providers, log formatters | Infrastructure concern, not business logic |
| Simple constructors | Assignment-only; no branching |
| Classes/methods marked `[Obsolete]` | Deprecated code; testing it encourages retention |
| Dead/unreachable code | Should be removed or refactored, not unit tested (do not confuse with rare but critical error/retry paths) |
| Generated code | Maintained by tooling, not humans |
