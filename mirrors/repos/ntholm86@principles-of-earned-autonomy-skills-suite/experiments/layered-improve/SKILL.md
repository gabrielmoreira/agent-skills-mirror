---
name: improve-layered-prototype
version: 0.1.0-experimental
description: 'Experimental layered Improve contract. Reason from target purpose, make one highest-leverage change or a bounded redesign/silence decision, verify it, reflect, and record. Not part of the installed suite.'
argument-hint: 'The target to improve, and optionally the concern'
---

# Improve - Layered Prototype

*Understand. Examine. Challenge. Decide. Act. Reflect. Record. Or argue convincingly that nothing should change.*

> Experimental artifact. Do not install as the production Improve skill. This prototype tests whether routine reasoning can remain complete while rare governance paths load only when triggered.

## Principles

1. **Operator's Intent:** understand the destination and why it matters; derive the route from the target rather than from examples or a checklist.
2. **Observable Autonomy:** make interpretation, evidence, decisions, uncertainty, actions, and outcomes reconstructable in Trail.
3. **Convergence Is Silence:** change nothing when no material finding survives examination; independent evaluators, not this run, establish convergence.

Everything except these principles is revisable. The moves below are reasoning vocabulary, not answers.

## 1. Understand

Apply the sibling Intent skill automatically before substantive work when available; it is an ingress service, not an operator command. If unavailable, use the Standalone Fallback. Narrate the interpretation so the operator can correct drift.

Read the target repo's current ACM surfaces in priority order: the complete current Destination, Orientation and its active rules, recent Learning, then only the Trail evidence needed for the present decision. A valid `current-destination: complete` / `destination-history` boundary makes the enclosed current section authoritative for routine work; widen to history for ambiguity, conflict, provenance, or Destination work.

For an underspecified continuation, form sourced hunches from those surfaces, state the one falsifiable question that would most change the next action, and proceed under the strongest explicit assumption when no answer is available.

## 2. Examine

Reason about what the target is for and what most limits that purpose. Purpose includes operator intent, the target's behavior and claims, its grounding and context, and anything else the situation makes material.

Separate observed facts, inferences, and proposed changes. Do not invent measurements, thresholds, systems, or operator preferences; label a new mechanism as a proposal rather than evidence.

Use lenses only when the target invites them:

- **Inconsistency:** parts that should agree but do not.
- **Overburden:** concentrated responsibility or risk.
- **Waste:** cost that earns no corresponding value.
- Add domain-specific lenses when they matter.

Name the evidence examined and what each applied lens revealed, including no finding.

## 3. Challenge

Test the first model:

- What material evidence or perspective is missing?
- Is the obvious finding hiding a stronger one?
- Is the structure itself wrong, making incremental repair poor value?
- Which prior learning or decision could this proposal contradict?

Use disconfirming evidence before committing to the preferred explanation.

## 4. Decide

Choose exactly one outcome for this iteration:

- **Incremental change:** the highest-leverage material finding.
- **Redesign argument:** why patching will not pay, the proposed boundary, costs, and rejected incremental path. Obtain operator authorization before implementing a structural redesign.
- **Bounded silence:** no actionable finding for named quality bars and surfaces; state what was not tested.

Before acting, record a falsifiable prediction: what should improve, what must be preserved, and what result would refute the decision. State why lower-ranked alternatives lost. Offer at most three short candidate next moves when genuine candidates emerged.

## 5. Act

Make only the chosen change. State the reason before each non-trivial action. Validate with the cheapest executable check that could falsify the prediction, then broaden checks in proportion to risk. If evidence overturns the decision, back it out and mark the reversal rather than defending it.

Compare the actual outcome with the prediction. A shorter, cleaner, or passing artifact is not evidence of improved capability unless the named preservation conditions also hold.

## 6. Reflect

Before recording, state:

- one falsifiable claim about what the target is or is becoming;
- one specific blind spot in this iteration;
- the strongest likely pushback from someone who knows the target better.

Evaluate whether the iteration reveals a recurring finding class, approaches silence, contradicts prior learning, or was explicitly requested as an arc-level question. When one fires, read the relevant arc and distinguish an action defect from a wrong governing variable or a defect in how the system learns. Mark durable insights and reversals explicitly.

## 7. Record

Before Trail becomes durable, decide whether Orientation is stale because Destination changed, a meaningful sequence accumulated, current claims were contradicted, or cross-iteration convergence is approaching. Raw iteration count is never sufficient, and missing Orientation context is not evidence that it is stale.

Apply the sibling Trail skill automatically after substantive work when available; it is an egress service, not an operator command. Its owning contract defines entry shape, append safety, derived artifacts, and evidence fidelity. Apply the sibling Orient skill automatically after the Trail entry is durable when freshness is stale. Use the Standalone Fallback only when an invoked sibling is unavailable. In a multi-iteration run, complete this checkpoint before beginning the next iteration.

When a visible trigger below fires, you must load its matching section of [CONDITIONAL_PROTOCOLS.md](./CONDITIONAL_PROTOCOLS.md) before continuing. Do not load other sections.

- **Standalone Fallback:** an invoked sibling service is unavailable.
- **Convergence Evaluation:** the ask concerns convergence, readiness, or cross-run silence.
- **High-Fidelity Writer Separation:** independent Trail authorship is requested or required by consequence.
- **Multi-Iteration Checkpointing:** one request authorizes multiple iterations.
- **Destination Boundary Failure:** completeness markers are invalid or current authority is ambiguous.
- **Precedent Conflict:** the decision may repeat or contradict prior learning.

Otherwise do not load the conditional file and stop without ceremony.

## Self-targeting

Apply the same purpose reasoning to this contract and its surrounding architecture. Do not privilege documentation fixes, named capabilities, or existing mechanisms merely because they are easy to inspect.
