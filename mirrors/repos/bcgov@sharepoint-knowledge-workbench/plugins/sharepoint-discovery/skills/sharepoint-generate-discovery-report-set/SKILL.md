---
name: sharepoint-generate-discovery-report-set
plugin: sharepoint-discovery
description: Assembles a set of Markdown discovery reports (master page/chrome, script editor & custom code, problematic web parts, unique web part code review catalog, security/permissions, custom list forms) from previously-collected SharePoint JSON/CSV export files. Pure local report assembly -- no tenant I/O.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/generate-sharepoint-discovery-report-set.ps1 -AnalysisDir \".\\contoso\\analysis\" -SiteName \"Contoso Intranet\""
  - "pwsh -File scripts/generate-sharepoint-discovery-report-set.ps1 -AnalysisDir \".\\contoso\\analysis\" -SiteName \"Contoso Intranet\" -PermissionsJson \".\\contoso\\security\\permissions.json\""
---

# Generate Discovery Report Set

## Trigger and Purpose

Use this skill once discovery collection has already produced its raw JSON/CSV export
files and you need those turned into readable Markdown reports for human review --
master page/chrome customization, Script Editor & custom-code web part analysis,
problematic web parts, a per-group web part code review catalog, a security/permissions
summary (only if permissions data was collected), and custom list form usage. This is a
pure **assembler** skill: it reads files a collector skill (e.g.
`collect-sharepoint-inventory`) or an analysis skill already produced, and never
contacts a SharePoint tenant itself.

## Integrity fix -- why this is not a literal port

This skill's script was ported from an originating migration repository's
`generate-discovery-reports.ps1`, but that source script had a real data-integrity
problem: several report sections asserted fixed, hardcoded conclusions regardless of
what the actual scan data said. This version fixes each one:

1. **Modern Script Editor (PnP SPFx) verdict.** The source always printed
   `**Are Modern Script Editor Web Parts (PnP SPFx) needed for this site?**: **No.**`
   as fixed prose, even though it had already computed `$sewpEntries.Count` (the actual
   Script Editor web part count) just above that line. This version computes the verdict
   from that count: `No.` only when `$sewpEntries.Count -eq 0` (with the reasoning shown
   using the real numbers), otherwise `Conditional -- requires manual review.` with an
   explanation that each detected Script Editor web part must be reviewed individually.
   The same fix is applied to the corresponding cell in `PROBLEMATIC-WEBPARTS-SUMMARY.md`.

2. **Custom forms summary.** The source always printed
   `**Genuine Custom Script Overrides Downloaded:** 0 (all standard OOB forms)` and
   `All list forms on this site use standard OOB SharePoint forms` as fixed prose, even
   though `$formCount` (read from a real CSV) could be nonzero. This version reports the
   real `$formCount`, states plainly that override-vs-OOB determination is **not**
   something the `lists_with_custom_forms.csv` input can answer (it only flags which
   lists have a custom form URL), and asks for manual review of each flagged list rather
   than asserting "all standard."

3. **Security & permissions summary.** The source generated `security-analysis-summary.md`
   from **zero data inputs** -- it was 100% static boilerplate text with no computed
   values at all. This version does not generate that report unless the caller supplies
   an explicit `-PermissionsJson` path; if omitted or unreadable, the report is skipped
   entirely and a `Write-Warning` explains why, rather than emitting an unearned
   narrative. When supplied, the report states real `Groups`/`BrokenInheritance` counts
   read from that file.

4. **Missing-input sections in general.** Every report section now checks whether its
   underlying input file exists before writing any conclusion. If a required input
   (`webpart_content_extract.json`, `webpart-code-groups.json`, `site-chrome.json`,
   `lists_with_custom_forms.csv`) is absent, the report says so explicitly
   (`Unavailable -- no <file> input was found at <path>`) instead of silently falling
   back to a hardcoded default value or narrative.

## Generalization from the source

The source script hardcoded a project-specific path-fixup regex (matching a specific
tenant's URL naming quirk) and assumed one project's fixed report-file layout. This
version drops that regex entirely -- `-AnalysisDir` is used as given -- and both
`-AnalysisDir` and `-SiteName` remain fully generic parameters with no project-specific
defaults.

## Read-only guarantee

This script performs local filesystem reads only (`Get-Content`, `Import-Csv`) and local
writes of the generated `.md` report files into `-AnalysisDir`. It never contacts a
SharePoint tenant.

## Usage

```bash
pwsh -File scripts/generate-sharepoint-discovery-report-set.ps1 -AnalysisDir ".\contoso\analysis" -SiteName "Contoso Intranet"
pwsh -File scripts/generate-sharepoint-discovery-report-set.ps1 -AnalysisDir ".\contoso\analysis" -SiteName "Contoso Intranet" -PermissionsJson ".\contoso\security\permissions.json"
```

## Related assets

`plugins/sharepoint-discovery/assets/master-discovery-meta-review-template.md` (if
present) is a separate roll-up template used by another skill to synthesize a
strategic/executive-level review across a full discovery run; it is not duplicated here.

## Scripts

- `scripts/generate-sharepoint-discovery-report-set.ps1` -- assembles the six reports
  described above from local JSON/CSV inputs.

## Provenance

Ported and corrected from `plugins/sharepoint-migration/scripts/page-migration/
generate-discovery-reports.ps1` in the originating SharePoint migration repository. All
hardcoded conclusions not backed by the actual input data were removed or made
conditional on real computed values (see "Integrity fix" above), and all project-specific
path/naming assumptions were generalized.

