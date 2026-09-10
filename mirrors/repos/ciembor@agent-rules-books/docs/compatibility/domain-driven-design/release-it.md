# Domain-Driven Design vs Release It!

Status: reviewed
Research basis: mini-only

Verdict: ✅ Complementary

Conflict: 12%
Overlap: 34%
Complementarity: 78%

## Loading Decision

Use together when the task has production boundaries plus Domain-Driven Design design pressure: preserve the code/model shape while adding timeouts, retries, isolation, limits, and observability only where triggered.

## Book A Pressure

- Domain-Driven Design should drive tasks where model language, lifecycle rules, invariants, or Bounded Contexts dominate.
- Evidence: `domain-driven-design/domain-driven-design.mini.md` lines 3-5: applies when business complexity, model language, lifecycle rules, or cross-team/system boundaries shape design more than generic technical organization.

## Book B Pressure

- Release It! should drive tasks where production failure semantics, demand limits, timeouts, retries, isolation, observability, and recovery dominate.
- Evidence: `release-it/release-it.mini.md` lines 3-5: applies to services, APIs, jobs, queues, deployment paths, control tooling, and critical flows that must survive production failures and operational mistakes.

## Complementary Forces

- Claim: Domain-Driven Design contributes model-language, Bounded-Context, invariant, and domain-test pressure; Release It! contributes production-failure, demand-limit, timeout, retry, isolation, observability, and recovery pressure. Together they are useful only where both scopes are active.
- Evidence:
  - `domain-driven-design/domain-driven-design.mini.md` lines 13-27: requires implementation-expressed models, Ubiquitous Language per Bounded Context, domain-layer business logic, tactical patterns for model meaning, Aggregate/Repository/Factory lifecycle management, model-first persistence, deeper insight refactoring, conceptual contours, explicit bounded contexts and relationships, Core Domain protection, source-supported prior art, domain-language tests, and domain-aware strategic moves.
  - `release-it/release-it.mini.md` lines 13-27: requires production failure assumptions, visible failure/limited blast radius/load shedding, operational concerns as part of the system, explicit time limits, safe bounded retries, isolation patterns, overload behavior, stability patterns, validated runtime/operational state, scarce-resource budgeting, untrusted external input, boundary observability, safe operational controls, production-aware interconnects/jobs/caches/contracts, security and bounded chaos/disaster testing.

## Overlap

- Claim: They overlap where both affect boundaries, explicit responsibilities, tests, coupling reduction, and avoiding hidden assumptions; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `domain-driven-design/domain-driven-design.mini.md` lines 43-48: checks explicit domain behavior, one language per context, tactical patterns protecting model meaning, explicit cross-context translation, executable model tests, and protected Core Domain.
  - `release-it/release-it.mini.md` lines 41-48: checks timeouts, retry safety, bounded queues/pools/payloads, failure isolation, validated external inputs, diagnostic coverage, recoverable operational controls, and explicit production failure behavior.

## Conflicts

- Claim: The tension is mechanism cost: reliability patterns add complexity and must be scoped to real production failure modes rather than added to simple local code.
- Evidence:
  - `domain-driven-design/domain-driven-design.mini.md` lines 7-9: corrects persistence/UI/framework/format/vocabulary replacing an implementation-driving model.
  - `release-it/release-it.mini.md` lines 31-37: fires on outbound calls, queues/buffers/pools/caches/jobs, deployment/config/startup/migrations/automation, health/load/service discovery, API contracts, incident/capacity reviews, admin/control/chaos work.

## Use Together When

- Use together when the other design concern touches services, APIs, jobs, queues, dependency calls, deployment paths, or critical flows that need explicit failure behavior.

## Prefer One When

- Prefer Release It when production failures, overload, timeouts, retries, dependencies, or observability dominate; prefer the other book for purely local design or construction work.

## Source Basis

- `domain-driven-design/domain-driven-design.mini.md` lines 3-5: applies when business complexity, model language, lifecycle rules, or cross-team/system boundaries shape design more than generic technical organization.
- `domain-driven-design/domain-driven-design.mini.md` lines 7-9: corrects persistence/UI/framework/format/vocabulary replacing an implementation-driving model.
- `domain-driven-design/domain-driven-design.mini.md` lines 13-27: requires implementation-expressed models, Ubiquitous Language per Bounded Context, domain-layer business logic, tactical patterns for model meaning, Aggregate/Repository/Factory lifecycle management, model-first persistence, deeper insight refactoring, conceptual contours, explicit bounded contexts and relationships, Core Domain protection, source-supported prior art, domain-language tests, and domain-aware strategic moves.
- `domain-driven-design/domain-driven-design.mini.md` lines 43-48: checks explicit domain behavior, one language per context, tactical patterns protecting model meaning, explicit cross-context translation, executable model tests, and protected Core Domain.
- `release-it/release-it.mini.md` lines 3-5: applies to services, APIs, jobs, queues, deployment paths, control tooling, and critical flows that must survive production failures and operational mistakes.
- `release-it/release-it.mini.md` lines 7-9: corrects happy-path production readiness by requiring failure semantics, demand limits, isolation, recovery, and diagnosis surfaces.
- `release-it/release-it.mini.md` lines 13-27: requires production failure assumptions, visible failure/limited blast radius/load shedding, operational concerns as part of the system, explicit time limits, safe bounded retries, isolation patterns, overload behavior, stability patterns, validated runtime/operational state, scarce-resource budgeting, untrusted external input, boundary observability, safe operational controls, production-aware interconnects/jobs/caches/contracts, security and bounded chaos/disaster testing.
- `release-it/release-it.mini.md` lines 41-48: checks timeouts, retry safety, bounded queues/pools/payloads, failure isolation, validated external inputs, diagnostic coverage, recoverable operational controls, and explicit production failure behavior.

## Review Notes

- External context was not used as decisive evidence for Domain-Driven Design vs Release It!; the verdict is based on the cited local `mini` line ranges.
