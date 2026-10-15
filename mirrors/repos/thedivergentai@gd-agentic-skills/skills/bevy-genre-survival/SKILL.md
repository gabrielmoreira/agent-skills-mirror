---
name: bevy-genre-survival
description: "Bevy ECS skill for survival loops. Keywords: Bevy, survival, hunger, warmth, day clock, crafting, ECS."
---

# Bevy survival

Vitals, a day clock, and crafting inputs live on components and resources. Stats, item stacks, gathering, and camps stay on the skills linked below.

## When to use

Load this for vitals, crafting inputs, and a day clock you own.

## ECS shape

- **Components** hold the genre's per-entity flags as plain data. This file does not name new engine types.
- **Resources** hold run-wide counters (score, wave index, seed) via bevy-data-resources.
- **Systems** read those components on `Update` or the fixed timestep from bevy-master. Order them with `.chain()` when a later system must see the result.
- **Schedule:** gameplay mode changes go through bevy-state-machines. Do not invent a genre plugin.

## Ownership

| Need | Bevy shape |
| --- | --- |
| Actors in the genre | Entities plus the domain skills linked below |
| Run-wide director | A resource |
| Loop notices | bevy-events-messaging |

## Routing

- [bevy-rpg-stats](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-rpg-stats/SKILL.md) - Vitals as stats.
- [bevy-inventory-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-inventory-system/SKILL.md) - Items.
- [bevy-game-loop-harvest](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-game-loop-harvest/SKILL.md) - Gathering.
- [bevy-3d-world-building](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-3d-world-building/SKILL.md) - Camps.

## Scope

- Hunger, warmth, and the day clock are data you own. Item stacks and camp layout stay on the linked skills.

## Examples

```toml
[package]
name = "survival"
version = "0.1.0"
edition = "2021"

[dependencies]
bevy = "0.20"
```

Hunger and warmth drain on the fixed step. Cold hours drain warmth faster. A meal and a fire restore them.

```rust
#[derive(Component)]
struct Vitals {
    hunger: f32,
    warmth: f32,
}

#[derive(Resource)]
struct DayClock {
    hour: f32,
    hours_per_day: f32,
}

fn tick_day(time: Res<Time<Fixed>>, mut clock: ResMut<DayClock>) {
    let hours = time.delta_secs() * (24.0 / clock.hours_per_day);
    clock.hour = (clock.hour + hours) % 24.0;
}

fn drain_vitals(time: Res<Time<Fixed>>, clock: Res<DayClock>, mut people: Query<&mut Vitals>) {
    let dt = time.delta_secs();
    let night = clock.hour < 6.0 || clock.hour >= 20.0;
    let warmth_rate = if night { 2.5 } else { 0.4 };
    for mut vitals in &mut people {
        vitals.hunger = (vitals.hunger - 1.2 * dt).max(0.0);
        vitals.warmth = (vitals.warmth - warmth_rate * dt).max(0.0);
    }
}

#[derive(Message)]
struct Eat {
    who: Entity,
    amount: f32,
}

fn apply_meals(mut meals: MessageReader<Eat>, mut people: Query<&mut Vitals>) {
    for meal in meals.read() {
        let Ok(mut vitals) = people.get_mut(meal.who) else {
            continue;
        };
        vitals.hunger = (vitals.hunger + meal.amount).min(100.0);
    }
}

pub struct SurvivalPlugin;

impl Plugin for SurvivalPlugin {
    fn build(&self, app: &mut App) {
        app.insert_resource(DayClock {
            hour: 8.0,
            hours_per_day: 480.0,
        })
        .add_message::<Eat>()
        .add_systems(FixedUpdate, (tick_day, drain_vitals, apply_meals).chain());
    }
}
```

A recipe spends named counts from a bag, then writes a crafted stack. The bag is a component so each camp or player carries their own stores.

```rust
#[derive(Clone, Copy, PartialEq, Eq)]
enum ItemKind {
    Wood,
    Fiber,
    Bandage,
}

#[derive(Component, Default)]
struct Bag {
    stacks: Vec<(ItemKind, u32)>,
}

fn count_of(bag: &Bag, kind: ItemKind) -> u32 {
    bag.stacks
        .iter()
        .filter(|(k, _)| *k == kind)
        .map(|(_, n)| *n)
        .sum()
}

fn spend(bag: &mut Bag, kind: ItemKind, mut need: u32) -> bool {
    if count_of(bag, kind) < need {
        return false;
    }
    for (k, n) in &mut bag.stacks {
        if *k != kind || need == 0 {
            continue;
        }
        let take = (*n).min(need);
        *n -= take;
        need -= take;
    }
    bag.stacks.retain(|(_, n)| *n > 0);
    true
}

fn craft_bandage(mut bags: Query<&mut Bag>) {
    for mut bag in &mut bags {
        if spend(&mut bag, ItemKind::Fiber, 2) {
            bag.stacks.push((ItemKind::Bandage, 1));
        }
    }
}
```

Spawn a survivor at dawn with full vitals.

```rust
#[derive(Component)]
struct Vitals {
    hunger: f32,
    warmth: f32,
}

fn spawn_survivor(mut commands: Commands) {
    commands.spawn((
        Vitals {
            hunger: 100.0,
            warmth: 100.0,
        },
        Transform::from_xyz(0.0, 0.0, 0.0),
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
| Hunger, warmth, clock, recipes | Components and resources in the examples | An engine survival module |

Load [references/ecs-ownership.md](references/ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- No types from another engine in Bevy code. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No invented genre APIs. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- Do not pick a physics or net crate here. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

Official links stay on bevy.org. The library pin on bevy-master stays **0.20**.

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
- [bevy-rpg-stats](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-rpg-stats/SKILL.md) - Vitals as stats.
- [bevy-inventory-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-inventory-system/SKILL.md) - Items.
- [bevy-game-loop-harvest](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-game-loop-harvest/SKILL.md) - Gathering.
- [bevy-3d-world-building](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-3d-world-building/SKILL.md) - Camps.

#### Downstream / consumers
- None. This router does not own a second implementation.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
