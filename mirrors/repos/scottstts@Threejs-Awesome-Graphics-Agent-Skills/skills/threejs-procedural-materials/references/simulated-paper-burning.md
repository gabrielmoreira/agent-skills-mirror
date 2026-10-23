# Simulated Paper Burning

## Contents

- Material lattice and mechanics
- Combustion and fluid coupling
- Optical integration
- Integration contract
- Limits and failure patterns
- Diagnostics

## Material lattice and mechanics

The `simulated-paper-burning` example represents a 0.297 × 0.210 m sheet on a
256 × 182 material lattice. `buildSheet(20241)` builds the crumpled rest shape,
fracture cells, material heterogeneity and a 1024 × 724 half-float crease map.

Fuel, temperature, scorch and pyrolysis rate belong to this material lattice.
Constraint links, connectivity and triangle visibility consume the same burn
state. Keep char compliance, char damping, brittle failure, shrinkage and
detached flake motion coupled to it. A visually shrinking mask without the
mechanical response is a different material.

The driver advances at 1/60 s. Each frame performs eight pairs of combustion
passes, ten sheet substeps and two constraint iteration pairs per sheet
substep. Reset settles the sheet for 70 unlit mechanics frames before ignition.

## Combustion and fluid coupling

The pyro volume is 128 × 56 × 96 cells with 0.003125 m voxels. Its lower corner
is (-0.2, 0, -0.15) m. Sheet emissions feed fuel, heat and smoke into this
volume. Preserve advection, reaction, curl, forces, divergence, 24 pressure
iterations and projection in their implemented order.

The volume also builds a bounding box, a column representation and a ground
texture. These carry flame visibility, near/far fire illumination and deposited
soot. The finale uses asynchronous flame-density checks: visibility threshold
0.06, five seconds after the last visible flame before wind, then three seconds
of wind before reset. Preserve the playback clock separately from simulation
time so pauses do not advance this sequence.

## Optical integration

Paper shading reads the simulated vertex and normal buffers. Broken links
collapse spanning triangles. Toner modulates the paper stock through an
injected print texture, while fuel, char, temperature and crease detail remain
material-driven.

The compositor clips its volume march against the scene depth and computed
volume bounds. Its step is 0.0022 m, capped at 200 samples. Flame emission,
extinction and smoke scattering consume the same fluid state. The receiver
uses `fireLight(worldPosition)` and `FIRE_LIGHT_COL` so soot and indirect fire
illumination follow the burning sheet.

## Integration contract

Read [the implementation](../examples/simulated-paper-burning/simulated-paper-burning.js)
for sheet construction, mechanics, combustion, fluid transport, material
shading, volume imaging and the burnout sequence.

Create the effect with `{ renderer, scene, camera, printTex }`. The renderer
must use WebGPU and allow ten storage buffers per shader stage. Supply a
loaded sRGB print texture with anisotropy 8. The caller owns daylight lighting,
environment, floor textures, floor geometry and navigation. The calibrated
display uses ACES filmic tone mapping with exposure 0.8 and soft PCF shadows.

Use Three.js 0.186.1 consistently for the renderer, TSL and addons.

Call `update(deltaSeconds)` only during playback, followed by `render()`.
`ignite(worldHit)` accepts a point on the sheet plane; `reset()` restores the
full coupled state. `U` exposes the grouped physical and optical uniforms.
`fireLight()` and `FIRE_LIGHT_COL` are reusable receiver-shading inputs.

Keep the camera above the receiver surface during orbit and pan. The effect
owns no page UI or animation loop. Release it with `dispose()` and release
caller-owned textures and receiver objects separately.

```js
const burning = await createSimulatedPaperBurning({ renderer, scene, camera, printTex });
const { fireLight, FIRE_LIGHT_COL } = burning; // receiver material inputs
burning.update(deltaSeconds);
burning.render();
```

## Limits and failure patterns

- The sheet and pyro grids form one calibrated scale; changing only one changes
  emission placement, diffusion, contact and optical thickness.
- A delayed burnout readback must update only the finale instance that requested
  it; a reset invalidates an older result.
- A receiver without the soot and fire-light fields loses the combustion's
  visible effect on its surroundings.
- Volume extinction must stop at opaque scene depth rather than overlaying
  flames through the sheet or floor.

## Diagnostics

`setDebugMode()` accepts `final`, `nopost`, `sheet` and `ground`. `nopost`
shows the volume composite without bloom, vignette or grain. `sheet` shows
the surface pass without the volume, and `ground` shows the illumination/soot
field. These modes require no on-canvas controls.
