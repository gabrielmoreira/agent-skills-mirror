---
title: XCTest
category: Test framework
x-claim-provenance:
- claim: With XCTExpectFailure a test executes normally but its failure is reported as expected, and under the default strict behavior a call that catches no failure generates a distinct unmatched expected failure.
  source: https://developer.apple.com/videos/play/wwdc2021/10207/
  scope: WWDC21 session Embrace Expected Failures in XCTest.
- claim: xcodebuild -test-iterations repeats tests a fixed number of times and combines with -run-tests-until-failure, which repeats until a failure, or -retry-tests-on-failure, which retries until success up to the maximum, and these flags override test plan settings.
  source: https://developer.apple.com/videos/play/wwdc2021/10296/
  scope: WWDC21 session Diagnose unreliable code with test repetitions.
---

XCTest tests are `test`-prefixed methods on `XCTestCase` subclasses, with `setUp`, `tearDown`, their `async throws` forms, and `addTeardownBlock` providing lifecycle cleanup. Specific assertions such as `XCTAssertEqual` and `XCTAssertThrowsError`, `XCTUnwrap` for checked unwrapping, and expectations with `fulfillment(of:)` for asynchronous completion avoid fixed sleeps, and `XCTExpectFailure` records a known failure without disabling the test and, under its default strict behavior, fails once that failure stops occurring. XCTest, unlike Swift Testing, parameterizes by iterating over cases inside a test, with the case included in assertion messages so a failure remains identifiable.

`-test-iterations <n>` with `-run-tests-until-failure` can expose flake, and disabling parallel testing can reveal whether a failure correlates with concurrency, while `-retry-tests-on-failure` retries until success up to the configured maximum. `xcodebuild test -only-testing:Target/Class/testMethod` or `swift test --filter <pattern>` narrows a run, and `-quiet` reduces build-log noise without changing the selected tests.
