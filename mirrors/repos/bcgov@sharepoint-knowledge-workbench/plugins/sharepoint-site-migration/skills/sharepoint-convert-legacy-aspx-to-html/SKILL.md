---
name: sharepoint-convert-legacy-aspx-to-html
plugin: sharepoint-site-migration
description: Use when converting one downloaded, static SharePoint ASPX page into a local HTML file; not for modern-page conversion, batch processing, sanitization, or SharePoint publishing.
allowed-tools: Bash, Read
---

# Convert Legacy ASPX to HTML

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- This skill converts one local `.aspx` file at a time. It does not download source files, connect to SharePoint, publish output, or process directories in batch.
- The default output is a sibling `.html` file. Existing output is protected unless `-Overwrite` is explicitly supplied; the output path must never resolve to the source file.
- The converter removes known ASP.NET/Office directives and comments, WebResource script references, spacer GIFs, redundant title markup, font wrappers, and simple single-cell layout tables. Meaningful tables and body content are retained.
- The converter rejects common active markup, including scripts, embedded documents, event-handler attributes, `srcdoc`, and JavaScript URLs, before writing output. It is not a general-purpose HTML sanitizer; inspect the generated markup before opening, sharing, or hosting it.
- Conversion is local file processing only. Publishing requires a separate approved workflow.

## Quick start

Run from this skill's root with a downloaded source file:

```powershell
pwsh -File .\scripts\convert-aspx-to-html.ps1 `
  -SourcePath .\temp\exhibit_risks.aspx `
  -OutputPath .\temp\exhibit_risks.html
```

The output path must differ from the source and must not already exist. To replace an existing output, use `-Overwrite` only after confirming that replacement is intended.

## Workflow

For a bulk migration, first download selected files with `sharepoint-download-file` and capture
an original Python link CSV with `sharepoint-extract-links`. Keep source URLs and originals;
conversion remains one eligible local page at a time. Re-extract links from converted output
before planning rewrites. See [bulk content workflow](references/bulk-content-link-workflow.md).

1. Confirm the input is the intended downloaded, static ASPX file and retain the original unchanged.
2. Choose a distinct, non-existing output `.html` path. Never use the source path as the output path.
3. Run the converter. If it rejects active markup, stop and report the error; do not weaken the guard or publish the source as a workaround.
4. Review the generated markup in a text editor first. Verify the title, body content, tables, links, and media; only open it in a browser after confirming the markup is appropriate. The converter is not a sanitizer.
5. Treat publishing as a separate operation with its own target validation and safety gates.

## Verification

- Confirm the command exits successfully and creates the requested output file.
- Confirm the source remains unchanged and the output contains the expected title and content.
- Confirm legacy-only artifacts are removed while meaningful tables remain.
- Confirm active source markup is rejected before output is written.
- Confirm an existing output remains unchanged unless `-Overwrite` is supplied; confirm source/output collisions are rejected.
- Review the output manually; a successful conversion is not a security or publication approval.

## References

- [Converter script](scripts/convert-aspx-to-html.ps1)
- [Routing evaluations](evals/evals.json)
- [Task-success contract](evals/task-success.json)
- [Acceptance criteria](acceptance-criteria.md)
