---
title: Evaluate observed skill behavior
cues:
- the requester asks to obtain behavioral evidence by running a skill with an agent
- the requester supplies completed interactions and asks what the observed agent behavior establishes about the skill
goal: Return a behavior claim no broader than the supplied or freshly obtained evidence supports, with this task itself changing neither source nor evaluated artifacts.
knowledge:
- working-accounts
- evidence-bounds
- child-skill-and-agent
- compiler-evidence
- compiler-integrity
- earliest-authored-cause
guides:
- effective-compiler
- fresh-evaluator-protocol
- supplied-artifact
handoffs:
- task: review
  applicability:
  - When the question needs no observed behavior, only a judgment of supplied Degardis source as written, and has neither an unfinished review responsible for it nor a review outcome on this route
- task: revise
  applicability:
  - When the evidence establishes a defect in supplied Degardis source, the requester asked to fix it, changing the source is authorized and permitted by the host, and no unfinished revision or revision outcome on this route covers the defect
- task: plan
  applicability:
  - When the evidence establishes a defect in supplied Degardis source, the requester asked to fix it, host instructions prohibit changing the source, and no unfinished plan or planning outcome on this route covers the defect
---

For a supplied Degardis source, the evaluated artifact is the bundle the effective compiler builds from the exact source, so establish that it builds before accepting or launching behavioral evidence. A source that cannot be built establishes no artifact whose behavior could be attributed to it, so report the structural blocker and make no behavioral correctness claim. Any other supplied skill, whether a Degardis bundle or a skill authored another way, is a built artifact evaluated under its own identity; do not reconstruct or validate source that was not supplied.

Before choosing evidence, name every question the request needs answered. Whether a request routes, whether the child agent can recover what it needs from the bundle, whether a changed instruction moves behavior, whether an end-to-end case succeeds, and whether the guidance holds at a stated capability floor are different questions needing different evidence, and one request can raise several.

Then take, for each, the least demanding class that can settle it, and the fewest instances of that class. One observation closes a question whose answer is visible in a single return; replication is for a question whose answer varies from one evaluator to the next, and every instance beyond the first is spend earned by that variance rather than by wanting a firmer number. Interactions the requester already supplied are cheapest, because the behavior has already happened; judge them in their own context and do not rerun a case merely to produce tidier evidence. A question that reading settles, such as a contradiction, a missing branch, an unreachable instruction, or an incompatible limit, needs no run: its answer is what the skill prescribes, not what an agent did. A fresh instance is for the case where the unknown genuinely depends on what a fresh evaluator does. Of its two kinds, a comprehension case puts the situation to the evaluator and asks for its decision without doing the work, so it settles what the evaluator recovers from the bundle at a fraction of an execution's cost; keep execution for what only doing the work shows, such as whether the evaluator notices a condition as it arises.

Plan fresh instances around all the questions that need one rather than one instance per question: an instance settles every question whose decisions it puts in front of the evaluator, so the fewest instances come from a setup that leaves the most of those decisions open. A setup may depart from ordinary use to save cost, such as a smaller task or a tighter limit that brings a condition within reach sooner, as long as the evaluator still meets each decision a planned question turns on and makes it itself. A setup that makes such a decision for the evaluator, as a session where nobody can answer settles whether it asks, leaves that question unanswered and costs another instance, so establish before launching what the setup will show and allow the evaluator at each of those decisions. Where no single setup leaves them all open, put the plan, with the questions each instance will answer, to the requester before spending on it.

Classify an unsuccessful observation before attributing it. A guidance failure is one where the child agent had to supply something the guidance owed it — a routing decision, discriminator, authority, fallback, or completion test. Evaluator capability, host behavior, tool availability, permission, fixture quality, and infrastructure are different causes with different repairs.

When an observed guidance failure is evidence of a source defect, attribute it to its earliest authored cause and return that attribution: the provision, the failure mode, and the reach evidence. Choosing the repair belongs to the task that changes the source.

Raising capability answers a different question than the one asked. A run that succeeds only after a more capable evaluator was substituted establishes that the weaker one could not follow the guidance; it is attribution evidence for that failure, never evidence that the claimed floor can be met. Where the evidence cannot distinguish guidance from another cause, keep the attribution inconclusive and name the observation that would distinguish them.

Close every started case as supported, failed, blocked, or inconclusive rather than smoothing a gap into a general judgment.
