# ECS ownership - bevy-genre-platformer

Who owns each piece of state, and on which schedule.

Target: **Bevy 0.20+**.

| Need | Owner | Schedule |
| --- | --- | --- |
| Per-entity | `Component` + `Query` | `Update` or `FixedMain` |
| App-wide | `Resource` | insert in `Startup` |
| Spawn | `Commands` | `Startup` or the runtime schedule |
| Ordered mutation | `.chain()` | same schedule |
| Plugin setup | `Plugin` `build` | before run |

Coyote time is per-entity data. The follow camera reads `Transform` and writes only the camera.

```rust
#[derive(Component)]
struct Mover {
    coyote: f32,
    grounded: bool,
}

fn refill(mut movers: Query<&mut Mover>) {
    for mut mover in &mut movers {
        if mover.grounded {
            mover.coyote = 0.12;
        }
    }
}
```
