---
title: Describe supplied skill material and its prescribed guidance
cues:
- the requester asks what supplied skill material says about its contents or what its instructions direct an agent to do
goal: An account of the requested aspect of the supplied material, including prescribed guidance for a scenario, taken from the material itself and no broader than the request, leaving it unchanged and reporting what the material does not settle as unestablished rather than judging it.
knowledge:
- working-accounts
- evidence-bounds
- compiler-evidence
guides:
- effective-compiler
- supplied-artifact
handoffs:
- task: review
  applicability:
  - When the account asked for needs a judgment of whether the material is right and that question has neither an unfinished review responsible for it nor a review outcome on this route
---

Take each statement from the material rather than from what a source of this shape usually does, and where the compiler settles a question the bytes do not — what a page ends up carrying, which task a page is written for, what a build would ship — prefer its own report to a reading of the source prose.

For a scenario, trace the instructions the agent would reach and the conditions deciding its actions, stops, and hand-offs. Report this as prescribed guidance: the material establishes what it teaches, while what an agent actually did requires interaction evidence. A scenario supplied to make the account concrete does not itself request a run.
