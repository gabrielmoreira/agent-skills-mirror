---
name: sharepoint-generate-discovery-report-set
plugin: sharepoint-discovery
description: Assembles a set of Markdown discovery reports (master page and chrome, script editor and custom code, problematic web parts, unique web part code review catalog, security and permissions, custom list forms) from previously collected SharePoint JSON/CSV export files. Use once discovery collection has produced its raw files and you need readable reports for human review. Pure local report assembly; no tenant I/O.
allowed-tools: Bash, Read
examples:
  - "pwsh -File scripts/generate-sharepoint-discovery-report-set.ps1 -AnalysisDir \".\\contoso\\analysis\" -SiteName \"Contoso Intranet\""
  - "pwsh -File scripts/generate-sharepoint-discovery-report-set.ps1 -AnalysisDir \".\\contoso\\analysis\" -SiteName \"Contoso Intranet\" -PermissionsJson \".\\contoso\\security\\permissions.json\""
---

# Generate Discovery Report Set

An assembler: it reads files a collector or analysis skill already produced and writes readable
Markdown reports into the analysis directory.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Local only. It reads files (`Get-Content`, `Import-Csv`) and writes `.md` reports into `-AnalysisDir`;
  it never contacts a SharePoint tenant.
- Never assert a conclusion the data doesn't support. Each section checks its input first. A missing
  input yields `Unavailable -- no <file> input was found at <path>`, not a hardcoded default.
- The security and permissions report is generated only when `-PermissionsJson` is supplied and
  readable; otherwise it is skipped with a `Write-Warning`.
- The Script Editor verdict is computed from the real count (`No.` only at zero, otherwise
  `Conditional -- requires manual review.`), and the custom-forms summary reports the real count and
  asks for manual review of each flagged list.
- `-AnalysisDir` and `-SiteName` have no defaults; pass both.

## Quick start

```bash
pwsh -File scripts/generate-sharepoint-discovery-report-set.ps1 -AnalysisDir ".\contoso\analysis" -SiteName "Contoso Intranet"
```

## Workflow

1. Confirm the inputs exist in `-AnalysisDir` (`webpart_content_extract.json`, `webpart-code-groups.json`,
   `site-chrome.json`, `lists_with_custom_forms.csv`). Add `-PermissionsJson` if permissions were collected.
2. Hand the user the command; the script is theirs to run.
3. Read the generated reports and list every "Unavailable" section and every `Write-Warning` as a gap.

## Verification

Confirm each expected `.md` report exists in `-AnalysisDir`, and that any skipped report has a matching
warning. A report set with unavailable sections is partial, not complete.

## References

- [Integrity fixes](references/discovery-report-set-integrity.md): read for what the six reports contain,
  why each hardcoded conclusion was replaced, and provenance.
