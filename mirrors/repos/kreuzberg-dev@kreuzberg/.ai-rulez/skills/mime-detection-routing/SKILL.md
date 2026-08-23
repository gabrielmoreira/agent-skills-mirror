---
name: mime-detection-routing
description: MIME type detection and extractor routing in core/mime.rs — the FORMATS registry that EXT_TO_MIME and SUPPORTED_MIME_TYPES are derived from, the path-based and bytes-based detection functions, priority-based registry selection, wildcard MIME families, and the real procedure for adding a format. Load when adding a format, wiring an extractor to a MIME type, or debugging why a file routes to the wrong (or no) extractor.
---

# MIME Detection & Routing

## Detection Flow

```text
Extension -> EXT_TO_MIME -> validate_mime_type -> registry.get(mime) -> extractor
```

## Key Functions

| Function | Location | Behaviour |
| --- | --- | --- |
| `detect_mime_type(path, check_exists: bool)` | `core/mime.rs` | **Path-based only** — never reads bytes. Lowercased extension → `EXT_TO_MIME`, then tree-sitter extension detection (feature `tree-sitter`), then `mime_guess::from_path`. `check_exists` gates a file-existence check, not content inspection. |
| `detect_mime_type_from_bytes(bytes)` | `core/mime.rs` | Magic-number detection via the `infer` crate. The only content-sniffing entry point. |
| `validate_mime_type(mime)` | `core/mime.rs` | Membership test against the static `SUPPORTED_MIME_TYPES` set (plus an `image/*` prefix rule and a case-insensitive retry). It does **not** consult the extractor registry — a MIME can validate and still have no extractor. |

## The FORMATS registry is the single source of truth

`FORMATS: &[FormatEntry { extensions, mime_type, aliases }]` in `core/mime.rs`.
`EXT_TO_MIME` and `SUPPORTED_MIME_TYPES` are `LazyLock`s **derived** from it by iteration —
there is no `m.insert` call site to add to, and hand-editing either is impossible.

Current size: 100 formats, 120 unique extensions, asserted by
`core/mime.rs::tests::format_and_extension_counts_match_the_published_headline`. Extension
lookup is case-insensitive (the extension is lowercased before the map hit).

## Registry Selection

```rust
let registry = get_document_extractor_registry();          // plugins/registry/mod.rs
let guard = registry.read()?;
let extractor: Arc<dyn DocumentExtractor> = guard.get(mime_type)?;  // Result, not Option
```

`DocumentExtractorRegistry::get` (`plugins/registry/extractor.rs`) returns the
highest-`priority()` extractor for the MIME type, and returns `Err` — not `None` — when none
matches.

## Wildcard Support

An extractor may register a family: `"image/*"` matches `image/png`, `image/jpeg`, and so on
(prefix match on a registered type ending in `/*`).

## Adding a New Format

1. Add one `FormatEntry` to `FORMATS` in `crates/xberg/src/core/mime.rs`. `EXT_TO_MIME` and
   `SUPPORTED_MIME_TYPES` update automatically.
2. Bump `PUBLISHED_FORMATS` / `PUBLISHED_EXTENSIONS` in
   `format_and_extension_counts_match_the_published_headline`, and the docs copies that test
   enumerates.
3. Implement `InternalDocumentExtractor` (not `DocumentExtractor` — see
   `plugin-architecture-patterns`) with `supported_mime_types()` returning the MIME.
4. Register in `crates/xberg/src/extractors/mod.rs::register_default_extractors()`.

## Critical Rules

1. Call `validate_mime_type()` before extraction — but do not treat it as proof an extractor exists.
2. Extension lookup is case-insensitive.
3. `detect_mime_type` inspects no content. Use `detect_mime_type_from_bytes` for extension-less or untrusted input.
4. Never edit `EXT_TO_MIME` or `SUPPORTED_MIME_TYPES` — edit `FORMATS`.
