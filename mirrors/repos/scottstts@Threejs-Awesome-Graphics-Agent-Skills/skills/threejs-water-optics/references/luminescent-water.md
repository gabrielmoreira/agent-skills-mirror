# Luminescent Water

## Contents

- Coupled flow and light
- Geometry and optical receivers
- Integration contract
- Limits and failure patterns
- Diagnostics

## Coupled flow and light

The `luminescent-water` example evolves a staggered shallow-water grid of
512 × 1024 cells at 0.01 m spacing. The domain is 5.12 × 10.24 m; its x origin
is 2.56 m inside a 10.24 m wide terrain tile. The z direction repeats.

Retain the velocity, positivity-scale and height pass order. A frame advances
at 1/60 s with eight hydrodynamic substeps. Transport the luminous excitation,
foam, turbulence and wetness fields with the same flow. The scalar path uses
MacCormack transport, and two displacement layers carry sub-grid detail with
resets at zero blend weight. Do not replace this transport with scrolling UVs.

`generateDetail()` builds a 512 × 512 half-float map. Height, normalized slopes
and foam cells remain coupled; its three height octaves avoid unresolved
caustic sparkle. Keep the 240-frame flow pre-roll before displaying the system.

## Geometry and optical receivers

Surface displacement, shading normals, advected detail and caustics consume
the exported simulation fields. Caustic meshes refract through indices 1.331,
1.334 and 1.338 into separate RGB contributions. A 1024 × 2048 target receives
the additive differential-area projection.

The terrain receiver is part of the optical coupling: its wetness, luminous
irradiance, submerged appearance and displaced bed cannot be replaced with an
unlit plane. The water material combines refracted bed radiance, absorption,
inscattering, luminescent film, reflection and flow-driven foam. Preserve the
shared bed-height function in the simulation and optical paths.

## Integration contract

Read [the implementation](../examples/luminescent-water/luminescent-water.js)
for the transport kernels, coupled bed shading, skirted LOD geometry and
optical compositor.

This example uses Three.js 0.180.0 and its `PostProcessing` compositor. Keep
the renderer, TSL, controls and display addons on that same revision.

`createLuminescentWater()` accepts an initialized WebGPU `renderer`, caller-owned
`scene` and `camera`, and these inputs:

- `terrain.tex`: half-float RGBA macro height, x slope, z slope and rock mask;
  `terrain.H`: the matching 1024 × 1024 CPU height array in metres.
- `colorTex`, `normalTex`: repeating rock albedo and normal textures.
- `packTex`: displacement, roughness and AO in RGB; `packMean` is the mean
  normalized displacement channel. Texture scale is 1.6 m per tile.
- `env`: an equirectangular radiance texture used by the reflection calculation.

The caller supplies scene lighting and fog. The calibrated optical settings
use ACES filmic tone mapping at exposure 1.05. The compositor tone maps before
FXAA, then applies grain; do not apply another output transform afterward.

Call `update(deltaSeconds)` before `render()`. Catch-up is limited to two
fixed frames. `stir(worldHit, velocityXZ)` injects the same flow disturbance
used by excitation; `endStir()` ends it. The frame path advances simulation
and draws caustics before the final composite without GPU buffer readbacks.

The caller owns texture loading, navigation and camera bounds. Keep the lens
above both the displaced terrain and current water surface. Call `dispose()`
when releasing the effect; separately release caller-owned input textures.

```js
const water = await createLuminescentWater({
  renderer, scene, camera, terrain, colorTex, normalTex, packTex, packMean, env,
});
water.update(deltaSeconds);
water.render();
```

## Limits and failure patterns

- This is an air-side river system with periodic z boundaries, not an
  underwater camera-medium transition.
- A camera clamp against a zero-height plane alone can enter waves or rock.
- Independent water and terrain texture scales break refraction and wetness.
- Removing the bed, RGB caustics or film-driven receiver light changes the
  defining optical system.
- Navigation can use the periodic CPU terrain lookup and a 0.14 m clearance
  above the larger of terrain height and the nominal zero-metre water level.
  Do not block each frame on a full simulation-grid readback.

## Diagnostics

`setDebugMode()` accepts `final`, `nopost`, `caustics` and `glow`. Inspect the
raw caustic and low-resolution luminous fields before adjusting final bloom.
The `nopost` path keeps tone mapping while bypassing bloom, FXAA and grain.
