---
name: bevy-inventory-system
description: "Bevy ECS skill for inventories. Keywords: Bevy, inventory, stack, item, ECS."
---

# Bevy inventory system

## When to use

Load this when stacks move between containers. UI grids stay on bevy-ui-layout. Economy prices stay on bevy-economy-system.

## ECS shape

- **Components:** item id and stack count you define.
- **Resources:** run-wide tables live in a resource (bevy-data-resources).
- **Systems:** mutate those components on `Update` or the fixed timestep. Use `.chain()` when damage must land before death.
- **Messages:** one-shot facts (hit, pickup, quest advance) go through bevy-events-messaging. This file does not add a new event type name.

## Ownership

| Need | Bevy shape |
| --- | --- |
| Stack | Item id plus count on a component or inside a resource inventory |
| Container | An entity that owns stacks |
| Equip | A marker component. Stat changes go through bevy-rpg-stats |

## Scope

- Item ids, stack counts, and containers are components. A move request is a message so one system writes both bags.
- Slot widgets stay on bevy-ui-layout. Prices stay on bevy-economy-system.

## Examples

```toml
[package]
name = "inventory"
version = "0.1.0"
edition = "2021"

[dependencies]
bevy = "0.20"
```

Stacks live on the container entity. Moves are messages so a single query mutably borrows both bags.

```rust
#[derive(Clone, Copy, PartialEq, Eq)]
struct ItemId(u32);

#[derive(Clone, Copy)]
struct Stack {
    item: ItemId,
    count: u32,
}

#[derive(Component, Default)]
struct Inventory {
    slots: Vec<Stack>,
}

#[derive(Message)]
struct MoveStack {
    from: Entity,
    to: Entity,
    slot: usize,
    count: u32,
}

fn add_stack(inv: &mut Inventory, item: ItemId, mut count: u32) {
    for stack in &mut inv.slots {
        if stack.item == item {
            stack.count += count;
            return;
        }
    }
    if count > 0 {
        inv.slots.push(Stack { item, count });
    }
}

fn transfer(mut requests: MessageReader<MoveStack>, mut bags: Query<&mut Inventory>) {
    for req in requests.read() {
        if req.from == req.to || req.count == 0 {
            continue;
        }
        let Ok([mut from, mut to]) = bags.get_many_mut([req.from, req.to]) else {
            continue;
        };
        let Some(stack) = from.slots.get_mut(req.slot) else {
            continue;
        };
        if stack.count < req.count {
            continue;
        }
        let item = stack.item;
        stack.count -= req.count;
        let moved = req.count;
        if stack.count == 0 {
            from.slots.remove(req.slot);
        }
        add_stack(&mut to, item, moved);
    }
}

pub struct InventoryPlugin;

impl Plugin for InventoryPlugin {
    fn build(&self, app: &mut App) {
        app.add_message::<MoveStack>()
            .add_systems(Update, transfer);
    }
}
```

Equip copies a stack onto a marker and leaves the remainder in the bag. Stat changes stay on bevy-rpg-stats.

```rust
#[derive(Clone, Copy, PartialEq, Eq)]
struct ItemId(u32);

#[derive(Component)]
struct Equipped {
    item: ItemId,
}

#[derive(Component, Default)]
struct Inventory {
    slots: Vec<(ItemId, u32)>,
}

fn equip_first(mut commands: Commands, actors: Query<(Entity, &Inventory), Without<Equipped>>) {
    for (entity, bag) in &actors {
        let Some((item, count)) = bag.slots.first().copied() else {
            continue;
        };
        if count == 0 {
            continue;
        }
        commands.entity(entity).insert(Equipped { item });
    }
}
```

Spawn a chest and a player bag with a starter stack.

```rust
#[derive(Clone, Copy, PartialEq, Eq)]
struct ItemId(u32);

#[derive(Clone, Copy)]
struct Stack {
    item: ItemId,
    count: u32,
}

#[derive(Component)]
struct Inventory {
    slots: Vec<Stack>,
}

fn spawn_bags(mut commands: Commands) {
    commands.spawn(Inventory {
        slots: vec![Stack {
            item: ItemId(1),
            count: 8,
        }],
    });
    commands.spawn(Inventory { slots: Vec::new() });
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
| Stacks and moves | `Inventory` plus a `MoveStack` message | Two systems each writing one bag |

Load [references/ecs-ownership.md](inventory-system-ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- No types from another engine in Bevy code. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No invented APIs or unnamed third-party crates as the chosen solver. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

Official links stay on bevy.org. The library pin on bevy-master stays **0.20**.

### Official Documentation
- [Assets](https://bevy.org/assets/) - Official asset catalog. No third-party crate was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, systems, `Query`, `Startup`, `Update`, and `.chain()`.
- [Plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and `add_plugins`.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Components and systems.
- [bevy-rpg-stats](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-rpg-stats/SKILL.md) - Equip bonuses.
- [bevy-ui-layout](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ui-layout/SKILL.md) - Slot layout.
- [bevy-data-resources](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-data-resources/SKILL.md) - Tables and definitions.
- [bevy-events-messaging](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-events-messaging/SKILL.md) - One-shot facts.

#### Complements
- [bevy-state-machines](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-state-machines/SKILL.md) - Mode flags.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
