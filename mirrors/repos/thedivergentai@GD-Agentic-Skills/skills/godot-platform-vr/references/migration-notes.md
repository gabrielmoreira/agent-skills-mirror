# Migration notes: godot-platform-vr

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 3.x → 4.0

Official: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html)

- Entire ARVR* → XR* rename set (auto in converter).
- `XRPositionalTracker` name/type getters renamed (`get_tracker_name`, …).
- Re-test OpenXR/WebXR interfaces on 4.0+; do not assume 3.x ARVRServer code paths.

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- `RenderingServer.global_shader_parameter_get_list()` returns `Array[StringName]`.
- `RenderingDevice.draw_list_begin()` `storage_textures` typed as `Array[RID]`.

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

- `XRInterface.environment_blend_mode` added (C#: `EnvironmentBlendModeEnum`) — update passthrough/mixed-reality samples.
- **Mesh format** upgrade — run Project → Tools → Upgrade Mesh Surfaces before shipping OpenXR builds.
- RenderingDevice `BarrierMask` enum values changed — rebuild custom RD/XR compositor extensions.

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- `WebXRInterface.get_input_source_tracker()` → `XRControllerTracker`; `XRServer.get_tracker()` → `XRTracker`.
- **Reverse Z** depth buffer — audit custom XR shaders and post effects comparing depth.
- Decal `modulate` now linear color space — retune passthrough UI overlays in world space.
- RenderingDevice barrier/draw_list APIs simplified (post_barrier params removed).

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- `RenderingDevice.draw_list_begin()` signature overhauled — update low-level XR render plugins.
- `Shader` default texture params use `Texture` / `TextureLayered`.
- `VisualShaderNodeVec4Constant` output type → Vector4 — recreate VR UI visual shaders.

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- `OpenXRExtensionWrapperExtension` → **`OpenXRExtensionWrapper`** in register APIs.
- OpenXR editor types moved to editor assembly — wrap C# tooling with `#if TOOLS`.
- GLTF/FBX **Naming Version** for non-joint skeleton nodes — reimport tracked avatars after upgrade.

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- `OpenXRExtensionWrapper` extension hooks gain `xr_version` parameter.
- `MeshInstance3D.skeleton` default empty `NodePath` — explicit skeleton paths in VR rig scenes.
- Glow default blend **Screen** + brighter volumetric fog — retune VR comfort brightness.
- New Windows projects default **D3D12** — validate OpenXR PC runtime on target GPUs.

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- `OpenXRExtensionWrapper._on_register_metadata()` gains `interaction_profile_metadata`.
- `OpenXRSpatialAnchorCapability.create_new_anchor()` optional `next` parameter.
- `Texture2D.get_format()` on base class — use when picking compression for stereo eye buffers.
- **AreaLight3D** preferred for soft rectangular lights; **HDR output** available on major HMD host platforms.
