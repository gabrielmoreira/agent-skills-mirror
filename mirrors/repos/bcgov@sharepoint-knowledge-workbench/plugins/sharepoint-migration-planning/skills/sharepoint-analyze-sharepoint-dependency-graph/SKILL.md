---
name: sharepoint-analyze-sharepoint-dependency-graph
plugin: sharepoint-migration-planning
status: implemented
description: >
  Deterministically shapes a caller-supplied dependency-matrix-shaped
  object list into a computed wave order (reusing sharepoint-provisioning's
  wave_planning.plan_waves directly, not reimplemented), gated by a set of
  completeness checks (source coverage, orphan matrix entries, unresolved
  lookup targets, destination-name collisions) that catch the matrix
  silently not matching the source it claims to describe. Pure computation
  -- no tenant I/O, no AI-model involvement, fully deterministic and
  testable.
allowed-tools: Bash, Read, Write
---

# Analyze SharePoint Dependency Graph

Stage 3a — the **deterministic half** of dependency analysis. Same input
always produces the same output; this is why it is plain, TDD-tested
Python, not an agent-assisted step (see
`../generate-sharepoint-wave-scripts/SKILL.md` for the AI-assisted half, and
`../../rules/test-driven-wave-deployment.md` for why this split matters).

## Public interface

```python
from dependency_graph import load_matrix_objects, build_dependency_matrix
from completeness_checks import run_all_checks

objects = load_matrix_objects(raw_matrix_entries)  # validates required fields, raises MatrixValidationError with the offending name/index

# Run completeness checks BEFORE trusting the matrix enough to compute a wave order --
# these catch problems plan_waves has no visibility into (the matrix vs. the source it
# claims to describe), distinct from plan_waves' own unresolved-dependency/cycle checks.
summary = run_all_checks(objects, source_names=observed_source_object_names)
if not summary.all_passed:
    # report summary.failed_check_names and stop -- do not proceed to wave computation
    # against a matrix known not to match its source
    ...

matrix = build_dependency_matrix(objects)
# {"outcome", "objects", "waves", "blocking_findings"} -- conforms to
# assets/dependency-matrix-schema.json
```

## Completeness checks block matrix emission on failure

A completeness failure (source coverage, orphan entries, unresolved lookup
targets, destination-name collisions) means the matrix does not accurately
describe the source it claims to, and downstream wave computation would be
building on a wrong premise. Callers must run `run_all_checks` and stop on
`all_passed is False`, rather than proceeding straight to
`build_dependency_matrix` — see `completeness_checks.py`'s module docstring
for why this is a distinct concern from `wave_planning.plan_waves`'s own
unresolved-dependency/cycle detection (which only sees the graph it is
given, never the source it was supposed to be derived from).

## Honest outcomes

A cycle or a dependency naming a nonexistent object is reported explicitly
via `blocking_findings` and `outcome=Outcome.FAILED` (matching
`wave_planning.py`'s existing behavior), never silently dropped or guessed
around. `build_dependency_matrix` never raises for a bad dependency graph;
`load_matrix_objects` does raise (`MatrixValidationError`) for a
structurally malformed raw entry, since that is caller input error, not a
planning outcome to report gracefully.

## Scripts

- `scripts/dependency_graph.py` -- `load_matrix_objects`, `build_dependency_matrix`, `MatrixValidationError`
- `scripts/completeness_checks.py` -- `run_all_checks`, and the four individual checks it composes
- `scripts/wave_planning.py` -- authored in this plugin (moved from `sharepoint-provisioning`
  2026-08-08, which never called it internally; see `plan-sharepoint-deployment-waves`'s provenance)
- `scripts/provisioning_outcomes.py` -- reused directly from `sharepoint-provisioning` via a
  managed file symlink (see `symlinks.json`), not reimplemented

## Rules

See `../../rules/deployment-decision-principles.md` for the three
principles that should guide whether a completeness finding warrants a
generated wave script (`generate-sharepoint-wave-scripts`) or a
recommendation for manual handling.

## Provenance

`dependency_graph.py` and the matrix shape itself are new design work,
generalizing the *concept* of a hand-curated dependency matrix observed in
a separate SharePoint migration repository (that file was hand-curated
there — no script built it automatically). `completeness_checks.py`
generalizes the shape-agnostic subset of an 18-check completeness QA gate
found during the Phase 9 exhaustive source audit
(`temp/phase9-source-audit/file-tracking.json`); the project-specific
business-rule checks in that source were deliberately not ported (see the
module's own docstring).

