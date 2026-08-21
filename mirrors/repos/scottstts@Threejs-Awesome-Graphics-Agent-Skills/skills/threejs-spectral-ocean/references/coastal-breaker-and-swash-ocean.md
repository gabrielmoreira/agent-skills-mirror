# Coastal breaker and swash ocean

Use this reference when the defining view is the transition from open water to
wet sand: shoaling waves, persistent breaker foam, a moving waterline, a thin
swash film, and dry terrain must meet without a seam. Read the
`coastal-breaker-ocean` example with this contract; the wave field, coast,
swash state, foam history, and sand response are one coupled system.

## Contents

1. System ownership
2. Band-limited gravity field
3. Layer comb and wave motion
4. Coast representation
5. Shallow-water swash chain
6. Foam state
7. Camera-following geometry
8. Shoreline optics
9. Runtime order
10. Limits and failure patterns
11. Diagnostics

## 1. System ownership

Keep these mechanisms together:

```text
deterministic band fields
  -> moving gravity and capillary textures
  -> displaced deep-water grid
  -> signed-distance terrain and coast ribbons
  -> coast-normal shallow-water chains
  -> world-space and film-space foam history
  -> water / wet sand / dry sand optical blend
```

The `coastal-breaker-ocean` example owns every stage above. The surrounding
scene supplies a camera, the visible sky mesh, the animation delta, and the
two effect-owned sand textures. The ocean and visible sky evaluate the same
`coastalSkyRadiance` function and sun vector.

## 2. Band-limited gravity field

The gravity texture set contains five deterministic `256 × 256` half-float
RGBA fields. Their channels are:

```text
R = height h
G = horizontal particle displacement d
B = dh/dx
A = dh/dy
```

Each field begins as seeded white noise in frequency space. Rotate frequency
coordinates by one of `0°, -10°, 10°, -5°, 5°`, apply a narrow directional
band pass, and integrate horizontal displacement by dividing by
`1 - exp(-iω)` along the travel axis. The zero-frequency pole is harmless
because the band pass vanishes quadratically there.

The five fields form a geometric comb with `COPY_RATIO = 0.87`. Their seeds
are `12345`, `23456`, `34567`, `45678`, and `56789`. Normalize height to unit
variance, normalize every displacement channel by the coarsest displacement
standard deviation, and weight comb entries proportional to `0.87^k` with a
unit root-sum-square normalization.

The capillary field is an independent deterministic `256 × 256` isotropic
band pass with seed `54321`, smoothing scales `2` and `6` texels, and no
horizontal displacement channel.

## 3. Layer comb and wave motion

The calibrated wave controls are:

```js
const wave = {
  wavelengthMeters: 10,
  rmsAmplitudeMeters: 0.2,
  choppiness: 1.5,
  layerCount: 5,
  directionalSpreadDegrees: 40,
  directionDegrees: 0,
  dispersion: 1,
}
```

For gravity wavelength `λ`, use phase speed
`sqrt(g λ / (2π))`, with `g = 9.81 m/s²`. The layer ratio is exactly:

```text
LAYER_RATIO = (0.68^7 / 0.87^4)^(1/4)
```

Normalize layer amplitudes by the root-sum-square of all active
`LAYER_RATIO^i` weights so changing layer count changes comb density rather
than total variance. The eight possible direction offsets are
`[0, 0.9, -0.75, 0.45, -0.35, 0.7, -1, 0.2]` times the directional spread.

Capillary phase speed uses
`sqrt(g/k + 7.4e-5 k)` with `k = 2π/λ`. The three isotropic angles are
`0.4`, `-0.8`, and `1.7` radians; three aligned bands use spread fractions
`0`, `0.45`, and `-0.35`. Their wavelength scales are `1`, `0.72`, and
`0.52` from the `0.5 m` base ripple scale.

## 4. Coast representation

The static coastline has three synchronized representations:

1. an arclength-resampled mainland table with `2048` entries at `0.8 m`;
2. a clockwise `96`-column island loop;
3. a `512 × 512` half-float signed-distance field covering `±384 m`.

Land is the positive signed-distance side. Terrain height is:

```text
terrainHeight(xz) = clamp(0.15 * coastSDF(xz), -seaDepth, 3 m)
```

Outside the baked field, blend toward the far-field mainland line
`x - 10 m`. The mainland table extends along its endpoint tangents so a
camera-following ribbon does not terminate at the table edge.

Do not replace the coast-normal table with nearest SDF gradients. The swash
columns need stable arclength ordering and stable landward normals; filtered
SDF gradients alone do not provide either.

## 5. Shallow-water swash chain

The moving waterline is a heightless Lagrangian film with `256` coast columns
and `64` nodes per column. Mainland columns `0…159` cover a camera-following
`160 m` window; columns `160…255` wrap around the island.

The junction depth is `REST_DEPTH = 0.25 m`. With beach slope `0.15`, the
rest junction is `-0.25 / 0.15 m` from the static shoreline. Every segment
conserves its triangular-wedge rest volume. For current segment length `L`,
surface level is:

```text
eta = terrain(midpoint) + restVolume / L + shockViscosity
acceleration = -9.81 * d(eta)/dx
```

Use four substeps, friction `0.3`, quadratic compression viscosity `0.25`,
acceleration cap `25 m/s²`, velocity cap `6 m/s`, and viscosity cap `0.5 m`.
The driving sea level is low-pass filtered with a `1 s` time constant and its
speed is capped at `5 m/s`.

A linear spring chain is a failure: uniformly spaced nodes can balance while
the water piles up. Conserved segment volume makes a flat free surface the
unique equilibrium.

## 6. Foam state

Run two persistent ping-pong simulations:

```text
world foam   512 × 512 over a camera-following ±80 m square
film foam    128 × 256 over coast-normal distance and coast column
```

The world field generates from horizontal-displacement Jacobian compression
and shallow crest height. The film field generates from swash-chain
compression, masks beyond the moving tip, and accelerates decay where water
is swallowed back seaward. Both retain a smoothed generation pair alongside
the accumulated red/green lifetime pair.

The display pattern is deterministic seed `777`: bubble-raft web noise at
scales `2/6`, clumping at `3/9`, and fine breakup at `1/2.5`. Keep the
simulation field continuous; threshold the display pattern only during
shading.

## 7. Camera-following geometry

The deep grid is `512 × 512` cells with a `0.4 m` linear cell size for the
first `160` cells from center and `1.12` geometric growth afterward. Snap its
origin to `0.4 m` world increments. The material mirrors this warp with a
linear radius of `64 m` and growth `1.08` for shading footprint estimates.

The mainland and island ribbons are separate meshes. Their material
coordinates carry coast column, swash distance, and local cell width; the
vertex shader reconstructs world position from the coast tables and chain
state. Keep the deep grid, ribbons, island loop, and land mesh in the same
depth-writing render sequence.

## 8. Shoreline optics

Blend sand and water by the actual vertical water column:

```text
column = max(surfaceY - terrainY, 0)
waterMask = smoothstep(0.025 m, 0.09 m, column)
```

The sand tiles every `3 m`. Fade tangent-space normal detail from derivative
footprint once a pixel covers multiple texels. Under water, refract toward the
bed with index ratio `0.752`, apply Beer-Lambert transmission
`exp(-vec3(0.25, 0.04, 0.02) * pathLength)`, and focus two moving capillary
samples into caustic webbing. Above the water, retain dry-sand diffuse response.

Foam is a final material identity over both branches. World foam dominates
offshore; film foam is parameterized along the swash chain and persists over
wet sand. A detached screen-space shoreline decal cannot reproduce this
ownership.

## 9. Runtime order

Per frame, preserve this order:

```text
advance gravity and capillary copy phases
sample the previous completed layer cache to drive swash chains
update coast-relative chain state and data textures
update ocean uniforms and the next layer cache
render gravity and capillary composition targets
advance both foam ping-pong targets when delta > 0
render the sky and ocean scene
```

The one-frame completed-layer handoff into the swash driver is intentional.
Reordering it creates a split CPU/GPU wave state at the junction.

## 10. Limits and failure patterns

- The wave field is a deterministic directional band comb, not an FFT sea-state
  spectrum; route ocean-scale spectral synthesis to the cascade examples.
- The swash chain is heightless. It moves the surface and waterline but does not
  solve a full two-dimensional shallow-water height field.
- The baked coast is finite; its far-field mainland fallback must remain
  straight and compatible with the arclength table endpoints.
- Rebuilding foam from the current frame loses breaker streak lifetime.
- Sampling sand normals without derivative filtering sparkles at grazing range.
- Letting the orbit camera pass below the terrain exposes the ribbon skirts and
  invalidates the intended view.

## 11. Diagnostics

The example exposes:

```text
final       coupled ocean, swash, foam, and sand
normals     resolved water and terrain normals
foam        red = world accumulation, green = film accumulation, blue = display mask
shoreline   signed coast side plus the zero-distance band
wireframe   deep grid, mainland ribbon, island ribbon, and land topology
```

Use a fixed camera at `(-16.2400, 3.5806, 11.1104) m`, looking at the origin,
with `60°` vertical field of view for deterministic coast comparisons.
