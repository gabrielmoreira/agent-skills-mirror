---
title: Human-facing API documentation
applicability:
- When text for a human reader states an interface's contract
x-claim-provenance:
- claim: Reference documentation is lookup-oriented description of software machinery and should be accurate, consistent, and structured for consultation.
  source: https://www.diataxis.fr/reference/
- claim: API reference comments should add purpose, usage, prerequisites, parameter meaning, return meaning, failures, and deprecation guidance rather than merely restating declarations.
  source: https://developers.google.com/style/api-reference-comments
- claim: API comments may need to state success and failure behavior, idempotency, units, side effects, formats, ranges, presence, and defaults when those facts affect use.
  source: https://google.aip.dev/192
- claim: Function and method docstrings should summarize behavior and document applicable arguments, returns, side effects, exceptions, and calling restrictions.
  source: https://peps.python.org/pep-0257/
- claim: A function docstring should provide enough caller-facing information to use the function without reading its implementation.
  source: https://google.github.io/styleguide/pyguide.html
---

A tutorial, how-to, conceptual explanation, or implementation comment that mentions an interface does not thereby become reference material; this guide shapes only the part that states the interface's contract.

Start from the consumer and the exact surface being documented. For a single symbol, stay local. When the requested result is a complete reference, establish the exported or otherwise published surface with a project or documentation-tool mechanism that could reveal an unexpected member, then account for each member the reference promises to cover. Do not infer a larger public surface from implementation visibility alone.

Treat the declaration, signature, schema, generated syntax, and prose as complementary. Let machine-readable structure own facts it already exposes reliably; use prose for meaning and behavior the reader cannot recover as cheaply from that structure. A type name does not explain units, a default literal does not explain omitted-value behavior, a nullable type does not explain whether absence has a distinct meaning, and a return type does not explain what the returned value represents. Delete prose that merely echoes names, types, modifiers, or syntax without changing understanding.

Write the smallest contract that lets the intended consumer decide whether and how to use the interface without opening its implementation. Consider the questions below only when their answers change correct use or interpretation; they are prompts, not mandatory headings or an exhaustive template:

- **Purpose and identity:** what the item represents or does, and the useful distinction its name or declaration does not already make clear.
- **Use context:** when or why it is used; prerequisites, permissions, feature conditions, dependencies, or a related alternative when those affect the call or result.
- **Input semantics:** what each non-obvious input means, including units, accepted formats, ranges and inclusivity, optional or missing meaning, meaningful defaults, ownership, or mutation when applicable.
- **Observable behavior:** effects and state changes the consumer can rely on, including ordering, repetition or idempotency, laziness or blocking, asynchronous completion, concurrency, cancellation, timeout, streaming, or pagination when material.
- **Result semantics:** what success gives the consumer and what the returned, yielded, emitted, or mutated value means beyond its declared type.
- **Failure contract:** the distinct conditions a consumer can recognize, how and when each failure surfaces, and material partial effects. Follow [[guide:documentation-evidence]] for prevention and recovery.
- **Caller obligations and limits:** preconditions, invariants, lifetime or cleanup duties, resource ownership, safety boundaries, supported combinations, and stable performance characteristics only when they are part of the contract.
- **Evolution:** availability or compatibility conditions, and for a deprecated surface, the replacement plus the caller action needed to move away from it.
- **Examples and cross-references:** one small representative example or a link to deeper task/concept material when interaction, ordering, or an edge case is hard to understand from the contract alone.

When the documented interface is also a software boundary with an independently changing consumer, establish the underlying interface and integration contract before translating it into reader-facing text. Documentation can expose an established contract; it cannot create a software guarantee that the implementation, schema, tests, or owning requirement does not support.

For docstrings and documentation comments, establish semantic content before choosing tags or section syntax. The summary sentence should state useful behavior or purpose rather than repeat the symbol name or signature. Parameter entries explain meaning and behavior, not merely type. Return or yield entries explain what the result represents. Failure entries identify conditions and timing rather than listing exception names alone. Inherited documentation is valid only where the inherited consumer contract still applies unchanged. Map these decisions into the project's configured generator only after the content is settled; tags and headings encode the contract, they do not define what the contract contains.

Keep implementation rationale separate from public contract. An implementation comment may explain a non-obvious invariant, external constraint, hazard, ownership rule, or enduring reason that a maintainer needs; it should not masquerade as API reference. Conversely, caller-facing behavior does not belong only in an implementation note if a consumer must know it to use the interface correctly.

Review a human-facing API entry with two opposing tests. First, can the intended consumer determine relevance, supply acceptable inputs, predict material results, effects, and failures, satisfy their obligations, and follow any replacement path without reading implementation? Second, can any sentence be removed because the declaration, shared reference owner, or linked material already communicates the same usable meaning? Missing answers reveal a contract gap; removable repetition reveals documentation noise.
