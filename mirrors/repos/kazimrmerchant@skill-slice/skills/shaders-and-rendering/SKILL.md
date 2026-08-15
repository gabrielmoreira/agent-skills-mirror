---
name: shaders-and-rendering
description: "Use when writing shaders or configuring rendering in Godot 4.x — covers the Godot shading language (GLSL-like), shader types (spatial, canvas_item, particles, sky, fog), vertex and fragment functions, Visual Shader editor, canvas_item shaders for 2D effects, spatial shaders for PBR and custom lighting, particle shaders, uniforms and shader parameters, screen-reading shaders (screen_texture, depth_texture), post-processing, rendering pipelines (Forward+, Mobile, Compatibility), and common shader recipes (dissolve, outline, water, hologram, CRT, blur). Make sure to use this skill whenever writing .gdshader files, creating visual effects, configuring rendering settings, or implementing custom materials in Godot."
version: 1.0.1
---

# Shaders & Rendering (Godot 4.x)

Complete reference for Godot 4.x shading language, visual shaders, rendering pipelines, and common shader effects.

## When to Use

Use when writing custom shaders, implementing visual effects, configuring rendering pipelines, or optimizing graphics in Godot 4.x.

## Prerequisites

- Godot 4.x project.
- Basic understanding of GLSL or Godot shading language.

## Procedure

### 1. Shader Structure

```glsl
shader_type canvas_item;  // spatial, canvas_item, particles, sky, fog

render_mode unshaded, blend_mix;  // rendering hints

// Uniforms — exposed as shader parameters in the inspector
uniform vec4 tint_color : source_color = vec4(1.0);
uniform float intensity : hint_range(0.0, 2.0) = 1.0;
uniform sampler2D noise_tex : filter_linear, repeat_enable;

// Instance uniforms — different value per instance (MultiMesh, etc.)
instance uniform vec4 instance_color : source_color = vec4(1.0);

// Varyings — pass data from vertex to fragment
varying vec2 world_pos;

void vertex() {
    world_pos = (MODEL_MATRIX * vec4(VERTEX, 0.0, 1.0)).xy;
}

void fragment() {
    COLOR = texture(TEXTURE, UV) * tint_color * intensity;
}
```

### 2. Shader Types

| Type | Use | Key Built-ins |
|---|---|---|
| `canvas_item` | 2D sprites, UI, particles | `UV`, `COLOR`, `TEXTURE`, `VERTEX` |
| `spatial` | 3D meshes, terrain | `ALBEDO`, `METALLIC`, `ROUGHNESS`, `EMISSION`, `NORMAL_MAP` |
| `particles` | GPU particle behavior | `VELOCITY`, `TRANSFORM`, `COLOR`, `CUSTOM`, `INDEX` |
| `sky` | Custom sky rendering | `EYEDIR`, `SKY_COORDS`, `AT_HALF_RES_PASS` |
| `fog` | Volumetric fog volumes | `WORLD_POSITION`, `OBJECT_POSITION`, `DENSITY` |

### 3. Canvas Item Shaders (2D)

#### Built-in variables

```glsl
// vertex():
VERTEX      // vec2 — position in local space
UV          // vec2 — texture coordinates
COLOR       // vec4 — vertex color (from modulate)

// fragment():
UV          // vec2 — interpolated texture coordinates
COLOR       // vec4 — output color (default = TEXTURE * vertex COLOR)
TEXTURE     // sampler2D — the node's texture
TEXTURE_PIXEL_SIZE  // vec2 — 1.0 / texture_size (useful for pixel-neighbor effects)
SCREEN_UV   // vec2 — screen-space UV (for screen-reading effects)
TIME        // float — engine time in seconds
```

#### Outline effect

```glsl
shader_type canvas_item;

uniform vec4 outline_color : source_color = vec4(0.0, 0.0, 0.0, 1.0);
uniform float outline_width : hint_range(0.0, 10.0) = 1.0;

void fragment() {
    vec2 size = TEXTURE_PIXEL_SIZE * outline_width;
    float alpha = texture(TEXTURE, UV).a;

    // Sample 4 neighbors
    alpha = max(alpha, texture(TEXTURE, UV + vec2(size.x, 0.0)).a);
    alpha = max(alpha, texture(TEXTURE, UV + vec2(-size.x, 0.0)).a);
    alpha = max(alpha, texture(TEXTURE, UV + vec2(0.0, size.y)).a);
    alpha = max(alpha, texture(TEXTURE, UV + vec2(0.0, -size.y)).a);

    vec4 original = texture(TEXTURE, UV);
    COLOR = mix(vec4(outline_color.rgb, alpha), original, original.a);
}
```

#### Dissolve effect

```glsl
shader_type canvas_item;

uniform float dissolve_amount : hint_range(0.0, 1.0) = 0.0;
uniform sampler2D noise_texture;
uniform vec4 edge_color : source_color = vec4(1.0, 0.5, 0.0, 1.0);
uniform float edge_width : hint_range(0.0, 0.1) = 0.05;

void fragment() {
    vec4 original = texture(TEXTURE, UV);
    float noise = texture(noise_texture, UV).r;

    if (noise < dissolve_amount) {
        discard;
    }

    float edge = smoothstep(dissolve_amount, dissolve_amount + edge_width, noise);
    COLOR = mix(edge_color, original, edge);
    COLOR.a = original.a;
}
```

#### CRT / scanline effect

```glsl
shader_type canvas_item;

uniform float scanline_intensity : hint_range(0.0, 1.0) = 0.3;
uniform float curvature : hint_range(0.0, 0.1) = 0.02;

void fragment() {
    // Apply barrel distortion (curvature)
    vec2 uv = SCREEN_UV * 2.0 - 1.0;
    uv *= 1.0 + curvature * dot(uv, uv);
    uv = uv * 0.5 + 0.5;

    // Discard pixels outside screen
    if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) {
        COLOR = vec4(0.0);
        return;
    }

    vec4 color = texture(TEXTURE, uv);

    // Scanlines
    float scanline = sin(uv.y * 800.0) * scanline_intensity;
    color.rgb -= scanline;

    COLOR = color;
}
```

#### Wave distortion (water surface)

```glsl
shader_type canvas_item;

uniform float wave_speed : hint_range(0.0, 10.0) = 2.0;
uniform float wave_amplitude : hint_range(0.0, 0.1) = 0.01;
uniform float wave_frequency : hint_range(0.0, 50.0) = 10.0;

void fragment() {
    vec2 uv = UV;
    uv.x += sin(uv.y * wave_frequency + TIME * wave_speed) * wave_amplitude;
    uv.y += cos(uv.x * wave_frequency + TIME * wave_speed) * wave_amplitude * 0.5;
    COLOR = texture(TEXTURE, uv);
}
```

### 4. Spatial Shaders (3D)

#### PBR properties

```glsl
shader_type spatial;
render_mode cull_back, diffuse_burley, specular_schlick_ggx;

uniform vec4 albedo_color : source_color = vec4(1.0);
uniform sampler2D albedo_tex : source_color;
uniform float metallic : hint_range(0.0, 1.0) = 0.0;
uniform float roughness : hint_range(0.0, 1.0) = 0.5;
uniform sampler2D normal_map : hint_normal;
uniform float normal_strength : hint_range(0.0, 2.0) = 1.0;
uniform vec3 emission_color : source_color = vec3(0.0);
uniform float emission_energy : hint_range(0.0, 16.0) = 0.0;

void fragment() {
    vec4 tex = texture(albedo_tex, UV);
    ALBEDO = tex.rgb * albedo_color.rgb;
    METALLIC = metallic;
    ROUGHNESS = roughness;
    NORMAL_MAP = texture(normal_map, UV).rgb;
    NORMAL_MAP_DEPTH = normal_strength;
    EMISSION = emission_color * emission_energy;
    ALPHA = tex.a * albedo_color.a;
}
```

#### Toon/cel shading

```glsl
shader_type spatial;
render_mode diffuse_toon, specular_toon;

uniform vec4 albedo_color : source_color = vec4(1.0);
uniform sampler2D albedo_tex : source_color;
uniform float shadow_threshold : hint_range(0.0, 1.0) = 0.3;
uniform vec4 shadow_color : source_color = vec4(0.5, 0.3, 0.4, 1.0);

void fragment() {
    ALBEDO = texture(albedo_tex, UV).rgb * albedo_color.rgb;
    ROUGHNESS = 1.0;
    METALLIC = 0.0;
}

void light() {
    float NdotL = dot(NORMAL, LIGHT);
    float stepped = step(shadow_threshold, NdotL);
    DIFFUSE_LIGHT += mix(shadow_color.rgb, ALBEDO, stepped) * ATTENUATION * LIGHT_COLOR;
}
```

#### Hologram effect

```glsl
shader_type spatial;
render_mode cull_disabled, unshaded;

uniform vec4 holo_color : source_color = vec4(0.0, 0.8, 1.0, 0.5);
uniform float scan_speed : hint_range(0.0, 5.0) = 1.0;
uniform float scan_line_count : hint_range(10.0, 200.0) = 50.0;
uniform float flicker_speed : hint_range(0.0, 20.0) = 5.0;

void fragment() {
    float scan = sin(UV.y * scan_line_count + TIME * scan_speed) * 0.5 + 0.5;
    float fresnel = pow(1.0 - abs(dot(NORMAL, VIEW)), 2.0);
    float flicker = sin(TIME * flicker_speed) * 0.1 + 0.9;

    ALBEDO = holo_color.rgb;
    ALPHA = (scan * 0.5 + fresnel * 0.5) * holo_color.a * flicker;
}
```

### 5. Particle Shaders

```glsl
shader_type particles;

uniform float spread : hint_range(0.0, 3.14) = 1.0;
uniform vec3 gravity = vec3(0.0, -9.8, 0.0);
uniform float initial_speed : hint_range(0.0, 100.0) = 10.0;

void start() {
    // Called once when particle spawns
    float angle = (float(INDEX) / float(AMOUNT)) * spread * 2.0 - spread;
    VELOCITY = vec3(sin(angle), cos(angle), 0.0) * initial_speed;
    COLOR = vec4(1.0, 0.5, 0.0, 1.0);
    CUSTOM.x = 0.0;  // custom data per particle
}

void process() {
    // Called every frame for each living particle
    VELOCITY += gravity * DELTA;
    COLOR.a = 1.0 - (CUSTOM.x / LIFETIME);
    CUSTOM.x += DELTA;  // track age
}
```

### 6. Uniforms and Shader Parameters

```gdscript
# Set shader parameters from GDScript:
var material: ShaderMaterial = sprite.material as ShaderMaterial
material.set_shader_parameter("dissolve_amount", 0.5)
material.set_shader_parameter("tint_color", Color.RED)

# Animate shader parameters with Tween:
var tween := create_tween()
tween.tween_method(
    func(value: float) -> void:
        material.set_shader_parameter("dissolve_amount", value),
    0.0, 1.0, 2.0  # from, to, duration
)
```

#### Uniform hints

| Hint | Type | Effect in Inspector |
|---|---|---|
| `source_color` | vec4/vec3 | Color picker |
| `hint_range(min, max, step)` | float/int | Slider |
| `hint_normal` | sampler2D | Marks as normal map |
| `filter_nearest` | sampler2D | Nearest-neighbor filtering |
| `filter_linear` | sampler2D | Bilinear filtering |
| `repeat_enable` | sampler2D | Enable texture tiling |

### 7. Screen-Reading Shaders

```glsl
shader_type canvas_item;

// Access screen contents (must be behind a transparent object)
uniform sampler2D screen_texture : hint_screen_texture, filter_linear_mipmap;

// Blur effect using screen texture:
void fragment() {
    vec2 pixel_size = 1.0 / vec2(textureSize(screen_texture, 0));
    vec4 color = vec4(0.0);
    float total = 0.0;

    for (int x = -2; x <= 2; x++) {
        for (int y = -2; y <= 2; y++) {
            color += texture(screen_texture, SCREEN_UV + vec2(float(x), float(y)) * pixel_size * 2.0);
            total += 1.0;
        }
    }
    COLOR = color / total;
}
```

#### 3D screen textures

```glsl
shader_type spatial;

// Available in spatial shaders:
uniform sampler2D screen_texture : hint_screen_texture, filter_linear_mipmap;
uniform sampler2D depth_texture : hint_depth_texture;
uniform sampler2D normal_roughness_texture : hint_normal_roughness_texture;

void fragment() {
    // Glass refraction example:
    vec2 ref_uv = SCREEN_UV + NORMAL.xy * 0.02;
    vec3 bg = texture(screen_texture, ref_uv).rgb;
    ALBEDO = bg;
}
```

### 8. Post-Processing

#### Full-screen shader via ColorRect

```gdscript
# Apply post-processing:
# 1. Create a CanvasLayer (layer = 100, to render above everything)
# 2. Add a ColorRect child (full screen via anchors)
# 3. Assign ShaderMaterial with your post-processing shader
# 4. Enable "Use Parent Material" = false

# ColorRect must cover entire viewport:
# Anchor preset: "Full Rect" (all anchors = 0 or 1)
```

#### Environment post-processing (3D)

WorldEnvironment provides built-in effects without custom shaders:

| Effect | Setting | Description |
|---|---|---|
| Glow/Bloom | Environment > Glow | Bright areas bleed light |
| SSAO | Environment > SSAO | Ambient shadows in crevices |
| SSR | Environment > SSR | Screen-space reflections |
| SSIL | Environment > SSIL | Screen-space indirect lighting |
| Fog | Environment > Volumetric Fog | Atmospheric depth fog |
| Tonemap | Environment > Tonemap | HDR to LDR conversion |
| DOF | Camera3D > Attributes > DOF | Depth of field blur |
| Color correction | Environment > Adjustment | Brightness, contrast, saturation, LUT |

### 9. Rendering Pipelines

| Feature | Forward+ | Mobile | Compatibility (GL) |
|---|---|---|---|
| Target hardware | Desktop/console | Mobile/mid-range | Low-end/web |
| SDFGI | ✅ | ❌ | ❌ |
| VoxelGI | ✅ | ❌ | ❌ |
| Volumetric fog | ✅ | ❌ | ❌ |
| SSR | ✅ | ❌ | ❌ |
| SSAO | ✅ | ❌ | ❌ |
| Clustered lighting | ✅ (unlimited) | Limited (8 per mesh) | Limited (8 per mesh) |
| Decals | ✅ | Limited | ❌ |
| Screen-space effects | All | Limited | Few |
| API | Vulkan/D3D12/Metal | Vulkan/D3D12/Metal | OpenGL 3.3/ES 3.0/WebGL2 |

Choose in **Project Settings > Rendering > Renderer > Rendering Method**.

### 10. Visual Shader Editor

Node-based shader creation for non-coders:
- Open via **Shader Editor** dock when a VisualShader resource is selected
- Key node categories: Input, Output, Scalar, Vector, Color, Texture, Transform, Logic, Math
- **Custom Expression node**: embed GLSL code inside a visual shader graph
- **Convert to text**: right-click VisualShader resource > "Convert to ShaderMaterial" for hand-tuning

### 11. Multi-pass Rendering

```gdscript
# next_pass creates layered shader effects:
# Pass 1: base material (StandardMaterial3D or ShaderMaterial)
# Pass 2: outline effect (via material.next_pass)
# Pass 3: glow overlay (via material.next_pass.next_pass)

var outline_material := ShaderMaterial.new()
outline_material.shader = preload("res://shaders/outline.gdshader")
base_material.next_pass = outline_material
```

## Pitfalls

- **`if` branching in fragment**: GPU branch divergence. Use `mix()`, `step()`, `smoothstep()` instead.
- **`screen_texture` everywhere**: Forces framebuffer copies. Use only when necessary.
- **High-res fullscreen shaders**: Kills GPU on mobile. Render at lower resolution in SubViewport.
- **Untyped uniforms**: No inspector controls. Always add hints (`source_color`, `hint_range`).
- **Recomputing constants per pixel**: Wasted GPU cycles. Precompute in `vertex()` or pass as uniform.
- **`render_mode unshaded` on lit objects**: No lighting. Only for UI, particles, or custom `light()`.

## Verification

- [ ] `shader_type` matches the node (`canvas_item` for 2D, `spatial` for 3D).
- [ ] All uniforms have appropriate hints (`source_color`, `hint_range`, etc.).
- [ ] Shader parameters set from GDScript use `set_shader_parameter()`.
- [ ] Screen-reading shaders use `hint_screen_texture`.
- [ ] Transparent shaders use `render_mode` with appropriate blend mode.
- [ ] No unnecessary branching in fragment functions.
- [ ] Visual Shaders consider conversion to text for complex effects.
- [ ] Rendering pipeline chosen matches target platform.

## Related skills

- 2D visual effects → [2d-development](../2d-development/SKILL.md)
- 3D environment setup → [3d-development](../3d-development/SKILL.md)
- Performance optimization → [performance-optimization](../performance-optimization/SKILL.md)
- Animation effects → [animation-system](../animation-system/SKILL.md)
- GDScript shader parameters → [gdscript](../gdscript/SKILL.md)
