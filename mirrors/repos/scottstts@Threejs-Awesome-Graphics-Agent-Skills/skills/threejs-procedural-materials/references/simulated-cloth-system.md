# Simulated cloth system

Use this reference for a woven textile where yarn-scale PBR structure and a
deforming sheet use one calibrated world scale. The
[simulated cloth example](../examples/simulated-cloth/simulated-cloth.js)
contains the reusable effect and exposes the GPU solver and pointer methods.

## Contents

1. Coordinate and material contract
2. Plain-weave texture construction
3. Sheet state and constraint data
4. Integration and contact order
5. Cloth grabbing
6. Reusable API contract
7. Limits and observed failure patterns
8. Diagnostics
9. Failure diagnosis

## Coordinate and material contract

Use metres, seconds, and kilograms. The indexed sheet is a `96 × 96` grid over
`1.46 m × 1.46 m`; its interior spacing is `1.46 / 95 = 0.015368421 m`.
Its initial centerline clears a sphere with radius `0.30 m` by `0.02 m` at the
center. The rendered sphere is centered at `(0, 0.30, 0) m`. Keep this scale
shared by the mesh, collision parameters, texture pitch, camera, and cove.

The physical and solver constants are:

```js
const cloth = {
  vertices: 96 * 96,
  size: 1.46,
  arealDensity: 0.20,       // kg/m²
  thickness: 0.0004,        // m
  yarnTension: 8.0e6,        // Pa; geometric yarn lengths are enforced directly
  compression: 8.0e2,       // Pa
  shear: 1.2e4,             // Pa; increases as warp and weft lock
  bendingRigidity: 9.0e-5,  // N·m
  sphereRadius: 0.30,       // m
  sphereGap: 0.0016,         // m
  groundY: 0.0010,           // m
  selfThickness: 0.0024,     // m
  cellSize: 1.5 * (1.46 / 95),
  sphereFriction: 0.20,
  groundFriction: 0.32,
  airNormal: 1.15,
  airTangential: 0.12,
  damping: 0.16,
  maximumSpeed: 4.0,         // m/s
  hashCells: 131072,
  hashSlots: 32,
  strainIterations: 3,
  rigidSweeps: 2,
};
```

The physical material uses double-sided rendering, base-colour, tangent-space
normal, roughness, and AO maps, with normal scale `0.8`, AO strength `0.75`,
sheen `0.62`, anisotropy `0.42`, and zero metalness. Do not fold these channels
into the solver mesh: the grid carries macro folds; the maps carry yarn crowns,
slubs, and fiber-scale variation.

## Plain-weave texture construction

Bake four seamless `2048 × 2048` canvases once during setup. The weave has
`72` yarns across the sheet, so its pitch is `1.46 / 72 = 0.020277778 m` and
its cross-section radius is `0.34` pitch. At UV cell `(iu, iv)`, alternate the
upper yarn with parity `(iu + iv) & 1`. The upper half-round profile is
`sqrt(1 - x²) * radius` for `|x| < 1`; use `0.28` of the buried yarn's crown
between the upper crowns. Warp and weft slub multipliers are independently
`1 ± 0.09`, and the fine fiber height adds a deterministic hash variation of
`±0.04` yarn radii.

Derive all maps from this same height and weave identity:

- Albedo distinguishes warp and weft dye, adds slow per-yarn dye variation,
  darkens the hem inside `1.2%` of the UV edge, and shades low valleys.
- Normal uses central height differences at one texel and converts those
  derivatives to tangent-space xyz.
- Roughness is `0.93 - 0.34 * crown` with a small hash variation of `±0.02`.
- AO interpolates from `0.48` in valleys to `1.0` on a yarn crown.

Set the albedo canvas to sRGB. Keep normal, roughness, and AO in
`NoColorSpace`. Use clamp-to-edge wrapping, anisotropy `8`, and trilinear mip
filtering. The UV perimeter carries the deliberate hem treatment. The texture
is generated procedurally; there is no image dependency to fetch.

## Sheet state and constraint data

Build a regular grid with two indexed triangles per cell. Store current
position, previous position, velocity, two pin arrays, contact history, and
render-frame data in separate GPU buffers. The render geometry uses dynamic
position, normal, tangent, UV, and UV2 attributes; write the GPU output into
those buffers through the renderer backend. Keep the constraint topology
separate from the render indices.

The construction pass emits:

- horizontal and vertical yarn-length constraints with alternating graph
  colours, so no two constraints in one pass share a vertex;
- triangle shear constraints with a low free-sliding response and a stronger
  nonlinear response after the yarns lock;
- warp and weft bending constraints with three graph colours per direction;
- indexed triangle and edge lists for point-triangle and edge-edge contact;
- per-vertex inverse mass from `0.20 kg/m²`, cell area, and half-weighted
  boundary cells.

Use the exact rest edge length from `SPACING`. Structural relaxation is `0.96`;
free shear begins at `0.10`. Yarn stretch is enforced geometrically rather than
by a soft tension penalty. Bending uses a dual segment of length `SPACING` and
compliance derived from `9.0e-5 N·m`. The WGSL includes the full constraint,
hash, projection, and render-packing kernels; do not replace self-contact with
a vertex-only repel.

## Integration and contact order

Accumulate host time at `60 Hz`, cap elapsed time to `0.05 s`, perform no more
than two `1/60 s` integrations per call, and retain at most `1/30 s` backlog.
For each frame integration, choose
`round(frameDt / (1/240))` solver substeps and clamp to `3…6`. Each substep
runs this order:

1. Verlet-style position integration, velocity damping, and pin projection.
2. Three strain iterations: four parity-separated structural passes, one
   coupled shear correction, apply the accumulated correction, then horizontal
   and vertical bending passes.
3. Vertex sphere and cove projection.
4. On the final substep only, rebuild triangle and edge spatial hashes, solve
   point-triangle and edge-edge contacts, then perform two rigid triangle-sphere
   sweeps.
5. Final rigid vertex projection and velocity reconstruction.

The hash has `131072` buckets and `32` entries per bucket. Contact thickness is
`2.4 mm`; sphere and ground friction are `0.20` and `0.32`. The cove is a
piecewise analytic profile: flat ground, a `1.20 m` quarter-circle transition
at `z = -0.05 m`, then a vertical wall at `z = -1.25 m`. Project invalid
positions onto that profile so the sheet cannot pass through the display floor
or cove. Self-contact uses both vertex-triangle and edge-edge tests to protect
against fold-through.

## Cloth grabbing

`beginGrab(ndc)` performs one asynchronous GPU position readback and tests the
indexed triangles with a Möller-Trumbore ray test. Ignore intersections inside
the stone. Choose the nearest triangle vertex within `2 * SPACING` of the hit,
then pin its nearby vertices from a `3 × 3` grid neighborhood whose actual
separation is at most `2.5 * SPACING`. Construct the drag plane through the
selected vertex, perpendicular to the camera forward vector. `moveGrab(ndc)`
updates the target pin positions while preserving each vertex's local offset;
`endGrab()` clears the pin arrays. A miss returns `false`, allowing the caller
to assign empty-space drags to camera movement.

Only one asynchronous readback is allowed at a time. Release during the
readback cancels the pending grab. Keep camera movement disabled while a valid
grab is active so the drag plane stays stable.

## Reusable API contract

Call `createSimulatedCloth({ renderer, scene, camera })` after initializing a
Three.js WebGPU renderer. The returned object owns the cloth mesh, generated
maps, GPU buffers, WGSL pipelines, pause state, and interaction state. It
exposes `update`, `beginGrab`, `moveGrab`, `endGrab`, `reset`, `togglePaused`,
`setPaused`, `setWireframe`, and `setDebugMode`; call `dispose` when removing
the effect. `setDebugMode` accepts `final`, `albedo`, `normal`, `roughness`,
and `occlusion`. The caller must provide the initialized renderer, scene, and
camera. Keep renderer construction, stage geometry, and input listeners
outside this effect module.

## Limits and observed failure patterns

- This is WebGPU-only and uses `renderer.backend` GPU buffer access; it has no
  WebGL or CPU solver fallback.
- The fixed `96 × 96` topology and `131072 × 32` contact hash define its cost.
  The hash reports bucket overflow but does not grow or rebuild at a larger
  capacity.
- `MAX_SUB = 10` remains an exported constant, but the active CPU integration
  path clamps to six `1/240 s` substeps; changing `MAX_SUB` alone has no effect.
- The four full-resolution canvases use substantial setup memory and must not
  be regenerated every frame.
- The position snapshot used for picking can lag behind one queued simulation
  submission; only the latest completed snapshot is available to a new grab.
- A zero, negative, or `NaN` update delta falls back to `0.016 s`; call
  `setPaused(true)` to stop integration instead of relying on a zero delta.
- A moving camera during a pin can move the hit ray away from its fixed drag
  plane; freeze orbit while the grab is held.
- Excessive constraint softness stretches the yarn lattice; omitting the
  final-substep edge-edge pass permits dense folds to intersect.
- Independent noise in albedo, roughness, AO, or normals breaks the shared
  weave and makes the cloth look printed instead of woven.

## Diagnostics

The map selector exposes each PBR input without changing simulation state.
Wireframe exposes the `96 × 96` solver resolution, not individual fibers.
Reset restores initial positions, zeroes dynamic velocities, clears pins, and
empties the fixed-step accumulator. Pause stops integrations while retaining
the last rendered and inspectable shape.

Check the following when diagnosing a failure:

- `albedo`: warp/weft alternation, hem width, slub scale, and tile seam;
- `normal`: yarn crowns and valley transitions from the same height field;
- `roughness`: smoother crowns and rougher valleys without high-frequency
  speckling;
- `occlusion`: continuous valley darkening with no independent pattern;
- `wireframe`: stable grid winding and no collapsed or duplicated cells;
- GPU compilation messages and uncaptured device errors during pipeline setup
  and compute submission;
- sphere, floor, and cove contact during a large pull and a tight fold.

## Failure diagnosis

If the sheet tears visually while the grid remains connected, inspect the
normal and tangent buffers and the UV2 attribute before changing solver stiffness.
If it tunnels through the sphere, check the per-substep vertex projection and
the final triangle-sphere sweeps. If fold-through occurs away from the sphere,
check hash insertion overflow, self-thickness, and the final-substep
point-triangle plus edge-edge passes. If a drag misses, verify the current GPU
position buffer mapping and the camera's NDC conversion before widening the
vertex-selection radius.
