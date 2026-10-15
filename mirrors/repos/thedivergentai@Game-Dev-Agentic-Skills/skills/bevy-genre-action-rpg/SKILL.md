---
name: bevy-genre-action-rpg
description: "Bevy 0.20 action-RPG router: real-time hits, stats, inventory, and quests as ECS joins, with domain work in the linked skills. Use when routing an action RPG. Keywords: Bevy, action RPG, hits, stamina, quests, ECS, router."
---

# Bevy Action RPG (thin router)

Genre router. Domain work lives in the Bevy skills below.

## When to use

Load this to route an action RPG: real-time hits, stats, inventory, and quests.

## ECS shape

- **Components** hold the genre's per-entity flags as plain data. This file does not name new engine types.
- **Resources** hold run-wide counters (score, wave index, seed) via bevy-data-resources.
- **Systems** read those components on `Update` or the fixed timestep from bevy-master. Order them with `.chain()` when a later system must see the result.
- **Schedule:** gameplay mode changes go through bevy-state-machines. Do not invent a genre plugin.

## Engine counterparts

| Godot idea | Bevy idiom |
| --- | --- |
| Genre scene tree | Entities plus the domain skills linked below |
| Autoload director | A resource, not a singleton node |
| Signal bus for the loop | bevy-events-messaging |

## Routing

- [bevy-character-movement](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-character-movement/SKILL.md) - Actor motion.
- [bevy-combat-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-combat-system/SKILL.md) - Hits.
- [bevy-rpg-stats](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-rpg-stats/SKILL.md) - Attributes.
- [bevy-inventory-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-inventory-system/SKILL.md) - Gear.
- [bevy-quest-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-quest-system/SKILL.md) - Objectives.
- [bevy-ability-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ability-system/SKILL.md) - Casts.

## Scope

This router shows the ECS joins an action RPG uses. Stats, hits, gear, and quests stay in the domain skills linked above. Hit volumes belong with the physics skills.

| Join | Owner | Schedule |
| --- | --- | --- |
| Incoming damage amount | Component on the actor, removed after it is applied | `Update`, apply then clear with `.chain()` |
| Reach and stamina | Components on the actor | Read by the ability skill; this router only spawns them |
| Slain count | One resource | `Update`, after the hit system |
| Gear id | Component on the actor | Inventory skill writes it; do not also write it from combat |

```toml
[dependencies]
bevy = "0.20"
```

```rust
#[derive(Component)]
struct Vitality {
    hp: i32,
    max_hp: i32,
}

#[derive(Component)]
struct IncomingHit {
    amount: i32,
}

fn apply_hits(mut actors: Query<(&mut Vitality, &IncomingHit)>) {
    for (mut vitality, hit) in &mut actors {
        vitality.hp = (vitality.hp - hit.amount).max(0);
    }
}

fn clear_hits(mut commands: Commands, hits: Query<Entity, With<IncomingHit>>) {
    for entity in &hits {
        commands.entity(entity).remove::<IncomingHit>();
    }
}

pub struct ActionHitPlugin;

impl Plugin for ActionHitPlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(Update, (apply_hits, clear_hits).chain());
    }
}
```

```rust
#[derive(Component)]
struct GearSlot {
    item_id: Option<u32>,
}

#[derive(Resource, Default)]
struct QuestFlags {
    slain: u32,
    need: u32,
}

fn equip(mut slots: Query<&mut GearSlot>) {
    for mut slot in &mut slots {
        if slot.item_id.is_none() {
            slot.item_id = Some(1);
        }
    }
}

fn note_kill(mut flags: ResMut<QuestFlags>) {
    if flags.slain < flags.need {
        flags.slain += 1;
    }
}

pub struct ActionProgressPlugin;

impl Plugin for ActionProgressPlugin {
    fn build(&self, app: &mut App) {
        app.insert_resource(QuestFlags { slain: 0, need: 3 })
            .add_systems(Update, (equip, note_kill));
    }
}
```

```rust
#[derive(Component)]
struct Actor;

#[derive(Component)]
struct MeleeReach(f32);

#[derive(Component)]
struct Stamina {
    current: f32,
    max: f32,
}

fn spawn_actor(mut commands: Commands) {
    commands.spawn((
        Actor,
        MeleeReach(1.5),
        Stamina {
            current: 100.0,
            max: 100.0,
        },
        Transform::default(),
    ));
}

pub struct ActionRpgPlugin;

impl Plugin for ActionRpgPlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(Startup, spawn_actor);
    }
}

fn main() {
    App::new()
        .add_plugins(MinimalPlugins)
        .add_plugins(ActionRpgPlugin)
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
| Per-entity data | `Component` + `Query` | A Godot node script |
| App-wide config or clock | `Resource` | Copy the value onto every entity |
| Stable simulation step | `FixedMain` and the `Fixed` clock | Tie simulation to raw frame `Update` |
| Startup spawn | `Commands` in `Startup` | Spawn from a render system |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| An API outside this skill | Load the skill that owns it | A made-up crate or API |

Load [references/ecs-ownership.md](references/ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not clear `IncomingHit` in parallel with the system that reads it. WHY: both mutably touch that component, so the clear must be `.chain()`ed after the apply.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- No Godot types in Bevy code. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No invented genre APIs. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- Do not pick a physics or net crate here. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

The library pin on bevy-master stays **0.20.0**. Official pages stay on the unversioned site.

### Official Documentation
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, systems, `Query`, `Startup`, `Update`, and `.chain()`.
- [Plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and `add_plugins`.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - ECS ownership and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Spawn and query shape.

#### Complements
- [godot-genre-action-rpg](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/godot-genre-action-rpg/SKILL.md) - Equivalent Godot skill.
- [bevy-character-movement](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-character-movement/SKILL.md) - Actor motion.
- [bevy-combat-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-combat-system/SKILL.md) - Hits.
- [bevy-rpg-stats](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-rpg-stats/SKILL.md) - Attributes.
- [bevy-inventory-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-inventory-system/SKILL.md) - Gear.
- [bevy-quest-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-quest-system/SKILL.md) - Objectives.
- [bevy-ability-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ability-system/SKILL.md) - Casts.

#### Downstream / consumers
- None. This router does not own a second implementation.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
