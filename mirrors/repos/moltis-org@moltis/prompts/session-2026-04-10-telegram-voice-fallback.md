# Session Summary: Telegram Voice Fallback Fix

Date: 2026-04-10
Issue: `moltis-bhf`

## Summary

Fixed the Telegram voice-message regression behind GitHub issue `#632`.

- Extracted voice handling into `handle_voice_message()` in `crates/telegram/src/handlers.rs`.
- The helper now returns `None` after sending a direct user-facing reply, and the caller exits early instead of dispatching placeholder strings to the LLM.
- Preserved caption fallback when a voice message includes useful caption text.
- Added exact reply-text constants so tests can assert user-visible fallback copy.

## Validation

- `cargo +nightly-2025-11-30 fmt --all -- --check`
- `cargo clippy -p moltis-telegram --all-targets -- -D warnings`
- `cargo test -p moltis-telegram`

## Follow-up

- Filed `moltis-dwx` for the same Matrix bug class.
- Filed `moltis-8i7` for the same WhatsApp bug class plus missing empty-transcript handling.
