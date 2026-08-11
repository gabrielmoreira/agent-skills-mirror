# Migration notes: godot-characterbody-2d

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- `Area2D.priority` type is `int` (was `float`) — only affects custom-gravity / conveyor Area setups paired with CharacterBody controllers.
- Viewports with physics picking enabled auto-mark `InputEvent`s handled — adjust drop-through or click-to-move patterns if you relied on unhandled propagation through a physics viewport.
- `PathFollow2D.lookahead` removed — update moving-platform path followers that CharacterBodies ride.

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

*No skill-relevant breaking changes for this hop.*

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

*No skill-relevant breaking changes for this hop.*

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- Android motion sensors disabled by default — enable Project Settings → Input Devices → Sensors before mobile tilt/virtual-stick controllers drive CharacterBody input.

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

*No skill-relevant breaking changes for this hop.*

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

*No skill-relevant breaking changes for this hop.*

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- `PhysicsServer2D.body_set_shape_as_one_way_collision()` direction is shape-relative — re-tune one-way platform drop-through; align platform collider rotation or pass explicit direction instead of assuming global up.
- `CollisionShape2D` one-way collision direction follows shape orientation — verify tile and StaticBody one-ways still match movement normals after upgrade.
- Mouse/keyboard device IDs are `InputEvent.DEVICE_ID_MOUSE` / `InputEvent.DEVICE_ID_KEYBOARD` (not `0`) — update device-filtered input routing in controllers; joypads may legitimately use ID `0`.
