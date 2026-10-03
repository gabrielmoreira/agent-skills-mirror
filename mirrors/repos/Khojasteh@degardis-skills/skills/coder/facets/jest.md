---
title: Jest
category: Test framework
x-claim-provenance:
- claim: Native ECMAScript modules evaluate static imports before Jest can register a mock, unlike transformed CommonJS where Jest can hoist jest.mock calls.
  source: https://jestjs.io/docs/ecmascript-modules
---

Jest suites are built from `describe` and `test`, with `test.each` and an identifiable title template for cases, `beforeEach` and `afterEach` for lifecycle, and `expect(...).rejects` or `.toThrow` for expected failures. A specific matcher preserves the intended expectation better than `toBeTruthy` when the subject is an object, and fake timers with `jest.setSystemTime` control time deterministically without waiting on the wall clock.

Module mocking depends on the configured module mode and transforms. In transformed CommonJS-style modules Jest may hoist `jest.mock` above the imports, but native ECMAScript modules evaluate static imports before any mock is registered, so mocking there needs the ESM mocking path the resolved Jest version supports, applied before the module is loaded dynamically. Jest's module-registry reset and isolation APIs cover the cases where one test's imports must not affect another in the same file, and `restoreMocks`, `resetMocks`, or an explicit `afterEach` restore mocks without hand-maintained restoration state.

Running with `--randomize` and a fixed `--seed` exposes order dependence, and comparing against a serialized run through `--runInBand` or fewer `--maxWorkers` exposes concurrency effects. `--runTestsByPath <file>` and `-t <name pattern>` narrow a run, and `--onlyFailures`, `--bail`, and `--silent` constrain reruns and output further. Invoking Jest through the project's own script keeps its configured transforms and environment.

Snapshots are expectations with a lifecycle of their own. A `.snap` entry can outlive the test that reviewed it, which is why the summary reports obsolete snapshots after tests are deleted or renamed, and the semantic diff determines which of those entries are actually stale. `--updateSnapshot` rewrites snapshot state, while `--ci` fails instead of silently creating a missing snapshot.
