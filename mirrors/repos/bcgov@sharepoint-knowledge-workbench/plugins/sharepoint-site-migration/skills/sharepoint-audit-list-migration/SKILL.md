---
name: sharepoint-audit-list-migration
plugin: sharepoint-site-migration
status: active
description: >
  Audit list and library content fidelity between an on-premises SharePoint source and SharePoint Online.
  Reconciles multi-value and single-value identity lookup columns against ground truth, detects item ID
  vs business-key suffix shifts/skews, flags dropped/missing pointers, and identifies false matches caused
  by string/name collisions. Use when verifying list content integrity, auditing ShareGate migrations,
  or preparing the evidence for a separately authorized lookup repair. This skill never writes to a tenant.
allowed-tools: Bash, Read, Write
---

# SharePoint List Content Audit

Read-only, config-driven content-level and lookup reconciliation between an on-premises SharePoint source and SharePoint Online. The site, lists and columns are described in an `audit-config.json`, never in the scripts.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Phases 1 and 2 are read-only and zero-PII. The raw PII CSVs are purged with `--delete-pii-after` once the Authors
  mapping is built.
- Run Phase 1 and Phase 2 together, in order, every time. Phase 1 numbers are data, not findings; the report has been
  silently wrong before.
- Always pass `--list-name ALL` for the real analysis run. When smoke-testing one list, also override `--output-md`
  and `--output-csv` to a scratch path, or the canonical site-wide report is overwritten.
- This skill is read-only. Repair is **not part of it**: stop after Phase 2 and report findings. Live source and SharePoint Online
  access is the user's to run.
- This skill ships no repair script; any repair is a separate, explicitly authorized action outside it.
- Run commands from this skill's root; scripts are in `scripts/`.

## Quick start

Generate the zero-PII executive tables from already-exported data:

```powershell
python -B scripts/analyze-lookup-variances.py --list-name ALL
```

## Workflow

1. **Phase 1, deterministic.** Write the audit config and, if the identity list was re-migrated, rebuild the ID mapping (Step 0). Export paired list content
   and run the reconciliation (Step 1), then generate the tables (Step 2).
2. **Phase 2, interpretive, required after every Phase 1 run.** Refresh the narrative variance analysis with the five
   required sections, investigate suspicious numbers with scratch scripts, and record recurring root causes in
   your local notes of known issues.
3. **Stop here.** Report the confirmed gaps. Any repair is a separate, explicitly authorized action (see the repair
   boundary in the constraints and [the workflow](references/list-content-audit-workflow.md#repair-boundary-not-part-of-the-read-only-audit)).

Every command and the five Phase 2 sections are in [the workflow](references/list-content-audit-workflow.md).

## Verification

Confirm the Phase 1 report and CSV exist, and that the Phase 2 narrative was refreshed this run. Check any
`0 Source Pointers in Dataset` or `100.0%` with far fewer co-existing rows than source rows against the script before
calling it a finding.

## References

- [Workflow](references/list-content-audit-workflow.md): read before running any phase, and for the Phase 2 section list.
- [Model, scripts and audit config](references/list-content-audit-scripts.md): read for the ground-truth model,
  what each script does, and the audit config format.
- [Acceptance criteria](references/acceptance-criteria.md): read when checking the skill's expected behavior.
