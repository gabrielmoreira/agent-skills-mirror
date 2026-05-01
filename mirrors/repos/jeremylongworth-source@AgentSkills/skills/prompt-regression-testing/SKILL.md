---
name: prompt-regression-testing
description: Design reusable prompt regression tests for agent skills and workflows. Use when Codex is asked to prevent a skill from regressing, create prompt test cases, cover known failures, or define repeatable evaluation prompts.
license: MIT
---

# Prompt Regression Testing

## Core Workflow

1. Identify the behavior that must not regress and the artifact it affects.
2. Create compact prompts for normal, edge, and known-failure cases.
3. Define expected invariants rather than brittle exact wording.
4. Pair each prompt with acceptance criteria and expected routing.
5. Add negative cases for over-triggering, unsafe actions, or missing context.
6. Record when the prompt should be re-run: before release, after skill edits,
   after host behavior changes, or after incidents.

## Safety Rules

- Do not include secrets, real customer data, or sensitive incidents in
  committed prompt tests.
- Do not make tests depend on exact prose unless exact language is the product.
- Do not rely only on happy-path prompts for high-risk skills.

## Deliverable Shape

For prompt regression plans, provide:

- Behavior under protection
- Prompt set
- Expected routing
- Acceptance criteria and invariants
- Negative cases
- Re-run trigger
- Validation command or review path

## References

- Read `references/prompt-regression-testing-checklist.md` when designing prompt
  regression coverage.
