# Migration notes: godot-genre-platformer

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- `Area2D.priority` type is `int` (was `float`) — audit hazard/trigger ordering on layered platforms.
- `PhysicsDirectSpaceState2D.collide_shape` returns `Array[Vector2]` (was `Array[PackedVector2Array]`).
- `PathFollow2D.lookahead` removed — update moving-platform path followers.
- Viewports with physics picking auto-mark input handled — remove redundant manual pick forwarding on drop-through / hazard rays.

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

*No skill-relevant breaking changes for this hop.*

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- **TileMap layers → `TileMapLayer` nodes** — migrate level chunks before relying on per-layer collision/z-order APIs.
- If the genre ships multiplayer, upgrade all peers to 4.3 together (`SceneMultiplayer` protocol break).

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

*No skill-relevant breaking changes for this hop.*

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

*No skill-relevant breaking changes for this hop.*

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- Retune Environment glow/fog if the genre leans on bloom-heavy looks (parallax glow, night levels).

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- Confirm project stretch mode and `AudioStreamPlayer.area_mask` after opening in 4.7.
- One-way collision **direction** is shape-relative — retune `CollisionShape2D` direction for angled platforms and drop-through handlers.
- `PhysicsServer2D.body_set_shape_as_one_way_collision` adds optional `direction` (relative to shape).
