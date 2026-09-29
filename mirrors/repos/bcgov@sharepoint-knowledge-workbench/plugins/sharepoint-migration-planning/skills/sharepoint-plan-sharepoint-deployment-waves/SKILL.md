---
name: sharepoint-plan-sharepoint-deployment-waves
plugin: sharepoint-migration-planning
description: Computes a deployment wave plan by topologically sorting a caller-supplied, dependency-annotated list of deployment objects -- groups objects into ordered stages where every dependency is satisfied by a strictly earlier stage, and honestly reports cycles or unresolved dependencies instead of guessing an order. Pure computation, no tenant I/O.
allowed-tools: Bash, Read
examples:
  - "python -c \"from wave_planning import plan_waves; print(plan_waves(objects).to_dict())\""
---

# Plan SharePoint Deployment Waves

## Trigger and Purpose

Use this skill when you have a set of SharePoint deployment objects (site
columns, content types, lists, or any other caller-defined object type) with
declared dependencies on each other, and need a safe, provably-correct
deployment order -- without hand-maintaining a fixed step list.

**Real-world motivation:** a hand-maintained deployment step list can
silently drift from the scripts it references. A master orchestrator can
keep listing objects/scripts by name in a fixed order long after some of
those names have been consolidated, renamed, or removed -- nothing catches
the drift until the orchestrator is actually run against a live tenant, at
which point it fails (or worse, silently skips work). Computing the
deployment order from a dependency graph, rather than hand-encoding each
object's position in a separate list, removes this entire class of staleness
bug: an object that no longer exists, or a dependency that doesn't resolve,
is reported as a planning failure before anything is ever run.

Stage: independent of `sharepoint-provisioning`'s `provision-fields` /
`provision-content-types` / `provision-list` -- this skill only computes
ORDER. It does not plan or apply any actual field/content-type/list change
itself; feed its output order into those skills' own planning, in stage
order. This skill and `analyze-sharepoint-dependency-graph` (stage 3a, in
this same plugin) share `scripts/wave_planning.py` directly -- both are the
pure-planning half of this workbench's plan/apply split; provisioning
consumes a finished wave order as an input, it does not produce one.

## Honest outcomes

| Outcome | Meaning |
|---|---|
| `EMPTY` | No objects were supplied -- nothing to order |
| `OBSERVED` | Every object's dependencies resolved; a full stage order was computed |
| `FAILED` | A dependency named an object absent from the input, or the graph contains a cycle -- `blocking_findings` explains exactly which |

`plan_waves` never raises on a bad input graph and never silently drops or
guesses an order for an unresolvable object -- a cycle or an unresolved
dependency name always surfaces as a `FAILED` plan with a specific,
human-readable finding, mirroring this plugin's existing
`detect_duplicate_lists` honesty pattern in `list_provisioning.py`.

## Dependencies are declared by object name only

`DeploymentObject.depends_on` names other `DeploymentObject`s by `name`
only. A caller declares "depends on this specific named thing," never
"depends on some earlier numbered stage" -- the latter is exactly the kind
of hand-maintained coupling (a stage number standing in for its contents)
that goes stale silently. See `scripts/wave_planning.py`'s module docstring
for the source ambiguity this deliberately does not carry forward.

## Usage

```bash
python -c "
from wave_planning import DeploymentObject, plan_waves

objects = [
    DeploymentObject(name='SiteColumnA', object_type='SiteColumn'),
    DeploymentObject(name='ContentTypeB', object_type='ContentType', depends_on=('SiteColumnA',)),
    DeploymentObject(name='ListC', object_type='List', depends_on=('ContentTypeB',)),
]

plan = plan_waves(objects)
print(plan.outcome, plan.to_dict())
"
```

## Scripts

- `scripts/wave_planning.py` -- `DeploymentObject`, `WavePlan`, `plan_waves`, `CycleDetected`, `UnresolvedDependency`

## Provenance

New-build work generalizing a pattern observed in a separate repository's
migration orchestrator (a hand-maintained, fixed-order deployment step
list that had silently drifted from the actual, consolidated set of
deployment scripts). This is **not** a code port -- no code, object names,
or domain content from that repository was carried over; only the general
principle (compute order from a dependency graph, don't hand-maintain a
step list) was generalized into this module. No entry is needed in the
Phase 9 `provenance.md` for this reason.

**Moved from `sharepoint-provisioning` to this plugin, 2026-08-08** (external
architecture review + user decision): `wave_planning.py` and its skills were
originally authored in `sharepoint-provisioning`, symlinked into this plugin.
Nothing in provisioning's own field/content-type/list/calendar provisioning
logic ever called `plan_waves` directly -- only this skill did -- so once
`analyze-sharepoint-dependency-graph` (this plugin) took on the completeness-
check and dependency-graph-shaping logic built on top of the same module,
provisioning was left exposing a skill it didn't itself depend on, while
the plugin that actually built on `wave_planning.py` was one symlink hop
away from it. Moved here so the whole pure-planning pipeline
(dependency-graph shaping -> completeness checks -> wave order) lives in one
plugin; `sharepoint-provisioning` now consumes a computed wave plan as an
input to its own gated apply, rather than producing one.

