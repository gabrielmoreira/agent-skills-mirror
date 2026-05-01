---
name: scenario-test-authoring
description: Write realistic routing and evaluation scenarios for agent skills and skillsets. Use when Codex is asked to add tests under tests/scenarios, define expected skill routing, create scenario prompts, or turn bundle use cases into scenario coverage.
license: MIT
---

# Scenario Test Authoring

## Core Workflow

1. Identify the user job, target artifact, and skill or bundle that should
   route for the request.
2. Write a realistic prompt that includes enough context to trigger the right
   skills without naming the expected answer.
3. List expected routing using exact skill folder names.
4. Add the scenario file under `tests/scenarios/` and the matching key in
   `tests/expected-routing.yaml`.
5. Include high-risk review or approval expectations in the prompt when the
   scenario touches customers, production, finance, legal, security, or policy.
6. Run validation after adding or changing route scenarios.

## Safety Rules

- Do not include private customer, employee, credential, or production data in
  committed scenarios.
- Do not write scenarios that require live systems or private connectors.
- Do not make routing depend on a host-specific command unless the scenario is
  explicitly host-specific.

## Deliverable Shape

For scenario work, provide:

- Scenario name and user prompt
- Expected routing list
- Future or current bundle
- Acceptance checks
- Risk and review notes
- Files updated
- Validation run

## References

- Read `references/scenario-test-authoring-checklist.md` when creating or
  reviewing route scenarios.
