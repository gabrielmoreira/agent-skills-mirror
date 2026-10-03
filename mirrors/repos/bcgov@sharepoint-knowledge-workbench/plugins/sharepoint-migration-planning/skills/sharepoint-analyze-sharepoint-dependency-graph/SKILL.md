---
name: sharepoint-analyze-sharepoint-dependency-graph
plugin: sharepoint-migration-planning
status: implemented
description: >
  Deterministically shapes a caller-supplied dependency-matrix object list into a computed wave order (reusing
  wave_planning.plan_waves directly), gated by completeness checks (source coverage, orphan matrix entries,
  unresolved lookup targets, destination-name collisions) that catch the matrix silently not matching the source
  it claims to describe. Use as stage 3a after inventory validation. Pure computation: no tenant I/O, no
  AI-model involvement, fully deterministic and testable.
allowed-tools: Bash, Read, Write
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from dependency_graph import load_matrix_objects, build_dependency_matrix; print(build_dependency_matrix(load_matrix_objects(raw_entries))['outcome'])\""
---

# Analyze SharePoint Dependency Graph

Stage 3a, the deterministic half of dependency analysis. The same input always gives the same output, which is why it is plain, tested Python and not an agent-assisted step.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Run `run_all_checks` BEFORE `build_dependency_matrix`, and stop if `all_passed` is false. A matrix that does not match its source must not drive wave computation.
- A cycle or a dependency naming a nonexistent object is `FAILED` with `blocking_findings`; never drop or guess around it. `load_matrix_objects` raises `MatrixValidationError` for a
  structurally malformed entry (caller error).
- No tenant I/O and no AI involvement. Run from this skill's root with `scripts/` on `sys.path`.

## Quick start

```python
import sys; sys.path.insert(0, "scripts")
from dependency_graph import load_matrix_objects, build_dependency_matrix
from completeness_checks import run_all_checks
objects = load_matrix_objects(raw_matrix_entries)
summary = run_all_checks(objects, source_names=observed_source_object_names)
matrix = build_dependency_matrix(objects) if summary.all_passed else None
```

## Workflow

1. Load the entries with `load_matrix_objects` (the output of the inventory stage's `matrix_objects`).
2. Run `run_all_checks(objects, source_names=...)`. If it fails, report `summary.failed_check_names` and stop.
3. Call `build_dependency_matrix(objects)` and report `{outcome, objects, waves, blocking_findings}`; it conforms to `assets/dependency-matrix-schema.json`.
4. Use the principles in `deployment-decision-principles.md` to decide whether a finding warrants a generated wave script or manual handling.

## Verification

Check `matrix["outcome"]` is `OBSERVED` and `blocking_findings` is empty. Validate the matrix against the schema when handing it to the next stage.

## References

- [Dependency graph details](references/dependency-graph-details.md): read for the full interface, why completeness checks block emission, and the script list.
- [Deployment decision principles](references/deployment-decision-principles.md): read when judging a completeness finding.
- [Test-driven wave deployment](references/test-driven-wave-deployment.md): read for why this half is deterministic and the other half is gated.
- [Matrix schema](assets/dependency-matrix-schema.json): read when checking the matrix shape.
