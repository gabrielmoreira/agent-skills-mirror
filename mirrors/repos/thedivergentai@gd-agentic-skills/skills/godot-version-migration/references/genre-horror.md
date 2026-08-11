# Migration notes: godot-genre-horror

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- `RenderingServer.global_shader_parameter_get_list` / RD shader version lists return `Array[StringName]`.
- `RenderingDevice.draw_list_begin` storage_textures typed as `Array[RID]`.

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

- **Mesh format** upgrade — use Project → Tools → Upgrade Mesh Surfaces; Restart & Upgrade prevents downgrade.
- ImporterMesh/MeshDataTool/SurfaceTool compression flag widths → `uint64`.
- RenderingDevice BarrierMask enum values changed.

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- If the genre uses TileMap, migrate to `TileMapLayer` nodes before relying on layer APIs.
- If the genre ships multiplayer, upgrade all peers to 4.3 together (`SceneMultiplayer` protocol).
- **Reverse Z** depth — update custom horror shaders (fog volumes, flashlight cones, post stacks).
- Decal modulate converted sRGB→linear — blood decals and grime overlays may look darker.
- `AudioStreamPlaybackPolyphonic.play_stream` gains `playback_type` and `bus` optionals.
- RenderingDevice barrier/draw_list API simplified (post_barrier params removed).

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- `RenderingDevice.draw_list_begin` signature overhauled (params removed + breadcrumb).
- `Shader` default texture parameter types use `Texture` / `TextureLayered`.
- `VisualShaderNodeVec4Constant` input type → Vector4 — recreate constants in flashlight/flicker graphs.

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- `RenderingServer.instance_reset_physics_interpolation` / `instance_set_interpolated` removed — retune camera/light flicker that relied on manual interpolation resets.

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- Retune Environment glow/fog if the genre leans on bloom-heavy looks.
- Glow default blend **Screen** (brighter) — retune Environment glow; Mobile glow rewrite looks different.
- Volumetric fog blending brighter — reduce density/energy in haunted corridors.
- New Windows projects default **D3D12** driver.
- Sky reflection `roughness_layers` default 7 (was 8).

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- Confirm project stretch mode and `AudioStreamPlayer.area_mask` after opening in 4.7.
- `AudioStreamPlayer.area_mask` default is **0** (disabled), was layer 1 — set mask explicitly for zone-attached ambience and stingers.
- `AudioEffectSpectrumAnalyzer.tap_back_pos` **removed** — migrate tension visualizers tied to spectrum analysis.
- Prefer **AreaLight3D** for flickering panels, TV glow, and rectangular soft shadows without GI hacks.
- `Texture2D.get_format()` unified on base class — use when tuning compressed horror texture pipelines.
- `LinearToSRGB` visual shader no longer clamps `[0,1]` on Mobile/Forward+ — recheck crushed shadow grades.
