---
name: bevy-game-loop-collection
description: "Bevy 0.20 collection loop: pickup markers, a quota resource, one score per entity per pass, and NextState when the quota is met. Use when the run is about collecting objects. Keywords: Bevy, collection, pickup, quota, NextState, ECS."
---

# Bevy collection loop

## When to use

Load this when the run is about picking up objects and reaching a count.

## ECS shape

- **Components:** a collected flag and a quota resource you define.
- **Resources:** run-wide tables live in a resource (bevy-data-resources), not an autoload.
- **Systems:** mutate those components on `Update` or the fixed timestep. Use `.chain()` when damage must land before death.
- **Messages:** one-shot facts (hit, pickup, quest advance) go through bevy-events-messaging. This file does not add a new event type name.

## Engine counterparts

| Godot idea | Bevy idiom |
| --- | --- |
| Pickup | A component marker. Detection waits on spatial queries. |
| Quota | A resource count. |
| Win | A state change via bevy-state-machines. |

## Scope

A collectible is a marker component. Overlap is a distance check you own until a physics skill supplies contacts. Mark each entity once per pass: `Commands::despawn` applies later, so a second collector would otherwise score the same pickup. The quota is a resource. Reaching it writes `NextState`, which the state schedule applies after this system.

```toml
[dependencies]
bevy = "0.20"
```

```rust
#[derive(Component)]
struct Collectible {
    points: u32,
}

#[derive(Component)]
struct Collector;

#[derive(Resource)]
struct CollectionScore {
    points: u32,
    quota: u32,
}

#[derive(States, Debug, Clone, Copy, PartialEq, Eq, Hash, Default)]
enum RunState {
    #[default]
    Playing,
    Won,
}

fn collect_by_distance(
    mut commands: Commands,
    mut score: ResMut<CollectionScore>,
    collectors: Query<&Transform, With<Collector>>,
    pickups: Query<(Entity, &Transform, &Collectible)>,
) {
    let mut taken = std::collections::HashSet::new();
    for collector in &collectors {
        for (entity, transform, item) in &pickups {
            if taken.contains(&entity) {
                continue;
            }
            let distance = collector.translation.distance(transform.translation);
            if distance <= 1.0 {
                taken.insert(entity);
                score.points += item.points;
                commands.entity(entity).despawn();
            }
        }
    }
}

fn reach_quota(score: Res<CollectionScore>, mut next: ResMut<NextState<RunState>>) {
    if score.points >= score.quota {
        next.set(RunState::Won);
    }
}

fn spawn_pickups(mut commands: Commands) {
    commands.insert_resource(CollectionScore {
        points: 0,
        quota: 3,
    });
    commands.spawn((Collector, Transform::default()));
    for index in 0..3 {
        commands.spawn((
            Collectible { points: 1 },
            Transform::from_xyz(index as f32, 0.0, 0.0),
        ));
    }
}

pub struct CollectionPlugin;

impl Plugin for CollectionPlugin {
    fn build(&self, app: &mut App) {
        app.init_state::<RunState>()
            .add_systems(Startup, spawn_pickups)
            .add_systems(Update, (collect_by_distance, reach_quota).chain());
    }
}
```

```rust
#[derive(Component)]
struct Remaining(u32);

#[derive(Resource, Default)]
struct Quota {
    collected: u32,
    need: u32,
}

fn tally(mut quota: ResMut<Quota>, mut counters: Query<&mut Remaining>) {
    for mut remaining in &mut counters {
        if remaining.0 > 0 {
            remaining.0 -= 1;
            quota.collected += 1;
        }
    }
}

fn quota_met(quota: Res<Quota>) -> bool {
    quota.collected >= quota.need && quota.need > 0
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
| Per-entity data | `Component` + `Query` | A Godot node script |
| App-wide config or clock | `Resource` | Copy the value onto every entity |
| Stable simulation step | `FixedMain` and the `Fixed` clock | Tie simulation to raw frame `Update` |
| Startup spawn | `Commands` in `Startup` | Spawn from a render system |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| An API outside this skill | Load the skill that owns it | A made-up crate or API |

Load [references/ecs-ownership.md](game-loop-collection-ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not treat `NextState::set` as already applied in the same system. WHY: the state schedule performs the transition after this system returns.
- Do not score a pickup from two collectors in one pass. WHY: `despawn` is deferred, so the entity is still in the query.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- No Godot node, resource, or signal types for this mechanic. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

- No Godot types in Bevy code. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No invented APIs or unnamed third-party crates as the chosen solver. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

The library pin on bevy-master stays **0.20.0**. Official pages stay on the unversioned site.

### Official Documentation
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, systems, `Query`, `Startup`, `Update`, and `.chain()`.
- [States](https://bevy.org/learn/quick-start/getting-started/ecs/) - `States`, `NextState`, and `init_state` on the same ECS schedule page.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Components and systems.
- [bevy-state-machines](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-state-machines/SKILL.md) - Win and lose states.
- [bevy-data-resources](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-data-resources/SKILL.md) - Tables and definitions.
- [bevy-events-messaging](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-events-messaging/SKILL.md) - One-shot facts.

#### Complements
- [bevy-state-machines](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-state-machines/SKILL.md) - Mode flags.
- [godot-game-loop-collection](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/godot-game-loop-collection/SKILL.md) - Equivalent Godot skill.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
