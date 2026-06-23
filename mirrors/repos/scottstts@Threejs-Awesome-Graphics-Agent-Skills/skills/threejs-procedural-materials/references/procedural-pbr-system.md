# Procedural PBR material systems

Use this reference for atlas filtering, shared shadow and light causes, planet-space material fields, wetness, per-instance dissolve, and authored physical-material identities.

## Contents

- atlas-based renderer block material
- Atlas and minification response
- Shared shadow/light causes
- planet-space implementation planetary material
- pooled VFX system terrain and debris
- selective gallery pipeline authored PBR identities
- Selection rules and limitations
- Diagnostics


## atlas-based renderer block material

The block material is a complete custom shader whose inputs include:

```text
atlas albedo and optional normal
per-vertex AO/skylight/tint color
sun direction/color
four custom shadow cascades
projected procedural cloud shadow
environment cube
roughness/metalness
daylight and starlight factors
```

Its useful material mechanisms are:

1. world position and view-space depth remain available for cascade choice;
2. world-space shadow texel width scales bias and filter radius;
3. cloud shadow projects a receiver point to a cloud plane along sun direction;
4. normal derivatives increase effective roughness;
5. atlas sampling clamps to the current tile interior;
6. anisotropic minification chooses a major-axis multi-tap filter.

Specular antialiasing:

```text
variance =
  max(dot(dFdx(N), dFdx(N)),
      dot(dFdy(N), dFdy(N)))

filteredRoughness =
  clamp(sqrt(roughness^2 + variance), 0, 1)
```

This is a practical filtering mechanism. It should still be compared against the
renderer’s current physical-material and normal-filtering behavior before
replacing built-in shading.

## Atlas and minification response

For an atlas with `atlasSize` tiles across and `tileSize` texels per tile:

```text
tile width = 1 / atlasSize
horizontal inset = 0.5 / (atlasSize * tileSize)
vertical inset = 0.5 / tileSize
```

Estimate the `dFdx/dFdy` footprint in texels. When minification grows, blend
away from the base sample. If anisotropy exceeds `2`, sample `7` or `9` taps
along the major axis.

This avoids adjacent-tile bleed for direct taps, but shader clamping cannot fix
atlas mip levels that were generated without duplicated tile borders. Require
offline mip-safe padding when adopting this mechanism.

## Shared shadow/light causes

atlas-based renderer’s cloud shadow uses the same conceptual field as its visible cloud
layer:

```text
project receiver to cloud altitude along sun direction
advect by shared wind and time scale
evaluate the same five-octave cloud field
apply coverage and density shaping
attenuate direct sunlight
```

The material does not darken emission or all ambient response with this term.
Keep projected environmental shadows attached to direct-light ownership.

## planet-space implementation planetary material

planet-space implementation’s solid planets preserve an undeformed radial attribute and use it for
all geological sampling. Camera-altitude weights reduce high-frequency bump
and optical detail.

For gas and ice giants, seam-free longitude is represented as:

```text
longitude = atan(z, x)
longitude circle = (cos(longitude + advection), sin(longitude + advection))
coordinate = (circle.x, circle.y, latitude01)
```

Latitude bands, seeded warp, turbulence, and storm masks share this coordinate.
Roughness responds to the same final mask. Limb haze and wrapped diffuse
lighting are added separately.

For solid bodies, procedural bump normal is derived from screen derivatives of
the height node and view position. This keeps the renderer’s material lighting
path while changing only the normal input.

The known debt is geometry/material field mismatch; see the planet and field
references. Do not infer that close bump can substitute for silhouette parity.

## pooled VFX system terrain and debris

Terrain identity:

```text
grassness = smoothstep(0.01, 1, normalWorld.y^1.6)
color = mix(shared-noise soil, shared-noise grass, grassness)
roughness = blend(soil response, grass response, grassness) - wetness
metalness = 0.2
```

Wetness comes from world height near the water plane and the broad noise field.
It changes roughness and color together.

Debris uses per-instance `isOrange` and `removalTimeSeconds`. Geometry-space
noise controls discard as lifetime expires. Its color is reinforced at the rim
through Fresnel and receives a small environment term of `0.05`.

The reusable pattern is per-instance material state, not one cloned material
per object.

## selective gallery pipeline authored PBR identities

The gallery defines distinct frame surfaces with real texture and response
bundles:

| Surface | Roughness | Metalness | Clearcoat | Clearcoat roughness | Bump |
| --- | ---: | ---: | ---: | ---: | ---: |
| walnut | 0.42 | 0.04 | 0.62 | 0.28 | 0.022 |
| antique gold | 0.24 | 0.78 | 0.24 | 0.20 | 0.012 |
| ebony | 0.40 | 0.03 | 0.70 | 0.24 | 0.018 |

Wall plaster stays near roughness `0.94–0.96`, floor `0.92`, and mat board
`0.92`. These ranges preserve material separation before bloom.

Chandelier bloom meshes intentionally use `MeshBasicMaterial`, with bulb and
filament materials marked `toneMapped = false`. That is contribution ownership
for a stylized light source, not a physically based metal recipe.

## Selection rules and limitations

Use the material mechanisms according to representation:

```text
atlas voxel surface -> atlas-based renderer filtering and custom shadow hooks
planet surface -> planet-space implementation radial fields and altitude filtering
terrain/wetness -> pooled VFX system world-height causal blend
authored luxury material -> selective gallery pipeline response bundle
pooled effect debris -> pooled VFX system per-instance attributes
```

Do not combine every mechanism into one universal material.

Exact node/material extension hooks are version-sensitive. Inspect the
installed renderer before porting atlas-based renderer's full custom shader or adapting
planet-space implementation's node-material normal and emissive inputs.

Observed limits:

- atlas-based renderer replaces the full physical shader, increasing maintenance and making
  backend migration harder.
- Its custom lighting must be checked for energy consistency and environment
  parity.
- selective gallery pipeline’s chandelier basic materials rely on selective bloom and are not a
  substitute for lit metal in non-emissive views.
- pooled VFX system uses undefined reversed-edge `smoothstep` in wetness expressions; write
  portable equivalent logic.
- planet-space implementation has approximate rather than exact geometry/material field parity.

## Diagnostics

Expose:

```text
atlas tile and sample footprint
roughness before/after specular AA
cloud shadow field
shadow cascade and world texel size
planet coordinate, altitude weights, and material masks
terrain grassness and wetness
debris instance attributes and dissolve threshold
base frame material without post
raw emissive contribution for bloom-only materials
```
