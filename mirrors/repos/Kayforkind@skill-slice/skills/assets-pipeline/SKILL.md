---
name: assets-pipeline
version: 1.1.1
description: "Configures Godot 4.x import-time assets: texture compression, glTF/.blend scenes, WAV/Ogg, .tres/.res, and .import sidecars plus headless reimport. Use when importing textures, glTF, blend, wav/ogg, tres/res, or running godot --headless --import. Not for runtime audio buses (audio-system), 3D materials/lighting (3d-essentials), 2D sprites (2d-essentials), animation playback, or WASM/web export."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## When to Use

Use this skill when working with asset import and management in Godot 4.x, including:

- **Image / texture import** — choosing between lossless and VRAM-compressed modes, filtering, and mipmaps. The right choice depends on whether the texture is 2D UI/pixel art (where sharpness matters) or a 3D surface (where GPU memory and sampling cost matter).
- **3D scene import** — bringing in glTF 2.0 (`.glb` / `.gltf`) or `.blend` files and configuring scale, generated collision shapes, and LODs. Import-time decisions here are hard to change later because they bake into the cached scene.
- **Audio import** — selecting a format per use case (short SFX vs. music) and setting loop points / normalization, which the engine cannot infer on its own.
- **Resource format selection** — deciding between `.tres` (text) and `.res` (binary) based on whether you value version-control diffs or load speed/size.
- **Import pipeline configuration** — understanding sidecar `.import` files, the regenerated `.godot/imported/` cache, and how to reimport reliably (including in CI).

## Do Not Use

These topics live in other skills because they concern *runtime behavior*, not *import-time configuration*:

- For audio **playback** logic and bus routing → use the **audio-system** skill.
- For 3D **material and lighting** setup → use the **3d-essentials** skill.
- For 2D **rendering and sprite** composition → use the **2d-essentials** skill.
- For **animation playback** wiring → use the **animation-system** skill.
- For assets that need **WASM / web export** tuning → use the **web-export** skill.
- For **AI-generated assets**, verify copyright/licensing before integrating; this skill assumes you already have the right to ship the asset.

## Prerequisites

- Godot 4.x editor installed and on `PATH` (or invoke the binary directly).
- A Godot project with a `project.godot` file at the root.
- Git initialized in the project root (for `.gitignore` and VCS checks).
- Windows host is primary (PowerShell). Commands below use PowerShell syntax; adapt for bash on other platforms.

## Procedure

### 1. Understand the three-part import system

When you drop a file into `res://`, Godot auto-imports it into an engine-optimized form. Understanding *where* each piece lives explains the version-control rules:

```
project/
├── textures/
│   ├── player.png           ← original source file (commit this)
│   └── player.png.import     ← import settings sidecar (commit this)
└── .godot/
    └── imported/             ← compiled, machine-specific cache (do NOT commit)
```

- The **original** is your source of truth.
- The **`.import` sidecar** records *how* to transform the original (compression mode, filter, etc.). It is small, text-based, and belongs in version control so every teammate and CI machine reproduces the same import.
- The **`.godot/imported/` cache** is regenerated from the first two. It is large and machine-specific, so committing it only causes merge conflicts and bloat.

### 2. Configure `.gitignore` (Windows PowerShell)

```powershell
# From the project root:
if (-not (Test-Path .gitignore)) { New-Item -ItemType File .gitignore }
$lines = Get-Content .gitignore -ErrorAction SilentlyContinue
if ($lines -notcontains ".godot/") {
    Add-Content .gitignore "`n# Godot import cache (regenerated locally)`n.godot/"
    Write-Host "Added .godot/ to .gitignore"
} else {
    Write-Host ".godot/ already in .gitignore"
}
```

### 3. Change import settings in the editor

1. Select the file in the **FileSystem** dock.
2. Open the **Import** dock (docked next to the Scene dock by default). It shows only the settings relevant to that file's type.
3. Adjust settings. Changing the *Preset* (e.g. **2D Pixel** vs **3D**) flips several options at once toward a sensible default for that use case.
4. Click **Reimport**. Select multiple files first to reimport them in one pass when applying the same change broadly.

### 4. Image import — choose mode per use case

| Use case | Mode | Filter | Mipmaps | Notes |
|---|---|---|---|---|
| Pixel art / 2D UI | Lossless | Nearest | Off | Set project-wide: Project Settings > Rendering > Textures > Default Texture Filter → Nearest. Pair with "Snap 2D Transforms to Pixel". |
| 3D surface (color/albedo) | VRAM Compressed | Linear | On | Uses S3TC/BPTC on desktop, ASTC/ETC2 on mobile. |
| 3D normal map | VRAM Compressed (Normal) | Linear | On | Dedicated normal-map compression avoids artifacts. |
| HDR / skybox | Lossless (HDR) | Linear | On | Keep full precision for lighting. |

### 5. 3D scene import — glTF 2.0 and .blend

1. Drop `.glb`, `.gltf`, or `.blend` into `res://`.
2. Select the file in the FileSystem dock and open the Import dock.
3. Set **Root Type** if the root should be a specific node (e.g. `RigidBody3D`).
4. Set **Root Scale** to match your project's unit convention (Godot 1 unit = 1 meter; Blender default is also 1 meter since Blender 2.8).
5. Enable **Generate > Collisions** if the mesh needs physics shapes baked at import.
6. Configure **LODs** if the mesh has multiple decimation levels.
7. Click **Reimport**. These settings bake into the cached scene — changing them later requires a full reimport.

### 6. Audio import — format by use case

| Use case | Format | Why |
|---|---|---|
| Short SFX (jumps, hits, clicks) | WAV (uncompressed) | Tiny on disk, zero decode latency, fires instantly. |
| Music / long tracks | Ogg Vorbis (`.ogg`) | File-size win outweighs small decode cost. Set loop points manually. |
| Voiceover (streamed) | MP3 or Ogg | Streaming from disk avoids loading the entire clip into RAM. |

> The engine cannot guess loop points. Unset loop points cause audible gaps at track boundaries. Set them in the Import dock or in the AudioStreamOggVorbis resource's `loop_offset` property.

### 7. Resource format — .tres vs .res

- **`.tres` (text):** Use for data you want to diff and merge in version control — items, dialogue, tuning tables.
- **`.res` (binary):** Use for large or performance-sensitive data where load speed and size matter more than readability.
- Always check the `Error` return from `ResourceSaver.save()`. Silent write failures are the most common resource bug.

### 8. Headless reimport (CI / clean validation)

```powershell
# From the project root on Windows:
# Replace with your Godot binary path if not on PATH.
godot --headless --import --path .

# If Godot is not on PATH, invoke directly:
# & "C:\Program Files\Godot\Godot_v4.x-stable_win64.exe" --headless --import --path .
```

This reimports every asset from originals + sidecars without opening the editor UI. If it exits with code 0 and no errors in the log, the committed sources are self-sufficient.

### 9. Runtime loading patterns

#### Image — texture loading with validation

```gdscript
func load_texture(path: String) -> Texture2D:
    if path.is_empty():
        push_error("load_texture: empty path")
        return null
    if not ResourceLoader.exists(path, "Texture2D"):
        push_error("load_texture: no texture at '%s'" % path)
        return null

    var resource: Resource = load(path)
    var texture: Texture2D = resource as Texture2D
    if texture == null:
        push_error("load_texture: '%s' is not a Texture2D" % path)
        return null
    return texture

func apply_character_texture(sprite: Sprite2D, path: String) -> void:
    if sprite == null:
        push_error("apply_character_texture: null sprite")
        return

    var texture: Texture2D = load_texture(path)
    if texture == null:
        return  # load_texture already reported why; keep the existing texture
    sprite.texture = texture
```

#### 3D scene — synchronous preload and threaded async load

```gdscript
# preload() resolves at parse time, so a missing or corrupt model fails the
# moment this script is first loaded rather than mid-gameplay.
const ENEMY_SCENE: PackedScene = preload("res://models/enemy.glb")

# Large meshes can stall the main thread if loaded synchronously, so stream
# them on a background thread and poll the status.
func spawn_model_async(path: String) -> Node3D:
    if path.is_empty():
        push_error("spawn_model_async: empty path")
        return null

    var request_error: Error = ResourceLoader.load_threaded_request(path, "PackedScene")
    if request_error != OK:
        push_error("spawn_model_async: could not queue '%s' (error %d)" % [path, request_error])
        return null

    var tree: SceneTree = Engine.get_main_loop() as SceneTree
    if tree == null:
        push_error("spawn_model_async: no active SceneTree to await frames on")
        return null

    var progress: Array = []
    while true:
        var status: ResourceLoader.ThreadLoadStatus = ResourceLoader.load_threaded_get_status(path, progress)
        if status == ResourceLoader.THREAD_LOAD_IN_PROGRESS:
            await tree.process_frame
            continue
        if status != ResourceLoader.THREAD_LOAD_LOADED:
            push_error("spawn_model_async: failed to load '%s' (status %d)" % [path, status])
            return null
        break

    var scene: PackedScene = ResourceLoader.load_threaded_get(path) as PackedScene
    if scene == null:
        push_error("spawn_model_async: '%s' did not resolve to a PackedScene" % path)
        return null

    var instance: Node3D = scene.instantiate() as Node3D
    if instance == null:
        push_error("spawn_model_async: root of '%s' is not a Node3D" % path)
        return null
    return instance
```

#### Audio — preload and play with guards

```gdscript
const JUMP_SFX: AudioStream = preload("res://audio/jump.wav")

@onready var _sfx_player: AudioStreamPlayer = $AudioStreamPlayer

func play_jump() -> void:
    if JUMP_SFX == null:
        push_error("play_jump: jump SFX failed to preload")
        return
    if _sfx_player == null:
        push_error("play_jump: missing child AudioStreamPlayer named 'AudioStreamPlayer'")
        return

    _sfx_player.stream = JUMP_SFX
    _sfx_player.play()
```

#### Resource — typed save/load with .tres and .res

```gdscript
# item_data.gd
class_name ItemData
extends Resource

@export var id: StringName = &""
@export var display_name: String = ""
@export var max_stack: int = 1
```

```gdscript
# item_repository.gd
extends Node

func save_item_text(item: ItemData, path: String) -> bool:
    if item == null:
        push_error("save_item_text: null item")
        return false
    if not path.ends_with(".tres"):
        push_error("save_item_text: expected a .tres path, got '%s'" % path)
        return false

    var result: Error = ResourceSaver.save(item, path)
    if result != OK:
        push_error("save_item_text: failed to save '%s' (error %d)" % [path, result])
        return false
    return true

func save_item_binary(item: ItemData, path: String) -> bool:
    if item == null:
        push_error("save_item_binary: null item")
        return false
    if not path.ends_with(".res"):
        push_error("save_item_binary: expected a .res path, got '%s'" % path)
        return false

    var flags: int = ResourceSaver.FLAG_COMPRESS | ResourceSaver.FLAG_BUNDLE_RESOURCES
    var result: Error = ResourceSaver.save(item, path, flags)
    if result != OK:
        push_error("save_item_binary: failed to save '%s' (error %d)" % [path, result])
        return false
    return true

func load_item(path: String) -> ItemData:
    if not ResourceLoader.exists(path):
        push_error("load_item: no resource at '%s'" % path)
        return null

    var resource: Resource = load(path)
    var item: ItemData = resource as ItemData
    if item == null:
        push_error("load_item: '%s' is not an ItemData resource" % path)
        return null
    return item
```

## Pitfalls

- **Never hand-edit files in `.godot/imported/`.** They are derived artifacts; the engine overwrites them on the next reimport, so any manual change is silently lost.
- **Commit `.import` sidecars and original assets together.** A sidecar without its source (or vice versa) produces a broken import on a fresh checkout.
- **Keep `.godot/` in `.gitignore`.** The cache is reproducible locally, so tracking it adds noise without benefit. Committing it causes merge conflicts on every reimport.
- **3D import settings bake into the cached scene.** Changing scale, collision generation, or LODs after import requires a full reimport — catch these at import time to avoid rework.
- **Audio loop points are not inferred.** Unset loop points on Ogg Vorbis tracks cause audible gaps. Set them explicitly in the Import dock or via `loop_offset`.
- **Texture compression is platform-specific.** Mobile typically uses ASTC/ETC2 and desktop uses S3TC/BPTC. A texture that loads on one platform may need a different compression preset on another. Test on every target platform.
- **`ResourceSaver.save()` returns an `Error` — always check it.** Assuming the write succeeded is the most common resource bug. A silent failure means the file is stale or missing.
- **Pixel art shimmer.** If sprites land on a half-pixel and shimmer as the camera moves, enable "Snap 2D Transforms to Pixel" in Project Settings and set the default texture filter to Nearest.
- **Large synchronous loads stall the main thread.** Use `ResourceLoader.load_threaded_request` / `load_threaded_get_status` for large meshes or scenes loaded at runtime.
- **AI-generated or third-party assets.** Import success says nothing about your right to distribute the asset. Validate copyright/licensing before shipping.

## Verification

Run these checks from the project root on Windows (PowerShell):

### VCS hygiene

```powershell
# Confirm .godot/ is gitignored:
Select-String -Path .gitignore -Pattern "\.godot/" -Quiet
# Expected output: True

# Confirm no .godot/ files are tracked:
git ls-files .godot/
# Expected output: (empty — no tracked files under .godot/)

# Confirm every original asset has a committed .import sidecar:
$assets = Get-ChildItem -Recurse -Include *.png,*.jpg,*.wav,*.ogg,*.glb,*.gltf,*.blend -Path res:// 2>$null
foreach ($a in $assets) {
    $sidecar = "$($a.FullName).import"
    if (-not (Test-Path $sidecar)) { Write-Host "MISSING sidecar: $sidecar" }
}
# Expected output: (empty — every asset has its sidecar)
```

### Headless reimport from clean checkout

```powershell
# Remove the cache to simulate a fresh clone:
Remove-Item -Recurse -Force .godot -ErrorAction SilentlyContinue

# Reimport from originals + sidecars only:
godot --headless --import --path .
# Expected: exits with code 0, no ERROR lines in output.

# Confirm the cache was regenerated:
Test-Path .godot/imported
# Expected output: True
```

### Texture mode spot-check

```powershell
# Check a pixel-art texture's sidecar for lossless + nearest filter:
Select-String -Path "res://textures/player.png.import" -Pattern "lossless=true" -Quiet
# Expected: True

Select-String -Path "res://textures/player.png.import" -Pattern "filter/nearest" -Quiet
# Expected: True (or verify filter=0 in the sidecar)
```

### Audio format spot-check

```powershell
# Confirm SFX are WAV and music is Ogg:
Get-ChildItem -Recurse -Include *.wav -Path res://audio | Measure-Object | Select-Object -ExpandProperty Count
# Expected: > 0 (short SFX present)

Get-ChildItem -Recurse -Include *.ogg -Path res://audio | Measure-Object | Select-Object -ExpandProperty Count
# Expected: > 0 (music tracks present)
```

### Resource save/load round-trip

```gdscript
# In a tool script or editor console:
var item := ItemData.new()
item.id = &"test_sword"
item.display_name = "Test Sword"
item.max_stack = 1

var saved := save_item_text(item, "res://items/test_sword.tres")
assert(saved, "save_item_text failed")

var loaded := load_item("res://items/test_sword.tres")
assert(loaded != null, "load_item returned null")
assert(loaded.id == &"test_sword", "id mismatch")
print("Round-trip OK: %s" % loaded.display_name)
```

### Checklist

- [ ] Commit originals and their `.import` sidecars together; never commit `.godot/`.
- [ ] Confirm `.godot/` is listed in `.gitignore`.
- [ ] Reimport from a clean checkout (`godot --headless --import`) and confirm assets build with no errors.
- [ ] Verify texture import mode per use: lossless + Nearest for pixel art, VRAM-compressed + mipmaps for 3D surfaces.
- [ ] Check 3D import scale, generated collision shapes, and LODs.
- [ ] Confirm audio settings: short SFX as WAV, music as Ogg Vorbis with loop points set.
- [ ] Choose resource format deliberately: `.tres` for VCS-diffable data, `.res` for large/binary data.
- [ ] Test loading on every target platform (ASTC/ETC2 on mobile, S3TC/BPTC on desktop).
- [ ] Validate copyright/licensing for any AI-generated or third-party assets before shipping.

## Related Skills

- **audio-system** — audio playback and bus architecture (runtime side of imported audio).
- **3d-essentials** — 3D materials and lighting applied to imported meshes.
- **2d-essentials** — 2D rendering and sprites that consume imported textures.
- **animation-system** — driving animations that arrive inside imported scenes.
- **godot-optimization** — profiling and reducing asset-related memory/CPU cost.
- **multithreading** — patterns behind threaded resource loading.
- **web-export** — asset trade-offs specific to WASM/web builds.
- **ai-assets** — copyright-compliant integration of AI-generated assets.
