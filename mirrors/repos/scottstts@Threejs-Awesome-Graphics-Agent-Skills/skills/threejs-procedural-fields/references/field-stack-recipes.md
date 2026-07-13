# Procedural field-stack recipes

Use this reference to construct coherent field bundles for spherical terrain, altitude-filtered detail, terrain wetness, water optics, and structured stochastic placement.

## Contents

- Stable coordinate ownership
- Planetary sphere fields
- Altitude filtering
- Wetness-coupled game terrain
- Shared-phase water fields
- Structured stochastic placement
- Cross-system implementation contract
- Diagnostics


## Stable coordinate ownership

The strongest common rule is that one stable coordinate domain owns related
visual channels.

Planetary terrain materials store normalized undeformed sphere direction in a
`surfaceDirection` attribute. Terrain shader fields sample:

```text
terrainCoordinateKm = normalize(surfaceDirection) * radiusKm
```

They do not sample the interpolated displaced position. This prevents noise
stretching over steep relief and allows orbit/close-detail filtering in the
same kilometer domain.

Wetness-coupled game terrain samples `positionWorld`, because wetness is tied
to a world water height. Open-water surfaces likewise sample world XZ so near
tiles and far ocean quads share wave phase.

Choose coordinates from the cause:

```text
planet geology -> undeformed radial direction * physical radius
water/wetness -> shared world plane
tree growth -> branch-local longitudinal and radial coordinates
```

## Planetary sphere fields

A planet-scale material performs tangential warp:

```text
warp = three seeded noise channels - 0.5
tangentWarp = warp - radial * dot(warp, radial)
warpAmplitudeKm = max(radiusKm * 0.012, 36)
warped = normalize(terrainKm + tangentWarp * warpAmplitudeKm) * radiusKm
```

Its broad terrain synthesis uses separated bands:

```text
macro A frequency = 0.00034, weight 0.52
macro B frequency = 0.00092, internal scale 0.52, weight 0.33
ridge frequency = 0.0029, weight 0.25
crater-like frequency = 0.0069, exponent 2.9
```

The CPU geometry uses a different deterministic value-noise stack:

```text
continental: 5 octaves, lacunarity 2.03, gain 0.50
highlands: 4 octaves, lacunarity 2.15, gain 0.55
ridges: 4 octaves, lacunarity 2.08, gain 0.52
crater-like: 3 octaves, pow(1 - noise, 3.2)
```

This mismatch is an observed defect, not a recommended pattern. The material
mixes only `8%` actual geometry displacement into shader macro height. A new
implementation should share one deterministic field or validate CPU/GPU parity
at fixed sphere directions. The `procedural-planet-surface` example under
`$threejs-procedural-planets` demonstrates the shared-field form: one
deterministic `sharedTerrain` stack evaluated identically for CPU displacement
and GLSL shading.

Derived climate causes in this field stack:

```text
humidity =
  0.65 * broadNoise(0.0022)
  + 0.35 * detailNoise(0.0075)

temperature =
  (1 - abs(latitude)^1.35) * 0.85
  + 0.15
  - macroHeight * 0.32

slope =
  1 - abs(dot(localNormal, radialDirection))
```

Snow, arid, lush, and rock masks combine those fields with altitude, ridges,
and a smaller jitter field. The important mechanism is causal reuse, not the
specific color palette.

## Altitude filtering

The same planetary material computes:

```text
cameraAltitude = max(distance(camera, center) - radius, 0)
detailAltitude = min(cameraAltitude, externally supplied detail altitude)

near = max(radius * 0.022, 6.5)
mid  = max(radius * 0.11, 24)
far  = max(radius * 0.50, 140)

nearWeight = 1 - smoothstep(near, mid, detailAltitude)
farWeight = smoothstep(mid, far, detailAltitude)
midWeight = clamp(1 - nearWeight - farWeight, 0, 1)
```

These weights attenuate bump, coastline sharpness, wave detail, clearcoat, and
micro material variation. The frequencies remain stable; contribution fades.

## Wetness-coupled game terrain

A stylized game terrain material uses three world-space noise bands:

```text
noise1: position * (0.2, 1, 0.2), amplitude 0.05, bias 0.2
noise2: position * 9, amplitude 0.4, bias 0.5
noise3: position * (14, 3, 14), amplitude 2, bias 0.5
soilNoise = noise1 + noise2 + noise3
```

Surface identity derives from geometry orientation:

```text
grassness = smoothstep(0.01, 1, normalWorld.y^1.6)
color = mix(soilColor, grassColor, grassness)
```

The same identity blends soil and grass roughness fields. World height adds a
wetness response near the water level:

```text
wetness = smoothstep(-1, -7, positionWorld.y) * noise1 * 3.5
roughness -= wetness
```

The reversed-looking edges are intentional, but GLSL leaves `smoothstep`
undefined when `edge0 > edge1`. Write it as `1 - smoothstep(-7, -1, y)` for
portable behavior.

## Shared-phase water fields

An open-water field bundle evaluates six directional wave bands in one
function and returns:

```text
RGB = analytic normal from summed gradients
A = crest metric derived from the same slopes and phases
```

Wavelengths:

```text
12, 6, 2.5, 5.25, 3.0, 1.5 world units
```

Amplitudes relative to the base:

```text
1.0, 0.55, 0.22, 0.12, 0.08, 0.05
```

The three smallest bands are attenuated from screen derivatives using their
wavenumbers. Foam consumes the returned crest metric; it does not sample an
unrelated scrolling mask. The `analytic-wave-optics` example under
`$threejs-water-optics` applies the same contract: `resolvedNormalAndCrest()`
returns the resolved normal and crest from one evaluation and attenuates its
three smallest bands by their derivative footprint.

## Structured stochastic placement

The `structured-ash-growth` example under `$threejs-procedural-vegetation`
demonstrates a different kind of field: constrained discrete placement. Child
branches use stratified longitudinal slots and independently permuted angular
slots. Randomness selects within valid slots rather than choosing every
position freely.

That same mechanism applies to:

```text
branch emergence
façade variants
particle burst directions
crater distribution
cloud-cell placement
```

When a pattern must remain authored, stratify the domain before applying
random jitter.

## Cross-system implementation contract

Before coding, record:

```text
coordinate domain
physical/perceptual units
primary fields
derived causes
consuming channels
filtering rule
CPU/GPU parity requirement
seed ownership
```

Reject a field stack when:

- color, roughness, and normal use unrelated structure;
- geometry and shading claim the same feature but evaluate different functions;
- a categorical mask is only a narrow noise threshold;
- high-frequency terms survive after their projected footprint is subpixel;
- world effects use object coordinates or planetary effects use flat world Y;
- random placement has no strata, budget, or semantic constraints.

## Diagnostics

Expose:

```text
source coordinates
tangential warp vector
each frequency band
actual geometry height versus shader height
humidity, temperature, slope, and identity masks
near/mid/far weights
water normal and crest from the same evaluation
wetness by world height
seed and stratification cells
```
