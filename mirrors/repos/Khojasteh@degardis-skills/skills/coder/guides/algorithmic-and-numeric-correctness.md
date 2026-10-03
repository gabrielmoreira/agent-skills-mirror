---
title: Algorithmic and numeric correctness
applicability:
- When correctness depends on what a computation produces across its input domain
x-claim-provenance:
- claim: Software construction and computing foundations include algorithms, data structures, grammar-based processing, contracts, complexity, and numerical precision and error.
  source: https://www.computer.org/education/bodies-of-knowledge/software-engineering/topics
---

State the input domain, preconditions, invariant, postcondition, termination condition, and any complexity or resource bound that the contract actually requires before selecting or changing the implementation. Distinguish mathematical validity from representation limits and from performance. A faster or shorter algorithm is not an improvement if it narrows the accepted domain, changes ordering, loses stability, or weakens a required invariant.

For state-machine or table-driven logic, establish the states, events or keys, guards, transitions or selected actions, initial and terminal conditions, and behavior for invalid, missing, or unknown input before changing the table or dispatch. Keep one authoritative transition or selection relation; do not let default branches silently turn an open domain into a closed one or duplicate policy between the table and callers. Check determinism, completeness, reachability, and transition coverage only to the extent the owning contract requires them.

For numeric work, establish units, range, precision, rounding rule, overflow and underflow behavior, exceptional values, accumulated error, and the representation used at every boundary that can change meaning. Do not compare floating-point results with an arbitrary tolerance; derive the acceptable error from the contract, numerical method, measurement resolution, or observed stable variation. Preserve integer width, signedness, timestamp or duration semantics, and decimal-vs-binary expectations where they are externally visible.

For collections and search/order logic, check empty and singleton inputs, duplicates, ties, already ordered and reverse-ordered data, adversarial shapes, equality/hash consistency, comparator transitivity, stable-order requirements, and mutation during traversal where the project model permits it. For graphs or recursive structures, include cycles, disconnected components, depth, and repeated nodes when the domain admits them. Bound recursion or allocation when an accepted input can otherwise exhaust a finite resource.

For parsers and formatters, identify the grammar or structural rules, encoding and normalization behavior, ambiguous or malformed input, unknown fields or tokens, size limits, and round-trip requirements. Reject or recover according to the owning contract rather than accepting an incidental parser behavior as the specification.

Choose evidence that can distinguish the algorithmic claim. Examples and boundary cases establish named cases; properties or invariants can cover an open domain; metamorphic relations help when the exact result is hard to enumerate; differential checks can compare independent implementations or a simpler oracle; fuzz or grammar-based generation can search broad input spaces; model checking or proof can establish only the model, assumptions, and properties actually encoded. Keep a counterexample when it reveals a distinct defect, and do not add a new testing tool or generator without project authority.
