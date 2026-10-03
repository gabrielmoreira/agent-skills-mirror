---
title: Observability and diagnostics
applicability:
- When telemetry or health signals affect behavior, evidence, or operations
x-claim-provenance:
- claim: Software engineering operations includes monitoring and operational evidence needed to run and troubleshoot software.
  source: https://www.computer.org/education/bodies-of-knowledge/software-engineering/topics
- claim: Logs, metrics, and traces are distinct telemetry signals whose semantics and correlation differ.
  source: https://opentelemetry.io/docs/concepts/signals/
---

Start from the decision the signal must support: what event or state occurs, who consumes it, what action they can take, and what absence, delay, duplication, or sampling would mean. Choose the signal whose semantics fit that question rather than emitting the same fact everywhere. A log records an event, a metric aggregates measurements, and a trace relates work across a request path; one cannot automatically substitute for another.

Define stable meaning before names and formatting. Specify the event or measurement, unit, status, severity where relevant, correlation context, timestamp or duration semantics, and the attributes needed to distinguish actionable cases. Reuse the project's established vocabulary and instrumentation path. Keep high-cardinality or unbounded values out of dimensions that retain per-value state unless the adopted telemetry system and requirement explicitly support them.

Treat telemetry as an outward data path. Exclude secrets and unnecessary personal or tenant data, preserve trust boundaries in propagated context, and respect established retention, access, sampling, and export rules. An identifier useful for debugging is not automatically safe to log or propagate. Audit evidence has a different integrity and access purpose from diagnostic logging; do not weaken one into the other for convenience.

Instrument at the owner of the state transition or boundary being observed so success, degradation, fallback, retries, cancellation, partial completion, and final failure cannot silently bypass the signal. Health, readiness, and liveness checks must answer the operational action that consumes them; a process that is alive is not necessarily ready to receive work, and a dependency outage is not necessarily a reason to restart the process.

Verify the signal together with the behavior it is meant to explain or guard. Exercise a representative success and material failure, confirm correlation across the relevant boundary, and check that the emitted values distinguish the states the operator or automated consumer needs. Sampling or filtered retention means absence of a telemetry record cannot by itself establish that the underlying event never occurred. Thresholds and alerts come from accepted objectives, budgets, baselines, or demonstrated failure conditions rather than arbitrary constants.
