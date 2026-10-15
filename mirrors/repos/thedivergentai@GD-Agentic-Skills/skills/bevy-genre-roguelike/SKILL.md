---
name: bevy-genre-roguelike
description: "Route a Bevy 0.20 roguelike: RunSeed resource, room entities, permadeath flag, turn energy, grid pickup. Keywords: Bevy, roguelike, RunSeed, permadeath, turn, loot, ECS."
---

# Bevy Roguelike (thin router)

Genre router. Domain work lives in the Bevy skills below.

## When to use

Load this for run seeds, room generation, and permadeath flags.

## ECS shape

- **Components** hold the genre's per-entity flags as plain data. This file does not name new engine types.
- **Resources** hold run-wide counters (score, wave index, seed) via bevy-data-resources.
- **Systems** read those components on `Update` or the fixed timestep from bevy-master. Order them with `.chain()` when a later system must see the result.
- **Schedule:** gameplay mode changes go through bevy-state-machines. Do not invent a genre plugin.

## Routing

- [bevy-procedural-generation](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-procedural-generation/SKILL.md) - Seed and spawn.
- [bevy-turn-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-turn-system/SKILL.md) - Turn order when the run is turn-based.
- [bevy-inventory-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-inventory-system/SKILL.md) - Run loot.
- [bevy-rpg-stats](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-rpg-stats/SKILL.md) - Run stats.

## Examples

```toml
[dependencies]
bevy = "0.20"
rand = "0.9"
```

The run seed is one resource. Rooms are entities. `StdRng` is built inside the system so the seed stays on the resource.

```rust
use rand::rngs::StdRng;
use rand::{Rng, SeedableRng};

#[derive(Resource)]
struct RunSeed(u64);

#[derive(Component)]
struct Room {
    x: i32,
    y: i32,
}

fn carve(mut commands: Commands, seed: Res<RunSeed>) {
    let mut rng = StdRng::seed_from_u64(seed.0);
    for _ in 0..8 {
        commands.spawn(Room {
            x: rng.random_range(-6..6),
            y: rng.random_range(-6..6),
        });
    }
}

fn install_run(app: &mut App) {
    app.insert_resource(RunSeed(0x5EED))
        .add_systems(Startup, carve);
}
```

Permadeath is a flag on the actor plus a run-wide resource. One system writes both.

```rust
#[derive(Component)]
struct Actor {
    hp: i32,
}

#[derive(Resource)]
struct RunOver(bool);

fn permadeath(mut actors: Query<&mut Actor>, mut over: ResMut<RunOver>) {
    for mut actor in &mut actors {
        if actor.hp > 0 {
            continue;
        }
        actor.hp = 0;
        over.0 = true;
    }
}
```

Turn energy accumulates on a resource. Acting spends it. Chain the two systems because both write `TurnClock`.

```rust
#[derive(Resource)]
struct TurnClock {
    energy: f32,
}

fn charge(time: Res<Time>, mut clock: ResMut<TurnClock>) {
    clock.energy = (clock.energy + time.delta_secs()).min(1.0);
}

#[derive(Component)]
struct Actor {
    hp: i32,
}

fn spend(mut clock: ResMut<TurnClock>, mut actors: Query<&mut Actor>) {
    if clock.energy < 1.0 {
        return;
    }
    clock.energy = 0.0;
    for mut actor in &mut actors {
        if actor.hp > 0 {
            actor.hp -= 1;
        }
    }
}

fn install_turns(app: &mut App) {
    app.insert_resource(TurnClock { energy: 0.0 })
        .add_systems(Update, (charge, spend).chain());
}
```

Loot on the floor is an entity the actor can pick up by grid distance.

```rust
#[derive(Component)]
struct Loot {
    value: u32,
}

#[derive(Component)]
struct GridPos {
    x: i32,
    y: i32,
}

#[derive(Component)]
struct Actor;

#[derive(Resource)]
struct RunSeed(u64);

fn pickup(
    mut commands: Commands,
    actors: Query<&GridPos, With<Actor>>,
    loot: Query<(Entity, &GridPos, &Loot)>,
    mut wallet: ResMut<RunSeed>,
) {
    for actor in &actors {
        for (entity, pos, item) in &loot {
            if actor.x == pos.x && actor.y == pos.y {
                wallet.0 = wallet.0.wrapping_add(u64::from(item.value));
                commands.entity(entity).despawn();
            }
        }
    }
}
```

`RunSeed` in `pickup` is only a stand-in counter so the example stays inside one resource. A coin wallet belongs on bevy-economy-system. `permadeath` and `spend` both write `Actor`; chain them when both run.

## Scope

- Noise and larger maps route to bevy-procedural-generation.
- Inventory stacks route to bevy-inventory-system.

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
| Per-entity data | `Component` + `Query` | A field stored off the entity |
| App-wide config or clock | `Resource` | Copy the value onto every entity |
| Stable simulation step | `FixedMain` and the `Fixed` clock | Tie simulation to raw frame `Update` |
| Startup spawn | `Commands` in `Startup` | Spawn from a render system |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| An API outside the documented set | Use the examples in this skill | A made-up crate or API |

Load [references/ecs-ownership.md](references/ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- Do not rebuild `StdRng` from a new seed each frame. WHY: the run seed stays on `RunSeed` so room layout stays reproducible.
- Do not let `permadeath` and `spend` both write `Actor` without `.chain()`. WHY: unordered mutable queries on the same component conflict.
- No invented genre APIs. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- Do not pick a physics or net crate here. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

The library pin on bevy-master stays **0.20.0**. Official pages stay on the unversioned `latest` branch.

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
- [godot-genre-roguelike](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/godot-genre-roguelike/SKILL.md) - Roguelike on the Godot engine, same depth.
- [bevy-procedural-generation](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-procedural-generation/SKILL.md) - Seed and spawn.
- [bevy-turn-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-turn-system/SKILL.md) - Turn order when the run is turn-based.
- [bevy-inventory-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-inventory-system/SKILL.md) - Run loot.
- [bevy-rpg-stats](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-rpg-stats/SKILL.md) - Run stats.

#### Downstream / consumers
- None. This router does not own a second implementation.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
