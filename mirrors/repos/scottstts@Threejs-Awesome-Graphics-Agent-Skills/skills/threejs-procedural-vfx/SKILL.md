---
name: threejs-procedural-vfx
description: Author production real-time VFX in Three.js. Use for ship-conforming reentry plasma, generated capsule wakes, instanced analytic sparks, timed dissolving debris, dense-swap effect pools, additive holographic projections, Fresnel rim shells, scanline banding, glitch displacement, swept shape-to-shape handovers, and explicit scene-relative HDR emission hierarchy.
---

# Procedural VFX

Build effects from an event envelope, motion field, geometry representation, and shading response. Avoid independent particle emitters that happen to share a color.

## Effect graph

```text
subject/event state
  → effect-specific geometry or instance attributes
  → flow-facing masks or analytic age
  → material response
  → pool/lifetime ownership
  → HDR and bloom contribution
```

Read [references/procedural-vfx-system.md](references/procedural-vfx-system.md)
for ship-conforming reentry shells, capsule wakes, dense instanced
spark/debris pools, holographic projection shells, HDR hierarchy, and
implementation limits.

Read the [reentry plasma implementation](examples/reentry-plasma/reentry-plasma.js)
for closed layered wake shells, flow-axis deformation, advected filament
fields, opacity shaping, and additive emission diagnostics.

Read the
[hologram projection material](examples/holographic-shape-transition/hologram-material.js)
for the additive rim shell itself: squared Fresnel incidence with grazing
falloff, footprint-filtered object-space scanlines, height-phased glitch
displacement, and index-gated participation. Read its
[shape-transition driver](examples/holographic-shape-transition/hologram-transition.js)
for the shared sweep range across a shape set, the linear progress ramp inside a
longer dwell, and the complementary-discard handover.

## Rules

- Every layer must have a role in silhouette, motion, illumination, or residue.
- Use normalized lifetime curves instead of scattered time constants.
- Derive secondary motion from the same flow or event direction.
- Keep bloom as a response to HDR emission, not as the effect's only shape.
- Pool instances and trails; do not allocate per burst.
- Filter every periodic band by pixel footprint, and fade it to the band's own
  mean rather than to zero.
- Measure rim incidence in a frame built from an inverse-transpose normal matrix.
- Give a multi-shape transition one shared normalised range and complementary
  discards, never per-shape ranges or overlapping coverage.
- Expose spawn, simulation, overdraw, and luminance debug views.
- Include a non-bloom baseline that remains legible.

## Routing boundary

Use `$threejs-temporal-surfaces` only for the screen-space
frost/touch-history pipeline. Use `$threejs-precipitation-surfaces` for
falling rain or snow, splash flipbooks, and weather events that alter ground
materials. Keep subject-space plasma, generated wakes, sparks, pooled debris,
and additive projection shells in this skill.
