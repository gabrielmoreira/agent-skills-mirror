# Analytic water surface system

Use this reference for bounded or analytic water with shared displacement and normals, derivative-filtered detail, analytic reflection, heuristic refraction, absorption, and crest foam. Use `$threejs-spectral-ocean` for stochastic FFT seas.

## Contents

- cinematic implementation displaced ocean
- Shared displacement/normal contract
- cinematic implementation optical hierarchy
- atlas-based renderer normal-only wave bundle
- atlas-based renderer refraction and absorption
- Foam and distance response
- Objective limits
- Diagnostics


## cinematic implementation displaced ocean

The Miller’s Planet scene uses five authored Gerstner-style components:

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

## cinematic implementation optical hierarchy

The surface adds four smaller sinusoidal normal bands after the displaced
normal, with spatial scales `0.44`, `0.8`, `1.55`, and `2.8` and decreasing
strength.

Water response:

```text
F0 = 0.02
F = F0 + (1 - F0) * (1 - NdotV)^5
```

Reflection samples the same analytic sky used by the sky dome. Sun response:

```text
reflection disc = dot(reflection, sun)^2500 * 22
reflection halo = dot(reflection, sun)^14 * 1.5
surface specular = dot(normal, halfVector)^1200 * 22
```

The transmitted body is a deep/shallow blue mix. A forward-scatter term uses
`dot(view, -sun)^4`, scaled by `0.42 * (1 - Fresnel)`. Crest foam derives from
`(1 - normal.y)`, and distance haze uses:

```text
1 - exp(-distance * 0.0026)
```

## atlas-based renderer normal-only wave bundle

atlas-based renderer’s water mesh is not displaced by the material. It computes a normal
and crest from six world-XZ wave bands:

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
metric combines slope with phase alignment from all six waves.

Use this only when normal-only water is appropriate. Do not claim geometry and
normal parity because the geometry remains flat.

## atlas-based renderer refraction and absorption

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

When scene color exists, it samples two clamped screen offsets from the
refracted direction and procedural noise. When scene depth is absent, path
length is approximated from fallback thickness and the refracted vertical
component:

```text
path = fallbackDepth / abs(refractedDirection.y)
transmittance = exp(-absorption * path)
```

This produces depth-dependent color but not actual object thickness.

## Foam and distance response

atlas-based renderer foam:

```text
foamSeed = noise(xz * 0.9 + wind * time * foamDrift)
foam = smoothstep(
  threshold,
  1,
  crest * noisy modulation
)
```

It is causally attached to the crest output, then broken up by noise.

The material also increases opacity over a configured distance range
(`25–140` world units) and treats underwater alpha separately. This helps a
bounded transparent surface meet a far-ocean horizon.

## Objective limits

- cinematic implementation uses an authored five-wave sea, not a directional spectrum.
- atlas-based renderer is normal-only and cannot produce crest silhouette or geometric
  parallax.
- atlas-based renderer refraction has no depth rejection and can sample foreground objects.
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
