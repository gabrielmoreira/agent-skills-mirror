---
name: performance-test-plan
description: Plan performance tests for frontend, backend, APIs, databases, jobs, and releases. Use when Codex is asked to define load tests, latency checks, Core Web Vitals, throughput, memory, query performance, or performance regression gates.
license: MIT
---

# Performance Test Plan

## Core Workflow

1. Identify performance goal, user journey or endpoint, expected load, baseline,
   environment, and release risk.
2. Choose metrics: latency percentiles, throughput, error rate, resource use,
   Core Web Vitals, query time, queue lag, or job duration.
3. Define test setup, data, traffic model, warmup, duration, and pass/fail
   thresholds.
4. Include profiling and observability needed to diagnose failures.
5. Separate synthetic, local, staging, and production-safe checks.
6. Add regression gates and follow-up tuning options.

## Safety Rules

- Do not run load tests against production without explicit approval and a safe
  window.
- Do not invent baseline numbers or capacity claims.
- Verify current platform-specific performance metrics from official docs when
  exact definitions matter.

## Deliverable Shape

For performance test plans, provide:

- Target and goal
- Metrics and thresholds
- Environment and data
- Traffic model
- Test steps
- Observability and profiling
- Regression gate
- Risks and follow-up

## References

- Read `references/performance-test-plan-checklist.md` when planning
  performance validation.
