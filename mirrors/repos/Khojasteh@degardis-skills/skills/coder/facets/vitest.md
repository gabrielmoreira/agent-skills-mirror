---
title: Vitest
category: Test framework
x-claim-provenance:
- claim: The vitest command enters watch mode in a development environment and run mode in CI or a non-interactive terminal.
  source: https://vitest.dev/guide/cli
  scope: Vitest documentation, read 2026-09.
- claim: Vitest filters files by name on the command line, accepts a file path with a line number from v3, filters tests by full name with -t or --testNamePattern, randomizes and reproduces order with --sequence.shuffle and --sequence.seed, and reruns failing tests with --retry.
  source: https://vitest.dev/guide/cli
  scope: Vitest documentation, read 2026-09.
- claim: By default Vitest does not write snapshots in CI, where snapshot mismatches, missing snapshots, and obsolete snapshots fail the run, and an obsolete snapshot is one that no longer matches any collected test, usually after a test is removed or renamed.
  source: https://vitest.dev/guide/snapshot
  scope: Vitest documentation, read 2026-09.
---

Whether Vitest watches or runs once depends on the configured version, the execution context, CI detection, and the project's command aliases, so a bare invocation has no universal watch or exit meaning. Environment, transforms, aliases, setup files, pool, isolation, and fake-timer behavior come from project configuration rather than Node defaults, and the configured Vitest APIs provide time, environment, and hoisted-module-mock control, while rejection and asynchronous-cleanup behavior remains observable at caller boundaries.

File and test-name selection syntax is version-dependent, and bail, silence, shuffling, seeding, retry, and file-parallelism controls are version-dependent as well. Snapshot creation and update depend on the configured mode and version: semantic diffs reveal changed expectations, obsolete snapshots can remain after a test is renamed or deleted, and Vitest by default writes no snapshots in CI, where missing, mismatched, and obsolete snapshots fail the run, so configuration that lets CI write them creates baselines nobody reviewed.
