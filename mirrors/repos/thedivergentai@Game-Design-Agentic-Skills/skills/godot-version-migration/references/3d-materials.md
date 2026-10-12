# Migration notes: godot-3d-materials

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 3.x → 4.0

Official: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html)

- `SpatialMaterial` → `StandardMaterial3D`.
- `StreamTexture` → `CompressedTexture2D` (reimport).
- ArrayMesh `.res` from 3.x incompatible — reimport source meshes.
- ShaderMaterial: apply shader foundation 3→4 notes.

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- `RenderingServer.global_shader_parameter_get_list` / RD shader version lists return `Array[StringName]`.
- `RenderingDevice.draw_list_begin` storage_textures typed as `Array[RID]`.

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

- **Mesh format** upgrade — use Project → Tools → Upgrade Mesh Surfaces; Restart & Upgrade prevents downgrade (material slots may remap after upgrade).
- ImporterMesh/MeshDataTool/SurfaceTool compression flag widths → `uint64`.
- RenderingDevice BarrierMask enum values changed.

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- **Reverse Z** depth — update spatial/custom shaders on StandardMaterial3D overrides and depth-based effects.
- Decal modulate converted sRGB→linear — emissive/decal material tints shift; rebalance albedo/emission pairs.
- RenderingDevice barrier/draw_list API simplified (post_barrier params removed).

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- `RenderingDevice.draw_list_begin` signature overhauled (params removed + breadcrumb).
- `Shader` default texture parameter types use `Texture` / `TextureLayered`.
- `VisualShaderNodeVec4Constant` input type → Vector4 — recreate material graph constants.
- VisualShader cubemap / Texture2DArray nodes use `TextureLayered`.
- CSG uses Manifold — **non-manifold** CSG booleans fail; use MeshInstance3D materials on imported meshes for planes/quads.

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- `RenderingServer.instance_reset_physics_interpolation` / `instance_set_interpolated` removed.
- GLTF/BLEND/FBX naming version for non-joint nodes in skeletons — set Import dock Naming Version for old PBR assets.

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- Glow default blend **Screen** (brighter) — retune emissive materials against new default bloom.
- Volumetric fog blending brighter — reduce fog density when pairing with transparent/transmission materials.
- Sky reflection roughness_layers default 7 (was 8) — affects environment-reflection roughness on PBR materials.

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- `Texture2D.get_format()` unified on base class — use when branching shader logic on compressed vs HDR formats.
- `LinearToSRGB` visual shader no longer clamps `[0,1]` on Mobile/Forward+ — rebalance emissive VisualShader graphs.
- `Image.save_exr*` gain color_image / max_linear_value optionals for HDR texture export pipelines.
