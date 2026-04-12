## Summary

Implemented GitHub issue #640 by threading channel provenance into hook payloads.

- Added `ChannelBinding` to hook payload schema in `moltis-common`.
- Kept channel-specific chat classification in `moltis-channels` via `ChannelType::classify_chat()` and `From<&ChannelReplyTarget> for ChannelBinding`.
- Reworked chat runtime channel context to reuse the shared binding shape and inject `_channel` into tool context.
- Populated `MessageReceived`, `BeforeToolCall`, and `SessionStart` hook payloads with optional channel metadata.
- Updated hook docs and adjusted plugin tests that construct these payloads directly.

## Validation

Passed:

- `just format`
- `just format-check`
- `cargo test -p moltis-common hooks::tests:: -- --nocapture`
- `cargo test -p moltis-channels plugin::tests:: -- --nocapture`
- `cargo test -p moltis-agents before_tool_call_hook_receives_channel_binding_from_tool_context -- --nocapture`
- `cargo test -p moltis-chat build_tool_context_includes_channel_binding -- --nocapture`
- `cargo test -p moltis-chat resolve_channel_runtime_context -- --nocapture`
- `cargo test -p moltis-gateway resolve_dispatches_session_start_with_ -- --nocapture`
- `cargo test -p moltis-plugins hooks::tests:: -- --nocapture`
- `cargo test -p moltis-plugins shell_hook::tests:: -- --nocapture`
- `cargo test -p moltis-plugins command_logger::tests:: -- --nocapture`

Attempted but failed for environment reasons:

- `just lint`
  - failed in `llama-cpp-sys-2` CMake setup with `CUDA Toolkit not found`
  - this occurred before any hook-related clippy issue surfaced

## Follow-up

- `ToolResultPersist` now has the schema field but still needs an actual dispatch site from issue #638.
- `sender_id` remains reserved and unset until the session/channel layer has a real source of truth for it.
