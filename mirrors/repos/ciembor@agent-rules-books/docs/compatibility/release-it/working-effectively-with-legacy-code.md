# Release It! vs Working Effectively with Legacy Code

Status: reviewed
Research basis: mini-only

Verdict: ✅ Complementary

Conflict: 12%
Overlap: 38%
Complementarity: 78%

## Loading Decision

Use together when changing existing code: one rule set controls safe change sequencing while the other defines the target design, construction, architecture, data, or production quality.

## Book A Pressure

- Release It! should drive tasks where production failure semantics, demand limits, timeouts, retries, isolation, observability, and recovery dominate.
- Evidence: `release-it/release-it.mini.md` lines 3-5: applies to services, APIs, jobs, queues, deployment paths, control tooling, and critical flows that must survive production failures and operational mistakes.

## Book B Pressure

- Working Effectively with Legacy Code should drive tasks where unclear or weakly tested code requires characterization, seams, dependency breaking, and small safe changes.
- Evidence: `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 3-5: applies when code is expensive to change safely because behavior is unclear, tests are weak, dependencies hidden, or runtime/framework setup blocks feedback.

## Complementary Forces

- Claim: Release It! contributes production-failure, demand-limit, timeout, retry, isolation, observability, and recovery pressure; Working Effectively with Legacy Code contributes characterization, seam, dependency-breaking, small-change, and local-refactoring pressure. Together they are useful only where both scopes are active.
- Evidence:
  - `release-it/release-it.mini.md` lines 31-37: fires on outbound calls, queues/buffers/pools/caches/jobs, deployment/config/startup/migrations/automation, health/load/service discovery, API contracts, incident/capacity reviews, admin/control/chaos work.
  - `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 13-27: requires treating untested areas as legacy, stating behavior delta and preserved behavior, following the legacy loop, focused tests, effect tracing, smallest useful seam, deliberate dependency breaking, separated behavior/refactor/cleanup, sprout/wrap/extract moves for risky edits, side-effect/policy separation, barrier-specific dependency breaking, responsibility sketching, legacy-risk review, rejecting hidden-dependency expansion or premature architecture, and leaving touched area more testable/changeable.

## Overlap

- Claim: They overlap where both affect safe existing-code change, tests, behavior preservation, ownership, and stopping before speculative cleanup; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `release-it/release-it.mini.md` lines 41-48: checks timeouts, retry safety, bounded queues/pools/payloads, failure isolation, validated external inputs, diagnostic coverage, recoverable operational controls, and explicit production failure behavior.
  - `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 42-50: checks legacy risk, behavior delta/preservation, characterization, close fast tests, smallest seam, reduced blocking dependency, separated behavior/refactor/cleanup, cleanup path for temporary seams, and improved understandability/testability.

## Conflicts

- Claim: The tension is scope creep: design or architecture improvements must not override behavior preservation, characterization, or the current-smell stop condition.
- Evidence:
  - `release-it/release-it.mini.md` lines 7-9: corrects happy-path production readiness by requiring failure semantics, demand limits, isolation, recovery, and diagnosis surfaces.
  - `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 7-9: corrects improving design before gaining control by requiring behavior understanding, preservation, smallest useful seam, dependency breaking, requested change, and local testability improvement.

## Use Together When

- Use together when changing weakly tested code toward Release It! goals: first characterize behavior and create the smallest seam, then apply the other rule set inside the controlled change area.

## Prefer One When

- Prefer Working Effectively with Legacy Code when tests are weak or behavior is unclear; prefer the other book only after control, characterization, or seams make the change safe.

## Source Basis

- `release-it/release-it.mini.md` lines 3-5: applies to services, APIs, jobs, queues, deployment paths, control tooling, and critical flows that must survive production failures and operational mistakes.
- `release-it/release-it.mini.md` lines 7-9: corrects happy-path production readiness by requiring failure semantics, demand limits, isolation, recovery, and diagnosis surfaces.
- `release-it/release-it.mini.md` lines 31-37: fires on outbound calls, queues/buffers/pools/caches/jobs, deployment/config/startup/migrations/automation, health/load/service discovery, API contracts, incident/capacity reviews, admin/control/chaos work.
- `release-it/release-it.mini.md` lines 41-48: checks timeouts, retry safety, bounded queues/pools/payloads, failure isolation, validated external inputs, diagnostic coverage, recoverable operational controls, and explicit production failure behavior.
- `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 3-5: applies when code is expensive to change safely because behavior is unclear, tests are weak, dependencies hidden, or runtime/framework setup blocks feedback.
- `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 7-9: corrects improving design before gaining control by requiring behavior understanding, preservation, smallest useful seam, dependency breaking, requested change, and local testability improvement.
- `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 13-27: requires treating untested areas as legacy, stating behavior delta and preserved behavior, following the legacy loop, focused tests, effect tracing, smallest useful seam, deliberate dependency breaking, separated behavior/refactor/cleanup, sprout/wrap/extract moves for risky edits, side-effect/policy separation, barrier-specific dependency breaking, responsibility sketching, legacy-risk review, rejecting hidden-dependency expansion or premature architecture, and leaving touched area more testable/changeable.
- `working-effectively-with-legacy-code/working-effectively-with-legacy-code.mini.md` lines 42-50: checks legacy risk, behavior delta/preservation, characterization, close fast tests, smallest seam, reduced blocking dependency, separated behavior/refactor/cleanup, cleanup path for temporary seams, and improved understandability/testability.

## Review Notes

- External context was not used as decisive evidence for Release It! vs Working Effectively with Legacy Code; the verdict is based on the cited local `mini` line ranges.
