---
name: godot-ui
description: >
  Builds Godot 4.x user interfaces with Control nodes — anchors/offsets for responsive
  layout, Container nodes (VBox/HBox/Grid/Margin) for automatic arrangement, Theme
  resources for consistent styling, and keyboard/gamepad focus navigation. Use when
  laying out a HUD, menu, inventory, dialog, or settings screen, or when working with
  Control/Container nodes, anchors, themes, focus, or .tscn UI in a Godot project.
  Never parent buttons under Node2D, set child anchors inside a Container, or treat
  this as full input rebinding.
version: 1.0.1
license: Apache-2.0
compatibility: Godot 4.3+
metadata:
  engine: godot
  category: godot
  difficulty: intermediate
  scope: T
  pack: tbs-skills-pack
---

# Godot UI / Control nodes (4.x)

Lay out responsive UI with `Control` anchors and `Container` nodes, style it with a
`Theme`, and make it navigable by keyboard and gamepad. Targets **Godot 4.3+**.

## When to Use

- Building HUDs, menus, inventories, dialog boxes, or settings screens with
  `Control`-derived nodes.
- Arranging UI that must adapt to window size changes.
- Creating or applying a `Theme` resource for consistent styling.
- Wiring focus navigation for controller/keyboard input.
- Working inside a `.tscn` that contains `Control`, `Container`, `Theme`, or focus
  properties.

**Trigger keywords:** Control, Container, VBoxContainer, HBoxContainer,
GridContainer, MarginContainer, anchors, offsets, size_flags, Theme, StyleBox,
focus, grab_focus, CanvasLayer, HUD, menu, UI layout.

**When *not* to use:**
- In-world 2D nodes (`Node2D`/sprites) → `godot-nodes-scenes`.
- Animating UI transitions → `godot-animation` (Tween).
- Genre-specific UI like card hands → `card-game` / `visual-novel`.
- Full input rebinding → `input-systems`.

## Prerequisites

- Godot 4.3 or newer project opened in the editor or available on CLI.
- A `.tscn` scene file to add or edit UI within.
- (Optional) A `Theme` resource (`.tres`) if you want centralized styling.

## Procedure

### 1. Use Control nodes for UI — not Node2D

`Control` nodes have a rect (position + size), anchors, and participate in focus and
theming. `Node2D` does not. Keep all UI under a `CanvasLayer` or `Control` subtree.

```gdscript
extends Control
```

### 2. Anchor for responsiveness

Anchors are fractions (0–1) of the parent rect that the Control's edges stick to. Use
the editor's **Layout** presets (Top-Left, Full Rect, Center, etc.) instead of
hand-placing pixels.

```gdscript
extends Control

func _ready() -> void:
    # Stretch this panel to fill its parent (equivalent to "Full Rect" preset).
    anchors_preset = Control.PRESET_FULL_RECT
    # Or set anchors manually: all four edges at the parent's far corners.
    # anchor_left = 0; anchor_top = 0; anchor_right = 1; anchor_bottom = 1
```

### 3. Let Containers position children

Put children in a `VBoxContainer`, `HBoxContainer`, `GridContainer`,
`MarginContainer`, etc. The container sets their position/size; you control flow with
`size_flags`. **Do not set child anchors inside a container** — the container
overrides them.

```gdscript
extends VBoxContainer    # children stack vertically, auto-sized

func _ready() -> void:
    for child in get_children():
        if child is Button:
            child.pressed.connect(_on_button_pressed.bind(child.name))
    # Give the first button focus so a gamepad can navigate immediately.
    if get_child_count() > 0:
        (get_child(0) as Control).grab_focus()

func _on_button_pressed(which: StringName) -> void:
    match which:
        "PlayButton":  get_tree().change_scene_to_file("res://game.tscn")
        "QuitButton":  get_tree().quit()
```

### 4. Size flags — make one child expand to fill leftover space

```gdscript
# In a HBoxContainer: a label on the left, a spacer that eats remaining width.
func _ready() -> void:
    $Label.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
    $Spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL   # grows to fill
```

### 5. Style with a Theme resource

Assign a `Theme` resource on a top-level `Control`; children inherit it. Override
per-node with `add_theme_*` setters only when necessary.

```gdscript
func _ready() -> void:
    # Per-node overrides: use add_theme_* (type-specific setters).
    $Title.add_theme_font_size_override("font_size", 32)
    $Title.add_theme_color_override("font_color", Color.GOLD)
    $Panel.add_theme_stylebox_override("panel", preload("res://ui/panel.stylebox.tres"))
```

### 6. Wire focus for keyboard/gamepad

Set a default focused control with `grab_focus()`. Define focus neighbors explicitly
or rely on auto-neighbor. Ensure `focus_mode` is not `FOCUS_NONE` on interactive
controls.

### 7. Connect signals

Wire UI events to game logic: `pressed`, `toggled`, `text_submitted`,
`value_changed`, `item_selected`, etc.

### 8. Load the reference for deep detail

**When you need** the anchor/offset math, every Container type, building/extending
Theme and StyleBox resources, focus neighbor wiring, or `CanvasLayer` for HUDs,
**load** `references/layout-and-theming.md` from this skill folder:

```powershell
# Windows / PowerShell — read the reference file
Get-Content .\references\layout-and-theming.md  # if present in this folder; else Godot 4 docs for Control/Theme
```

Load this reference when the core steps above are insufficient — e.g., you need the
full list of Container types, StyleBox subclass details, or focus neighbor
properties.

## Pitfalls

- **Mixing manual position with Containers.** A child of a `Container` cannot set its
  own position/anchors — the container owns layout. To free-place, take the node out
  of the container or use a plain `Control`/`PanelContainer` wrapper.
- **Anchors vs offsets.** Anchors are fractions of the parent; offsets are pixel deltas
  from the anchored point. Set anchors via presets, then nudge with offsets. Setting
  only `position` while anchors are at 0 makes UI not scale with the window.
- **`Node2D` for UI.** Buttons/labels parented under a `Node2D` won't theme or take
  focus correctly. Keep UI under a `CanvasLayer`/`Control` subtree.
- **Focus lost on gamepad.** If nothing is focused, directional input does nothing.
  Call `grab_focus()` on an initial control and ensure `focus_mode` is not
  `FOCUS_NONE`.
- **Theme vs theme override.** A `Theme` resource styles a whole subtree;
  `add_theme_*` overrides one node. Overusing per-node overrides defeats centralized
  theming.
- **`rect_*` properties are renamed.** Godot 3's `rect_size` / `rect_position` /
  `rect_min_size` are now `size` / `position` / `custom_minimum_size` in 4.x.
- **`mouse_filter`** on a full-rect Control can swallow clicks meant for nodes
  beneath it; set `MOUSE_FILTER_IGNORE` on purely decorative panels.
- **Never delete** existing `Theme` or `StyleBox` resources referenced by scenes —
  unlink or replace first, then remove.

## Verification

1. **Scene opens without errors** — open the `.tscn` in the Godot editor; the Output
   dock should show no parse errors.

2. **Layout adapts to window resize** — run the scene and resize the window; anchored
   controls should stretch, container children should reflow.

   ```powershell
   # Launch the project from CLI (Windows / PowerShell)
   & "C:\Program Files\Godot\Godot.exe" --path . res://your_ui_scene.tscn
   ```

   Adjust the Godot executable path if installed elsewhere.

3. **Focus works on keyboard/gamepad** — press arrow keys / D-pad; focus should move
   between buttons. Verify with:

   ```gdscript
   print(get_viewport().gui_get_focus_owner())
   ```

   This should print the currently focused Control node name, not `null`.

4. **Theme applies to subtree** — confirm child nodes inherit the parent `Theme`
   resource. A quick check in `_ready()`:

   ```gdscript
   print($Title.get_theme_font_size("font_size"))  # should match theme value
   ```

5. **No `rect_*` remnants** — search the `.tscn` for Godot 3 property names:

   ```powershell
   Select-String -Path "res://your_ui_scene.tscn" -Pattern "rect_size|rect_position|rect_min_size"
   ```

   No matches expected in a clean 4.x scene.

## Related skills

- `game-ui-ux` — cross-engine UI/UX: responsive scaling, safe areas, focus navigation,
  screen flow.
- `godot-animation` — Tween-based UI transitions and juicing.
- `godot-signals-groups` — connecting UI events to game logic.
- `input-systems` — rebindable input and multi-device focus.
- `card-game` / `visual-novel` — UI-heavy genre templates.
