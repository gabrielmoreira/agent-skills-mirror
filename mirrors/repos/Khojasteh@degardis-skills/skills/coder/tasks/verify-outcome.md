---
title: Verify a software outcome
cues:
- whether existing software, or a claim about it, passes a check or meets a criterion as it stands is asked
goal: The named claim has a pass, fail, or unverified verdict tied to criteria fixed before execution and to current evidence from the identified project state, with no project source changed.
knowledge:
- authorized-software-surface
- project-grounding
guides:
- change-contract
- user-interface-work
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
handoffs:
- task: investigate-problem
  applicability:
  - When the verdict is a failure, the requester asked why it fails, and its cause is not yet established
- task: implement-change
  applicability:
  - When the verdict is a failure of the subject, the requester authorized fixing it, the fix changes anything beyond project documentation, and it is not yet made
- task: document-software
  applicability:
  - When the verdict is a failure of the subject, the requester authorized fixing it, the fix changes only project documentation, and it is not yet made
---

This task may run checks but does not repair their failures. Fixing the subject, weakening an expectation, regenerating an accepted baseline, or editing configuration to obtain a pass would replace the thing being verified.

Identify the exact claim, criteria, project revision, configuration, and environment before choosing evidence. Recover expected results from the independent sources that define the contract. If the claim has no decidable criterion, report that gap before executing evidence that cannot settle it.

Then run the adopted check that can answer the claim; the request for a verdict authorizes one whose effects stay confined to disposable output, and any other effect needs authority of its own. Classify a failure under [[principle:software-evidence]] before attributing it to the subject: an invalid harness, an unavailable dependency, or a failure that predates what the claim covers is reported as what it is, and only evidence that the claim itself is false yields a failing verdict.

Give one verdict at the width the evidence supports. A pass names the claim and decisive evidence. A failure names the violated criterion and observed result. An unverified verdict names the unavailable or inconclusive evidence and the one check that would settle it.
