# Configuration

> Configuration and runner scripts are repository-owned. Add or migrate config only for the requested behavior.

- Keep project-specific environment and setup ownership. Use `test.projects` for distinct projects and give each a
  stable name; a project container does not run tests itself. Do not change a suite-wide environment for one exception.
- Keep aliases consistent with TypeScript and Vite resolution; aliases do not repair arbitrary externalized
  dependencies.
- Setup files are for truly suite-wide polyfills, matcher registration, cleanup, and mocks. Keep scenario data and heavy
  initialization in owned fixtures or tests.
- Coverage is opt-in. When requested, specify the intended source set and retain repository thresholds; do not use a
  provider change or lower threshold to hide a bad include/exclude set.
- For v4 migration, replace removed workspace/match-glob and worker settings with the documented project/worker model;
  `coverage.all` and the `basic` reporter are gone, `verbose` is flat, and browser APIs come from `vitest/browser`.
  Check the installed version's [migration guide](https://vitest.dev/guide/migration.html) rather than carrying shims.

Use repository reporter conventions. Otherwise prefer minimal agent-oriented output: Vitest 4.1 introduced
`--reporter=agent`; current versions call it `minimal` and retain `agent` as an alias. Use automatic agent detection
when available, and check the installed version's [reporter documentation](https://vitest.dev/guide/reporters.html)
before passing a flag. See [configuration](https://vitest.dev/config/file),
[projects](https://vitest.dev/config/projects), and [aliases](https://vitest.dev/config/alias).
