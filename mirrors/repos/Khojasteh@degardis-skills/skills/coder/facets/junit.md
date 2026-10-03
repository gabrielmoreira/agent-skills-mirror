---
title: JUnit
category: Test framework
x-claim-provenance:
- claim: JUnit Vintage provides a TestEngine for running JUnit 3 and JUnit 4 based tests on the JUnit Platform, and the Vintage engine is deprecated and meant only for temporary use while migrating tests.
  source: https://docs.junit.org/current/user-guide/
  scope: JUnit 6.1.3 user guide, read 2026-09.
- claim: Setting junit.jupiter.execution.parallel.enabled to true enables parallel execution, but test classes and methods still execute sequentially by default until an execution mode makes them concurrent.
  source: https://docs.junit.org/6.0.3/writing-tests/parallel-execution.html
  scope: JUnit 6.0.3 user guide.
- claim: MethodOrderer.Random orders methods pseudo-randomly with a default seed from System.nanoTime that is logged at CONFIG level, and a custom seed can be supplied through the junit.jupiter.execution.order.random.seed configuration parameter.
  source: https://docs.junit.org/current/api/org.junit.jupiter.api/org/junit/jupiter/api/MethodOrderer.Random.html
  scope: JUnit 6.1.3 API documentation.
---

JUnit's annotation and lifecycle semantics depend on the configured API and engine. Jupiter has its own lifecycle, parameterized-test, nesting, timeout, and temporary-directory APIs, while JUnit 4 has distinct lifecycle, runner, rule, and expected-exception forms. JUnit 4 and Jupiter tests can both remain discoverable when the Vintage engine, which JUnit deprecates as a temporary migration aid, or another bridge is configured, so which tests are discovered depends on the actual engine set rather than on the annotations in the source.

Where the configured assertion API returns the thrown exception, that object can carry further assertions. Named parameterized cases and grouped assertions identify failures better when later checks stay informative after an earlier one fails.

Parallel execution and ordering are engine and build configuration: in Jupiter, `junit.jupiter.execution.parallel.enabled` alone still runs tests sequentially until an execution mode makes them concurrent, and `MethodOrderer.Random` logs its default seed at `CONFIG` level and replays an order from `junit.jupiter.execution.order.random.seed`. Repetition, or a shuffled order with a recorded seed, can expose interference between tests. Narrow selection of a class or method comes from the project's configured build tool or console runner, whose syntax varies across installed Maven, Gradle, and console versions.
