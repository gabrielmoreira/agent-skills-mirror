---
title: Pest
category: Test framework
x-claim-provenance:
- claim: --retry reorders the suite to run previously failed tests first and otherwise runs it as usual, --dirty runs only tests with uncommitted changes according to Git and always treats tests written in PHPUnit syntax as dirty, --filter matches a regular expression against test descriptions, --group selects groups, and --bail stops at the first failure or error.
  source: https://pestphp.com/docs/filtering-tests
  scope: Pest documentation, read 2026-09.
- claim: pest()->extend() with in() in Pest.php associates a base test case class with a folder or the whole suite, changing what $this refers to in its tests.
  source: https://pestphp.com/docs/configuring-tests
  scope: Pest documentation, read 2026-09.
- claim: Datasets attach to a test through ->with(), and a dataset key, when present, is used in the generated test description.
  source: https://pestphp.com/docs/datasets
- claim: --parallel runs tests in parallel, and --compact replaces the default result output with a compact format.
  source: https://pestphp.com/docs/cli-api-reference
---

Pest test files define closure-based tests through `test(...)` or `it(...)` and assert through the `expect()` chain. They are not PHPUnit test classes, so PHPUnit attributes placed in the file do not apply as class metadata. Pest provides `->group()`, `->skip()`, and `->throws()` chains, `pest()->extend()` or `uses()` in `Pest.php` binds a base test case, and `beforeEach`, not a constructor, is the per-test setup mechanism. Parameterized cases come from `->with([...])` or named datasets, whose case identity can appear in failures.

Pest runs on PHPUnit, so PHPUnit's isolation semantics still apply to static state, globals, the container, and database state between tests. `--parallel` changes concurrency and can help expose interference, while `--retry` only reorders the suite to run previously failed tests first. `--filter`, `--group`, or `--dirty`, which always counts PHPUnit-syntax tests as dirty, narrows a run, `--bail` limits later failures, and `--compact` reduces output.
