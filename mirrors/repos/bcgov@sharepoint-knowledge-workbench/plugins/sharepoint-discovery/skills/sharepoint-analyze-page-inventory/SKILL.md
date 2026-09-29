---
name: sharepoint-analyze-page-inventory
plugin: sharepoint-discovery
description: Analyses an exported classic SharePoint page inventory -- scoring per-page migration complexity, classifying web-part categories, and emitting a disposition hint per page -- using a caller-supplied rules file. Read-only; consumes an export you provide and never contacts a tenant.
allowed-tools: Bash, Read
examples:
  - "python -c \"from page_inventory_analysis import run; print(run(inventory_path='inv.json', rules_path='rules.json', output_dir='out/').status)\""
---

# Analyze Page Inventory

## Trigger and Purpose

Use this skill when planning a classic-to-modern SharePoint migration and you
need to know which pages are cheap to move and which are hard. It consumes a
page inventory exported from a tenant -- either produced by
`scripts/collect-sharepoint-page-inventory.ps1` (this skill's own real,
read-only PnP.PowerShell collector) or supplied from any other source in the
same JSON shape -- and produces a scored, prioritised analysis.

It answers: how complex is each page, which web-part categories appear, and
what is the suggested disposition (migrate as-is, rebuild, retire).

## Rules are data, not code

`load_rules(path)` reads a caller-supplied JSON rules file. Complexity
weights, category classifications, and disposition thresholds are **all**
supplied by you -- **no site-specific migration judgement is built in.** The
source implementation this was extracted from embedded one organisation's
thresholds directly; those are removed.

## Honest outcomes

Every run returns a `DiscoveryOutcome` carrying a `DiscoveryStatus`:
`OBSERVED`, `EMPTY`, `PARTIAL`, `UNAVAILABLE`, `FORBIDDEN`, or `FAILED`.

A missing input file is `UNAVAILABLE` and **no output directory is created** --
the run does not fabricate defaults to appear successful. An empty inventory
is `EMPTY`, never a pass.

## Read-only guarantee

`page_inventory_analysis.py` itself makes no writes to any tenant and no
network access -- it reads the export path you name and writes analysis
artifacts to the output directory you name.
`collect-sharepoint-page-inventory.ps1` (below) does connect to a live
tenant, but only ever calls read cmdlets (`Get-PnP*`) -- it makes zero
tenant writes.

## Collecting a fresh export

`collect-sharepoint-page-inventory.ps1` connects interactively (delegated
auth, per `.agent/rules/sharepoint-ps1-authentication-convention.md`) to a
live site and writes a `page-inventory.json` in the exact shape
`page_inventory_analysis.py` consumes. Read-only -- calls only `Get-PnP*`
cmdlets, zero tenant writes. Covers the Site Pages library only in this first
pass; list-form (`NewForm`/`EditForm`/`DispForm`) scanning is not yet
implemented (`-IncludeListForms` currently warns and no-ops).

```bash
pwsh -File scripts/collect-sharepoint-page-inventory.ps1 -SiteUrl "https://tenant.sharepoint.com/sites/Test" -OutputPath page-inventory.json
```

## Usage

```bash
python -c "
from page_inventory_analysis import run
outcome = run(inventory_path='page-inventory.json', rules_path='rules.json', output_dir='out/')
print(outcome.status, outcome.detail)
"
```

## Scripts

- `scripts/collect-sharepoint-page-inventory.ps1` -- real, read-only PnP.PowerShell collector
- `scripts/page_inventory_analysis.py` -- `run`, `analyse`, `generate_report`, `load_rules`, `compute_complexity`, `disposition_hint`
- `scripts/discovery_inputs.py` -- `DiscoveryStatus`, `DiscoveryOutcome`, `load_json_input`, `require_output_dir`

## Provenance

Adapted from `sp-discovering-pages` / `sp-analysing-aspx-pages` in the
originating SharePoint migration repository. See
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`.

