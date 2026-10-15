# Capture modes (platform expert notes)

Host utility — runs on the **agent machine**, not inside an exported game. Depth here is **Expert Knowledge Delta** for OS capture landmines.

## Modes

| Mode | Command | Notes |
|------|---------|--------|
| screen | `capture.py screen [--monitor N]` | `0` = virtual desktop union (may have **negative** left/top on Windows) |
| region | `capture.py region --x --y --w --h` | Physical pixels when DPI-aware |
| window | `capture.py window --title SUBSTR` | Best-effort; OS limits below |
| asset | `capture.py asset --paths ... [--sheet]` | Files/folders/`res://` → WebP / ≤2×2 sheet |
| editor | `capture.py editor --project-root ...` | TEMP EditorPlugin handshake; `--godot` auto-launches |

Common flags: `--project-root`, `--out`, `--quality`, `--short-edge` (default **512**), `--detail` / `--max-edge`, `--label`, `--skip-gitignore`.

### `res://` resolution (asset mode)

`--paths` accepts filesystem paths **or** Godot URIs. `res://ui/icon.png` → `{--project-root}/ui/icon.png`. Relative: cwd first, then project root.

---

## Windows (DPI is the #1 agent footgun)

- **Stack:** `mss` + ctypes `EnumWindows` (optional `pywin32`). DXGI/`dxcam` is optional continuous/fullscreen-only — not default one-shot.
- **Boot order:** set `SetProcessDpiAwarenessContext(PER_MONITOR_AWARE_V2)` **before** any HWND geometry / mss grab. Import `mss` before libraries that call older DPI APIs (`pyautogui`/`pyscreeze`) or coords desync.
- **Monitors:** `monitors[0]` = virtual union; `1..N` = physical displays. Spanning windows can cross negative origins.
- **Window match:** case-insensitive title substring; prefer longest match (Godot titles include scene paths). Empty titles, cloaked HWNDs, elevated-vs-unelevated mismatch → `no_match`.
- **Black frames:** minimized windows; exclusive fullscreen / some GPU paths → BitBlt black. Prefer windowed editor, region of visible client, DXGI only if you accept the weight, or **editor bridge**.
- **Layered UI:** menus/tooltips may need CAPTUREBLT-class paths (Pillow `include_layered_windows`) if chrome is missing.
- **No TCC equivalent** for interactive user BitBlt — but Session 0 / service / Secure Desktop still fail.

## macOS (TCC is a hard gate)

- Grant **Screen Recording** to the **exact** `sys.executable` / IDE helper performing capture — not “the shell script.”
- **Wallpaper-only** frames ⇒ permission denial (hard fail). Preflight APIs can false-negative for bare Python; always probe a real grab.
- Prefer in-process `mss` / Quartz over `/usr/sbin/screencapture` under agents (LaunchAgent/SSH attribution breaks).
- Window-by-title needs `pyobjc-framework-Quartz` (`CGWindowListCopyWindowInfo` → `CGWindowListCreateImage`). Decide **logical points** vs **Retina backing pixels** and document — click loops vs vision OCR disagree if mixed.
- Headless / no Aqua session: unsupported.

## Linux (X11 vs Wayland)

Detect `XDG_SESSION_TYPE` / `WAYLAND_DISPLAY` / `DISPLAY`.

| Session | Path |
|---------|------|
| **X11** | `mss` for screen/region; window via `wmctrl`/`xdotool` when present |
| **Wayland** | **Do not trust mss** (XGetImage fail / black via XWayland). Prefer `grim` (± compositor IPC). Portal Screenshot/ScreenCast is interactive — out of silent v1 loops |
| **Title capture** | Not portable on Wayland; compositor-specific or portal picker only |

Fallback order: X11→mss → grim → clear failure naming the session.

## Doctor

```text
python scripts/capture.py doctor
python scripts/capture.py list-windows
```

## Security

Prefer window/region over full desktop. Avoid password fields, secrets, unrelated IDE chrome.

## Budgets

Default **short-edge 512** for identity/overview. `--detail` → long-edge **1568** for glyphs/layout. See [webp-budgets.md](webp-budgets.md).
