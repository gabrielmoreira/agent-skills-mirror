---
title: Investigate the cause of a software problem
cues:
- the cause of a problem in software, or in a check or operation run on it, is asked
goal: The reported symptom has a supported causal explanation at the first demonstrated divergence, or a bounded account of what remains unknown and the evidence needed next, with no project source changed.
knowledge:
- authorized-software-surface
- project-grounding
guides:
- user-interface-work
- failure-investigation
- performance-evidence
- performance-comparisons
- performance-cost-domains
- technology-change
- test-work
- existing-test-maintenance
- documentation-evidence
- structural-transformations
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
handoffs:
- task: implement-change
  applicability:
  - When the cause is established, the requester authorized repairing it, the repair changes anything beyond reader-facing project text, and it is neither carried out nor pending on this route
- task: document-software
  applicability:
  - When the cause is established, the requester authorized repairing it, the repair changes only reader-facing project text, and it is neither carried out nor pending on this route
---

Diagnosis is the deliverable. Do not turn a likely fix into an edit, and do not treat a successful workaround as proof of cause.

Define the reproduction first, as [[guide:failure-investigation]] describes it. Start from supplied failures and existing artifacts, then search for the symbols and boundaries they name. Read the implicated path before broadening the search. Run a focused reproduction only when it is safe, authorized, and able to distinguish competing explanations.

Trace the symptom to the first state or decision that departs from the established contract, and report the cause at the layer where that departure occurs: a test, harness, environment, or configuration cause is reported as such, not as a product defect.

Report the established cause and its location, or the narrowest supported explanation with its confidence and remaining uncertainty. Name the evidence that ruled out material alternatives, the surface reached, and the next check that would settle any blocking unknown. Proposed repairs remain clearly proposed.
