# Analytic water surface system

Use this reference for analytic water surfaces with shared displacement and normals, derivative-filtered detail, analytic reflection, heuristic refraction, absorption, and crest foam. For the bounded pool heightfield simulation and its volume optics, read the `interactive-pool-volume` example. Use `$threejs-spectral-ocean` for stochastic FFT seas.

## Contents

- Authored five-wave displaced ocean
- Shared displacement/normal contract
- Optical hierarchy
- Normal-only wave bundle
- Side-aware refraction and absorption
- Foam and distance response
- Objective limits
- Diagnostics


## Authored five-wave displaced ocean

The `analytic-wave-optics` example uses five authored Gerstner-style
components:

| Direction X/Z | Amplitude | Wavelength | Steepness |
| --- | ---: | ---: | ---: |
| `0.94, 0.32` | 0.38 | 28.0 | 0.50 |
| `-0.42, 0.91` | 0.24 | 18.0 | 0.46 |
| `0.78, -0.52` | 0.16 | 12.0 | 0.42 |
| `-0.35, -0.78` | 0.10 | 10.0 | 0.35 |
| `0.55, 0.62` | 0.06 | 9.5 | 0.28 |

For every wave:

```text
k = 2π / wavelength
omega = sqrt(9.81 * k)
phase = k * dot(direction, xz) - omega * time
horizontal offset = direction * steepness * amplitude * cos(phase)
vertical offset = amplitude * sin(phase)
```

The ocean is a `1200 x 1200` plane with `256 x 256` segments. A CPU height
function evaluates the same five vertical sine terms for camera clearance.

## Shared displacement/normal contract

The TSL normal function evaluates the same directions, amplitudes,
wavelengths, and phases as displacement:

```text
Nx += direction.x * k * amplitude * sin(phase)
Ny += steepness * k * amplitude * cos(phase)
Nz += direction.y * k * amplitude * sin(phase)
normal = normalize((-Nx, 1 - Ny, -Nz))
```

This exact parameter sharing is the defining mechanism. If a wave changes,
both geometry and normal evaluation change together.

## Optical hierarchy

After the displaced macro normal, the example adds three derivative-attenuated
micro wave bands (wavelengths `5.25`, `3.0`, `1.5`, amplitudes `0.12`, `0.08`,
`0.05`) and two low-amplitude noise gradients for wind-aligned
micro-turbulence.

Water response is side-aware:

```text
above water: eta = 1 / 1.333
underwater:  eta = 1.333
F0 = ((1 - eta) / (1 + eta))^2 + 0.035
F = F0 + (1 - F0) * (1 - |NdotV|)^5
```

Reflection samples the same analytic sky used by the sky dome. Sun response:

```text
reflection disc = dot(reflection, sun)^2500 * 14
reflection halo = dot(reflection, sun)^14 * 1.1
surface specular = dot(normal, halfVector)^1200 * 12
```

The transmitted body mixes a deep-blue base with the refracted scene sample
(`mix(deep, sceneRefraction, 0.65)`) under Beer-Lambert transmittance. A
forward-scatter term uses `dot(view, -sun)^4`, scaled by `0.42 * (1 - Fresnel)`.
Crest scatter adds `crest * 0.28`; crest itself derives from `(1 - normal.y)`
slope, and distance haze uses:

```text
1 - exp(-distance * 0.0026)
```

## Normal-only wave bundle

The flat-mesh variant leaves geometry undisplaced. Its material computes a
normal and crest from six world-XZ wave bands:

```text
wavelengths = 12, 6, 2.5, 5.25, 3.0, 1.5
relative amplitudes = 1, 0.55, 0.22, 0.12, 0.08, 0.05
directions = wind, cross-wind, 45°, +30°, -30°, +60°
dispersion = sqrt(9.8 * k)
```

High-frequency bands are attenuated from screen derivatives:

```text
aa3 = 1 - smoothstep(0, 2.0, footprint * k3)
aa4 = 1 - smoothstep(0, 1.5, footprint * k4)
aa5 = 1 - smoothstep(0, 1.0, footprint * k5)
```

Two low-amplitude noise gradients add wind-aligned micro-turbulence. The crest
metric combines slope with phase alignment from all six waves. The
`analytic-wave-optics` example adopts this bundle’s three finest bands and
turbulence gradients as its micro detail.

Use this only when normal-only water is appropriate. Do not claim geometry and
normal parity because the geometry remains flat.

## Side-aware refraction and absorption

Defaults:

```text
air/water eta = 1 / 1.333
extra Fresnel bias = 0.035
absorption = (0.20, 0.06, 0.02) per meter
fallback depth = 4 m
refraction strength = 0.18
roughness control = 0.35
```

The shader is side-aware:

```text
above water: eta = air / water
underwater: eta = water / air
F0 = ((1 - eta) / (1 + eta))^2 + artistic bias
```

When scene color exists, sample one or two clamped screen offsets from the
refracted direction and procedural noise (the `analytic-wave-optics` example
uses one clamped sample). When scene depth is absent, path length is
approximated from fallback thickness and the refracted vertical component:

```text
path = fallbackDepth / abs(refractedDirection.y)
transmittance = exp(-absorption * path)
```

This produces depth-dependent color but not actual object thickness.

## Foam and distance response

Crest-attached foam:

```text
foamSeed = noise(xz * 0.9 + wind * time * foamDrift)
foam = smoothstep(
  threshold,
  1,
  crest * noisy modulation
)
```

It is causally attached to the crest output, then broken up by noise.

A bounded transparent surface can also increase opacity over a configured
distance range (`25–140` world units) and treat underwater alpha separately.
This helps it meet a far-ocean horizon.

## Objective limits

- The five-wave sea is authored, not a directional spectrum.
- The normal-only bundle cannot produce crest silhouette or geometric
  parallax.
- The screen refraction has no depth rejection and can sample foreground
  objects.
- Its thickness is a fallback estimate, not reconstructed scene thickness.
- The demonstrated paths use artistic sky reflection rather than environment
  prefiltering or planar reflection.
- Crest foam is instantaneous and lacks persistent build/decay.
- Route to `$threejs-spectral-ocean` when the target is implementation-level
  spectral open water rather than a bounded authored-wave surface.

## Diagnostics

Expose:

```text
each authored wave band
displaced position and analytic normal
normal-only versus displaced comparison
derivative attenuation per micro band
crest metric before noise
Fresnel and side classification
raw refraction UV and validity
fallback path length and transmittance
reflection, body scatter, glint, and foam separately
distance haze/opacity
CPU versus GPU surface height at camera position
```
