---
name: managing-sharepoint-navigation
description: "Export, diff, validate, and provision SharePoint Online top navigation and Quick Launch menus from an Excel workbook or JSON snapshot using PnP PowerShell. Use when asked to 'sync navigation', 'update navigation menu', 'export navigation', 'diff navigation', or provision site menus."
---

# Managing SharePoint Navigation

Manage SharePoint Online **native** navigation declaratively. Native navigation stays
the runtime source of truth in SharePoint; the Excel workbook is a structured, reviewable
way to define, diff, and provision menu nodes.

## Contents

- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Constraints](#constraints)
- [Modes](#modes)
- [Verification](#verification)

## Quick start

1. **Export live menu:**
   ```powershell
   pwsh -File scripts/export-spo-navigation.ps1 -ConfigPath <config.psd1> -Format Json -OutputPath temp/nav-live.json
   ```
2. **Generate editable workbook from snapshot:**
   ```bash
   python3 scripts/navigation_plan.py to-workbook --snapshot temp/nav-live.json --out temp/nav-menu.xlsx
   ```
3. **Validate & Diff workbook against live snapshot:**
   ```bash
   python3 scripts/navigation_plan.py plan --workbook temp/nav-menu.xlsx --out temp/nav-plan.json
   python3 scripts/navigation_plan.py diff --plan temp/nav-plan.json --snapshot temp/nav-live.json --out temp/nav-ops.json
   ```
4. **Dry-run apply:**
   ```powershell
   pwsh -File scripts/sync-spo-navigation.ps1 -ConfigPath <config.psd1> -OpsPath temp/nav-ops.json
   ```
5. **Execute write (human-gated):** Add `-Execute -ConfirmToken PROVISION-SPO-NAV`.

## Workflow

1. **Export or Author**: Start with an exported live tree (`export-navigation`) or the declarative schema template (`assets/navigation-menu.xlsx`).
2. **Diff & Validate**: Run `navigation_plan.py` to validate hierarchy rules and compute the surgical operations payload (`diff-navigation`).
3. **Review Operations**: Review proposed `add_child`, `add_root`, `update`, and `prune` actions before executing.
4. **Synchronize**: Apply via PnP PowerShell with dry-run verification before passing `-Execute` and `-ConfirmToken PROVISION-SPO-NAV` (`sync-navigation`).

## Constraints

- Default operations are local and read-only. Tenant writes require `-Execute` and explicit `-ConfirmToken PROVISION-SPO-NAV`.
- Removal is strictly opt-in: missing nodes are only reported unless `-Prune` is explicitly passed.
- Preflight verifies all update and prune targets, saves a JSON backup, and halts at the first error.
- All helpers and PowerShell scripts reside locally in `scripts/`; zero external symlinks.

## Modes

| Mode | Purpose | Instructions |
|:---|:---|:---|
| `export-navigation` | Export live SPO navigation tree to JSON or terminal | [mode](references/modes/export-navigation.md) |
| `diff-navigation` | Validate workbook structure and compute change operations | [mode](references/modes/diff-navigation.md) |
| `sync-navigation` | Apply navigation plan idempotently to SharePoint Online | [mode](references/modes/sync-navigation.md) |
| `workbook-schema` | Column structure, rules, and linkless header conventions | [mode](references/modes/workbook-schema.md) |

## Verification

The verification contract and test scenarios are documented in `references/acceptance-criteria.md`. Run automated tests via:
```bash
pytest tests/test_navigation_plan.py
```
