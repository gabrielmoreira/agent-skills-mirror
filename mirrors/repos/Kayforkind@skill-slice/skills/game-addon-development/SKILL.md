---
name: game-addon-development
version: 1.1.1
description: "Creates Godot 4.3+ editor plugins: plugin.cfg, EditorPlugin enter/exit registration, @tool scripts, custom inspectors, docks, and 3D gizmos. Use when extending the Godot editor with custom node types, inspector widgets, or project tooling. Not for runtime gameplay systems, GdUnit4/export CI (game-godot), or Control/Theme UI (godot-ui)."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## Overview
Editor plugins extend the Godot editor itself: custom node types, inspector panels, dock widgets, 3D gizmos, and toolbar buttons. All examples target Godot 4.3+ and avoid deprecated APIs. The recurring theme throughout this skill is that the editor is a long-lived process that runs your plugin code directly. That single fact explains almost every rule below: anything you register stays registered until you remove it, anything that blocks freezes the whole editor, and any code that assumes a running game will misbehave at edit time.

## When to Use
- When you need to extend the Godot editor's functionality with project-specific tooling.
- When creating custom node types that should appear in the **Add Node** dialog with their own icon and editor behavior.
- When building custom inspector panels or property editors for specific types (e.g. a color-ramp widget or an enum dropdown that the default inspector can't express).
- When creating custom dock panels for project-wide tooling such as level browsers, asset summaries, or build dashboards.
- When implementing 3D gizmos for interactive editing in the 3D viewport (draggable handles, radius rings, direction arrows).
- When you need a script to execute logic *inside* the editor viewport — live previews, validation, procedural geometry — via `@tool`.

## Prerequisites
- Godot 4.3+ project.
- Windows host (PowerShell) is primary. Keep Windows path notes when present.

## Procedure

### 1. Plugin Structure
Every plugin lives inside `addons/` at the project root. Godot discovers plugins by scanning that folder for `plugin.cfg` files, so the directory layout *is* the registration mechanism — there is no central manifest to edit.

```text
res://
└── addons/
    └── my_plugin/
        ├── plugin.cfg          # required — plugin metadata, read during the addons/ scan
        ├── plugin.gd           # main EditorPlugin script (path named in plugin.cfg)
        ├── my_inspector.gd     # optional — EditorInspectorPlugin
        ├── my_dock.tscn        # optional — dock panel scene
        └── icons/
            └── my_node.svg     # optional — custom node icons (16×16 SVG renders crisply at any DPI)
```

`plugin.cfg` is a plain INI file. The `script` key must point to the main plugin script *relative to the plugin folder*, because Godot resolves it against the folder it found the config in. A complete example:

```ini
[plugin]

name="My Plugin"
description="Adds a custom node, dock, and gizmo for level design."
author="Your Name"
version="1.0.0"
script="plugin.gd"
```

Enable the plugin via **Project → Project Settings → Plugins** and tick the checkbox next to its name. Ticking the box is what triggers `_enter_tree()`; un-ticking triggers `_exit_tree()`.

### 2. @tool Annotation
`@tool` (GDScript) / `[Tool]` (C#) makes a script run inside the editor process as well as at runtime. Without it, the script's code only executes when the game is playing, so editor-time features — live previews, configuration warnings, procedural setup — never fire.

#### GDScript
```gdscript
@tool
extends Sprite2D

# _process runs both in the editor (because of @tool) and at runtime.
# Engine.is_editor_hint() is true only inside the editor, so this branch keeps
# editor work and gameplay work cleanly separated in a single script.
func _process(delta: float) -> void:
    if Engine.is_editor_hint():
        # Safe to call editor-facing helpers here. Re-checking warnings each
        # frame is cheap and keeps the Scene-dock badge accurate during edits.
        update_configuration_warnings()
        return

    # Runtime gameplay logic goes here and never executes in the editor.


# _get_configuration_warnings() returns the strings shown as yellow warning
# badges on the node in the Scene dock. Surfacing a clear message at edit time
# is far friendlier than a null-reference crash when the game runs.
func _get_configuration_warnings() -> PackedStringArray:
    var warnings := PackedStringArray()
    if texture == null:
        warnings.append("Texture is not set. Assign a Texture2D in the Inspector.")
    return warnings
```

#### C#
```csharp
#if TOOLS
using Godot;
using System;

[Tool]
public partial class MyToolSprite : Sprite2D
{
    public override void _Process(double delta)
    {
        // Because of [Tool] this runs in-editor too; branch so editor-only
        // work never ships and gameplay never executes at edit time.
        if (Engine.IsEditorHint())
        {
            UpdateConfigurationWarnings();
            return;
        }

        // Runtime gameplay logic goes here.
    }

    public override string[] _GetConfigurationWarnings()
    {
        // A non-empty array shows a yellow warning badge in the Scene dock.
        if (Texture is null)
            return new[] { "Texture is not set. Assign a Texture2D in the Inspector." };

        return Array.Empty<string>();
    }
}
#endif
```

**Why these guards matter**
- `@tool` / `[Tool]` is what makes the script run in the editor at all. Without it the editor shows the node but never executes your code, so warnings and live previews never appear.
- Guarding runtime logic with `Engine.is_editor_hint()` prevents editor crashes: editor `_process` can begin before a scene is fully wired up, and gameplay code that assumes runtime systems (input, physics, autoloads) will fault when it runs at edit time.
- Call `update_configuration_warnings()` whenever a property that affects validity changes, because Godot only re-queries `_get_configuration_warnings()` when notified — otherwise a node keeps a stale badge after you've fixed (or newly broken) it.

### 3. EditorPlugin Base
The main plugin script extends `EditorPlugin`. Godot calls `_enter_tree()` when the plugin is enabled and `_exit_tree()` when it is disabled or the project closes. Because the editor outlives a single enable/disable cycle, **everything added in `_enter_tree()` must be removed in `_exit_tree()`** — otherwise registrations stack up as duplicates the next time the plugin is enabled. The flags below make the teardown auditable and idempotent.

#### GDScript
```gdscript
# res://addons/my_plugin/plugin.gd
@tool
extends EditorPlugin

const MY_NODE_SCRIPT_PATH := "res://addons/my_plugin/my_node.gd"
const MY_NODE_ICON_PATH := "res://addons/my_plugin/icons/my_node.svg"
const MY_PLUGIN_ACTION_NAME := "My Plugin Action"

# Track what we actually registered so teardown removes exactly that, even if
# _enter_tree bailed out early on a load failure.
var _custom_type_added := false
var _menu_item_added := false


func _enter_tree() -> void:
    # load() returns null and pushes an error when a path is wrong. Validate
    # before registering, because a custom type built from a null script would
    # leave a broken, uninstantiable entry in the Add Node dialog.
    var node_script := load(MY_NODE_SCRIPT_PATH) as Script
    if node_script == null:
        push_error("addon-development: could not load script at %s" % MY_NODE_SCRIPT_PATH)
        return

    var node_icon := load(MY_NODE_ICON_PATH) as Texture2D
    if node_icon == null:
        push_error("addon-development: could not load icon at %s" % MY_NODE_ICON_PATH)
        return

    # Registers MyNode under Node2D in the Add Node dialog with a custom icon.
    add_custom_type("MyNode", "Node2D", node_script, node_icon)
    _custom_type_added = true

    # Passing the method directly auto-binds a Callable to self. The menu item
    # appears under the Project menu in the top toolbar.
    add_tool_menu_item(MY_PLUGIN_ACTION_NAME, _on_tool_menu_item)
    _menu_item_added = true


func _exit_tree() -> void:
    if _menu_item_added:
        remove_tool_menu_item(MY_PLUGIN_ACTION_NAME)
        _menu_item_added = false
    if _custom_type_added:
        remove_custom_type("MyNode")
        _custom_type_added = false


func _on_tool_menu_item() -> void:
    # Parent editor dialogs under the editor's base Control, not the main
    # screen: the base control gives the dialog the editor theme and DPI and
    # positions it over the editor window. The main screen is reserved for the
    # 2D/3D/Script editors and would be the wrong parent.
    var base_control := EditorInterface.get_base_control()
    var dialog := ConfirmationDialog.new()
    dialog.title = "My Plugin"
    dialog.dialog_text = "Run the plugin action?"
    base_control.add_child(dialog)

    # Free the dialog whichever way it closes, so repeated invocations don't
    # leak orphaned Control nodes into the editor scene tree.
    dialog.confirmed.connect(_run_plugin_action)
    dialog.confirmed.connect(dialog.queue_free)
    dialog.canceled.connect(dialog.queue_free)
    dialog.popup_centered()


func _run_plugin_action() -> void:
    print("addon-development: plugin action confirmed")
```

#### C#
```csharp
// res://addons/my_plugin/Plugin.cs
#if TOOLS
using Godot;

[Tool]
public partial class MyPlugin : EditorPlugin
{
    private const string MyNodeScriptPath = "res://addons/my_plugin/MyNode.cs";
    private const string MyNodeIconPath = "res://addons/my_plugin/icons/my_node.svg";
    private const string MyPluginActionName = "My Plugin Action";

    private bool _customTypeAdded;
    private bool _menuItemAdded;

    public override void _EnterTree()
    {
        // GD.Load<T> gives a typed result and logs on failure; guard against
        // null so we never register a half-broken custom type.
        Script nodeScript = GD.Load<Script>(MyNodeScriptPath);
        if (nodeScript is null)
        {
            GD.PushError($"addon-development: could not load script at {MyNodeScriptPath}");
            return;
        }

        Texture2D nodeIcon = GD.Load<Texture2D>(MyNodeIconPath);
        if (nodeIcon is null)
        {
            GD.PushError($"addon-development: could not load icon at {MyNodeIconPath}");
            return;
        }

        AddCustomType("MyNode", "Node2D", nodeScript, nodeIcon);
        _customTypeAdded = true;

        // MethodName.* is generated at build time, so a renamed handler fails
        // to compile instead of silently breaking the menu callback.
        AddToolMenuItem(MyPluginActionName, new Callable(this, MethodName.OnToolMenuAction));
        _menuItemAdded = true;
    }

    public override void _ExitTree()
    {
        if (_menuItemAdded)
        {
            RemoveToolMenuItem(MyPluginActionName);
            _menuItemAdded = false;
        }
        if (_customTypeAdded)
        {
            RemoveCustomType("MyNode");
            _customTypeAdded = false;
        }
    }

    private void OnToolMenuAction()
    {
        // Parent under the editor base control for correct theme, DPI, and
        // placement — see the note in the GDScript example above.
        Control baseControl = EditorInterface.Singleton.GetBaseControl();
        var dialog = new ConfirmationDialog
        {
            Title = "My Plugin",
            DialogText = "Run the plugin action?",
        };
        baseControl.AddChild(dialog);

        dialog.Confirmed += () =>
        {
            GD.Print("addon-development: plugin action confirmed");
            dialog.QueueFree();
        };
        dialog.Canceled += dialog.QueueFree;
        dialog.PopupCentered();
    }
}
#endif
```

**add_custom_type parameters:**

| Parameter | Type | Description |
|---|---|---|
| `name` | `String` | The name shown in the **Add Node** dialog |
| `base` | `String` | String name of the Godot base class to extend |
| `script` | `Script` | The GDScript / C# script resource the new node uses |
| `icon` | `Texture2D` | A `Texture2D`, typically a 16×16 SVG |

`add_tool_menu_item` adds an entry under **Project** in the top menu bar. Pass a `Callable` that takes no arguments; in GDScript you can pass the method reference directly and it binds to `self`.

### 4. Custom Inspector Plugin
When the default inspector can't express the widget you want for a property, register an `EditorInspectorPlugin` from your main `EditorPlugin`. The inspector plugin overrides `_can_handle` to opt in to specific object types and `_parse_property` (or `_parse_begin`) to inject custom controls. The actual widget is an `EditorProperty` subclass, which is the bridge between your control and the editor's undo/redo and multi-edit systems.

`MyCustomNode` below refers to one of your own scripts declared with `class_name MyCustomNode`; that registration is what lets `object is MyCustomNode` resolve.

```gdscript
# res://addons/my_plugin/my_inspector_plugin.gd
@tool
extends EditorInspectorPlugin

# Resolve the widget class explicitly via preload so the reference never
# depends on global class-name registration order.
const MyCustomPropertyEditor := preload("res://addons/my_plugin/my_custom_property_editor.gd")


# _can_handle decides, per selected object, whether this plugin contributes
# any custom UI. Returning false for unrelated types keeps the Inspector fast
# and means we never touch objects we don't understand.
func _can_handle(object: Object) -> bool:
    return object is MyCustomNode


# _parse_property runs once per exported property. Return true to take over
# rendering for that property; return false to let Godot draw the default.
func _parse_property(
        object: Object,
        type: Variant.Type,
        name: String,
        hint_type: PropertyHint,
        hint_string: String,
        usage_flags: int,
        wide: bool) -> bool:
    # Only replace the widget for the one property we care about, and only when
    # it is the expected numeric type. Checking the type guards against a later
    # rename or retype silently feeding the wrong value into our editor.
    if name == "my_custom_property" and type == TYPE_FLOAT:
        add_property_editor(name, MyCustomPropertyEditor.new())
        return true
    return false
```

The `EditorProperty` subclass owns the actual control and keeps it in sync with the edited object:

```gdscript
# res://addons/my_plugin/my_custom_property_editor.gd
@tool
extends EditorProperty

var _slider := EditorSpinSlider.new()


func _init() -> void:
    _slider.min_value = 0.0
    _slider.max_value = 100.0
    _slider.step = 0.1
    add_child(_slider)
    # add_focusable lets keyboard tabbing reach our widget like a native field.
    add_focusable(_slider)
    _slider.value_changed.connect(_on_value_changed)


# Called by the Inspector whenever the underlying value changes (undo, multi-
# edit, external edits). Push the model value into the widget WITHOUT emitting,
# or you create an update loop between the widget and the property.
func _update_property() -> void:
    var current: float = get_edited_object().get(get_edited_property())
    _slider.set_value_no_signal(current)


func _on_value_changed(value: float) -> void:
    # emit_changed routes the edit through the editor's UndoRedo, so Ctrl+Z and
    # multi-object editing both work for free.
    emit_changed(get_edited_property(), value)
```

Register and unregister the inspector plugin from your main `EditorPlugin`, following the same allocate/free discipline as section 3:

```gdscript
# res://addons/my_plugin/plugin.gd  (inspector registration shown in isolation)
const MyInspectorPlugin := preload("res://addons/my_plugin/my_inspector_plugin.gd")

var _inspector_plugin: EditorInspectorPlugin


func _enter_tree() -> void:
    _inspector_plugin = MyInspectorPlugin.new()
    add_inspector_plugin(_inspector_plugin)


func _exit_tree() -> void:
    if _inspector_plugin != null:
        # EditorInspectorPlugin is RefCounted: removing the registration drops
        # the last reference and it frees itself. There is no queue_free() to
        # call (that is a Node method) — just clear our handle.
        remove_inspector_plugin(_inspector_plugin)
        _inspector_plugin = null
```

For the C# versions of these classes and to learn about `EditorResourcePicker` and `EditorResourcePreviewGenerator`, load [references/inspector-plugins.md](references/inspector-plugins.md).

### 5. Custom Dock Panels
To add custom UI panels to the editor, use `add_control_to_dock()`, `add_control_to_bottom_panel()`, or `add_control_to_container()`. For a full dock-slot table and the C# version, load [references/dock-panels.md](references/dock-panels.md).

### 6. Gizmos
`EditorNode3DGizmoPlugin` adds visual handles for 3D nodes in the viewport — wireframe shapes, draggable handles, rotation rings. The canonical Godot 4 pattern is to subclass the plugin and implement the drawing and handle callbacks directly: `_init` (create reusable materials), `_get_gizmo_name`, `_has_gizmo`, `_redraw`, and `_get_handle_value` / `_set_handle` / `_commit_handle` for interactive editing.

`MyCustomNode3D` below is your own `Node3D` subclass declared with `class_name MyCustomNode3D`, exposing a `target_offset: Vector3` property that this gizmo edits.

```gdscript
# res://addons/my_plugin/my_gizmo_plugin.gd
@tool
extends EditorNode3DGizmoPlugin

const MAIN_MATERIAL := "main"
const HANDLE_MATERIAL := "handles"


func _init() -> void:
    # Named materials are created once and reused across every gizmo this
    # plugin draws — cheaper than allocating a material each redraw.
    create_material(MAIN_MATERIAL, Color(1.0, 0.5, 0.0, 0.8))
    create_handle_material(HANDLE_MATERIAL)


func _get_gizmo_name() -> String:
    return "MyCustomNode3D"


# Decide per node whether to draw a gizmo. Keep this a cheap type check —
# _has_gizmo is called frequently as the selection changes.
func _has_gizmo(node: Node3D) -> bool:
    return node is MyCustomNode3D


# _redraw rebuilds the gizmo from scratch every time the node changes. Clear
# first and never cache geometry between calls, or stale lines accumulate.
func _redraw(gizmo: EditorNode3DGizmo) -> void:
    gizmo.clear()

    var node := gizmo.get_node_3d() as MyCustomNode3D
    if node == null:
        return

    # A line from the node origin to its target, plus a draggable handle there.
    var lines := PackedVector3Array([Vector3.ZERO, node.target_offset])
    gizmo.add_lines(lines, get_material(MAIN_MATERIAL, gizmo), false)

    var handles := PackedVector3Array([node.target_offset])
    gizmo.add_handles(handles, get_material(HANDLE_MATERIAL, gizmo), [])


# Return the pre-drag value so the editor can restore it if the user cancels.
func _get_handle_value(gizmo: EditorNode3DGizmo, handle_id: int, secondary: bool) -> Variant:
    var node := gizmo.get_node_3d() as MyCustomNode3D
    return node.target_offset if node != null else Vector3.ZERO


# Translate the mouse position into a new handle position while dragging.
func _set_handle(
        gizmo: EditorNode3DGizmo,
        handle_id: int,
        secondary: bool,
        camera: Camera3D,
        point: Vector2) -> void:
    var node := gizmo.get_node_3d() as MyCustomNode3D
    if node == null:
        return

    var ray_from := camera.project_ray_origin(point)
    var ray_dir := camera.project_ray_normal(point)
    # Guard against a ray parallel to the drag plane (ray_dir.y == 0), which
    # would divide by zero and produce NaN positions.
    if is_zero_approx(ray_dir.y):
        return

    var distance := (node.global_position.y - ray_from.y) / ray_dir.y
    node.target_offset = ray_from + ray_dir * distance - node.global_position
    node.update_gizmos()


# Commit (or roll back) the drag through UndoRedo so Ctrl+Z restores the value.
func _commit_handle(
        gizmo: EditorNode3DGizmo,
        handle_id: int,
        secondary: bool,
        restore: Variant,
        cancel: bool) -> void:
    var node := gizmo.get_node_3d() as MyCustomNode3D
    if node == null:
        return

    if cancel:
        node.target_offset = restore
        return

    # EditorInterface.get_editor_undo_redo() returns the editor's shared
    # EditorUndoRedoManager — the same history the rest of the editor uses, so
    # the user's undo stack stays consistent.
    var undo_redo := EditorInterface.get_editor_undo_redo()
    undo_redo.create_action("Move MyCustomNode3D Target")
    undo_redo.add_do_property(node, "target_offset", node.target_offset)
    undo_redo.add_undo_property(node, "target_offset", restore)
    undo_redo.commit_action()
```

Register the gizmo plugin from your main `EditorPlugin`:

```gdscript
# res://addons/my_plugin/plugin.gd  (gizmo registration shown in isolation)
const MyGizmoPlugin := preload("res://addons/my_plugin/my_gizmo_plugin.gd")

var _gizmo_plugin: EditorNode3DGizmoPlugin


func _enter_tree() -> void:
    _gizmo_plugin = MyGizmoPlugin.new()
    add_node_3d_gizmo_plugin(_gizmo_plugin)


func _exit_tree() -> void:
    if _gizmo_plugin != null:
        # EditorNode3DGizmoPlugin is RefCounted (via Resource); removing the
        # registration drops the last reference and it frees itself. There is
        # no queue_free() to call here.
        remove_node_3d_gizmo_plugin(_gizmo_plugin)
        _gizmo_plugin = null
```

For a worked C# gizmo (a spawn-radius ring with a single drag handle wired to UndoRedo), load [references/gizmos-deep-dive.md](references/gizmos-deep-dive.md).

### 7. Testing Plugins

#### Reloading a plugin in the editor
The fastest way to pick up plugin code changes without restarting Godot is to toggle the plugin off and on, which forces `_exit_tree()` then `_enter_tree()` to re-run with the new scripts:

1. **Project → Project Settings → Plugins** → untick the plugin → tick it again.
2. Or do it programmatically from **Editor → Run → Execute Script**, or from any `@tool` script:

```gdscript
# The identifier is the plugin's folder name under addons/ — the same name
# Godot uses in the Plugins list.
const PLUGIN_NAME := "my_plugin"


func reload_plugin() -> void:
    # is_plugin_enabled guards against toggling a plugin that was never enabled,
    # which would otherwise enable it as a side effect of "reloading".
    if not EditorInterface.is_plugin_enabled(PLUGIN_NAME):
        push_warning("Plugin '%s' is not enabled; nothing to reload." % PLUGIN_NAME)
        return

    EditorInterface.set_plugin_enabled(PLUGIN_NAME, false)
    EditorInterface.set_plugin_enabled(PLUGIN_NAME, true)
    print("Plugin '%s' reloaded." % PLUGIN_NAME)
```

#### Debugging with print and the error stream
`print()` writes to the Godot **Output** panel and to stdout when Godot is launched from a terminal. For anomalies, prefer `push_warning()` / `push_error()`: they appear in the Debugger's **Errors** tab with a stack trace and a clickable script location, so you can jump straight to the cause instead of scrolling the Output log.

```gdscript
func _enter_tree() -> void:
    # Lifecycle tracing: confirms the plugin actually entered the tree and when.
    print("[my_plugin] _enter_tree called")

    # Validate packaging assumptions and surface failures where you can click
    # through to them. A missing plugin.cfg usually means a broken export or a
    # mis-typed path, so warn loudly rather than failing silently later.
    if not FileAccess.file_exists("res://addons/my_plugin/plugin.cfg"):
        push_warning("[my_plugin] plugin.cfg not found — packaging may be broken")
        return

    print("[my_plugin] initialization complete")
```

When something goes wrong inside an editor callback, remember that exceptions there can destabilize the editor itself — which is exactly why the examples above validate loads, null-check cast results, and guard against degenerate math before acting.

## Pitfalls
- **Don't run gameplay-only logic in `@tool` scripts.** `@tool` makes a script execute inside the editor process, so movement, spawning, or state mutation also runs while you are editing the scene — which can corrupt the saved `.tscn`, spam the undo history, or leave orphan nodes behind. Gate runtime logic behind `Engine.is_editor_hint()` so it only runs in an actual game.
- **Don't call editor-only APIs from code that ships in the game.** Classes such as `EditorInterface` and everything under the `editor/` namespace are stripped from export templates. A call that works in the editor throws "class not found" or null-reference errors in a shipped build. Guard with `Engine.is_editor_hint()` in GDScript, or compile it out entirely with `#if TOOLS` in C# (a compile-time exclusion is stronger than a runtime check because the symbol never makes it into the build).
- **Tear down in `_exit_tree()` everything you set up in `_enter_tree()`.** Because the editor stays alive across plugin enable/disable cycles, custom types, docks, menu items, inspector plugins, and gizmo plugins accumulate as duplicates and leaked nodes if you don't remove them. Treat the two callbacks as a strict allocate/free pair — every `add_*` needs a matching `remove_*`.
- **Don't park arbitrary UI in the main screen.** `EditorInterface.get_editor_main_screen()` returns the central viewport that hosts the 2D/3D/Script editors; injecting controls there fights Godot's layout and vanishes when the user switches screens. Use `add_control_to_dock()`, `add_control_to_bottom_panel()`, or `add_control_to_container()` so your UI participates in the editor's saved layout, and parent transient dialogs under `EditorInterface.get_base_control()` instead.
- **Don't call `ProjectSettings.save()` from `_enter_tree()` / `_exit_tree()`.** Those callbacks fire during editor startup, shutdown, and plugin toggling — exactly when the editor may also be writing `project.godot`. A concurrent or interrupted save can corrupt the file. Persist settings in response to an explicit user action (a button, a menu item) where the timing is under your control.
- **In C#, load editor resources with `GD.Load<T>()`, not GDScript's `preload`.** `preload` is a compile-time, GDScript-only construct; C# has no equivalent. `GD.Load<T>()` returns a strongly-typed result and fails predictably (a logged error and a null), which beats a path typo surfacing as a confusing null far downstream.
- **Prefer the dedicated `add_control_to_*` helpers over low-level container insertion.** The typed dock, bottom-panel, and container helpers route your control through the editor's layout system, so it docks, floats, and restores like a native panel. Hand-managing container children bypasses that system and is far more likely to break across Godot versions.
- **Never hardcode secrets in plugin scripts.** Addons ship as readable `.gd` / `.cs` files in `addons/`, are usually committed to version control, and are often distributed through the Asset Library — so any embedded API key or credential is effectively public. Read secrets from user-level configuration stored outside the repository.
- **Keep `_process` / `_physics_process` cheap in `@tool` scripts.** The editor calls them every editor frame on the main thread; a blocking loop or heavy computation freezes the entire editor UI, not just your plugin. Move expensive work onto a `Thread`, or defer it with `Callable.call_deferred()` so it runs after the current frame instead of stalling it.
- **Don't depend on the editor's internal UI structure.** The node names and paths inside the editor are not a stable API and change between releases; reaching into them makes your plugin break on upgrade. Interact only through documented `EditorInterface` methods.

## Verification
1. Check that `plugin.cfg` exists and is valid:
   ```powershell
   Test-Path "res://addons/my_plugin/plugin.cfg"
   ```
   (Or check via `FileAccess.file_exists("res://addons/my_plugin/plugin.cfg")` in a tool script).
2. Enable the plugin via **Project → Project Settings → Plugins** and tick the checkbox next to its name.
3. Verify that `_enter_tree()` ran by checking the Godot **Output** panel for `[my_plugin] _enter_tree called` and `[my_plugin] initialization complete`.
4. Disable the plugin (untick the checkbox) and verify that `_exit_tree()` ran without leaving orphan nodes or duplicate menu items.
5. If using `@tool` scripts, verify that `Engine.is_editor_hint()` correctly gates runtime logic by checking that no gameplay logic executes while editing the scene.
6. If using gizmos, select the custom 3D node in the viewport and verify that the gizmo appears and handles are draggable. Verify that `Ctrl+Z` undoes the drag operation.

## Related skills
- `godot-game-development` - General Godot game development patterns.
