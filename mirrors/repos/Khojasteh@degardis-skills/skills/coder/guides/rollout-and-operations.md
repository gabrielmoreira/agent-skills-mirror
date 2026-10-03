---
title: Rollout and operations
applicability:
- When the order or stages by which a change reaches a running system can affect its correctness
- When the accepted operating contract includes continuity or recovery beyond a single deployment
x-claim-provenance:
- claim: Software engineering operations includes availability and continuity, capacity, backup and disaster recovery, failover, deployment/release engineering, rollback, and data migration.
  source: https://www.computer.org/education/bodies-of-knowledge/software-engineering/topics
---

Define every state the system can occupy during rollout and which versions can coexist; their authorities, synchronization, reconciliation, and reversal follow [[guide:temporary-coexistence]]. State which side answers at each stage and what happens when either side fails. Name the observation that advances, stops, or reverses each stage. A deployable artifact is not evidence that the deployed transition is safe.

Keep defaults backward compatible where the contract requires mixed versions. Permit a bridge only for a named stage and under the same coexistence contract.

Keep artifacts from both sides distinguishable and reproducible so the running side is identifiable without trusting a deployment log.

Where the accepted operating contract includes continuity beyond one deployment, establish the service objective and tolerated recovery time or data loss from project authority rather than inventing them. Identify the restart, failover, backup, restore, dependency, credential, and traffic assumptions that recovery needs. A backup is not recovery evidence until its required state can be restored, and a standby is not failover evidence until the relevant state, routing, permissions, and dependencies work together. Exercise the narrowest safe recovery path capable of settling the requirement, or leave the claim unverified; distinguish failover, data restore, forward repair, and deployment rollback because they recover different states.

Expose the smallest signal that distinguishes success, degradation, fallback use, divergence, and partial completion without disclosing sensitive material. Applying a rollout or operational change is externally visible work and requires authority separate from preparing it.
