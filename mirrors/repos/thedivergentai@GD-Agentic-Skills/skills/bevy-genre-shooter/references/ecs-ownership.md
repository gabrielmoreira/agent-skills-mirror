# ECS ownership - bevy-genre-shooter

Who owns each piece of state, and on which schedule.

Target: **Bevy 0.20+**.

| Need | Owner | Schedule |
| --- | --- | --- |
| Per-entity | `Component` + `Query` | `Update` or `FixedMain` |
| App-wide | `Resource` | insert in `Startup` |
| Spawn | `Commands` | `Startup` or the runtime schedule |
| Ordered mutation | `.chain()` | same schedule |
| Plugin setup | `Plugin` `build` | before run |

Projectiles are entities. The wave index is one resource.

```rust
#[derive(Component)]
struct Projectile {
    damage: i32,
}

#[derive(Resource)]
struct Wave {
    index: u32,
}

fn boot(mut commands: Commands) {
    commands.insert_resource(Wave { index: 1 });
    commands.spawn(Projectile { damage: 1 });
}
```
