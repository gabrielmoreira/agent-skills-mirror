---
name: godot-save-load-systems
description: "Persists Godot 4.7+ game state with FileAccess JSON or store_var, user:// slots, PERSIST-group snapshots, schema versioning, AES-encrypted files, and SHA-256 integrity. Trigger on save/load, auto-save, encrypted slots, or save migration. Not for AutoLoad singleton wiring (godot-autoload-architecture) or dialogue-node persistence. Never write absolute OS paths or serialize Node references."
version: 1.0.1
---

## When to Use

Activate this skill when you need to implement or debug **save/load systems** in a Godot 4.7+ project. Trigger keywords: `save`, `load`, `JSON`, `FileAccess`, `user://`, `serialization`, `version migration`, `PERSIST group`, `encrypted saves`, `save slots`, `auto-save`.

Typical scenarios:
- Implementing a JSON or binary save system for player progress, settings, or game state.
- Adding version migration logic to handle old save files after schema changes.
- Setting up the PERSIST group pattern for auto-saving nodes.
- Adding encryption, backup slots, or integrity validation to an existing save system.
- Debugging corrupted saves, handle leaks, or cross-session identification issues.

## Prerequisites

- **Godot 4.7+** (stable, 2026-06-18). Consult the [Godot 4.7 migration guide](https://docs.godotengine.org/en/4.7/tutorials/migrating/upgrading_to_godot_4.7.html) when upgrading from 4.6.
- **NEVER** assume 4.6 defaults (stretch mode, audio area_mask, RichTextLabel percent flags) without checking 4.7 migration notes.
- Windows host is primary (PowerShell). `user://` resolves to `%APPDATA%\Godot\app_userdata\[project_name]` on Windows.
- A Godot project with an AutoLoad entry for `SaveManager` (or equivalent) must exist or be created as part of the procedure.

## Procedure

### Step 0: Load Reference Scripts (Mandatory)

Before implementing any pattern, read the relevant script from this skill's `scripts/` directory:

1. **`scripts/save_load_patterns.gd`** — Load this BEFORE implementing JSON saves, binary snapshots, safe-parsing, or threaded loading. Contains 10 expert patterns including PERSIST group serialization.
2. **`scripts/save_migration_manager.gd`** — Load this BEFORE implementing version migration or schema upgrades. Contains automatic migration logic between schema versions.
3. **`scripts/save_system_encryption.gd`** — Load this BEFORE implementing encrypted saves. Contains AES-256 encryption with compression.

### Step 1: Choose Save Format

| Format | Use Case | Pros | Cons |
|--------|----------|------|------|
| JSON | Most games, human-readable saves | Debuggable, portable | Slow for large data, no strict types |
| Binary (`store_var`) | Large saves, performance-critical | Fast, type-preserving | Not human-readable |
| Encrypted | Sensitive data, anti-tamper | Secure | Key management overhead |

### Step 2: Implement JSON Save System (Pattern 1 — Recommended for Most Games)

1. Create `save_manager.gd` as an AutoLoad:

```gdscript
# save_manager.gd
extends Node

const SAVE_PATH := "user://savegame.save"

## Save data to JSON file
func save_game(data: Dictionary) -> void:
    var save_file := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
    if save_file == null:
        push_error("Failed to open save file: " + str(FileAccess.get_open_error()))
        return
    
    var json_string := JSON.stringify(data, "\t")  # Pretty print
    save_file.store_line(json_string)
    save_file.close()
    print("Game saved successfully")

## Load data from JSON file
func load_game() -> Dictionary:
    if not FileAccess.file_exists(SAVE_PATH):
        push_warning("Save file does not exist")
        return {}
    
    var save_file := FileAccess.open(SAVE_PATH, FileAccess.READ)
    if save_file == null:
        push_error("Failed to open save file: " + str(FileAccess.get_open_error()))
        return {}
    
    var json_string := save_file.get_as_text()
    save_file.close()
    
    var json := JSON.new()
    var parse_result := json.parse(json_string)
    if parse_result != OK:
        push_error("JSON Parse Error: " + json.get_error_message())
        return {}
    
    return json.data as Dictionary

## Delete save file
func delete_save() -> void:
    if FileAccess.file_exists(SAVE_PATH):
        DirAccess.remove_absolute(SAVE_PATH)
        print("Save file deleted")
```

2. Implement `save_data()` and `load_data()` on persistent nodes:

```gdscript
# player.gd
extends CharacterBody2D

var health: int = 100
var score: int = 0
var level: int = 1

func save_data() -> Dictionary:
    return {
        "health": health,
        "score": score,
        "level": level,
        "position": {
            "x": global_position.x,
            "y": global_position.y
        }
    }

func load_data(data: Dictionary) -> void:
    health = data.get("health", 100)
    score = data.get("score", 0)
    level = data.get("level", 1)
    if data.has("position"):
        global_position = Vector2(
            data.position.x,
            data.position.y
        )
```

3. Trigger save/load from a game manager:

```gdscript
# game_manager.gd
extends Node

func save_game_state() -> void:
    var save_data := {
        "player": $Player.save_data(),
        "timestamp": Time.get_unix_time_from_system(),
        "version": "1.0.0"
    }
    SaveManager.save_game(save_data)

func load_game_state() -> void:
    var data := SaveManager.load_game()
    if data.is_empty():
        print("No save data found, starting new game")
        return
    
    if data.has("player"):
        $Player.load_data(data.player)
```

### Step 3: Implement Binary Save System (Pattern 2 — Advanced, Faster)

Use this for large save files or when human-readability isn't needed:

```gdscript
const SAVE_PATH := "user://savegame.dat"

func save_game_binary(data: Dictionary) -> void:
    var save_file := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
    if save_file == null:
        return
    
    save_file.store_var(data, true)  # true = full objects
    save_file.close()

func load_game_binary() -> Dictionary:
    if not FileAccess.file_exists(SAVE_PATH):
        return {}
    
    var save_file := FileAccess.open(SAVE_PATH, FileAccess.READ)
    if save_file == null:
        return {}
    
    var data: Dictionary = save_file.get_var(true)
    save_file.close()
    return data
```

### Step 4: Implement PERSIST Group Pattern (Pattern 3)

For auto-saving nodes tagged with the `persist` group:

1. Add nodes to the `persist` group in the editor or via code:

```gdscript
add_to_group("persist")
```

2. Implement `save()` and `load()` in each persistent node:

```gdscript
func save() -> Dictionary:
    return {
        "filename": get_scene_file_path(),
        "parent": get_parent().get_path(),
        "pos_x": position.x,
        "pos_y": position.y,
    }

func load(data: Dictionary) -> void:
    position = Vector2(data.pos_x, data.pos_y)
```

3. SaveManager collects all persist nodes:

```gdscript
func save_all_persist_nodes() -> void:
    var save_nodes := get_tree().get_nodes_in_group("persist")
    var save_dict := {}
    
    for node in save_nodes:
        if not node.has_method("save"):
            continue
        save_dict[node.name] = node.save()
    
    save_game(save_dict)
```

### Step 5: Version Your Save Format

```gdscript
const SAVE_VERSION := "1.0.0"

func save_game(data: Dictionary) -> void:
    data["version"] = SAVE_VERSION
    # ... save logic

func load_game() -> Dictionary:
    var data := # ... load logic
    if data.get("version") != SAVE_VERSION:
        push_warning("Save version mismatch, migrating...")
        data = migrate_save_data(data)
    return data
```

Load `scripts/save_migration_manager.gd` before implementing `migrate_save_data()`.

### Step 6: Add Encryption (Optional)

Load `scripts/save_system_encryption.gd` first, then:

```gdscript
func save_encrypted(data: Variant, password: String) -> void:
    var file := FileAccess.open_encrypted_with_pass(SAVE_PATH, FileAccess.WRITE, password)
    if file:
        file.store_var(data, true)
        file.close()
```

### Step 7: Add Rolling Backup Slots

```gdscript
func _create_backup() -> void:
    if FileAccess.file_exists(SAVE_PATH):
        DirAccess.copy_absolute(SAVE_PATH, BACKUP_PATH)

func safe_save(data: Variant) -> void:
    _create_backup()
    save_encrypted(data, "pass")
```

### Step 8: Add Integrity Validation (SHA-256)

```gdscript
func verify_save_integrity(path: String, expected_hash: String) -> bool:
    var current_hash := FileAccess.get_sha256(path)
    return current_hash == expected_hash

func load_with_validation() -> Variant:
    if not verify_save_integrity(SAVE_PATH, stored_hash):
        return _load_from_backup()
    return load_encrypted(SAVE_PATH, "pass")
```

### Step 9: Auto-Save Pattern

```gdscript
var auto_save_timer: Timer

func _ready() -> void:
    auto_save_timer = Timer.new()
    add_child(auto_save_timer)
    auto_save_timer.wait_time = 300.0
    auto_save_timer.timeout.connect(_on_auto_save)
    auto_save_timer.start()

func _on_auto_save() -> void:
    save_game_state()
    print("Auto-saved")
```

## Pitfalls

### NEVER Do (Hard Rules)

1. **NEVER save without a version field** — Old saves will break on schema changes. Always include `"version": "1.0.0"` and implement migration logic.
2. **NEVER use absolute OS paths** — Hardcoding `C:/Users/...` breaks on every other machine. Always use `user://`.
3. **NEVER attempt to save Node references directly** — Nodes are objects, not raw data. Extract primitives (positions, health, levels) into a `Dictionary` or `Resource`.
4. **NEVER forget to close FileAccess handles** — Explicit `close()` is safer for long-running logic, even though Godot 4 auto-closes on scope exit.
5. **NEVER use JSON for very large binary data** — Base64 in JSON is slow and bloated. Use `store_var()` or separate asset files.
6. **NEVER trust loaded data without validation** — Users can edit save files. Always use `data.get("field", default_value)` and validate ranges.
7. **NEVER trigger a save during high-frequency physics or animation updates** — A crash mid-write corrupts the file. Save only on explicit game events (menu, level end, checkpoint).
8. **NEVER modify a save Dictionary while iterating over its keys** — Calling `erase()` or `add()` inside a loop over the same dictionary causes iteration errors. Use `data.duplicate()`.
9. **NEVER store raw passwords or sensitive credentials in unencrypted JSON** — Use `FileAccess.open_encrypted_with_pass()`.
10. **NEVER use `ResourceLoader.load()` for massive scenes on the main thread** — It causes a visible freeze. Use `ResourceLoader.load_threaded_request()`.
11. **NEVER rely on `get_instance_id()` for cross-session identification** — Runtime IDs change on restart. Generate persistent `String` UUIDs.
12. **NEVER forget to call `duplicate(true)` on a loaded Resource stats block** — Multiple enemies loading the same `goblin_stats.tres` will share one health pool unless duplicated.
13. **NEVER use the `"allow_objects"` flag in `store_var`/`get_var` for untrusted data** — Full object decoding is a security risk for downloaded saves.
14. **NEVER use JSON for data requiring strict type preservation** — JSON converts `Vector3` to a string or dictionary. Use `var_to_bytes()` or binary format.
15. **NEVER leave internal metadata (`set_meta`) in persistent dictionaries** — It inflates save file size. Clean dictionaries before serialization.

### Common Gotchas

**Saved Vector2/Vector3 not loading correctly:**
```gdscript
# ✅ Store as x, y, z components
"position": {"x": pos.x, "y": pos.y}
# Then reconstruct:
position = Vector2(data.position.x, data.position.y)
```

**Resource paths not resolving:**
```gdscript
# ✅ Store resource paths as strings
"texture_path": texture.resource_path
# Then reload:
texture = load(data.texture_path)
```

## Verification

### Verify Save File Exists (PowerShell)

```powershell
# Check the user:// save location on Windows
$savePath = "$env:APPDATA\Godot\app_userdata\YOUR_PROJECT_NAME\savegame.save"
Test-Path $savePath
```

Expected output: `True` after a successful save.

### Verify JSON Content (PowerShell)

```powershell
Get-Content "$env:APPDATA\Godot\app_userdata\YOUR_PROJECT_NAME\savegame.save" | ConvertFrom-Json
```

Expected: A PowerShell object with fields matching your save schema, including a `version` field.

### In-Engine Test

```gdscript
func _ready() -> void:
    if OS.is_debug_build():
        test_save_load()

func test_save_load() -> void:
    var test_data := {"test_key": "test_value", "number": 42}
    save_game(test_data)
    var loaded := load_game()
    assert(loaded.test_key == "test_value")
    assert(loaded.number == 42)
    print("Save/Load test passed")
```

Expected console output: `Save/Load test passed`

### Verify Integrity Hash (PowerShell)

```powershell
Get-FileHash "$env:APPDATA\Godot\app_userdata\YOUR_PROJECT_NAME\savegame.save" -Algorithm SHA256
```

Compare the hash against the stored `expected_hash` value.

## Related Skills

- **godot-master** — Master Godot skill with cross-cutting patterns. See `../godot-master/SKILL.md`.
- **godot-scene-management** — For threaded scene loading patterns referenced in this skill.
