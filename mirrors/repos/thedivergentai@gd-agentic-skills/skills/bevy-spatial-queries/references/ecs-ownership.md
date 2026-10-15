# ECS ownership - bevy-spatial-queries

Who owns each piece of state, and on which schedule.

Target: **Bevy 0.20+**.

| Need | Owner | Schedule |
| --- | --- | --- |
| Per-entity | `Component` + `Query` | `Update` or `FixedMain` |
| App-wide | `Resource` | insert in `Startup` |
| Spawn | `Commands` | `Startup` or the runtime schedule |
| Ordered mutation | `.chain()` | same schedule |
| Plugin setup | `Plugin` `build` | before run |
| Pointer pick | `Camera` + `PrimaryWindow` | `Update`, read-only |
| Radius | `Probe` component | read after movement |
| Same-frame facing | `Transform` | `advance` then `can_see`, `.chain()` |

Do not invent ray APIs. Collider casts stay on the physics skills.
