# build-knowledge-graph

> Translate the raw legacy code inventory into a structured, queryable knowledge graph that captures domain concepts, business rules, and business processes — stripped of all implementation artifacts.

## When to use this skill

After `read-legacy-code` is complete and the legacy inventory files exist in `_superml/legacy-inventory/`.

Can also be triggered standalone if the user has:
- External documents (specifications, user manuals, requirement docs)
- Domain expert willing to describe the business in conversation
- A mix of code + documents

Ask user on activation:
> "I'll build the knowledge graph from the legacy code inventory. Do you also have any additional sources to include?
> 1. Functional specification documents (Word/PDF/text)
> 2. Data dictionaries provided by business
> 3. Process flow diagrams or swimlane diagrams
> 4. A domain expert you can relay information from
> 5. None — proceed from code only"

## What is a knowledge graph (in this context)?

Not a graph database. A structured collection of markdown files that captures:

- **Domain entities** — the business objects (Customer, Order, Policy, Account...)
- **Business rules** — the constraints, validations, calculations, and decisions
- **Business processes** — end-to-end flows, triggers, steps, outcomes
- **Domain vocabulary** — what things are called in THIS business

It is the bridge between "what the legacy code does" and "what the new system must do."

## Outputs

Written to `{project-root}/_superml/knowledge-graph/`:
- `graph.md` — master knowledge graph (entities + relationships + rules index)
- `entities/` — one file per domain entity
- `business-rules.md` — numbered rule registry
- `process-flows.md` — business processes
- `domain-glossary.md` — business vocabulary

## Instructions

Read `./workflow.md` and execute each step in order.
