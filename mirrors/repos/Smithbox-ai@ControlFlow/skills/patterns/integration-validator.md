# Integration Validator Patterns

## Purpose
Catch cross-task incompatibilities before execution: dependency cycles, data-flow contract breaks, file collisions, and interface mismatches between phases.

## Dependency Graph Validation

Build a phase dependency graph from the plan's `wave` and `dependencies` fields:

1. Create a node for each phase.
2. Add a directed edge for each declared dependency.
3. Run cycle detection (DFS with back-edge tracking).

**Violation rules:**
- A cycle → BLOCKING (plan cannot execute).
- A phase in Wave N depending on a phase in Wave N+1 → BLOCKING ordering conflict.
- A declared dependency that is missing from the plan → MAJOR gap.

## Data Flow Contract Checks

For each pair of phases where Phase B depends on Phase A:
- Identify the output artifact from Phase A (file path, schema type, return shape).
- Verify Phase B's input expectation matches Phase A's output format.
- Mismatched types or shapes → MAJOR finding.

Examples:
- Phase A produces `governance/tool-grants.json` (JSON object keyed by filename) → Phase B reads it expecting the same key shape.
- Phase A creates `skills/index.md` → Phase B runs validate.mjs which reads `skills/index.md` — format must be compatible.

## File Collision Detection

Within a single wave (parallel phases), check every file listed under **Files** across all phases:
- If two parallel phases target the same file → BLOCKING collision.
- Any file overlap that requires serialization must be moved to different waves.

Detection:
1. Collect all file paths modified in Wave N across all phases.
2. Sort and find duplicates.
3. Each duplicate is a collision — BLOCKING unless the overlap is read-only on one side.

## Shared Resource Conflict

Beyond file paths, check for:
- Same validator pass modified by two parallel phases (e.g., both adding to `requiredArtifacts`).
- Same agent prompt section edited by two parallel phases.
- Emit MAJOR for any shared write resource between parallel phases.

## Interface Contract Verification

For functions or schemas produced in one phase and consumed in another:
- Verify exported symbol names, schema `$id` values, and JSON key names are stable.
- If a phase renames a key that the next phase reads → MAJOR contract break.

## Acceptance Signal

An integration-valid plan passes all of:
1. Zero dependency cycles.
2. Zero wave-ordering conflicts.
3. Zero parallel-phase file collisions.
4. Data flow types match at all phase boundaries.
5. No renamed interface contracts consumed by downstream phases.
