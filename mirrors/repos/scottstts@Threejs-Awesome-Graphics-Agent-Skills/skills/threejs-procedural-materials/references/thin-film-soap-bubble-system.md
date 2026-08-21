# Thin-film soap bubble system

Use this reference for floating soap bubbles whose colour comes from coherent
air-film-air interference rather than glass refraction or a painted rainbow.
The `thin-film-soap-bubbles` example couples membrane optics, capillary shape,
flight, nearby-bubble reflection, puncture retraction, and liquid aftermath.

## Contents

1. Optical boundary
2. Cauchy index and Airy reflectance
3. RGB spectral bands and transparent blending
4. Nearby-bubble reflection
5. Radial modes, normals, and volume
6. Flight and capillary mechanics
7. Camera-aware inflow
8. Puncture and visible drops
9. Runtime order
10. Limits and failure patterns
11. Diagnostics

## 1. Optical boundary

A soap membrane is:

```text
air (n0 = 1.000277)
  -> aqueous film (n1 around 1.33, thickness 170…1450 nm)
  -> air (n2 = 1.000277)
```

Because the exterior media match, the transmitted ray is essentially parallel
to the incident ray. Do not treat the bubble as a solid glass sphere. The
defining image is wavelength-dependent coherent reflection from the two film
interfaces, evaluated for the rear membrane and then the front membrane.

Use two separate meshes over one `IcosahedronGeometry(1, 5)`: `BackSide`
first and `FrontSide` second. Both use normal alpha blending, depth test on,
depth write off, and forced single-pass rasterization.

## 2. Cauchy index and Airy reflectance

For wavelength `λ` in nanometres, convert to micrometres and evaluate:

```text
n1(λ) = 1.322 + 0.00306 / (λ × 10^-3)^2
```

At incident cosine `c0`, use Snell's law for `c1` and exact s/p amplitude
coefficients `r01s`, `r12s`, `r01p`, and `r12p`. Film phase is:

```text
phi = 4π n1 thicknessNm c1 / wavelengthNm
```

For either polarization, with `a = r01`, `b = r12`:

```text
R_airy = (a² + b² + 2ab cos(phi)) /
         (1 + a²b² + 2ab cos(phi))
R = 0.5 (R_airy_s + R_airy_p)
```

This form includes the infinite sequence of internal film reflections. It
must approach zero at zero thickness because the exterior media match, remain
inside `[0, 1]`, and approach one at grazing incidence. The example runs these
CPU checks before constructing the system.

## 3. RGB spectral bands and transparent blending

Represent linear-sRGB channels with three-tap bands:

```text
red    center 610 nm, half-width 12 nm
green  center 545 nm, half-width 10 nm
blue   center 460 nm, half-width 10 nm
weights per band = [0.25, 0.5, 0.25]
```

Mean film thickness begins in `470…880 nm`, drains exponentially toward
`260…450 nm` over `9…23 s`, varies with vertical drainage by
`1 - 0.24 * worldRadial.y`, and adds a bottom Plateau-border term up to
`260 nm`. Two advected `triNoise3D` bands add `48 nm` and `18 nm`; clamp the
result to `170…1450 nm`.

Standard transparent blending attenuates the destination with one scalar, so
set:

```text
alpha = clamp(mean(Rrgb), 0.001, 0.985)
sourceRGB = reflectedRadiance * reflectedWeight / alpha
```

The post-blend reflected contribution is then exactly
`reflectedRadiance * reflectedWeight`. The rear membrane adds one extra
`1 - Rrgb` transmission estimate because its reflection must cross the near
membrane again.

## 4. Nearby-bubble reflection

Each bubble carries six analytic neighboring sphere proxies. On the CPU, rank
other live bubbles by approximate angular size and upload only the best six.
The proxy radius is the current physical radius times the volume correction,
the radial-mode envelope, and margin `1.005`.

For a reflection ray, find the nearest positive sphere root beyond
`5e-4 m`. Shade only that hit. Evaluate the near and far proxy membranes with
the same RGB Airy bands, but use only gravity drainage and bottom thickening
for secondary thickness. Compose one bounded shell bounce:

```text
throughFar = Rfar * Tnear * reflectedFar + Tfar * environment
secondary  = Rnear * reflectedNear + Tnear * throughFar
```

The additional `Tnear` on the returning far reflection is required for energy
consistency. Testing every bubble per fragment or rendering per-bubble cube
maps is outside this bounded contract.

## 5. Radial modes, normals, and volume

The shell is a radial graph over five real low-order mode shapes: three
degree-two terms and two degree-three terms. Evaluate position as:

```text
localPosition = unitDirection * (1 + modeField) * volumeScale
```

Derive the exact radial-graph normal by projecting the polynomial gradient onto
the sphere tangent plane:

```text
gradSurface = grad - direction * dot(grad, direction)
normalLocal = normalize(direction - gradSurface / max(radius, 0.85))
```

Never use the undeformed sphere normal. Estimate enclosed volume over `384`
deterministic Fibonacci directions and set
`volumeScale = mean(radius^3)^(-1/3)`. The mechanics self-test requires the
corrected mean cube radius to stay within `2e-4` of one.

## 6. Flight and capillary mechanics

Scene units are metres. The calibrated constants are:

```js
const mechanics = {
  outsideAirDensity: 1.204,
  insideAirDensity: 1.185,
  waterDensity: 997,
  gravity: 9.80665,
  airDynamicViscosity: 1.81e-5,
  effectiveSurfaceTension: 0.056,
  addedMassCoefficient: 0.5,
  bubbleCount: 20,
};
```

Bubble radii follow a log-normal distribution with median `0.105 m` and log
sigma `0.34`, clamped to `0.050…0.195 m`. Film mass is
`waterDensity * 4πR² * thickness`. Inertial mass includes enclosed air, film,
and `0.5` displaced-air added mass.

Use buoyancy minus enclosed-gas and film weight plus quadratic drag. Drag uses
Schiller-Naumann below Reynolds number `1000` and `Cd = 0.44` above it. Advance
with semi-implicit Euler at fixed `1/120 s`, at most five steps per frame.

The air field combines ambient drift, three smooth compact vortices, and weak
shear. An Ornstein-Uhlenbeck velocity process gives each bubble finite-energy,
finite-correlation turbulence. Rotation relaxes toward half the finite-
difference curl of the air field.

For shape degree `l`, use Rayleigh-Lamb scaling:

```text
omega² = (l - 1)(l + 1)(l + 2) gamma /
         ((rhoOutside + rhoInside) R³)
```

Degree-two amplitude is capped at `±0.045`; degree-three at `±0.020`.

## 7. Camera-aware inflow

Respawning is a boundary condition, never a steering force. Sample a sphere
fully outside the current camera frustum, initialize it from the local air
velocity plus small isotropic release variation, and integrate the unchanged
buoyancy/drag equations forward at `1/30 s` for up to `7 s`. Accept the spawn
only when that trajectory naturally intersects the view.

Try up to `96` candidates. If a highly oblique camera prevents a predicted
entry, retain a strictly offscreen release without adding a camera-seeking
force. Prewarm `6.5 s` of invisible history so no bubble is born inside the
first rendered frame.

Once a bubble has entered, recycle it only after it remains outside an expanded
frustum for `2.4 s`. If camera motion invalidates a not-yet-entered trajectory,
resample after `10 s` rather than bending the path.

## 8. Puncture and visible drops

A click opens a geodesic hole in the same local spherical parameter used by the
deformed shell. Film removal is object-space and derivative-antialiased. The
Taylor-Culick speed uses combined two-interface tension:

```text
vTC = sqrt(gammaEffective / (waterDensity * thicknessMeters))
burstDuration = π R / vTC
```

Compute swept cap volume analytically and collect it into a rim whose angular
half-width derives from the mass-equivalent circular cross-section. Once the
rim is many wavelengths thick, shade it with incoherent water/air Schlick
Fresnel rather than thin-film interference.

Resolve only `2…5` millimetre-scale drops from `16…38%` of film volume; the
remaining liquid is unresolved mist. A fixed pool of `64` instanced drops uses
buoyancy-corrected gravity, Schiller-Naumann drag, volume-preserving oblate or
oscillating geometry, and Rayleigh degree-two drop frequency. Drops expire at
`3 s` or beyond `10 m` camera distance.

## 9. Runtime order

Per frame:

```text
refresh the current camera frustum
run up to five fixed 1/120 s mechanics steps
advance the Taylor-Culick rupture clock
advance visible liquid drops
select six reflection peers per live bubble
sort bubbles far-to-near
assign rear then front render order per bubble
render the surrounding scene
```

The reusable system accepts its camera, orbit target, input element, and an
already configured equirectangular environment. It owns all bubble meshes,
materials, mechanics, interaction, and state; it does not own renderer,
camera, controls, or environment loading.

## 10. Limits and failure patterns

- An RGB environment is not spectral radiance. The three bands filter
  representative channel wavelengths but cannot reconstruct missing spectra.
- Nearby bubbles use one bounded analytic shell bounce and sphere proxies; no
  recursive transport or exact deformed-mesh ray intersection is attempted.
- One scalar destination alpha cannot apply chromatic transmitted attenuation;
  reflected RGB remains exact for the sampled bands while destination
  attenuation uses their mean.
- A glass volume, screen-space distortion, painted hue, or view-facing billboard
  is the wrong optical model.
- An undeformed normal disconnects interference bands from capillary shape.
- Uniform min/max radii remove the characteristic population distribution.
- In-frame respawn or camera-directed acceleration makes recycling visible.

## 11. Diagnostics

The example exposes:

```text
final                 full membrane, nearby reflection, mechanics, and drops
no-interreflection    environment reflection with all peer proxy radii zeroed
spherical-membranes   optical film with five radial-mode uniforms set to zero
rear-membranes        rear shell pass alone, with visible drops hidden
```

The deterministic CPU gates cover zero-thickness cancellation, reflectance
bounds, grazing reflectance, mechanics finiteness, volume correction,
Taylor-Culick speed, rim instability scales, and rim mass conservation.
