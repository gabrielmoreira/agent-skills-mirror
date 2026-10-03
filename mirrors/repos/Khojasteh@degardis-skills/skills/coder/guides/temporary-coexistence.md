---
title: Temporary coexistence
applicability:
- When old and new forms of one responsibility serve consumers side by side during a transition
---

Coexistence is justified only when consumers or stored state cannot move atomically; otherwise it is a second implementation to maintain. Define each stage of the transition and, for every stage, one authority per responsibility: reads, writes, configuration, generated output, conflict resolution, traffic, and reversal. Never allow two writable authorities without deterministic conflict semantics. State how synchronization, ordering, idempotency, retries, partial failure, and reconciliation work between the sides, the mixed-version limits, and the condition that ends coexistence.

Give every bridge — flag, adapter, shim, proxy, dual read or write, shadow path, synchronization, or fallback — a bounded surface, its supported consumers, an owner, an end condition, the evidence that allows its removal, and a control that prevents new consumers from adopting it. A bridge without a bounded consumer, end condition, and removal path is retained architecture, not a transition.

Before authority moves, reconcile divergence with checks that compare meaning — keys, invariants, aggregates, and samples selected for the invariants they cover — not only counts. State reversal per stage in terms of code, configuration, traffic, contracts, and data. A fallback is not rollback once state or ownership has diverged, and a code rollback is not recovery when state has advanced incompatibly; name forward repair where reversal is no longer safe.

The new side is not authoritative, and the transition is not complete, while the old side can still affect correctness. Each remainder that stays needs a supported consumer or an unfinished stage, an owner, and a removal condition.
