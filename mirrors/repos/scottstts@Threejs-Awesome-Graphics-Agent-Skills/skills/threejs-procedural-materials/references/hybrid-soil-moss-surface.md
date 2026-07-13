# Hybrid PBR soil and moss surface

## Contents

- Hybrid implementation boundary
- Shared height ownership
- Soil identity fields
- Ground moss identity and height
- Model moss accumulation
- PBR channel coupling
- Diagnostics
- Default parameter contract
- Mound formula
- Crack formula
- Texture contract
- Failure modes

## Hybrid implementation boundary

Treat this example as a hybrid texture-backed and procedural material. The
soil and moss texture sets provide albedo, AO, roughness, and tangent-space
normal microdetail. Procedural fields provide mound displacement, macro
normals, tone and moisture variation, cracks, moss coverage and thickness, and
model accumulation. The displacement texture is loaded with the PBR set
but disabled; procedural height owns the silhouette.

Do not call the soil or moss appearance fully procedural and do not imply that
their PBR texture channels are synthesized by the shader.

## Shared height ownership

Use one world-XZ field for broad mound displacement and finite-difference
relief normals. The field combines five-octave simplex fBm, a coverage
threshold, finer drift, and a rim taper. Read
[the hybrid soil and moss implementation](../examples/hybrid-soil-moss-surface/hybrid-soil-moss-surface.js)
for the exact uniforms, shader injection points, and defaults.

## Soil identity fields

Keep three independently positioned but causally meaningful masks:

- broad tone variation multiplies the base albedo;
- moisture darkens albedo and lowers roughness together;
- warped two-scale Worley borders create recessed dry cracks.

The crack field must drive color, roughness, and groove normals. The moisture
field must drive color and roughness. Do not replace either with unrelated
channel noise.

## Ground moss identity and height

Use one world-XZ fBm mask for both moss coverage and raised moss thickness.
Add `mossHeightAt` to `groundHeightAt`, then reuse the same coverage for moss
albedo, AO, roughness, and normal-map blending. Read
[the hybrid soil and moss implementation](../examples/hybrid-soil-moss-surface/hybrid-soil-moss-surface.js)
for the exact mask, rim taper, shader stages, texture loading, and defaults.

Keep the moss baseline together:

```text
enabled             0 by default
patch scale         0.14
coverage            0.55
patch edge          0.14
thickness           0.14 world units
relief scale        0.90
relief strength     0.70
texture scale       0.35 tiles per world unit
roughness           1.00
normal strength     1.00
AO strength         1.00
```

## Model moss accumulation

Read [the model moss implementation](../examples/hybrid-soil-moss-surface/model-moss-accumulation.js)
when moss must settle on an arbitrary GLB. Share the ground moss maps, tint,
and master enable uniform by reference. Compute coverage in model-locked XZ
coordinates, gate it by the world-normal upward component, and displace along
the local normal after converting the desired world thickness through the
mesh scale. Refresh the group world-to-model matrix after transforms.

Keep these model defaults together:

```text
coverage            0.70
patch scale         0.90
patch edge          0.15
thickness           0.05 world units
upward threshold    0.35
texture scale       2.00
roughness           1.00
AO strength         1.00
relief strength     0.50
relief scale        3.00
```

## PBR channel coupling

Use the included soil and moss albedo, AO, roughness, and OpenGL normal maps
as the texture-backed PBR identity. Tile each material's channels consistently.
Keep texture displacement disabled because procedural mound and moss height
own the silhouette; use texture normals for microstructure and finite-
difference procedural fields for macro relief.

## Diagnostics

Expose final, mound height, moisture, crack, and moss masks. Permit a
ground-only view when a model is present. Report seed, mound coverage, moss
coverage, moisture coverage, crack enablement, and texture scale.

## Default parameter contract

Keep this visual baseline together:

```text
mound scale       0.12
mound depth       0.55 world units
mound coverage    1.00
mound edge        0.15
fine relief scale 0.70
fine strength     0.60
tone scale        0.08
tone amount       0.28
moisture scale    0.18
wet darkening     0.50
wet roughness     0.35
crack amount      0.75
crack scale       0.90
crack width       0.06
crack depth       0.70
macro normal mix  0.70
```

Treat scales as world-XZ frequencies. Seeds are two-dimensional field offsets,
not random numbers sampled per frame.

## Mound formula

```glsl
float base = fbm(worldXZ * uMoundScale + uSeed) * 0.5 + 0.5;
float drift = fbm(worldXZ * uBumpScale + uSeed * 0.5) * 0.5 + 0.5;
float h = base * (1.0 - 0.4 * uBumpStrength
                        + 0.4 * uBumpStrength * drift);
float threshold = mix(1.0 + uMoundEdge,
                      -uMoundEdge,
                      uMoundCoverage);
h *= smoothstep(threshold - uMoundEdge,
                threshold + uMoundEdge,
                base);
```

Taper the field over the final two world units of a plane with half-extent ten.
If the host has a different extent, parameterize the taper rather than silently
stretching this constant.

## Crack formula

Evaluate Worley F1/F2 border distance twice. The secondary field runs at `2.7`
times the primary coordinate and contributes half strength. Form the final
channel with `max(primary, secondary)`. Apply optional fBm warp before both
evaluations so the large and small fissures remain related.

```text
primary   = 1 - smoothstep(0, width, F2 - F1)
secondary = (1 - smoothstep(0, width * 1.6, F2b - F1b)) * 0.5
crack     = saturate(max(primary, secondary)) * amount
```

## Texture contract

Decode only the color map as sRGB. Keep AO, roughness, OpenGL tangent normal,
and displacement maps linear. Use repeat wrapping, identical repeat values,
and the renderer's supported anisotropy. Supply `uv1` for AO on current Three.js
versions. Keep metalness at zero and base roughness at one before maps and
procedural modifiers.

## Failure modes

- texture normal and procedural macro normal use incompatible spaces;
- wet soil darkens but remains equally rough;
- cracks are an albedo decal without groove response;
- geometry uses a different mound field from shading;
- changing coverage changes the seed or spatial frequency;
- the plane edge ends in an unsupported vertical cliff;
- ground moss color and raised height use different masks;
- model moss swims because coverage is evaluated in world coordinates;
- model scale changes the apparent world-space moss thickness;
- ground and model moss use unrelated PBR texture identities.
