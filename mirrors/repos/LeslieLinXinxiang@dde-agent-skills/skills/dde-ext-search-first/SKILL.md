---
name: dde-ext-search-first
description: "DDE subordinate extension. Research-before-implementation workflow for dependency/library/approach selection. Can execute discovery commands, but cannot bypass DDE write gates."
---

# DDE Extension: Search First

Skill Version: v0.1

## Authority Chain
- Commander: `dde-bootstrap`
- Write gate: `dde-code-guard`
- This skill is subordinate and cannot override Layer 0-4 docs.

## When to Use
- User asks to add a new feature likely having existing solutions.
- User asks to introduce dependencies, tools, or wrappers.
- DDE workflow requests pre-implementation research.

## Execution Scope
Allowed:
- Repo scan (`rg`, file reads, dependency inspection)
- External package/options comparison
- Produce recommendation matrix: Adopt / Extend / Build
- Run non-destructive checks

Not allowed:
- No direct requirement mutation
- No bypass of RFC flow
- No direct code write without DDE gate

## Mandatory Flow
1. Clarify target capability and constraints.
2. Search existing in-repo implementation first.
3. Search external maintained options.
4. Produce a ranked recommendation with tradeoffs.
5. If recommendation requires file changes, emit handoff:

`DDE_EXTENSION_HANDOFF_REQUIRED`

Handoff fields:
- Reason
- Target files
- Expected effect
- Risk notes

Then stop and re-enter `dde-code-guard` two-phase approval.

## Output Contract
- Short decision summary
- Candidate table (name, maturity, fit, risk)
- Final recommendation
- Handoff block if writes are required
