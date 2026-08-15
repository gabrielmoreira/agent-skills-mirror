---
name: editor-and-tooling
description: "Use when extending the Godot 4.x editor or configuring development tooling — covers EditorPlugin creation, @tool scripts, custom inspectors, docks and panels, EditorScript for batch operations, custom resource editors, GDExtension (C++/Rust), debugger, version control with Git, EditorExportPlugin, CLI and headless mode, EditorImportPlugin, editor/project settings, code editor integrations (VS Code, Rider, Neovim), GDScript LSP, Asset Library, custom 3D gizmos, testing frameworks (GUT, GdUnit4), documentation generation, and build automation with CI/CD. Make sure to use this skill whenever the user writes editor plugins, @tool scripts, custom inspectors, export plugins, import plugins, GDExtension bindings, CI/CD pipelines, or asks about Godot editor customization, testing, or tooling."
version: 1.0.1
---

## Overview
Godot's editor is itself a Godot application — every panel, dock, and inspector is a scene. This means you can extend and customize the editor using the same APIs you use for games. This skill covers creating editor plugins, `@tool` scripts, custom inspectors, GDExtension bindings, debugging, testing, version control, CI/CD, and all supporting tooling.

## When to Use
Use when building editor plugins, writing `@tool` scripts, creating custom inspector UIs, setting up CI/CD pipelines, configuring testing frameworks, integrating external editors, or working with GDExtension.

## Prerequisites
- Godot 4.x installed.
- For GDExtension: C++ or Rust toolchain configured.
- For CI/CD: Git and optionally GitHub Actions.
- Windows host is primary (PowerShell). Adjust paths for external editors accordingly.

## Procedure

### 1. EditorPlugin Creation
An **EditorPlugin** is the entry point for all editor extensions. It lives under `addons/<plugin_name>/` and is activated via Project Settings > Plugins.

Directory structure:
```text
addons/
  my_plugin/
    plugin.cfg          # Required metadata
    plugin.gd           # Main EditorPlugin script
    inspector.gd        # Optional: EditorInspectorPlugin
    dock.tscn           # Optional: custom dock scene
    icon.svg            # Optional: plugin icon
```

`plugin.cfg`:
```ini
[plugin]

name="My Plugin"
description="Does something useful in the editor."
author="Your Name"
version="1.0.0"
script="plugin.gd"
```

Plugin lifecycle:
```gdscript
@tool
extends EditorPlugin

var _inspector_plugin: MyInspectorPlugin
var _dock: Control

func _enter_tree() -> void:
    # Called when the plugin is activated.
    # Add all custom types, inspectors, docks here.
    _inspector_plugin = MyInspectorPlugin.new()
    add_inspector_plugin(_inspector_plugin)

    _dock = preload("res://addons/my_plugin/dock.tscn").instantiate()
    add_control_to_dock(DOCK_SLOT_LEFT_UL, _dock)

    add_custom_type(
        "MyCustomNode",
        "Node3D",
        preload("res://addons/my_plugin/my_custom_node.gd"),
        preload("res://addons/my_plugin/icon.svg")
    )

func _exit_tree() -> void:
    # Called when the plugin is deactivated.
    # Remove EVERYTHING you added — reverse order of _enter_tree.
    remove_custom_type("MyCustomNode")
    remove_control_from_docks(_dock)
    _dock.queue_free()
    remove_inspector_plugin(_inspector_plugin)

func _has_main_screen() -> bool:
    return false  # true to add a main screen tab like "2D", "3D", "Script"

func _get_plugin_name() -> String:
    return "My Plugin"

func _get_plugin_icon() -> Texture2D:
    return preload("res://addons/my_plugin/icon.svg")

func _make_visible(visible: bool) -> void:
    # Called when main screen plugin is toggled on/off.
    pass
```

Dock slots:
```text
DOCK_SLOT_LEFT_UL   DOCK_SLOT_RIGHT_UL
DOCK_SLOT_LEFT_BL   DOCK_SLOT_RIGHT_BL
DOCK_SLOT_LEFT_UR   DOCK_SLOT_RIGHT_UR
DOCK_SLOT_LEFT_BR   DOCK_SLOT_RIGHT_BR
```

### 2. @tool Scripts
The `@tool` annotation makes a GDScript run in the editor (not just at runtime). Use for live previews, in-editor gizmos, and procedural generation.
```gdscript
@tool
extends Sprite2D

@export var radius: float = 100.0:
    set(value):
        radius = value
        queue_redraw()  # Redraw in editor when changed

func _draw() -> void:
    draw_circle(Vector2.ZERO, radius, Color.CORNFLOWER_BLUE)

func _process(delta: float) -> void:
    # CRITICAL: guard runtime-only logic
    if Engine.is_editor_hint():
        # Editor-only code (live preview updates, gizmo redraws)
        return
    # Runtime-only code
    position += velocity * delta
```

### 3. Custom Inspectors
Use `EditorInspectorPlugin` to add custom UI to the inspector.
```gdscript
@tool
extends EditorInspectorPlugin

func _can_handle(object: Object) -> bool:
    return object is MyCustomResource

func _parse_begin(object: Object) -> void:
    # Add controls BEFORE the default properties
    var label := Label.new()
    label.text = "Custom Header for %s" % object.resource_name
    add_custom_control(label)

func _parse_property(object: Object, type: Variant.Type,
        name: String, hint_type: PropertyHint,
        hint_string: String, usage_flags: int, wide: bool) -> bool:
    if name == "custom_color":
        var editor := MyColorProperty.new()
        add_property_editor(name, editor)
        return true  # true = replaces default editor for this property
    return false  # false = use default editor

func _parse_end(object: Object) -> void:
    # Add controls AFTER the default properties
    var button := Button.new()
    button.text = "Recalculate"
    button.pressed.connect(func(): object.recalculate())
    add_custom_control(button)
```

### 4. Custom Docks and Panels
```gdscript
# In your EditorPlugin._enter_tree():

# --- Dock (side panel) ---
var dock: Control = preload("res://addons/my_plugin/dock.tscn").instantiate()
add_control_to_dock(DOCK_SLOT_LEFT_UL, dock)

# --- Bottom panel (like Output, Debugger) ---
var bottom: Control = preload("res://addons/my_plugin/bottom.tscn").instantiate()
add_control_to_bottom_panel(bottom, "My Panel")
# Optionally bring it to front:
make_bottom_panel_item_visible(bottom)

# --- In _exit_tree(), remove them ---
remove_control_from_docks(dock)
dock.queue_free()
remove_control_from_bottom_panel(bottom)
bottom.queue_free()
```

### 5. EditorScript for Batch Operations
`EditorScript` runs a one-shot script via **File > Run** (or `Ctrl+Shift+X`). Perfect for batch renaming, asset processing, or scene tree manipulation.
```gdscript
@tool
extends EditorScript

func _run() -> void:
    # Access the currently edited scene's root
    var root: Node = get_scene()
    if root == null:
        printerr("No scene open.")
        return

    # Example: batch-rename all Sprite2D nodes
    var count: int = 0
    for node: Node in root.get_children():
        if node is Sprite2D:
            node.name = "Sprite_%03d" % count
            count += 1

    print("Renamed %d sprites." % count)
```

### 6. Custom Resource Editors
Three approaches for editing custom resources:
| Approach | Complexity | Best for |
|---|---|---|
| EditorInspectorPlugin | Low | Adding buttons, custom property widgets |
| Dedicated bottom panel | Medium | Multi-field editors, graphs, curve editors |
| Main screen plugin | High | Full visual editors (tilemap, dialogue tree) |

For a main screen plugin, implement `_has_main_screen() -> true` in your EditorPlugin and provide `_make_visible()`, `_get_plugin_name()`, and `_get_plugin_icon()`.

### 7. GDExtension (C++/Rust)
GDExtension allows writing high-performance native code that integrates with Godot like built-in classes.

**C++ with godot-cpp**
```ini
[configuration]

entry_symbol = "my_extension_init"
compatibility_minimum = "4.3"

[libraries]

windows.x86_64 = "res://bin/my_extension.windows.x86_64.dll"
linux.x86_64 = "res://bin/libmy_extension.linux.x86_64.so"
macos = "res://bin/libmy_extension.macos.framework"

[dependencies]

windows.x86_64 = {}
linux.x86_64 = {}
macos = {}
```

**Rust with godot-rust (gdext)**
```rust
use godot::prelude::*;
use godot::classes::Node3D;

#[derive(GodotClass)]
#[class(base=Node3D)]
struct MyNode {
    #[export]
    speed: f64,
    base: Base<Node3D>,
}

#[godot_api]
impl INode3D for MyNode {
    fn init(base: Base<Node3D>) -> Self {
        Self { speed: 10.0, base }
    }

    fn ready(&mut self) {
        godot_print!("MyNode ready with speed {}", self.speed);
    }
}
```

### 8. Godot Debugger
- **Breakpoints**: Click the left gutter in the script editor to toggle a breakpoint.
- **Step Over** (`F10`), **Step Into** (`F11`), **Continue** (`F12`).
- **Profiler**: Debugger > Profiler for per-frame function timings.
- **Remote scene tree**: While the game is running, the **Remote** tab in the Scene dock shows the live scene tree.

### 9. Version Control
`.gitignore`:
```gitignore
# Godot 4.x
.godot/
*.uid

# Export
export/
*.pck
*.zip

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
*.swp
```

`.gitattributes`:
```gitattributes
# Treat Godot text resources as text for clean diffs
*.tscn text eol=lf
*.tres text eol=lf
*.gd text eol=lf
*.cfg text eol=lf
*.import text eol=lf

# Binary assets — track with Git LFS
*.png filter=lfs diff=lfs merge=lfs -text
*.jpg filter=lfs diff=lfs merge=lfs -text
*.webp filter=lfs diff=lfs merge=lfs -text
*.ogg filter=lfs diff=lfs merge=lfs -text
*.wav filter=lfs diff=lfs merge=lfs -text
*.mp3 filter=lfs diff=lfs merge=lfs -text
*.glb filter=lfs diff=lfs merge=lfs -text
*.gltf filter=lfs diff=lfs merge=lfs -text
*.blend filter=lfs diff=lfs merge=lfs -text
*.ttf filter=lfs diff=lfs merge=lfs -text
*.otf filter=lfs diff=lfs merge=lfs -text
```

Git LFS setup (run in PowerShell or bash):
```powershell
git lfs install
git lfs track "*.png" "*.ogg" "*.glb" "*.wav" "*.blend"
git add .gitattributes
```

### 10. EditorExportPlugin
Run custom logic during export (e.g., strip debug code, inject build metadata, validate assets).
```gdscript
@tool
extends EditorExportPlugin

func _get_name() -> String:
    return "BuildMetadataInjector"

func _export_begin(features: PackedStringArray, is_debug: bool,
        path: String, flags: int) -> void:
    print("Exporting to: ", path)
    print("Features: ", features)
    print("Debug: ", is_debug)

    # Inject a build info file
    var build_info: Dictionary = {
        "version": ProjectSettings.get_setting("application/config/version"),
        "timestamp": Time.get_datetime_string_from_system(),
        "debug": is_debug,
    }
    var json: String = JSON.stringify(build_info)
    add_file("res://build_info.json", json.to_utf8_buffer(), false)

func _export_file(path: String, type: String, features: PackedStringArray) -> void:
    # Skip specific files from export
    if path.begins_with("res://debug/"):
        skip()
```

### 11. Command-Line Interface
```powershell
# Run a project
godot --path /path/to/project

# Headless mode (no window — for servers, CI)
godot --headless --path /path/to/project

# Export (release)
godot --headless --path /path/to/project --export-release "Windows Desktop"

# Validate GDScript without running
godot --headless --path /path/to/project --check-only

# Import resources then quit (useful in CI before export)
godot --headless --path /path/to/project --import
```

### 12. EditorImportPlugin
Create custom importers for file formats the editor doesn't natively support.
```gdscript
@tool
extends EditorImportPlugin

func _get_importer_name() -> String:
    return "my_plugin.csv_importer"

func _get_visible_name() -> String:
    return "CSV Data Table"

func _get_recognized_extensions() -> PackedStringArray:
    return PackedStringArray(["csv"])

func _get_save_extension() -> String:
    return "tres"

func _get_resource_type() -> String:
    return "Resource"

func _get_priority() -> float:
    return 1.0

func _get_import_order() -> int:
    return 0

func _get_preset_count() -> int:
    return 1

func _get_preset_name(preset_index: int) -> String:
    return "Default"

func _get_import_options(path: String, preset_index: int) -> Array[Dictionary]:
    return [
        { "name": "delimiter", "default_value": ",", "hint_string": "Delimiter character" },
    ]

func _import(source_file: String, save_path: String,
        options: Dictionary, platform_variants: Array[String],
        gen_files: Array[String]) -> Error:
    var file := FileAccess.open(source_file, FileAccess.READ)
    if file == null:
        return FileAccess.get_open_error()

    var data: Array[PackedStringArray] = []
    while not file.eof_reached():
        var line: String = file.get_line()
        if line.strip_edges() != "":
            data.append(line.split(options.get("delimiter", ",")))

    var resource := DataTable.new()
    resource.rows = data

    var save_file: String = "%s.%s" % [save_path, _get_save_extension()]
    return ResourceSaver.save(resource, save_file)
```

### 13. Editor and Project Settings
```gdscript
# Project settings (project.godot)
var gravity: float = ProjectSettings.get_setting("physics/2d/default_gravity")

# Editor settings (editor-level, not project-level)
var font_size: int = EditorInterface.get_editor_settings().get_setting(
    "interface/editor/main_font_size"
)
```

### 14. Code Editor Integrations
**VS Code — Godot Tools extension**
1. Install the **Godot Tools** extension (`geequlim.godot-tools`).
2. In Godot: **Editor > Editor Settings > Text Editor > External** → enable **Use External Editor**.
3. Set **Exec Path** to your VS Code path (`code` on Linux/macOS, full path on Windows like `C:\Program Files\Microsoft VS Code\Code.exe`).
4. Set **Exec Flags** to `{project} --goto {file}:{line}:{col}`.

**JetBrains Rider**
1. Install the **Godot Support** plugin from the JetBrains marketplace.
2. Configure the Godot executable path in **Settings > Languages & Frameworks > Godot**.

**Neovim**
1. Configure the built-in LSP client to connect to `localhost:6005` (Godot's GDScript LSP).
2. Use `nvim-lspconfig` with the `gdscript` server config:
```lua
require("lspconfig").gdscript.setup({
    cmd = { "ncat", "localhost", "6005" },  -- or use 'nc' on macOS
    filetypes = { "gd", "gdscript" },
})
```

### 15. GDScript LSP
- **Default port**: `6005` (configurable in Editor Settings > Network > Language Server).
- **Features**: autocompletion, hover documentation, go-to-definition, find references, diagnostics, symbol search, signature help.
- **Starts automatically** when the Godot editor is open — external editors connect to the running instance.

### 16. Custom 3D Gizmos
Register in your EditorPlugin:
```gdscript
var _gizmo_plugin: MyGizmoPlugin

func _enter_tree() -> void:
    _gizmo_plugin = MyGizmoPlugin.new()
    add_node_3d_gizmo_plugin(_gizmo_plugin)

func _exit_tree() -> void:
    remove_node_3d_gizmo_plugin(_gizmo_plugin)
```

### 17. Testing Frameworks
**GUT 9.x (Godot Unit Test)**
```gdscript
extends GutTest

func before_each() -> void:
    gut.p("Setting up test")

func test_health_decreases_on_damage() -> void:
    var player := Player.new()
    add_child_autofree(player)
    player.take_damage(25)
    assert_eq(player.health, 75, "Health should decrease by damage amount")
```

**GdUnit4**
```gdscript
extends GdUnitTestSuite

func test_health_system() -> void:
    var player: Player = auto_free(Player.new())
    add_child(player)
    player.take_damage(30)
    assert_int(player.health).is_equal(70)
```

### 18. Documentation Generation
Use `##` comments above classes, members, and methods. Godot parses these into the built-in help system.
```gdscript
## A loot table that randomly selects items based on weight.
##
## Each entry has an [member Item] and a [code]weight[/code] value.
## Higher weights increase selection probability.[br]
## [b]Example:[/b]
## [codeblock]
## var table := LootTable.new()
## table.add_entry(sword, 10)
## table.add_entry(potion, 50)
## var item := table.roll()
## [/codeblock]
class_name LootTable
extends Resource
```

XML export for external docs:
```powershell
godot --headless --path /path/to/project --doctool ./docs/
```

### 19. Build Automation
**GitHub Actions workflow**
```yaml
name: Godot CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  GODOT_VERSION: "4.3"

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          lfs: true
      - uses: chickensoft-games/setup-godot@v2
        with:
          version: ${{ env.GODOT_VERSION }}
          use-dotnet: false
      - name: Validate GDScript
        run: godot --headless --path . --check-only

  test:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
        with:
          lfs: true
      - uses: chickensoft-games/setup-godot@v2
        with:
          version: ${{ env.GODOT_VERSION }}
          use-dotnet: false
      - name: Import resources
        run: godot --headless --path . --import
      - name: Run GUT tests
        run: |
          godot --headless --path . \
            --script res://addons/gut/gut_cmdln.gd \
            -- -gdir=res://tests -gexit

  export:
    runs-on: ubuntu-latest
    needs: test
    strategy:
      matrix:
        preset: ["Windows Desktop", "Linux", "macOS", "Web"]
    steps:
      - uses: actions/checkout@v4
        with:
          lfs: true
      - uses: chickensoft-games/setup-godot@v2
        with:
          version: ${{ env.GODOT_VERSION }}
          use-dotnet: false
      - name: Install export templates
        run: |
          mkdir -p ~/.local/share/godot/export_templates/${{ env.GODOT_VERSION }}.stable
          # Download and extract templates (platform-specific)
      - name: Import resources
        run: godot --headless --path . --import
      - name: Export
        run: |
          mkdir -p build
          godot --headless --path . --export-release "${{ matrix.preset }}" build/game
      - uses: actions/upload-artifact@v4
        with:
          name: ${{ matrix.preset }}
          path: build/
```

**Multi-platform export script (local PowerShell)**
```powershell
$ErrorActionPreference = "Stop"
$PROJECT_DIR = (Get-Location).Path
$BUILD_DIR = "$PROJECT_DIR\build"
$GODOT = "godot"  # or full path to Godot executable

Write-Host "=== Importing resources ==="
& $GODOT --headless --path $PROJECT_DIR --import

Write-Host "=== Validating GDScript ==="
& $GODOT --headless --path $PROJECT_DIR --check-only

$presets = @("Windows Desktop", "Linux", "macOS", "Web")
foreach ($preset in $presets) {
    Write-Host "=== Exporting: $preset ==="
    $presetDir = $BUILD_DIR + "\" + ($preset -replace " ", "_")
    New-Item -ItemType Directory -Force -Path $presetDir | Out-Null
    & $GODOT --headless --path $PROJECT_DIR --export-release $preset "$presetDir\game"
}

Write-Host "=== All exports complete ==="
```

## Pitfalls
- **Unbalanced `_enter_tree` / `_exit_tree`**: Everything added in `_enter_tree` MUST be removed in `_exit_tree`. Failing to remove controls, types, or inspectors causes memory leaks and ghost UI elements.
- **`@tool` dependency chain**: If script A is `@tool` and references script B via `preload`, script B **must also be `@tool`** — otherwise the editor cannot parse B's class and will report errors. Chain `@tool` through all dependencies.
- **Unguarded runtime logic in `@tool`**: Always guard runtime-only logic with `if Engine.is_editor_hint(): return` in `_process` or `_physics_process` to prevent editor crashes or unexpected behavior.
- **LSP Port Conflicts**: The GDScript LSP defaults to port `6005`. If external editors fail to connect, ensure Godot is running and the port is not blocked by a firewall.
- **CI Import Step**: Always run `--import` before `--export-release` in CI/CD pipelines, otherwise exports may fail due to missing `.import` files.
- **Custom Settings Cleanup**: Custom project settings added in `_enter_tree` should be removed in `_exit_tree` by setting them to `null` to avoid cluttering the user's project settings.

## Verification
- **Plugin Lifecycle**: Enable and disable the plugin in Project Settings > Plugins. Check that no errors appear in the Output panel and no ghost UI remains.
- **@tool Scripts**: Change an `@export` variable in the inspector. The editor viewport should update immediately if `_draw` or `queue_redraw` is used.
- **CLI Validation**: Run `godot --headless --path . --check-only` to validate all GDScript without running the game.
- **CI Pipeline**: Trigger the GitHub Actions workflow. Ensure the `lint` and `test` jobs pass before `export`.
- **Export**: Run the local export script or CI export job. Verify the `build/` directory contains the exported binaries for all presets.

## Related
- GDScript syntax for @tool scripts → [gdscript](../gdscript/SKILL.md)
- Scene tree that plugins manipulate → [scene-and-nodes](../scene-and-nodes/SKILL.md)
- C# as a GDExtension alternative → [csharp-godot](../csharp-godot/SKILL.md)
- Export and deployment → [export-and-deployment](../export-and-deployment/SKILL.md)
- Architecture patterns for testable code → [architecture-patterns](../architecture-patterns/SKILL.md)
