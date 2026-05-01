---
name: e2e-test-plan
description: Plan end-to-end tests for user journeys, browser flows, CLI workflows, APIs, and multi-system behavior. Use when Codex is asked to define E2E coverage, Playwright/Cypress-style flows, smoke tests, or release-critical user paths.
license: MIT
---

# E2E Test Plan

## Core Workflow

1. Identify the critical user journey, entry point, data setup, success signal,
   and release risk.
2. Choose the smallest E2E path that verifies the user-visible outcome.
3. Define setup, actions, assertions, cleanup, test data, and environment.
4. Include accessibility, responsive, auth, payment, email, or external-system
   concerns only when relevant to the journey.
5. Separate smoke tests from full regression flows.
6. Specify command, CI cadence, flake risks, and manual fallback.

## Safety Rules

- Do not use real payment methods, production accounts, or customer data.
- Do not overuse E2E tests for behavior better covered by unit or integration
  tests.
- Do not claim browser flows work without runtime evidence.

## Deliverable Shape

For E2E plans, provide:

- Journey and success criteria
- Environment and test data
- Steps and assertions
- Smoke versus regression scope
- Cleanup
- Command and CI cadence
- Flake risks and mitigations

## References

- Read `references/e2e-test-plan-checklist.md` when planning E2E coverage.
