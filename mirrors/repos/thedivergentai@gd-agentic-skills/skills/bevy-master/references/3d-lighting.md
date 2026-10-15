---
name: bevy-3d-lighting
description: "Spawn and tune Bevy 0.20 directional, point, and spot lights, cascade shadows, distance fog, and a nearest-light shadow budget. Use when a 3D scene needs a sun, local lights, or fog on the camera. Keywords: DirectionalLight, PointLight, SpotLight, CascadeShadowConfig, DistanceFog, bevy_light."
---

# Bevy 3D lighting

## When to use

Load this when a 3D scene needs lights. Materials stay on bevy-3d-materials. Spawn light entities; clustering and shadow extraction stay engine-owned.

## ECS shape

- **Module:** `bevy::light` says it provides directional, point, and spot lights, plus light probes, atmosphere, volumetrics, and shadow configuration.
- **Feature:** `bevy_light` is described the same way on the crate feature list.
- **PBR page names:** `DirectionalLightViewEntities`, `ExtractedDirectionalLight`, `ExtractedPointLight`, `ExtractedRectLight`, `GpuClusteredLight` (point, spot, or rectangle), `DistanceFog`, `LightProbePlugin`, `ContactShadows`.
- **Systems:** light clustering and extraction are engine-owned. Gameplay only spawns light entities.

## Light choice

| Need | Spawn |
| --- | --- |
| Sun | `DirectionalLight` plus `CascadeShadowConfig` on one entity. |
| Local omni | `PointLight` (`intensity` in lumens, `range` in meters). |
| Cone | `SpotLight` with `inner_angle` and `outer_angle` in radians. |
| Distance haze | `DistanceFog` on the camera entity. |
| Local image-based lighting | `LightProbe` with `EnvironmentMapLight` cubemap handles. |

`bevy_solari` is the experimental raytraced-lighting Cargo feature. These examples use the raster lights in `bevy::light`.

```toml
[dependencies]
bevy = "0.20"
```

```rust
use bevy::light::{
    CascadeShadowConfig, CascadeShadowConfigBuilder, DirectionalLightShadowMap, SunDisk,
};

fn spawn_sun(mut commands: Commands) {
    commands.insert_resource(DirectionalLightShadowMap { size: 4096 });
    let cascades: CascadeShadowConfig = CascadeShadowConfigBuilder {
        num_cascades: 4,
        minimum_distance: 0.1,
        first_cascade_far_bound: 10.0,
        maximum_distance: 500.0,
        overlap_proportion: 0.2,
    }
    .into();
    commands.spawn((
        DirectionalLight {
            illuminance: 10_000.0,
            shadow_maps_enabled: true,
            shadow_depth_bias: DirectionalLight::DEFAULT_SHADOW_DEPTH_BIAS,
            shadow_normal_bias: DirectionalLight::DEFAULT_SHADOW_NORMAL_BIAS,
            color: Color::srgb(1.0, 0.96, 0.9),
            ..default()
        },
        cascades,
        SunDisk::EARTH,
        Transform::from_rotation(Quat::from_euler(EulerRot::XYZ, -0.8, 0.4, 0.0)),
    ));
}

pub struct SunPlugin;

impl Plugin for SunPlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(Startup, spawn_sun);
    }
}
```

```rust
fn spawn_local_lights(mut commands: Commands) {
    commands.spawn((
        PointLight {
            intensity: 800.0,
            range: 8.0,
            radius: 0.1,
            shadow_maps_enabled: false,
            color: Color::srgb(1.0, 0.65, 0.3),
            ..default()
        },
        Transform::from_xyz(2.0, 1.5, 0.0),
    ));
    commands.spawn((
        SpotLight {
            intensity: 4_000.0,
            range: 18.0,
            inner_angle: 0.2,
            outer_angle: 0.45,
            shadow_maps_enabled: true,
            color: Color::WHITE,
            ..default()
        },
        Transform::from_xyz(0.0, 2.2, 1.0).looking_at(Vec3::ZERO, Vec3::Y),
    ));
}

fn spawn_fog_camera(mut commands: Commands) {
    commands.spawn((
        Camera3d::default(),
        DistanceFog {
            color: Color::srgb(0.65, 0.7, 0.78),
            directional_light_color: Color::srgb(1.0, 0.9, 0.7),
            directional_light_exponent: 8.0,
            falloff: FogFalloff::Linear {
                start: 20.0,
                end: 90.0,
            },
        },
        Transform::from_xyz(0.0, 2.0, 10.0).looking_at(Vec3::ZERO, Vec3::Y),
    ));
}

fn orbit_sun(time: Res<Time>, mut suns: Query<&mut Transform, With<DirectionalLight>>) {
    for mut transform in &mut suns {
        transform.rotation = Quat::from_euler(
            EulerRot::XYZ,
            -std::f32::consts::FRAC_PI_2 + time.elapsed_secs() * 0.04,
            0.35,
            0.0,
        );
    }
}

fn keep_nearest_point_shadows(
    camera: Query<&GlobalTransform, With<Camera3d>>,
    mut lights: Query<(&GlobalTransform, &mut PointLight)>,
) {
    let Ok(view) = camera.single() else {
        return;
    };
    let origin = view.translation();
    let mut ranked: Vec<(f32, Mut<PointLight>)> = lights
        .iter_mut()
        .map(|(transform, light)| (transform.translation().distance(origin), light))
        .collect();
    ranked.sort_by(|a, b| a.0.total_cmp(&b.0));
    for (index, (_, light)) in ranked.iter_mut().enumerate() {
        light.shadow_maps_enabled = index < 4;
    }
}

pub struct LightingPlugin;

impl Plugin for LightingPlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(Startup, (spawn_local_lights, spawn_fog_camera))
            .add_systems(Update, (orbit_sun, keep_nearest_point_shadows).chain());
    }
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
| Per-entity data | `Component` + `Query` | One script that owns the whole actor |
| App-wide config or clock | `Resource` | Copy the value onto every entity |
| Stable simulation step | `FixedMain` and the `Fixed` clock | Tie simulation to raw frame `Update` |
| Startup spawn | `Commands` in `Startup` | Spawn from a render system |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| An API outside the documented set | Check the official docs first | A made-up crate or API |

Load [references/ecs-ownership.md](3d-lighting-ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- No light-node types from another engine. WHY: a ported node API will not cluster, extract, or cast cascades the way `bevy::light` does.
- No foreign engine types in Bevy code. WHY: the schedule, queries, and light components only exist on Bevy entities.
- No invented APIs or unnamed third-party crates as the chosen solver. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

The library pin on bevy-master stays **0.20.0**. Load [references/ecs-ownership.md](3d-lighting-ecs-ownership.md) when deciding whether a light value is a component or a resource. Do not load it for material authoring.

### Official Documentation
- [Assets](https://bevy.org/assets/) - Official asset catalog. No third-party crate was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, systems, `Query`, `Startup`, `Update`, and `.chain()`.
- [Plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and `add_plugins`.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Components and systems.
- [bevy-3d-materials](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-3d-materials/SKILL.md) - Lit surfaces.
- [bevy-camera-systems](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-camera-systems/SKILL.md) - Camera the lights affect.

#### Complements
- [bevy-3d-world-building](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-3d-world-building/SKILL.md) - Place light entities in a level.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
