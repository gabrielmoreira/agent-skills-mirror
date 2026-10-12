---
title: Propose a software design
cues:
- how software, or a change to it, should be designed is asked
goal: A decision-ready design proposal gives whoever decides on it the recommended design, or the viable designs the evidence cannot separate, with the trade-offs and open questions that bear on the decision, is delivered in the response or as the design document the request asks for, and leaves every other project file unchanged.
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
---

A design request asks which design should be built and why, for whoever decides on it, not for the work to be ordered or carried out.

Establish the requested outcome, who decides on the design, the starting state that bears on it, and the facts still open. Inspect code, configuration, tests, history, platform constraints, and available tooling until every question that could change the choice of design is settled or stands open. The design request authorizes running a command whose effects stay confined to disposable output, and any other effect needs authority of its own.

Where the evidence separates one viable design from the rest, recommend it; where it does not, present each viable design with the fact or decision that would separate them and who supplies it, since a recommendation the evidence cannot carry reads to the decider as settled.

Write the proposal for whoever decides on it, who did not see the investigation, in the shape [[guide:document-types]] gives the type of design document the request names, such as a decision record, or a design proposal when it names none, whether it is delivered in the response or as the design document the request asks for.
