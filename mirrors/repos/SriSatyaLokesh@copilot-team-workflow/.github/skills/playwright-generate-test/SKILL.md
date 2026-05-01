---
name: playwright-generate-test
description: "Use when a developer wants to create a Playwright end-to-end or browser test for a specific feature, flow, or scenario — when they say 'write a Playwright test for', 'generate a test for the login flow', 'add e2e tests for', or 'test this UI with Playwright'. Uses Playwright MCP tools to first interact with the real browser (not just guess at selectors), then generates a TypeScript spec using @playwright/test. Saves to tests/ directory with <feature>.spec.ts naming. Iterates until the test passes. Auto-loads when Playwright, e2e, browser test, or UI test is mentioned."
---

# Test Generation with Playwright MCP

Your goal is to generate a Playwright test based on the provided scenario after completing all prescribed steps.

## Specific Instructions

- You are given a scenario, and you need to generate a Playwright test for it. If the user does not provide a scenario, ask them to provide one.
- **DO NOT** generate test code prematurely or based solely on the scenario without completing all prescribed steps.
- **DO** run steps one by one using the tools provided by the Playwright MCP.
- Only after all steps are completed, emit a Playwright TypeScript test that uses `@playwright/test` based on message history.
- Save the generated test file in the `tests/` directory following the naming convention `<feature>.spec.ts`.
- Execute the test file and iterate until the test passes.