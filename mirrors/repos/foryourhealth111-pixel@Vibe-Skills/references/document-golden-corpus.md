# Document Golden Corpus

## Cases

| Case | Primary tool | Fallback | Required fields |
|---|---|---|---|
| born-digital PDF | `docling` | `pdf` | content, pages, provenance |
| OCR-heavy PDF | `docling` | `markitdown` | degraded_mode, failure_object |
| DOCX with comments | `docx` | `markitdown` | comments, structure, provenance |
| extensionless OOXML attachment | `docling` | `docx` / `xlsx` / `pptx` | source.mime_type, artifact_bundle, provenance |
| table-rich document | `docling` | `xlsx` / `pdf` | artifact_bundle, page mapping |
