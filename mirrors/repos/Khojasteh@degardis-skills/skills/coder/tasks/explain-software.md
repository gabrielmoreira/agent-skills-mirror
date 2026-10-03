---
title: Explain how software works
cues:
- how existing software works should be explained to the requester
goal: The requester receives an evidence-grounded explanation at the requested scope and depth, with material uncertainty and the inspected boundary explicit, while project source, documentation, and operational state remain unchanged.
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

The explanation itself is the deliverable, so documentation, comments, examples, diagrams, generated artifacts, and other persistent material are not created in the project merely because those forms could explain the subject.

Establish the reader's question and the smallest software surface that can answer it. Start from the symbols, entry points, configuration, interfaces, or behavior named by the request, then follow only the callers, registrations, generated relationships, schemas, state transitions, or tests needed to make the explanation correct. Distinguish what the implementation directly establishes from requirements, historical intent, or an inference about why it was designed that way.

Explain in the reader's decision order: what enters, which component owns each material step, how control or data moves, what state or boundary changes, what leaves, and the failure or alternate paths needed to understand the requested behavior. Use examples only to illuminate a rule already established by the project. Do not turn a request about one path into a codebase assessment or offer unrequested redesign recommendations.

When the explanation depends on a version-sensitive tool or generated relationship, establish that dependency from project evidence or an authorized narrow observation before presenting it as fact. If the available surface cannot settle part of the question, state the uncertainty and the specific evidence that would settle it rather than filling the gap from ecosystem habit, and name the inspected boundary wherever it limits the answer.
