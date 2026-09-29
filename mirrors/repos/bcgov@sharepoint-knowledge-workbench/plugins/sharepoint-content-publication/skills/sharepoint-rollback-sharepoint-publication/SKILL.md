---
name: sharepoint-rollback-sharepoint-publication
description: Builds a rollback plan reversing a prior publication's exact actions, package-scoped to one document, then a real PnP executor removes each target (Remove-PnPPage/Remove-PnPFile, with fail-loud removal verification). Dry-run by default.
---

# rollback-sharepoint-publication

## Purpose

Given a prior `PublishPlan`, produces a `RollbackPlan` — the exact set of targets to remove — via
`sharepoint_publish_plan.py`. The real executor, `scripts/spo-rollback-publication.ps1`, then
removes each target: `Remove-PnPPage` for a `SitePages` target, `Remove-PnPFile` for a
document-library target, verifying absence after each removal (throws if a target is still
present, rather than reporting success on an unverified delete). Package-scoped: only reverses
the named `document_id`'s own actions, never another document's — rejects a mismatched
`document_id` rather than silently rolling back the wrong document. Dry-run by default; real
deletions require `-Execute -ConfirmToken ROLLBACK-SPO-PLAN`.

**Correction (2026-08-17):** this SKILL.md previously said real tenant writes "remain gated
behind Stage 3.4.3's unapproved write-identity decision." That was a stale/incorrect blocker —
see `publish-markdown-to-sharepoint`'s SKILL.md for the same correction and reasoning. The real
gap was simply that no removal executor had been built yet — now fixed.

## Input boundaries

- `document_id` must match the supplied `PublishPlan`'s own `document_id` exactly — a mismatch
  raises `PlanError` rather than producing a plan for the wrong document.

## Prohibited scope

- The planning module itself performs zero tenant I/O — it only builds the plan.
- The real executor performs no deletion without `-Execute -ConfirmToken ROLLBACK-SPO-PLAN`, and
  verifies each target is actually gone afterward rather than trusting the cmdlet call alone.

## Scripts

- `../../scripts/sharepoint_publish_plan.py` (`build_rollback_plan`)
- Real executor: `../../scripts/spo-rollback-publication.ps1`

## Tests

- `../../tests/unit/test_sharepoint_publish_plan.py` — includes the cross-document-mismatch
  rejection test (a real safety property, not a hypothetical edge case).

