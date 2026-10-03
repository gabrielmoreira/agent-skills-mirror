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
- task: withdraw-software
  applicability:
  - When the change requires retiring an existing capability beyond removing what the change made stale, the requester authorized that withdrawal, and it is neither carried out nor pending on this route
---

This task owns a requested addition or change whose finished state is new or revised software behavior. Diagnosis, design, implementation, verification, test maintenance, documentation, migration, and reconciliation are stages only when they serve that outcome.

Before editing, establish the observable outcome, acceptance evidence, authorized write surface, relevant repository instructions, adopted tools, current behavior, existing workspace changes, and every affected public, persisted, security, or operational boundary. Diagnose a reported defect to a demonstrated cause. When the request leaves this work to find the defects it fixes, admit each candidate under [[principle:finding-evidence]] before editing for it, and change nothing for a candidate that fails it. For an addition, migration, or restructuring, establish the consumers and behavior that must remain. A request only for tests changes no production behavior to make a test pass.

Settle every material design choice before editing, then make the change, splitting large work into independently verifiable units under [[guide:work-slicing]].

Verify each unit, and then the combined change, against its acceptance criteria. After they pass, review the complete final diff for unintended movement, temporary artifacts, stale comments or documentation, missed consumers, and remaining compatibility or migration work.

Report the behavior or project state now delivered, the decisive verification, and any action the reader must take. Put blockers, compatibility breaks, migrations, security effects, skipped material checks, and residual risks beside the claim they qualify.
