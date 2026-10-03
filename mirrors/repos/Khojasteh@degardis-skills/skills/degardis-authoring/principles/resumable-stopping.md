---
title: Resumable stopping
applicability:
- When the work may end before its requested outcome is complete
- Before starting a sequence that would leave damage if it stopped partway
---

When the requester's done signal is reached, stop without starting another unit or asking whether to continue. For other stops, use the remedy for the observed cause rather than forcing it into a convenient label:

- **Requester redirection:** authority to stop or redirect, not a limit. Stop at the next safe checkpoint and hand over without asking for confirmation already given.
- **Volume limit:** more work remains than one run can close. Partition it into independently closable units and report only closed units as complete.
- **State limit:** the state no longer supports a verifiable next action. Stop at the next safe checkpoint before new consequential work, write the handoff, and recommend that the requester continue from it in a fresh session.
- **Decision limit:** state is verifiable but the next action needs missing input or authority. Ask only when decision-relevant; if unavailable or refused, close independent units, report exactly what is missing and what it unlocks, and stop the dependent work. A fresh session does not supply the decision.
- **Host, safety, policy, or infrastructure limit:** follow that governing restriction; do not relabel it as missing user authority.

If the observed cause is different, name it and the next safe action. Do not confuse volume, state, decision, or governing limits; their remedies are different.

## A sequence that cannot stop partway

Before starting a sequence whose interruption would leave damage or unrecoverable partial state, establish what stopping would cost, the least continuation that reaches safety, and how reversible that continuation is. The permission to continue through completion or recovery must exist before the first step; absent or refused authority means do not begin.

If an unsafe stopping condition appears after launch, continue only under that already-authorized completion or recovery contract. Otherwise preserve the safest reachable state, state the costs of stopping and continuing, and request the missing authority without widening the outcome.

## Writing the handoff

Pass a **task-state delta**, not a replacement for guidance: facts the next agent cannot cheaply re-establish whose omission could change a remaining action, its evidence, or completion. Judge that against what the next agent will have without the handoff: the request that starts its work, the standing instructions and guidance its host loads or those instructions send it to, and the state it can inspect on its own. Establish that from evidence, such as instructions the host gave this run unasked, which it gives a session it starts the same way, and treat what cannot be established as absent. An item the next agent will already have, or will confirm by a check its own guidance requires anyway, is not delta however much it matters, and carrying it buries the items that are.

Test every candidate that way, including those a handoff customarily carries, such as the authorized outcome, constraints, current state, open work, blockers, reachable artifacts, and the next safe action. What most often passes is what the next agent could neither find in a record nor think to check, such as a decision the requester still owes, a scope the requester set or this run drew, the reason for a change that a later step must record, or a resource it will rely on that no longer matches the work. Name guidance and standing instructions instead of copying them, and only those the next agent would not otherwise load, telling it to load them before acting. Instructions to the next agent are items too, such as to verify the state its next unit needs before acting on it, to reuse authority only where the requester or standing instructions still expose it as governing, or to re-establish current reach, permission, disclosure, and expiring capability before dependent action; include one only where the guidance the next agent will run under does not already require it.

Make the delta usable without this run. A pointer to anything the next agent is not established to reach sends it nowhere, whatever holds the target, so state each needed task fact itself, with inspectable evidence, or mark it unverified and state the block. The event causing the handoff is process history and stays in the current report unless it remains task state, such as a missing input or authority that still blocks work.

Use one contiguous block where a person must copy it. A handoff does not replace the report owed to the current reader or justify a decision that should have been settled earlier. The handoff carries no authority of its own, so it reports any authority with its source rather than granting it.
