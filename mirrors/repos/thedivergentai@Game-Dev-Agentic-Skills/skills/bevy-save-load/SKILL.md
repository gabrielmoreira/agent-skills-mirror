---
name: bevy-save-load
description: "Persists a versioned Bevy Resource as RON when a SaveRequest exists. Use for player slots; scene spawn stays on bevy-asset-scenes. Keywords: Bevy, save, load, RON, serde, Resource, SaveRequest."
---

# Bevy save and load

## When to use

Load this when a design asks to persist player progress. Route asset and scene spawning to `bevy-asset-scenes`. Keep save bytes as data you serialize yourself until a current docs page names a format.

## ECS shape

- **What exists:** app-wide progress is a `Resource` you serialize yourself. Level content loads through `AssetServer` and scene spawn (`bevy-asset-scenes`). A scene spawn is not a player slot.
- **Format:** progress structs use `serde` and RON. The file holds primitives and a `version` field. Entity ids and asset handles stay out of the file.
- **Schedule:** write the slot from an explicit request system. Do not write the file from every `Update` frame.

`serde` and `ron` sit beside Bevy. The progress type is a normal resource.

```toml
[dependencies]
bevy = "0.20"
serde = { version = "1", features = ["derive"] }
ron = "0.10"
```

```rust
use serde::{Deserialize, Serialize};

#[derive(Resource, Clone, Serialize, Deserialize)]
struct Progress {
    version: u32,
    coins: u32,
    level: String,
}

fn fresh_progress() -> Progress {
    Progress {
        version: 2,
        coins: 0,
        level: "town".to_string(),
    }
}
```

Encode and decode are plain functions. Call them from the request system, not from a per-frame query.

```rust
use serde::{Deserialize, Serialize};

#[derive(Clone, Serialize, Deserialize)]
struct Progress {
    version: u32,
    coins: u32,
    level: String,
}

fn encode_slot(progress: &Progress) -> String {
    ron::ser::to_string_pretty(progress, ron::ser::PrettyConfig::default())
        .expect("progress encodes")
}

fn decode_slot(text: &str) -> Progress {
    ron::from_str(text).expect("progress decodes")
}

fn round_trip() {
    let saved = Progress {
        version: 2,
        coins: 4,
        level: "town".to_string(),
    };
    let loaded = decode_slot(&encode_slot(&saved));
    assert_eq!(loaded.coins, 4);
}
```

Older files omit `version`. Migration builds the current struct before anything inserts it.

```rust
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
struct SaveV1 {
    coins: u32,
}

#[derive(Resource, Clone, Serialize, Deserialize)]
struct Progress {
    version: u32,
    coins: u32,
}

fn load_any(text: &str) -> Progress {
    if let Ok(current) = ron::from_str::<Progress>(text) {
        return current;
    }
    let legacy: SaveV1 = ron::from_str(text).expect("legacy slot");
    Progress {
        version: 2,
        coins: legacy.coins,
    }
}
```

The save system runs only while `SaveRequest` is present, then removes it. One system owns the resource and the disk write.

```rust
use serde::{Deserialize, Serialize};

#[derive(Resource, Clone, Serialize, Deserialize)]
struct Progress {
    version: u32,
    coins: u32,
}

#[derive(Resource)]
struct SaveRequest {
    path: String,
}

fn write_slot(progress: Res<Progress>, request: Res<SaveRequest>) -> std::io::Result<()> {
    let text = ron::ser::to_string(&*progress).expect("progress encodes");
    std::fs::write(&request.path, text)
}

fn save_when_asked(mut commands: Commands, progress: Res<Progress>, request: Option<Res<SaveRequest>>) {
    let Some(request) = request else {
        return;
    };
    let _ = write_slot(progress, request);
    commands.remove_resource::<SaveRequest>();
}

pub struct SavePlugin;

impl Plugin for SavePlugin {
    fn build(&self, app: &mut App) {
        app.insert_resource(Progress {
            version: 2,
            coins: 0,
        })
        .add_systems(Update, save_when_asked);
    }
}
```

## What to persist

| Need | Bevy idiom |
| --- | --- |
| Designer content | An asset `Handle`, or a `Resource` you own in code |
| Level instance | `Scene` spawn on `bevy-asset-scenes` |
| Player save slot | A versioned `Resource` written as RON when a `SaveRequest` exists |

## Scope

- The slot path, version field, and RON text live on `Progress` and `SaveRequest` above.
- Scene spawn is not a save game. Do not treat `bsn!` as a user save.
- A native `std::fs` write is the desktop slot. Web builds need a different storage story. Do not call `std::fs` and assume a browser has that path.

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
| Per-entity data | `Component` + `Query` | A free-floating struct outside the `World` |
| App-wide config or clock | `Resource` | Copy the value onto every entity |
| Stable simulation step | `FixedMain` and the `Fixed` clock | Tie simulation to raw frame `Update` |
| Startup spawn | `Commands` in `Startup` | Spawn from a render system |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| An API outside the documented set | Check the official docs first | A made-up crate or API |

Load [references/ecs-ownership.md](references/ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- No engine config-file types in the slot. WHY: the slot is a versioned `Resource` encoded as RON.
- No `DynamicScene` or scene-file writer this file does not list. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No third-party save crates. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

The library pin on bevy-master stays **0.20**. Scene spawn is not a save format.

### Official Documentation
- [Resources](https://bevy.org/learn/quick-start/getting-started/resources/)  -  App-wide data the slot serializes.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples)  -  Example tree on the `latest` branch. Scene spawn lives with `bevy-asset-scenes`.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  Who owns which piece of state.
- [bevy-data-resources](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-data-resources/SKILL.md)  -  `Resource` versus `Component`.
- [bevy-asset-scenes](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-asset-scenes/SKILL.md)  -  Loading content. Not a save slot.

#### Downstream / consumers
- None until a save format is opened.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  Bevy router.
