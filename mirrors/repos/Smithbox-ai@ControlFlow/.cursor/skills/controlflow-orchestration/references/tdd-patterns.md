# TDD Patterns

Adapted from the main ControlFlow project. Use during implementation phases run by `controlflow-orchestration` and during post-implementation `controlflow-review`.

## TDD Iron Law: RED -> GREEN -> REFACTOR

1. **RED** — Write a failing test that describes the desired behavior. The test MUST fail before implementation.
2. **GREEN** — Write the minimum code to make the test pass. No more, no less.
3. **REFACTOR** — Clean up the implementation while keeping tests green.

## Decision Heuristic

Ask: "Can I write `expect(fn(input)).toBe(output)` before writing `fn`?"

- **Yes** -> Write the test first (standard TDD).
- **No** -> Clarify requirements until you can. If requirements are genuinely unclear, write a spike (exploratory code), then delete it and restart with TDD.

## Test Quality Signals

### Good Tests

- **Behavior-describing** — Test names describe what the system does, not how.
- **Independent** — Each test sets up its own state; no ordering dependencies.
- **Fast** — Unit tests complete in <100ms each.
- **Deterministic** — Same input -> same result, always.

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

## Prove-It Framing

A test must prove a production behavior, not merely exercise code. It should fail when the behavior is absent, stubbed, wired to the wrong dependency, or returning the wrong observable result. If a gutted implementation could still pass the test, move the assertion to the public boundary, strengthen the expected output, or add the missing state/contract check.

## Beyonce Rule

If a behavior matters enough to change, it matters enough to protect with an automated signal. Bug fixes need regression coverage, new behavior needs a test or contract check, and newly discovered edge cases should become stable fixtures. When ordinary test coverage is impossible, record why and add the closest deterministic guard available.

## DAMP Over DRY In Tests

Tests should read like small examples of behavior. Prefer descriptive setup, meaningful literals, and explicit assertions over clever shared helpers that hide the scenario. Use helpers for noisy plumbing, not for the facts a reviewer needs in order to understand the case.

## Test Size & Resource Model

| Size | Target Share | Boundary | Best For | Cost |
| ---- | ------------ | -------- | -------- | ---- |
| Small | ~80% | Same process, no I/O or network | Pure logic, validators, transforms, local policy checks | Fastest and easiest to debug. |
| Medium | ~15% | Local integration with filesystem, database, or service-like boundary | Schema fixtures, module handoffs, local persistence | More setup and moderate flake risk. |
| Large | ~5% | Full workflow, browser, network, or external-like environment | Critical end-to-end journeys | Slowest and most expensive to maintain. |

Default to the smallest test that can prove the behavior. Use larger tests only when the behavior exists at a real boundary that smaller tests cannot represent.

## Commit Granularity

- One test + its implementation = one commit.
- Refactoring = separate commit (tests must stay green).
- Never commit a failing test on the main branch unless it's explicitly marked as pending/skip.

## Interaction with `controlflow-executability-verifier`

The 8-point cold-start checklist already requires `verify_command_complete` and `test_specifics_concrete`. This skill is the implementation-side counterpart: when the plan says "write tests for X", the executor follows RED -> GREEN -> REFACTOR rather than writing tests after the fact to pass an existing implementation.
