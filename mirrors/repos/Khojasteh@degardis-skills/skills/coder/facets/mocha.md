---
title: Mocha
category: Test framework
x-claim-provenance:
- claim: Mocha allows any assertion library, and anything that throws an Error works.
  source: https://mochajs.org/features/assertions/
- claim: Mocha needs no special syntax for parameterized tests because suites and tests are function expressions that plain JavaScript can generate dynamically.
  source: https://mochajs.org/declaring/dynamic-tests/
- claim: Since Mocha v3.0.0, a test that both returns a Promise and calls done() fails with an overspecified-resolution error.
  source: https://mochajs.org/features/asynchronous-code/
- claim: Arrow functions passed to Mocha lexically bind this and cannot access the Mocha context, so this.timeout() fails inside them, while chained calls such as .timeout() on tests and hooks remain available.
  source: https://mochajs.org/features/arrow-functions/
- claim: The Mocha CLI provides --check-leaks for global variable leaks, --forbid-only to fail on exclusive tests, --parallel with --jobs for concurrent jobs, --retries to retry failed tests, --grep and --fgrep to select tests, and --bail to abort after the first failure.
  source: https://mochajs.org/running/cli/
---

Mocha leaves assertions and test doubles to the libraries the project already depends on, and its documented parameterization is one generated `it` per case with the case in its title so a failure identifies it. An asynchronous test completes through either a returned promise or the `done` callback, not both, and a test that uses Mocha's `this.timeout` or `this.retries` context has to be a non-arrow function.

`--check-leaks` exposes leaked globals, `--forbid-only` detects a leftover `.only`, `--parallel` with `--jobs` changes concurrency to diagnose interference, and `--retries` reruns failed tests. A spec path plus `--grep` or `--fgrep` narrows a run, `--bail` limits later failures, and `--reporter dot` or `--reporter min` reduces output.
