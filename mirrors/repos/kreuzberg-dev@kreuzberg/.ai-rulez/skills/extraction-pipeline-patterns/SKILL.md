---
description: "Document extraction pipeline architecture and patterns"
name: extraction-pipeline-patterns
priority: critical
---

# Extraction Pipeline Patterns

**Format detection → extractor routing → post-processing, across 100 formats / 120 file extensions**

The counts are asserted in-tree by
`crates/xberg/src/core/mime.rs::tests::format_and_extension_counts_match_the_published_headline`
(`PUBLISHED_FORMATS = 100`, `PUBLISHED_EXTENSIONS = 120`). Cite that test rather than copying
the number, and update it when `FORMATS` changes.

## Layout

- `crates/xberg/src/core/pipeline/` — orchestration (`mod.rs`, `cache.rs`, `execution.rs`,
  `features.rs`, `format.rs`, `initialization.rs`, `page_markers.rs`)
- `crates/xberg/src/core/mime.rs`, `core/formats.rs` — detection and the `FORMATS` registry
- `crates/xberg/src/extractors/` — one module per format, each implementing
  `InternalDocumentExtractor`
- `crates/xberg/src/extraction/` — shared parsing/rendering helpers used by those extractors
- `crates/xberg/src/core/config/`, `core/config_validation/` — both directories, not files

## Flow

1. **Detect** — MIME from extension via `EXT_TO_MIME`, or from bytes via
   `detect_mime_type_from_bytes`; validate against `SUPPORTED_MIME_TYPES`.
2. **Route** — registry returns the highest-`priority()` extractor registered for that MIME.
3. **Extract** — the extractor produces an `InternalDocument`.
4. **Post-process** — `core::pipeline::run_pipeline(doc, config)` (async) or
   `run_pipeline_sync` (WASM) runs validators, quality processing, chunking and hooks, and
   returns `ExtractedDocument`. Every extraction path goes through it.

## Extractor modules

| Category | Extractors | Modules |
| --- | --- | --- |
| Office | DOCX, PPTX, PPT, DOC, XLSX/XLS, ODT, ODP, iWork, HWP/HWPX, WordPerfect | `extractors/{docx,pptx,ppt,doc,excel,odt,odp,hwp,hwpx,wordperfect}.rs`, `extractors/iwork/` |
| PDF | text, encrypted, OCR fallback | `extractors/pdf/` |
| Images | PNG, JPG, TIFF, WebP, HEIC, SVG, QR | `extractors/{image,qr}.rs`, `extraction/{image,image_ocr,heif}.rs` |
| Web | HTML, XHTML, XML, MDX | `extractors/{html,xml,mdx}.rs`, `extraction/html/` |
| Email | EML, MSG, PST | `extractors/{email,pst}.rs`, `extraction/email.rs` |
| Archives | ZIP, TAR, GZ, 7Z | `extractors/archive.rs`, `extraction/archive/` |
| Markup | MD, TXT, RST, Org, RTF, AsciiDoc, Typst, Djot | `extractors/{markdown,text,rst,orgmode,asciidoc,typst}.rs`, `extractors/{rtf,djot_format}/` |
| Academic | LaTeX, BibTeX, JATS, Jupyter, DocBook, EPUB, FictionBook | `extractors/{bibtex,jupyter,docbook,fictionbook}.rs`, `extractors/{latex,jats,epub}/` |
| Structured | JSON, YAML, TOML, CSV, DBF | `extractors/{structured,csv,dbf}.rs` |

## Fallback strategies

- **Password-protected PDFs** — try the configured password, then the secondary list; on
  failure report `is_encrypted` in metadata rather than erroring out.
- **OCR fallback** — a PDF page with no extractable text routes to the OCR pipeline;
  `config.force_ocr` and `config.force_ocr_pages` force it.
- **Nested archives** — recursive with a depth limit from `SecurityLimits`.
- **Corrupted input** — emit what parsed and attach the error location; never panic.

## Plugin integration

`crates/xberg/src/plugins/`. Registry selection is by **`priority()`, highest wins** — not by
registration order. Register above 50 to override a built-in. See
`plugin-architecture-patterns`.

## Features

All features live in `crates/xberg/Cargo.toml`; there is no `FEATURE_MATRIX.md`.

| Group | Features |
| --- | --- |
| OCR | `ocr` (Tesseract), `ocr-wasm`, `paddle-ocr` / `paddle-ocr-tract`, `sceptre-ocr`, `candle-vlm-ocr` |
| Formats | `pdf` (→ `pdf-native`), `office`, `excel` / `excel-wasm`, `html`, `xml`, `email`, `archives`, `heic`, `wordperfect`, `hwp`, `hwpx`, `iwork`, `notebook`, `mdx`, `svg` |
| AI/ML | `embeddings` (ORT), `static-embeddings` (pure Rust), `layout-detection` / `layout-tract`, `keywords`, `language-detection`, `ner-onnx`, `ner-llm` |
| Server | `api` (Axum), `mcp`, `otel`, `prometheus`, `tokio-runtime` |
| Aggregates | `formats`, `analysis`, `services`, `full`, `no-ort-target`, `wasm-target`, `android-target`, `windows-target`, `macos-intel-target` |

Bindings are separate crates, not features of `crates/xberg`. The one mutually-exclusive pair
is `ort-bundled` / `ort-dynamic`. WASM excludes ORT-backed `embeddings`, but **does** carry
`ocr-wasm`, `keywords` and `static-embeddings`. Full detail in `feature-flag-policy`.

## Critical Rules

1. **Detect before routing** — never dispatch on a caller-supplied extension alone.
2. **Post-processing is mandatory** — all results flow through `run_pipeline` / `run_pipeline_sync`.
3. **Selection is by priority, not registration order** — the registry returns the highest `priority()` for a MIME type.
4. **Stream large inputs** — PDFs and archives must not be fully buffered.
5. **Apply `SecurityLimits` to user content** — archive size, compression ratio, file count, nesting depth.
6. **Fail gracefully** — malformed input returns partial content plus error context, never a panic.

## Related Skills

- **mime-detection-routing** — the `FORMATS` registry and how to add a format
- **plugin-architecture-patterns** — which trait an extractor actually implements
- **format-specific-extraction** — per-format workflows and helpers
- **chunking-embeddings** — post-extraction text splitting
