---
name: sharepoint-audit-list-content
plugin: sharepoint-content-migration
status: active
description: >
  Audit list and library content fidelity between SP2016 On-Premises and SharePoint Online.
  Reconciles multi-value and single-value Person lookup columns against ground truth, detects Item ID
  vs Case ID suffix shifts/skews, flags dropped/missing pointers, and identifies false matches caused
  by string/name collisions. Use when verifying list content integrity, auditing ShareGate migrations,
  or preparing non-destructive lookup backfills.
allowed-tools: Bash, Read, Write
---

# SharePoint List Content Audit

Read-only content-level and lookup reconciliation between a SharePoint 2016 On-Premises source and SharePoint Online.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Phases 1 and 2 are read-only and zero-PII. The raw PII CSVs are purged with `--delete-pii-after` once the Persons
  mapping is built.
- Run Phase 1 and Phase 2 together, in order, every time. Phase 1 numbers are data, not findings; the report has been
  silently wrong before.
- Always pass `--list-name ALL` for the real analysis run. When smoke-testing one list, also override `--output-md`
  and `--output-csv` to a scratch path, or the canonical site-wide report is overwritten.
- Phase 3 healing is non-destructive and `ITAU_Cases` only. Start with `-Limit 5 -DryRun`, and run it only after
  Phase 2 confirms the gap is real. Live SP2016 and SPO access is the user's to run.
- Run commands from this skill's root; scripts are in `scripts/`.

## Quick start

Generate the zero-PII executive tables from already-exported data:

```powershell
python -B scripts/analyze-lookup-variances.py --list-name ALL
```

## Workflow

1. **Phase 1, deterministic.** If Persons was re-migrated, rebuild the ID mapping (Step 0). Export paired list content
   and run the reconciliation (Step 1), then generate the tables (Step 2).
2. **Phase 2, interpretive, required after every Phase 1 run.** Refresh the narrative variance analysis with the five
   required sections, investigate suspicious numbers with scratch scripts, and record recurring root causes in
   `known-issues.json`.
3. **Phase 3, healing, only if a real gap is confirmed.** Dry run first, then the full execution.

Every command and the five Phase 2 sections are in [the workflow](references/list-content-audit-workflow.md).

## Verification

Confirm the Phase 1 report and CSV exist, and that the Phase 2 narrative was refreshed this run. Check any
`0 Source Pointers in Dataset` or `100.0%` with far fewer co-existing rows than source rows against the script before
calling it a finding.

## References

- [Workflow](references/list-content-audit-workflow.md): read before running any phase, and for the Phase 2 section list.
- [Model, scripts and known issues](references/list-content-audit-scripts.md): read for the ground-truth model,
  what each script does, and the known-issues registry.
- [Acceptance criteria](references/acceptance-criteria.md): read when checking the skill's expected behavior.
