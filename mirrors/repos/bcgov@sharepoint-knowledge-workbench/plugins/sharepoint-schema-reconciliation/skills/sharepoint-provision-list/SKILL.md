---
name: sharepoint-provision-list
plugin: sharepoint-provisioning
description: Reconciles a whole declarative SharePoint provisioning schema (site columns, content types, target lists) against caller-supplied current state, detects duplicate-titled lists before any delete, and gates any real write behind dry-run-by-default, an explicitly injected executor, and a plan-derived confirmation token. THE ONLY WRITE-capable skill in this plugin.
allowed-tools: Bash, Read
examples:
  - "python -c \"from list_provisioning import plan_provisioning; print(plan_provisioning(schema, current).to_dict())\""
  - "python -c \"from list_provisioning import apply_provisioning; print(apply_provisioning(plan).to_dict())\""
---

# Provision List

## Trigger and Purpose

Use this skill to reconcile a whole declarative schema — site columns,
content types, and target list/library objects — against a caller-supplied
observation of current live state, and (only after explicit review) apply
the resulting plan through your own injected executor.

Stage: `provision-content-types` / `provision-fields` (per-object planning) →
`provision-list` (whole-schema reconciliation and gated apply).

## Write safety — three independent gates, plus one unconditional refusal

Per Phase 9 spec section 13, no autonomous production write is reachable —
this mirrors `sharepoint-link-remediation`'s `remediate-links` exactly:

1. **Dry-run is the default.** `apply_provisioning(plan)` with no arguments
   changes nothing.
2. **An executor must be injected.** This module ships no tenant transport.
   Without an `executor(step, detail)` callable, a real apply raises
   `ExecutorRequired` rather than silently no-op'ing or faking success.
3. **A confirmation token is required.** `dry_run=False` additionally
   requires `confirm=plan.confirmation_token`, derived from the plan's own
   content. A stale or absent token raises `ConfirmationRequired`, so a plan
   cannot be applied after the underlying schema or observed state changes.
4. **Duplicate-titled lists unconditionally block execution.** If
   `detect_duplicate_lists` found more than one live object sharing a
   `recreate=True` list's exact title, `apply_provisioning` raises
   `DuplicateListsBlockProvisioning` regardless of confirmation token — a
   real incident in the source material (a stray duplicate list silently
   resolved to the wrong one) is why this gate exists.

## Where the "injected executor" actually lives

This skill's Python `apply_provisioning(plan, executor=...)` ships no tenant
transport of its own -- by design (see Write safety above). The real,
tested PnP.PowerShell executor that plan JSON is meant to be submitted to is
`sharepoint-migration-planning`'s `apply-sharepoint-provisioning-plan` skill
(`spo-provision-list.ps1` specifically, which consumes this module's
`ProvisioningPlan.to_dict()` output verbatim -- see that script's own
docstring for the exact field-name match). This skill produces the plan;
that skill is the executor you inject.

## Honest outcomes

| Outcome | Meaning |
|---|---|
| `OBSERVED` | All intended steps succeeded (or, for a plan, real changes are planned) |
| `EMPTY` | Nothing to do -- schema and current state already match |
| `PARTIAL` | Some steps succeeded, some failed; both lists populated |
| `FORBIDDEN` | The executor raised `PermissionError` |
| `FAILED` | Every step failed, or the plan carries a blocking duplicate finding |

## Fail-loud deletion verification

`verify_deletion_complete(title, still_exists=...)` raises
`DeletionVerificationFailed` if an object expected to be gone after a
delete step is still observed to exist -- never silently assume a delete
succeeded.

## Usage

```bash
# 1. Plan (always safe -- pure computation over caller-supplied inputs)
python -c "
from list_provisioning import plan_provisioning
plan = plan_provisioning(schema, current_state)
print(plan.outcome, plan.to_dict())
"
```

Apply only after reviewing the plan, with a real executor and the plan's own
confirmation token, and only once any blocking findings are resolved.

## Scripts

- `scripts/list_provisioning.py` -- `ProvisioningSchema`, `CurrentState`, `ListDef`, `ListState`, `plan_provisioning`, `detect_duplicate_lists`, `apply_provisioning`, `verify_deletion_complete`, safety errors
- `scripts/field_provisioning.py`, `scripts/content_type_provisioning.py` -- per-object planning this skill aggregates
- `scripts/provisioning_outcomes.py` -- shared `Outcome` vocabulary

## Provenance

Adapted from `list-helpers.ps1` (`Invoke-WithRetry`, `New-ListSafe`,
`New-LibrarySafe`) plus the reconcile-schema, duplicate-detection, and
fail-loud *pattern* (not any project-specific content) of
`reset-and-provision-etl-target-schema.ps1` — see
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`.
The three-gate write-safety hardening (dry-run default, injected executor,
confirmation token) is a deliberate improvement over the source, which had
no confirmation-token gate at all.

