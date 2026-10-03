---
kind: guidance
title: Behavioral evaluation
requires:
- evidence-bounds
---

For a supplied Degardis source, the evaluated artifact is the bundle the effective compiler builds from the exact source, so establish that it builds before accepting or launching behavioral evidence. A source that cannot be built establishes no artifact whose behavior could be attributed to it, so report the structural blocker and make no behavioral correctness claim. Any other supplied skill, whether a Degardis bundle or a skill authored another way, is a built artifact evaluated under its own identity; do not reconstruct or validate source that was not supplied.

Name the question first. Whether a request routes, whether the child agent can recover what it needs from the bundle, whether a changed instruction moves behavior, whether an end-to-end case succeeds, and whether the guidance holds at a stated capability floor are different questions needing different evidence.

Then take the least demanding class that can settle it, and the fewest instances of that class. One observation closes a question whose answer is visible in a single return; replication is for a question whose answer varies from one evaluator to the next, and every instance beyond the first is spend earned by that variance rather than by wanting a firmer number. Interactions the requester already supplied are cheapest, because the behavior has already happened; judge them in their own context and do not rerun a case merely to produce tidier evidence. A contradiction, a missing branch, an unreachable instruction, or an incompatible limit is settled by reading. A fresh instance is for the case where the unknown genuinely depends on what a fresh evaluator does.
