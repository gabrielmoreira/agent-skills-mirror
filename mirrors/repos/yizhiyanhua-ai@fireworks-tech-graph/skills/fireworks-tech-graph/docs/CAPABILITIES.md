# Capability contract

## Input

- Legacy JSON remains supported and normalizes to schema v1.
- Versioned input uses `schema_version: 1` and a `mode` matching the selected renderer.
- Duplicate IDs, dangling references, non-finite coordinates, malformed waypoints, and unknown schema versions fail before layout.
- Style-specific fields and unknown renderer extensions are preserved.
- `style` and `visual_theme` resolve through one catalog covering Styles 1–12; unknown or conflicting selectors fail closed.

## Engineering semantics

- Style 9 defaults to `c4-review`: one C4 level, typed elements, responsibilities, technologies, and protocols.
- Style 10 defaults to `cloud-fabric`: acyclic deployment boundaries, explicit workload ownership, versioned neutral icons, and named cross-boundary mechanisms.
- Style 11 defaults to `event-transit`: ordered topic rails, declared junctions, consumer groups, state projections, and real DLQ targets.
- Style 12 defaults to `ops-pulse`: exact golden signals, one contiguous business critical path, separate telemetry semantics, and a valid trace tree.
- `semantic_profile: "generic"` keeps any generator-backed visual theme available for internal topology regression without pretending domain semantics are present.

## Geometry

- All generated business edges are rectilinear outside declared bridge arcs.
- `route_points` are exact ordered waypoints; every leg is routed safely.
- Nodes, section headers, legends, title blocks, footers, labels, and the canvas boundary participate in layout checks.
- Distinct ports are allocated deterministically for shared node sides.
- Collinear edge overlap is fatal. Proper crossings receive a visible bridge and background mask.
- Layout output and reports are deterministic for the same input.

## Output

- SVG is the canonical artifact and carries `data-graph-role`, style, diagram-type, semantic-profile, semantic-role, edge-kind, topic, and critical-path metadata.
- PNG export uses CairoSVG or `rsvg-convert` in the shell workflow.
- Offline interactive HTML supports pan, zoom, reset, light/dark themes, SVG copy, and SVG/PNG/JPEG/WebP export at 1×–4×.
- Interactive export rejects active elements, event handlers, external references, `foreignObject`, and external CSS.

## Distribution

- Git clone and npm archives contain the complete skill.
- The committed `skills/fireworks-tech-graph/` mirror supports deterministic `npx skills add` subpath installation for Codex and Claude Code.
- npm `.tgz` and GitHub release `.zip` are built from the same payload and checked by file hash.
