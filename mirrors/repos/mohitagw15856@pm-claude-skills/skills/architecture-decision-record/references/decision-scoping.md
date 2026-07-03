# What Deserves an ADR (and What "Context" Must Contain)

ADR practices die two ways: recording everything (ceremony fatigue) or recording nothing until archaeology is required. And the ADRs that DO get written fail at the context section — the part future readers actually need.

## The ADR bar — record it when ≥2 apply

- Reversing it later costs weeks+ (data models, protocols, build-vs-buy, framework choices)
- Multiple sane options existed and people disagreed (the disagreement is the value — capture it)
- Someone will ask "why is it like this?" within two years
- It constrains OTHER teams' choices

Below the bar: naming conventions, library-of-the-week, anything a linter enforces. Those go in style guides, not ADRs.

## Context: write for the 2-years-later reader

The context section's job is reconstructing the *pressures*, because the pressures explain the choice long after the choice looks odd:
- The constraints THEN: team size/skills, traffic scale, deadline, the systems that existed
- What we knew and didn't ("we assumed <10k tenants; we had no EU customers yet")
- The forcing event (why decide NOW rather than later)

The test: a new senior hire reads context alone and can guess the decision. If they can't, the context is missing the real pressure (often political/deadline — write it diplomatically but write it).

## Alternatives: the graveyard is the goldmine

Each rejected option gets: what it was, its genuine strengths (a strawman graveyard destroys trust), and the SPECIFIC reason it lost — tied to a context pressure. "Considered Postgres, chose Dynamo" teaches nothing; "Postgres lost on the ops burden with our then-zero DBA capacity" teaches everything, including *when to revisit* (you have DBAs now).

## Consequences: debts, not just benefits

The section future-you audits: what gets harder (the honest half) · new operational burdens · the revisit triggers ("if we exceed X tenants / add region Y, reopen this"). An ADR with only positive consequences wasn't finished.

## Lifecycle honesty

Statuses: proposed → accepted → superseded-by-[link] / deprecated. Never edit an accepted ADR's decision — supersede it. The chain of superseded ADRs is the architecture's memoir; editing history deletes the memoir.
