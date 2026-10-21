# companion/

## Responsibility

Desktop companion application showing active agent GIFs per session. Runs as an accessory macOS app (invisible Dock), displays floating animated windows over projects, and visualizes agent activity through embedded sprite sheets.

## Design

The companion communicates with OpenCode host runtime via file-based state sharing (JSON files) and displays animated overlays for active agents:

- Displays animated GIFs for `idle`, `question`, `unknown`, and agent-specific animations (`council`, `designer`, `explorer`, `fixer`, `observer`, `oracle`, `orchestrator`).
- Agent tiles can expose live session model/variant metadata on hover; waiting-input uses an attention outline without changing the animation contract. Error attention is intentionally deferred until canonical terminal evidence is available.
- Each waiting-input request carries a monotonic attention generation; native informational attention deduplicates by session/generation so back-to-back questions cannot collapse into one notification. The plugin restores that generation/request fence across manager replacement; ordinary states reset the native request.
- Animated windows can be resized (S/M/L/XL presets), repositioned via drag-and-drop, and anchored to screen edges. Window-position persistence is dispatched off the egui thread with latest-write-wins generation fencing so shared-state lock contention cannot freeze animation or dragging.
- Right-click opens an independent native eframe viewport (rather than a tiny `egui::Area` inside the GIF window), using a compact scrollable body and header-only `StartDrag` handle with upper-right close control. The child is pre-rendered hidden and revealed using `ViewportCommand::Visible(true)`/Focus to avoid changing egui 0.29's recreation-prone `active` builder field. Windows opening freezes a physical desktop anchor and enumerates usable monitor areas once through `screen.rs`; the hidden child applies geometry using its own effective pixels-per-point and waits for the native rectangles and drawing area to settle before revealing. This avoids egui-winit 0.29's primary-monitor scaling of builder positions. Size is capped to the work area without a conflicting minimum-size constraint, and placement commands stop after reveal so manual dragging remains independent. The popup has searchable Active / All open / Known project views, full paths and a direct Project/Global preset selector with Inherit. The visible animation session remains independent of the editing target; preset navigation cannot move the root overlay. Known projects are a bounded history from real OpenCode instances, not a filesystem scan. The Rust UI sends typed scoped requests; only TypeScript validates and persists preset changes, including requests routed to remembered but inactive project directories. Pending request IDs fence acknowledgement/completion and rejection when the target manager exits.
- Project actions stay native and host-independent: open the published session cwd in the platform file manager or copy it through egui clipboard output. The opener is reaped off the UI thread; status is session-scoped, async completion never closes a later menu, and failures reuse the compact Open button instead of increasing menu height.
- Session state tracks window positions, sizes, and config per project directory using a hidden state file. Windows restoration checks saved rectangles against enumerated monitors (including negative origins) using egui's effective scale (native DPI times UI zoom) and uses a visible anchor when stale or off-screen; fallback does not overwrite the saved preference. The persisted x/y format is unchanged and does not record the scale at capture.
- Animations are pre-generated as 72-frame JPEG sprite sheets (12x6 grid, 200x200 each frame) from companion/VIDEOS/*.mp4 source videos.

## Flow

1. Companion reads OH_MY_OPENCODE_SLIM_COMPANION_SESSION_ID as the process that launched the singleton; display selection itself is activity-driven and may target any published live project.
2. Acquires a singleton lock via file-based coordination to prevent duplicate instances.
3. Loads agent sprite sheets embedded at compile time from `companion/animations/` (`include_bytes!` in `gifs.rs`); `state.rs` is the Rust state module, not a data file.
4. Renders animated overlays in an Egui window for each active session using that in-process state.
5. Persistent state stores window geometry, size, config per project directory in `$XDG_DATA_HOME/opencode/storage/oh-my-opencode-slim/companion-state.json` (XDG fallback: `~/.local/share`).

## Integration

- Acts as a UI visualization layer for OpenCode sessions, complementing the TS plugin.
- Injected into OpenCode runtime via OH_MY_OPENCODE_SLIM_COMPANION_SESSION_ID environment variable.
- `companion/VIDEOS/` holds MP4 source media used to generate the runtime JPEG sprite sheets; release binaries embed the sheets from `companion/animations/` via `include_bytes!` and never decode the MP4s.
- Serves as the visual anchor for agent activity indicators in the oh-my-opencode-slim ecosystem.

## Shared-state locking

`state.rs` recovers abandoned `companion-state.json.lock` directories after a bounded stale interval. Native window-position writes run on a background worker, while the UI keeps the latest position in memory until the shared state reflects it. This prevents the previous one-second UI stall when a state writer was blocked.

## Popup regression coverage

`src/app/popup_tests.rs` drives the production menu through real egui parent/child frames with a thread-isolated immediate renderer. It checks hidden rendering, an ordered reveal/focus pair only after preparation and Windows geometry readiness, close/reopen state reset, primary-press-only header dragging (including a new drag after a consumed release), the separate close hit area, and root-window command isolation in both native and embedded modes. Windows placement fixtures cover negative and positive monitor offsets, different root/child DPI scales, UI zoom, work-area edges, constrained sizes with a published preset catalog and long names, and independent movement after reveal. These tests cover egui state and emitted commands; physical Windows/macOS/Linux smoke still verifies compositor-visible flashing, cross-monitor movement and native pointer release.

## Windows native dragging

`src/window_drag.rs` repairs the `WM_NCLBUTTONDOWN` caption message posted by winit 0.30.13, which passes a stack `POINTS` address where Win32 expects packed signed screen coordinates. The Windows event-loop message hook in `main.rs` copies the message, packs its recorded `MSG.pt` coordinates, dispatches the copy once, and suppresses the original. It never dereferences the faulty payload or reposts it; winit retains ownership of capture and native drag bookkeeping. Other messages pass through unchanged. This applies to both the root animation and popup header.

Portable tests verify signed coordinate packing. Windows CI also runs invisible message-only window tests that verify the corrected payload reaches a real window procedure exactly once, the original message stays untouched, and unrelated messages are not intercepted. These tests do not simulate an interactive move between physical displays.
