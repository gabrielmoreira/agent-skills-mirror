---
name: sharepoint-provision-modern-calendar-list
plugin: sharepoint-provisioning
description: Plans provisioning of a working modern SharePoint Online calendar list, structurally preventing a real platform bug (Start/End declared as site columns or content-type-linked fields silently breaks calendar view rendering) by refusing any definition that would trigger it and always planning the validated workaround shape. Gates any real write behind dry-run-by-default, an explicitly injected executor, and a plan-derived confirmation token.
allowed-tools: Bash, Read
examples:
  - "python -c \"from calendar_provisioning import plan_calendar_list, CalendarListDef; print(plan_calendar_list(CalendarListDef(title='Team Calendar')).to_dict())\""
  - "python -c \"from calendar_provisioning import apply_calendar_list; print(apply_calendar_list(plan).to_dict())\""
---

# Provision Modern Calendar List

## Trigger and Purpose

Use this skill when asked to provision a SharePoint Online calendar list
that needs to actually render correctly. There is a real, validated SPO
platform bug this skill exists to prevent: if a calendar list's Start/End
date fields are declared as site columns (or linked to the list via a
content type) *before* the list is created, SPO creates the list without
error but its calendar view silently never renders events correctly. There
is no supported fix once a list is in this state — it must be deleted and
recreated correctly.

## The workaround, encoded structurally

`plan_calendar_list` does not merely document the fix — it makes the
mistake unrepresentable:

1. **Generic List template (100), never Calendar template (106).**
2. **Start/End are always planned as list-local fields only** — never as
   site columns, never content-type-linked.
3. **The modern calendar view is always planned as a REST creation step**
   (`ViewTypeKind=1`, `ViewType2="MODERNCALENDAR"`), not left to whatever
   view a template would provision.

If a caller passes `CalendarListDef(start_end_site_columns=(...))` —
i.e., declares the exact trigger for the bug — `plan_calendar_list` raises
`StartEndScopeViolation` immediately. There is no code path that produces
a plan matching the broken shape.

## Write safety — same three-gate contract as `provision-list`

1. **Dry-run is the default.** `apply_calendar_list(plan)` with no further
   arguments changes nothing.
2. **An executor must be injected.** This module ships no tenant transport.
   Without an `executor(step, detail)` callable, a real apply raises
   `ExecutorRequired`.
3. **A confirmation token is required.** `dry_run=False` additionally
   requires `confirm=plan.confirmation_token`, derived from the plan's own
   content — a stale token (schema changed since the plan was produced)
   raises `ConfirmationRequired`.

## Where the "injected executor" actually lives

This skill's Python `apply_calendar_list(plan, executor=...)` ships no tenant
transport of its own -- by design (see Write safety above). A tested
PnP.PowerShell executor (`spo-provision-calendar.ps1`) exists in
`sharepoint-migration-planning/scripts/` and is being designed for integration
into the `apply-sharepoint-provisioning-plan` skill. Until that integration is
complete, calendar provisioning is not yet part of the full workflow — treat
this skill as a follow-up planning-only capability.

## Honest outcomes

| Outcome | Meaning |
|---|---|
| `OBSERVED` | All three steps (list creation, list-local fields, view creation) succeeded |
| `PARTIAL` | Some steps succeeded, some failed; both lists populated |
| `FORBIDDEN` | The executor raised `PermissionError` |
| `FAILED` | Every step failed |

A valid plan is never `EMPTY` — provisioning a calendar list always has the
same three required write steps.

## Usage

```bash
python -c "
from calendar_provisioning import plan_calendar_list, CalendarListDef
plan = plan_calendar_list(CalendarListDef(title='Team Calendar'))
print(plan.outcome, plan.to_dict())
"
```

Apply only after reviewing the plan, with a real executor and the plan's
own confirmation token.

## Scripts

- `scripts/calendar_provisioning.py` -- `CalendarListDef`, `plan_calendar_list`, `apply_calendar_list`, `StartEndScopeViolation`, `ExecutorRequired`, `ConfirmationRequired`
- `scripts/provisioning_outcomes.py` -- shared `Outcome` vocabulary

## Provenance

Generalized from a source-repository calendar-provisioning helper's
`Add-CalendarContentTypeSafe` / `Set-NewButtonContentTypes` /
`Add-ListFieldToContentTypeSafe` / `New-ModernCalendarList` functions,
identified during the Phase 9 exhaustive source audit
(`temp/phase9-source-audit/file-tracking.json`) as a genuine, non-obvious,
validated platform-bug workaround applicable to any SPO tenant — not the
project-specific bulk-calendar-provisioning content that consumed it in the
source repo, which stays out of scope. The three-gate write-safety
hardening matches `provision-list`'s pattern, a deliberate improvement over
the source (which had no confirmation-token gate).

