---
name: threejs-procedural-materials
description: Author production procedural materials in Three.js. Use for hybrid texture-backed PBR soil and moss with procedural displacement and masks, upward-facing model moss accumulation, atlas filtering, specular AA, planet-space fields, terrain wetness, lava and emissive surfaces, per-instance dissolve, authored PBR identities, derivative normals, and custom direct-light shadow modulation.
---

# Procedural Materials

Build a material from surface identity and causes. Color, roughness, metalness, normal, transmission, and emission should describe the same surface—not unrelated noise textures.

## Material graph order

```text
stable coordinates
  → structural fields
  → material identity weights
  → causal modifiers
  → filtered microstructure
  → PBR channels
  → lighting/shadow extensions
```

Read [references/procedural-pbr-system.md](references/procedural-pbr-system.md)
for atlas filtering, specular AA, planetary coordinates,
world-height wetness, per-instance dissolve, and authored PBR response bundles.

Read the
[sculpted gallery frame geometry](../threejs-procedural-geometry/examples/sculpted-gallery-frame/frame-geometry.js)
for walnut, antique-gold, and ebony texture/roughness/metalness/clearcoat
bundles under a grazing-light setup.

Read the
[procedural planet surface](../threejs-procedural-planets/examples/procedural-planet-surface/planet-system.js)
for shared geological, climate, water, biome, roughness, and derivative-normal
causes on a procedural planetary surface.

Read the
[analytic wave optics](../threejs-water-optics/examples/analytic-wave-optics/water-system.js)
for coupled reflection, refraction, absorption, filtered microstructure,
resolved crest response, and their diagnostic channels.

Read the
[lava flow surface material](examples/lava-flow-surface/lava-surface.js)
for raymarched procedural height fields whose normals, rock/lava identity,
emission, glow, embers, fog, and grain are coupled to one material cause stack.

## Required controls

- real or perceptual texture scale;
- material identity weights;
- roughness range and micro-normal strength;
- the causal fields required by the selected material pattern;
- distance/derivative filtering;
- specular antialiasing;
- channel and mask debug modes.
- emissive-material debug modes when the material owns glow or volumetric
accumulation.

Read [references/hybrid-soil-moss-surface.md](references/hybrid-soil-moss-surface.md)
and the
[hybrid soil and moss implementation](examples/hybrid-soil-moss-surface/hybrid-soil-moss-surface.js)
for texture-backed soil and moss albedo, AO, roughness, and normal microdetail
combined with procedural mound displacement, moisture, moss coverage/height,
and warped cellular cracks. Do not describe its surface identity as fully
procedurally synthesized. When moss must also settle onto a model, read the
[model moss implementation](examples/hybrid-soil-moss-surface/model-moss-accumulation.js)
for model-locked coverage, upward-face accumulation, displaced thickness, and
shared moss PBR identity.

## Failure conditions

- every PBR channel samples independent noise;
- roughness is a scalar afterthought;
- high-frequency normals survive below one pixel;
- triplanar projection has visible orientation or scale seams;
- atlas padding is ignored under mipmapping;
- custom lighting removes energy conservation without an explicit stylized goal;
- post-processing is used to hide unstable highlights.

## Routing boundary

Use `$threejs-procedural-fields` when the main problem is designing shared
scalar/vector causes. Use `$threejs-procedural-planets` for a complete
orbit-to-close-approach body, not merely its material. Use
`$threejs-parallax-occlusion-mapping` when a height field must own ray-marched
intersection, silhouette coverage, or relief-aware shadows.
