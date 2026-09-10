# Refactoring.Guru vs Release It!

Status: reviewed
Research basis: mini-only

Verdict: ✅ Complementary

Conflict: 12%
Overlap: 38%
Complementarity: 78%

## Loading Decision

Use together when changing existing code: one rule set controls safe change sequencing while the other defines the target design, construction, architecture, data, or production quality.

## Book A Pressure

- Refactoring.Guru should drive tasks where smell diagnosis, smallest treatment choice, behavior verification, and stop conditions dominate.
- Evidence: `refactoring-guru/refactoring-guru.mini.md` lines 3-5: applies when code smells, technique choice, behavior preservation, and cleanup scope control matter.

## Book B Pressure

- Release It! should drive tasks where production failure semantics, demand limits, timeouts, retries, isolation, observability, and recovery dominate.
- Evidence: `release-it/release-it.mini.md` lines 3-5: applies to services, APIs, jobs, queues, deployment paths, control tooling, and critical flows that must survive production failures and operational mistakes.

## Complementary Forces

- Claim: Refactoring.Guru contributes smell-diagnosis, smallest-treatment, behavior-verification, and stop-condition pressure; Release It! contributes production-failure, demand-limit, timeout, retry, isolation, observability, and recovery pressure. Together they are useful only where both scopes are active.
- Evidence:
  - `refactoring-guru/refactoring-guru.mini.md` lines 40-53: fires on comment/scroll/state-heavy methods, multi-reason classes, primitive meaning, long parameters, shotgun surgery, navigation chains, middle men, query-mutation mixing, repeated branches, null checks, inheritance problems, dead/speculative code, incomplete library gaps, and spreading cleanup.
  - `release-it/release-it.mini.md` lines 13-27: requires production failure assumptions, visible failure/limited blast radius/load shedding, operational concerns as part of the system, explicit time limits, safe bounded retries, isolation patterns, overload behavior, stability patterns, validated runtime/operational state, scarce-resource budgeting, untrusted external input, boundary observability, safe operational controls, production-aware interconnects/jobs/caches/contracts, security and bounded chaos/disaster testing.

## Overlap

- Claim: They overlap where both affect safe existing-code change, tests, behavior preservation, ownership, and stopping before speculative cleanup; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `refactoring-guru/refactoring-guru.mini.md` lines 57-64: checks work type, diagnosed smell/cost, smallest treatment, behavior preservation, smell reduction, no speculative pattern use, public/state/ownership checks, and documented untreated smells.
  - `release-it/release-it.mini.md` lines 41-48: checks timeouts, retry safety, bounded queues/pools/payloads, failure isolation, validated external inputs, diagnostic coverage, recoverable operational controls, and explicit production failure behavior.

## Conflicts

- Claim: The tension is scope creep: design or architecture improvements must not override behavior preservation, characterization, or the current-smell stop condition.
- Evidence:
  - `refactoring-guru/refactoring-guru.mini.md` lines 7-9: corrects treating refactoring as general cleanup or pattern application instead of smell-driven treatment with verification and stop condition.
  - `release-it/release-it.mini.md` lines 7-9: corrects happy-path production readiness by requiring failure semantics, demand limits, isolation, recovery, and diagnosis surfaces.

## Use Together When

- Use together when existing code must be reshaped toward Release It! goals without changing observable behavior or turning cleanup into redesign.

## Prefer One When

- Prefer the refactoring rule set when observable behavior must stay unchanged; prefer the other book when designing new behavior rather than reshaping existing structure.

## Source Basis

- `refactoring-guru/refactoring-guru.mini.md` lines 3-5: applies when code smells, technique choice, behavior preservation, and cleanup scope control matter.
- `refactoring-guru/refactoring-guru.mini.md` lines 7-9: corrects treating refactoring as general cleanup or pattern application instead of smell-driven treatment with verification and stop condition.
- `refactoring-guru/refactoring-guru.mini.md` lines 40-53: fires on comment/scroll/state-heavy methods, multi-reason classes, primitive meaning, long parameters, shotgun surgery, navigation chains, middle men, query-mutation mixing, repeated branches, null checks, inheritance problems, dead/speculative code, incomplete library gaps, and spreading cleanup.
- `refactoring-guru/refactoring-guru.mini.md` lines 57-64: checks work type, diagnosed smell/cost, smallest treatment, behavior preservation, smell reduction, no speculative pattern use, public/state/ownership checks, and documented untreated smells.
- `release-it/release-it.mini.md` lines 3-5: applies to services, APIs, jobs, queues, deployment paths, control tooling, and critical flows that must survive production failures and operational mistakes.
- `release-it/release-it.mini.md` lines 7-9: corrects happy-path production readiness by requiring failure semantics, demand limits, isolation, recovery, and diagnosis surfaces.
- `release-it/release-it.mini.md` lines 13-27: requires production failure assumptions, visible failure/limited blast radius/load shedding, operational concerns as part of the system, explicit time limits, safe bounded retries, isolation patterns, overload behavior, stability patterns, validated runtime/operational state, scarce-resource budgeting, untrusted external input, boundary observability, safe operational controls, production-aware interconnects/jobs/caches/contracts, security and bounded chaos/disaster testing.
- `release-it/release-it.mini.md` lines 41-48: checks timeouts, retry safety, bounded queues/pools/payloads, failure isolation, validated external inputs, diagnostic coverage, recoverable operational controls, and explicit production failure behavior.

## Review Notes

- External context was not used as decisive evidence for Refactoring.Guru vs Release It!; the verdict is based on the cited local `mini` line ranges.
