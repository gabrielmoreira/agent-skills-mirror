# Migration notes: godot-3d-lighting

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 3.x → 4.0

Official: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html)

- `GIProbe` → `VoxelGI`; `BakedLightmap` → `LightmapGI` (re-bake).
- `PanoramaSky`/`ProceduralSky` → `Sky`.
- `SpatialMaterial` → `StandardMaterial3D`.
- Environment effect quality → project settings; keep visual toggles on Environment.

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- `RenderingServer.global_shader_parameter_get_list` / RD shader version lists return `Array[StringName]`.
- `RenderingDevice.draw_list_begin` storage_textures typed as `Array[RID]`.
- `Node3D.look_at` / `look_at_from_position` gain `use_model_front` — retarget spot/area light rigs that used `-Z` forward assumptions.

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

- **Mesh format** upgrade — use Project → Tools → Upgrade Mesh Surfaces; Restart & Upgrade prevents downgrade (re-import meshes that receive baked lighting).
- ImporterMesh/MeshDataTool/SurfaceTool compression flag widths → `uint64`.
- RenderingDevice BarrierMask enum values changed.

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- **Reverse Z** depth — update custom lighting/shadow shaders and depth-based effects (see Introducing Reverse Z article).
- Decal modulate converted sRGB→linear — retune projector/decal tints in lit scenes.
- RenderingDevice barrier/draw_list API simplified (post_barrier params removed).

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- `RenderingDevice.draw_list_begin` signature overhauled (params removed + breadcrumb).
- `Shader` default texture parameter types use `Texture` / `TextureLayered` — affects light cookie and IES texture slots.

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- `RenderingServer.instance_reset_physics_interpolation` / `instance_set_interpolated` removed.

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- Glow default blend **Screen** (brighter) — retune Environment glow; Mobile glow rewrite looks different.
- Volumetric fog blending brighter — reduce density/energy in fog-heavy lighting setups.
- New Windows projects default **D3D12** driver — verify Forward+/Mobile lighting parity after backend change.
- Sky reflection roughness_layers default 7 (was 8).

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- Prefer **AreaLight3D** for rectangular soft lights — correct falloff and shadow softness vs emissive-material workarounds.
- **HDR output** supported on major platforms — enable in Project Settings → Rendering → Viewport for a true HDR display chain.
- `Texture2D.get_format()` unified on base class (ImageTexture/PortableCompressedTexture2D).
- `LinearToSRGB` visual shader no longer clamps `[0,1]` on Mobile/Forward+ — rebalance tonemapped emissive looks.
- `Image.save_exr*` gain color_image / max_linear_value optionals for HDR light-map export.
- **NEVER** rely on emissive-only panels when AreaLight3D gives physically correct rectangular lighting in Forward+.
