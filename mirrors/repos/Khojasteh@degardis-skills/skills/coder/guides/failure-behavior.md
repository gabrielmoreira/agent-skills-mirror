---
title: Failure behavior and recovery
applicability:
- When correctness depends on what an operation does when it fails
- When an operation acquires a resource that must be released
---

For each material failure point, establish when it can occur, what has already changed, how the caller or operator recognizes it, and the remedy available to them. Surface exactly the context that remedy needs while preserving the cause and withholding secrets or accidental implementation detail from untrusted callers. Distinguish validation, deferred, streamed, background, partial, and lost-acknowledgement failures when their remedies differ. Use the ecosystem's established failure mechanism and handling boundary; do not introduce parallel return codes, sentinel values, or logs that callers cannot act on.

Define acquisition, cleanup, and retained state across success, failure, timeout, cancellation, and retry. Check handles, sockets, connections, pooled clients, locks, child processes, subscriptions, timers, and temporary paths where applicable, including cleanup skipped by the success path; first establish what the language, framework, or scope already releases. Leave effects complete or undone where the owning system permits it, and verify cleanup and externally visible failure effects. Preserve the originating failure when cleanup also fails.

Make repeated effects safe only through a demonstrated idempotency or deduplication mechanism. Bound retries, waiting, backoff, buffering, per-item calls, result sets, uploads, pages, caller-sized collections, input-driven growth, and recursion from an established requirement or measured constraint rather than an invented constant. For an input-driven risk, name a reachable size that encounters a timeout, pool, memory, or queue limit; do not report an abstract timeout or faster alternative without the dependency, caller effect, and evidence.

Choose recovery, compensation, rollback, or forward repair from the owning system's actual guarantees. Do not claim atomicity, reversibility, or retry safety from control flow alone; verify the boundary that commits the effect and execute material failure paths rather than calling them designed from inspection alone. Do not swallow a failure, return ambiguous success, replace the cause with a broad substitute, or collapse failures whose remedies differ. Add a timeout, retry, circuit breaker, or other control only for an evidenced failure surface, and state the dependency and behavior it protects.
