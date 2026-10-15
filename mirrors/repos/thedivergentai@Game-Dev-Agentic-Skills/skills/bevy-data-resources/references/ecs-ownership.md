# ECS ownership - bevy-data-resources

Who owns each piece of state, and on which schedule.

Target: **Bevy 0.20+**.

| Need | Owner | Schedule |
| --- | --- | --- |
| Per-entity | `Component` + `Query` | `Update` or `FixedMain` |
| App-wide | `Resource` | insert in `Startup` |
| Spawn | `Commands` | `Startup` or the runtime schedule |
| Ordered mutation | `.chain()` | same schedule |
| Plugin setup | `Plugin` `build` | before run |

Multiply a stored base by `SpeedScale` when you write `Speed`. Writing `speed *= scale` every `Update` compounds. `insert_resource` on the `App` is for values known at plugin build. `Commands::insert_resource` is for values known only after `Startup` work such as `AssetServer::load`. Do not invent crates or types.
