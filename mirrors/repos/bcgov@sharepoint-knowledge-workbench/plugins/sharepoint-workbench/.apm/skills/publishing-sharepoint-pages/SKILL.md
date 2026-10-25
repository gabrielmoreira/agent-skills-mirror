---
name: publishing-sharepoint-pages
description: "Publish, author, and deploy modern SharePoint pages, web parts, navigation links, and HTML or markdown pages. Handles modern page publication, wave publication, dynamic ASPX page modernization to modern canvas, static ASPX library file conversion, and CKEditor 5 RTE HTML sanitization. Use when asked to 'publish page', 'create modern page', 'publish markdown', 'publish dynamic aspx page', 'publish static aspx page', 'upload static page', 'convert static aspx', 'sync navigation', or 'copy page'."
---

# Publishing SharePoint Pages

Publish and deploy modern SharePoint Online pages, web parts, and converted HTML/markdown assets. Route the request to the matching mode in `references/modes/`. Each mode preserves its operation-specific flags, publication plan shape, validation gates, and rollback contract.

## Contents

- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Constraints](#constraints)
- [Modes](#modes)
- [Verification](#verification)

## Quick start

1. **Dry-Run Page Publication:**
   ```powershell
   pwsh -File scripts/spo-publish-modern-page.ps1 -ConfigPath <config.psd1> -PageName "Home" -Layout Home -Title "Home"
   ```
2. **Dynamic ASPX to Modern Canvas Publication:**
   ```powershell
   pwsh -File scripts/new-page-migration-dry-run.ps1 -ConfigPath <config.psd1> -PackagePath temp/package-rte.json
   ```
3. **Execute Live Publication (Human Confirmation Gate):**
   ```powershell
   pwsh -File scripts/publish-spo-page.ps1 -ConfigPath <config.psd1> -PackagePath temp/package-rte.json -Execute -ConfirmToken PUBLISH-SPO-PAGE
   ```

## Workflow

1. **Select Publication Mode**: Match user intent to modern page creation, markdown/HTML publishing, dynamic ASPX modernization, or static library upload.
2. **Lint & Sanitize Rich Text**: For web parts with HTML, run `scripts/sp_text_webpart_html.py` against `assets/rte-vocabulary.json` and convert with `scripts/convert-package-to-rte.ps1`.
3. **Generate Publication Plan**: Run dry-run to preview sections, column layouts, canvas controls, and link rewrites.
4. **Authorize & Execute**: Provide explicit confirmation token (`PUBLISH-SPO-PAGE` or mode token) to commit changes.
5. **Post-Publication Verification**: Validate webparts, links, images, and layout rendering.

## Constraints

- Writes remain dry-run by default; live publication requires `-Execute` and explicit confirmation tokens.
- No raw classic `.aspx` files may be uploaded directly to `SitePages`.
- Rich-text web parts must comply with CKEditor 5 allowlist to avoid editing-mode stripping in the browser.
- All scripts and assets are local to this skill; zero external symlinks.

## Modes

| Mode | Purpose | Reference |
|:---|:---|:---|
| `dynamic-aspx-page-publication` | Modernize and publish classic dynamic ASPX pages to SPO canvas | [mode](references/modes/dynamic-aspx-page-publication.md) |
| `static-aspx-file-publication` | Convert and publish document-library static ASPX files as HTML | [mode](references/modes/static-aspx-file-publication.md) |
| `page-publish-contract` | Comprehensive publication contract and execution specifications | [mode](references/modes/page-publish-contract.md) |
| `rte-sanitization` | CKEditor 5 RTE rich-text HTML sanitization and linting | [mode](references/modes/rte-sanitization.md) |
| `publish-markdown` | Publish Markdown files as modern SharePoint pages | [mode](references/modes/publish-markdown.md) |
| `publish-html-page` | Publish HTML files to modern SharePoint pages | [mode](references/modes/publish-html-page.md) |
| `copy-page` | Copy modern pages between SharePoint sites | [mode](references/modes/copy-page.md) |
| `plan-publication` | Generate deterministic publication plan | [mode](references/modes/plan-publication.md) |
| `apply-publication` | Apply approved publication plan | [mode](references/modes/apply-publication.md) |
| `validate-publication` | Validate deployed publication integrity | [mode](references/modes/validate-publication.md) |
| `compare-publication` | Compare local content against published page | [mode](references/modes/compare-publication.md) |
| `remove-publication` | Remove published page with rollback safeties | [mode](references/modes/remove-publication.md) |

## Verification

Run automated tests:
```bash
pytest tests/test_sp_text_webpart_html.py
```
Check publication validation:
```powershell
pwsh -File scripts/validate-spo-wave-completion.ps1 -ConfigPath <config.psd1> -WaveId <wave>
```
