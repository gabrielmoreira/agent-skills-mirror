---
name: bevy-shaders
description: "Bevy ECS skill for shaders. Keywords: Bevy, shader, material, bevy_shader, bevy_material, StandardMaterial."
---

# Bevy shaders and materials

## When to use

Load this when a surface needs a custom material or a full-screen effect. `StandardMaterial` field lists stay on bevy-3d-materials. Shader source is WGSL loaded as an asset.

## ECS shape

- **Shader asset:** `AssetServer` loads a `Shader` from a path. `ShaderRef::Handle` or a path string points a material at that asset.
- **Material:** implement `Material`, derive `AsBindGroup`, and register `MaterialPlugin::<T>`. The engine extracts materials. Do not schedule a shader compiler.
- **Full-screen:** `Bloom` is a camera component from `bevy::post_process`. It requires an HDR camera, which the component requests itself.

## Examples

```toml
[dependencies]
bevy = "0.20"
```

A material stores a color uniform and names its fragment shader. Register the plugin before any system spawns that material.

```rust
use bevy::pbr::{Material, MaterialPlugin};
use bevy::render::render_resource::AsBindGroup;
use bevy::shader::ShaderRef;

#[derive(Asset, TypePath, AsBindGroup, Clone)]
struct PulseMaterial {
    #[uniform(0)]
    color: LinearRgba,
}

impl Material for PulseMaterial {
    fn fragment_shader() -> ShaderRef {
        "shaders/pulse.wgsl".into()
    }
}

fn main() {
    App::new()
        .add_plugins(DefaultPlugins)
        .add_plugins(MaterialPlugin::<PulseMaterial>::default())
        .run();
}
```

Spawn uses the same mesh and material components as a PBR surface. The asset store owns the material.

```rust
use bevy::pbr::Material;
use bevy::render::render_resource::AsBindGroup;
use bevy::shader::ShaderRef;

#[derive(Asset, TypePath, AsBindGroup, Clone)]
struct PulseMaterial {
    #[uniform(0)]
    color: LinearRgba,
}

impl Material for PulseMaterial {
    fn fragment_shader() -> ShaderRef {
        "shaders/pulse.wgsl".into()
    }
}

fn spawn_pulse(
    mut commands: Commands,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<PulseMaterial>>,
) {
    let mesh = meshes.add(Cuboid::new(1.0, 1.0, 1.0));
    let material = materials.add(PulseMaterial {
        color: LinearRgba::rgb(0.2, 0.7, 0.9),
    });
    commands.spawn((
        Mesh3d(mesh),
        MeshMaterial3d(material),
        Transform::default(),
    ));
}
```

Load the shader yourself when the handle must be explicit. `ShaderRef` accepts that handle.

```rust
use bevy::shader::{Shader, ShaderRef};

#[derive(Resource)]
struct PulseShader(Handle<Shader>);

fn load_pulse(asset_server: Res<AssetServer>, mut commands: Commands) {
    let handle: Handle<Shader> = asset_server.load("shaders/pulse.wgsl");
    commands.insert_resource(PulseShader(handle));
}

fn shader_ref(shader: Res<PulseShader>) -> ShaderRef {
    shader.0.clone().into()
}
```

Bloom is the full-screen pass. Intensity is the scene-wide scatter amount.

```rust
use bevy::post_process::bloom::Bloom;

fn spawn_bloom_camera(mut commands: Commands) {
    commands.spawn((
        Camera3d::default(),
        Bloom {
            intensity: 0.2,
            ..default()
        },
    ));
}
```

## Same job, Bevy types

| Design | Bevy idiom |
| --- | --- |
| ShaderMaterial | `Material` plus a WGSL path in `fragment_shader` |
| Spatial shader | Vertex and fragment `ShaderRef` on that material |
| Full-screen pass | `Bloom` (or another `bevy::post_process` component) on the camera |

## Scope

WGSL entry points live in the shader file the `ShaderRef` names. Bindings are the `AsBindGroup` fields on the material struct. Pipeline specialization stays inside the material plugin.

## Expert Knowledge Delta

Target: **Bevy 0.20+**.

Core ECS types: `Component`, `Resource`, `Query`, `Commands`, `Startup`, `Update`, `Fixed` / `FixedMain` (`bevy::time`), `.chain()`, `Plugin`, `DefaultPlugins`, `MinimalPlugins`. Messages and observers are an ownership slot. See `bevy-events-messaging` for their APIs. Systems run in parallel unless `.chain()` orders the ones that conflict.

### Who owns state

| Piece | Owner | Who may mutate | Schedule |
| --- | --- | --- | --- |
| Data on one entity | `Component` | One system via `Query` | `Update` or `FixedMain` |
| One value for the whole app | `Resource` | One system | `Startup` to insert, then the schedule that reads it |
| Spawn | `Commands` | The spawning system | `Startup` for the initial world; later schedules for runtime spawn |
| Order that must not race | `.chain()` | The chained systems only | Same schedule |
| Plugin boundary | `Plugin` | `build` registers systems and resources | Before the app runs |

Borrow rule: two systems that both mutably query the same component must be ordered (`.chain()`) or split so only one writes. Unrelated systems stay parallel. That is the ECS page rule, not a guess at a system-set API.

### Decision

| If you need | Do this | Do not |
| --- | --- | --- |
| Per-entity data | `Component` + `Query` | A scene-tree script hung on the entity |
| App-wide config or clock | `Resource` | Copy the value onto every entity |
| Stable simulation step | `FixedMain` and the `Fixed` clock | Tie simulation to raw frame `Update` |
| Startup spawn | `Commands` in `Startup` | Spawn from a render system |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| An API outside the documented set | Check the official docs first | A made-up crate or API |

Load [references/ecs-ownership.md](references/ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- No Godot shader language or hint syntax. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

- No Godot types in Bevy code. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No invented APIs or unnamed third-party crates as the chosen solver. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

Official pages stay on unversioned bevy.org URLs. The library pin on bevy-master stays **0.20.0**. Custom surfaces use `Material`, `AsBindGroup`, and `MaterialPlugin`. `StandardMaterial` field lists stay on bevy-3d-materials.

### Official Documentation
- [Assets](https://bevy.org/assets/) - Official asset catalog. No third-party crate was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, systems, `Query`, `Startup`, `Update`, and `.chain()`.
- [Plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and `add_plugins`.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Components and systems.
- [bevy-3d-materials](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-3d-materials/SKILL.md) - StandardMaterial surface fields.
- [bevy-asset-scenes](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-asset-scenes/SKILL.md) - Asset handles.

#### Complements
- [bevy-3d-lighting](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-3d-lighting/SKILL.md) - Lights are not shaders.
- [godot-shaders-basics](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/godot-shaders-basics/SKILL.md) - Equivalent Godot skill.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
