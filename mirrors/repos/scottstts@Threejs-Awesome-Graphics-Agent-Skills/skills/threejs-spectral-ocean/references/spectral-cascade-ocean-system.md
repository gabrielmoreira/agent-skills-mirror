# Spectral cascade ocean system

Use this reference for a large, unbounded-looking ocean whose identity comes from directional spectral synthesis, staged inverse FFTs, derivative maps, Jacobian whitecaps, and coherent optical shading.

## Contents

1. Architecture contract
2. Cascade partition
3. Initial directional spectrum
4. Hermitian pairing and packed fields
5. GPU inverse FFT schedule
6. FFT hard gate
7. Spatial map assembly
8. Jacobian whitecaps with history
9. Fold-aware surface normal
10. Optical composition
11. Submerged interface optics
12. Runtime order
13. Geometry, camera, and fog
14. Required diagnostics
15. Failure diagnosis

## 1. Architecture contract

Keep these stages distinct and inspectable:

```text
sea-state parameters
  -> deterministic Gaussian field
  -> initial directional spectrum h0(k)
  -> conjugate packing h0(k), conj(h0(-k))
  -> time-evolved packed frequency fields
  -> horizontal IFFT stages
  -> vertical IFFT stages
  -> centered-spectrum permutation
  -> displacement + derivative + foam-history maps
  -> displaced surface + optical shading
```

One cascade owns one patch length and one disjoint wavenumber interval. Shared
sea-state uniforms and Gaussian seeds keep the cascades statistically related;
separate buffers prevent writes from aliasing.

The 256², three-cascade configuration uses:

```ts
const oceanPreset = {
  resolution: 256,
  patchLengthsMeters: [250, 17, 5],
  boundaryFactor: 6,
  depthMeters: 500,
  gravity: 9.81,
  choppiness: 1.3,
}
```

Treat these as a validated starting scale, not universal constants.

## 2. Cascade partition

For cascade `i`, define:

```text
deltaK(i) = 2π / patchLength(i)
handoff(i) = 2π / patchLength(i) * boundaryFactor
```

Use:

```text
cascade 0: [epsilon, handoff(1)]
cascade 1: [handoff(1), handoff(2)]
cascade 2: [handoff(2), largeUpperBound]
```

The in-band mask must be applied after all singular inputs have been made safe.
Do not rely on multiplication by zero to hide `1/0`, `sqrt(NaN)`, or infinite
frequency derivatives. Clamp the evaluated wavenumber first:

```glsl
float kSafe = max(kLength, cutoffLow);
float inBand =
  step(cutoffLow, kLength) *
  step(kLength, cutoffHigh);
```

Debug every cascade as a centered spectrum heatmap. Adjacent bands may touch
at a boundary; they must not overlap broadly or leave a visible spectral hole.

## 3. Initial directional spectrum

Generate two independent standard-normal values per grid cell once. Seed the
generator explicitly so image comparisons and regression tests are stable.

For each centered grid coordinate:

```text
k = (gridIndex - N/2) * deltaK
omega(k) = sqrt(g * |k| * tanh(min(|k| * depth, 20)))
```

The sea state sums two spectra:

```text
energy =
  localWindSea(omega, direction)
  + swell(omega, direction)
```

Each term combines:

```text
JONSWAP frequency energy
* TMA finite-depth correction
* directional spreading
* exp(-shortWaveFade² * |k|²)
```

Compute JONSWAP peak terms from wind speed and fetch:

```text
alpha = 0.076 * (g * fetch / windSpeed²)^(-0.22)
peakOmega = 22 * (windSpeed * fetch / g²)^(-0.33)
```

Use the standard JONSWAP sigma split around the peak (`0.07` below, `0.09`
above), peak enhancement `gamma`, and an explicit scale per local/swell lobe.

Directional spreading must rotate around the configured wind angle and tighten
as the frequency approaches the energetic range. Blend a broad cosine-squared
base with a Donelan–Banner-style powered cosine lobe.

Initial complex amplitude:

```text
amplitude =
  sqrt(
    energy
    * 2
    * abs(dOmega/dk)
    / kSafe
    * deltaK²
  )

h0(k) = gaussianComplex(k) * amplitude * inBand
```

Expose at least:

```text
local-only spectrum
swell-only spectrum
combined spectrum
in-band mask
frequency derivative
```

## 4. Hermitian pairing and packed fields

Real spatial fields require conjugate symmetry. Store:

```text
packedH0(k) = [h0(k), conjugate(h0(-k))]
```

At time `t`:

```text
h(k,t) =
  h0(k) * exp(i * omega * t)
  + conjugate(h0(-k)) * exp(-i * omega * t)
```

Compute horizontal displacement from `i * k / |k| * h`, vertical displacement
from `h`, and spatial derivatives by multiplying by the relevant wave-number
components.

Pack two real spatial fields into one complex IFFT input. A useful four-buffer
layout is:

```text
field 0: horizontal displacement X + i horizontal displacement Z
field 1: height + i cross derivative
field 2: height slope X + i height slope Z
field 3: horizontal derivative XX + i horizontal derivative ZZ
```

Packing halves the number of transforms. Document the unpacking algebra next
to the field contract; a swapped real/imaginary sign can look plausible while
rotating or mirroring the sea.

## 5. GPU inverse FFT schedule

Precompute a butterfly table on the CPU for every FFT stage and output column:

```ts
type ButterflyEntry = {
  twiddleReal: number
  twiddleImaginary: number
  inputA: number
  inputB: number
}
```

For each complex field:

1. execute `log2(N)` horizontal butterfly stages;
2. execute `log2(N)` vertical butterfly stages;
3. multiply by `(-1)^(x+y)` to reconcile centered frequency coordinates.

Ping-pong between the field buffer and a dedicated scratch buffer. Never let
two logical fields share scratch storage during the same stage.

The critical WebGPU backend rule is:

```text
one FFT stage -> one compute submission boundary
```

Do not assume writes from one dispatch are visible to the next dispatch inside
an implementation-defined combined pass. Batch independent fields at the same
stage into one submission, then submit the next stage:

```ts
for (let stage = 0; stage < logN; stage++) {
  renderer.compute(allHorizontalFieldsAt(stage))
}
for (let stage = 0; stage < logN; stage++) {
  renderer.compute(allVerticalFieldsAt(stage))
}
renderer.compute(allCenteringPermutations)
```

Inspect the installed renderer before relying on this exact API shape.

## 6. FFT hard gate

Validate the transform before connecting the spectrum:

```text
test A:
  centered DC impulse
  expected spatial result = constant complex (1, 0)

test B:
  centered one-bin X-frequency impulse
  expected spatial result =
    cos(2πx/N) + i sin(2πx/N)
```

Measure maximum absolute error over every texel. A practical gate for half- or
single-precision storage is `1e-3`, adjusted only with evidence.

If either test fails, stop. Do not tune spectrum amplitude, choppiness, or
shading around a broken transform.

Diagnostic causes:

```text
constant test alternates signs -> missing or duplicated centering permutation
sine direction reversed -> inverse twiddle sign is wrong
frequency appears on Y -> horizontal/vertical indexing is swapped
every other stage corrupts -> ping-pong source/destination parity is wrong
random blocks -> missing inter-stage visibility boundary
```

## 7. Spatial map assembly

Assemble filterable repeating textures after the IFFT:

```text
displacement.rgba =
  [lambda * Dx, height, lambda * Dz, foamHistory]

derivatives.rgba =
  [dHeight/dx, dHeight/dz, lambda * dDx/dx, lambda * dDz/dz]
```

Half-float storage textures are a strong bandwidth/quality compromise when the
target backend supports storage writes and filtered sampling for that format.
Verify capabilities rather than assuming them.

## 8. Jacobian whitecaps with history

Choppy horizontal displacement can fold. Build the 2×2 horizontal mapping
Jacobian:

```text
jxx = 1 + lambda * dDx/dx
jzz = 1 + lambda * dDz/dz
jxz = lambda * dDz/dx
J = jxx * jzz - jxz²
```

Low or negative `J` identifies real fold/compression regions. Store a persistent
per-texel history initialized to `1`.

One effective update shape is:

```text
historyNext =
  min(
    currentJacobian,
    historyPrevious
      + dt * recoveryRate / max(currentJacobian, 0.5)
  )
```

This snaps toward a breaking event and recovers gradually. Keep simulation
history separate from the display threshold:

```text
foamCoverage =
  smoothstep(lowCoverage, highCoverage,
    sum(saturate((foamThreshold - history) * foamScale)))
```

Do not include a finest cascade that produces constant speckle merely because
it is available. Validate each cascade’s foam contribution separately.

## 9. Fold-aware surface normal

Sum derivative maps across cascades. Horizontal compression changes the height
slope denominator:

```text
slopeX = sum(dHeight/dx) / (1 + sum(lambda * dDx/dx))
slopeZ = sum(dHeight/dz) / (1 + sum(lambda * dDz/dz))
normal = normalize([-slopeX, 1, -slopeZ])
```

This keeps normals coupled to choppy displacement. A normal derived from height
alone misses overturning/compression behavior.

Add sub-grid normal detail only after this resolved normal exists. Sample a
seamless detail field at two independently scrolling scales and keep its
strength low enough that it cannot rewrite the swell direction.

## 10. Optical composition

This is the base optical tier. Section 11 documents the exact-dielectric
submerged tier and states which example implements it; the Schlick fit below
belongs to the `spectral-cascade-ocean` example, not to that one.

Use one sky-radiance function for both the dome and reflected ray:

```text
sky(direction) =
  horizon-to-zenith gradient
  + narrow sun disc
  + broad sun halo
```

Water-air Fresnel:

```text
F = 0.02 + 0.98 * (1 - saturate(N·V))^5
```

Build the body term from deep color plus crest scatter. Use a
view/sun/normal half-vector response weighted by crest height, then:

```text
water = mix(body, sky(reflect(-V, N)), F)
```

Foam changes the final response rather than adding a white texture. Shade it
with sun/sky incidence and modulate brightness with a separate bubbly detail
field. Do not punch noisy holes in the physically derived foam coverage.

The visible sky and reflected sky must share:

```text
sun direction
sun color
horizon color
zenith color
```

Otherwise the reflection will appear pasted onto the surface.

## 11. Submerged interface optics

Section 10 is the base tier: a Schlick fit, one reflected sky sample, and a body
term. The `submerged-snell-ocean` example implements the exact tier, and every
constant below is that example's code. Do not mix the two — the Schlick fit
over-reflects by up to about 6 percentage points across the 80–85 degree grazing
range that dominates a low camera, and it does not rise correctly into the
critical angle, so a structure stays pasted over what should be total internal
reflection.

**Exact unpolarised dielectric Fresnel, both sides.** One helper answers three
questions: reflectance, whether transmission is physically possible, and the
transmitted cosine that the water-to-air side reuses for its angular stretch.

```text
etaRatio      = etaI / etaT                       (air 1.0, water 1.333)
sinT2         = etaRatio² · (1 − cosI²)
criticalWidth = clamp(fwidth(sinT2) · 1.5, 0.001, 0.05)
canTransmit   = 1 − smoothstep(1 − criticalWidth, 1 + criticalWidth, sinT2)
cosT          = sqrt(max(1 − sinT2, 0))
rs            = (etaI·cosI − etaT·cosT) / (etaI·cosI + etaT·cosT)
rp            = (etaT·cosI − etaI·cosT) / (etaT·cosI + etaI·cosT)
F             = (rs² + rp²) / 2
```

The critical-angle boundary moves across the screen with the wave normal, so the
binary domain test is derivative-filtered over roughly one output pixel. Exact
Fresnel still drives transmitted energy to zero at the physical limit; the mask
only stops an animated normal from toggling a whole pixel.

**The optical side is a camera-medium state, never a facing test.** At a crossing
a displaced sheet can expose nearby backfaces before the camera itself is
submerged. Use one state for the whole draw and multiply the resolved fold-aware
normal by a side sign of `isAbove · 2 − 1`.

**Both sides share the one resolved normal.** Never filter the interface to
stabilize what is transported through it: the window's rim IS the interface's own
silhouette. A second below-surface normal whose cascade keeps ran on
`pixelFootprint × stretch²` reaches 3–45 at the rim against thresholds authored
in metres per pixel, so past about 10 m of camera depth every cascade zeroes and
the window refracts off a mathematically flat plane — a clean analytic conic
where the sea should show a live, dappled, wave-shaped rim.

**The transmitted sun is the only genuinely unresolvable source, so its LOBE is
broadened, not the geometry.** Water-to-air expands angles by
`S = eta·cosI/cosT`, unbounded at the critical angle, and for a fixed view ray a
normal tilting by δ moves the transmitted direction by `|1 − S|·δ`. Since
`cos^n ≈ exp(−n·δ²/2)`, an authored lobe carries variance `1/n`:

```text
stretch  = max(eta · cosI / max(cosT, 0.04), 1)
spread   = (stretch − 1) · max(|∂n/∂x|, |∂n/∂y|) · 0.5
exponent = 1 / (1/700 + spread²)
glint    = pow(max(dot(refracted, sunDir), 0), exponent) · exponent · 24/700
```

Rescaling the peak by the surviving exponent conserves the lobe's integrated
energy as it widens: resolved water keeps the hard sparkle, the rim hands it to a
broad sheen instead of crawling. Note for any future stretch-aware filtering that
the water-to-air solid-angle Jacobian is `S·eta`, not `S²`, and that the stretch
is anisotropic — meridional `S`, sagittal `eta`.

**The underside outside the critical angle must be BRIGHT.** Total internal
reflection mirrors the upwelling water light, so start from a radiance close to
what the fog converges to — silvery teal near the medium's horizontal ambient:

```text
tirBody = (0.035, 0.14, 0.19) + SSS_TINT · crestScatter · 0.5
```

A near-black `DEEP · 0.55` ceiling carves a bright gap band at the surface
silhouette against converged fog. Keep this in the same family as the medium's
ambient endpoints if either is retuned.

**Opposite-medium structures are FORWARD projected.** A dedicated layer solves
the optical path and rasterizes each source vertex at its refracted screen
position; the water then samples that target at its own screen UV and applies
coverage once. Forward projection is frustum-safe: if a projected image lands
offscreen, so does the water pixel that needed it. Backward tracing never can be
— it projects a ray DIRECTION and requires the vanishing point to be inside the
frustum, which is a pure function of camera pitch.

```text
raw = layer.color.sample(screenUV)
if (raw.a · layer.active > 0.001)     # linear filtering premultiplies edge color
  source = raw.rgb / max(raw.a, 0.001)
```

**Bracket the crossing solve by the critical angle.** A ray in water that
connects to a source in air is inside Snell's cone by construction, so its
crossing point can never lie further than `tan θc ≈ 1.1346` times its own
distance from the interface. Submerged, that bound belongs to the CAMERA, so the
bisection interval is about `1.13 × depth` — identical for every vertex and
independent of distance. Bracketing by the camera-to-source span instead leaves
an absolute error proportional to horizontal separation while the refracted image
shrinks as `1/L`, so the solve goes coarser than the thing it resolves: the
returned crossing becomes a staircase anchored to each vertex's own span, and
neighbouring vertices land on incommensurate grids. Fourteen halvings of the
correct interval land within a ten-thousandth of it.

**What a correct distant refraction looks like**, so it is not "fixed" again.
Refraction compresses incidence only; azimuth passes through untouched. Measured
apparent height of a 6.5 m structure from 14 m down at 1600×900 and a 55 degree
vertical field:

```text
25 m → 135 px    40 m → 46 px    60 m → 16 px    90 m → 6 px    130 m → 2.6 px
```

Roughly `1/L^2.4`, because the compression factor itself grows with distance. A
thin bright streak hard against the rim IS the right answer at range; anything
appreciably taller is a solver artifact. Retire the layer where its image falls
below a pixel — drawing it beyond that scintillates, and clean sky reads better.

**Spectral LOD is by pixel footprint.** The cascade maps carry no mips, and at
grazing incidence the vertical footprint is `distance² · pixelAngle / heightGap`,
so a 4.4 m deck eye is under-sampled at 200 m while a diver sees the same span
steeply and keeps detail. Distance-only fades can never serve both.

```text
PIXEL_ANGLE = 0.001 rad
footprint   = distance² · PIXEL_ANGLE / max(|cameraY − surfaceY|, 0.5)
keeps (shortest wavelengths ~41 / 2.8 / 0.83 m):
  cascade 0 above-water   1 − smoothstep(2.5, 5.5, footprint)
  cascade 1               1 − smoothstep(0.35, 1.2, footprint)
  cascade 2               1 − smoothstep(0.1, 0.4, footprint)
  normal flatten              smoothstep(5.0, 16.0, footprint)
  capillary bands A / B   1 − smoothstep(0.025, 0.12) / (0.008, 0.035)
```

The same three keeps apply to VERTEX displacement, measured against the y = 0
base plane so the grazing gap is just camera height. Flattening the reconstructed
normal while leaving displacement alive collapses displaced triangle rows into a
second comb near the mesh fade.

**Caustics read two ways from one texture.** Surfaces take the footprint-faded
sampler; the god-ray march takes the exact one, because its per-pixel jitter
makes screen derivatives meaningless.

```text
tile 17 m, 256² source grid drawn 3×3 into a 1024² wrapping target
field mean 0.18 (differential-area reprojection conserves flux)
surface fade: mix(field, 0.18, smoothstep(0.06, 0.28, metresPerPixel))
depth fade:   min(exp(y · 0.055), 1)
god rays: march ≤85 m, 8/14/22 steps, hash jitter, weight exp(−0.03 t), × 0.007
```

Fading a caustic web to zero instead of to its mean makes distant sand change
brightness with camera height; it is an albedo term.

**Do NOT add a near-surface scattering layer to the medium.** For any camera
below such a slab, up-grazing rays integrate along it while down-grazing rays
exit it, so a brightness step sits pinned to the exact view horizon and reads as
a screen-space tint mask. Close the horizon gap at its roots instead: terrain
that fills the water column geometrically, and the physically bright underside
above.

## 12. Runtime order

Use this order each frame:

```text
update time and dt uniforms
compute all time-dependent spectra
submit horizontal FFT stages
submit vertical FFT stages
submit centering permutations
assemble maps and update foam history
update optional spray
render ocean and sky
resolve GPU timing asynchronously
```

Sea-state changes that alter `h0` should recompute the initial spectrum on
interaction release, not continuously while dragging a control.

## 13. Geometry, camera, and fog

The presentation uses:

```text
camera FOV: 55°
camera: (0, 16, 68)
target: (0, 0, -20)
surface: 400 m square, 900 × 900 subdivisions
fog: horizon-colored exponential fog
```

The dense plane is justified because displacement is evaluated per vertex.
Scale tessellation against the smallest resolved cascade and camera distance.
Fog must hide the finite mesh edge before the plane ends.

Lower-cost modes should preserve the mechanism:

```text
high: 256², 3 cascades, dense mesh, persistent foam
medium: 256², 2 cascades, lower mesh tessellation, persistent foam
low: 128², 2 cascades, no spray, reduced detail texture
```

Do not call a four-wave analytic surface a low-quality FFT tier; that is a
different representation and should be routed to `$threejs-water-optics`.

## 14. Required diagnostics

Expose:

```text
FFT test errors
Gaussian seed field
per-cascade in-band spectrum
time-evolved frequency magnitude
spatial height
horizontal displacement
height slopes
horizontal derivatives
Jacobian determinant
foam history
foam display coverage
resolved normal
sub-grid normal contribution
final without foam
final without detail
GPU milliseconds by compute and render phase
```

Capture a fixed camera at multiple times. A single attractive frame cannot
prove temporal stability, transform correctness, or foam persistence.

## 15. Failure diagnosis

```text
periodic square tiles:
  cascade lengths or camera coverage expose repetition; add disjoint scales

all waves travel in one artificial line:
  directional spread is too narrow or wind/swell angles are identical

energy explodes near the center:
  DC/small-k singularities are evaluated before masking

surface moves but normals lag:
  derivative maps are stale or sampled with different coordinates

white noise foam:
  thresholding finest-cascade compression without temporal filtering

foam disappears instantly:
  history is not persistent or recovery is interpreted as decay-to-zero

foam never clears:
  recovery sign or Jacobian denominator clamp is wrong

glitter detached from sun:
  visible sky and reflection use different sun direction or color

GPU corruption after increasing N:
  FFT stage count, butterfly table, index type, or scratch allocation is wrong
```
