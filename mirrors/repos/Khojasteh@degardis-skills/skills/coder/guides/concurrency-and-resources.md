---
title: Concurrency and resources
applicability:
- When more than one operation can be in flight at once and correctness depends on how they interact
x-claim-provenance:
- claim: Software design and construction treat concurrency, distribution, middleware, fault tolerance, and distributed/cloud behavior as separate correctness concerns.
  source: https://www.computer.org/education/bodies-of-knowledge/software-engineering/topics
---

Name ownership, lifetime, allowed overlap, ordering, and the event that completes or cancels each operation. Distinguish thread safety, process safety, distributed coordination, and event-loop ordering; evidence for one does not establish another.

Protect invariants at the owner of shared state, and define duplicate, stale, out-of-order, and partial-completion behavior for overlapping or retried operations. Bound queues and concurrency from project requirements or measured capacity rather than an invented constant.

Across a process, host, broker, or network boundary, establish the delivery and ordering guarantees the actual transport provides rather than assuming exactly-once or reliable request/response behavior. Define behavior for disconnection, timeout after an unknown commit state, duplicate or replayed delivery, partition or stale reads, clock or lease assumptions, retry amplification, and consumer restart where those states are reachable. State the consistency or staleness the contract permits and the reconciliation or deduplication mechanism that restores an invariant. A local lock, transaction, or event-loop guarantee does not extend across that boundary unless the remote system explicitly provides it.

Propagate cancellation only across work the caller owns. Idempotency of repeated effects, and acquisition, release, and retained state across success, failure, timeout, and cancellation, follow [[guide:failure-behavior]]. Verification must exercise the actual scheduler, resource, or boundary when a substitute cannot reproduce the relevant ordering or lifetime.
