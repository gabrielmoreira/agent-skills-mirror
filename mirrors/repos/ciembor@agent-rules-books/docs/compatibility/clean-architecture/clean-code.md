# Clean Architecture vs Clean Code

Status: reviewed
Research basis: mini-only

Verdict: ✅ Complementary

Conflict: 16%
Overlap: 35%
Complementarity: 76%

## Loading Decision

Use together when policy independence or framework/persistence leakage appears alongside the other book's scope; Clean Architecture supplies dependency direction while the other book supplies local decision criteria.

## Book A Pressure

- Clean Architecture should drive tasks where business policy must stay independent from frameworks, databases, delivery, vendors, and volatile mechanisms.
- Evidence: `clean-architecture/clean-architecture.mini.md` lines 3-5: applies when business rules should survive changes in frameworks, databases, delivery mechanisms, services, vendors, or schedule pressure.

## Book B Pressure

- Clean Code should drive tasks where local readability, naming, function shape, side effects, tests, and scoped cleanup dominate.
- Evidence: `clean-code/clean-code.mini.md` lines 3-5: applies when readability, local reasoning, and maintainable code shape are the main concerns.

## Complementary Forces

- Claim: Clean Architecture contributes policy-independence and replaceable-detail pressure; Clean Code contributes local-readability, naming, function-shape, side-effect, test, and scoped-cleanup pressure. Together they are useful only where both scopes are active.
- Evidence:
  - `clean-architecture/clean-architecture.mini.md` lines 13-24: requires inward dependencies, domain/use-case policy placement, plain request/response boundaries, outer-layer details, policy-owned ports, humble adapters, use-case structure, boundary cost checks, and enforceable boundaries.
  - `clean-code/clean-code.mini.md` lines 13-26: requires scoped cleanup, local reasoning, precise names, small focused functions, few meaningful parameters, command/query separation, clear happy paths, behavior-not-representation APIs, business behavior isolated from technical details, useful comments, clean tests, emergent design, and bounded cleanup.

## Overlap

- Claim: They overlap where both affect boundaries, explicit responsibilities, tests, coupling reduction, and avoiding hidden assumptions; the overlap score reflects how often an agent would receive similar pressure from both.
- Evidence:
  - `clean-architecture/clean-architecture.mini.md` lines 42-49: checks policy independence, inward dependencies, invariant-guarding entities/use cases, enforced boundaries, humble adapters, business-revealing structure, fast core tests, and replaceable details.
  - `clean-code/clean-code.mini.md` lines 41-47: checks local followability, meaningful names/APIs, explicit mutation, hidden technical details, smell removal, protected behavior, and executed validation.

## Conflicts

- Claim: The tension is boundary cost: Clean Architecture may introduce ports/adapters/use cases where the other rule set would prefer a smaller local change unless policy independence is actually at risk.
- Evidence:
  - `clean-architecture/clean-architecture.mini.md` lines 7-9: corrects detail-driven architecture by keeping business policy independent and dependencies pointing inward.
  - `clean-code/clean-code.mini.md` lines 13-26: requires scoped cleanup, local reasoning, precise names, small focused functions, few meaningful parameters, command/query separation, clear happy paths, behavior-not-representation APIs, business behavior isolated from technical details, useful comments, clean tests, emergent design, and bounded cleanup.

## Use Together When

- Use together when one change simultaneously involves policy independence, inward dependencies, and replaceable details and local readability, names, function shape, side effects, and scoped cleanup; otherwise load only the rule set whose trigger is actually present.

## Prefer One When

- Prefer Clean Architecture when policy independence and replaceable details are the risk; prefer the other book when the task is narrower than architecture boundaries.

## Source Basis

- `clean-architecture/clean-architecture.mini.md` lines 3-5: applies when business rules should survive changes in frameworks, databases, delivery mechanisms, services, vendors, or schedule pressure.
- `clean-architecture/clean-architecture.mini.md` lines 7-9: corrects detail-driven architecture by keeping business policy independent and dependencies pointing inward.
- `clean-architecture/clean-architecture.mini.md` lines 13-24: requires inward dependencies, domain/use-case policy placement, plain request/response boundaries, outer-layer details, policy-owned ports, humble adapters, use-case structure, boundary cost checks, and enforceable boundaries.
- `clean-architecture/clean-architecture.mini.md` lines 42-49: checks policy independence, inward dependencies, invariant-guarding entities/use cases, enforced boundaries, humble adapters, business-revealing structure, fast core tests, and replaceable details.
- `clean-code/clean-code.mini.md` lines 3-5: applies when readability, local reasoning, and maintainable code shape are the main concerns.
- `clean-code/clean-code.mini.md` lines 7-9: corrects the idea that working code is automatically clean code.
- `clean-code/clean-code.mini.md` lines 13-26: requires scoped cleanup, local reasoning, precise names, small focused functions, few meaningful parameters, command/query separation, clear happy paths, behavior-not-representation APIs, business behavior isolated from technical details, useful comments, clean tests, emergent design, and bounded cleanup.
- `clean-code/clean-code.mini.md` lines 41-47: checks local followability, meaningful names/APIs, explicit mutation, hidden technical details, smell removal, protected behavior, and executed validation.

## Review Notes

- External context was not used as decisive evidence for Clean Architecture vs Clean Code; the verdict is based on the cited local `mini` line ranges.
