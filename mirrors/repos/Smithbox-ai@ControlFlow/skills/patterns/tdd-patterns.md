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
|-------|-------|-------|-------------|
| Unit | Single function/class | <100ms | Always — default layer |
| Integration | Module boundaries | <1s | Cross-module data flow |
| Contract | API/schema compliance | <500ms | Schema validation, API response shapes |
| E2E | Full user workflow | <30s | Critical user journeys only |

## Commit Granularity
- One test + its implementation = one commit.
- Refactoring = separate commit (tests must stay green).
- Never commit a failing test on main unless it's explicitly marked as pending/skip.
