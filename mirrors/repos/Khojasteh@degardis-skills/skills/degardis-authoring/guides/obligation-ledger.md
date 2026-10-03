---
title: Obligation ledger
applicability:
- When the work depends on what a source's outcome obliges it to do
---

Keep the ledger and its ownership map in re-readable working state.

Derive the ledger from the requested outcome, its authorities, supplied evidence, and accepted field facts before inventorying constructs, and keep it separate from the source inventory until both can be compared. Completeness is relative to the declared outcome contract, never universal.

For every request class and materially different initial state, record:

- the requested outcome and boundary;
- required inputs and who can supply or authorize them;
- operational dependencies, host capabilities, and unavailable/partial branches for each;
- prerequisites and the evidence making each true or false;
- decisions and their discriminators;
- each obligation's applicability condition, revealing evidence and timing, and whether correct completion of an already in-scope instance requires it when the condition holds;
- actions, effects, prohibited effects, trust boundaries, and foreseeable harms;
- domain facts or external rules whose version, date, jurisdiction, or freshness can change a decision;
- outputs or artifacts, acceptance conditions, and consumers;
- success, failure, partial, and ambiguous states;
- fallbacks, stops, recovery, and hand-offs;
- observable completion evidence;
- reporting the next actor needs to act safely; and
- each claim's status, basis, and unresolved facts.

These fields prompt coverage, not a closed ontology. Add subject-specific items the outcome needs. Do not assign construct kinds here, so current placement or a situational label cannot pre-classify ownership.

## Ownership map

For every obligation, record one authored owner, baseline-or-specialization role, applicable domain, selector, supporting constructs, consumer, and generated page. Derive owner kind from that independently recorded behavior under [[guide:construct-ownership]], not current placement.

Map the other direction too: every affected authored contribution points to one distinct point and consumer; every behavior-bearing contribution also points to an established obligation. Establish both directions of the map as [[principle:complete-enumeration]] requires. A contribution that cannot clear that point-uniqueness test remains unsupported, obsolete, duplicated, or outside the declared outcome until evidence settles which.

Keep point ownership separate from rehearsal. Two live owners can produce the same result in one case, so a passing case cannot establish single ownership.

## Terminal dispositions

Every obligation ends as one of these:

- supported, owned, reachable, and verified;
- resolved at runtime by an input or authority the child agent can obtain before dependent action;
- removed from the required outcome by an authorized narrowing or withdrawal;
- established by evidence as outside the declared outcome; or
- unresolved, leaving the affected completion claim blocked and naming the single check or authority that would settle it.

The standard, rather than the list, governs an unlisted situation: no dependent action or completion claim proceeds on an unresolved required premise.
