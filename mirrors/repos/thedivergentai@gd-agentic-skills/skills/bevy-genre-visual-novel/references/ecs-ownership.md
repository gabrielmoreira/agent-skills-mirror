# ECS ownership - bevy-genre-visual-novel

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
#[derive(Resource, Default)]
struct RouteFlags {
    names: Vec<String>,
}

fn remember(flag: &str, routes: &mut RouteFlags) {
    routes.names.push(flag.to_string());
}
```
