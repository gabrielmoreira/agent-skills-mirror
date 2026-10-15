---
name: bevy-genre-metroidvania
description: "Bevy genre router for Metroidvania. Keywords: Bevy, Metroidvania, genre, ECS, router."
---

# Bevy Metroidvania

Genre router. Domain work lives in the Bevy skills below.

## When to use

Load this for ability-gated exploration and a map of rooms.

## ECS shape

- **Components** hold the genre's per-entity flags as plain data. This file does not name new engine types.
- **Resources** hold run-wide counters (score, wave index, seed) via bevy-data-resources.
- **Systems** read those components on `Update` or the fixed timestep from bevy-master. Order them with `.chain()` when a later system must see the result.
- **Schedule:** gameplay mode changes go through bevy-state-machines. Ability flags, visited cells, and the map fog below are components plus one resource.

## Examples

```toml
[dependencies]
bevy = "0.20"
```

Traversal is a set of flags on the player. A gate stores the flag it needs. The map stores which cells are revealed. Input, gate checks, and fog share `AbilitySet` and `MapFog`, so those systems chain.

```rust
#[derive(Clone, Copy, PartialEq, Eq)]
enum Ability {
    Dash,
    WallClimb,
    DoubleJump,
}

#[derive(Component)]
struct AbilitySet {
    owned: [bool; 3],
}

impl AbilitySet {
    fn has(&self, ability: Ability) -> bool {
        self.owned[ability as usize]
    }

    fn grant(&mut self, ability: Ability) {
        self.owned[ability as usize] = true;
    }
}

#[derive(Component)]
struct Gate {
    requires: Ability,
    open: bool,
}

#[derive(Component)]
struct MapCell {
    x: i32,
    y: i32,
    visited: bool,
}

#[derive(Resource, Default)]
struct MapFog {
    revealed: u32,
}

fn boot(mut commands: Commands) {
    commands.insert_resource(MapFog { revealed: 0 });
    commands.spawn(AbilitySet {
        owned: [false, false, false],
    });
    commands.spawn(Gate {
        requires: Ability::Dash,
        open: false,
    });
    commands.spawn(MapCell {
        x: 0,
        y: 0,
        visited: false,
    });
}

fn grant_dash(keys: Res<ButtonInput<KeyCode>>, mut players: Query<&mut AbilitySet>) {
    if !keys.just_pressed(KeyCode::KeyE) {
        return;
    }
    for mut set in &mut players {
        set.grant(Ability::Dash);
    }
}

fn open_gates(players: Query<&AbilitySet>, mut gates: Query<&mut Gate>) {
    let Some(player) = players.iter().next() else {
        return;
    };
    for mut gate in &mut gates {
        gate.open = player.has(gate.requires);
    }
}

fn reveal_cell(mut cells: Query<&mut MapCell>, mut fog: ResMut<MapFog>) {
    for mut cell in &mut cells {
        if cell.x == 0 && cell.y == 0 && !cell.visited {
            cell.visited = true;
            fog.revealed = fog.revealed.saturating_add(1);
        }
    }
}

fn install(app: &mut App) {
    app.add_systems(Startup, boot).add_systems(
        Update,
        (grant_dash, open_gates, reveal_cell).chain(),
    );
}
```

A shortcut opens once the player holds both dash and wall climb.

```rust
#[derive(Clone, Copy)]
enum Ability {
    Dash,
    WallClimb,
    DoubleJump,
}

#[derive(Component)]
struct AbilitySet {
    owned: [bool; 3],
}

impl AbilitySet {
    fn has(&self, ability: Ability) -> bool {
        self.owned[ability as usize]
    }
}

fn shortcut_open(players: Query<&AbilitySet>) -> bool {
    players.iter().any(|set| set.has(Ability::Dash) && set.has(Ability::WallClimb))
}
```

## Scene shape

| Piece | Bevy idiom |
| --- | --- |
| Genre content | Entities plus the domain skills linked below |
| Run-wide director | A `Resource` |
| Loop notices | bevy-events-messaging |

## Routing

- [bevy-ability-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ability-system/SKILL.md) - Traversal abilities.
- [bevy-character-movement](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-character-movement/SKILL.md) - Motion.
- [bevy-save-load](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-save-load/SKILL.md) - Map flags.
- [bevy-mechanic-secrets](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-mechanic-secrets/SKILL.md) - Optional rooms.

## Scope

- Ability flags live on `AbilitySet`. Gates and visited cells are components. `MapFog` counts revealed cells. Bevy has no map-graph type; the example above is the data.

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
| Per-entity data | `Component` + `Query` | One script that owns the whole tree |
| App-wide config or clock | `Resource` | Copy the value onto every entity |
| Stable simulation step | `FixedMain` and the `Fixed` clock | Tie simulation to raw frame `Update` |
| Startup spawn | `Commands` in `Startup` | Spawn from a render system |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| An API outside the documented set | Check the official docs first | A made-up crate or API |

Load [references/ecs-ownership.md](genre-metroidvania-ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- No foreign-engine types in Bevy code. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No invented genre APIs. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- Do not pick a physics or net crate here. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

Official pages stay on unversioned permalinks. The library pin on bevy-master stays **0.20**.

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
- [godot-genre-metroidvania](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/godot-genre-metroidvania/SKILL.md) - Peer skill for the same genre.
- [bevy-ability-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ability-system/SKILL.md) - Traversal abilities.
- [bevy-character-movement](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-character-movement/SKILL.md) - Motion.
- [bevy-save-load](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-save-load/SKILL.md) - Map flags.
- [bevy-mechanic-secrets](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-mechanic-secrets/SKILL.md) - Optional rooms.

#### Downstream / consumers
- None. This router does not own a second implementation.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
