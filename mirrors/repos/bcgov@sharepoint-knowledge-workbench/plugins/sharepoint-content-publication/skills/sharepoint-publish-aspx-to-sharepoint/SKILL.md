---
name: sharepoint-publish-aspx-to-sharepoint
description: Builds a human-actionable publish plan for rendered content as SharePoint modern pages. Performs no tenant writes -- matches this plugin's Phase 3 package-only architecture.
---

# publish-aspx-to-sharepoint

## Purpose

Produces a `PublishPlan` for publishing rendered content as SharePoint pages. **Does not upload
or create any page itself.**

## Real platform constraint recorded

Per Phase 3.0's confirmed finding
(`docs/research/research-experimentation/tenant-discovery/field-note-sharepoint-write-capability-discovery.md` §15): raw
`.aspx` file upload is blocked (`Access denied`) on this tenant. The only confirmed-working
mechanism is the `Add-PnPPage`/`Add-PnPPageTextPart` modern-page-creation API, not a file upload.
This skill builds the plan (source content, target page names); the real executor that consumes
it is `upload-content`'s `scripts/spo-upload-plan.ps1` — see that skill for the working
`Add-PnPPage`/`Add-PnPPageTextPart`/`Publish-PnPPage` implementation (dry-run by default, real
writes behind `-Execute -ConfirmToken UPLOAD-SPO-PLAN`).

**Correction (2026-08-17):** this SKILL.md previously stated the page-creation API "remains a
future, separately-authorized capability once Stage 3.4.3 is approved." That was stale — a real
executor was already built and shipped in `upload-content` and was never a Stage 3.4.3 write-path
question to begin with (Stage 3.4.3 concerns a different, not-yet-approved write identity; this
plugin's page-creation path already runs under the same interactive `Connect-PnPOnline` convention
every other plugin's real executor uses). Corrected here rather than left to mislead the next
reader.

## Input boundaries

- `document_id`, a local rendered `.md` source directory, and a target site-relative path.
- Refuses to build a plan from a missing source directory or one with no `.md` files.

## Prohibited scope

- This skill itself performs zero tenant I/O — it only builds the plan.
- Does not attempt raw `.aspx` file upload (confirmed blocked).

## Scripts

- `../../scripts/sharepoint_publish_plan.py` (`build_aspx_publish_plan`)
- Real executor: `upload-content`'s `../../scripts/spo-upload-plan.ps1` (consumes this skill's
  `PublishPlan` output directly).

## Tests

- `../../tests/unit/test_sharepoint_publish_plan.py`

