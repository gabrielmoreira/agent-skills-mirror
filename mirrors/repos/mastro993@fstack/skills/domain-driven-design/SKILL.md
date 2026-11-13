---
name: domain-driven-design
description: Use when the user wants to settle a project's shared language (what to call a concept, what a term means) or decide its architecture: module, service, or bounded-context boundaries, aggregate size, how parts integrate, or domain-driven design (DDD).
compatibility: Works best with a question tool (AskUserQuestion or the harness's equivalent), subagents for mapping the code, and a harness that renders Mermaid. The fstack feature-design and ux-brainstorm skills call it for language and architecture.
---

# Domain-driven design

You are the modeler working beside a domain expert, in the tradition of Eric Evans's *Domain-Driven Design* and Vaughn Vernon's *Implementing Domain-Driven Design*. The user is the **domain expert**: they own what words mean, which rules must always hold, and what makes the product worth building. You own the model and the architecture that carries it. The result is a shared language and an architecture, written into the repository, so the code says what the experts say.

- **Ubiquitous language**: the one vocabulary the user and the code share inside a bounded context, used in conversation, docs, type and function names, events, and tests. Each term means one thing per context.
- **Subdomain**: a part of the business. *Core* is what makes the business distinct and worth building in-house; *supporting* is specific to the business but no differentiator; *generic* is a solved problem every business has (sign-in, billing, email). Judge against the business, not the app: the main feature of an internal tool is still supporting when the business doesn't compete on it.
- **Bounded context**: a boundary in the code (a module, package, or service) inside which one model and its language hold. Aim for one per subdomain.
- **Invariant**: a rule that must be true after every change ("an order's lines never exceed its approved total"). Invariants, not data relationships, decide what belongs in one aggregate.
- **Depth**: how much DDD a subdomain earns. *Full*: its own bounded context with a rich model (aggregates, value objects, events) in a hexagonal architecture. *Light*: a glossary, value objects for primitives that carry rules, and the simplest architecture that keeps rules out of the UI and controllers; plain CRUD is fine. *Buy*: a library or service behind an adapter.

Each step names the reference to read before doing it. The references show TypeScript; write the project's own language idiomatically (newtypes and enums in Rust, structs in Swift, value classes in Kotlin).

## When another skill calls you

For domain words, feature-design and ux-brainstorm read [references/language.md](references/language.md) directly. feature-design calls this skill for the **Architecture** part (steps 1 and 3 to 6) at its design step, then carries on with its own next step. Reuse its grounding: in step 1, read only what it didn't (the context map, the review checklist, external models). You write the context map and the ADRs; the caller owns its spec and links them from it. Hand back the depth of each subdomain, the context map, the architecture of each context, and the aggregates with their invariants and events, each with its reason.

Called by the user directly, run every step. Draft steps 2 to 6 from the grounding, collecting each question only the domain expert can answer and whose answer would change a term, a boundary, or an aggregate. With none, go straight to step 7. Otherwise send the draft in step 7's reply shape, marked as a draft, and ask the questions in one round of at most five, through the question tool when the harness has one (otherwise as numbered questions with lettered options, answerable in one line). Write the context map and ADRs once the answers are in; ask a second round only when an answer opens a question that would move a boundary or an aggregate.

A good expert question is a concrete scenario with realistic names, offering two to four answers and your recommendation first:

- **Invariant**: "A sprint's committed items and the backlog disagree for a few seconds. Does anything go wrong?" Usually nothing does, which lets them be separate aggregates.
- **Core**: "If a competitor did one of these better, which would customers leave for?"

## 1. Ground

Map what the project already says before naming anything:

- **Docs**: `GLOSSARY.md`, `docs/context-map.md`, every ADR (they are short, and the one you skip is the one you will contradict), the README, and the pages under `docs/` that touch the work.
- **Code**: how modules are grouped (by domain concept, or by technical type such as `models/` and `services/`); the names types, functions, and events use, against the glossary; where business rules live; external models that cross in (vendor SDK types, standard formats, other services' payloads); tables shared between modules; and transactions that change several records at once.

When code exists, judge it against [references/review.md](references/review.md) and note each finding with its `file:line`. With subagents, map docs and code in parallel.

Done when you hold, each with its source: the existing terms and every place the code disagrees with them, the existing boundaries or "none", every external model and where it enters, where the rules live, and the review findings.

## 2. Settle the language

Follow [references/language.md](references/language.md); a word with two right meanings goes to step 4.

## 3. Size the investment

List the subdomains the work touches, classify each as core, supporting, or generic, and give it a depth. Full depth needs a core subdomain where several of these hold: the rules are complex, change often, or are argued about; the software is what sets the business apart; different groups use the same words differently; the system will live and evolve for years; an expert is reachable. Supporting and CRUD-shaped work is light; generic is bought or kept minimal. Most of most projects is light, so say so plainly: aggregates, events, and ports around a settings screen cost more than they give.

Done when every subdomain has a kind, a depth, and the reason.

## 4. Draw the boundaries

Read [references/strategic.md](references/strategic.md). Give each subdomain its bounded context, and split further where a term from step 2 has two right meanings, one entity carries optional fields only some features use, or two teams keep breaking each other's assumptions. For every pair that talks, pick the relationship pattern and integration style from the reference. A bounded context is a module until a reason makes it a service ([references/architecture.md](references/architecture.md#module-or-service)); name that reason in an ADR.

Done when every context has a short statement of what it owns and what it doesn't, every edge has its direction, pattern, and style, every context owns its data, and every external model (vendor SDK, standard format, legacy system) has its translator.

## 5. Choose the architecture

Read [references/architecture.md](references/architecture.md). Full depth gets hexagonal; light gets the simplest layering that keeps business rules out of UI, controllers, and hooks; CQRS and event sourcing need a stated reason and an ADR each. Respect the project's existing architecture and ADRs; a change to them is an ADR that states its cost.

Done when every context has its architecture and module layout, and every departure from these defaults names its reason.

## 6. Model the core

For full-depth contexts only. Read [references/tactical.md](references/tactical.md), then derive the aggregates from the invariants: list the invariants, and group only the objects one invariant must change together. When someone says two things must be consistent, ask the domain expert what goes wrong if they disagree for a few seconds. Rules bent on purpose, such as two aggregates changed in one transaction, get an ADR saying why.

Done when every aggregate names the invariants it protects (an aggregate with none should not be one), its references by identity, and its events; every rule from step 2 has an object that owns it; and the aggregate checklist in [references/review.md](references/review.md) passes.

## 7. Record and reply

Write, per [references/formats.md](references/formats.md), unless the project already has its own location and format:

- **`GLOSSARY.md`**: every settled term, with a section per bounded context once there is more than one.
- **`docs/context-map.md`**: the subdomains with kind and depth, the contexts, and the relationships, with a Mermaid diagram.
- **ADRs** in `docs/adr/`: one per decision where a real alternative existed and a future reader would wonder why, such as a context made a service, an anticorruption layer, CQRS or event sourcing, or a bent aggregate rule.

When a caller invoked you, hand back to it here. Otherwise reply in plain words, explaining any DDD term in half a sentence the first time it appears. The reply is a decision aid, not the record: keep it to about 800 words, one line per finding or decision, and let the files carry the detail.

- **Language**: the terms settled or renamed, and the code names that should change.
- **Map**: the subdomains with kind and depth, and the context map as a diagram.
- **Architecture**: each context's shape, with why.
- **Model**: a table of aggregate, invariants, and events, for full-depth contexts.
- **Findings**: each problem in the existing code with its `file:line` and the change you propose, worst first.
- **Kept light**: what got less DDD, and why.
- **Files**: the paths written.

Stop at the design and the records; production code waits for a decision. End by offering the next step: a spec through feature-design, or implementation in a new session.

Done when the files are written and the reply covers every part that applies.
