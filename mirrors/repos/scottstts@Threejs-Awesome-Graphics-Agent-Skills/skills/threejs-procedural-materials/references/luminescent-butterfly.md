# Luminescent Butterfly

## Contents

- Wing identity and articulation
- Microfacet glints and emitted light
- Lens and exposure
- Integration contract
- Limits and failure patterns
- Diagnostics

## Wing identity and articulation

The `luminescent-butterfly` example uses centimetres. Forewing and hindwing
masks are painted procedurally at 2048 texels along the longest dimension.
Outline, veins, pigment, luminous spots and corrugation normals share one
wing layout. Keep coverage and microstructure attached to the wing surface.

Both wings on a side share a hinge at x = ±0.16 cm, y = 0.64 cm. Forewings
lead by four degrees. The stroke envelope is `6 * Math.PI / 180 - 0.02` to
`46 * Math.PI / 180 + 0.02` radians, including tremor. The seeded resting
timeline has holds, partial flicks and unequal opening/closing durations.
`wingPose()` drives deformation, perch clearance and the geometry audit.

The articulated body includes segmented anatomy, fur, antennae, tarsal contact
and tibial spines. Perch placement tests complete-stroke clearance rather than
only the initial pose. The caller supplies the static perch mesh and its
matching geometry; the butterfly owns the pose and contact calculation.

## Microfacet glints and emitted light

The wing scale lattice is approximately 0.024 × 0.016 cm. Resolved scales and
subpixel stochastic glints use the same slope distribution. Unresolved glints
use Poisson statistics tied to footprint cells and reflection direction, with
the mean matched to smooth microfacet reflection. Environment glints sample
the same radiance environment used by the surrounding surfaces.

`wingEmission()` integrates the actual mask-dependent emission and its
centroid. Wing-mounted lights use equivalent radius `sqrt(area / Math.PI)`
and intensity equal to integrated radiance-area divided by two. Their
finite-distance law and two-sided cosine lobe illuminate nearby receivers
without a point-light singularity. Airborne scattering uses those same
moving emitters.

## Lens and exposure

The lens shares focus and aperture between gathered defocus, scattered bright
highlights and explicit emitter sprites. The nine-blade aperture includes
rounded blades, field-angle clipping, normalized front/rear profiles and
longitudinal chromatic tint. GTAO attenuates indirect illumination while direct
lights keep their own shadows.

A 64 × 36 HDR luminance meter reads asynchronously every 12 frames. Exposure
uses weighted log luminance, middle gray 0.18 and compensation -2.8 EV, bounded
to 0.05–2.0. Adaptation rates are 3.2 toward increasing exposure and 1.1 toward
decreasing exposure. Bloom threshold is divided by current exposure. Preserve
the single AgX output transform and the ordering of lens imaging, glare and
exposure adaptation.

## Integration contract

Read [the implementation](../examples/luminescent-butterfly/luminescent-butterfly.js)
for wing painting, scale glints, anatomy, articulation, perch clearance, finite
wing emission, particle optics, the lens compositor and swept-geometry audit.

Use Three.js 0.186.1 consistently for the renderer, TSL and display addons.

Create with caller-owned `renderer`, `scene` and `camera`, plus:

- `perchMesh`: the static, world-transformed contact mesh;
- `perchSurface.geometry`: the same indexed geometry used by `perchMesh`;
- `perchCenter`: a world-space point establishing the subject's facing;
- `hero.cam`: a configured framing camera used for the normalized perch pick
  at (0.414, 0.497), measured from the image's top-left corner;
- optional async `setupStage(context)`: receives `hero`, `raycaster`, `bfly`,
  `dustMoon`, `spriteCloud` and the grouped parameters `P`. Use it to finish
  scene emitters and an environment probe after placing the butterfly.

`spriteCloud()` builds coherent luminous or scattering particles. If the
callback uses these, finish the environment capture before returning; their
materials then switch into the dedicated lens emitter attachment.

The caller owns all surrounding geometry, texture loading, lights and
navigation. Supply an environment for reflected scale glints and shadow maps
for wing illumination. `LUMINESCENT_BUTTERFLY_DEFAULTS` exposes the calibrated
parameter groups. `taperTube()` provides the same tapered curve geometry used
by appendages.

Call `update(deltaSeconds, orbitTarget)` before `render()`. The latter renders
the optical pipeline before advancing its exposure meter. `auditButterfly()`
returns the complete-stroke intersection report without adding UI. Dispose
the effect, then separately release caller-owned scene resources.

Keep viewing resolution adaptive: begin at `min(devicePixelRatio, 2)`, measure
FPS every 500 ms, and lower DPR by 0.25 after four consecutive windows below
40 FPS. Raise it by 0.25 after seven windows above 100 FPS, bounded between
1 and `min(devicePixelRatio, 2)`. The runtime owns this policy; its resizing
must preserve the effective DPR rather than restore a fixed value each frame.

```js
const butterfly = await createLuminescentButterfly({
  renderer, scene, camera, perchSurface, perchMesh, perchCenter, hero, setupStage,
});
butterfly.update(deltaSeconds, orbitTarget);
butterfly.render();
const intersections = butterfly.auditButterfly();
```

## Limits and failure patterns

- Perch transforms must be current before construction; stale matrices corrupt
  clearance and foot placement.
- Perch clearance is a bounded pose search. When adapting the perch, inspect
  `bfly.userData.clearance.cost` for a finite solution and run the independent
  complete-stroke audit; the search does not guarantee a solution for every mesh.
- A constant point-light approximation loses the wing's near-field response.
- Independent random glints shimmer rather than remain attached to scales.
- A second exposure or tone-map stage changes luminous colour and brightness.
- Lens sprites require a separate MRT attachment; treating them as ordinary
  depth-buffer surfaces breaks their defocus.

## Diagnostics

`setDebugMode()` accepts `final`, `nopost`, `scene` and `defocus`. `nopost`
shows scene and emitter radiance with tone mapping; `scene` isolates the scene
attachment; `defocus` shows the gathered lens image before emitter addition,
glare and final grading. The numeric geometry audit is a separate callable.
