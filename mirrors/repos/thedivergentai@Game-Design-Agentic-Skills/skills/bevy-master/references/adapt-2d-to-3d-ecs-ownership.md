# ECS ownership - bevy-adapt-2d-to-3d

Who owns each piece of state, and on which schedule.

Target: **Bevy 0.20+**.

| Need | Owner | Schedule |
| --- | --- | --- |
| Per-entity | `Component` + `Query` | `Update` or `FixedMain` |
| App-wide | `Resource` | insert in `Startup` |
| Spawn | `Commands` | `Startup` or the runtime schedule |
| Ordered mutation | `.chain()` | same schedule |
| Plugin setup | `Plugin` `build` | before run |
| Sprite and Camera2d removal | `Commands` on the same entity | `Startup`, chained before any 3D reader |
| Lifted motion | `WishVelocity` | `FixedUpdate` only; do not also write `PlanarVelocity` there |

`promote_actors` and `promote_camera` share no component, but both run before gameplay reads the new draw components, so they stay on one `Startup` chain. `lift_velocity` is the only writer of `WishVelocity`.
