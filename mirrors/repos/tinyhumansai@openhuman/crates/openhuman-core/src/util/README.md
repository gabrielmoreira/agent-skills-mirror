# util

Kernel helper family — `pub mod util;` in `lib.rs` is unconditional, never
feature-gated. Helpers reused across domains; nothing here may reach into a
domain. No file in this directory has a `use crate::` line, and that is the
rule: a helper that needs config, a `Tool`, a workspace, or security policy
belongs in the domain that owns those, not here. New external crates are also
off-limits — this is kernel surface under the `scripts/kernel-floor.limits`
dependency ratchet, which is why `bm25` is hand-rolled and `redact` is a
six-line copy rather than an engine link.

## Layout

| File | Purpose |
| --- | --- |
| `bm25.rs` | `Bm25Index` + `tokenize` — BM25 ranking over `(id, text)` pairs, the shared core behind `tools/impl/meta/tool_search.rs` and `skills/search.rs`. Names nothing from `crate::` so it can move into a loadable module unchanged. |
| `redact.rs` | `redact()` — SHA-256 → 8 hex chars for source ids, entity ids, and content paths in log lines. Same helper as `tinymemory_core::util::redact`, kept as a local copy so the host does not link the memory engine for a log formatter; the two copies never need to agree. |
| `retry.rs` | `retry_with_backoff` / `retry_with_backoff_async` (`base_ms * 2^i` backoff, `warn!` per retry) and `is_transient_fs_error` — for Windows mandatory-locking errors (`ERROR_SHARING_VIOLATION`, `ERROR_ACCESS_DENIED`) on a tree another handle still holds. |
| `sanitize.rs` | Pure re-export of `tinymcp_bus::sanitize` (`sanitize_for_llm`, `strip_control_chars`, `strip_instruction_fences`, `truncate_utf8_safe`, `MAX_DESCRIPTION_BYTES`, `MAX_TITLE_BYTES`) at the path callers already use. The rule lives in `tinymcp_bus` so MCP tool descriptions and the orchestrator prompt builder's skill descriptions get the same stripping; do not fork it back here. |
| `text.rs` | `truncate_with_ellipsis` / `truncate_with_suffix` (char-count truncation), `truncate_at_byte_boundary` (byte-cap with `…`), `floor_char_boundary` / `ceil_char_boundary` / `utf8_safe_prefix_at_byte_boundary` (byte-index rounding), `provenance_tag` (`chat:xxxxxxxx` hash of a session id for the cross-chat context block, so the raw `client_id` never reaches a prompt). |
| `types.rs` | `MaybeSet<T>` — `Set(T)` / `Unset` / `Null`, distinguishing "field absent" from "field explicitly null" in partial-update payloads (see `tools/impl/system/proxy_config.rs`). |
| `tls/` | `tls_client_builder()` — platform-conditional TLS backend for `reqwest` clients. See [tls/README.md](tls/README.md). |

`*_tests.rs` files sit beside each module.

## Public surface

`mod.rs` re-exports `retry`, `text`, and `types` items at the module root, so
`crate::util::truncate_with_ellipsis`, `crate::util::retry_with_backoff`, and
`crate::util::MaybeSet` resolve without the submodule. `bm25`, `redact`,
`sanitize`, and `tls` are reached through their submodule:
`crate::util::bm25::Bm25Index`, `crate::util::redact::redact`,
`crate::util::sanitize::sanitize_for_llm`, `crate::util::tls::tls_client_builder`.
From outside the crate the lib is `openhuman_core`, which is the path the
`truncate_with_ellipsis` doctest uses.
