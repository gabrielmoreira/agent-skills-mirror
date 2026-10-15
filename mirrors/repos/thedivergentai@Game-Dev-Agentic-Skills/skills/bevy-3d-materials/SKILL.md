---
name: bevy-3d-materials
description: "Bevy ECS skill for PBR materials. Keywords: Bevy, StandardMaterial, PBR, material, ExtendedMaterial."
---

# Bevy 3D materials

## When to use

Load this when a mesh needs a PBR surface. Custom shader extension points are on bevy-shaders. Lighting is on bevy-3d-lighting.

## ECS shape

- **Type:** `StandardMaterial` (feature blurbs and `DistanceFog`).
- **Extension:** `ExtendedMaterial` on the pbr page.
- **Features that mention StandardMaterial textures:** `pbr_anisotropy_texture`, `pbr_multi_layer_material_textures`, `pbr_specular_textures`, `pbr_transmission_textures`. Check the struct page for field names before writing them.
- **Plugin:** `bevy_pbr` adds PBR rendering. It is part of the 3d render collection.

## Surface choice

| Need | Bevy idiom |
| --- | --- |
| PBR surface | `StandardMaterial` on `MeshMaterial3d`, with `base_color`, `metallic`, and `perceptual_roughness`. |
| Extra shader data on that surface | `ExtendedMaterial<StandardMaterial, E>` where `E: MaterialExtension`. |
| Transparency | `alpha_mode`: `AlphaMode::Mask` for cutout, `AlphaMode::Blend` for glass. |

## Examples

```toml
[dependencies]
bevy = "0.20"
```

Spawn a mesh with a metal `StandardMaterial`. The mesh component is `Mesh3d`. The material component is `MeshMaterial3d<StandardMaterial>`.

```rust
fn spawn_metal(
    mut commands: Commands,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<StandardMaterial>>,
) {
    let mesh = meshes.add(Cuboid::new(1.0, 1.0, 1.0));
    let material = materials.add(StandardMaterial {
        base_color: Color::srgb(0.75, 0.15, 0.12),
        metallic: 1.0,
        perceptual_roughness: 0.25,
        reflectance: 0.5,
        ..default()
    });
    commands.spawn((Mesh3d(mesh), MeshMaterial3d(material), Transform::default()));
}
```

Cutout foliage discards fragments under the mask. Glass uses alpha blending and a translucent base color.

```rust
fn cutout_leaf(image: Handle<Image>) -> StandardMaterial {
    StandardMaterial {
        base_color_texture: Some(image),
        alpha_mode: AlphaMode::Mask(0.5),
        diffuse_transmission: 0.4,
        cull_mode: None,
        ..default()
    }
}

fn glass() -> StandardMaterial {
    StandardMaterial {
        base_color: Color::srgba(0.7, 0.85, 1.0, 0.25),
        alpha_mode: AlphaMode::Blend,
        metallic: 0.0,
        perceptual_roughness: 0.05,
        ..default()
    }
}
```

One shared asset stays the source of truth. A runtime tint clones the handle's material into a new asset so other meshes keep the original.

```rust
fn tint_one_mesh(
    mut materials: ResMut<Assets<StandardMaterial>>,
    mesh: Query<&MeshMaterial3d<StandardMaterial>>,
) {
    let Ok(handle) = mesh.single() else {
        return;
    };
    let Some(source) = materials.get(handle.id()) else {
        return;
    };
    let mut tinted = source.clone();
    tinted.base_color = Color::srgb(0.2, 0.45, 0.9);
    let _unique = materials.add(tinted);
}
```

`ExtendedMaterial` keeps every `StandardMaterial` field and adds extension data. Register the concrete material type before spawning it.

```rust
use bevy::pbr::{ExtendedMaterial, MaterialExtension};
use bevy::render::render_resource::AsBindGroup;

#[derive(Asset, AsBindGroup, TypePath, Clone, Default)]
struct Wear {
    #[uniform(100)]
    amount: f32,
}

impl MaterialExtension for Wear {}

fn register_wear(app: &mut App) {
    app.add_plugins(MaterialPlugin::<ExtendedMaterial<StandardMaterial, Wear>>::default());
}

fn spawn_worn(
    mut commands: Commands,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<ExtendedMaterial<StandardMaterial, Wear>>>,
) {
    let mesh = meshes.add(Cuboid::new(1.0, 1.0, 1.0));
    let material = materials.add(ExtendedMaterial {
        base: StandardMaterial {
            base_color: Color::srgb(0.4, 0.35, 0.3),
            perceptual_roughness: 0.8,
            ..default()
        },
        extension: Wear { amount: 0.6 },
    });
    commands.spawn((Mesh3d(mesh), MeshMaterial3d(material)));
}
```

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
| Per-entity data | `Component` + `Query` | A plain struct stored outside the world |
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

- No material fields this skill did not name. WHY: unnamed fields change between Bevy releases and the compiler is the check.
- No invented APIs or unnamed third-party crates as the chosen solver. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

The library pin on bevy-master stays **0.20.0**. Permalinks stay unversioned.

### Official Documentation
- [Assets](https://bevy.org/assets/) - Official asset catalog. No third-party crate was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [3D examples](https://github.com/bevyengine/bevy/tree/latest/examples/3d) - Mesh, material, and lighting samples.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, systems, `Query`, `Startup`, `Update`, and `.chain()`.
- [Plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and `add_plugins`.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Components and systems.
- [bevy-shaders](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-shaders/SKILL.md) - Custom shaders and material extensions.
- [bevy-3d-lighting](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-3d-lighting/SKILL.md) - Lights that shade the material.

#### Complements
- None yet.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
