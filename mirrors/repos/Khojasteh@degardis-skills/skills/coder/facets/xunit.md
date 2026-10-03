---
title: xUnit.net
category: Test framework
x-claim-provenance:
- claim: VSTest and xUnit.net v3 under Microsoft Testing Platform expose different command-line filtering interfaces.
  source: https://xunit.net/docs/getting-started/v3/microsoft-testing-platform
  scope: xUnit.net v3 with Microsoft Testing Platform.
- claim: xUnit.net v3 4.0 adds parallel mode all, in which tests can run concurrently regardless of collection, and adds corresponding runner parallel-mode controls.
  source: https://xunit.net/docs/running-tests-in-parallel
  scope: xUnit.net v3 runner 4.0 parallel-mode behavior.
---

In xUnit.net, `[Fact]` denotes a single case, while `[Theory]` with `[InlineData]`, `[MemberData]`, or `[ClassData]` supplies parameterized cases. `Assert.Throws<T>` and `Assert.ThrowsAsync<T>` return the captured exception, so assertions can examine the exception rather than only the fact that one was raised. Setup, teardown, fixture, shared-context, and cancellation hooks vary by major version, and the resolved version's contract together with the project's existing tests establishes which forms are available. Asynchronous cleanup and timeout cancellation use hooks exposed by the resolved framework and runner; cancellation signals can propagate into code under test where the called APIs accept them, and cleanup remains part of the observable failure and timeout contract.

Collection and parallelism semantics depend on the resolved version, the runner, and the effective parallel mode, so collection membership is not sufficient evidence of serialization across every supported runner and mode combination, and runner-supported isolation controls establish shared-state behavior more directly than added sleeps. The parallel mode, algorithm, and thread limits a runner supports can change concurrency for diagnosis. Method, class, trait, or query filtering depends on the configured runner and resolved version, and because VSTest and Microsoft Testing Platform expose different interfaces, the runner's help or matching first-party documentation establishes the real selector contract.
