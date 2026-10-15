# ECS ownership - bevy-ecs-composition

Who owns each piece of state, and on which schedule.

Target: **Bevy 0.20+**.

| Need | Owner | Schedule |
| --- | --- | --- |
| Per-entity | `Component` + `Query` | `Update` or `FixedMain` |
| App-wide | `Resource` | insert in `Startup` |
| Spawn | `Commands` | `Startup` or the runtime schedule |
| Ordered mutation | `.chain()` | same schedule |
| Plugin setup | `Plugin` `build` | before run |

A system that writes `Name` and a system that reads the new value share one `.chain()`. A system that only reads `Name` and does not depend on that write stays outside the chain so it can run in parallel. `ChildOf` is data on the child, not a scene tree. Do not invent crates or types.
