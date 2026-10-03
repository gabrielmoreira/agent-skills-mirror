---
title: Cypress
category: Test framework
x-claim-provenance:
- claim: Cypress commands do not act when invoked but enqueue themselves to run later, and they yield rather than return their subjects, so a command's return value cannot be used directly.
  source: https://docs.cypress.io/app/core-concepts/introduction-to-cypress
- claim: When an assertion fails, Cypress requeries the application's DOM from the top of the chain of linked queries and keeps retrying until the timeout is reached.
  source: https://docs.cypress.io/app/core-concepts/retry-ability
- claim: Test retries are disabled by default, with 0 retry attempts for both cypress run and cypress open.
  source: https://docs.cypress.io/app/guides/test-retries
  scope: Cypress documentation, read 2026-09.
- claim: cypress run --spec runs the specified spec files instead of all tests and --quiet reduces output printed to stdout, and the command-line reference lists no built-in option to filter tests by title.
  source: https://docs.cypress.io/app/references/command-line
  scope: Cypress documentation, read 2026-09.
- claim: screenshotsFolder defaults to cypress/screenshots and videosFolder to cypress/videos, and trashAssetsBeforeRuns, true by default, makes cypress run clear the entire contents of the downloads, screenshots, and videos folders before tests run.
  source: https://docs.cypress.io/app/references/configuration
  scope: Cypress documentation, read 2026-09.
---

Cypress commands are enqueued rather than executed where they are written, so a command's result does not behave like an immediate local value, and chaining preserves the queue's semantics. Assertions made with `should` and `and` retry until the application reaches the expected state, which usually makes a fixed delay unnecessary for anything observable. `cy.wait(<number>)` is exactly such a fixed delay, while waiting on an aliased request or a retrying assertion gives an observable synchronization point.

`cy.intercept`, `cy.clock`, and `cy.tick` control the network and time, `cy.session` can cache authenticated state, and stable test attributes keep selectors from depending on generated class names. State that one spec leaves behind can make another depend on order. The `retries` configuration turns a first failure into a later pass, which hides the failing outcome a diagnosis needs.

A spec path narrows a run natively, as in `cypress run --spec "cypress/e2e/thing.cy.ts"`, and `--quiet` with a terse reporter reduces output. Where the resolved Cypress version has no built-in filter by test title, title filtering works only through a grep plugin the project has already configured.

Cypress does not prune fixtures or snapshot-plugin baselines when the last test using them disappears. `cypress/screenshots` and `cypress/videos` hold run output rather than committed expectations, and under the default `trashAssetsBeforeRuns`, `cypress run` empties them and the downloads folder before each run.
