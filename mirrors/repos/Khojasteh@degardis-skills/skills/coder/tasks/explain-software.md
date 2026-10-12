---
title: Explain how software works
cues:
- how existing software works should be explained to the requester
goal: The requester receives an evidence-grounded explanation at the requested scope and depth, with material uncertainty explicit and the inspected boundary named wherever it limits the answer, while project source, documentation, and operational state remain unchanged.
knowledge:
- authorized-software-surface
- project-grounding
guides:
- user-interface-work
- documentation-evidence
- human-api-documentation
- value-boundaries
- failure-behavior
- data-and-state
- concurrency-and-resources
- security-boundaries
- interface-contracts
- dependency-and-artifact-integrity
- observability-and-diagnostics
- algorithmic-and-numeric-correctness
- commands-and-tooling
- workspace-integrity
- version-control
---

Establish the reader's question and the smallest software surface that can answer it. Distinguish what the implementation directly establishes from requirements, historical intent, or an inference about why it was designed that way.

Cover, as far as the question needs them, what enters, which component owns each material step, how control or data moves, what state or boundary changes, what leaves, and the failure or alternate paths that bear on the requested behavior. Use examples only to illuminate a rule already established by the project. Do not turn a request about one path into a codebase assessment or offer unrequested redesign recommendations.

When the explanation depends on a version-sensitive tool or generated relationship, establish that dependency from project evidence, or from a narrow observation whose effects stay confined to disposable output, before presenting it as fact; an observation with any other effect needs authority of its own.
