# Asset Pipeline Checklist

Use this checklist for game-ready 3D props, environments, modular kits, and engine imports.

## Planning

- Asset purpose, camera distance, platform, and target engine are known.
- Scale and units match the project.
- Pivot, orientation, snapping, collision, and interaction requirements are defined.
- Mesh, material, texture, LOD, and draw-call budgets are stated or inferred from the project.
- Source, export, and engine paths follow the team's naming and folder conventions.

## Geometry

- Polygons are concentrated where they affect silhouette, gameplay, deformation, collision, or close-up lighting.
- Hidden faces and internal geometry are removed unless needed.
- Long thin triangles and avoidable shading artifacts are addressed.
- Modular pieces align on grid and share consistent dimensions.

## Materials And Textures

- Material slots are minimized and named clearly.
- Texture size matches on-screen importance and platform memory limits.
- Texture dimensions are power-of-two when the engine/platform benefits from it.
- Tiling textures, trims, decals, or atlases are used when they improve reuse.
- Source texture files remain editable and output textures are stored with consistent naming.

## Engine Readiness

- Collision is simple enough for runtime use and accurate enough for gameplay.
- LODs preserve silhouette and material assignment.
- Lightmap or secondary UVs exist when the lighting workflow requires them.
- Import settings preserve normals, scale, materials, and animation data as needed.
- The asset is checked in a representative scene with real lighting and camera distance.

## Handoff

- Editable source files, high-poly meshes, low-poly meshes, bakes, textures, exports, and engine assets are distinguishable.
- Known limitations and follow-up tasks are documented.
