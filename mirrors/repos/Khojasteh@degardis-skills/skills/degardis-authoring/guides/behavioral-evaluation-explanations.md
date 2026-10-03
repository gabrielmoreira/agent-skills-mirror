---
title: Behavioral evaluation explanations
applicability:
- Before explaining how to obtain or attribute evidence of a skill's behavior
---

Explain the evidence needed for the question, not a run to carry out. Routing, recovery of instructions from a bundle, an instruction's effect, end-to-end success, and a capability floor are different questions; each needs evidence that can settle it.

## Evidence selection

For Degardis source, explain why the evaluated artifact must be a build from the exact source: a structural blocker leaves no artifact to attribute behavior to. A supplied built skill is evaluated under its own identity, without reconstructing absent source. [[guide:supplied-artifact]] and [[guide:artifact-identity]] supply the material and identity decisions.

Explain the least demanding evidence that settles the question. Supplied interactions already record behavior and are interpreted in their own context rather than rerun for tidier evidence. Reading can settle a contradiction, missing branch, unreachable instruction, or incompatible limit; a fresh instance is needed where the unknown depends on what an evaluator does. A single return suffices for a question visible there, while replication is justified by variation between evaluators. [[guide:fresh-evaluator-protocol]] supplies the fresh-instance contract to explain; its authority, resources, and isolation requirements remain part of the method, not permission to launch it.

Keep compiler integrity distinct from behavioral evidence. The strictest closing check reports warnings as findings; an unresolved warning bars that integrity claim unless explicitly accepted beside it, while pages still composed can be examined. One successful behavioral run establishes that run, not general correctness, and comparisons credit a source change only with other configuration fixed.

## Attribution

Distinguish a guidance failure, where the agent had to supply a routing decision, discriminator, authority, fallback, or completion test owed by the instructions, from evaluator capability, host behavior, tools, permission, fixtures, and infrastructure. If evidence cannot distinguish them, explain the inconclusive attribution and the observation that would settle it.

For an established guidance failure, explain the earliest authored cause: the first authored decision whose absence, ambiguity, reach, order, or completion test made the failure family possible. The nearby sentence or proximate agent mistake may only be a manifestation; attribution needs the provision's compiled reach and assembled page. A stronger evaluator's success explains the weaker evaluator's failure, not that the claimed capability floor was met. Selecting or applying a repair is a separate source-work outcome.
