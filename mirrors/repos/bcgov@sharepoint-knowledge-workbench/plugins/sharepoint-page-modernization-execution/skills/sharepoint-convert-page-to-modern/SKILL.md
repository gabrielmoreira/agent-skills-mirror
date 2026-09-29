---
name: sharepoint-convert-page-to-modern
plugin: sharepoint-content-publication
description: Converts a single classic SharePoint page to a modern Site Page via ConvertTo-PnPPage and stamps caller-supplied field-mapping/literal metadata onto the converted page. Dry-run by default; real writes gated behind -Execute and a confirmation token.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/spo-convert-page-to-modern.ps1 -PageName \"article.aspx\" -SourceLibrary \"ClassicPages\" -Execute -ConfirmToken CONVERT-SPO-PAGE"
---

# Convert Page to Modern

## Trigger and Purpose

Use this skill to convert one classic `.aspx` page to a modern SharePoint
Site Page within the same site, stamping any source metadata you want
carried over onto the converted page under different (target) field names.

## Real platform constraint recorded

`ConvertTo-PnPPage`'s `-UrlMappingFile`/`-SkipUrlRewriting` parameters only
apply to cross-site transformations. Converting within one site (this
skill's scope) does **not** rewrite embedded links in the page body -- run a
link remediation pass separately (see `sharepoint-link-remediation`) if the
source content contains embedded links that need fixing.

## Field mapping is caller-supplied, never built in

`-FieldMapping` (source field internal name -> target field internal name)
and `-LiteralFieldValues` (target field internal name -> fixed value, e.g. a
migration tag) are both optional JSON files you provide. No project-specific
field names ship with this skill.

## Safety

Dry run by default -- prints the plan, makes zero tenant writes. Real writes
require `-Execute -ConfirmToken CONVERT-SPO-PAGE`.

## Usage

```bash
# Dry run
pwsh -File scripts/spo-convert-page-to-modern.ps1 -PageName "article.aspx" -SourceLibrary "ClassicPages"

# Real conversion with field mapping
pwsh -File scripts/spo-convert-page-to-modern.ps1 -PageName "article.aspx" -SourceLibrary "ClassicPages" -FieldMapping field-mapping.json -LiteralFieldValues literals.json -Execute -ConfirmToken CONVERT-SPO-PAGE
```

## Scripts

- `scripts/spo-convert-page-to-modern.ps1` -- real PnP.PowerShell executor (dry-run/-Execute)

## Provenance

Generalized from the originating SharePoint migration repository's
`link-conversion/LinkConversion.ps1` -- removed hardcoded destination-site
name and hardcoded field mapping (project-specific source->target field
names), replaced with caller-supplied `-FieldMapping`/`-LiteralFieldValues`
JSON files.

