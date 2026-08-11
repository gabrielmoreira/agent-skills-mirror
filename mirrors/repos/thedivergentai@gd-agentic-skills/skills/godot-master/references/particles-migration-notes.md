# Migration notes: godot-particles

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 3.x → 4.0

Official: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html)

- `Particles`/`Particles2D` → `GPUParticles3D`/`GPUParticles2D`.
- `ParticlesMaterial` → `ParticleProcessMaterial`; `set_flag` → `set_particle_flag`.
- CPU particle flag enums renamed (`PARTICLE_FLAG_*`).
- Re-author process material curves after convert.

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- `RenderingServer.global_shader_parameter_get_list` / RD shader version lists return `Array[StringName]`.
- `RenderingDevice.draw_list_begin` storage_textures typed as `Array[RID]`.

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

- **Mesh format upgrade** — run Project → Tools → Upgrade Mesh Surfaces before GPU particle meshes rely on legacy `.mesh` data.
- ImporterMesh/MeshDataTool/SurfaceTool compression flag widths → `uint64`.
- `RenderingDevice` BarrierMask enum values changed — update custom GPU particle compute barriers.

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- **Reverse Z** depth — update custom particle shaders comparing depth or using `POSITION.z`.
- Decal `modulate` converted sRGB→linear — attached particle decal tints look different; rebalance color values.
- `RenderingDevice` draw_list barrier API simplified (post_barrier params removed).
- **GPUParticles2D** stutter when parented to fast physics bodies — prefer `CPUParticles2D` with `fract_delta = true` for high-speed 2D trails (behavioral; not an API rename).

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- `CPUParticles2D/3D` and `GPUParticles2D/3D.restart()` gain optional **`keep_seed`** — use for deterministic one-shot burst replay in VFX tests.
- `RenderingDevice.draw_list_begin` signature overhauled — update custom GPU particle draw helpers.
- `Shader` default texture parameter types use `Texture` / `TextureLayered`.
- `VisualShaderNodeVec4Constant` input type → Vector4 — recreate vec4 constants in visual particle graphs.

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- `RenderingServer.instance_reset_physics_interpolation` / `instance_set_interpolated` removed — drop physics-interpolation toggles on particle mesh instances.

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- Environment glow default blend mode **`Screen`** (brighter) — retune `Environment.glow_*` when particle bloom looks blown out.
- Volumetric fog default blending brighter — reduce fog density/energy behind particle-heavy scenes.
- New Windows projects default **D3D12** driver — re-test GPU particles if switching render backends.
- Sky `reflection roughness_layers` default 7 (was 8) — may shift lit particle specular in outdoor scenes.

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- `request_particles_process` / `particles_request_process_time` gain `process_time_residual` — use when syncing one-shot bursts to gameplay clocks.
- `Texture2D.get_format()` unified on base class — branch import/shader paths on format without casting to `ImageTexture`.
- `LinearToSRGB` visual shader no longer clamps `[0,1]` on Mobile/Forward+ — HDR particle trails may need manual clamp in shader.
