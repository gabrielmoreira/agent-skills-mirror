# TDD Patterns

## TDD Iron Law: RED → GREEN → REFACTOR

1. **RED** — Write a failing test that describes the desired behavior. The test MUST fail before implementation.
2. **GREEN** — Write the minimum code to make the test pass. No more, no less.
3. **REFACTOR** — Clean up the implementation while keeping tests green.

## Decision Heuristic

Ask: "Can I write `expect(fn(input)).toBe(output)` before writing `fn`?"

- **Yes** → Write the test first (standard TDD).
- **No** → Clarify requirements until you can. If requirements are genuinely unclear, write a spike (exploratory code), then delete it and restart with TDD.

## Test Quality Signals

### Good Tests

- **Behavior-describing** — Test names describe what the system does, not how.
- **Independent** — Each test sets up its own state; no ordering dependencies.
- **Fast** — Unit tests complete in <100ms each.
- **Deterministic** — Same input → same result, always.

### Bad Tests (Anti-Patterns)

- **Implementation-mirroring** — Test restates the code logic rather than testing outcomes.
- **Fragile** — Test breaks when internal structure changes but behavior stays the same.
- **Tautological** — Test cannot fail (e.g., `expect(true).toBe(true)`).
- **Flaky** — Test sometimes passes, sometimes fails without code changes.

## Test Layer Matrix

| Layer | Scope | Speed | When to Use |
| ----- | ----- | ----- | ----------- |
| Unit | Single function/class | <100ms | Always — default layer |
| Integration | Module boundaries | <1s | Cross-module data flow |
| Contract | API/schema compliance | <500ms | Schema validation, API response shapes |
| E2E | Full user workflow | <30s | Critical user journeys only |

## Commit Granularity

- One test + its implementation = one commit.
- Refactoring = separate commit (tests must stay green).
- Never commit a failing test on main unless it's explicitly marked as pending/skip.

## Prove-It Framing

Every test must prove production behavior. A test is useful only when it fails for the missing or broken behavior and passes when that behavior is correctly implemented.

Before accepting a test, ask: if the production implementation were gutted, stubbed, or wired to the wrong dependency, would this test still pass? If yes, it is not proving the behavior yet. Strengthen the assertion, move the test to the right boundary, or add the missing observable outcome.

## Beyonce Rule

If you liked it, you should have put a test on it. Bug fixes require regression tests. Behavior changes require test changes. New edge cases, schema expectations, validators, orchestration rules, and user-visible workflows need a matching automated signal.

When a test cannot be added in the normal layer, record why and choose the closest deterministic guard available. Do not treat manual confidence as equivalent to regression coverage.

## DAMP Over DRY (In Tests)

Production code often benefits from removing duplication. Test code benefits from being readable in isolation. Prefer DAMP: Descriptive And Meaningful Phrases that make each test explain its scenario, action, and expected outcome without forcing the reader through a maze of shared setup.

Use helpers for noisy plumbing, not for hiding the facts that make a case meaningful. Repeated literals, clear fixture construction, and explicit assertions are acceptable when they make the test read like a small specification.

## Test Size & Resource Model

| Size | Target Share | Resource Boundary | Typical Use | Cost Profile |
| ---- | ------------ | ----------------- | ----------- | ------------ |
| Small | ~80% | Unit scope, same process, no I/O, no network | Pure logic, validators, transforms, local policy checks | Fastest, most deterministic, easiest to debug. |
| Medium | ~15% | Integration scope with local I/O or local services only | Module boundaries, schema/fixture checks, local persistence | More setup, slower feedback, moderate flake risk. |
| Large | ~5% | E2E or full workflow, browser, network, or external-like environment | Critical user journeys and end-to-end orchestration | Highest maintenance cost and highest flake risk. |

Default to the smallest test that can prove the behavior. Larger tests are valuable when the behavior only exists across a real boundary, but they should not replace focused unit or contract coverage for logic that can be checked cheaply.

## Test Anti-Rationalization Table

| Pattern | Why It Fails | Required Action |
| ------- | ------------ | --------------- |
| Test the implementation directly | The test can pass while the public behavior is broken, and it becomes fragile during refactors. | Assert through the behavior boundary the caller actually uses. |
| Skip tests because the change is small | Small changes still create regressions, especially in validators, prompts, and edge cases. | Add the smallest meaningful guard or explain the verified existing coverage. |
| Mock everything | Over-mocking proves interactions with doubles instead of behavior in the system. | Use real code or lightweight fakes unless the dependency is slow, unstable, or unsafe. |
| Test passes locally so it's fine | Local success can miss order dependence, schema drift, and broader regressions. | Run the targeted test and the required suite for the change scope. |
| Assert only that nothing throws | The test may ignore the output, state change, or contract that actually matters. | Assert the observable result that would fail if the behavior regressed. |
