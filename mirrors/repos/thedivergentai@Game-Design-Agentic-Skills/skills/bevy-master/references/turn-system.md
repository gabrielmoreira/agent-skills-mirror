---
name: bevy-turn-system
description: "Run Bevy 0.20 turns with initiative on components and the active entity plus round on one resource. Use when play steps by turn instead of every frame. Keywords: Bevy, turns, initiative, TurnClock, chain, ECS."
---

# Bevy turn system

## When to use

Load this when play advances in turns rather than continuous time. Time still exists; you choose not to step the simulation every frame.

## ECS shape

- **Components:** initiative and the active entity id you define.
- **Resources:** the active entity and the round live in one `Resource` (bevy-data-resources).
- **Systems:** mutate those components on `Update` or the fixed timestep. Use `.chain()` when damage must land before death.
- **Messages:** one-shot facts (hit, pickup, quest advance) go through bevy-events-messaging. This file does not add a new event type name.

## Turn ownership

| Fact | Owner |
| --- | --- |
| Initiative | A component number, sorted when the round opens. |
| Active actor | `TurnClock.order[index]`. |
| Round | A counter on that same resource. Advance it in the chained end system. |

## Scope

- Initiative is a component. The active entity and the round counter are one resource so a single system advances them.
- Rebuild the queue when a round starts or when a speed stat changes. Do not sort again on every action.
- `bevy::state` is for app modes, not an initiative queue. See bevy-state-machines.

## Examples

```toml
[dependencies]
bevy = "0.20"
```

Each fighter stores speed and action points. The clock names who is active.

```rust
#[derive(Component)]
struct Fighter {
    speed: i32,
    tie_break: u32,
    action_points: u32,
}

#[derive(Resource)]
struct TurnClock {
    round: u32,
    order: Vec<Entity>,
    index: usize,
}

fn spawn_match(mut commands: Commands) {
    let a = commands
        .spawn(Fighter {
            speed: 12,
            tie_break: 0,
            action_points: 2,
        })
        .id();
    let b = commands
        .spawn(Fighter {
            speed: 12,
            tie_break: 1,
            action_points: 2,
        })
        .id();
    commands.insert_resource(TurnClock {
        round: 1,
        order: vec![a, b],
        index: 0,
    });
}
```

Sort once. Equal speed falls through to a stable id so replays stay deterministic.

```rust
#[derive(Component, Clone, Copy)]
struct Fighter {
    speed: i32,
    tie_break: u32,
}

#[derive(Resource)]
struct TurnClock {
    order: Vec<Entity>,
}

fn build_order(mut clock: ResMut<TurnClock>, fighters: Query<(Entity, &Fighter)>) {
    let mut rows: Vec<_> = fighters.iter().collect();
    rows.sort_by(|left, right| {
        right
            .1
            .speed
            .cmp(&left.1.speed)
            .then(left.1.tie_break.cmp(&right.1.tie_break))
    });
    clock.order = rows.into_iter().map(|(entity, _)| entity).collect();
}
```

Spend points only after the cost check. `take_action` sets `end_requested`. `end_turn` refills points and advances the index only when that flag is set. Both systems mutably use `TurnClock` and `Fighter`, so `.chain()` is required or the flag and the points race.

```rust
#[derive(Component)]
struct Fighter {
    action_points: u32,
}

#[derive(Resource)]
struct TurnClock {
    order: Vec<Entity>,
    index: usize,
    round: u32,
    end_requested: bool,
}

fn spend(cost: u32, fighter: &mut Fighter) -> bool {
    if fighter.action_points < cost {
        return false;
    }
    fighter.action_points -= cost;
    true
}

fn take_action(mut clock: ResMut<TurnClock>, mut fighters: Query<&mut Fighter>) {
    if clock.end_requested {
        return;
    }
    let Some(&current) = clock.order.get(clock.index) else {
        return;
    };
    let Ok(mut fighter) = fighters.get_mut(current) else {
        return;
    };
    if spend(1, &mut fighter) {
        clock.end_requested = true;
    }
}

fn end_turn(mut clock: ResMut<TurnClock>, mut fighters: Query<&mut Fighter>) {
    if !clock.end_requested || clock.order.is_empty() {
        return;
    }
    let Some(&current) = clock.order.get(clock.index) else {
        return;
    };
    if let Ok(mut fighter) = fighters.get_mut(current) {
        fighter.action_points = 2;
    }
    clock.end_requested = false;
    clock.index += 1;
    if clock.index >= clock.order.len() {
        clock.index = 0;
        clock.round += 1;
    }
}

pub struct TurnPlugin;

impl Plugin for TurnPlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(Update, (take_action, end_turn).chain());
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
| Per-entity data | `Component` + `Query` | A field stored outside the world |
| App-wide config or clock | `Resource` | Copy the value onto every entity |
| Stable simulation step | `FixedMain` and the `Fixed` clock | Tie simulation to raw frame `Update` |
| Startup spawn | `Commands` in `Startup` | Spawn from a render system |
| Initiative queue | `TurnClock` order built when the round opens | `States` or a sort on every action |
| Spend then end | `take_action` then `end_turn` with `.chain()` | Two unordered systems writing `Fighter` and `TurnClock` |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| An API outside the documented set | Check the official documentation | A made-up crate or API |

Load [references/ecs-ownership.md](turn-system-ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- Do not sort initiative on every action. WHY: the queue is rebuilt when a round opens or a speed stat changes, so replays stay stable.
- Do not use `bevy::state` as the initiative queue. WHY: states are app modes; the active entity is `TurnClock`.
- No invented APIs or unnamed third-party crates as the chosen solver. WHY: this skill only names documented Bevy crates and modules.

## Reference

Official links stay on unversioned `latest` pages. The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- [Assets](https://bevy.org/assets/) - Official asset catalog. No third-party crate was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, systems, `Query`, `Startup`, `Update`, and `.chain()`.
- [Plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and `add_plugins`.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Components and systems.
- [bevy-state-machines](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-state-machines/SKILL.md) - App mode is not turn order.
- [bevy-data-resources](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-data-resources/SKILL.md) - Tables and definitions.
- [bevy-events-messaging](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-events-messaging/SKILL.md) - One-shot facts.

#### Complements
- [bevy-state-machines](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-state-machines/SKILL.md) - Mode flags.
- [godot-turn-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/godot-turn-system/SKILL.md) - Godot package for turn order.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
