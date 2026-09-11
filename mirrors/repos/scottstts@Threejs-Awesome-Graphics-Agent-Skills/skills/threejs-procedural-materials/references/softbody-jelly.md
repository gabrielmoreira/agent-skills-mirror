# Softbody jelly material

Use this reference for a small deformable translucent body whose mechanics,
surface geometry, view-ray thickness, absorption, shadow, and refractive
caustics share a deforming shell. The [softbody-jelly example](../examples/softbody-jelly/softbody-jelly.js)
is the executable contract. Mechanics and ray tracing run on the CPU; the
material uses WebGPU/TSL. Constants below describe this calibrated flower body.

## Contents

1. Coordinate and geometry contract
2. XPBD neo-Hookean mechanics
3. Damping, contact, and sleep
4. Refractive receiver and transmissive material
5. Observed limits and defects
6. Diagnostics and validation
7. Failure diagnosis

## Coordinate and geometry contract

Use metres, kilograms, seconds, and pascals. Keep identity object transforms:
cage, camera position, picking, and optics share world coordinates. The optical
receiver is the plane `y = 0 m`. The rest body is a five-lobed
flower built from a regular triangular lattice with `latticeRadius = 6` and
`layers = 5`. It has `762` cage nodes, `3240` tetrahedra, `792` boundary
triangles, and rest volume:

```text
V₀ = 0.00011933031247661388 m³
```

For a non-central lattice point, with `t = layer/5`, ring fraction `u = ring/6`, and ring angle
`a = ordinal/(6 ring) × 2π` radians,
the radial profile is:

```text
lobes   = 1 + 0.19 cos(5a) + 0.018 cos(10a)
rounding = 0.88 + 0.12 sin(πt)^0.6
radius  = 0.032 u lobes rounding
y       = 0.010 + 0.042t + 0.0024(1 − 2t)u⁴
```

The centre follows `x = z = 0` and `y = 0.010 + 0.042t`. Split each lattice
triangle prism into the three globally ordered tetrahedra
`[a,b,c,C]`, `[a,b,B,C]`, and `[a,A,B,C]`; correct negative determinants by
swapping the second and third IDs, then throw on determinants below `1e-13 m³`; do not omit elements.

The rendered shell is not a second simulation. Apply two Loop subdivision
passes as weighted stencils over the cage boundary. The final shell has `6338`
stencil vertices and `12672` triangles. Recompute its positions, vertex
normals, bounding box, and bounding sphere once after each frame’s mechanics
batch. Attach `opticalThickness` as a dynamic scalar attribute to the same
geometry.

## XPBD neo-Hookean mechanics

The calibrated parameters are:

```js
const physics = {
  density: 1050,
  shear: 600,
  bulk: 65000,
  damping: 3,
  gravity: 9.81,
  step: 1 / 240,
  iterations: 3,
  staticFriction: 0.65,
  dynamicFriction: 0.42,
  restitution: 0.065,
  floor: 0.00015,
  maxGrabForce: 2.8,
};
```

For each tetrahedron, derive shape gradients from the inverse rest matrix,
then store the gradients, rest volume, and three XPBD multipliers. Evaluate the translation-free deformation
gradient `F`, its determinant `J`, and the two coupled constraints from the
compressible neo-Hookean energy:

```text
W = μ/2 (||F||² − 3) + K/2 (J − 1 − μ/K)²
```

Here `μ = shear`, `K = bulk`, and `W` is energy per rest volume in Pa.
The constraints are `C_D = ||F||` and `C_H = J − 1 − μ/K`. Their derivatives
with respect to `F` are `F / ||F||` and the cofactor matrix of `F`; multiply
these by each node’s rest shape gradient to obtain position gradients. Use
time-scaled compliances `1/(μ V h²)` and `1/(K V h²)` for rest volume `V`. Solve their two-by-two multiplier system together. The
rest state must have zero combined stress; solving the terms independently
can introduce residual motion at rest.

Keep the unilateral determinant barrier at `J = 0.16`. Integrate velocity and
position with the fixed `1/240 s` step, reset element and grab multipliers, then run three XPBD
sweeps in forward, reverse, forward order, apply the grab constraint, and project floor contact at `y = 0.00015`
inside every pass. A grab uses stiffness `90 N/m`, time-scaled compliance `1/(90h²)`, and
clamps each axis multiplier to `±(2.8 N)h²`; this is a per-axis force limit.

Accumulate floor corrections as `normal` across the sweeps. Before velocity
reconstruction, remove all tangential displacement when its length is below
`0.65 normal`; otherwise remove the fraction
`min(1, 0.42 normal/(tangent + 1e-20 m))`. Reconstruct velocity over `h`.
For contact with incoming vertical velocity below zero, use
`vy = max(vy, bounce)`, where `bounce = −0.065 incoming` below `−0.18 m/s`
and zero otherwise. Larger upward projection velocities are retained.

Clamp elapsed time to `0…0.05 s`, execute at most 12 fixed substeps per frame,
and cap leftover accumulation to one substep when that limit is reached.

## Damping, contact, and sleep

Compute the mass-weighted centre and velocity, inertia tensor, angular momentum,
and rigid angular velocity. Decompose every node velocity into rigid translation
plus rotation and an internal residual. Apply one frame-rate-independent decay
to both components:

```text
decay = exp(−max(0, damping) h)
```

Expose the mass-weighted RMS values of the internal and rigid components. A
grounded body with no grab sleeps after more than `0.45 s` when `rigidRms < 0.004 m/s`
and `internalRms < 0.021 m/s`. Sleeping clears velocity and preserves the
projected position; a grab, reset, or nudge wakes the body.

The default body mass is `0.12529682810044418 kg`, and its initial centre is:

```text
(-0.000001684837451731872, 0.031000000000150137, -3.366955965335844e-19) m
```

Use volume ratio and kinetic energy as stability signals. If any position or
velocity is non-finite, or any position component exceeds `3 m` in absolute value, reset and pause before
rendering the next frame.

## Refractive receiver and transmissive material

Refit the triangle BVH at the start of each optical refresh. Its ray traversal uses slab-box
tests and Möller-Trumbore triangle intersections, rejects hits at or below
`1e-7 m`, and interpolates shell normals from the dynamic geometry. If the
interpolated normal fails `dot(normal, ray) × sign <= −0.015`, with `sign = +1`
for entry and `−1` for exit, replace it with the geometric cross product.
Normalize, apply the entry/exit sign, and orient against the ray.

For direction `d`, oriented normal `n`, and indices `n₁`, `n₂`, use:

```text
c = clamp(−dot(d,n), 0, 1)
η = n₁/n₂
k = 1 − η²(1 − c²)
```

Return no transmitted ray when `k < 0`. Otherwise use exact unpolarised Fresnel
with the s and p amplitude ratios, and set transmission to
`1 − 0.5(rs² + rp²)`. Offset every new ray by `2e-6 m`.

The receiver field uses:

```js
const optical = {
  size: 192,
  minSpan: 0.22,
  maxSpan: 0.75,
  samples: 42,
  internalBounces: 4,
  ior: [1.347, 1.350, 1.354],
};
```

Fit the field to the body footprint and its oblique-light projection. Add
`0.060 m` to the larger extent before clamping the span to `0.22…0.75 m`,
then centre the square on the combined bounds. Stratify each
of the `42 × 42` launch samples with the deterministic `(73,37)` and `(31,83)`
hash pairs. Transport red, green, and blue independently; multiply each
interior segment by `exp(−σ distance)` using the active preset:

```text
berry = [5, 46, 23] 1/m
mint  = [40, 8, 20] 1/m
honey = [5, 17, 58] 1/m
```

Use at most four internal intersection attempts. Reflect only on total internal
reflection; otherwise take the transmitted exit and discard the reflected
Fresnel branch. Reject unescaped paths, throughput below `0.002`, exit
`dy >= −1e-5`, non-positive receiver distances, or another body hit before
the receiver. Splat `throughput × sampleArea/pixelArea` using the normalised
`7 × 7` kernel `exp(−(kx² + ky²)/3.5)` with bilinear distribution. Blur only
shadow and contact, horizontally then vertically, with weights
`1, 2, 3, 2, 1` divided by `9`. Clear the
outer two texels before uploading the shadow/contact and RGB light textures so
clamp-to-edge filtering cannot repeat energy outside the fitted field.

The view-thickness pass uses the camera-to-vertex direction and updates only
vertices with `dot(direction, normal) <= −0.01`. Refract at IOR `1.35`, trace
the first interior hit, clamp distance to `0.0002…0.16 m`, or use `0.002 m`
if no hit exists. Skipped vertices retain their previous thickness, initially
`0.03 m`. Update the receiver/BVH before view thickness. The optical clock
triggers at `>= 1/24 s` and resets to zero, so ordinary refreshes run at most
at 24 Hz and depend on frame rate. They continue while mechanics are paused;
between refreshes optical data can lag behind the current shell.

Encode shadow in red and contact in green. Photon RGB is encoded as
`round(clamp(photons/5, 0, 1) × 255)` in unsigned-byte textures with
`NoColorSpace`, linear filtering, and no mipmaps. Receiver UV is
`(positionWorld.xz − originNode)/spanNode`; decode light RGB by multiplying
by `5`. With receiver albedo `bench`, use
`colorNode = bench × (1 − 0.63 shadow) × (1 − 0.40 contact)` and
`emissiveNode = bench × decodedLight × 0.67`. The caller creates the receiver
material using the example’s exposed textures and uniforms. Transport and
direct lighting share `normalize([-0.6123724357, −0.5, 0.6123724357])`.

The physical material uses `roughness = 0.075`, `transmission = 1`,
`thickness = 0.035 m`, `ior = 1.35`, `dispersion = 0.025`,
`attenuationDistance = 0.035 m`, `clearcoat = 0.42`, and
`clearcoatRoughness = 0.05`. Bind `opticalThickness` to `thicknessNode` and
derive the attenuation colour from the active extinction coefficients as
`exp(−sigma × attenuationDistance)` in linear RGB. Surface colour remains a
separate preset. Keep `transparent = false` and `side = FrontSide`.

## Observed limits and defects

- The mesh has no self-collision or tearing constraint; extreme folding can
  create visual intersections.
- Transmission is view-dependent and cannot see a surface outside the frame.
- The receiver is planar, finite, and limited to `192²` texels and `42²`
  stratified launch samples; it is not a path tracer.
- Receiver and thickness data can lag between optical refreshes, including
  during camera movement.
- The subdivision shell smooths the rendered boundary but does not add
  mechanical degrees of freedom.
- The finite internal-reflection budget can discard bright trapped paths too;
  partial Fresnel reflection branches are not traced.
- Encoded light saturates at `5` before the receiver’s artistic gain; this is
  not a fully energy-conserving renderer.
- The example allows one active system per module and assumes an unparented
  camera and identity group transforms.
- The receiver texture must not be allowed to repeat non-zero edge texels.

## Diagnostics and validation

Expose the following inspection modes without changing the final branch:

```text
final       physical jelly, receiver shadow, and caustic composition
wireframe   subdivided shell wireframe over the physical material
shadow      receiver red/green shadow and contact channels
caustics    receiver RGB transport field
```

Report mass, volume ratio, kinetic energy, optical field size, and fixed-step
duration. Deterministic checks should pin `762` cage nodes, `3240` tetrahedra,
`792` boundary faces, `6338` shell stencils, `12672` shell triangles, the rest
volume, default mass, `192` field size, `42` samples per grid axis, and the normal
incidence transmission approximately `0.977818017202354` for `n₁ = 1`, `n₂ = 1.35`.

## Failure diagnosis

- If the body gains energy while grounded, verify that deviatoric and
  hydrostatic multipliers are solved together and that damping is applied to
  both rigid and internal velocity components.
- If the surface looks faceted but the cage is stable, verify both Loop passes,
  dynamic shell positions, and `computeVertexNormals()` after stepping.
- If caustics smear into long bands, inspect receiver span fitting and confirm
  that the outer two texels of both data textures are zeroed.
- If colours change without deformation, check that the active extinction
  preset is shared by the material attenuation colour and RGB transport.
- If the body appears to refract through itself, inspect BVH refit order,
  `2e-6 m` ray offsets, geometric-normal fallback, and the four-bounce limit.
- If the receiver shadow is displaced from the jelly, verify that the direct
  light direction, projected footprint, and planar receiver use the same vector.
