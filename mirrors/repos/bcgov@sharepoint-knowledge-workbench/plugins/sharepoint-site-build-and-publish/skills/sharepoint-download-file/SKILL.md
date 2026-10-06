---
name: sharepoint-download-file
plugin: sharepoint-site-build-and-publish
description: Use when downloading SharePoint Online or on-prem SP2016 files for inspection, offline analysis or migration. Supports one file, or bulk HTML/HTM/ASPX and selected document downloads from a recursive files.csv inventory, preserving source URLs and local paths for Python link extraction. Zero tenant writes; dry-run by default.
allowed-tools: Bash, Read, Write
examples:
  - "pwsh -File scripts/spo-download-file.ps1 -ServerRelativeUrl \"/sites/Site/Shared Documents/file.pdf\" -DestinationDir \"./downloads\" -Execute -ConfirmToken DOWNLOAD-SPO-FILE"
---

# Download File from SharePoint Online

Downloads files using Online PnP.PowerShell or on-prem Windows authentication, singly or from
a recursive inventory CSV. Use the bulk route for local Python page/document link analysis.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Zero tenant writes: downloads content only; never modifies tenant state.
- Dry-run by default: running without `-Execute` validates connection configuration and prints the planned local destination path without downloading.
- Real execution requires `-Execute -ConfirmToken DOWNLOAD-SPO-FILE`.
- By default does not overwrite existing local files unless `-Overwrite` is passed.
- Requires PnP.PowerShell module with delegated/interactive or app-only authentication configured.
- Bulk route: `download-sharepoint-inventory-files.ps1 -InventoryCsv <files.csv>
  -ConfigPath <profile.psd1> -OutputDir <folder>`. Default extensions: `html,htm,aspx`;
  `-Extensions 'html,htm,aspx,docx,xlsx,pptx,pdf'` selects more formats.
- Bulk execution requires `-Execute -ConfirmToken DOWNLOAD-SHAREPOINT-INVENTORY-FILES`.
  Preview writes only `downloads.csv`; live calls are user-run. Online signs in interactively;
  on-prem prompts once (or accepts `-Credential`); bulk never uses default session credentials.
- Bulk preserves remote identity in `downloads.csv` and uses hash directories to prevent
  duplicate filenames colliding. On-prem `-RawFile` downloads stored bytes through REST.
  Downloaded `.aspx` files alone do not export modern-page stored fields.

## Quick start

### 1. Dry Run (Preview download target)

```powershell
pwsh -File scripts/spo-download-file.ps1 `
  -ServerRelativeUrl "/sites/AG-CSB-INTRANET-DEV/Shared Documents/test2.html" `
  -DestinationDir ".\temp"
```

### 2. Live Download

```powershell
pwsh -File scripts/spo-download-file.ps1 `
  -ServerRelativeUrl "/sites/AG-CSB-INTRANET-DEV/Shared Documents/test2.html" `
  -DestinationDir ".\temp" `
  -Execute `
  -ConfirmToken DOWNLOAD-SPO-FILE
```

## Workflow

1. **Resolve Remote URL**: Identify the server-relative or site-relative URL of the file (e.g. `/sites/<site>/<library>/<file>`).
2. **Pre-flight Check**: Run dry-run to ensure the destination path is writable and determine if `-Overwrite` is needed.
3. **Execute Download**: Run with `-Execute -ConfirmToken DOWNLOAD-SPO-FILE`.
4. **Post-Download Verification**: Check that the local file exists and byte size matches expectations.
5. **Bulk link workflow**: Obtain `files.csv` with `sharepoint-collect-site-inventory`, preview
   selected downloads, then pass `downloads.csv` to the Python exporter in `sharepoint-extract-links`.
   Keep originals and source URLs. See [bulk download workflow](references/bulk-download-workflow.md).

## Verification

Check local file arrival and size:
```powershell
Get-Item .\temp\test2.html | Select-Object Name, Length, LastWriteTime
```

## References

- Implementation: `scripts/spo-download-file.ps1`
- Connection helper: `scripts/Get-WorkbenchConnectionConfig.ps1`
