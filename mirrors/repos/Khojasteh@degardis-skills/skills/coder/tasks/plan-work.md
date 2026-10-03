---
title: Plan software work
cues:
- a plan for work that would build, change, or remove software or its documentation, or what that work would take, is asked
goal: A decision-ready plan connects the requested outcome to the available starting state, ordered implementation units, verification evidence, open decisions, and explicit blockers, is delivered in the response or as the durable record or document the request asks for, and leaves every other project file unchanged.
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
- performance-cost-domains
- technology-change
- implementation-modernization
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
  - When the requester authorized carrying out the plan, its finished state changes existing software beyond reader-facing project text and does more than withdraw a capability, and the plan is neither carried out nor pending on this route
- task: create-product
  applicability:
  - When the requester authorized carrying out the plan, its finished state is a new product, and the plan is neither carried out nor pending on this route
- task: withdraw-software
  applicability:
  - When the requester authorized carrying out the plan, its finished state is a withdrawal, and the plan is neither carried out nor pending on this route
- task: document-software
  applicability:
  - When the requester authorized carrying out the plan, its finished state changes only reader-facing project text, and the plan is neither carried out nor pending on this route
---

A plan request asks for decisions and sequence, not speculative edits or a patch, so a requested durable plan, such as a plan file or design record, is the only project material it may write.

Establish the requested observable outcome, the available starting state that bears on it, the authorized surface or destination, and the facts still open. Read the applicable instructions before existing project or starter material, then inspect code, configuration, tests, history, platform constraints, and available tooling until every design-driving question is settled or stands as an explicit decision or blocker. Do not run a command merely to make the plan look verified; run one only when it is authorized and its result changes the design.

Settle the design and the change's contract before ordering the plan, and order it around the smallest coherent change that realizes them. For a new product, separate requester- and platform-fixed decisions from implementation defaults. For each work unit, name its purpose, inputs, affected contracts or state, dependencies, completion evidence, and the next unit that consumes it. Put discovery before a unit only when the answer could change that unit. Keep migrations, compatibility work, test changes, documentation changes, and rollout steps inside the same plan when the requested outcome requires them.

Finish with an ordered plan that another agent can execute without reconstructing the investigation. Separate settled decisions from assumptions and requester-owned choices. State what was reached, what was not inspected, the evidence the executing work must obtain, and every missing fact or authority that blocks a unit.
