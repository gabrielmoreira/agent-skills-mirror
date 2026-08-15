---
name: godot-3d-materials
description: "Expert patterns for Godot 3D PBR materials using StandardMaterial3D including albedo, metallic/roughness workflows, normal maps, ORM texture packing, transparency modes, and shader conversion. Use when creating realistic 3D surfaces, PBR workflows, or material optimization. Trigger keywords: StandardMaterial3D, BaseMaterial3D, albedo_texture, metallic, metallic_texture, roughness, roughness_texture, normal_texture, normal_enabled, orm_texture, transparency, alpha_scissor, alpha_hash, cull_mode, ShaderMaterial, shader parameters. Not a DirectionalLight3D/VoxelGI/SDFGI chair (godot-3d-lighting). Do not use TRANSPARENCY_ALPHA for cutouts or metallic=0.5 on dielectrics."
version: 1.0.1
---

# 3D Materials

Expert guidance for PBR materials and StandardMaterial3D in Godot 4.x (4.7-aware). Covers PBR texture setup, metallic/roughness workflows, transparency modes, ORM channel packing, shader conversion, and performance optimization for TBS and general 3D game projects.

## When to Use

- Creating or configuring 3D PBR materials in Godot (StandardMaterial3D, BaseMaterial3D).
- Setting up albedo, normal, metallic, roughness, AO, ORM, emission, rim, clearcoat, or anisotropy.
- Choosing transparency modes (alpha scissor, alpha hash, alpha blend).
- Optimizing material batching, draw calls, LOD/HLOD, or instance uniforms.
- Converting StandardMaterial3D to ShaderMaterial or writing spatial shaders.
- Fixing Z-fighting, texture seams, flat-looking materials, or normal map silent failures.

Trigger keywords: `StandardMaterial3D`, `BaseMaterial3D`, `albedo_texture`, `metallic`, `metallic_texture`, `roughness`, `roughness_texture`, `normal_texture`, `normal_enabled`, `orm_texture`, `transparency`, `alpha_scissor`, `alpha_hash`, `cull_mode`, `ShaderMaterial`, `shader parameters`.

## Prerequisites

- Godot 4.x project (4.7 features referenced where available).
- Textures imported with correct type (e.g., Normal Map = true for normal textures).
- For HDR emission: HDR rendering enabled in Project Settings.
- Windows host primary (PowerShell). Paths use `res://` in GDScript; filesystem paths use backslashes on Windows.

## NEVER Do (Hard Rules)

- **NEVER use separate metallic/roughness/AO textures** — Use ORM packing (1 RGB texture with Occlusion/Roughness/Metallic channels) to save texture slots and memory.
- **NEVER forget to enable `normal_enabled`** — Normal maps don't work unless you set `normal_enabled = true`. Silent failure is common.
- **NEVER use `TRANSPARENCY_ALPHA` for cutout materials** — Use `TRANSPARENCY_ALPHA_SCISSOR` or `TRANSPARENCY_ALPHA_HASH` instead. Full alpha blending is expensive and causes sorting issues.
- **NEVER set `metallic = 0.5`** — Materials are either metallic (1.0) or dielectric (0.0). Values between are physically incorrect except for rust/dirt transitions.
- **NEVER use emission without HDR** — Emission values > 1.0 only work with HDR rendering enabled in Project Settings.
- **NEVER use transparent materials for large environmental surfaces** — Transparent objects cannot rely on the Z-buffer for early fragment rejection, resulting in massive overdraw. If only a tiny part of a mesh is transparent, split the mesh into two surfaces: one opaque, one transparent.
- **NEVER create hundreds of slightly varied StandardMaterial3D resources if performance is dropping** — Godot minimizes GPU state changes by automatically reusing the underlying shader for materials that share the exact same configuration flags (checkboxes). Try to group your material configurations.
- **NEVER attempt to fix Z-fighting strictly by moving objects further apart** — Floating-point precision degrades over distance. To fix flickering textures, increase your Camera3D's `Near` plane property and decrease the `Far` property to compress the precision range.
- **NEVER use unique Material resources per MeshInstance3D** — This breaks draw call batching. Use 'Instance Uniforms' to vary parameters while keeping a single shared material.
- **NEVER use Decals on dynamic moving actors without a Cull Mask** — Bullet holes should not stick to the player's face as they walk over them. Mask out character layers.

## Godot 4.7: Materials

- **AreaLight3D** pairs with emissive materials for physically correct rectangular emitters.
- `Texture2D.get_format()` unified on base class for portable compressed textures.

## Available Scripts

> **MANDATORY**: Read the appropriate script before implementing the corresponding pattern. Load from `scripts/` relative to this skill folder.

| Script | When to Load |
|--------|-------------|
| `scripts/material_fx.gd` | Runtime material property animation for damage effects, dissolve, and texture swapping. Load before implementing dynamic material state changes. |
| `scripts/pbr_material_builder.gd` | Runtime PBR material creation with ORM textures and triplanar mapping. Load before building PBR materials at runtime. |
| `scripts/organic_material.gd` | Subsurface scattering and rim lighting for organic surfaces (skin, leaves). Load before creating character or vegetation materials. |
| `scripts/triplanar_world.gdshader` | Triplanar projection for terrain without UV mapping. Load for cliffs, caves, or procedural terrain. |
| `scripts/pbr_orm_packer.gd` | Packs AO, Roughness, and Metallic into a single ORM texture. Load before optimizing VRAM and draw calls. |
| `scripts/vertex_wind_sway.gdshader` | GPU-driven foliage animation using vertex world coordinates and vertex color weight painting. Load for foliage without skeletons. |
| `scripts/triplanar_world_projection.gdshader` | UV-less environment mapping projecting textures along X/Y/Z axes. Load for organic blending over complex rocks and terrain. |
| `scripts/subsurface_scattering_setup.gd` | Configuring realistic organic materials: Skin Mode, Transmittance, depth scattering for Forward+. Load before setting up SSS. |
| `scripts/instance_uniform_batching.gdshader` | Architecture pattern for high-speed batching of 10,000 meshes sharing one material with unique instance uniforms. Load before implementing instance variation. |
| `scripts/decal_placer_expert.gd` | Dynamic 3D decal system with cull masking and life-cycle management. Load before placing impact decals. |
| `scripts/transparency_sorting_fix.gd` | Solving visual artifacts using Alpha Hash and Depth Prepass. Load before fixing transparency sorting. |
| `scripts/shader_state_manager.gd` | Toggling shader-based visual states (Frozen, Burned) on multiple entities. Load before implementing state toggling. |
| `scripts/depth_precision_fix.gd` | Camera-side fix for Z-fighting and texture flickering in large-scale worlds. Load before fixing depth precision. |
| `scripts/material_batcher.gd` | Global override system to ensure environmental meshes draw in optimized, state-locked batches. Load before implementing global batching. |

## Procedure

### 1. PBR Texture Setup (StandardMaterial3D)

```gdscript
# Create physically-based material
var mat := StandardMaterial3D.new()

# Albedo (base color)
mat.albedo_texture = load("res://textures/wood_albedo.png")
mat.albedo_color = Color.WHITE  # Tint multiplier

# Normal map (surface detail)
mat.normal_enabled = true  # CRITICAL: Must enable first
mat.normal_texture = load("res://textures/wood_normal.png")
mat.normal_scale = 1.0  # Bump strength

# ORM Texture (R=Occlusion, G=Roughness, B=Metallic)
mat.orm_texture = load("res://textures/wood_orm.png")

# Alternative: Separate textures (less efficient — avoid)
# mat.roughness_texture = load("res://textures/wood_roughness.png")
# mat.metallic_texture = load("res://textures/wood_metallic.png")
# mat.ao_texture = load("res://textures/wood_ao.png")

# Apply to mesh
$MeshInstance3D.material_override = mat
```

### 2. Metallic vs Roughness Workflows

**Metal Workflow:**
```gdscript
# Pure metal (steel, gold, copper)
mat.metallic = 1.0
mat.roughness = 0.2  # Polished metal
mat.albedo_color = Color(0.8, 0.8, 0.8)  # Metal tint

# Rough metal (iron, aluminum)
mat.metallic = 1.0
mat.roughness = 0.7
```

**Dielectric Workflow:**
```gdscript
# Non-metal (wood, plastic, stone)
mat.metallic = 0.0
mat.roughness = 0.6  # Typical for wood
mat.albedo_color = Color(0.6, 0.4, 0.2)  # Brown wood

# Glossy plastic
mat.metallic = 0.0
mat.roughness = 0.1  # Very smooth
```

**Transition Materials (Rust/Dirt):**
```gdscript
# Use texture to blend metal/non-metal
mat.metallic_texture = load("res://rust_mask.png")
# White areas (1.0) = metal
# Black areas (0.0) = rust (dielectric)
```

### 3. Transparency Modes

| Mode | Use Case | Performance | Sorting Issues |
|------|----------|-------------|---------------|
| `ALPHA_SCISSOR` | Foliage, chain-link fence | Fast | No |
| `ALPHA_HASH` | Dithered fade, LOD transitions | Fast | Noisy |
| `ALPHA` | Glass, water, godot-particles | Slow | Yes (render order) |

**Alpha Scissor (Cutout):**
```gdscript
mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
mat.alpha_scissor_threshold = 0.5  # Pixels < 0.5 alpha = discarded
mat.albedo_texture = load("res://leaf.png")  # Must have alpha channel
mat.cull_mode = BaseMaterial3D.CULL_BACK
```

**Alpha Hash (Dithered):**
```gdscript
mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_HASH
mat.alpha_hash_scale = 1.0  # Dither pattern scale

# Animate fade
var tween := create_tween()
tween.tween_property(mat, "albedo_color:a", 0.0, 1.0)
```

**Alpha Blend (Full Transparency):**
```gdscript
mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
mat.blend_mode = BaseMaterial3D.BLEND_MODE_MIX
mat.depth_draw_mode = BaseMaterial3D.DEPTH_DRAW_DISABLED
mat.cull_mode = BaseMaterial3D.CULL_DISABLED  # Show both sides
```

### 4. Advanced Features

**Emission (Glowing Materials):**
```gdscript
mat.emission_enabled = true
mat.emission = Color(1.0, 0.5, 0.0)  # Orange glow
mat.emission_energy_multiplier = 2.0  # Brightness (HDR)
mat.emission_texture = load("res://lava_emission.png")

# Animated emission
func _process(delta: float) -> void:
    mat.emission_energy_multiplier = 1.0 + sin(Time.get_ticks_msec() * 0.005) * 0.5
```

**Rim Lighting (Fresnel):**
```gdscript
mat.rim_enabled = true
mat.rim = 1.0  # Intensity
mat.rim_tint = 0.5  # How much albedo affects rim color
```

**Clearcoat (Car Paint):**
```gdscript
mat.clearcoat_enabled = true
mat.clearcoat = 1.0
mat.clearcoat_roughness = 0.1
```

**Anisotropy (Brushed Metal):**
```gdscript
mat.anisotropy_enabled = true
mat.anisotropy = 1.0
mat.anisotropy_flowmap = load("res://brushed_flow.png")
```

### 5. Texture Channel Packing (ORM)

**ORM Texture (Recommended):**
```python
# External tool (GIMP, Substance, Python script):
# Combine 3 grayscale textures into 1 RGB:
# R channel = Ambient Occlusion (bright = no occlusion)
# G channel = Roughness (bright = rough)
# B channel = Metallic (bright = metal)
```

```gdscript
# In Godot:
mat.orm_texture = load("res://textures/material_orm.png")
# This replaces ao_texture, roughness_texture, and metallic_texture!
```

**Custom Packing:**
```gdscript
mat.roughness_texture_channel = BaseMaterial3D.TEXTURE_CHANNEL_GREEN
mat.metallic_texture_channel = BaseMaterial3D.TEXTURE_CHANNEL_BLUE
```

### 6. Shader Conversion (StandardMaterial3D → ShaderMaterial)

When to convert: need custom effects (dissolve, vertex displacement), StandardMaterial3D limitations hit, or shader optimizations (remove unused features).

```gdscript
# 1. Create StandardMaterial3D with all settings
var std_mat := StandardMaterial3D.new()
std_mat.albedo_color = Color.RED
std_mat.metallic = 1.0
std_mat.roughness = 0.2

# 2. Convert to ShaderMaterial
var shader_mat := ShaderMaterial.new()
shader_mat.shader = load("res://custom_shader.gdshader")

# 3. Transfer parameters manually
shader_mat.set_shader_parameter("albedo", std_mat.albedo_color)
shader_mat.set_shader_parameter("metallic", std_mat.metallic)
shader_mat.set_shader_parameter("roughness", std_mat.roughness)
```

### 7. Material Variants (Godot 4.0+)

```gdscript
# Base material (shared)
var base_red_metal := StandardMaterial3D.new()
base_red_metal.albedo_color = Color.RED
base_red_metal.metallic = 1.0

# Variant 1: Rough
var rough_variant := base_red_metal.duplicate()
rough_variant.roughness = 0.8

# Variant 2: Smooth
var smooth_variant := base_red_metal.duplicate()
smooth_variant.roughness = 0.1

# Note: Use resource_local_to_scene for per-instance tweaks
```

### 8. Performance Optimization

**Material Batching:**
```gdscript
# GOOD: Reuse materials across meshes
const SHARED_STONE := preload("res://materials/stone.tres")

func _ready() -> void:
    for wall in get_tree().get_nodes_in_group("stone_walls"):
        wall.material_override = SHARED_STONE
    # All walls batched in single draw call

# BAD: Unique material per mesh
func _ready() -> void:
    for wall in get_tree().get_nodes_in_group("stone_walls"):
        var mat := StandardMaterial3D.new()  # New material!
        mat.albedo_color = Color(0.5, 0.5, 0.5)
        wall.material_override = mat
    # Each wall is separate draw call
```

**Texture Atlasing:**
```gdscript
extends StandardMaterial3D

func set_atlas_region(tile_x: int, tile_y: int, tiles_per_row: int) -> void:
    var tile_size := 1.0 / tiles_per_row
    uv1_offset = Vector3(tile_x * tile_size, tile_y * tile_size, 0)
    uv1_scale = Vector3(tile_size, tile_size, 1)
```

### 9. Expert Techniques

**LOD Transitions using Pixel Dither:**
When using HLOD or Visibility Ranges to fade objects at distance, standard alpha blending causes severe performance hits. Configure Distance Fade mode to `DISTANCE_FADE_PIXEL_DITHER` for smooth fade within the opaque pipeline.

**Stencil Buffers (Godot 4.5+):**
Use Stencil Buffer directly in StandardMaterial3D for outlines or X-ray effects behind walls without custom shaders.

**AR Shadow Overlay Shader:**
```glsl
shader_type spatial;
// shadow_to_opacity makes the material invisible when lit,
// but opaque (dark) when it receives a shadow.
render_mode blend_mix, depth_draw_opaque, cull_back, shadow_to_opacity;

void fragment() {
    ALBEDO = vec3(0.0, 0.0, 0.0);
}
```

### 10. Expert Pattern: Material-Texture-Array (Instanced Variation)

Render hundreds of varied objects in a single draw call using Instance Uniforms with a texture array.

```glsl
shader_type spatial;

uniform sampler2D texture_array[4];
instance uniform int texture_index;

void fragment() {
    vec4 tex_color;
    switch (texture_index) {
        case 0: tex_color = texture(texture_array[0], UV); break;
        case 1: tex_color = texture(texture_array[1], UV); break;
        case 2: tex_color = texture(texture_array[2], UV); break;
        case 3: tex_color = texture(texture_array[3], UV); break;
    }
    ALBEDO = tex_color.rgb;
}
```

```gdscript
func apply_variant(mesh_instance: GeometryInstance3D, index: int) -> void:
    mesh_instance.set_instance_shader_parameter(&"texture_index", index)
```

### 11. Expert Pattern: Dissolve-Shader-Integration (Alpha Scissor)

```gdscript
func trigger_dissolve(mesh: MeshInstance3D, duration: float = 1.0) -> void:
    var mat := mesh.get_surface_override_material(0) as StandardMaterial3D
    if not mat: return

    mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
    var tween := create_tween()
    tween.tween_property(mat, "alpha_scissor_threshold", 1.0, duration).from(0.0)
```

### 12. Expert Pattern: Material-LOD-System (HLOD)

```gdscript
func setup_lod_materials(detailed_node: GeometryInstance3D, distant_node: GeometryInstance3D) -> void:
    detailed_node.visibility_range_end = 50.0
    detailed_node.visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_SELF

    distant_node.visibility_range_begin = 50.0
    distant_node.visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_SELF

    var dist_mat := distant_node.get_surface_override_material(0) as StandardMaterial3D
    if dist_mat:
        dist_mat.normal_enabled = false
        dist_mat.rim_enabled = false
        dist_mat.clearcoat_enabled = false
        dist_mat.subsurf_scatter_enabled = false
        dist_mat.distance_fade_mode = BaseMaterial3D.DISTANCE_FADE_PIXEL_DITHER
```

### 13. Common Material Presets

```gdscript
# Glass
func create_glass() -> StandardMaterial3D:
    var mat := StandardMaterial3D.new()
    mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
    mat.albedo_color = Color(1, 1, 1, 0.2)
    mat.metallic = 0.0
    mat.roughness = 0.0
    mat.refraction_enabled = true
    mat.refraction_scale = 0.05
    return mat

# Gold
func create_gold() -> StandardMaterial3D:
    var mat := StandardMaterial3D.new()
    mat.albedo_color = Color(1.0, 0.85, 0.3)
    mat.metallic = 1.0
    mat.roughness = 0.3
    return mat
```

## Pitfalls

- **Normal maps silently fail** — `normal_enabled` defaults to `false`. Always set it to `true` before assigning `normal_texture`.
- **Wrong texture import settings** — In the Import tab, set Texture type to "Normal Map" for normal textures, or they render incorrectly.
- **Mipmaps cause seams on tightly-packed UVs** — Disable mipmaps (Import → Mipmaps → Generate = false) for atlas-style textures.
- **Material looks flat** — Missing normal map or roughness variation. Add both for surface detail.
- **`metallic = 0.5` is physically incorrect** — Use 1.0 (metal) or 0.0 (dielectric) unless simulating rust/dirt transitions via a mask texture.
- **Emission > 1.0 does nothing without HDR** — Enable HDR in Project Settings → Rendering.
- **Transparent materials on large surfaces cause massive overdraw** — Split mesh into opaque + transparent surfaces if only a small part is transparent.
- **Hundreds of slightly varied materials break batching** — Group configurations; Godot reuses the underlying shader only when flags match exactly.
- **Z-fighting fixed by moving objects apart fails at distance** — Increase Camera3D `Near`, decrease `Far` to compress precision range.
- **Unique Material per MeshInstance3D breaks draw call batching** — Use Instance Uniforms to vary parameters on a shared material.
- **Decals stick to moving actors** — Always set a Cull Mask on Decals to exclude character layers.
- **Full alpha blend (`TRANSPARENCY_ALPHA`) for cutouts** — Use `ALPHA_SCISSOR` or `ALPHA_HASH` instead; full blend is slow and causes sorting issues.

## Verification

1. **Normal map enabled:**
   ```gdscript
   print(mat.normal_enabled)  # Expected: true
   print(mat.normal_texture)  # Expected: non-null Resource
   ```

2. **ORM texture assigned:**
   ```gdscript
   print(mat.orm_texture)  # Expected: non-null, replaces separate AO/rough/metal
   ```

3. **Transparency mode correct for use case:**
   ```gdscript
   print(mat.transparency)  # Foliage: 1 (ALPHA_SCISSOR), Glass: 3 (ALPHA)
   ```

4. **Metallic is binary (unless transition):**
   ```gdscript
   print(mat.metallic)  # Expected: 0.0 or 1.0 for pure materials
   ```

5. **Material reuse (batching):**
   ```gdscript
   # All walls should share the same resource instance
   var mats := get_tree().get_nodes_in_group("stone_walls").map(
       func(w): return w.material_override.get_instance_id()
   )
   print(mats.all(func(id): return id == mats[0]))  # Expected: true
   ```

6. **Emission with HDR:**
   ```gdscript
   print(ProjectSettings.get_setting("rendering/viewport/hdr_2d"))  # Expected: true if emission > 1.0
   ```

7. **Camera depth precision (Z-fighting fix):**
   ```gdscript
   print($Camera3D.near)  # Should be as large as acceptable
   print($Camera3D.far)   # Should be as small as acceptable
   ```

8. **Decal cull mask set:**
   ```gdscript
   print($Decal.cull_mask)  # Expected: character layers excluded
   ```

## Related Skills

- Master Skill: [godot-master](../godot-master/SKILL.md)
