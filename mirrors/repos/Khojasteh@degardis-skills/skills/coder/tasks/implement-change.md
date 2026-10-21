---
title: Implement a software change
cues:
- an existing software project should be changed
goal: The authorized software change is present in the requested surface, its affected contracts and state are reconciled, and proportionate current-run evidence verifies the requested outcome, or the result is reported at the exact incomplete state with no unsupported completion claim.
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
- code-style
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
- change-descriptions
- work-slicing
handoffs:
- task: withdraw-software
  applicability:
  - When the change requires retiring an existing capability beyond removing what the change made stale, the requester authorized that withdrawal, and it is not yet carried out
---

This task owns a requested change to an existing software project, whether or not its finished state changes behavior. Diagnosis, design, implementation, verification, test maintenance, documentation, migration, and reconciliation are stages only when they serve that outcome.

Before editing, establish the observable outcome, acceptance evidence, authorized write surface, adopted tools, current behavior, existing workspace changes, and every affected public, persisted, security, or operational boundary. Diagnose a reported defect to a demonstrated cause. When the request leaves this work to find the defects it fixes, admit each candidate under [[principle:finding-evidence]] before editing for it, and change nothing for a candidate that fails it. For an addition, migration, or restructuring, establish the consumers and behavior that must remain.

Settle every material design choice before editing, then make the change, splitting large work into independently verifiable units under [[guide:work-slicing]].

Verify each unit, and then the combined change, against its acceptance criteria. Passing checks establish the behavior they exercise, not that the change is coherent, so after they pass, and before reporting the change complete, review the combined change as a whole, including increments of it already reported complete to earlier requests. Confirm that each premise it retires has been followed to every surface resting on it; that nothing the change superseded survives beside what replaced it, such as a mechanism, a second representation of one fact, or state kept for a superseded design; and that no unintended movement, temporary artifact, stale comment or documentation, missed consumer, or unfinished compatibility or migration work remains. The review's result is a disposition for each problem it finds: corrected, retained with a stated reason, or reported as open beside the claim it limits. Until each has one, the review is not done, whatever has been recorded about it.

Report the behavior or project state now delivered, any premises the change retired and how the material resting on each was reconciled, the decisive verification, and any action the reader must take. Put blockers, compatibility breaks, migrations, security effects, skipped material checks, and residual risks beside the claim they qualify.
