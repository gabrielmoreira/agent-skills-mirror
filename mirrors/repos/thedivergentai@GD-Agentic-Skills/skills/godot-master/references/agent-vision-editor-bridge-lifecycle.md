# Editor bridge lifecycle

TEMP Godot **EditorPlugin** for viewport grabs Python cannot see cleanly. **NEVER Autoload. NEVER export. NEVER leave the staged addon committed.**

## Paths

| Path | Role |
|------|------|
| `.gdskills/vision/bridge/` | Copied templates (scratch) |
| `addons/_gdskills_agent_vision/` | Staged TEMP addon (delete after) |
| `.gdskills/vision/request` | Mode line: `2d` / `3d` / `main` |
| `.gdskills/vision/raw/*.png` | Bridge output |
| `.gdskills/vision/done` | Written after PNG flush |

## Steps

1. `ensure_gitignore` → `.gdskills/`
2. Copy templates → stage `addons/_gdskills_agent_vision/`
3. Append `res://addons/_gdskills_agent_vision/plugin.cfg` to `project.godot` `[editor_plugins] enabled=`
4. Open/focus Godot editor on the project (plugin `_process` polls `request`)
5. Python waits for `done` + stable PNG → encode WebP → delete handshake files
6. **Teardown:** remove plugin from `enabled=`, delete `addons/_gdskills_agent_vision/`

CLI:

```text
python scripts/capture.py editor --project-root . --editor-mode 3d
python scripts/capture.py editor --project-root . --godot "C:/Path/Godot_v4.7.exe" --editor-mode 2d
# debug only — MUST teardown afterward:
python scripts/capture.py editor --keep-bridge
```

When `--godot` is set, the CLI `Popen`s `godot -e --path <project>` after staging so the plugin can see `request`.

## Capture WHY (empty / wrong pixels)

- Always `await RenderingServer.frame_post_draw` (twice is safer) before `Viewport.get_texture().get_image()` — otherwise the Image can be empty or one frame stale.
- HDR / float viewports may need conversion before PNG; if `save_png` fails or Image is empty, switch main screen (`2D`/`3D`) and retry.
- DPI mis-crop on Windows OS capture: process not Per-Monitor V2 aware → window rect in wrong space → black bars or wrong panel. Sympton for OS modes, not editor SubViewport grabs.
- **Control crop WHEN:** need a dock/inspector slice rather than the 2D/3D scene SubViewport. HOW: capture editor main viewport Image, then `Image.get_region(Rect2i(control.get_global_rect()))` (see `agent_vision_editor_bridge_capture_viewport.gd`). Clamp to image bounds — global rects can extend off-screen.

## Recovery

| Symptom | Fix |
|---------|-----|
| Timeout waiting for `done` | Editor not open; plugin disabled; `.gdskills` not under project root; pass `--godot` |
| Empty PNG / plugin error | Wrong main screen; await frames; try `--editor-mode main` |
| Leftover addon after kill | Manually delete `addons/_gdskills_agent_vision/` and strip `enabled=` entry |
| `--keep-bridge` left on | Run teardown: disable plugin, delete addon, restore `project.godot` |

## Invariants

- Underscore addon name signals private/temp.
- Do not register docks, export plugins, or autoloads.
- Prefer `EditorInterface.get_editor_viewport_2d/3d` + `await RenderingServer.frame_post_draw`.
- If timeout: confirm editor is open, plugin enabled, and `.gdskills/vision/request` is visible to the editor (`res://.gdskills/...`).

## Docs

- [EditorPlugin](https://docs.godotengine.org/en/stable/classes/class_editorplugin.html)
- [EditorInterface](https://docs.godotengine.org/en/stable/classes/class_editorinterface.html)
- [Using Viewports](https://docs.godotengine.org/en/stable/tutorials/rendering/viewports.html)
