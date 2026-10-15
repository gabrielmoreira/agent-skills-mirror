# ECS ownership - bevy-mechanic-revival

Who owns each piece of state, and on which schedule.

Target: **Bevy 0.20+**.

| Need | Owner | Schedule |
| --- | --- | --- |
| Per-entity | `Component` + `Query` | `Update` or `FixedMain` |
| App-wide | `Resource` | insert in `Startup` |
| Spawn | `Commands` | `Startup` or the runtime schedule |
| Ordered mutation | `.chain()` | same schedule |
| Plugin setup | `Plugin` `build` | before run |

```rust
#[derive(Component)]
struct Bleed {
    seconds: f32,
}

fn age(time: Res<Time>, mut bleeds: Query<&mut Bleed>) {
    let dt = time.delta_secs();
    for mut bleed in &mut bleeds {
        bleed.seconds += dt;
    }
}
```
