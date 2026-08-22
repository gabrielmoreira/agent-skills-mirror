---
name: godot-builder
description: "Expert-level toolkit for modular Godot 4.7+ CLI automation and headless build orchestration. Use when you need to: (1) Build complex scene trees or UI layouts programmatically, (2) Automate expert 3D asset pipelines (glTF -> Collision), (3) Optimize procedural geometry headlessly (CSG -> Static Mesh), or (4) Engineer production-grade CI/CD pipelines. Set GODOT_PATH env var for custom engine location. Keywords: Godot CLI, headless, CI, export, builder, 4.7."
---

# Godot Builder Skill

The `godot-builder` skill provides an expert-grade foundation for programmatic game development and headless automation using the Godot 4.7-stable CLI. Override paths via `GODOT_PATH` and `GODOT_CONSOLE_PATH` environment variables.

## Expert Automation Mindset

- **Headless Isolation via XDG**: When running multiple concurrent Godot instances, always override `XDG_DATA_HOME` and `XDG_CONFIG_HOME` to prevent cache corruption between instances.
- **Cache Invalidation (Force Import)**: Programmatically delete the `.godot/imported/` directory to force the engine to re-evaluate modified global import settings.
- **Explicit Ownership**: Scene nodes MUST have their `owner` property set to the scene root, or they will be discarded during serialization.
- **Latency-Sensitive Multi-threading**: GPU interactions (textures, image data) must stay on the main thread to avoid pipeline stalls and deadlocks.

## Hardened Anti-Patterns (NEVER List)

- **NEVER** save runtime-generated UIDs headlessly; `ResourceSaver.save()` does NOT serialize UIDs in headless mode. Invoke `godot -e --headless --import` as a post-process.
- **NEVER** use `Resource.duplicate(true)` in Godot 4.4+; use `duplicate_deep(Resource.DEEP_DUPLICATE_ALL)` to prevent procedural state-bleed.
- **NEVER** hardcode `.tscn` or `.tres` extensions; always load via `uid://` or without extensions to avoid failures in exported binary builds.
- **NEVER** execute GPU-bound calls on secondary threads. Use `RenderingServer.call_on_render_thread()`.
- **NEVER** enable the Shader Baker for Dedicated Server builds; the headless backend ignores it.
- **NEVER** call `ResourceUID.set_id()` without calling `has_id()` first; it causes a fatal CLI crash.
- **NEVER** skip `RenderingServer.canvas_item_reset_physics_interpolation()` when programmatically moving low-level CanvasItems on their first frame; failure causes visual desync between rendering and physics systems.

## Expert Automation Workflows

> **Do NOT Load** the full script catalog for a single task. Load only the MANDATORY scripts named in the active workflow. Thin process wrappers (`builder_launch_editor.py`, `builder_run_project.py`, `builder_stop_project.py`, `get_*`, `builder_list_projects.py`) live in the appendix — do not preload them unless that exact CLI action is required.

### Workflow #1: The Hardened 3D Asset Pipeline
**Purpose**: Automates the ingestion of raw 3D assets into production-ready scenes with accurate physics collisions.
- **MANDATORY — read before improvising CLI flags**: [builder_gltf_processor.py](../scripts/builder_gltf_processor.py) → [builder_collision_generator.py](../scripts/builder_collision_generator.py) → [builder_save_scene.py](../scripts/builder_save_scene.py). Then run `godot -e --headless --import` (or [builder_import_automator.py](../scripts/builder_import_automator.py)) — do not invent alternate flag orders.
- **Sequence**: `builder_gltf_processor.py` -> `builder_collision_generator.py` -> `builder_save_scene.py` -> headless `--import`.
- **Expert Defense**: Sets explicit `owner` for every node. Forces a final headless import to fix the missing UID serialization.
- **Failure modes / fallbacks**:
  - **UID missing after headless save**: Expected — `ResourceSaver` does not serialize UIDs headless. Fallback: re-run `--import`; if UIDs still missing, run [builder_update_project_uids.py](../scripts/builder_update_project_uids.py) after import completes.
  - **Import hangs / never exits**: Script omitted `quit()` or editor import is waiting on GPU. Fallback: ensure the post-process script calls `get_tree().quit()`; kill the PID via [builder_stop_project.py](../scripts/builder_stop_project.py) and retry with `XDG_*` isolation.
  - **Collision mesh empty / wrong**: Source glTF had no mesh arrays or wrong node paths. Fallback: inspect [builder_gltf_processor.py](../scripts/builder_gltf_processor.py) output scene before regenerating collisions.

### Workflow #2: Procedural Level Optimization & 4.4+ Scaling
**Purpose**: Generates optimized procedural level chunks without shared resource state corruption between instances.
- **MANDATORY — read before improvising**: [builder_csg_optimizer.py](../scripts/builder_csg_optimizer.py) → [builder_navmesh_baker.py](../scripts/builder_navmesh_baker.py). Apply `duplicate_deep(Resource.DEEP_DUPLICATE_ALL)` between bake steps — do not use `duplicate(true)`.
- **Sequence**: `builder_csg_optimizer.py` -> `duplicate_deep(ALL)` -> `builder_navmesh_baker.py`.
- **Expert Defense**: Uses `duplicate_deep` to isolate materials/resources. Bakes CSG to static geometry before triggering NavMesh pathfinding.
- **Failure modes / fallbacks**:
  - **NavMesh bake on live CSG**: Pathfinding holes / empty regions. Fallback: confirm CSG→static mesh bake finished before [builder_navmesh_baker.py](../scripts/builder_navmesh_baker.py).
  - **Material/state bleed across chunks**: Used shallow duplicate. Fallback: re-bake with `DEEP_DUPLICATE_ALL` per instance.
  - **Headless bake hang**: Missing `quit()` after bake. Fallback: add explicit quit; isolate via `XDG_DATA_HOME` / `XDG_CONFIG_HOME`.

### Workflow #3: Production CI/CD & Force-Import Validation
**Purpose**: Validates cross-platform builds and ensures global project settings (VRAM compression) are strictly applied.
- **MANDATORY — read before improvising export flags**: [builder_test_runner.py](../scripts/builder_test_runner.py) → [builder_profile_generator.py](../scripts/builder_profile_generator.py) → [builder_ci_export_prepper.gd](../scripts/builder_ci_export_prepper.gd) → [builder_ci_exporter.py](../scripts/builder_ci_exporter.py).
- **Sequence**: `rm -rf .godot/imported` -> `builder_test_runner.py` -> `builder_profile_generator.py` -> `builder_ci_exporter.py`.
- **Expert Defense**: Forces full re-import to validate asset compression. Isolates CI runs via XDG variables. Injects secure keystore paths from environment variables.
- **Failure modes / fallbacks**:
  - **Export preset missing / wrong platform**: `export_presets.cfg` not mutated for the target. Fallback: run [builder_ci_export_prepper.gd](../scripts/builder_ci_export_prepper.gd) headlessly before `--export-release`; verify preset name matches CI matrix.
  - **Hung headless CI (no exit)**: Script never called `quit()`. Fallback: always end `-s` scripts with `quit()`; treat non-zero hang as kill + retry with XDG isolation.
  - **UID / import validation fail after cache wipe**: Re-import incomplete. Fallback: re-run `--import`, then [builder_update_project_uids.py](../scripts/builder_update_project_uids.py); do not export until import finishes cleanly.

---

## Automation & CI/CD Pipelines (Godot 4.7)

Professional Godot building requires a "Zero-Touch" philosophy for assets and binary exports.

### 1. Programmatic Asset Re-import
- **NEVER** manually select 500 textures to change their compression.
- Use `ConfigFile` to mutate `.import` files and `EditorFileSystem.reimport_files()` to trigger a batch update on the main thread safely.

### 2. Orphan Asset Detection (Slop Scan)
- **NEVER** trust `res://` is clean. Over time, deleted scenes leave behind orphaned textures and sounds that bloat the final build.
- Use `ResourceLoader.get_dependencies()` to recursively trace exactly which assets are linked to your "Main Scene" and flag anything else as slop.

### 3. Headless CI/CD Context
- Use `--headless --script` for versioning tasks (mutating `export_presets.cfg`) before running the final `--export-release`.
- **Tip**: Always call `quit()` at the end of a headless script, or your CI runner will hang indefinitely.

---

## Expert Pipeline Scripts (load on demand)

Primary automation scripts — open only when the matching workflow requires them.

### Scene & Asset Pipelines
- **builder_gltf_processor.py**: Headlessly converts raw `.glb/.gltf` assets into Godot Scenes.
- **builder_collision_generator.py**: Generates `ConcavePolygonShape3D` physics from mesh data.
- **builder_save_scene.py**: Safely packs and persists the current node tree to disk (set `owner` first).
- **builder_csg_optimizer.py**: Bakes procedural CSG boolean operations into static meshes.
- **builder_navmesh_baker.py**: Executes asynchronous headless NavMesh pathfinding baking.
- **builder_tilemap_generator.py**: Procedurally builds TileMapLayer grids from JSON data.
- **builder_ui_assembler.py**: Constructs complex GUI layouts from standardized JSON structures.
- **builder_create_scene.py** / **builder_add_node.py** / **builder_load_sprite.py**: Programmatic scene tree builders.
- **builder_export_mesh_library.py**: Converts 3D scenes into `.meshlib` resources for GridMaps.
- **builder_orphan_asset_scanner.gd**: Recursive dependency tracer for identifying unused resources.

### CI / Import / Export Pipelines
- **builder_ci_exporter.py**: Orchestrates multi-platform release exports headlessly.
- **builder_ci_export_prepper.gd**: Headless versioning script for `export_presets.cfg`.
- **builder_profile_generator.py**: Generates feature profiles for module-stripping optimization.
- **builder_test_runner.py**: Executes headless unit and integration tests (GUT/doctest).
- **builder_import_automator.py** / **builder_asset_reimport_utility.gd**: Batch import enforcement.
- **builder_update_project_uids.py** / **builder_get_uid.py**: UID sync after headless saves.
- **builder_config_compiler.py**: Compiles JSON/CSV data into optimized `.cfg` config files.

### Appendix: Thin Process Wrappers (Do NOT preload)

Convenience CLI only — not expert pipeline prose. Load when you need that exact process action.

- **builder_launch_editor.py** / **builder_run_project.py** / **builder_stop_project.py**: Editor/game process lifecycle.
- **builder_get_debug_output.py** / **builder_get_godot_version.py** / **builder_get_project_info.py** / **builder_list_projects.py**: Read-only project/process introspection.

## Reference

> Progressive disclosure: open Official Documentation links only when researching a specific API; load Related Skills when routing to a peer domain — do not preload the whole lattice.

### Official Documentation
- [Command line tutorial](https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html) — `--headless`, `--path`, `-s`/`--script`, `--import`, and `--export-*` flags that every builder wrapper invokes.
- [Exporting projects](https://docs.godotengine.org/en/stable/tutorials/export/exporting_projects.html) — Export presets, CLI release/debug export flow, and why CI must mutate `export_presets.cfg` before `--export-release`.
- [Feature tags](https://docs.godotengine.org/en/stable/tutorials/export/feature_tags.html) — Custom/feature-profile tags used when stripping modules or gating CI smoke paths with `OS.has_feature`.
- [Exporting for dedicated servers](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_dedicated_servers.html) — Headless/server export constraints (no GPU bake assumptions) that pair with CI isolation via XDG vars.
- [Import process](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/import_process.html) — `.import` + `.godot/imported` lifecycle; why deleting imported cache forces project-wide revalidation.
- [Importing 3D scenes](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/index.html) — glTF→scene pipeline entry before `GLTFDocument`/`ResourceSaver` automation.
- [Available 3D formats](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html) — glTF/GLB expectations for headless converters and collision generation.
- [Using CSG tools](https://docs.godotengine.org/en/stable/tutorials/3d/csg_tools.html) — Why procedural CSG must bake to static meshes before shipping or NavMesh baking.
- [Using NavigationMeshes](https://docs.godotengine.org/en/stable/tutorials/navigation/navigation_using_navigationmeshes.html) — Headless NavMesh bake ownership and region setup after CSG/static geometry lands.
- [ResourceUID](https://docs.godotengine.org/en/stable/classes/class_resourceuid.html) — Safe `has_id`/`set_id`/`uid://` sync after headless saves (UIDs are not serialized by `ResourceSaver` headless).
- [ResourceSaver](https://docs.godotengine.org/en/stable/classes/class_resourcesaver.html) — Pack/save API for programmatic `.tscn` writes; ownership must be set before `PackedScene.pack`.
- [EditorFileSystem](https://docs.godotengine.org/en/stable/classes/class_editorfilesystem.html) — `reimport_files()` for batch import enforcement from `@tool` EditorScripts.

### Related Skills

#### Prerequisites
- [godot-project-foundations](project-foundations.md) — Feature folders, `project.godot` metadata, and VCS ignores must exist before CLI launch/import/export automation.
- [godot-gdscript-mastery](gdscript-mastery.md) — Headless `SceneTree` workers, typed Resources, and `quit()` lifecycle patterns used by every `-s` script.
- [godot-resource-data-patterns](resource-data-patterns.md) — `PackedScene`, UID paths, and deep-duplicate rules that prevent procedural state-bleed across builder runs.

#### Complements
- [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) — CI / headless target engine bumps: hop-by-hop via the migration hub before baking against new APIs.
- [godot-export-builds](export-builds.md) — Platform templates, codesign/keystore, and filter rules that sit on top of `builder_ci_exporter.py` orchestration.
- [godot-3d-world-building](3d-world-building.md) — CSG/GridMap/MeshLibrary authoring that this skill bakes and exports headlessly.
- [godot-navigation-pathfinding](navigation-pathfinding.md) — Runtime agents and layer costs that consume NavMeshes produced by `builder_navmesh_baker.py`.
- [godot-tilemap-mastery](tilemap-mastery.md) — TileSet/TileMapLayer conventions for scenes generated by `builder_tilemap_generator.py`.
- [godot-ui-containers](ui-containers.md) — Container layout rules that `builder_ui_assembler.py` should emit instead of absolute Control positions.
- [godot-physics-3d](physics-3d.md) — Collision layers/shapes for trimesh bodies created by `builder_collision_generator.py`.

#### Downstream / consumers
- [godot-testing-patterns](testing-patterns-expert-testing-patterns.md) — GUT/integration suites launched through `builder_test_runner.py` in CI after import/export steps.
- [godot-performance-optimization](performance-optimization.md) — Escalate when orphan scans, import compression, or export size still miss budgets.
- [godot-monte-carlo-balancer](monte-carlo-balancer.md) — Headless `test_runner` calibration loops for balance sims after builder CI smoke passes.
- [godot-debugging-profiling](debugging-profiling.md) — Consume `builder_get_debug_output.py` logs when headless imports/exports fail without a GUI.

#### Master
- [godot-master](../SKILL.md) — Library router and mirrored module entry; open when discovering which Domain Skill owns a cross-cutting build/automation concern.

