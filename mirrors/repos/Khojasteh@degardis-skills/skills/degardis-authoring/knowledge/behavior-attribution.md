---
kind: guidance
title: Behavior attribution
requires:
- evidence-bounds
- earliest-authored-cause
---

Classify an unsuccessful observation before attributing it. A guidance failure is one where the child agent had to supply something the guidance owed it — a routing decision, discriminator, authority, fallback, or completion test. Evaluator capability, host behavior, tool availability, permission, fixture quality, and infrastructure are different causes with different repairs.

When an observed guidance failure is evidence of a source defect, attribute it to its earliest authored cause and return that attribution: the provision, the failure mode, and the reach evidence. Choosing the repair belongs to the task that changes the source.

Raising capability answers a different question than the one asked. A run that succeeds only after a more capable evaluator was substituted establishes that the weaker one could not follow the guidance; it is attribution evidence for that failure, never evidence that the claimed floor can be met. Where the evidence cannot distinguish guidance from another cause, keep the attribution inconclusive and name the observation that would distinguish them.
