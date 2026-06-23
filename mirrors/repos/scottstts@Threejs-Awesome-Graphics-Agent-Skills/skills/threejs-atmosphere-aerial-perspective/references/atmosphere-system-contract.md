# Atmosphere system contract

Use this contract to choose between a precomputed LUT/ellipsoid atmosphere and bounded dynamic integration while keeping sky, aerial perspective, surface lighting, and coordinate transforms coherent.

## Contents

- Shared parameter model
- LUT atmosphere implementation LUT contract
- Ellipsoid and depth ownership
- planet-space implementation body profiles
- planet-space implementation integration
- Shell/post handoff
- Implementation limits
- Diagnostics


## Shared parameter model

`LUT atmosphere implementation` keeps one atmosphere object for sky and aerial perspective.
Earth-like defaults:

```text
solar irradiance = (1.474, 1.8504, 1.91198)
sun angular radius = 0.004675 rad
bottom radius = 6,360,000 m
top radius = 6,420,000 m
Rayleigh scattering = (0.005802, 0.013558, 0.0331)
Mie scattering = (0.003996, 0.003996, 0.003996)
Mie extinction = (0.00444, 0.00444, 0.00444)
Mie phase g = 0.8
absorption extinction = (0.00065, 0.001881, 0.000085)
ground albedo = 0.1
```

Density profiles are two-layer functions:

```text
density(h) =
  clamp(
    expTerm * exp(expScale * h)
    + linearTerm * h
    + constantTerm,
    0,
    1
  )
```

The default Rayleigh exponential scale is `-0.125`, Mie `-0.833333`.
Absorption uses two linear layers centered around the ozone region rather than
another ground-heavy exponential.

One explicit meter-to-render-unit conversion is applied when parameters become
uniforms. Preserve this single conversion boundary.

## LUT atmosphere implementation LUT contract

The sky material and aerial-perspective effect consume the same:

```text
transmittance texture
scattering 3D texture
irradiance texture
optional single-Mie and higher-order scattering textures
atmosphere parameters
sun direction
```

The sky material reconstructs rays from inverse projection and inverse view
matrices. It can render sun, moon, ground, and shadow-length integration.

The aerial-perspective effect owns:

```text
camera projection/view and inverses
camera world position
depth
optional normal buffer
ellipsoid radii
world-to-ECEF transform
altitude correction
geometric-error correction
overlay/cloud shadow/light-mask inputs
```

Default composition enables segment transmittance and inscatter. Direct sun
light and sky-light relighting are separate switches. Do not collapse these
signals into one fog color.

## Ellipsoid and depth ownership

The geospatial path defaults to `Ellipsoid.WGS84` and can correct both
camera altitude and geometry error. Atmosphere altitude is therefore not
`worldPosition.y`.

Required coordinate contract:

```text
world position
  -> world-to-ECEF
  -> ellipsoid-relative position
  -> corrected altitude
  -> LUT coordinates / segment scattering
```

The aerial effect declares depth ownership through its post-processing effect
attribute. It also supports octahedral normals or normal reconstruction when
lighting terms require orientation.

## planet-space implementation body profiles

planet-space implementation derives profiles by body kind and density. Terrestrial baseline:

```text
Rayleigh = (0.0058, 0.0135, 0.0331)
Mie scattering = (0.0022, 0.0022, 0.0022)
Mie extinction = (0.0032, 0.0032, 0.0032)
Rayleigh scale height = lerp(7.2, 10.8, normalized density) km
Mie scale height = lerp(0.9, 1.7, normalized density) km
Mie g = 0.76
ozone extinction = (0.00065, 0.001881, 0.000085)
solar intensity = 13.8
```

Rocky bodies reduce scattering and remove ozone. Gas/ice giants use much
larger scale heights and `g` around `0.80–0.82`.

The implementation enforces:

```text
mieExtinction[channel] >= mieScattering[channel] + 0.0001
g <= 0.92
```

This prevents negative absorption and unstable phase behavior.

## planet-space implementation integration

For each camera ray, planet-space implementation:

1. intersects the top atmosphere sphere;
2. clamps the segment against the surface sphere;
3. marches `ATMOSPHERE_VIEW_SAMPLES`;
4. accumulates Rayleigh, Mie, and triangular ozone depth;
5. at every view sample, marches a sun segment with
   `ATMOSPHERE_LIGHT_SAMPLES`;
6. tests planet occlusion of the sun;
7. evaluates Rayleigh and anisotropic Mie phase;
8. returns in-scattered radiance and view transmittance.

It adds an upper-Rayleigh exponential term and fades density over the final
`24%` of atmosphere thickness to soften the shell edge.

The compact path includes a small multiple-scattering approximation derived
from `1 - transmittance`; it is not equivalent to the precomputed higher-order
scattering available in `LUT atmosphere implementation`.

## Shell/post handoff

planet-space implementation renders a double-sided shell and a depth-aware post path from one
profile. Runtime face-opacity weights avoid a hard front/back cull switch.

The post blend is based on altitude above the atmosphere top:

```text
entry blend near = 140 km
entry blend far = max(448 km, visual atmosphere height * 0.58)
post blend = 1 - smoothstep(near, far, altitudeFromTop)
```

The post path applies only where scene depth represents a surface. The shell
continues to own sky pixels and limb appearance.

Preserve:

```text
one body center and radius
one atmosphere profile
one sun direction
one unit conversion
surface-depth classification
continuous shell/post blend
```

## Implementation limits

- planet-space implementation performs nested dynamic integration and is expensive compared with
  LUT lookup.
- Its atmosphere uses spheres, while `LUT atmosphere implementation` supports an ellipsoid
  and ECEF correction.
- planet-space implementation’s multiple-scattering term is an artistic approximation.
- `LUT atmosphere implementation` is version-sensitive and built around its own
  post-processing/coordinate utilities; adapt the architecture, not imports
  blindly.
- Do not combine LUT radiance and dynamic integrated radiance at full weight.
  Choose ownership or a validated transition.

## Diagnostics

Expose:

```text
planet/ECEF coordinates and corrected altitude
top and bottom intersections
Rayleigh, Mie, and absorption density
view and sun optical depth
sun visibility
segment transmittance
single and multiple scattering
sky versus surface depth classification
shell front/back opacity
post blend
LUT coordinates and texture slices
```
