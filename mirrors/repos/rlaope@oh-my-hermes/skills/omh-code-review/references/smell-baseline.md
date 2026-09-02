# Smell Baseline

The named baseline for maintainability findings. A smell here is a judgement
call to argue from evidence in the diff, never an automatic finding - and the
reviewed repository's own documented standards override this baseline wherever
they conflict. Cite the smell name in the finding so the author can look up the
same definition. Adapted from the classic Fowler/Beck catalog.

## The twelve baseline smells

| Smell | What it is | The usual fix |
| --- | --- | --- |
| Mysterious name | A name that forces the reader to open the body to learn what it does. | Rename to what it does or returns; a long clear name beats a short opaque one. |
| Duplicated code | The same decision encoded in two places, so one edit needs two. | Extract the shared decision to one owner; leave lookalikes that encode different decisions alone. |
| Feature envy | A function that reads or writes another module's data more than its own. | Move the function to the data it envies, or move the data to the function. |
| Data clumps | The same group of values travelling together through signatures. | Introduce the object the clump is trying to be. |
| Primitive obsession | Domain concepts passed as bare strings/ints so nothing checks them. | Wrap the concept in a type that validates at the boundary. |
| Repeated switches | The same type/kind dispatch re-implemented at several sites. | Centralize the dispatch (polymorphism, a table, one router) so a new case is one edit. |
| Shotgun surgery | One conceptual change that requires edits scattered across many files. | Move the pieces of the concept into one place before the next change. |
| Divergent change | One module edited for many unrelated reasons. | Split the module along its change reasons. |
| Speculative generality | Hooks, parameters, or layers serving only an imagined future caller. | Delete until a real second caller exists. |
| Message chains | `a.b().c().d()` walks a structure the caller should not know. | Hand the caller what it actually needs, or hide the walk behind the owner. |
| Middle man | A layer that only forwards to another layer. | Collapse it; talk to the real owner. |
| Refused bequest | A subtype that stubs, ignores, or overrides most of what it inherits. | Replace the inheritance with composition or split the interface. |

## How to report one

- Name the smell, cite the evidence (`path`, `line_range`, and what shows it),
  and say what the fix would be - as a finding, usually `P2`/`P3` unless the
  smell hides a correctness risk.
- One instance is a question; a pattern is a finding. Prefer the site where the
  next change will hurt.
- Do not report a baseline smell the repository's standards explicitly accept;
  cite the standard instead and move on.
- New code matching surrounding style beats abstract purity: a smell the whole
  file already commits to belongs in a follow-up scope question, not a blocking
  finding on this diff.

## Boundary

A smell finding is a maintainability judgement over the diff, not execution,
verification, CI, or merge evidence, and never blocks on its own unless the
reviewed repository's standards say it does.
