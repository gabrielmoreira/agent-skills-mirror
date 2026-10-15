---
name: bevy-genre-sandbox
description: "Bevy 0.20 sandbox router: placed cells, remove, and a serde snapshot of the build. Use when routing a sandbox. Keywords: Bevy, Sandbox, place, save, ECS, router."
---

# Bevy Sandbox (thin router)

Genre router. Domain work lives in the Bevy skills below.

## When to use

Load this for place, remove, and save of player-built entities.

## ECS shape

- **Components** hold the genre's per-entity flags as plain data. This file does not name new engine types.
- **Resources** hold run-wide counters (score, wave index, seed) via bevy-data-resources.
- **Systems** read those components on `Update` or the fixed timestep from bevy-master. Order them with `.chain()` when a later system must see the result.
- **Schedule:** gameplay mode changes go through bevy-state-machines. This file registers only place, edit, and the build snapshot.

## Routing

- [bevy-3d-world-building](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-3d-world-building/SKILL.md) - Props.
- [bevy-inventory-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-inventory-system/SKILL.md) - Build pieces.
- [bevy-save-load](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-save-load/SKILL.md) - World persistence.
- [bevy-input-handling](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-input-handling/SKILL.md) - Place.

## Scope

A placed cell is a component with a grid coordinate and a kind id. Props, inventories, and file persistence stay in the skills linked above.

| Call | Owner here | Leave to the linked skill |
| --- | --- | --- |
| A press places a cell | `PlacedCell` spawned with a kind id | Prop meshes in bevy-3d-world-building |
| Kind 1 at x = 0 becomes kind 2, then kind 0 despawns | `.chain()` paint then remove | File IO in bevy-save-load |
| The build must round-trip | `BuildSnapshot` of serde records | The save plugin in bevy-save-load |

```toml
[dependencies]
bevy = "0.20"
serde = { version = "1", features = ["derive"] }
```

```rust
#[derive(Component, Clone, Copy)]
struct PlacedCell {
    x: i32,
    y: i32,
    z: i32,
    kind: u16,
}

fn place_cell(keys: Res<ButtonInput<KeyCode>>, mut commands: Commands) {
    if keys.just_pressed(KeyCode::KeyP) {
        commands.spawn((
            PlacedCell {
                x: 0,
                y: 0,
                z: 0,
                kind: 1,
            },
            Transform::from_xyz(0.0, 0.0, 0.0),
        ));
    }
}

pub struct PlacePlugin;

impl Plugin for PlacePlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(Update, place_cell);
    }
}
```

```rust
#[derive(Component, Clone, Copy)]
struct PlacedCell {
    x: i32,
    y: i32,
    z: i32,
    kind: u16,
}

fn remove_empty(mut commands: Commands, cells: Query<(Entity, &PlacedCell)>) {
    for (entity, cell) in &cells {
        if cell.kind == 0 {
            commands.entity(entity).despawn();
        }
    }
}

fn paint_neighbor(mut cells: Query<&mut PlacedCell>) {
    for mut cell in &mut cells {
        if cell.x == 0 && cell.kind == 1 {
            cell.kind = 2;
        }
    }
}

pub struct EditPlugin;

impl Plugin for EditPlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(Update, (paint_neighbor, remove_empty).chain());
    }
}
```

```rust
use serde::{Deserialize, Serialize};

#[derive(Component)]
struct PlacedCell {
    x: i32,
    y: i32,
    z: i32,
    kind: u16,
}

#[derive(Serialize, Deserialize, Clone, Default)]
struct CellRecord {
    x: i32,
    y: i32,
    z: i32,
    kind: u16,
}

#[derive(Resource, Default)]
struct BuildSnapshot(Vec<CellRecord>);

fn snapshot(cells: Query<&PlacedCell>, mut saved: ResMut<BuildSnapshot>) {
    saved.0 = cells
        .iter()
        .map(|cell| CellRecord {
            x: cell.x,
            y: cell.y,
            z: cell.z,
            kind: cell.kind,
        })
        .collect();
}

pub struct SnapshotPlugin;

impl Plugin for SnapshotPlugin {
    fn build(&self, app: &mut App) {
        app.init_resource::<BuildSnapshot>()
            .add_systems(Update, snapshot);
    }
}

fn main() {
    App::new()
        .add_plugins(MinimalPlugins)
        .add_plugins(SnapshotPlugin)
        .run();
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
| Per-entity data | `Component` + `Query` | One mutable blob shared by every entity |
| App-wide config or clock | `Resource` | Copy the value onto every entity |
| Stable simulation step | `FixedMain` and the `Fixed` clock | Tie simulation to raw frame `Update` |
| Startup spawn | `Commands` in `Startup` | Spawn from a render system |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| Behavior a linked domain skill already owns | Keep this router to components and resources | A second implementation in this file |

Load [references/ecs-ownership.md](references/ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- Do not paint a cell and despawn it in the same unordered pair. WHY: both touch `PlacedCell` data, so paint runs before remove through `.chain()`.
- No invented genre APIs. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- Do not pick a physics or net crate here. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

The library pin on bevy-master stays **0.20.0**. Official pages stay on the unversioned site.

### Official Documentation
- [Assets](https://bevy.org/assets/) - Official asset catalog. No third-party crate was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, systems, `Query`, `Startup`, `Update`, and `.chain()`.
- [Plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and `add_plugins`.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - ECS ownership and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Spawn and query shape.

#### Complements
- [bevy-3d-world-building](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-3d-world-building/SKILL.md) - Props.
- [bevy-inventory-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-inventory-system/SKILL.md) - Build pieces.
- [bevy-save-load](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-save-load/SKILL.md) - World persistence.
- [bevy-input-handling](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-input-handling/SKILL.md) - Place.

#### Downstream / consumers
- None. This router does not own a second implementation.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
