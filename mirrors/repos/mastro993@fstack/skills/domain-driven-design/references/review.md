# Review checklists and anti-patterns

Use these to judge an existing model, a proposed one, or a pull request. Each failed check is a finding: the problem, its `file:line`, and the change you propose.

## Starting a new context

- The subdomain is classified (core, supporting, generic) and its depth agreed.
- A short statement says what the context owns, and what it doesn't.
- A glossary exists, and no term in it means two things.
- The context-map edges are drawn: upstream, downstream, pattern, integration style.
- Events, commands, and candidate aggregates came from expert scenarios ("when…", "after…").
- Architecture is hexagonal for full depth, with CQRS or event sourcing only for a stated reason.

## Aggregates

- It names the invariants it protects. With none, it need not be a cluster.
- It is as small as those invariants allow.
- It refers to other aggregates by identity only.
- Each transaction changes exactly one aggregate, or an ADR says why not.
- Its state changes are announced as past-tense domain events.
- It is created through a factory or static method that guarantees validity.
- Its repository is per aggregate root, with the interface in the domain.

## Code

- Names match the glossary; an expert would recognize them.
- Primitives with rules are wrapped in value objects.
- No business rule sits in an application service, controller, component, or hook.
- External formats are translated at the boundary rather than flowing into the domain.
- Tests read in the domain's language: scenarios, not mechanics.

## Anti-patterns

| Anti-pattern | Symptom | Remedy |
| --- | --- | --- |
| DDD-lite | Entities and repositories everywhere, no bounded contexts or language | Start from strategic design; tactical patterns come second |
| Anemic domain model | Objects without behavior; logic in services | Move rules onto the objects that own the data |
| Mega-aggregate | Locking conflicts, slow loads, "everything is in the Order" | Apply the four rules; split and use events |
| Shared database between contexts | One team's schema change breaks another | Integrate through APIs or events; each context owns its data |
| Leaky external model | Vendor or standard types used throughout the domain | Anticorruption layer at the boundary |
| One model to rule them all | Classes with dozens of optional fields serving many departments | Split into bounded contexts, each with its own model |
| Technical naming | Managers, helpers, processors, a generic `update()` | Rename after domain operations |
| Pattern for pattern's sake | Factories and specifications with no rule inside; ports and aggregates around CRUD | Use a pattern only when it expresses something real; go light |
