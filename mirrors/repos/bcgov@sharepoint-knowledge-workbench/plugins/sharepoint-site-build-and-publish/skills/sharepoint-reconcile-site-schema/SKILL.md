---
name: sharepoint-reconcile-site-schema
plugin: sharepoint-site-build-and-publish
description: Reconciles a whole declarative SharePoint provisioning schema (site columns, content types, target lists) against caller-supplied current state, detects duplicate-titled lists before any delete, and gates any real write behind dry-run-by-default, an explicitly injected executor and a plan-derived confirmation token. Use for whole-schema reconciliation and the gated apply.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from list_provisioning import plan_provisioning; print(plan_provisioning(schema, current).to_dict())\""
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from list_provisioning import apply_provisioning; print(apply_provisioning(plan).to_dict())\""
---

# Provision List

Reconcile a whole declarative schema (site columns, content types and list or library objects) against observed live state, and apply the plan only after explicit review.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Four write gates, structural not advisory: dry-run by default; an `executor(step, detail)` must be injected (else `ExecutorRequired`); a real apply needs `confirm=plan.confirmation_token` (else `ConfirmationRequired`); and duplicate-titled
  lists unconditionally block execution (`DuplicateListsBlockProvisioning`, whatever the token).
- Never assume a delete worked: `verify_deletion_complete` raises `DeletionVerificationFailed` if a deleted object still exists.
- Apply only after the user reviews the plan and any blocking findings are resolved. The real executor is the `sharepoint-site-build-and-publish` plugin's `spo-provision-list.ps1`; this skill ships no tenant transport.
- Run from this skill's root with `scripts/` on `sys.path`. Standard library only.

## Quick start

```python
import sys; sys.path.insert(0, "scripts")
from list_provisioning import plan_provisioning
plan = plan_provisioning(schema, current_state)   # always safe
print(plan.outcome, plan.to_dict())
```

## Workflow

1. Build the `ProvisioningSchema` and the `CurrentState` observation; call `plan_provisioning`.
2. Review the plan and any `blocking_findings` with the user; resolve duplicates first.
3. To apply: `apply_provisioning(plan, executor=..., dry_run=False, confirm=plan.confirmation_token)`.
4. Check deletions with `verify_deletion_complete`.

## Verification

The plan outcome is `OBSERVED` (changes planned) or `EMPTY` (already matches); `FAILED` with a blocking finding means it cannot be applied. After an apply, confirm the outcome and that each deleted object is gone.

## References

- [List provisioning details](references/list-provisioning-details.md): read for the stage, full usage, scripts and provenance.
- [Pipeline and write safety](references/schema-reconciliation-pipeline.md): read for the gates in full, the outcome table, and where the executors live.
