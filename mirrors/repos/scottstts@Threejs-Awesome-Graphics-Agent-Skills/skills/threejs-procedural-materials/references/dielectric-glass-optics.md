# Dielectric glass optics

Use this reference when a body has to transmit its surroundings rather than
merely look shiny: cast and blown glass, crystal, resin, ice blocks, gemstone
substitutes, and any material whose interior path — not its surface — produces
the image.

A transmissive body is not a PBR channel bundle with the opacity turned down.
It is a path: enter, travel, hit the far interface, either leave or bounce, and
carry a wavelength-dependent index and a per-unit-length extinction the whole
way. Every mechanism below exists to keep one of those stages honest.

## Contents

- Two-pass ownership
- Back-face data buffer
- Interior exit search
- Interface response and the bounce budget
- Volume absorption from a tint
- Spectral path and dispersion
- Environment probe and the visible surround
- Choosing between geometric and image-space transmission
- Limits and failure patterns
- Diagnostics

## Two-pass ownership

The material owns two passes and the buffer between them:

```text
pass 1  subject meshes → back-face data target (world normal, camera distance)
pass 2  camera pass: glass material reads that target per fragment
```

Ordering is a contract, not an optimisation. Pass 1 runs every frame, before
the camera pass, with the same camera. A buffer left over from the previous
frame refracts the previous frame's silhouette, which reads as a body whose
interior lags the camera by one frame — most visible while orbiting.

The target tracks the drawing-buffer size in physical pixels, because the
interior ray addresses it by projecting world points into that exact space.

## Back-face data buffer

The `spectral-dispersive-glass` example allocates:

```text
format          RGBA, HalfFloatType
filtering       NearestFilter (min and mag)
mipmaps         disabled
depth buffer    enabled
contents        xyz = geometric world normal, w = distance to camera
```

Three properties of the pass matter more than the format:

1. **Double-sided, no culling.** A body assembled from several
   interpenetrating shells has no consistent winding, so a facing test picks
   the wrong triangles. Rasterise everything.
2. **Inverted fragment depth.** Writing `1 − depth` makes the default
   less-than test keep the *farthest* surface along each view ray. That
   surface is the exit of the union hull, which is the interface refraction
   should target. Without the inversion, the buffer holds the nearest back
   face and interiors collapse to a thin skin.
3. **A pure geometric normal.** Store `normalize(modelNormalMatrix *
   normalLocal)` — never a normal already flipped toward the viewer by the
   rasteriser. The consuming pass re-orients the stored vector along the ray
   it is currently following, so authored normal direction stops mattering.

Half float is required, not preferred: `w` is a scene-scale distance and the
normal is signed. Nearest filtering is also required — linear filtering across
a silhouette blends two unrelated surfaces into a distance that lies between
them, and the exit search then lands in empty space.

## Interior exit search

The exit point is found by projection and refinement rather than by
intersection. Per segment, `EXIT_REFINEMENTS = 3` passes of:

```text
Pest = orig + dir * tSeg                    estimated exit point
uv   = clamp(projectToBufferUV(Pest), 0, 1) where the camera sees that point
bb   = backFaceData(uv)                     surface stored under that texel
Pb   = camP + normalize(Pest − camP) * bb.w rebuilt world position
tSeg = clamp(dot(Pb − orig, dir), minWall, maxSegment)
```

The rebuild matters. The buffer stores a distance along the camera ray through
that texel, not along the interior ray, so the surface point has to be
reconstructed before the segment length is measured along `dir`.

The seed for the first segment is the view-ray thickness at the fragment:
`bb.w − distFront`, floored at the minimum wall. Where the buffer holds nothing
— the silhouette rim, where the exit surface projects outside the visible
buffer — the seed falls back to `0.015 × bounding diagonal`.

Bounds, both derived from the subject's world bounding-box diagonal:

- `MIN_WALL = 0.08` world units at the example's normalised subject scale.
  Open, zero-volume sheets would otherwise transmit over no path length at all
  and lose their tint completely.
- `MAX_SEGMENT_RATIO = 3.0 × diagonal`. A refinement that lands on an
  unrelated distant surface would otherwise stretch one segment across the
  whole scene.

Three passes converge on gently curved bodies. They cannot recover a surface
the camera never saw; that is the standing cost of solving this in image space.

## Interface response and the bounce budget

Every interface uses exact unpolarised Fresnel reflectance:

```text
sin²θt = (n1/n2)² (1 − cos²θi)
cosθt  = sqrt(max(1 − sin²θt, 1e-6))
r_s    = (n1 cosθi − n2 cosθt) / (n1 cosθi + n2 cosθt)
r_p    = (n2 cosθi − n1 cosθt) / (n2 cosθi + n1 cosθt)
F      = sin²θt ≥ 1 ? 1 : clamp(0.5 (r_s² + r_p²), 0, 1)
```

Schlick is not interchangeable here. The interior path spends most of its
interfaces near grazing incidence, exactly where the approximation drifts, and
it never reaches 1 at the critical angle — so total internal reflection leaks
energy out of the body instead of trapping it.

Returning 1 past the critical angle is what makes TIR fall out of the same
expression. The segment loop needs no separate test: it refracts out with
weight `1 − F`, multiplies the running throughput by `F`, reflects, and
continues.

Budget in the example: `PATH_SEGMENTS = 4` (TIR bounces plus the exit that
ends the path), with an early `Break` once throughput drops below
`THROUGHPUT_CUTOFF = 0.004`. After the last segment, the remaining throughput
leaves along the current direction and is added as residual energy. Omitting that
residual term darkens the deepest parts of the body, where paths are most
likely to exhaust the budget.

Entry incidence is clamped to `[1e-4, 1]` and exit incidence likewise, so
grazing fragments cannot divide by zero at the silhouette.

## Volume absorption from a tint

Transmission is attenuated by Beer-Lambert over the accumulated internal path
length, not by a flat colour multiply:

```text
σ      = −ln(clamp(t, 1e-4, 1)) / max(depth, 1e-3)   [1/unit]
L_out  = L_in · exp(−σ · s)                          s = path length so far
```

Inverting the exponential keeps the control perceptual — choose the colour a
chosen thickness should show — and, more importantly, keeps one body internally
consistent: thin edges and thick cores read the same σ over their own path
lengths, which is what makes cast glass look solid rather than surface-tinted.

The `spectral-dispersive-glass` example uses `tint = #d0edda` at `depth = 0.5`
world units, which resolves to `σ ≈ (0.922, 0.332, 0.710) 1/unit`.

Decode the tint exactly once, and decode it explicitly. A `Color` built from an
sRGB literal is already in the linear working space, so an added
`convertSRGBToLinear()` squares the transfer and inflates extinction by roughly
`2.3×`. Nothing about the image announces this: doubling only deepens the tint,
so tuning by eye absorbs the error while the picker quietly stops meaning what
it says, and the mistake then travels with the tuned literal. It also drifts
with saturation rather than scaling uniformly — a mid-grey tint moves from
`σ 3.07` to `6.53 1/unit` — so the depth control becomes least predictable
exactly where the tint is strongest. Parse the literal as
`LinearSRGBColorSpace` to keep its raw components and apply the one decode
yourself; σ is then identical whether or not colour management is enabled.

## Spectral path and dispersion

Dispersion is a property of the index, so it belongs ahead of the whole path,
not in a post-hoc channel offset. The index comes from the two numbers
glass catalogues publish, `n_d` and the Abbe number `V_d`:

```text
K = 1/486.13² − 1/656.27²      nm⁻²   (F and C Fraunhofer lines)
B = (n_d − 1) / (V_d · K)      nm²
A = n_d − B / 589.29²
n(λ) = A + B / λ²
```

`A` and `B` are constant for a given glass and resolve on the CPU; only
`A + B/λ²` belongs in the shader. The example ships `n_d = 1.5`, `V_d = 32` —
crown-glass index with flint-like fire.

The whole interior path is then traced once per wavelength sample.
`SPECTRAL_SAMPLES = 8` stratified centres span `415–695 nm`, deliberately
narrower than the full visible range because the colour matching curves are
near zero at both ends. Each sample is weighted by CIE 1931 colour matching,
built from multi-lobe piecewise Gaussians and converted XYZ → linear sRGB:

```text
X = 1.056 g(λ;599.8,37.9,31.0) + 0.362 g(λ;442.0,16.0,26.7) − 0.065 g(λ;501.1,20.4,26.2)
Y = 0.821 g(λ;568.8,46.9,40.5) + 0.286 g(λ;530.9,16.3,31.1)
Z = 1.217 g(λ;437.0,11.8,36.0) + 0.681 g(λ;459.0,26.0,13.8)

g(λ; μ, s₁, s₂) = exp(−½ t²),  t = (λ − μ) / (λ < μ ? s₁ : s₂)
```

Accumulate `weight · radiance` and `weight` separately and divide at the end,
guarding the divisor at `1e-4`. That running normalisation is what guarantees a
dispersion-free spectrum reconstructs the environment exactly instead of
picking up a cast, and it keeps the image stable when the sample count changes.
Individual weights are legitimately negative outside the sRGB gamut, so clamp
the final sum — never the per-sample weights.

Below roughly six samples the fire separates into discrete coloured copies of
the environment rather than a continuous spread. Cost scales linearly: each
sample re-traces every segment.

## Environment probe and the visible surround

Both the external specular reflection and every exit ray read one
equirectangular HDR probe, sampled at an **explicit** mip level. Explicit is
mandatory, not stylistic: every lookup on the interior path sits inside a
non-uniform loop, where implicit derivatives are undefined.

Probe requirements:

```text
mapping      EquirectangularReflectionMapping
wrapS        RepeatWrapping        closes the horizontal seam
wrapT        ClampToEdgeWrapping   keeps the poles from wrapping together
mipmaps      enabled               explicit LOD needs a chain to walk
filtering    LinearMipmapLinear / Linear
```

The mip level doubles as surface micro-roughness: level 0 is polished glass,
higher levels integrate a wider cone of incoming radiance and read as frost.
The example ships level 0 and a probe rotation of 0 rad.

Assign the same probe as the scene background. What the viewer sees through the
body has to be the radiance field they see around it, or the body reads as a
cutout of an unrelated scene — a mismatch that no amount of index tuning fixes.

Derive the background direction from the **geometric world normal**, never from
`positionWorld − cameraPosition`. A background node is drawn on a unit sphere
the renderer owns, and nothing in the contract says where that sphere sits;
renderers have both centred it on the camera and left it at the world origin.
Where it sits at the origin, a position-derived direction compresses the whole
view into a cone of half-angle `asin(1 / |cameraPosition|)` around the
camera-to-origin axis. At a camera distance of 2.86 units that is a 41° cone
covering the full screen. The failure is quiet: the background still looks like
a plausibly lit environment, just magnified and warped, which reads as a
low-resolution probe rather than a wrong direction. A sphere's outward normal
is translation invariant and stays correct under either placement.

The material returns unbounded linear radiance. The host owns exposure and the
display transform, which must handle values well above 1; a clamped transform
crushes exactly the caustic-like concentrations this path exists to produce.

## Choosing between geometric and image-space transmission

Two transmission strategies belong to different geometry, not different
quality tiers:

| | image-space path | geometric path |
| --- | --- | --- |
| exit surface from | back-face data buffer | BVH first hit against the mesh |
| tolerates open sheets, multiple shells, bad winding | yes | no |
| sees surfaces outside the frustum or occluded | no | yes |
| dispersion model | per-wavelength Cauchy index | per-channel index offset |
| cost driver | samples × segments × buffer reads | bounces × BVH traversal |

Use the `spectral-dispersive-glass` example for scanned, assembled, or
non-watertight bodies, and where dispersion has to track a real catalogue
index. Use the `raytraced-diamond` example for closed faceted gems, where the
cut itself produces the optical result and the exit facet must be exact even
when it faces away from the camera.

## Limits and failure patterns

- **Off-screen exits are unknowable.** Any interior ray whose exit projects
  outside the buffer falls back to the assumed wall thickness. Wide-angle
  framing and bodies that overflow the frame expand this region.
- **Occluded exits resolve to the occluder.** The buffer holds one surface per
  texel; if another object is in front, the search reads that object's
  distance. Render only the transmissive subject into the data pass.
- **A moving subject must be followed into the data pass.** The pass draws its
  own copy of the hierarchy, so every pose change has to reach that copy before
  it renders, or the visible surface moves while the stored back faces do not
  and the interior refracts a pose the body no longer holds. The
  `spectral-dispersive-glass` example follows the root's world transform — so
  ancestor motion counts — plus each descendant's local matrix, visibility, and
  morph weights, every pass. Geometry buffers and skeletons are shared by
  reference, so vertex edits and skinned animation need nothing. Structural
  change is the exception: meshes added or removed, or a geometry swapped, need
  the copy rebuilt, because the node pairing is fixed when it is built.
- **No caustics, no shadow transport.** This path resolves what the body shows,
  not what it casts. Light it as an unshadowed transmissive object.
- **A dense subject pays twice.** The data pass rasterises the full triangle
  count double-sided every frame, in addition to the camera pass.
- **Cost is multiplicative.** Samples × segments × three refinements × two
  buffer reads per refinement is the per-fragment budget; halving the sample
  count is the cheapest lever, followed by the segment budget.
- **A flipped V still looks plausible.** The projection inverts V for backends
  that rasterise render targets with Y flipped relative to the classic GL
  convention. A wrong choice produces a coherent but incorrect interior.

## Diagnostics

The material can output three channels in place of the final image. Read them
in this order — each one clears a stage before the next becomes meaningful.

| view | shows | failure it exposes |
| --- | --- | --- |
| view-ray thickness | `(bb.w − distFront) / (0.6 × diagonal)` | black interior means the data pass wrote nothing; a flat mid-grey body means the depth inversion is missing and only the near skin is stored |
| back-face normal | stored normal, `×0.5 + 0.5` | noise or single-colour fields mean winding or the normal matrix is wrong; black regions mark texels with no data, which is exactly where the fallback thickness applies |
| entry Fresnel | `F(cosθi, 1 → n_d)` | the only term independent of the interior path. If this looks right and the final image does not, the defect is in the exit search, not the surface response |

Further checks that are worth running once per integration:

1. **Ground-truth the projection.** Compare the buffer against a CPU raycast
   mask of the same frame before trusting any interior result.
2. **Collapse the spectrum.** One sample at `λ_d` must reconstruct the
   environment with no colour cast. A cast means the weight normalisation is
   broken.
3. **Zero the absorption.** With `σ = 0`, total radiance must not exceed the
   probe's brightest value; excess means throughput is being double-counted
   across segments.
4. **Single segment.** With one segment the body must show refraction but no
   internal structure. Structure at one segment means the residual term is
   being added inside the loop rather than after it.
