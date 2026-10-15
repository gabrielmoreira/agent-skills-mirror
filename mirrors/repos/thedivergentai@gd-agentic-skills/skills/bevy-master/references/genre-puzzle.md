---
name: bevy-genre-puzzle
description: "Bevy genre router for Puzzle. Keywords: Bevy, Puzzle, genre, ECS, router."
---

# Bevy Puzzle

Genre router. Domain work lives in the Bevy skills below.

## When to use

Load this for grid rules and an undo stack you own.

## ECS shape

- **Components** hold the genre's per-entity flags as plain data. This file does not name new engine types.
- **Resources** hold run-wide counters (score, wave index, seed) via bevy-data-resources.
- **Systems** read those components on `Update` or the fixed timestep from bevy-master. Order them with `.chain()` when a later system must see the result.
- **Schedule:** gameplay mode changes go through bevy-state-machines. Grid tiles and the undo stack below are components plus one resource.

## Examples

```toml
[dependencies]
bevy = "0.20"
```

Each tile stores a grid coordinate and whether it is a goal. The undo stack is a resource of prior coordinates. Read input, push history, then slide. Those systems share `Tile`, so they chain.

```rust
#[derive(Clone, Copy)]
struct GridPos {
    x: i32,
    y: i32,
}

#[derive(Component)]
struct Tile {
    pos: GridPos,
    goal: bool,
}

#[derive(Component)]
struct PlayerToken;

#[derive(Resource, Default)]
struct UndoStack {
    steps: Vec<GridPos>,
}

fn boot(mut commands: Commands) {
    commands.insert_resource(UndoStack { steps: Vec::new() });
    commands.spawn((
        PlayerToken,
        Tile {
            pos: GridPos { x: 0, y: 0 },
            goal: false,
        },
    ));
    commands.spawn(Tile {
        pos: GridPos { x: 2, y: 0 },
        goal: true,
    });
}

fn read_move(keys: Res<ButtonInput<KeyCode>>) -> GridPos {
    if keys.just_pressed(KeyCode::ArrowRight) {
        GridPos { x: 1, y: 0 }
    } else if keys.just_pressed(KeyCode::ArrowLeft) {
        GridPos { x: -1, y: 0 }
    } else if keys.just_pressed(KeyCode::ArrowUp) {
        GridPos { x: 0, y: 1 }
    } else if keys.just_pressed(KeyCode::ArrowDown) {
        GridPos { x: 0, y: -1 }
    } else {
        GridPos { x: 0, y: 0 }
    }
}

fn push_undo(
    keys: Res<ButtonInput<KeyCode>>,
    players: Query<&Tile, With<PlayerToken>>,
    mut undo: ResMut<UndoStack>,
) {
    if keys.just_pressed(KeyCode::KeyZ) {
        return;
    }
    let delta = read_move(keys);
    if delta.x == 0 && delta.y == 0 {
        return;
    }
    if let Some(tile) = players.iter().next() {
        undo.steps.push(tile.pos);
    }
}

fn slide_player(
    keys: Res<ButtonInput<KeyCode>>,
    mut players: Query<&mut Tile, With<PlayerToken>>,
) {
    if keys.just_pressed(KeyCode::KeyZ) {
        return;
    }
    let delta = read_move(keys);
    for mut tile in &mut players {
        tile.pos.x += delta.x;
        tile.pos.y += delta.y;
    }
}

fn undo_move(
    keys: Res<ButtonInput<KeyCode>>,
    mut undo: ResMut<UndoStack>,
    mut players: Query<&mut Tile, With<PlayerToken>>,
) {
    if !keys.just_pressed(KeyCode::KeyZ) {
        return;
    }
    let Some(prev) = undo.steps.pop() else {
        return;
    };
    for mut tile in &mut players {
        tile.pos = prev;
    }
}

fn install(app: &mut App) {
    app.add_systems(Startup, boot).add_systems(
        Update,
        (undo_move, push_undo, slide_player).chain(),
    );
}
```

The puzzle is solved when the player token shares a cell with a goal tile.

```rust
#[derive(Clone, Copy, PartialEq, Eq)]
struct GridPos {
    x: i32,
    y: i32,
}

#[derive(Component)]
struct Tile {
    pos: GridPos,
    goal: bool,
}

#[derive(Component)]
struct PlayerToken;

fn solved(players: Query<&Tile, With<PlayerToken>>, goals: Query<&Tile>) -> bool {
    let Some(player) = players.iter().next() else {
        return false;
    };
    goals.iter().any(|tile| tile.goal && tile.pos == player.pos)
}
```

`push_undo` and `slide_player` both call `read_move`, which reads `ButtonInput` twice in one frame. `just_pressed` stays true for the frame, so both see the same key.

## Scene shape

| Piece | Bevy idiom |
| --- | --- |
| Genre content | Entities plus the domain skills linked below |
| Run-wide director | A `Resource` |
| Loop notices | bevy-events-messaging |

## Routing

- [bevy-state-machines](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-state-machines/SKILL.md) - Solve state.
- [bevy-input-handling](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-input-handling/SKILL.md) - Moves.
- [bevy-data-resources](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-data-resources/SKILL.md) - Rule tables.
- [bevy-ui-layout](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ui-layout/SKILL.md) - Hints.

## Scope

- Tiles store `GridPos`. `UndoStack` keeps prior player coordinates. Bevy has no puzzle-grid type; the example above is the data.

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

Load [references/ecs-ownership.md](genre-puzzle-ecs-ownership.md) for the ownership table.

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
- [godot-genre-puzzle](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/godot-genre-puzzle/SKILL.md) - Peer skill for the same genre.
- [bevy-state-machines](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-state-machines/SKILL.md) - Solve state.
- [bevy-input-handling](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-input-handling/SKILL.md) - Moves.
- [bevy-data-resources](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-data-resources/SKILL.md) - Rule tables.
- [bevy-ui-layout](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ui-layout/SKILL.md) - Hints.

#### Downstream / consumers
- None. This router does not own a second implementation.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
