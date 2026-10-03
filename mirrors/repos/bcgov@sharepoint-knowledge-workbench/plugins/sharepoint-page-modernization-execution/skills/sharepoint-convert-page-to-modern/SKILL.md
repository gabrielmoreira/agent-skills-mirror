---
name: sharepoint-convert-page-to-modern
plugin: sharepoint-page-modernization-execution
description: Converts a single classic SharePoint page to a modern Site Page with ConvertTo-PnPPage and stamps caller-supplied field-mapping and literal metadata onto the converted page. Use to convert one classic .aspx page within the same site. Dry-run by default; real writes are gated behind -Execute and a confirmation token.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-convert-page-to-modern.ps1 -PageName \"article.aspx\" -SourceLibrary \"ClassicPages\" -Execute -ConfirmToken CONVERT-SPO-PAGE"
---

# Convert Page to Modern

Convert one classic `.aspx` page to a modern Site Page in the same site, carrying over source metadata under different target field names.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Dry run by default: it prints the plan and makes zero tenant writes. A real conversion needs `-Execute -ConfirmToken CONVERT-SPO-PAGE` and is a live tenant write that the user runs.
- Same-site conversion does not rewrite embedded links in the page body (`-UrlMappingFile` and `-SkipUrlRewriting` are cross-site only). Run the `sharepoint-link-remediation` skills separately if links need fixing.
- Field mapping is caller-supplied. `-FieldMapping` and `-LiteralFieldValues` are optional JSON files; ship and invent no project-specific field names.
- When running from an installed copy, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).

## Quick start

```bash
pwsh -File scripts/spo-convert-page-to-modern.ps1 -PageName "article.aspx" -SourceLibrary "ClassicPages"
```

## Workflow

1. Dry run as above and review the plan with the user.
2. Add `-FieldMapping field-mapping.json -LiteralFieldValues literals.json` if metadata should be carried over.
3. After the user confirms, rerun with `-Execute -ConfirmToken CONVERT-SPO-PAGE`.
4. Validate with `sharepoint-validate-page-migration`.

## Verification

The dry run lists the page and the fields it would stamp; after a real run the converted page exists in `-TargetLibrary` (default `Site Pages`) with the mapped and literal fields populated.

## References

- [Conversion details](references/page-conversion-details.md): read for field mapping, usage and provenance.
- [Gates, tokens and config](references/page-execution-gates-and-config.md): read for the token table, the `-ConfigPath` note and the link-rewriting limit.
