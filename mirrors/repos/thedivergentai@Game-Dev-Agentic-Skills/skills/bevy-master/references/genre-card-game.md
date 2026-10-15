---
name: bevy-genre-card-game
description: "Bevy card-game router: zones, turn resource, deck order, catalog costs, EndTurn and PlayCard messages. Use for a local hand, board, and seat order. Keywords: Bevy, card game, zone, turn, deck, energy, chain."
---

# Bevy card game

Genre router. Domain work lives in the Bevy skills below.

## When to use

Load this for a local card zone, hand, and turn order.

## ECS shape

- **Components** hold the genre's per-entity flags as plain data. This file does not name new engine types.
- **Resources** hold the turn index, energy, and the card catalog via bevy-data-resources.
- **Systems** read those components on `Update` or the fixed timestep from bevy-master. Order them with `.chain()` when a later system must see the result.
- **Schedule:** gameplay mode changes go through bevy-state-machines. Do not invent a genre plugin.

## Idioms

| Need | Bevy shape |
| --- | --- |
| Cards and zones | Entities with `Card` and `InZone` |
| Turn and catalog | Resources |
| End turn, draw, play | Messages consumed on one `.chain()` |

## Routing

- [bevy-turn-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-turn-system/SKILL.md) - Turns.
- [bevy-inventory-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-inventory-system/SKILL.md) - Zones as containers of card ids.
- [bevy-ui-layout](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ui-layout/SKILL.md) - Hand layout.
- [bevy-data-resources](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-data-resources/SKILL.md) - Card definitions.

## Scope

- A card is an entity. Its zone is a component. Turn index and the definition table are resources.
- Local play shuffles with `rand`. Online play stays on the networking skills.

## Examples

```toml
[package]
name = "cards"
version = "0.1.0"
edition = "2021"

[dependencies]
bevy = "0.20"
rand = "0.9"
```

Zones and the active seat are plain data. Ending a turn advances the seat, then draws one card into that seat's hand.

```rust
#[derive(Clone, Copy, PartialEq, Eq)]
enum ZoneKind {
    Deck,
    Hand,
    Board,
}

#[derive(Component)]
struct Card {
    def: u32,
}

#[derive(Component)]
struct InZone {
    owner: u8,
    kind: ZoneKind,
    order: u16,
}

#[derive(Resource)]
struct Turn {
    active: u8,
    players: u8,
}

#[derive(Message)]
struct EndTurn;

fn end_turn(mut turns: MessageReader<EndTurn>, mut turn: ResMut<Turn>) {
    for _end in turns.read() {
        turn.active = (turn.active + 1) % turn.players.max(1);
    }
}

fn draw_one(turn: Res<Turn>, mut ends: MessageReader<EndTurn>, mut cards: Query<(Entity, &mut InZone)>) {
    if ends.read().next().is_none() {
        return;
    }
    let mut next_order = 0u16;
    let mut pick: Option<Entity> = None;
    for (entity, zone) in &cards {
        if zone.owner != turn.active {
            continue;
        }
        if zone.kind == ZoneKind::Hand {
            next_order = next_order.max(zone.order.saturating_add(1));
        }
        if zone.kind == ZoneKind::Deck && pick.is_none() {
            pick = Some(entity);
        }
    }
    if let Some(entity) = pick {
        if let Ok((_entity, mut zone)) = cards.get_mut(entity) {
            zone.kind = ZoneKind::Hand;
            zone.order = next_order;
        }
    }
}

pub struct CardLoopPlugin;

impl Plugin for CardLoopPlugin {
    fn build(&self, app: &mut App) {
        app.insert_resource(Turn {
            active: 0,
            players: 2,
        })
        .add_message::<EndTurn>()
        .add_systems(Update, (end_turn, draw_one).chain());
    }
}
```

Shuffle writes a new deck order from `rand::rng`. Run it from `Startup` before the first draw.

```rust
use rand::seq::SliceRandom;

#[derive(Component)]
struct InZone {
    owner: u8,
    order: u16,
}

fn shuffle_deck(mut cards: Query<&mut InZone>) {
    let mut order: Vec<u16> = (0..cards.iter().count() as u16).collect();
    order.shuffle(&mut rand::rng());
    for (mut zone, index) in cards.iter_mut().zip(order) {
        zone.order = index;
    }
}
```

Definitions sit in one resource. The entity only stores the id.

```rust
#[derive(Clone, Copy, PartialEq, Eq)]
enum ZoneKind {
    Hand,
    Board,
}

#[derive(Component)]
struct InZone {
    kind: ZoneKind,
}

#[derive(Clone, Copy)]
struct CardDef {
    id: u32,
    cost: u8,
}

#[derive(Resource)]
struct CardCatalog {
    rows: Vec<CardDef>,
}

#[derive(Component)]
struct Card {
    def: u32,
}

fn cost_of(catalog: &CardCatalog, card: &Card) -> u8 {
    catalog
        .rows
        .iter()
        .find(|row| row.id == card.def)
        .map(|row| row.cost)
        .unwrap_or(0)
}

#[derive(Message)]
struct PlayCard {
    card: Entity,
}

fn play_card(
    mut plays: MessageReader<PlayCard>,
    catalog: Res<CardCatalog>,
    mut cards: Query<(&Card, &mut InZone)>,
    mut energy: ResMut<Energy>,
) {
    for play in plays.read() {
        let Ok((card, mut zone)) = cards.get_mut(play.card) else {
            continue;
        };
        if zone.kind != ZoneKind::Hand {
            continue;
        }
        let cost = cost_of(&catalog, card);
        if energy.left < cost {
            continue;
        }
        energy.left -= cost;
        zone.kind = ZoneKind::Board;
    }
}

#[derive(Resource)]
struct Energy {
    left: u8,
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

Load [references/ecs-ownership.md](genre-card-game-ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- No scene-tree node or signal bus in this router. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No invented genre APIs. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- Do not pick a physics or net crate here. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

The library pin on bevy-master stays **0.20**.

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
- [bevy-turn-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-turn-system/SKILL.md) - Turns.
- [bevy-inventory-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-inventory-system/SKILL.md) - Zones as containers of card ids.
- [bevy-ui-layout](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ui-layout/SKILL.md) - Hand layout.
- [bevy-data-resources](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-data-resources/SKILL.md) - Card definitions.

#### Downstream / consumers
- None. This router does not own a second implementation.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
