---
name: game-assets-pipeline
version: 1.1.1
description: "Sets Godot 4.x import-time settings: lossless versus VRAM textures, glTF and .blend scale, collision, and LODs, WAV versus Ogg, .tres versus .res, and committed .import sidecars rather than the imported cache. Use for reimport jobs, pixel-art filter fixes, 3D VRAM compression, or headless CI import. Not for runtime audio buses, materials, or sprite composition. Do not use as a WASM export tuner or as proof of rights to ship third-party art."
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

### Do not use here — these belong in other skills

These topics concern *runtime behavior*, not *import-time configuration*:

- Audio **playback** logic and bus routing → **audio-system** skill.
- 3D **material and lighting** setup → **3d-essentials** skill.
- 2D **rendering and sprite** composition → **2d-essentials** skill.
- **Animation playback** wiring → **animation-system** skill.
- Assets that need **WASM / web export** tuning → **web-export** skill.
- **AI-generated assets** — verify copyright/licensing before integrating; this skill assumes you already have the right to ship the asset.

## Prerequisites

- Godot 4.x project open or available on disk.
- For headless reimport (CI or validation): the Godot executable on your `PATH` or a full path to it.
- On Windows (PowerShell), the Godot executable is typically at a path like `C:\Godot\godot.exe` — adjust to your install location.
- Original asset files (`.png`, `.glb`, `.gltf`, `.blend`, `.wav`, `.ogg`, etc.) placed under `res://`.
- A `.gitignore` file at the project root (or willingness to create one).

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

### 2. Follow version-control conventions

- **Never hand-edit files in `.godot/imported/`.** They are derived artifacts; the engine overwrites them on the next reimport, so any manual change is silently lost.
- **Commit `.import` sidecars and original assets together.** A sidecar without its source (or vice versa) produces a broken import on a fresh checkout.
- **Keep `.godot/` in `.gitignore`.** The cache is reproducible locally, so tracking it adds noise without benefit.
- **Reimport from originals to validate, not from the cache.** If a clean checkout can rebuild every asset, you know the committed sources and sidecars are complete.

### 3. Change import settings in the editor

1. Select the file in the **FileSystem** dock.
2. Open the **Import** dock (docked next to the Scene dock by default). It shows only the settings relevant to that file's type, which is why texture options differ from audio options.
3. Adjust settings. Changing the *Preset* (e.g. **2D Pixel** vs **3D**) flips several options at once toward a sensible default for that use case.
4. Click **Reimport**. Select multiple files first to reimport them in one pass when applying the same change broadly.

### 4. Configure texture import per use case

| Use case | Compression | Filter | Mipmaps | Notes |
|---|---|---|---|---|
| 2D pixel art | Lossless | Nearest | Off | Set project-wide: Project Settings > Rendering > Textures > Default Texture Filter → Nearest. Pair with "Snap 2D Transforms to Pixel". |
| 2D UI / HD art | Lossless | Linear | Off | Crisp edges, no mipmap overhead. |
| 3D surface (color) | VRAM Compressed (S3TC/BPTC on desktop, ASTC/ETC2 on mobile) | Linear | On | Saves VRAM; mipmaps reduce aliasing at distance. |
| 3D normal map | VRAM Compressed (RGTC) | Linear | On | Use a normal-map-specific compression to avoid artifacts. |

### 5. Configure 3D scene import (glTF 2.0 / .blend)

1. Select the `.glb`, `.gltf`, or `.blend` file in the **FileSystem** dock.
2. In the **Import** dock, set the **Root Type** if you need a specific node type (default is `Node3D`).
3. Set **Scale** to match your project's unit convention (Godot default is 1 unit = 1 meter).
4. Enable **Generate > Collision Shape** if the mesh needs physics collision baked at import.
5. Configure **LODs** if the mesh supports them — these bake into the cached scene and are hard to change later.
6. Click **Reimport**.

### 6. Configure audio import per use case

| Use case | Format | Why |
|---|---|---|
| Short SFX (jumps, hits, UI clicks) | WAV (uncompressed) | Tiny on disk, zero decode latency, fires instantly. |
| Music / long ambient tracks | Ogg Vorbis (`.ogg`) | File-size win outweighs small decode cost. |

- Set **Loop** on music tracks in the Import dock. The engine cannot guess loop points, so unset ones cause audible gaps.
- Enable **Normalize** if the source audio has inconsistent loudness levels.

### 7. Choose resource format

| Format | When to use | Why |
|---|---|---|
| `.tres` (text) | Data you want to diff and merge in VCS — items, dialogue, tuning tables | Human-readable, diffable. |
| `.res` (binary) | Large or performance-sensitive data | Faster load, smaller file, not readable. |

### 8. Reimport in CI / headless validation

On Windows (PowerShell):

```powershell
# Replace with your Godot executable path
& "C:\Godot\godot.exe" --headless --import --path "C:\path\to\project"
```

On Linux/macOS:

```bash
godot --headless --import --path /path/to/project
```

This rebuilds the `.godot/imported/` cache from committed originals and sidecars. If it completes with no errors, your committed assets are self-sufficient.

### 9. Runtime loading with validation (GDScript examples)

#### Image import — texture loading with validation

```gdscript
# Pixel-art projects want crisp, unfiltered texels. Set the filter once,
# project-wide, instead of overriding every sprite by hand:
#   Project Settings > Rendering > Textures > Default Texture Filter -> Nearest
# Pair it with "Snap 2D Transforms to Pixel" so sprites never land on a
# half-pixel and shimmer as the camera moves.

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

#### 3D scene import — glTF 2.0, synchronous and threaded

```gdscript
# preload() resolves at parse time, so a missing or corrupt model fails the
# moment this script is first loaded rather than mid-gameplay. Use it for
# assets you always need.
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

#### Audio import — format chosen by use case

```gdscript
# Short, frequently-triggered SFX (jumps, hits) are best kept as uncompressed
# WAV: tiny on disk and zero decode latency, so they fire instantly. Reserve
# Ogg Vorbis for longer music tracks, where the file-size win outweighs the
# small decode cost.
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

#### Resource formats — typed save/load

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

# Use .tres (text) for data you want to diff and merge in version control —
# items, dialogue, tuning tables. Use .res (binary) for large or
# performance-sensitive data where load speed and size matter more than
# readability. ResourceSaver.save() returns an Error, so check it every time.
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

    # Compress to shrink the file; bundle sub-resources so the saved file is
    # self-contained and does not depend on external paths at load time.
    var flags: int = ResourceSaver.FLAG_COMPRESS | ResourceSaver.FLAG_BUNDLE_RESOURCES
    var result: Error = ResourceSaver.save(item, path, flags)
    if result != OK:
        push_error("save_item_binary: failed to save '%s' (error %d)" % [path, result])
        return false
    return true

# Validate the resource is the subclass you expect before handing it back.
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

- **Hand-editing `.godot/imported/` files** — the engine overwrites them on the next reimport; any manual change is silently lost. Never do this.
- **Committing `.godot/` to version control** — the cache is large, machine-specific, and reproducible. It only causes merge conflicts and repo bloat. Keep it in `.gitignore`.
- **Committing a sidecar without its source (or vice versa)** — a fresh checkout will have a broken import. Always commit `.import` files and their original assets together.
- **Wrong texture compression for the platform** — mobile typically uses ASTC/ETC2 and desktop uses S3TC/BPTC. A texture that loads on one may need a different compression on another. Test on every target platform.
- **Using Linear filter on pixel art** — causes blur. Set Default Texture Filter → Nearest project-wide and enable "Snap 2D Transforms to Pixel".
- **Missing mipmaps on 3D surfaces** — causes aliasing/shimmer at distance. Enable mipmaps for 3D color and normal maps.
- **Unset audio loop points** — the engine cannot guess them. Music tracks will have audible gaps at the loop boundary. Set loop points in the Import dock.
- **Using Ogg Vorbis for short SFX** — adds decode latency that can delay time-critical sounds. Use WAV for short, frequently-triggered effects.
- **Ignoring `ResourceSaver.save()` return code** — silent write failures go unnoticed. Always check the returned `Error`.
- **Baking 3D import settings (collision, LODs) incorrectly** — these bake into the cached scene and are hard to change later. Verify scale, collision, and LOD settings before clicking Reimport.
- **Assuming import success means you have distribution rights** — import success says nothing about copyright/licensing. Validate rights for AI-generated or third-party assets before shipping.

## Verification

Each check below states *what* to confirm and *why* it matters:

- [ ] **Commit originals and their `.import` sidecars together; never commit `.godot/`.** A missing sidecar yields a broken import on a fresh clone, while a committed cache only causes merge churn.
- [ ] **Confirm `.godot/` is listed in `.gitignore`.** This keeps the regenerated cache out of version control.
  ```powershell
  # PowerShell — check if .godot is gitignored
  Get-Content .gitignore | Select-String ".godot"
  ```
- [ ] **Reimport from a clean checkout and confirm assets build with no errors.** This proves the committed sources and sidecars are self-sufficient.
  ```powershell
  & "C:\Godot\godot.exe" --headless --import --path "C:\path\to\project"
  ```
  Expected: command exits with code 0 and prints no ERROR lines.
- [ ] **Verify texture import mode per use:** lossless + Nearest filter for pixel art, VRAM-compressed + mipmaps for 3D surfaces. The wrong mode shows up as blur, aliasing, or wasted VRAM.
- [ ] **Check 3D import scale, generated collision shapes, and LODs.** These bake into the cached scene, so catching them at import time avoids rework later.
- [ ] **Confirm audio settings:** short SFX as WAV for low latency, music as Ogg Vorbis with loop points set. Unset loop points cause audible gaps.
- [ ] **Choose resource format deliberately:** `.tres` for VCS-diffable data, `.res` for large/binary data; have tooling check `ResourceSaver.save()` return codes so silent write failures are caught.
- [ ] **Test loading on every target platform.** Mobile typically uses ASTC/ETC2 and desktop uses S3TC/BPTC, so a texture that loads on one may need a different compression on another.
- [ ] **Validate copyright/licensing for any AI-generated or third-party assets** before shipping, since import success says nothing about your right to distribute the asset.

## Related skills

- **audio-system** — audio playback and bus architecture (runtime side of imported audio).
- **3d-essentials** — 3D materials and lighting applied to imported meshes.
- **2d-essentials** — 2D rendering and sprites that consume imported textures.
- **animation-system** — driving animations that arrive inside imported scenes.
- **godot-optimization** — profiling and reducing asset-related memory/CPU cost.
- **multithreading** — patterns behind threaded resource loading.
- **web-export** — asset trade-offs specific to WASM/web builds.
- **ai-assets** — copyright-compliant integration of AI-generated assets.
