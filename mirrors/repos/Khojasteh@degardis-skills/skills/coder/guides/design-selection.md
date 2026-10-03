---
title: Design selection
applicability:
- When requirements and established project architecture leave a material design choice open
x-claim-provenance:
- claim: Architecture is expressed through significant design decisions and evaluated against stakeholder concerns and quality attributes.
  source: https://www.computer.org/education/bodies-of-knowledge/software-engineering/topics
---

Compare candidate designs at the level where their tradeoffs differ, not as code sketches whose incidental syntax hides the decision. Start from the accepted contract, project architecture, fixed constraints, affected consumers, and existing mechanisms. Compare viable alternatives before editing, at the level of responsibility, dependency direction, state authority, representation, lifecycle, abstraction, and boundary placement. Generate alternatives only while they expose a real unresolved choice; do not manufacture patterns to reach a quota. If only one design remains viable, establish what rules the alternatives out instead of treating absence of comparison as evidence.

Challenge each viable candidate with concrete architectural and coding heuristics. These are diagnostic questions rather than independent requirements, and the set is not exhaustive:

- **Ownership and cohesion:** does each policy, invariant, state transition, and responsibility have a clear owner, with behavior that changes together kept together and independently varying behavior separated?
- **Coupling and dependencies:** does the design minimize unnecessary knowledge between units, preserve the project's intended dependency direction, avoid cycles and backchannels, and limit how many places one future change must touch?
- **Information hiding and invariants:** are volatile representation and validation rules hidden behind the narrowest semantic boundary that can keep the invariant true, rather than leaked for callers to coordinate?
- **Authority and state:** is each fact or policy authoritative in one place, with derived representations and mutation paths unable to become competing sources of truth?
- **Local reasoning:** can the common path be understood from explicit inputs, dependencies, state, and effects without reconstructing distant globals, temporal setup, mode flags, or surprising callbacks?
- **Abstraction fit:** does every abstraction and indirection earn its place under [[guide:abstraction-boundaries]]?
- **Change and verification cost:** does the design make the likely next change and required evidence narrower rather than spreading policy, setup, failure handling, or tests across unrelated units?

Use the heuristics to expose consequences, not to score designs by acronym or force a pattern. For an architecture-level choice, make the process, deployment, data, trust, integration, and failure-isolation boundaries explicit enough to evaluate the scenario that drives the decision. Compare only qualities implicated by this work: correctness, architectural fit, ownership, cohesion, coupling, change amplification, comprehensibility, testability, compatibility, migration or operational cost, plus any established security, performance, availability, scalability, observability, portability, concurrency, persistence, or failure boundary. Treat these qualities as tradeoffs tied to concrete scenarios and consumers, not as scores or slogans.

Prefer the candidate that satisfies the fixed contract and project constraints with the lowest justified total cost and fewest unsupported assumptions. Reject a candidate that works only by creating a second source of truth, bypassing an established owner, reversing an intended dependency, spreading one policy across unrelated units, hiding lifecycle or effects, or adding indirection without a demonstrated responsibility. Keep the decisive alternatives, tradeoffs, and rejected assumptions in re-readable working state; update a maintained architecture/design record only when the project or request already requires one.
