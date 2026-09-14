# Accessibility

Cross-platform accessibility middleware. Owns the macOS AX / IOKit FFI, the unified Swift helper-process bridge (focus queries, paste, and overlay in one persistent process), focused-text inspection, system-permission detection (Accessibility, Input Monitoring, Microphone), the Globe-key listener, "System Events" automation-denial tracking, terminal heuristics, and AX-string normalization. Centralises platform-specific code so that `voice` never touches FFI directly.

## Public surface

Re-exported from `mod.rs`:

- `pub fn clear_automation_denial` / `mark_system_events_denied` / `system_events_denied` — `automation_state.rs` — tracks whether macOS has denied AppleScript "System Events" automation, so callers can stop retrying until the user re-grants it.
- `pub fn focused_text_context` / `focused_text_context_verbose` / `validate_focused_target` — `focus.rs` — query the OS for the currently focused text field.
- `pub fn globe_listener_start` / `globe_listener_stop` / `globe_listener_poll` / `pub struct GlobeHotkeyPollResult` / `pub enum GlobeHotkeyStatus` — `globe.rs` — macOS Globe-key (Fn) hotkey monitor.
- `pub fn precompile_helper_background` — `helper.rs`, split into submodules `helper/process.rs` (process management, `pub(crate) helper_send_receive`), `helper/swift_focus.rs` / `helper/swift_paste.rs` / `helper/swift_overlay.rs` / `helper/swift_ax_actions.rs` (embedded Swift source pieces), and `helper/swift_source.rs` (assembles the full source) — compile the Swift helper with `swiftc` on a background thread so the first request avoids compile latency. No caller outside this module today.
- Permission detection: `detect_permissions`, `detect_microphone_permission`, `microphone_denied_message`, `permission_to_str`, `request_microphone_access` (cross-platform); macOS-only `detect_accessibility_permission`, `detect_input_monitoring_permission`, `open_macos_privacy_pane`, `request_accessibility_access` — `permissions.rs`. Microphone detection probes `cpal` for a default input device and needs the `inference` feature; without it the result is `PermissionState::Unknown`.
- `pub fn extract_terminal_input_context` / `is_terminal_app` / `is_text_role` / `looks_like_terminal_buffer` — `terminal.rs` — terminal-window heuristics.
- `pub fn normalize_ax_value` / `parse_ax_number` / `truncate_tail` — `text_util.rs` — AX value normalization.
- `pub struct ElementBounds` / `FocusedTextContext` / `PermissionKind` / `PermissionState` / `PermissionStatus` — `types.rs`.

## Calls into

- macOS frameworks `ApplicationServices`, `CoreFoundation`, and `IOKit` via `#[link]` FFI in `permissions.rs`; `CGEvent` key synthesis happens inside the Swift helper, not in Rust.
- The Swift helper process, compiled on first use with `swiftc` from the source assembled in `helper/swift_source.rs` and driven over stdin/stdout JSON by `helper_send_receive`.
- `cpal` (behind the `inference` feature) for the microphone probe.
- No `crate::*` imports: this module does not read `Config`.

## Called by

- `crates/openhuman-core/src/voice/server/hotkey_listener.rs` — `globe_listener_start` / `globe_listener_poll` for the Fn hotkey; `voice/server/pipeline.rs` — `focused_text_context_verbose` to capture the frontmost app at hotkey press.
- `crates/openhuman-core/src/voice/text_input.rs` — `validate_focused_target` before inserting dictated text.
- `crates/openhuman-core/src/voice/always_on/capture.rs` — `detect_microphone_permission`; `audio_capture.rs` — the same plus `microphone_denied_message` / `request_microphone_access` before opening the input device.
- `crates/openhuman-core/src/core/all_tests.rs` — asserts `detect_microphone_permission()` is `Unknown` when `inference` is compiled out.

## Tests

- Sibling `*_tests.rs` files for `automation_state`, `focus`, `globe`, `permissions`, `terminal`, and `text_util`, attached via `#[cfg(test)] #[path = ...] mod tests;`.
- AX FFI and the Swift helper are only exercised on a real macOS host — Linux CI skips the platform-gated paths.
