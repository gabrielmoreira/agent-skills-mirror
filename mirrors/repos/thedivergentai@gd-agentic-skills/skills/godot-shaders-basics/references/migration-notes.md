# Migration notes: godot-shaders-basics

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 3.x → 4.0

Official: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html)

- Rename `.shader` → `.gdshader`; update references.
- `hint_albedo`/`hint_color` → `source_color`; filter/repeat on uniforms.
- Particles shaders: `start()`/`process()` instead of `vertex()`.
- Custom `light()` and matrix builtins changed — visual QA required.

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- `RenderingServer.global_shader_parameter_get_list` / RD shader version lists return `Array[StringName]`.
- `RenderingDevice.draw_list_begin` storage_textures typed as `Array[RID]`.

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

- **Mesh format** upgrade — re-test shader variants on upgraded mesh surfaces.
- RenderingDevice BarrierMask enum values changed.

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- **Reverse Z** depth — custom spatial shaders comparing depth or using `POSITION.z` may break; migrate depth sampling.
- Decal modulate converted sRGB→linear — shader/decal color inputs shift.
- RenderingDevice barrier/draw_list API simplified (post_barrier params removed).

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- `RenderingDevice.draw_list_begin` signature overhauled (params removed + breadcrumb).
- `Shader` default texture parameter types use `Texture` / `TextureLayered`.
- VisualShader cubemap / Texture2DArray nodes use `TextureLayered`.
- `VisualShaderNodeVec4Constant` input type → Vector4 — recreate constant nodes.

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- `RenderingServer.instance_reset_physics_interpolation` / `instance_set_interpolated` removed.

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- Glow default blend **Screen** (brighter) — shader output may look hotter against default bloom.
- Sky reflection roughness_layers default 7 (was 8).

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- `LinearToSRGB` visual shader no longer clamps `[0,1]` on Mobile/Forward+.
- `Texture2D.get_format()` unified on base class — branch format-specific shader paths on the base API.
- `Image.save_exr*` gain color_image / max_linear_value optionals.
