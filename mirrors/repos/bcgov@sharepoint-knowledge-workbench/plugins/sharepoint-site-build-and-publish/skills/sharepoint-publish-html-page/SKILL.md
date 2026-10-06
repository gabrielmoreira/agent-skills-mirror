---
name: sharepoint-publish-html-page
plugin: sharepoint-site-build-and-publish
description: Publishes an HTML page (.html) to a SharePoint Online document library or Site Pages library (SitePages/) with checkout/checkin discipline and post-upload presence verification. Supports native SharePoint HTML page rendering (M365 Roadmap ID 569208). Dry-run by default; real writes require -Execute and confirmation token PUBLISH-SPO-HTML.
allowed-tools: Bash, Read, Write
examples:
  - "pwsh -File scripts/spo-publish-html-page.ps1 -HtmlPath \"./dashboard.html\" -TargetLibrary \"SitePages\" -Execute -ConfirmToken PUBLISH-SPO-HTML"
---

# Publish HTML Page to SharePoint Online

Uploads and publishes `.html` files to SharePoint Online Document Libraries or the Site Pages library (`SitePages/`) using PnP.PowerShell (`Add-PnPFile`). Aligns with native SharePoint HTML Page rendering (Microsoft 365 Roadmap ID 569208).

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Dry-run by default: running without `-Execute` prints the target server-relative URL and upload plan without modifying tenant state.
- Real writes require `-Execute -ConfirmToken PUBLISH-SPO-HTML`.
- Enforces `.html` or `.htm` file extensions.
- Uses checkout/checkin discipline (`Set-PnPFileCheckedOut` / `Set-PnPFileCheckedIn -CheckinType MajorCheckIn`) when replacing existing files.
- Verifies post-upload presence and outputs the clean browser URL.

## Quick start

### 1. Dry Run (Preview upload destination)

```powershell
pwsh -File scripts/spo-publish-html-page.ps1 `
  -HtmlPath ".\test-parent.html" `
  -TargetLibrary "SitePages"
```

### 2. Live Publication

```powershell
pwsh -File scripts/spo-publish-html-page.ps1 `
  -HtmlPath ".\test-parent.html" `
  -TargetLibrary "SitePages" `
  -Execute `
  -ConfirmToken PUBLISH-SPO-HTML
```

## Workflow

1. **Prepare HTML Asset**: Ensure the local `.html` file is self-contained with modern CSS and relative links to sibling files.
2. **Plan Destination**: Choose target library (`SitePages` for intranet pages, or a document library like `Documents`).
3. **Run Dry Run**: Validate configuration and resolve the server-relative destination URL.
4. **Publish**: Execute with `-Execute -ConfirmToken PUBLISH-SPO-HTML`.
5. **Verify in Browser**: Open the returned direct URL to verify native in-browser rendering.

## Verification

Check file presence via PnP.PowerShell:
```powershell
Get-PnPFile -Url "/sites/Site/SitePages/test-parent.html"
```

## References

- Implementation: `scripts/spo-publish-html-page.ps1`
- Connection helper: `scripts/Get-WorkbenchConnectionConfig.ps1`
