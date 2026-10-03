---
title: Minitest
category: Test framework
x-claim-provenance:
- claim: assert_equal takes the expected value before the actual value, and assert_raises returns the matched exception so its message and attributes can be checked.
  source: https://docs.seattlerb.org/minitest/Minitest/Assertions.html
- claim: Runnable methods are randomized by default, parallelize_me! runs a class's tests in parallel, and i_suck_and_my_tests_are_order_dependent! forces ordered tests.
  source: https://docs.seattlerb.org/minitest/Minitest/Test.html
- claim: The minitest runner options include -s or --seed SEED, also settable through the SEED environment variable, -n or --name PATTERN and -e or --exclude PATTERN to filter on a regexp or string, and -v or --verbose for progress output.
  source: https://github.com/minitest/minitest/blob/master/README.rdoc
---

Minitest tests are `test_`-prefixed methods on `Minitest::Test` or `it` blocks under `Minitest::Spec`, with `setup` and `teardown` as lifecycle hooks. `assert_equal expected, actual` takes the expected value first, and `assert_raises` returns the captured exception for further assertions. Parameterized behavior is commonly written as one generated test method per case, with the case encoded in the method name so a failure stays identifiable. `Minitest::Mock` and `stub` provide test doubles, and an unmet mock expectation surfaces when the mock is verified.

Runner order and seed behavior depend on the version and configuration. When a run reports a reproducible seed, that seed can reproduce an order-dependent failure. `parallelize_me!` changes execution only where class state can tolerate parallelism.

A run can be narrowed with `ruby -Itest test/thing_test.rb -n test_name` or a `/pattern/`, or through the project's Rake task with `TEST=` and `TESTOPTS="-n /pattern/"`. `--verbose` adds progress output, which is useful only when that output is needed.
