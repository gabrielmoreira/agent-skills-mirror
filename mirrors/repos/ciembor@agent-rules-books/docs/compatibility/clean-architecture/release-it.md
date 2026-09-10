# Clean Architecture vs Release It!

Status: reviewed
Research basis: mini-only

Verdict: ✅ Complementary

Conflict: 12%
Overlap: 34%
Complementarity: 78%

## Loading Decision

Use together when the task has production boundaries plus Clean Architecture design pressure: preserve the code/model shape while adding timeouts, retries, isolation, limits, and observability only where triggered.

## Book A Pressure

- Clean Architecture should drive tasks where business policy must stay independent from frameworks, databases, delivery, vendors, and volatile mechanisms.
- Evidence: `clean-architecture/clean-architecture.mini.md` lines 3-5: applies when business rules should survive changes in frameworks, databases, delivery mechanisms, services, vendors, or schedule pressure.

## Book B Pressure

- Release It! should drive tasks where production failure semantics, demand limits, timeouts, retries, isolation, observability, and recovery dominate.
- Evidence: `release-it/release-it.mini.md` lines 3-5: applies to services, APIs, jobs, queues, deployment paths, control tooling, and critical flows that must survive production failures and operational mistakes.

## Complementary Forces

- Claim: Clean Architecture contributes policy-independence and replaceable-detail pressure; Release It! contributes production-failure, demand-limit, timeout, retry, isolation, observability, and recovery pressure. Together they are useful only where both scopes are active.
- Evidence:
  - `clean-architecture/clean-architecture.mini.md` lines 13-24: requires inward dependencies, domain/use-case policy placement, plain request/response boundaries, outer-layer details, policy-owned ports, humble adapters, use-case structure, boundary cost checks, and enforceable boundaries.
  - `release-it/release-it.mini.md` lines 13-27: requires production failure assumptions, visible failure/limited blast radius/load shedding, operational concerns as part of the system, explicit time limits, safe bounded retries, isolation patterns, overload behavior, stability patterns, validated runtime/operational state, scarce-resource budgeting, untrusted external input, boundary observability, safe operational controls, production-aware interconnects/jobs/caches/contracts, security and bounded chaos/disaster testing.

## Overlap

- Claim: They overlap where both affect boundaries, explicit responsibilities, tests, coupling reduction, and avoiding hidden assumptions; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `clean-architecture/clean-architecture.mini.md` lines 42-49: checks policy independence, inward dependencies, invariant-guarding entities/use cases, enforced boundaries, humble adapters, business-revealing structure, fast core tests, and replaceable details.
  - `release-it/release-it.mini.md` lines 41-48: checks timeouts, retry safety, bounded queues/pools/payloads, failure isolation, validated external inputs, diagnostic coverage, recoverable operational controls, and explicit production failure behavior.

## Conflicts

- Claim: The tension is mechanism cost: reliability patterns add complexity and must be scoped to real production failure modes rather than added to simple local code.
- Evidence:
  - `clean-architecture/clean-architecture.mini.md` lines 7-9: corrects detail-driven architecture by keeping business policy independent and dependencies pointing inward.
  - `release-it/release-it.mini.md` lines 31-37: fires on outbound calls, queues/buffers/pools/caches/jobs, deployment/config/startup/migrations/automation, health/load/service discovery, API contracts, incident/capacity reviews, admin/control/chaos work.

## Use Together When

- Use together when the other design concern touches services, APIs, jobs, queues, dependency calls, deployment paths, or critical flows that need explicit failure behavior.

## Prefer One When

- Prefer Release It when production failures, overload, timeouts, retries, dependencies, or observability dominate; prefer the other book for purely local design or construction work.

## Source Basis

- `clean-architecture/clean-architecture.mini.md` lines 3-5: applies when business rules should survive changes in frameworks, databases, delivery mechanisms, services, vendors, or schedule pressure.
- `clean-architecture/clean-architecture.mini.md` lines 7-9: corrects detail-driven architecture by keeping business policy independent and dependencies pointing inward.
- `clean-architecture/clean-architecture.mini.md` lines 13-24: requires inward dependencies, domain/use-case policy placement, plain request/response boundaries, outer-layer details, policy-owned ports, humble adapters, use-case structure, boundary cost checks, and enforceable boundaries.
- `clean-architecture/clean-architecture.mini.md` lines 42-49: checks policy independence, inward dependencies, invariant-guarding entities/use cases, enforced boundaries, humble adapters, business-revealing structure, fast core tests, and replaceable details.
- `release-it/release-it.mini.md` lines 3-5: applies to services, APIs, jobs, queues, deployment paths, control tooling, and critical flows that must survive production failures and operational mistakes.
- `release-it/release-it.mini.md` lines 7-9: corrects happy-path production readiness by requiring failure semantics, demand limits, isolation, recovery, and diagnosis surfaces.
- `release-it/release-it.mini.md` lines 13-27: requires production failure assumptions, visible failure/limited blast radius/load shedding, operational concerns as part of the system, explicit time limits, safe bounded retries, isolation patterns, overload behavior, stability patterns, validated runtime/operational state, scarce-resource budgeting, untrusted external input, boundary observability, safe operational controls, production-aware interconnects/jobs/caches/contracts, security and bounded chaos/disaster testing.
- `release-it/release-it.mini.md` lines 41-48: checks timeouts, retry safety, bounded queues/pools/payloads, failure isolation, validated external inputs, diagnostic coverage, recoverable operational controls, and explicit production failure behavior.

## Review Notes

- External context was not used as decisive evidence for Clean Architecture vs Release It!; the verdict is based on the cited local `mini` line ranges.
