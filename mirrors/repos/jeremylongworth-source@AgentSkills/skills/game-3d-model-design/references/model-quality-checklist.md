# Model Quality Checklist

Use this checklist when building, repairing, or reviewing a 3D game model.

## Form

- Primary forms read without textures.
- Secondary forms support the design rather than adding noise.
- The silhouette is accurate from gameplay and inspection angles.
- Proportions match the intended style and use case.

## Topology

- Edge flow supports deformation where the model bends.
- Hard-surface support loops, bevels, and normals produce clean shading.
- Poles and triangles are placed where they will not deform or shade badly.
- Nonmanifold geometry, duplicate vertices, loose edges, and hidden faces are cleaned.
- Transforms, normals, scale, and object origins are correct before export.

## UVs And Baking

- UV seams are deliberate and hidden where possible.
- Stretching is acceptable for the asset's visual importance.
- Texel density is consistent unless priority areas intentionally receive more density.
- Mirrored or stacked UVs are intentional and compatible with normal baking and decals.
- Normal, AO, curvature, or other bakes are checked for seams, skewing, and cage issues.

## Rig And Animation

- Deformation loops support shoulders, elbows, knees, wrists, fingers, neck, jaw, eyes, cloth bends, and other moving areas.
- Accessories either deform cleanly or are separated for sockets/attachments.
- The mesh has enough geometry for deformation but not more than the target needs.

## Engine Import

- Export format, triangulation, normals, smoothing, materials, scale, and axes are verified.
- The model imports cleanly into the target engine with no unexpected scale, rotation, missing material, or broken normal issues.
