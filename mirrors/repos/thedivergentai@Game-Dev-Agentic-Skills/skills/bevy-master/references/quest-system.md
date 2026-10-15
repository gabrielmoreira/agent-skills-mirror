---
name: bevy-quest-system
description: "Track Bevy 0.20 quest definitions in a Resource and per-party progress in a Component, advanced by Messages. Use when objectives must change stage without inventing a quest crate. Keywords: Bevy, quest, objective, QuestProgress, Message, ECS."
---

# Bevy quest system

## When to use

Load this when objectives advance. Dialogue that grants them stays on bevy-dialogue-system.

## ECS shape

- **Components:** quest id and stage you define.
- **Resources:** run-wide tables live in a `Resource` (bevy-data-resources).
- **Systems:** mutate those components on `Update` or the fixed timestep. Use `.chain()` when damage must land before death.
- **Messages:** one-shot facts (hit, pickup, quest advance) go through bevy-events-messaging. This file does not add a new event type name.

## Where a quest lives

| Fact | Owner |
| --- | --- |
| Definition | Id plus objectives in `QuestCatalog`. |
| Objective count | A number incremented from a `Message`. |
| Complete | A stage change on `QuestProgress`. Rewards go through inventory or economy skills. |

## Scope

- A quest definition is a `Resource` table. Runtime progress is a `Component` on the party entity.
- One system writes stage changes. Completion grants stay as data another skill reads.

## Examples

```toml
[dependencies]
bevy = "0.20"
```

Definitions live in one resource. The party entity stores which quests are active and how far each objective has counted.

```rust
#[derive(Clone, Copy, PartialEq, Eq, Hash)]
struct QuestId(u32);

#[derive(Clone, Copy, PartialEq, Eq)]
enum QuestStage {
    Inactive,
    Active,
    Complete,
}

#[derive(Clone, Copy)]
struct ObjectiveDef {
    id: u32,
    required: u32,
}

struct QuestDef {
    id: QuestId,
    objectives: Vec<ObjectiveDef>,
}

#[derive(Resource)]
struct QuestCatalog {
    quests: Vec<QuestDef>,
}

#[derive(Clone, Copy)]
struct ObjectiveProgress {
    id: u32,
    count: u32,
}

#[derive(Component)]
struct QuestProgress {
    quest: QuestId,
    stage: QuestStage,
    objectives: Vec<ObjectiveProgress>,
}

fn accept(catalog: Res<QuestCatalog>, mut commands: Commands, party: Query<Entity, Without<QuestProgress>>) {
    let Some(def) = catalog.quests.first() else {
        return;
    };
    for entity in &party {
        commands.entity(entity).insert(QuestProgress {
            quest: def.id,
            stage: QuestStage::Active,
            objectives: def
                .objectives
                .iter()
                .map(|objective| ObjectiveProgress {
                    id: objective.id,
                    count: 0,
                })
                .collect(),
        });
    }
}
```

A pickup or kill is a message. The quest system is the only writer of `QuestProgress`.

```rust
#[derive(Clone, Copy, PartialEq, Eq)]
enum QuestStage {
    Active,
    Complete,
}

#[derive(Component)]
struct QuestProgress {
    stage: QuestStage,
    objective: u32,
    count: u32,
    required: u32,
}

#[derive(Message)]
struct ObjectiveFact {
    objective: u32,
}

fn apply_facts(mut facts: MessageReader<ObjectiveFact>, mut quests: Query<&mut QuestProgress>) {
    for fact in facts.read() {
        for mut quest in &mut quests {
            if quest.stage != QuestStage::Active || quest.objective != fact.objective {
                continue;
            }
            quest.count = (quest.count + 1).min(quest.required);
            if quest.count >= quest.required {
                quest.stage = QuestStage::Complete;
            }
        }
    }
}
```

Register the message, accept on startup, then apply facts. One system writes `QuestProgress`. A completed stage is the reward payload other skills read.

```rust
#[derive(Clone, Copy, PartialEq, Eq)]
enum QuestStage {
    Active,
    Complete,
}

#[derive(Component)]
struct QuestProgress {
    stage: QuestStage,
    objective: u32,
    count: u32,
    required: u32,
}

#[derive(Message)]
struct ObjectiveFact {
    objective: u32,
}

#[derive(Resource, Default)]
struct QuestCatalog;

fn accept(mut commands: Commands) {
    commands.spawn(QuestProgress {
        stage: QuestStage::Active,
        objective: 1,
        count: 0,
        required: 3,
    });
}

fn apply_facts(mut facts: MessageReader<ObjectiveFact>, mut quests: Query<&mut QuestProgress>) {
    for fact in facts.read() {
        for mut quest in &mut quests {
            if quest.stage != QuestStage::Active || quest.objective != fact.objective {
                continue;
            }
            quest.count = (quest.count + 1).min(quest.required);
            if quest.count >= quest.required {
                quest.stage = QuestStage::Complete;
            }
        }
    }
}

pub struct QuestPlugin;

impl Plugin for QuestPlugin {
    fn build(&self, app: &mut App) {
        app.init_resource::<QuestCatalog>()
            .add_message::<ObjectiveFact>()
            .add_systems(Startup, accept)
            .add_systems(Update, apply_facts);
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
| Quest definitions | `QuestCatalog` | Copying progress counts back into the catalog |
| Stage change | The one `Update` system that reads `MessageReader<ObjectiveFact>` | A dialogue system writing `QuestProgress` |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| An API outside the documented set | Check the official documentation | A made-up crate or API |

Load [references/ecs-ownership.md](quest-system-ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- Do not keep a second writer of `QuestProgress`. WHY: two mutable queries of the same component race unless `.chain()` orders them.
- Do not import another engine's node or signal types. WHY: quest stage is a component and a message, not a foreign object.
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
- [bevy-dialogue-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-dialogue-system/SKILL.md) - Lines that grant quests.
- [bevy-data-resources](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-data-resources/SKILL.md) - Tables and definitions.
- [bevy-events-messaging](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-events-messaging/SKILL.md) - One-shot facts.

#### Complements
- [bevy-state-machines](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-state-machines/SKILL.md) - Mode flags.
- [godot-quest-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/godot-quest-system/SKILL.md) - Godot package for quest tracking.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
