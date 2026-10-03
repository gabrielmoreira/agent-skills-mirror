---
title: Playwright
category: Test framework
x-claim-provenance:
- claim: Playwright Test snapshot locations can be configured with snapshotPathTemplate, including assertion-specific path templates.
  source: https://playwright.dev/docs/api/class-testconfig#test-config-snapshot-path-template
  scope: Playwright Test 1.28+; the first-party API documents snapshotPathTemplate as added in 1.28.
---

Each Playwright test receives a fresh browser context. Authenticated state can be shared through `storageState`, fixtures extend through `test.extend`, and routing and interception can control network behavior instead of a live external service. Role, label, and test-identifier locators pair with web-first assertions such as `expect(locator).toHaveText(...)`, which retry until the expectation holds or times out; a one-shot `textContent()` read lacks that retry contract, and `waitForTimeout` or any other fixed sleep is only elapsed time rather than evidence of application readiness.

`--repeat-each <n>` and `--workers 1` can expose flake and concurrency effects. A run narrows to a line with `playwright test path/to/spec.ts:42`, to a title with `-g`, to one browser with `--project`, or to the previous failures with `--last-failed`; `-x` or `--max-failures <n>` constrains later failures, and `--reporter line` or `--reporter dot` reduces output. Headed execution is relevant only when rendering itself is the question.

Visual and snapshot baselines follow the resolved snapshot configuration, including custom path templates, so which test owns a baseline depends on that configuration rather than on an assumed default `-snapshots` layout.
