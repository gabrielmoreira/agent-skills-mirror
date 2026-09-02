# Cleanup Passes

The pass contract for slop cleanup. One smell category per pass, verification
between passes, never bundled - a diff that deletes dead code AND renames AND
reshuffles tests cannot be reviewed for behavior preservation, and reverting
one mistake reverts all three.

## The taxonomy (classify before deleting)

| Category | What it looks like | Default treatment |
| --- | --- | --- |
| Duplication | The same decision encoded twice; near-identical helpers with drifted edges. | Keep one owner, delete the copies; lookalikes encoding different decisions stay. |
| Dead code | Unused symbols and imports; unreachable branches; commented-out blocks (version control preserves history); feature flags nothing reads. | Delete outright; no deprecation shims for code with zero callers. |
| Needless abstraction | Single-use helpers, single-implementation interfaces, layers that only forward, config for values that never vary. | Inline and delete; re-extract only when a real second caller exists. |
| Boundary violation | Reaching into another module's internals; circular imports; logic in the wrong layer. | Repair the boundary with the existing surface; a boundary-CHANGING fix routes to `ralplan` first. |
| Missing tests | Behavior with no lock; tests asserting implementation details or nothing at all. | Add the behavior lock in the test-reinforcement pass; delete assert-nothing tests as dead code. |
| Templated defaults | Boilerplate comments restating the code, placeholder docstrings, copy-pasted config blocks nothing uses. | Delete; a comment survives only when it states what the code cannot. |

## Detection, when no smell was named

Hand back an inventory before editing anything. Prepared commands, per stack -
prepared_not_observed until their exit status and output are seen:

- Python: the repo's own lint gate first (often `ruff check` with unused-import
  and unused-variable rules), `vulture` for dead symbols where available,
  plus a grep for `noqa`/`type: ignore` clusters and commented-out blocks.
- JS/TS: the repo's ESLint gate, `knip` for unused exports/files/dependencies
  where available, `tsc --noEmit` for dead branches behind narrowed types.
- Any stack: the version-control question - `git log --follow` on suspicious
  files; code no commit has touched since its introduction and no caller
  imports is the first deletion candidate.

Detector output is a candidate list, not a verdict: every candidate gets a
caller check before it enters the inventory.

## The passes, in order

1. **Dead code** - deletion only. No renames, no moves. The diff should be
   almost entirely red. Re-verify.
2. **Duplicates** - collapse each duplicated decision to one owner; call sites
   move to the survivor. Re-verify.
3. **Naming and error handling** - rename what misleads, surface what is
   swallowed; no structural moves in this pass. Re-verify.
4. **Test reinforcement** - add the missing behavior locks found in pass 1-3,
   delete tests that assert nothing. Re-verify.

Stop between passes when the regression checks fail: fix or revert that pass
before opening the next. Never carry a red gate forward.

## Scope contract

A user-supplied file list is the whole territory. Findings outside it are
listed under "out of scope" in the closing report - never edited, and never
used to justify widening the diff.

## Closing report

Four parts, every run: **changed files** (with per-pass counts),
**simplifications** (what was deleted or collapsed, by category),
**behavior lock** (the commands run before and after, with observed results),
**remaining risks** (what was found and deliberately not touched, and why).

## Boundary

An inventory, pass plan, or prepared detector command is prepared context;
behavior preservation is claimed only from the observed before/after
verification, and a cleanup diff is never review, CI, or merge evidence.
