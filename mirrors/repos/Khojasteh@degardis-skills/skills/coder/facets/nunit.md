---
title: NUnit
category: Test framework
x-claim-provenance:
- claim: Inside Assert.Multiple, NUnit stores the failures encountered in the block and reports all of them together when the block exits.
  source: https://docs.nunit.org/articles/nunit/writing-tests/assertions/multiple-asserts.html
- claim: RetryAttribute reruns a test on assertion failure up to a maximum count that is the total number of attempts, so Retry(1) does nothing, and a test with an unexpected exception is not retried unless that exception type is listed in RetryExceptions.
  source: https://docs.nunit.org/articles/nunit/writing-tests/attributes/retry.html
- claim: NUnit tests are not parallel by default, and ParallelizableAttribute marks an assembly, fixture, or method as eligible for parallel execution.
  source: https://docs.nunit.org/articles/nunit/writing-tests/attributes/parallelizable.html
- claim: The NUnit console runner's --where option selects tests by an expression over names, classes, methods, categories, or properties, and its --seed option sets the random seed used to generate test cases.
  source: https://docs.nunit.org/articles/nunit/running-tests/Console-Command-Line.html
- claim: dotnet test --filter FullyQualifiedName~value selects NUnit tests whose fully qualified name contains the value, and NUnit supports the FullyQualifiedName, Name, Priority, TestCategory, Category, and Property filter properties.
  source: https://learn.microsoft.com/en-us/dotnet/core/testing/selective-unit-tests
  scope: Page dated 2026-07-22.
---

NUnit defines `[Test]`, `[TestCase]`, `[TestCaseSource]`, `[Values]`, and `[Combinatorial]` for cases and `[SetUp]`, `[TearDown]`, `[OneTimeSetUp]`, and `[OneTimeTearDown]` for lifecycle. These attributes are NUnit's own: other .NET frameworks do not define the same set, and xUnit's fixture interfaces are not NUnit lifecycle constructs. Its constraint model asserts through `Assert.That`, expected failures are expressed with `Throws.TypeOf<T>()` or `Assert.ThrowsAsync<T>`, and `Assert.Multiple` groups related checks when later assertions stay informative.

The console runner's `--seed` sets the seed for generated test cases, so it reproduces a failure that depends on generated data rather than on test order, while `[Parallelizable]` and `[NonParallelizable]` change concurrency without encoding a test order. `[Repeat]` and `[Retry]` rerun a test; `[Retry]` counts total attempts and reruns only assertion failures unless `RetryExceptions` names other exceptions. A run can be narrowed with `dotnet test --filter "FullyQualifiedName~Class.Method"` or the NUnit console runner's `--where` expression, and minimal console logging keeps the result surface compact.
