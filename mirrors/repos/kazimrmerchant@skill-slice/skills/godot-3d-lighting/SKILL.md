---
name: godot-3d-lighting
description: "Expert patterns for Godot 3D lighting including DirectionalLight3D shadow cascades, OmniLight3D attenuation, SpotLight3D projectors, VoxelGI vs SDFGI, and LightmapGI baking. Use when implementing realistic 3D lighting, shadow optimization, global illumination, or light probes. Trigger keywords: DirectionalLight3D, OmniLight3D, SpotLight3D, shadow_enabled, directional_shadow_mode, directional_shadow_split, omni_range, omni_attenuation, spot_range, spot_angle, VoxelGI, SDFGI, LightmapGI, ReflectionProbe, Environment, WorldEnvironment. Never enable SDFGI on Mobile/Compatibility or LightmapGI for fully dynamic scenes; not a StandardMaterial3D PBR chair (godot-3d-materials)."
version: 1.0.1
---

## When to Use
Use this skill when implementing realistic 3D lighting, shadow optimization, global illumination, or light probes in Godot 4.x. 
Trigger keywords: `DirectionalLight3D`, `OmniLight3D`, `SpotLight3D`, `shadow_enabled`, `directional_shadow_mode`, `directional_shadow_split`, `omni_range`, `omni_attenuation`, `spot_range`, `spot_angle`, `VoxelGI`, `SDFGI`, `LightmapGI`, `ReflectionProbe`, `Environment`, `WorldEnvironment`.

## Prerequisites
- Godot 4.x (Forward+ renderer required for SDFGI and `AreaLight3D` features).
- Windows host (PowerShell) for local file operations if modifying scripts directly.

## Procedure

### 1. Load Required Scripts
**MANDATORY**: Read the appropriate script before implementing the corresponding pattern.
- `scripts/day_night_cycle.gd`: Dynamic sun position and color based on time-of-day. Load when building outdoor day/night systems.
- `scripts/light_probe_manager.gd`: VoxelGI and SDFGI management. Load when setting up global illumination.
- `scripts/lighting_manager.gd`: Dynamic light pooling and LOD. Load when optimizing performance with many lights.
- `scripts/volumetric_fx.gd`: Volumetric fog and god ray configuration. Load for atmospheric effects.
- `scripts/shadow_cascade_tuner.gd`: Adjusting DirectionalLight3D shadow split distances dynamically. Load for outdoor shadow optimization.
- `scripts/lightmap_bake_helper.gd`: Advanced LightmapGI configuration using Shadowmasking mode. Load for hybrid static/dynamic shadowing.
- `scripts/sdfgi_probe_manager.gd`: Dynamic quality scaler for real-time GI (SDFGI). Load when adjusting cell size and occlusion for performance/quality trade-offs.
- `scripts/volumetric_fog_zones.gd`: Smoothly transitioning localized fog density. Load for cave entrances or forest clearings using Tweens and Area3D triggers.
- `scripts/fake_gi_bounce.gd`: Efficient 'Mobile-GI' pattern. Load when simulating light bouncing off the floor for lower-end platforms.
- `scripts/environment_blender.gd`: Transitioning WorldEnvironment parameters. Load for gameplay-based Sky, Ambient, and Tonemap transitions.
- `scripts/shadow_bias_tuner.gd`: Correcting 'Peter Panning' and 'Shadow Acne'. Load for high-fidelity directional light optimization.
- `scripts/light_lod_optimizer.gd`: Distance-based shadow and visibility culling. Load for dense OmniLight3D environments.
- `scripts/reflection_probe_manager.gd`: Performance-aware ReflectionProbe handling. Load for large environmental changes using manual 'Update Once' triggers.
- `scripts/spotlight_projector_setup.gd`: High-detail lighting using Projector textures. Load to fake complex shadow patterns (grates, glass ripples).

### 2. DirectionalLight3D (Sun/Moon) & Shadow Cascades
For outdoor scenes, use parallel 4-split shadow cascades for better quality at distance.

```gdscript
extends DirectionalLight3D

func _ready() -> void:
    shadow_enabled = true
    directional_shadow_mode = SHADOW_PARALLEL_4_SPLITS
    
    # Split distances (in meters from camera)
    directional_shadow_split_1 = 10.0   # First cascade: 0-10m
    directional_shadow_split_2 = 50.0   # Second: 10-50m
    directional_shadow_split_3 = 200.0  # Third: 50-200m
    # Fourth cascade: 200m - max shadow distance
    
    directional_shadow_max_distance = 500.0
    directional_shadow_blend_splits = true  # Smooth transitions
```

### 3. OmniLight3D (Point Light) Attenuation
Keep `omni_range` as small as visually acceptable. Light attenuation is quadratic.

```gdscript
extends OmniLight3D

func _ready() -> void:
    omni_range = 10.0  # Maximum reach
    omni_attenuation = 2.0  # Falloff curve (1.0 = linear, 2.0 = quadratic/realistic)
    
    # For "magical" lights, reduce attenuation
    # omni_attenuation = 0.5  # Flatter falloff, reaches farther
```

### 4. SpotLight3D (Flashlight/Headlights) & Projectors
Use projector textures (cookies/gobos) to fake complex shadow patterns.

```gdscript
extends SpotLight3D

func _ready() -> void:
    spot_range = 20.0
    spot_angle = 45.0  # Cone angle (degrees)
    spot_angle_attenuation = 2.0  # Edge softness
    shadow_enabled = true
    
    # Projector texture (optional)
    light_projector = load("res://textures/flashlight_mask.png")
```

### 5. Global Illumination: VoxelGI vs SDFGI
- **VoxelGI**: Use for indoor, small-medium scenes. Place one per room/area and tightly fit the `size`.
- **SDFGI**: Use for large outdoor scenes. Enable via `WorldEnvironment`. Forward+ exclusive.

```gdscript
# VoxelGI Setup
extends VoxelGI

func _ready() -> void:
    size = Vector3(20, 10, 20) # Tightly fit the room
    subdiv = VoxelGI.SUBDIV_128
    bake()
```

```gdscript
# SDFGI Setup
extends WorldEnvironment

func _ready() -> void:
    var env := environment
    env.sdfgi_enabled = true
    env.sdfgi_use_occlusion = true
    env.sdfgi_read_sky_light = true
    env.sdfgi_min_cell_size = 0.2
    env.sdfgi_max_distance = 200.0
```

### 6. LightmapGI (Baked Static Lighting)
Use for static architecture (buildings, dungeons) or mobile/low-end targets. 
Bake in the editor (not runtime). Use Shadowmasking mode for hybrid static/dynamic shadowing.

```gdscript
extends LightmapGI

func _ready() -> void:
    quality = LightmapGI.BAKE_QUALITY_HIGH
    bounces = 3  # Indirect light bounces
```

### 7. Environment, Sky & Volumetric Fog
Configure HDR skybox and volumetric fog via `WorldEnvironment`.

```gdscript
extends WorldEnvironment

func _ready() -> void:
    var env := environment
    env.background_mode = Environment.BG_SKY
    var sky := Sky.new()
    var sky_material := PanoramaSkyMaterial.new()
    sky_material.panorama = load("res://hdri/sky.hdr")
    sky.sky_material = sky_material
    env.sky = sky
    
    env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
    env.ambient_light_sky_contribution = 1.0
    
    env.volumetric_fog_enabled = true
    env.volumetric_fog_density = 0.01
    env.volumetric_fog_albedo = Color(0.9, 0.9, 1.0)
```

### 8. ReflectionProbe
Use for localized reflections (mirrors, shiny floors). Keep on `UPDATE_ONCE` for performance.

```gdscript
extends ReflectionProbe

func _ready() -> void:
    size = Vector3(10, 5, 10)
    resolution = ReflectionProbe.RESOLUTION_512
    update_mode = ReflectionProbe.UPDATE_ONCE
```

### 9. Performance Optimization & Light Budgets
- DirectionalLight3D with shadows: 1-2
- OmniLight3D with shadows: 3-5
- SpotLight3D with shadows: 2-4
- OmniLight3D without shadows: 20-30
- SpotLight3D without shadows: 15-20

Disable shadows for distant lights dynamically:
```gdscript
extends OmniLight3D

@export var shadow_max_distance := 50.0

func _process(delta: float) -> void:
    var camera := get_viewport().get_camera_3d()
    if camera:
        var dist := global_position.distance_to(camera.global_position)
        shadow_enabled = (dist < shadow_max_distance)
```

### 10. Expert Techniques
- **Fake Global Illumination**: Duplicate main `DirectionalLight3D`, rotate 180° (pointing up), Shadows OFF, Specular 0.0, Energy 10-40%.
- **Simulating PCSS (Contact-Hardening Shadows)**: Use `light_size` on `OmniLight3D` (high performance cost, keep low). Use `distance_fade_enabled` to cull when out of range.
- **Light-Volume-Trigger**: Use `Area3D` triggers and `Tween`-driven `Camera3D` overrides to smoothly transition between lighting environments.
- **Lighting-Quality-Settings**: Manage complex lighting features at runtime using the `RenderingServer` API for direct engine control (e.g., `gi_set_use_half_resolution(true)`).

## Pitfalls
- **NEVER use VoxelGI without setting a proper extents** — Unbound VoxelGI tanks performance. Always set `size` to tightly fit your scene.
- **NEVER enable shadows on every light** — Each shadow-casting light is expensive. Use shadows sparingly: 1-2 DirectionalLights, ~3-5 OmniLights max.
- **NEVER forget directional_shadow_mode** — Default is ORTHOGONAL. For large outdoor scenes, use PARALLEL_4_SPLITS for better shadow quality at distance.
- **NEVER use LightmapGI for fully dynamic scenes** — Lightmaps are baked. Moving geometry won't receive updated lighting. Use VoxelGI or SDFGI instead.
- **NEVER set omni_range too large** — Light attenuation is quadratic. A range of 500 affects 785,000 sq units. Keep range as small as visually acceptable.
- **NEVER hide a Light node using the Visible property to exclude it from a Lightmap bake** — Hiding a light has no effect on the baker. You must change the light's Bake Mode to Disabled.
- **NEVER use VoxelGI with paper-thin walls** — VoxelGI evaluates lighting using a 3D grid. Thin walls (less than one voxel thick) will cause severe light leaking. Seal your geometry or place hidden thick MeshInstance3D blocks around the exterior.
- **NEVER leave shadow bias at default for cascades** — Default bias often causes Peter Panning or light leaking at split transitions. Tune bias per-light based on your scene's scale.
- **NEVER bake LightmapGI without a Denoiser** — Godot's baked lightmaps are noisy by default. Use OIDN or JNLM (in Project Settings) for professional results.
- **NEVER use real-time SDFGI on Mobile/Compatibility renderers** — It is a Forward+ exclusive feature. Use fake GI bounce lights for lower-end platforms.
- **NEVER use 'Update Continuity' in ReflectionProbes for performance** — Keep ReflectionProbes on 'Update Once' and trigger manual updates only when necessary.
- **NEVER use emissive-only fake panels when AreaLight3D gives correct falloff and shadow softness in Forward+**.

## Verification
1. **Check Light Budgets**: Ensure shadow-casting lights do not exceed recommended limits (1-2 Directional, 3-5 Omni, 2-4 Spot).
2. **Verify Shadow Cascades**: In Godot Editor, visually inspect shadow transitions at split distances (10m, 50m, 200m). Ensure no Peter Panning or light leaking at split transitions.
3. **Check VoxelGI Extents**: Ensure `size` tightly fits the room and no unbound VoxelGI nodes exist.
4. **Verify LightmapGI Bake Mode**: Ensure lights meant to be excluded from bake have Bake Mode set to Disabled, not just hidden via the Visible property.
5. **Verify SDFGI Renderer**: Confirm project is using Forward+ renderer if SDFGI is enabled.

## Related skills
- Master Skill: [godot-master](../godot-master/SKILL.md)
