---
title: Abstraction and ownership boundaries
applicability:
- When a decision depends on whether an abstraction or ownership boundary earns its place
---

Prefer improving names, existing boundaries, and direct control flow before adding an abstraction. Use the fewest cohesive concepts, files, layers, dependencies, and indirections that the demonstrated behavior needs. Keep each changed unit and the common execution path locally followable, make every added navigation jump earn its cost, preserve clear ownership and construction paths, and group behavior by demonstrated reasons to change rather than unit size.

Every abstraction names a real concept, variation, ownership boundary, or evidence seam, and each indirection earns its navigation and lifecycle cost. Derive an interface from concrete caller needs and add an extension point only for demonstrated variation. Add another boundary only when project evidence shows a real substitution, isolation, nondeterminism, external-ownership, or policy boundary. Prefer direct composition when no established substitutability relationship requires inheritance. Each retained abstraction must identify the concept it owns, the pressure that requires it, and the comprehension, cohesion, coupling, navigation, or testing benefit it supplies.

Do not invert every dependency, introduce hypothetical extensibility, or hide straightforward behavior behind factories, strategies, wrappers, or configuration merely to conform to a pattern. When inheritance or polymorphism changes, preserve established exceptions, invariants, and accepted input ranges.
