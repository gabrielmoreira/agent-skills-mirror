# Luminescent Jellyfish

## Contents

- Anatomy and motion
- Tissue and surrounding medium
- Layer compositor
- Integration contract
- Limits and failure patterns
- Diagnostics

## Anatomy and motion

The `luminescent-jellyfish` example couples bell geometry, swimming, photocyte
emission and simulated appendages. One unit is approximately 0.15 m, the hero
bell's characteristic radius. Each animal has 32 tentacles and four oral arms;
each chain has 32 simulation nodes.

Bell contraction deforms the inner and outer tissue together. CPU Verlet
chains follow their attachment points, flow and collision constraints. Float
textures carry chain positions and frames to the shaded geometry. Keep the
Catmull–Rom sampling and ribbon frames coupled to the same uploaded state.

Advance mechanics at 1/60 s, with an eight-second initial warmup and a
three-step catch-up cap. Preserve the seeded layout, contraction phases,
body transforms and light updates; the glowing core is an emitter moving
with the animal rather than a view-facing painted spot.

## Tissue and surrounding medium

The bell profile thickness is exactly `0.20 * (1 - s) ** 1.4 + 0.012` in bell
radius units. Face-specific optical paths, refractive offsets, pigment
absorption, frosted forward scatter and tissue emission share this anatomy.

The water attenuation coefficients are (0.075, 0.034, 0.024) per scene unit.
Path radiance integrates the photocytes and camera-mounted lamps. Marine snow
and bubbles share the same medium and lens response; preserve their depth
placement relative to the translucent animals.

## Layer compositor

Begin with half-resolution water path radiance. Sort animals far to near and
draw each intervening particle depth slice before compositing the next animal.
Each tissue layer carries radiance plus auxiliary refraction and optical-depth
data. The auxiliary attachment uses additive blending, and empty optical depth
must clear to zero.

Blur a layer using its own circle of confusion before attenuating and
refracting the accumulated image. The final path applies near/wide veiling
glare, port distortion, lateral colour, vignette, exposure and grain. Applying
one full-frame blur after compositing would destroy the depth ordering.

## Integration contract

Read [the implementation](../examples/luminescent-jellyfish/luminescent-jellyfish.js)
for bell construction, swimming, Verlet appendages, tissue shading, medium
transport, particles and the ordered layer compositor.

Create with `{ renderer, camera, seed = 7, msaa = 4, fullRect = false,
blur = true }`. The caller owns its WebGPU renderer, navigation and camera;
use AgX tone mapping at exposure 1. The compositor owns every clear, so set
`renderer.autoClear = false` and a transparent black clear colour.

Use Three.js 0.186.1 consistently for the renderer, TSL and addons. The MRT
contract requires `setClearColor()` on each attachment as well as per-attachment
blend modes; a renderer that lacks the clear API cannot execute this compositor.

Call `resize({ bufferWidth, bufferHeight })` before the first frame and whenever
the drawing buffer changes. The effect derives pixel angle, refraction scale,
blur scale and all render-target sizes from those dimensions and camera FOV.
Call it again if FOV changes independently of buffer size.

After updating the camera matrices, call `update(deltaSeconds, orbitTarget)`
and `render()`. The orbit target selects the nearest bell for eased autofocus.
Camera-mounted light positions and view-centred particles follow that camera.
Call `dispose()` when releasing the system.

```js
const animals = await createLuminescentJellyfish({ renderer, camera, seed: 7, msaa: 4 });
animals.resize({ bufferWidth, bufferHeight });
camera.updateMatrixWorld();
animals.update(deltaSeconds, orbitTarget);
animals.render();
```

## Limits and failure patterns

- This optical system assumes a submerged observer; it does not implement an
  air/water interface crossing.
- Clearing auxiliary alpha to one creates nonzero optical depth in empty layers.
- Rendering all particles as one background loses the animals' depth slices.
- A camera FOV or DPR change without resizing produces incorrect refraction,
  ribbon widths and optical blur.
- A failed scissor or MRT restoration contaminates subsequent layer passes.

## Diagnostics

`setDebugMode()` accepts `final`, `nopost`, `no-water-blur` and `no-defocus`.
`nopost` retains the tissue/medium compositor and tone mapping, bypassing the
final lens treatment. The other modes isolate medium blur and lens defocus
without changing swimming or appendage mechanics.
