---
title: MSTest
category: Test framework
x-claim-provenance:
- claim: MSTest test methods are public instance methods returning void, Task, or ValueTask, the last from MSTest 3.3, and async void test methods are to be replaced by async Task or async ValueTask.
  source: https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-mstest-writing-tests
  scope: Page dated 2026-09-02.
- claim: MSTest runs tests sequentially within each assembly by default, and parallelization is enabled through the assembly Parallelize attribute, runsettings, testconfig.json, or MSBuild properties.
  source: https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-mstest-writing-tests-controlling-execution
  scope: Page dated 2026-09-14.
- claim: RetryAttribute, introduced in MSTest 3.8, retries test methods that fail or time out, and the documentation advises addressing the root cause of flaky tests rather than relying on retries.
  source: https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-mstest-writing-tests-controlling-execution
  scope: Page dated 2026-09-14.
- claim: dotnet test --filter expressions support the =, !=, ~, and !~ operators, and MSTest supports the FullyQualifiedName, Name, ClassName, Priority, TestCategory, and Id properties.
  source: https://learn.microsoft.com/en-us/dotnet/core/testing/selective-unit-tests
  scope: Page dated 2026-07-22.
---

MSTest's attribute, assertion, data-source, and lifecycle forms depend on the referenced framework, adapter, and runner versions, and its expected-exception and asynchronous assertion APIs are its own rather than interchangeable with NUnit or xUnit forms. `TestContext` exposes runtime information where the configured version supports it, and asynchronous test methods return `Task` rather than `async void`.

Initialization and cleanup run at test, class, or assembly scope, so mutable state shared at a wider scope can couple tests. Concurrency is controlled through supported assembly attributes or run settings, and `Retry` exists only where the referenced MSTest version provides it. Narrow filtering comes from `dotnet test` or the configured runner, with filter and logger syntax that depends on the installed adapter and SDK.
