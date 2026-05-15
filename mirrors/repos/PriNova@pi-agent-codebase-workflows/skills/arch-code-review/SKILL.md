---
name: arch-code-review
description: Architecture-aware code review for current diffs in documented codebases. Use to review changes against architecture, data model, invariants, dependency rules, risk register, side-effect boundaries, and tests. Read-only workflow.
---

# Architecture Code Review

Goal: review proposed changes for correctness, drift, data consistency, side-effect boundary violations, and missing tests.

## Scope Argument

Review prompts accept an optional `[scope]` argument. Use it to focus review on a module, package, app, service, directory, or bounded domain area when a diff spans multiple areas. Still inspect immediate dependencies and contracts needed to judge correctness.

## Rules

- Do not edit code.
- Review current diff unless user specifies another target.
- Do not explicitly read `AGENTS.md`; pi injects root `AGENTS.md` automatically.
- Read only relevant deeper docs:
  - `docs/agent/ARCHITECTURE.md`
  - `docs/agent/DATA_MODEL.md`
  - `docs/agent/INVARIANTS.md`
  - `docs/agent/DEPENDENCY_RULES.md`
  - `docs/agent/RISK_REGISTER.md`
  - `docs/agent/CHANGE_GUIDE.md`
- Prioritize correctness, architecture drift, data consistency, side-effect boundaries, public contracts, and tests.
- Ignore style unless it affects maintainability or correctness.
- No generic comments.
- Every finding needs evidence and fix direction.
- Classify severity: critical / high / medium / low.

## Review Checklist

- Does diff match documented architecture and dependency directions?
- Are invariants preserved or intentionally updated?
- Are data model/schema changes documented and tested?
- Are side effects kept at existing boundaries?
- Are public contracts/backward compatibility respected?
- Are known risk areas touched?
- Are tests sufficient for changed behavior?
- Did implementation combine feature, bug fix, and refactoring accidentally?
- Are docs updated only for durable semantic changes?

## Output

1. Summary verdict:
   - approve
   - approve with comments
   - request changes
2. Findings, each with:
   - Severity
   - Location
   - Problem
   - Evidence
   - Why it matters
   - Suggested fix
3. Missing tests
4. Documentation updates needed
5. Architecture drift risk
6. Final recommendation
