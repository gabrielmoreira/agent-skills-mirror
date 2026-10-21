---
title: Plan software work
cues:
- a plan for work that would build, change, or remove software or its documentation is asked
- what building, changing, or removing software or its documentation would take is asked
goal: A decision-ready plan connects the requested outcome to the available starting state, ordered implementation units, verification evidence, open decisions, and explicit blockers, sizes its units when the request asks what the work would take, is delivered in the response or as the plan document the request asks for, and leaves every other project file unchanged.
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
- performance-evidence
- performance-comparisons
- technology-change
- implementation-modernization
- test-work
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
  - When the requester authorized carrying out the plan, its finished state changes existing software beyond project documentation and does more than withdraw a capability, and the plan is not yet carried out
- task: create-product
  applicability:
  - When the requester authorized carrying out the plan, its finished state is a new product, and the plan is not yet carried out
- task: withdraw-software
  applicability:
  - When the requester authorized carrying out the plan, its finished state is a withdrawal, and the plan is not yet carried out
- task: document-software
  applicability:
  - When the requester authorized carrying out the plan, its finished state changes only project documentation, and the plan is not yet carried out
---

A plan request asks for decisions and sequence, not speculative edits or a patch.

Establish the requested observable outcome, the available starting state that bears on it, the authorized surface or destination, and the facts still open. Inspect code, configuration, tests, history, platform constraints, and available tooling until every design-driving question is settled or stands as an explicit decision or blocker. The plan request authorizes running a command whose effects stay confined to disposable output, and any other effect needs authority of its own.

Put the requester-owned choices the investigation leaves open to the requester together before settling the design, even those the plan could carry: a requester asked nothing can take the plan as settled and pass it on unread, so settling the design is not independent work for these choices to wait behind. Offer to leave each one open for the plan to carry at the work units it governs, except one without which no plan can be written. Put the choices that surface only during design the same way before the plan is delivered, and any the design cannot proceed without as soon as it surfaces.

Settle the design and the change's contract before ordering the plan, and order it around the smallest coherent change that realizes them. For a new product, separate requester- and platform-fixed decisions from implementation defaults. For each work unit, name its purpose, inputs, affected contracts or state, dependencies, the facts it must establish before acting, each open decision or missing authority that blocks it and who settles it, its completion evidence, and the next unit that consumes it. Put discovery before a unit only when the answer could change that unit.

When the request asks what the work would take, the plan's units, dependencies, open decisions, and blockers are its scope. Size each unit against the others from what drives its cost here, such as the change sites it touches, the consumers and state it must reconcile, and the evidence it must produce, and name the open decision or blocker that could change that size. A duration or effort figure depends on who does the work and at what rate, which the project's code does not establish: give one only from capacity and rate the requester supplies, since a figure the evidence cannot carry reads to the decider as a commitment.

Finish with an ordered plan that another agent can execute without reconstructing the investigation: the outcome it reaches, the starting state it assumes, then its units in execution order. What only the requester needs, to judge or decide on the plan rather than carry it out, belongs in the response that delivers it, outside the plan.
