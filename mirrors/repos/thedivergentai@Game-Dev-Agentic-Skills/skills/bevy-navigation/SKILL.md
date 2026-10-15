---
name: bevy-navigation
description: "Bevy ECS skill for navigation. Keywords: Bevy, navigation, pathfinding, ECS."
---

# Bevy navigation

## When to use

Load this when agents need a path over walkable space before adding a crate. Movement of the actor after a path exists belongs on bevy-character-movement. Policy for chase, patrol, and retarget belongs on bevy-ai-navigation.

## ECS shape

- **Components** store the goal cell and the waypoint list for one agent.
- **Resources** own the walk grid: width, height, and blocked cells.
- **Systems** search on `Update`, then step along the path on `FixedUpdate`. `.chain()` keeps the new path visible before motion.
- **Schedule:** search and follow stay on the app schedules above. Crowd policy stays on bevy-ai-navigation.

## Ownership

| Need | Bevy shape |
| --- | --- |
| Agent | An entity with a goal and a waypoint list |
| Walkable space | A `WalkGrid` resource of blocked cells |
| Avoidance | Separation stays on bevy-ai-navigation |
| Next waypoint | `AgentPath` stepped on `FixedUpdate` |

## Scope

- A grid, a breadth-first search, and a follower are enough for walkable cells. Navmesh baking and crowd radius stay outside this skill.
- Actor locomotion after a waypoint exists belongs on bevy-character-movement.

## Examples

```toml
[package]
name = "navigation"
version = "0.1.0"
edition = "2021"

[dependencies]
bevy = "0.20"
```

The grid is a resource. Search writes waypoints. The follower consumes them on the fixed step.

```rust
use std::collections::VecDeque;

#[derive(Resource)]
struct WalkGrid {
    width: i32,
    height: i32,
    cell: f32,
    blocked: Vec<bool>,
}

#[derive(Component)]
struct GoalCell(i32, i32);

#[derive(Component)]
struct AgentPath {
    waypoints: Vec<Vec3>,
    index: usize,
}

fn cell_index(grid: &WalkGrid, x: i32, y: i32) -> Option<usize> {
    if x < 0 || y < 0 || x >= grid.width || y >= grid.height {
        return None;
    }
    Some((y * grid.width + x) as usize)
}

fn search(grid: &WalkGrid, start: (i32, i32), goal: (i32, i32)) -> Vec<Vec3> {
    let Some(start_i) = cell_index(grid, start.0, start.1) else {
        return Vec::new();
    };
    if grid.blocked[start_i] {
        return Vec::new();
    }
    let mut prev: Vec<Option<(i32, i32)>> = vec![None; grid.blocked.len()];
    let mut queue = VecDeque::new();
    prev[start_i] = Some(start);
    queue.push_back(start);
    while let Some((x, y)) = queue.pop_front() {
        if (x, y) == goal {
            break;
        }
        for (nx, ny) in [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)] {
            let Some(i) = cell_index(grid, nx, ny) else {
                continue;
            };
            if grid.blocked[i] || prev[i].is_some() {
                continue;
            }
            prev[i] = Some((x, y));
            queue.push_back((nx, ny));
        }
    }
    let Some(_) = cell_index(grid, goal.0, goal.1).filter(|i| prev[*i].is_some()) else {
        return Vec::new();
    };
    let mut cells = Vec::new();
    let mut cursor = goal;
    cells.push(cursor);
    while cursor != start {
        let Some(i) = cell_index(grid, cursor.0, cursor.1) else {
            break;
        };
        let Some(parent) = prev[i] else {
            break;
        };
        if parent == cursor {
            break;
        }
        cursor = parent;
        cells.push(cursor);
    }
    cells.reverse();
    cells
        .into_iter()
        .map(|(x, y)| Vec3::new(x as f32 * grid.cell, 0.0, y as f32 * grid.cell))
        .collect()
}

fn plan_paths(
    grid: Res<WalkGrid>,
    mut agents: Query<(&Transform, Ref<GoalCell>, &mut AgentPath)>,
) {
    let grid_changed = grid.is_changed();
    for (tf, goal, mut path) in &mut agents {
        if !grid_changed && !goal.is_changed() {
            continue;
        }
        let start = (
            (tf.translation.x / grid.cell).floor() as i32,
            (tf.translation.z / grid.cell).floor() as i32,
        );
        path.waypoints = search(&grid, start, (goal.0, goal.1));
        path.index = 0;
    }
}

fn follow_paths(time: Res<Time<Fixed>>, mut agents: Query<(&mut Transform, &mut AgentPath)>) {
    let step = 4.0 * time.delta_secs();
    for (mut tf, mut path) in &mut agents {
        let Some(goal) = path.waypoints.get(path.index).copied() else {
            continue;
        };
        let delta = goal - tf.translation;
        let dist = delta.length();
        if dist <= step || dist == 0.0 {
            tf.translation = goal;
            path.index += 1;
        } else {
            tf.translation += delta / dist * step;
        }
    }
}

pub struct NavigationPlugin;

impl Plugin for NavigationPlugin {
    fn build(&self, app: &mut App) {
        let width = 8;
        let height = 8;
        app.insert_resource(WalkGrid {
            width,
            height,
            cell: 1.0,
            blocked: vec![false; (width * height) as usize],
        })
        .add_systems(Update, plan_paths)
        .add_systems(FixedUpdate, follow_paths);
    }
}
```

Mark a cell blocked and give an agent a goal. Planning runs again because the grid resource changed.

```rust
#[derive(Resource)]
struct WalkGrid {
    width: i32,
    height: i32,
    cell: f32,
    blocked: Vec<bool>,
}

#[derive(Component)]
struct GoalCell(i32, i32);

#[derive(Component)]
struct AgentPath {
    waypoints: Vec<Vec3>,
    index: usize,
}

fn block_cell(mut grid: ResMut<WalkGrid>) {
    let x = 2;
    let y = 3;
    let i = (y * grid.width + x) as usize;
    if let Some(cell) = grid.blocked.get_mut(i) {
        *cell = true;
    }
}

fn spawn_agent(mut commands: Commands) {
    commands.spawn((
        Transform::from_xyz(0.0, 0.0, 0.0),
        GoalCell(5, 5),
        AgentPath {
            waypoints: Vec::new(),
            index: 0,
        },
    ));
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
| Per-entity data | `Component` + `Query` | A field stored outside a component |
| App-wide config or clock | `Resource` | Copy the value onto every entity |
| Stable simulation step | `FixedMain` and the `Fixed` clock | Tie simulation to raw frame `Update` |
| Startup spawn | `Commands` in `Startup` | Spawn from a render system |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| A path over cells | `WalkGrid` plus breadth-first search | An engine navmesh type this crate does not ship |

Load [references/ecs-ownership.md](references/ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- No navigation types from another engine. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No named third-party navigation crate as the chosen solver. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No invented bake, avoidance, or path-query APIs. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

Official links stay on bevy.org. The library pin on bevy-master stays **0.20**. No navigation module was opened.

### Official Documentation
- [Assets](https://bevy.org/assets/) - Official asset catalog. No navigation plugin was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, `Query`, `Commands`, and `.chain()`.
- [Quick Start: plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `add_plugins` without a chosen nav crate.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - ECS ownership.
- [bevy-character-movement](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-character-movement/SKILL.md) - How an actor moves once a waypoint exists.

#### Complements
- [bevy-ai-navigation](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ai-navigation/SKILL.md) - Chase, patrol, and retarget policy. Not the mesh.

#### Downstream / consumers
- Genre skills route chase, patrol, and similar policies.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
