---
name: game-blender-asset-pipeline
version: 1.0.1
description: "Use when authoring and optimizing 3D game assets in Blender for export to a game engine — clean topology and retopo, UV unwrapping, baking high-to-low normal/AO maps, scale/orientation and apply-transforms hygiene, armature rigging and weight painting, LOD generation, custom collision hulls, and glTF/FBX export settings for Unreal/Unity/Godot. Triggers on Blender, glTF, GLB, FBX, retopology, normal bake, UV unwrap, armature, weight paint, LOD, collision hull, apply transform, export to engine. Not for Godot's import-dock configuration of an already-exported file (use assets-pipeline), in-engine material/lighting (use 3d-essentials), or procedural/AI mesh generation (use the relevant generation skill)."
risk: safe
source: opus
date_added: 2026-06-27
---

# Blender Asset Pipeline

Author, optimize, and export game-ready 3D assets from Blender so they arrive in Unreal, Unity, or Godot with correct scale, clean topology, working rigs, and engine-friendly materials.

## When to Use

- **Topology & retopo**: turning a sculpt or messy mesh into clean, evenly-quaded, animation-ready geometry with a sane poly budget.
- **UVs & baking**: unwrapping, packing UDIMs/atlases, and baking high-poly detail (normal, AO, curvature) onto a low-poly target.
- **Transform hygiene**: scale, orientation (which axis is "up"/"forward"), origins, and applying transforms before export.
- **Rigging & skinning**: armatures, bone naming/hierarchy, weight painting, and exporting deformation rigs.
- **LODs & collision**: generating level-of-detail chains and authoring simple **collision hull** meshes separate from the render mesh.
- **Export**: choosing and configuring **glTF 2.0** or **FBX** export for the target engine.

## Prerequisites

- Blender installed (e.g., Windows default path: `C:\Program Files\Blender Foundation\Blender 4.x\blender.exe`).
- Target game engine documentation available for import conventions.
- When configuring glTF/FBX export, follow **§6 Export**. When authoring collision hulls, follow **§5 LODs & Collision Hulls** (engine naming: Unreal `UCX_<MeshName>`, Godot `*-colonly` / `*-convcol`).

## Procedure

### 1. Transform Hygiene & Scale
1. Set scene units to **Metric** and scale to **1.0** (1 Blender unit = 1 meter).
2. Place the object origin where the engine pivots it (feet for characters, base for props), not at the random sculpt center.
3. Apply **Rotation & Scale** (`Ctrl+A` -> `Rotation & Scale`) before export. Unapplied scale corrupts normals, physics, and child transforms.
4. Name objects/materials meaningfully; engines import them by name. Avoid duplicate `.001` suffixes.

### 2. Topology & Poly Budget
1. Model in **quads** for clean deformation; triangulate only on export (or let the exporter do it). N-gons deform unpredictably and can triangulate badly.
2. Add edge loops where it bends (elbows, knees, mouth); keep flat areas sparse. Geometry is for silhouette and deformation, not flat surface detail.
3. Put surface detail in **normal maps baked from a high-poly**, not in extra polygons. A 2k-tri prop with a good normal map beats a 200k-tri one.
4. Match the budget to platform and distance: hero/first-person assets get more; background props get less and rely on LODs.

### 3. Baking High-to-Low
1. Sculpt or model the **high-poly**; build a clean **low-poly** target with good UVs.
2. Use a **cage** (or ray distance) so the projection captures detail without skewing at edges.
3. Bake **normal** (tangent-space for deforming meshes), **AO**, and optionally curvature/cavity into the low-poly's UV layout.
4. Verify the normal map's **green-channel direction** matches the target engine (OpenGL vs DirectX); flip green if normals read inverted in-engine.

### 4. Rigging & Skinning
1. Build the armature with **clean bone hierarchy and consistent names**; engines (and retarget tools, Unreal's IK Rig, Humanoid in Unity) map by name.
2. **Apply transforms** on both mesh and armature before binding. Bind with automatic weights as a start, then **weight-paint** problem joints (shoulders, hips) so no vertex is owned by the wrong bone.
3. Keep **influences per vertex** within the engine limit (commonly ≤4 or ≤8). More influences than the engine supports get silently clamped, breaking deformation.
4. Export the deform rig only — strip control bones / IK helpers, or mark them non-deforming, so the engine skeleton stays clean.

### 5. LODs & Collision Hulls
1. **LODs**: author or decimate a chain (LOD0 full → LOD1 ~50% → LOD2 ~25%…). Some engines auto-generate (Unreal), but hand-authored LODs preserve silhouette better on hero assets. Keep UVs/material slots consistent across levels.
2. **Collision**: never use the render mesh as a collider. Author a **separate, low-poly convex hull** (or a few primitives) and name it per the engine's convention (e.g. Unreal `UCX_<MeshName>`, or a child named `*-colonly`/`*-convcol` for Godot glTF). A complex concave render mesh as a collider tanks physics performance.

### 6. Export (glTF vs FBX)
1. **Prefer glTF 2.0 (`.glb`/`.gltf`)**: Open standard, Blender's first-class exporter. Best for Godot, web, modern engines, PBR materials. Prefer **`.glb` (binary glTF)** for game assets: single self-contained file, embedded textures optional, clean PBR.
2. **Use FBX**: Proprietary (Autodesk), via Blender's FBX addon. Use when Unreal/Unity studio pipelines mandate it. Material transfer is lossy; often re-author in-engine.
3. **Axis Conversion**: Blender is Z-up; most engines are Y-up. Use the exporter's axis conversion (glTF handles this; FBX needs the right preset) rather than rotating the mesh by hand.
4. **Selection**: Export selected, or use collections deliberately. Cameras, lights, and helper empties leak into the engine if exported.

## Pitfalls

1. **Unapplied scale/rotation**: the #1 export bug — child objects, normals, and physics behave wrong. `Ctrl+A` → Apply Rotation & Scale before every export.
2. **Wrong unit scale**: a character imports at 100× or 0.01× because Blender units weren't meters. Fix in Blender, not by scaling in-engine.
3. **Using the render mesh as collision**: enormous physics cost. Always author a separate hull.
4. **Detail in geometry instead of normal maps**: blows the poly budget for detail that a bake would carry for free.
5. **N-gons on deforming meshes**: unpredictable deformation and triangulation artifacts. Keep quads on anything that bends.
6. **Inverted normal maps in-engine**: green-channel convention mismatch (OpenGL vs DirectX). Bake or flip to the target.
7. **Too many bone influences**: exceeding the engine cap clamps weights and breaks deformation silently.
8. **Embedding huge textures in the .glb unnecessarily**: bloats the file; keep textures external when the engine manages them, or compress before embedding.
9. **Exporting the whole scene**: cameras, lights, and helper empties leak into the engine. Export selected, or use collections deliberately.

## Verification

- [ ] Rotation & Scale applied; scene units Metric at 1.0 (1 unit = 1 m).
- [ ] Object origins placed at the engine pivot point.
- [ ] Mesh is quad-dominant where it deforms; budget matches platform/distance.
- [ ] Normal/AO baked from high-poly; green channel matches the target engine.
- [ ] Armature bones named/hierarchied for engine retargeting; ≤ influence cap; weights painted on problem joints.
- [ ] LOD chain (if used) keeps consistent UVs/materials; collision authored as a separate hull with the engine's naming convention.
- [ ] Exported as `.glb` (or FBX per pipeline) with correct axis conversion; only the intended objects exported.
- [ ] Asset imports into the target engine at correct scale/orientation with working deformation.

## Related skills

- `assets-pipeline` - Godot-side import configuration of the files this skill exports.
- `3d-essentials` - In-engine materials, lighting, and PBR for the imported mesh.
- `unreal-engine` / `unity-engine` - Host engines that consume these glTF/FBX assets (Nanite, Humanoid rigs, LOD systems).
- `fmod-wwise-integration` - Unrelated audio pipeline, listed only to disambiguate "asset pipeline" overlap.
