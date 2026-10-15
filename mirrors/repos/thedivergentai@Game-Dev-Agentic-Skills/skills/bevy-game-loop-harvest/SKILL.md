---
name: bevy-game-loop-harvest
description: "Bevy ECS harvest loop: Crop stage on Time<Fixed>, season scale, catch-up from a LastVisit resource, Harvested messages. Use when growth must finish before the yield message. Keywords: Bevy, harvest, crop, FixedUpdate, season, catch-up."
---

# Bevy harvest loop

## When to use

Load this when crops advance on a timer and a harvest message records the yield.

## ECS shape

- **Components:** growth elapsed and a stage index you define.
- **Resources:** the last visit and the season scale live in resources (bevy-data-resources).
- **Systems:** step growth on `FixedUpdate`. Use `.chain()` so harvest reads the stage growth just wrote.
- **Messages:** `Harvested` is the one-shot yield fact. Inventory applies it in bevy-inventory-system.

## Idioms

| Need | Bevy shape |
| --- | --- |
| Growth | Elapsed time on a component, stepped on the fixed clock. |
| Extract | A `Harvested` message. Inventory consumes it. |
| Season | A resource scale. No calendar type was opened. |

## Scope

- A crop component stores stage and elapsed time. Growth steps on `Time<Fixed>`.
- Offline catch-up reads `Time::elapsed_secs` against a resource that remembers the last visit.

## Examples

```toml
[package]
name = "harvest"
version = "0.1.0"
edition = "2021"

[dependencies]
bevy = "0.20"
```

Growth advances one stage per interval. Harvest only fires when the last stage is ready.

```rust
#[derive(Component)]
struct Crop {
    stage: u8,
    elapsed: f32,
    stage_seconds: f32,
    stages: u8,
}

#[derive(Message)]
struct Harvested {
    plot: Entity,
    yield_item: u32,
}

fn grow(time: Res<Time<Fixed>>, mut crops: Query<&mut Crop>) {
    let dt = time.delta_secs();
    for mut crop in &mut crops {
        if crop.stage + 1 >= crop.stages {
            continue;
        }
        crop.elapsed += dt;
        if crop.elapsed >= crop.stage_seconds {
            crop.elapsed = 0.0;
            crop.stage += 1;
        }
    }
}

fn harvest(
    mut commands: Commands,
    crops: Query<(Entity, &Crop)>,
    mut harvested: MessageWriter<Harvested>,
) {
    for (entity, crop) in &crops {
        if crop.stage + 1 < crop.stages {
            continue;
        }
        harvested.write(Harvested {
            plot: entity,
            yield_item: 7,
        });
        commands.entity(entity).despawn();
    }
}

pub struct HarvestPlugin;

impl Plugin for HarvestPlugin {
    fn build(&self, app: &mut App) {
        app.add_message::<Harvested>()
            .add_systems(FixedUpdate, (grow, harvest).chain());
    }
}
```

Catch-up applies the seconds since the last recorded visit, then stores the new mark.

```rust
#[derive(Component)]
struct Crop {
    stage: u8,
    elapsed: f32,
    stage_seconds: f32,
    stages: u8,
}

#[derive(Resource)]
struct LastVisit {
    elapsed_secs: f32,
}

fn catch_up(time: Res<Time>, mut last: ResMut<LastVisit>, mut crops: Query<&mut Crop>) {
    let now = time.elapsed_secs();
    let gap = (now - last.elapsed_secs).max(0.0);
    last.elapsed_secs = now;
    if gap <= 0.0 {
        return;
    }
    for mut crop in &mut crops {
        let mut left = gap;
        while left > 0.0 && crop.stage + 1 < crop.stages {
            let need = (crop.stage_seconds - crop.elapsed).max(0.0);
            if left < need {
                crop.elapsed += left;
                left = 0.0;
            } else {
                left -= need;
                crop.elapsed = 0.0;
                crop.stage += 1;
            }
        }
    }
}
```

A season resource scales how fast every crop in the run advances.

```rust
#[derive(Resource)]
struct Season {
    growth_scale: f32,
}

#[derive(Component)]
struct Crop {
    stage: u8,
    elapsed: f32,
    stage_seconds: f32,
    stages: u8,
}

fn season_grow(time: Res<Time<Fixed>>, season: Res<Season>, mut crops: Query<&mut Crop>) {
    let dt = time.delta_secs() * season.growth_scale.max(0.0);
    for mut crop in &mut crops {
        if crop.stage + 1 >= crop.stages {
            continue;
        }
        crop.elapsed += dt;
        if crop.elapsed >= crop.stage_seconds {
            crop.elapsed -= crop.stage_seconds;
            crop.stage += 1;
        }
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
| Per-entity data | `Component` + `Query` | A scene-tree script on the actor |
| App-wide config or clock | `Resource` | Copy the value onto every entity |
| Stable simulation step | `FixedMain` and the `Fixed` clock | Tie simulation to raw frame `Update` |
| Startup spawn | `Commands` in `Startup` | Spawn from a render system |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| An API outside the documented set | Read the official manual linked below | A made-up crate or API |

Load [references/ecs-ownership.md](references/ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- No scene-tree node or signal bus for this mechanic. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No invented APIs or unnamed third-party crates as the chosen solver. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

The library pin on bevy-master stays **0.20**.

### Official Documentation
- [Assets](https://bevy.org/assets/) - Official asset catalog. No third-party crate was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, systems, `Query`, `Startup`, `Update`, and `.chain()`.
- [Plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and `add_plugins`.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Components and systems.
- [bevy-inventory-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-inventory-system/SKILL.md) - Where the yield goes.
- [bevy-data-resources](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-data-resources/SKILL.md) - Tables and definitions.
- [bevy-events-messaging](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-events-messaging/SKILL.md) - One-shot facts.

#### Complements
- [bevy-state-machines](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-state-machines/SKILL.md) - Mode flags.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
