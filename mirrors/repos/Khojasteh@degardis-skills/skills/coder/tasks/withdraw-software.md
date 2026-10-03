---
title: Withdraw an existing software feature or construct
cues:
- an existing software capability or construct should stop being available or supported, with nothing taking its place
goal: The requested capability or construct is withdrawn to the authorized degree, every affected surviving contract is reconciled, obsolete owned material is removed or deliberately retained for a stated compatibility reason, and current evidence establishes the resulting supported surface.
knowledge:
- authorized-software-surface
- project-grounding
- design-integrity
- change-scope
guides:
- change-contract
- user-interface-work
- design-selection
- failure-investigation
- defect-repair
- technology-change
- test-work
- existing-test-maintenance
- documentation-work
- source-comments
- documentation-evidence
- structural-cost
- structural-transformations
- abstraction-boundaries
- change-sites
- value-boundaries
- failure-behavior
- removal-and-compatibility
- data-and-state
- concurrency-and-resources
- security-boundaries
- rollout-and-operations
- interface-contracts
- dependency-and-artifact-integrity
- observability-and-diagnostics
- algorithmic-and-numeric-correctness
- commands-and-tooling
- workspace-integrity
- version-control
- work-slicing
handoffs:
- task: implement-change
  applicability:
  - When surviving consumers need new or changed behavior beyond the withdrawal's migration path, the requester authorized that change, and it is neither made nor pending on this route
---

This task owns withdrawal as the requested finished state. Do not treat removal as ordinary implementation with negative code: the work must establish what stops being supported, what must continue to work, and whether compatibility requires deprecation, migration, a transitional shim, or immediate absence.

Before editing, establish the withdrawal target, the authorized degree of removal, and the point after which use must fail or disappear if such a point exists. The surviving contract, its consumers, and any compatibility or migration promise are fixed under [[guide:change-contract]], and whether the behavior was published and which kinds of consumer can rely on it are established under [[guide:removal-and-compatibility]]. Search by behavior and public names over the mechanisms that bind consumers without a textual reference, so indirect ownership is not mistaken for dead code.

Choose the smallest coherent withdrawal that satisfies that boundary. Remove obsolete owners rather than leaving inert copies; a deprecated entry point, migration path, compatibility adapter, or tombstone that stays is coexistence under [[guide:temporary-coexistence]]. Reconcile consumers in dependency order; do not silently convert a removal request into replacement functionality or unrelated cleanup.

Derive completion evidence from the resulting contract; whether absence itself earns a maintained test follows [[guide:test-work]], and which existing tests are removed, revised, or retained follows [[guide:existing-test-maintenance]].

After focused evidence passes, reconcile the maintained surfaces whose truth changed, then review the final diff for accidental replacement behavior, orphaned compatibility code, stale mentions, and unrelated deletion. Report what is no longer supported, what remains compatible, any migration the reader must perform, and the evidence establishing both the withdrawal and the surviving surface.
