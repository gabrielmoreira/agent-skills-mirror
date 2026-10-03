---
title: Swift Testing
category: Test framework
x-claim-provenance:
- claim: A Swift Testing suite that needs deinitialization for teardown must be a class or an actor rather than a structure.
  source: https://developer.apple.com/documentation/testing/migratingfromxctest
- claim: Swift Testing and XCTest can coexist in one test target, while interoperability behavior depends on the configured toolchain.
  source: https://developer.apple.com/documentation/testing/migratingfromxctest
---

In Swift Testing, `@Test` denotes a test and `@Suite` a group; `#expect` records a check after which the test continues, `#require` represents a prerequisite that must hold for the remainder, and `#expect(throws:)` represents an expected failure. `@Test(arguments:)` supplies parameterized cases and reports each case separately, so case identity needs no hand-written loop. Suite setup can live in `init` and teardown in `deinit`, and because each test receives a fresh suite instance, a suite that needs `deinit` must be a reference type such as a class or actor.

Swift Testing and XCTest can coexist in one target, but helper behavior across that boundary depends on the configured interoperability mode and the resulting issue severity, and one assertion API per test avoids mixed failure semantics. A known failure uses the resolved toolchain's known-issue mechanism when one is available; without it, the failure remains visible rather than becoming a disabled test.

Tests are expected to be independent of execution order and shared mutable state unless the resolved runner configuration establishes an ordering or serialization contract, and parallelism defaults are toolchain and configuration facts rather than assumptions. The `.serialized` trait is available for suites or parameterized tests whose shared state requires serialization. Narrow selection depends on the configured Swift test runner and toolchain: its own help or matching toolchain documentation defines the supported selector syntax.
