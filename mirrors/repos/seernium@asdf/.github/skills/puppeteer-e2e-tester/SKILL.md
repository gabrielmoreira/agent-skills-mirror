---
name: puppeteer-e2e-tester
description: Write and run end-to-end browser tests using Puppeteer — user flows, form submissions, navigation, visual/console error checks. Use when asked to "write an e2e test", "test this user flow in a browser", or "check this page with Puppeteer".
---

# Puppeteer E2E Tester Skill

This repo uses Puppeteer (via the Puppeteer MCP server, see `.vscode/mcp.json`) for true browser-driven E2E tests, distinct from Vitest/RTL component tests (DOM-only, no real browser) and Playwright (if also present, used for cross-browser suites).

## When to use Puppeteer vs RTL
- **RTL** (`test-writer-vitest-rtl` skill): component-level, fast, no real browser — use for most logic/UI tests.
- **Puppeteer**: full user flows that cross multiple pages/routes, need a real rendered browser (visual checks, real navigation, third-party scripts, file uploads, console-error detection), or are explicitly requested as "E2E"/"browser test".

## Process

1. Identify the user flow to test (e.g. "sign up → verify email → land on dashboard").
2. Create the test file under `e2e/puppeteer/<flow-name>.e2e.ts` using [e2e-test-template.ts](./e2e-test-template.ts).
3. Always:
   - Wait for elements via `page.waitForSelector` (or better, accessible role-based queries if using `puppeteer-testing-library`) — never `page.waitForTimeout` as a substitute for a real wait condition.
   - Assert on visible outcomes (URL changed, text appeared, element state) not implementation details.
   - Capture and assert there are no unexpected `console.error` calls during the flow (see template's console listener).
4. For forms, fill via `page.type`/`page.click` on labeled, role-queryable elements — coordinate with the `accessibility-auditor` agent if elements aren't queryable, since that's usually also an a11y gap.
5. Run with `pnpm test:e2e:puppeteer` and confirm pass/fail before reporting done.
6. Take a screenshot on failure (`page.screenshot`) to aid debugging — see template.

## Checklist
- [ ] Test targets a real user flow, not an implementation detail
- [ ] No `waitForTimeout` used as a wait strategy
- [ ] Console errors during the flow are captured and asserted on
- [ ] Screenshot-on-failure configured
- [ ] Test is independent (doesn't depend on state left by another test)
