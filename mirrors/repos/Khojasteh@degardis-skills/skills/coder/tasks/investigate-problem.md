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
- technology-change
- test-work
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
  - When the cause is established, the requester authorized repairing it, the repair changes anything beyond project documentation, and it is not yet carried out
- task: document-software
  applicability:
  - When the cause is established, the requester authorized repairing it, the repair changes only project documentation, and it is not yet carried out
---

Do not treat a successful workaround as proof of cause.

Define the reproduction first, as [[guide:failure-investigation]] describes it. Start from supplied failures and existing artifacts, then search for the symbols and boundaries they name. Read the implicated path before broadening the search. Run a focused reproduction only when it is safe and can distinguish competing explanations; the request for the cause authorizes one whose effects stay confined to disposable output, and any other effect needs authority of its own.

Trace the symptom to the first state or decision that departs from the established contract, and report the cause at the layer where that departure occurs.

Report the established cause and its location, or the narrowest supported explanation with its confidence and remaining uncertainty. Name the evidence that ruled out material alternatives, the surface reached, and the next check that would settle any blocking unknown. Proposed repairs remain clearly proposed.
