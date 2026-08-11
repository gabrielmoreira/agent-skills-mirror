# Migration notes: godot-input-handling

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 3.x → 4.0

Official: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html)

- Prefer `Signal.connect(callable)` over string `connect` (converter may leave strings).
- `InputEventWithModifiers`: `alt`/`shift`/… → `alt_pressed`/`shift_pressed`/…
- `InputEventMouseButton.doubleclick` → `double_click`.
- Screen/window queries moved OS → `DisplayServer` (`screen_get_size`, etc.).

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- Viewports with physics picking enabled auto-mark `InputEvent`s handled — adjust `_unhandled_input` gameplay handlers that expected pick events to bubble.
- `SubViewportContainer.mouse_filter` behavior changed — mouse events may pass through differently; verify UI-over-world click routing.

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

*No skill-relevant breaking changes for this hop.*

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

*No skill-relevant breaking changes for this hop.*

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- Android motion sensors disabled by default — enable Project Settings → Input Devices → Sensors before tilt/virtual-analog input drives gameplay actions.

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

*No skill-relevant breaking changes for this hop.*

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

*No skill-relevant breaking changes for this hop.*

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- **`InputEvent.DEVICE_ID_MOUSE`** / **`InputEvent.DEVICE_ID_KEYBOARD`** replace magic `-1` / `0` for mouse and keyboard — update device routing in glyph prompts and split-screen controllers.
- **NEVER** compare `event.device == 0` for mouse/keyboard — joypads may legitimately use device ID `0`.
- New projects default stretch mode **`canvas_items`** + aspect **`expand`** (was `disabled`/`keep`) — retest touch/action coordinate mapping on resizable windows.
