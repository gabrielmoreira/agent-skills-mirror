# ECS ownership - bevy-genre-roguelike

Who owns each piece of state, and on which schedule.

Target: **Bevy 0.20+**.

| Need | Owner | Schedule |
| --- | --- | --- |
| Per-entity | `Component` + `Query` | `Update` or `FixedMain` |
| App-wide | `Resource` | insert in `Startup` |
| Spawn | `Commands` | `Startup` or the runtime schedule |
| Ordered mutation | `.chain()` | same schedule |
| Plugin setup | `Plugin` `build` | before run |

The seed is app-wide. Each room is an entity spawned once at startup.

```rust
#[derive(Resource)]
struct RunSeed(u64);

#[derive(Component)]
struct Room;

fn boot(mut commands: Commands) {
    commands.insert_resource(RunSeed(1));
    commands.spawn(Room);
}
```
