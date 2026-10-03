---
kind: guidance
title: The scope of a software change
---

A change reaches its intended contract through the smallest coherent transformation. Addition, modification, migration, restructuring, and withdrawal are different transformations because they preserve and retire different contributions. Implementation, tests, documentation, configuration, schemas, migrations, generated material, and operational declarations belong to the change only when the requested contract or an affected dependency makes them part of it.

Screen the proposed design, and the final change where the work produces one, against the concerns the task page's guides name; an affected concern no guide names is screened by the same test. Enter a concern only when the requested outcome or project evidence implicates it, and add controls only for the risk established there.

Follow the change's consequences through affected consumers and maintained representations. Remove or update only the stale implementation, tests, documentation, examples, configuration, migrations, generated outputs, compatibility shims, or operational material whose truth or ownership changed; a surface that remains correct is evidence of no work there, not a reason to touch it for consistency. Defects the change introduces are part of its scope, and it is not complete until they are corrected.

When evidence disproves a decision the change rests on, whether cause, requirement, contract, design, technology, or implementation, classify the failure and revise that decision before advancing.
