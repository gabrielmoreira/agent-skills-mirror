---
name: bevy-procedural-generation
description: "Bevy ECS skill for procedural generation. Keywords: Bevy, procedural, seed, dungeon, terrain, ECS."
---

# Bevy procedural generation

## When to use

Load this when a level, loot table, or map should be reproducible from a seed, and you need the ECS shape. Spawning the finished layout uses `Commands` on `Startup` or a later schedule you already use. Saving the seed belongs on bevy-save-load.

## ECS shape

- **Components:** cell facts you define, spawned with `Commands`.
- **Resources:** one `RunSeed` for the whole run. The generator reads it; it does not invent a Bevy RNG type. `rand` 0.9 supplies `StdRng`.
- **Systems:** insert the seed on `Startup`, then spawn from that data. `.chain()` so the spawn system sees the seed.
- **Schedule:** `Startup` for a one-shot map. A streaming map is a later `Update` system that still reads the same seed.

```toml
[dependencies]
bevy = "0.20"
rand = "0.9"
```

The seed is a resource. The walk is plain data. Entities are spawned only after the seed exists.

```rust
use rand::rngs::StdRng;
use rand::{Rng, SeedableRng};

#[derive(Resource)]
struct RunSeed(u64);

#[derive(Component, Clone, Copy)]
struct FloorCell {
    x: i32,
    y: i32,
}

fn insert_seed(mut commands: Commands) {
    commands.insert_resource(RunSeed(42));
}

fn spawn_walk(mut commands: Commands, seed: Res<RunSeed>) {
    let mut rng = StdRng::seed_from_u64(seed.0);
    let mut x = 0;
    let mut y = 0;
    for _ in 0..24 {
        commands.spawn((
            FloorCell { x, y },
            Transform::from_xyz(x as f32, y as f32, 0.0),
        ));
        match rng.random_range(0..4) {
            0 => x += 1,
            1 => x -= 1,
            2 => y += 1,
            _ => y -= 1,
        }
    }
}

pub struct DungeonPlugin;

impl Plugin for DungeonPlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(Startup, (insert_seed, spawn_walk).chain());
    }
}
```

Height samples stay in a resource. The same seed always rebuilds the same grid. Sampling happens once, not every frame.

```rust
#[derive(Resource)]
struct HeightGrid {
    width: i32,
    samples: Vec<f32>,
}

#[derive(Resource)]
struct RunSeed(u64);

fn hash_unit(x: i32, y: i32, seed: u64) -> f32 {
    let mut n = seed
        .wrapping_mul(0x9E37_79B9_7F4A_7C15)
        ^ (x as u64).wrapping_mul(0xBF58_476D_1CE4_E5B9)
        ^ (y as u64).wrapping_mul(0x94D0_49BB_1331_11EB);
    n = (n ^ (n >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
    n = (n ^ (n >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
    n ^= n >> 31;
    (n >> 40) as f32 / (1u32 << 24) as f32
}

fn build_heights(mut commands: Commands, seed: Res<RunSeed>) {
    let width = 16;
    let mut samples = Vec::with_capacity((width * width) as usize);
    for y in 0..width {
        for x in 0..width {
            samples.push(hash_unit(x, y, seed.0));
        }
    }
    commands.insert_resource(HeightGrid { width, samples });
}
```

Rooms are rectangles carved into a grid you own. Spawn markers only for floor cells.

```rust
struct Room {
    x: i32,
    y: i32,
    w: i32,
    h: i32,
}

fn carve(width: i32, rooms: &[Room]) -> Vec<bool> {
    let mut floor = vec![false; (width * width) as usize];
    for room in rooms {
        for y in room.y..room.y + room.h {
            for x in room.x..room.x + room.w {
                if (0..width).contains(&x) && (0..width).contains(&y) {
                    floor[(y * width + x) as usize] = true;
                }
            }
        }
    }
    floor
}

#[derive(Component, Clone, Copy)]
struct FloorCell {
    x: i32,
    y: i32,
}

fn spawn_rooms(mut commands: Commands) {
    let rooms = [
        Room { x: 1, y: 1, w: 4, h: 3 },
        Room { x: 8, y: 6, w: 5, h: 4 },
    ];
    let width = 16;
    for (i, open) in carve(width, &rooms).into_iter().enumerate() {
        if open {
            let x = (i as i32) % width;
            let y = (i as i32) / width;
            commands.spawn(FloorCell { x, y });
        }
    }
}
```

## Choose the owner

| Need | Owner |
| --- | --- |
| Seeded run | A `Resource` holding a seed you define |
| Chunk or dungeon grid | Your components, spawned with `Commands` |
| Hash, rooms, or walk | Your functions over a `RunSeed`. `rand::rngs::StdRng` is the seeded generator. |
| Floor cells | Entities spawned from the grid. Tilemaps belong on the tile skill. |
| Nav bake after generation | Nav bake after generation belongs on bevy-navigation. |

## Scope

- Seeded walks and room carves above use `rand` 0.9 and your own grid. Bevy does not ship a dungeon solver.
- Build the grid on the main schedule, then spawn. `Commands` stay on the system that runs there.
- Navigation rebake after a generated map belongs on bevy-navigation.

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
| Per-entity data | `Component` + `Query` | A value that is not a component |
| App-wide config or clock | `Resource` | Copy the value onto every entity |
| Stable simulation step | `FixedMain` and the `Fixed` clock | Tie simulation to raw frame `Update` |
| Startup spawn | `Commands` in `Startup` | Spawn from a render system |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| An API outside the documented set | Check the official docs first | A made-up crate or API |

Load [references/ecs-ownership.md](procedural-generation-ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- No Godot noise, tile, or thread-pool types. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No invented noise, wave-function, or chunk APIs. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No named third-party generation crate as the chosen tool. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- [Assets](https://bevy.org/assets/) - Official asset catalog.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, `Commands`, `Startup`, and `.chain()`.
- [Resources](https://bevy.org/learn/quick-start/getting-started/resources/) - App-wide seed state. API limits are on bevy-data-resources.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - ECS ownership.
- [bevy-data-resources](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-data-resources/SKILL.md) - `Resource` versus `Component`.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Spawn tuples and `.chain()`.

#### Complements
- [bevy-asset-scenes](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-asset-scenes/SKILL.md) - Spawn a scene asset. Not a generator.
- [bevy-save-load](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-save-load/SKILL.md) - Seed persistence.
- [bevy-navigation](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-navigation/SKILL.md) - No bake after a generated map.
- [godot-procedural-generation](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/godot-procedural-generation/SKILL.md) - Equivalent Godot skill.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
