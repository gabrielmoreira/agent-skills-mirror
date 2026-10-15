---
name: bevy-asset-scenes
description: "Load Bevy 0.20 assets with AssetServer and spawn scenes with bsn!, spawn_scene, and queue_spawn_scene. Use when content comes from disk, a handle must be ready, or a level root should be replaced. Keywords: AssetServer, Handle, is_loaded_with_dependencies, bsn, Scene, file_watcher, LevelRoot."
---

# Bevy asset scenes

## When to use

Load this when content comes from disk or a scene description should spawn entities. `AssetServer` loads files. `bsn!` describes a `Scene` that `spawn_scene` or `queue_spawn_scene` turns into entities.

## ECS shape

- **Assets:** `AssetServer` is the resource that loads from disk. `AssetServer::load` returns a `Handle` and does not reload while a strong handle still exists. Loaded data lives in `Assets<T>`. `AssetServer::is_loaded_with_dependencies` is true when the asset and its dependencies are ready. `LoadState` is the status type named on that page.
- **Handles:** strong handles are reference counted. Dropping the last strong handle removes the asset. Weak handles do not keep it alive. `Assets::add` inserts a procedural asset and does not deduplicate.
- **Hot reload:** the `file_watcher` Cargo feature, and `AssetPlugin`'s `watch_for_changes_override` field, are the toggles named on the asset index.
- **Scenes:** `bevy::scene` describes a `Scene` (entity, components, children, assets), built with the `bsn!` macro. `World::spawn_scene` and `Commands::spawn_scene` spawn immediately and error if asset dependencies are not loaded. `World::queue_spawn_scene` and `Commands::queue_spawn_scene` wait, then spawn in the `SpawnScene` schedule between `Update` and `PostUpdate`.
- **Hierarchy in a scene:** `Children [ ... ]` inside `bsn!`. Separate sibling entities with `--`. `#Name` assigns a `Name` inside that macro's scope.

## Asset choice

| Need | Do this |
| --- | --- |
| Load a file | `AssetServer::load` returns a `Handle` |
| Wait until ready | `is_loaded_with_dependencies` before a state change |
| Spawn a scene now | `spawn_scene` only after dependencies are loaded |
| Spawn when ready | `queue_spawn_scene` (`SpawnScene` sits between `Update` and `PostUpdate`) |
| Children in that scene | `Children` inside `bsn!` |
| Change one entity's mesh | Swap the `Handle` on the component that stores it |

`.bsn` files on disk are still ahead of the shipping scene API. Author scenes with `bsn!`. Free a previous level by despawning its root, then queue the next scene. Register a custom `AssetLoader` with `App::register_asset_loader` once that loader type exists.

```toml
[dependencies]
bevy = { version = "0.20", features = ["file_watcher"] }
```

```rust
#[derive(Resource)]
struct PropMesh(Handle<Mesh>);

fn begin_load(mut commands: Commands, assets: Res<AssetServer>) {
    let handle: Handle<Mesh> = assets.load("models/crate.glb#Mesh0/Primitive0");
    commands.insert_resource(PropMesh(handle));
}

fn mesh_is_ready(assets: Res<AssetServer>, mesh: Option<Res<PropMesh>>) -> bool {
    match mesh {
        Some(mesh) => assets.is_loaded_with_dependencies(&mesh.0),
        None => false,
    }
}

fn store_generated_material(
    mut materials: ResMut<Assets<StandardMaterial>>,
    mut commands: Commands,
) {
    let handle = materials.add(StandardMaterial {
        base_color: Color::srgb(0.8, 0.8, 0.82),
        ..default()
    });
    commands.insert_resource(GeneratedMaterial(handle));
}

#[derive(Resource)]
struct GeneratedMaterial(Handle<StandardMaterial>);
```

```rust
#[derive(Component, Default, Clone)]
struct CrateProp;

#[derive(Component, Default, Clone)]
struct Lid;

#[derive(Component, Default, Clone)]
struct LevelRoot;

fn spawn_crate(mut commands: Commands) {
    commands.spawn_scene(bsn! {
        #SupplyCrate
        CrateProp
        Children [
            Lid
        ]
    });
}

fn queue_level(mut commands: Commands) {
    commands.queue_spawn_scene(bsn! {
        :"levels/yard.bsn"
        LevelRoot
    });
}

fn replace_level(mut commands: Commands, roots: Query<Entity, With<LevelRoot>>) {
    for entity in &roots {
        commands.entity(entity).despawn();
    }
    commands.queue_spawn_scene(bsn! {
        LevelRoot
    });
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

Load [references/ecs-ownership.md](asset-scenes-ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- No packed-scene or resource-loader types from another engine. WHY: readiness is `is_loaded_with_dependencies`, and spawn is `spawn_scene` or `queue_spawn_scene`, not a node instance.
- No scene format this file did not open. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No third-party scene crates. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

The library pin on bevy-master stays **0.20.0**. Load [references/ecs-ownership.md](asset-scenes-ecs-ownership.md) when a handle is a resource and a scene root is a component. Do not load it to write a custom loader body.

### Official Documentation
- [Assets](https://bevy.org/assets/)  -  Official asset catalog. `AssetServer`, `Handle`, and `Assets<T>` are the load path. `Scene`, `bsn!`, `spawn_scene`, `queue_spawn_scene`, and `SpawnScene` are the spawn path.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples)  -  Example tree on the `latest` branch.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  Who owns which piece of state.
- [bevy-project-foundations](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-project-foundations/SKILL.md)  -  Cargo features, including asset watcher flags.
- [bevy-state-machines](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-state-machines/SKILL.md)  -  The asset page points at app states for load gates.

#### Complements
- [bevy-audio-systems](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-audio-systems/SKILL.md)  -  Clips loaded through `AssetServer`.
- [bevy-save-load](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-save-load/SKILL.md)  -  Player saves, separate from scene spawn.

#### Downstream / consumers
- [bevy-camera-systems](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-camera-systems/SKILL.md)  -  Camera entities a scene may spawn.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  Bevy router.
