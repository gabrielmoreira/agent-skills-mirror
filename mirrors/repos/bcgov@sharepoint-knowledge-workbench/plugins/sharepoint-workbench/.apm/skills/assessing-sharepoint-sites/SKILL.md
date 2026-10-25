---
name: assessing-sharepoint-sites
description: Assesses classic and modern SharePoint sites through read-only inventory of documents, images, subsites, permissions, schemas, metadata, columns, forms, web-parts, navigation, and reports. Use when collecting or interpreting site assessment evidence for migration, modernization, or governance decisions.
allowed-tools: Bash, Read
---

# Assess SharePoint Sites

Use this self-contained hub for read-only SharePoint discovery and assessment. Choose one
mode for a focused result, or run `inventory` first and combine the resulting exports.

## Quick start

For live collection, validate the selected SharePoint connection first, then hand the
operator the appropriate command from `references/modes/sharepoint-collect-site-inventory.md`.
For offline analysis, run from this skill's root with `scripts/` on `sys.path`:

```bash
python3 -c "import sys; sys.path.insert(0, 'scripts'); from navigation_analysis import run; print(run(navigation_path='navigation.json', output_dir='out/').status)"
```

Read the selected mode file in `references/modes/` before running a collector or analysis.
The mode files preserve the original commands, flags, examples, prompts, and verification
requirements.

## Constraints

- Read-only: collectors use SharePoint GET/read operations; analysis writes only to the
  caller-selected local output directory.
- Never fabricate completeness, formulas, choices, groups, classifications, or conclusions.
  Report `EMPTY`, `PARTIAL`, `UNAVAILABLE`, `FORBIDDEN`, and `FAILED` honestly.
- Caller-supplied exports, rules, labels, and knowledge bases remain the source of truth.
- The operator runs live tenant commands. Do not authenticate, write to a tenant, or invent
  tenant-specific defaults.
- Record every warning and missing input as an assessment gap.

## Modes

| Mode | Purpose | Start with |
|---|---|---|
| `inventory` | Collects full site structure, lists, pages, files, libraries, schemas, and content counts. | `references/modes/sharepoint-collect-site-inventory.md` |
| `permissions` | Audits permission levels, broken inheritance, evaluated objects, and groups. | `references/modes/sharepoint-analyze-permissions.md` |
| `drift-audit` | Audits on-prem schema drift and compares exported on-prem/cloud schemas against baselines. | `references/modes/sharepoint-audit-onprem-schema-drift.md` |
| `metadata` | Audits managed metadata, term groups, term sets, and taxonomy-bound fields. | `references/modes/sharepoint-audit-managed-metadata.md` |
| `columns` | Extracts calculated and choice columns, formulas, dependencies, options, and unknowns. | `references/modes/sharepoint-extract-calculated-columns.md` |
| `forms-webparts` | Analyzes custom forms, InfoPath/custom layouts, and classic web-part behavior. | `references/modes/sharepoint-analyze-custom-forms.md` |
| `navigation` | Audits site navigation trees, hierarchy, depth, and child counts. | `references/modes/sharepoint-analyze-site-navigation.md` |
| `report` | Generates consolidated executive and technical discovery reports from assessment outputs. | `references/modes/sharepoint-generate-assessment-reports.md` |

## Verification

Use the verification section in the selected mode. A successful command is not sufficient:
confirm the expected artifacts exist, inspect status values, and list all warnings and gaps.
Run focused tests from the plugin root with:

```bash
pytest plugins/sharepoint-site-assessment/tests/
```
