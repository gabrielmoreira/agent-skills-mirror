---
name: sharepoint-copy-page-between-sites
plugin: sharepoint-site-build-and-publish
description: Builds a safe, human-reviewed plan for copying or promoting an existing SharePoint Online Site Page, such as an .aspx page in Site Pages, from one SPO site to another. Use for TEST-to-PROD page promotion requests. Performs no tenant writes by default, runs a reviewed copy only with -Execute and a confirmation token, and avoids raw .aspx file upload.
allowed-tools: Bash, Read, Write
examples:
  - "pwsh -File scripts/spo-copy-page.ps1 -SourcePageUrl \"https://tenant.sharepoint.com/sites/Test/SitePages/Page.aspx\" -TargetPageUrl \"https://tenant.sharepoint.com/sites/Prod/SitePages/Page-copy.aspx\""
---

# Copy Page Between Sites

Plan promotion of an existing SPO Site Page from a source site to a target site. This is SPO-to-SPO page copy, not SP2016 classic page modernization.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Do not run live tenant write commands automatically. The script prints a plan by default; a real copy needs `-Execute -ConfirmToken COPY-SPO-PAGE` and is run by the user.
- Use `-Overwrite` only when the target page may be replaced.
- Never use raw `.aspx` file upload; use the supported SPO page APIs and PnP promotion patterns.
- Reject a non-`.aspx` page name. Route a classic SP2016 modernization request to the page modernization skills.
- When running from an installed copy, pass `-ConfigPath` (or `-ClientId`, `-TenantId`).

## Quick start

```bash
pwsh -File scripts/spo-copy-page.ps1 -SourcePageUrl "https://tenant.sharepoint.com/sites/Test/SitePages/Page.aspx" -TargetPageUrl "https://tenant.sharepoint.com/sites/Prod/SitePages/Page-copy.aspx"
```

## Workflow

1. Confirm the source and target site URLs, page library, source and target page names, and the overwrite expectation.
2. Build the plan with the script above (full URLs under `/SitePages/`).
3. Present the plan and the recommended human-run execution approach; do not execute for the user.
4. Same-site and cross-site copies take different flows; see the details reference before executing.

## Verification

The plan names the correct source and target paths, whether overwrite is allowed, and the flow (same-site or cross-site). After a user-run execution, confirm the target page exists.

## References

- [Copy plan details](references/page-copy-plan-details.md): read for the steps, the same-site vs cross-site flows and the common failures.
- [Gates, tokens and config](references/page-execution-gates-and-config.md): read for the token table and the `-ConfigPath` note.
- [Acceptance criteria](references/acceptance-criteria.md): read when checking the skill's expected behavior.
