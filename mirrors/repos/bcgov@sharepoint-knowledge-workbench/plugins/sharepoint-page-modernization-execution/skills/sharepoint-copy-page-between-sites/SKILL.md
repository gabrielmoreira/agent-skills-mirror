---
name: sharepoint-copy-page-between-sites
plugin: sharepoint-content-publication
description: Build a safe, human-reviewed plan for copying or promoting an existing SharePoint Online Site Page, such as an .aspx page in Site Pages, from one SPO site to another. Use for TEST-to-PROD page promotion requests; performs no tenant writes by default and avoids raw .aspx file upload.
allowed-tools: Bash, Read, Write
---

# copy-spo-page-between-sites

## Identity

Plans promotion of an existing SharePoint Online Site Page from a source SPO site
to a target SPO site. This is for SPO-to-SPO page copy/promotion, not SP2016
classic page modernization.

## Steps

1. Confirm the source site URL, target site URL, page library, source page
   name, target page name, and overwrite expectation.
2. Build a page-to-page copy plan with `scripts/spo-page-copy-plan.ps1`.
   - Use `-SourcePageUrl` and `-TargetPageUrl` when the user provides full
     source and destination page URLs.
   - Use `-Overwrite` only when the target page may be replaced.
3. Present the generated plan and the recommended human-run execution approach.
4. Do not run live tenant write commands automatically.

## Common Failures

- A non-`.aspx` page name is supplied.
- The target page should use a different name but no `target_page_name` is
  provided to the plan helper.
- The request is actually classic SP2016 modernization; route that to the page
  modernization skills instead.
- The user asks for raw `.aspx` upload; prefer supported SPO page APIs/PnP page
  promotion patterns instead.

