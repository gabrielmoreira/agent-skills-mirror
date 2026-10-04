---
name: sharepoint-reconcile-calendar-list
plugin: sharepoint-site-build-and-publish
description: Plans provisioning of a working modern SharePoint Online calendar list, structurally preventing a real platform bug (Start/End declared as site columns or content-type-linked fields silently breaks calendar view rendering) by refusing any definition that would trigger it and always planning the validated workaround shape. Use when asked for a calendar list. Gates any real write behind dry-run-by-default, an injected executor and a plan-derived confirmation token.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from calendar_provisioning import plan_calendar_list, CalendarListDef; print(plan_calendar_list(CalendarListDef(title='Team Calendar')).to_dict())\""
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from calendar_provisioning import apply_calendar_list; print(apply_calendar_list(plan).to_dict())\""
---

# Provision Modern Calendar List

Provision a SharePoint Online calendar list that actually renders, by making the bug-triggering shape impossible to plan.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Never plan Start/End as site columns or content-type-linked fields. `CalendarListDef(start_end_site_columns=(...))` raises `StartEndScopeViolation`; there is no supported fix for a list created that way (it must be deleted and recreated).
- Always the Generic List template (100), never the Calendar template (106); Start/End are list-local fields only; the modern calendar view is a REST creation step (`ViewTypeKind=1`, `ViewType2="MODERNCALENDAR"`).
- Same write gates as `sharepoint-reconcile-site-schema`: dry-run by default; an injected executor (else `ExecutorRequired`); `confirm=plan.confirmation_token` (else `ConfirmationRequired`).
- The PowerShell executor `spo-provision-calendar.ps1` ships in this plugin's `scripts/calendar-executor/` namespace and is not part of `sharepoint-apply-provisioning-plan`; delegate execution to it.
- Run from this skill's root with `scripts/` on `sys.path`. Standard library only.

## Quick start

```python
import sys; sys.path.insert(0, "scripts")
from calendar_provisioning import plan_calendar_list, CalendarListDef
plan = plan_calendar_list(CalendarListDef(title="Team Calendar"))
print(plan.outcome, plan.to_dict())
```

## Workflow

1. Plan with `plan_calendar_list(CalendarListDef(title=...))`.
2. Review the three steps (list creation, list-local fields, view creation) with the user.
3. Apply only with a real executor and the plan's own token: `apply_calendar_list(plan, executor=..., dry_run=False, confirm=plan.confirmation_token)`.

## Verification

A valid plan always has the same three write steps and is never `EMPTY`. After an apply, `OBSERVED` means all three succeeded; treat `PARTIAL`, `FORBIDDEN` and `FAILED` as incomplete.

## References

- [Calendar provisioning details](references/calendar-provisioning-details.md): read for the platform bug, the structural workaround, outcomes and the executor note.
- [Pipeline and write safety](references/schema-reconciliation-pipeline.md): read for the shared gates and outcome table.
