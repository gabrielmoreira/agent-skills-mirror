# ECS ownership - bevy-project-foundations

Who owns each piece of state, and on which schedule.

Target: **Bevy 0.20+**.

| Need | Owner | Schedule |
| --- | --- | --- |
| Per-entity | `Component` + `Query` | `Update` or `FixedMain` |
| App-wide | `Resource` | insert in `Startup` |
| Spawn | `Commands` | `Startup` or the runtime schedule |
| Ordered mutation | `.chain()` | same schedule |
| Plugin setup | `Plugin` `build` | before run |

The plugin inserts app-wide data in `build`. The startup system spawns the entity.

```rust
#[derive(Resource)]
struct GameConfig {
    title: String,
}

#[derive(Component)]
struct Player;

fn spawn_player(mut commands: Commands) {
    commands.spawn(Player);
}

pub struct FoundationsPlugin;

impl Plugin for FoundationsPlugin {
    fn build(&self, app: &mut App) {
        app.insert_resource(GameConfig {
            title: "Game".to_string(),
        })
        .add_systems(Startup, spawn_player);
    }
}
```
