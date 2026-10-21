---
kind: guidance
title: The scope of a software change
---

A change reaches its intended contract through the smallest coherent transformation. Addition, modification, migration, restructuring, and withdrawal are different transformations because they preserve and retire different contributions. Implementation, tests, documentation, configuration, schemas, migrations, generated material, and operational declarations belong to the change only when the requested contract or an affected dependency makes them part of it.

Screen the proposed design, and the final change where the work produces one, against the concerns the task page's guides name and any other concern the change affects: enter a concern only when the requested outcome or project evidence implicates it, and add controls only for the risk established there.

Follow the change's consequences through affected consumers and maintained representations. A consumer search finds what names or binds the changed code, not what was built on a premise the change retires: a property the old contract or design held and the new one does not, such as a unit or scale, a range, which direction counts as better, a default, an ordering, an owner, or a lifetime. Implementation, tests, fixtures, test doubles, examples, and documentation can encode such a premise in their values and structure without referring to anything the change touched, and a test resting on it can keep passing because its inputs never reach a case where the old and new contracts differ. So name each premise the change retires, including one a later revision of the request retires, and treat what rests on it as a set of change sites under [[guide:change-sites]], searched by meaning and by value as well as by name. Remove or update only the stale implementation, tests, fixtures, documentation, examples, configuration, migrations, generated outputs, compatibility shims, or operational material whose truth or ownership changed; a surface that remains correct is evidence of no work there, not a reason to touch it for consistency. Judge that correctness against the current contract, not from a check that still passes. Defects the change introduces are part of its scope, and it is not complete until they are corrected.

When a change is made in increments, whether slices of one request or successive requests that extend or revise it, the change is everything the work has altered since it began, judged against the requirements as they now stand: each increment can pass its own checks while retiring a premise an earlier one built on.

When evidence disproves a decision the change rests on, whether cause, requirement, contract, design, technology, or implementation, classify the failure and revise that decision before advancing.
