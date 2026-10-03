---
title: Source comments and docstrings
applicability:
- When a source comment or docstring is among what the work produces or assesses
- When a change may leave a source comment or docstring untrue
---

Docstrings and documentation comments expose a human-facing local interface contract; ordinary comments preserve an invariant, ownership rule, hazard, external constraint, or enduring rationale that code cannot state clearly.

Before editing comments or docstrings, detect their syntax, generator, build settings, and surrounding convention. Use that generator's tags, links, and verification command; do not import incompatible conventions or replace the documentation tool without an explicit request. When it applies, read [[guide:human-api-documentation]] before drafting or reviewing a docstring or documentation comment.

Ordinary implementation comments are maintained code, not a reasoning log: add one only for a non-obvious invariant, hazard, external constraint, ownership rule, or enduring rationale that code cannot state clearly; omit step-by-step reasoning, alternatives, patch narration, obsolete history, syntax restatement, and comments that merely compensate for unclear structure. Do not restate names, signatures, types, defaults, or enumerations without adding meaning, and prefer a clearer name to a compensating comment.

If a change leaves a comment or docstring untrue, update it when authorized or report the change incomplete. Merely touching a file that contains comments does not justify rewriting them.
