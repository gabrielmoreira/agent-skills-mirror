---
title: Performance evidence
applicability:
- When a performance or resource-cost measure is part of the requested outcome
- When a claim states an effect on a performance or resource-cost measure
---

Define the metric, workload, scale, environment, configuration, sample method, natural variation, minimum worthwhile effect, and every existing budget, service objective, or contractual limit before measuring. Capacity and tail behavior require offered load and concurrency to be stated; a single-operation timing cannot establish them.

Name the statistic the outcome depends on, such as a tail percentile, sustained throughput, peak footprint, cold start, transferred size, or unit cost. Make the workload representative in input shape, scale, state, concurrency, and lifecycle, including the common case and any boundary or high-load case the outcome depends on, and state what production dimensions it misses. If a representative input is unavailable, label any synthesized or sampled workload as a proxy, state how it was derived and what would validate it, and do not claim a representative result from it. Do not measure against a default invented for an indispensable missing outcome, workload, environment, guardrail, or worthwhile effect.

Use existing telemetry or measurements first, then a focused profile, trace, plan, counter, or benchmark that can attribute the dominant cost to one of the resource domains in [[guide:performance-cost-domains]].

Locate the path or bounded set owning the largest material share of the resource named by the outcome, not the first code that looks expensive. Account for sampling bias, instrumentation overhead, missing spans, and aggregation that can hide a dominant tail. When representative measurement is unavailable, keep the causal proxy, its claim limits, and the workload and environment needed to validate it; code shape or a familiar optimization target does not establish cost.

Establish the layer that owns the cost before choosing a change. Common, non-exhaustive candidates are the implementation, a correctness defect, environment contention, configuration, a dependency, the data shape, an external system, and the measurement itself. Suspect the instrument when the reported cost is implausible for the work. When a lower layer owns the resource use, separately test whether this project's call frequency, transferred volume, resource lifetime, or requested buffering owns a material share; neither stopping at the dependency boundary nor compensating downstream establishes the cause. Report a defect, misconfiguration, saturated dependency, or contended environment as such rather than absorbing it into an optimization.

Make one falsifiable optimization hypothesis before editing: the causal cost, the mechanism the change alters, the predicted effect on the primary metric, possible regressions, and the comparable result that would disprove it. Change one causal factor at a time when practical. Do not bundle changes beyond attribution, apply a familiar optimization before its mechanism owns the cost, or add speculative structure, dependency churn, or a benchmark-only fast path in place of a hypothesis.

Settle independently grounded correctness checks and resource guardrails before editing, treating documented timing, capacity, ordering, and resource guarantees as contract. The measurement proving lower cost cannot also prove that required work still happened; do not gain speed by weakening an assertion, skipping validation or work, loosening a tolerance, returning an incomplete result, or changing values, failures, effects, ordering, or compatibility. When optimizing a test suite, preserve behavioral coverage, independent oracles, determinism, isolation, diagnostics, and the required test levels; do not delete, disable, or merge tests merely to reduce suite duration.

Compare the final state with the baseline under the same material conditions. Retain a change only when [[guide:performance-comparisons]] credits its effect, correctness evidence passes, and the tradeoff is acceptable. Quantify any cost moved to another metric, path, system, team, or future maintainer where possible, and obtain approval when it exceeds a budget or changes a contract. Otherwise remove the change and report the attempted effect as unproved or insufficient; preserve failed or inconclusive findings only when they change what should be tried or avoided next.

Generating load, profiling a shared or live system, raising production diagnostics, or incurring spend requires separate bounded authority.
