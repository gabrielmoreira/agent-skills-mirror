---
name: sharepoint-analyze-permissions
plugin: sharepoint-discovery
description: Analyses an exported classic SharePoint permissions/security snapshot -- deriving groups, evaluated objects, and the subset with broken permission inheritance -- to produce a group provisioning worksheet and a broken-inheritance exception report. Read-only; consumes an export you provide and never contacts a tenant.
allowed-tools: Bash, Read
examples:
  - "python -c \"from permissions_analysis import run; print(run(permissions_path='permissions.json', output_dir='out/').status)\""
---

# Analyze Permissions

## Trigger and Purpose

Use this skill when planning a classic-to-modern SharePoint migration and you
need to know which groups exist and which lists/libraries have broken
permission inheritance that must be explicitly re-provisioned rather than
inherited. It consumes a permissions export -- either produced by
`scripts/collect-sharepoint-permissions.ps1` (this skill's own real,
read-only NTLM/REST collector) or supplied from any other source in one of
the two accepted shapes below.

## Two accepted export shapes

1. A flat JSON array of permission entries, one row per (principal, object)
   pair -- `webUrl`, `principalTitle`, `permissionLevels`, and either
   `objectTitle` or `listName`.
2. A structured JSON object -- `siteUrl`, `groups: [{name, permission}]`,
   `objects: [{title, hasUniqueRoleAssignments, roleAssignments}]`.

Both are accepted by the same `analyse()` entry point; the flat shape has no
explicit inheritance flag, so every derived object is treated as evaluated
(it does not claim to know inheritance state it cannot see).

## Honest outcomes

Every run returns a `DiscoveryOutcome` carrying a `DiscoveryStatus`:
`OBSERVED`, `EMPTY`, `PARTIAL`, `UNAVAILABLE`, `FORBIDDEN`, or `FAILED`.

A missing permissions export is `UNAVAILABLE` and **no output directory is
created** -- this module never fabricates a placeholder group/object list to
appear successful (the source implementation this was extracted from did;
that fallback is removed). An export with no groups or objects is `EMPTY`,
never a pass. An input that is neither a JSON array nor object is `FAILED`.

## Read-only guarantee

`permissions_analysis.py` itself makes no writes to any tenant and no network
access -- it reads the export path you name and writes analysis artifacts to
the output directory you name. `collect-sharepoint-permissions.ps1` (below)
does connect to a live site, but only ever calls REST GET
(`_api/web/roleassignments`) -- zero tenant writes.

## Collecting a fresh export

`collect-sharepoint-permissions.ps1` connects via Windows-credential/NTLM
REST (works against both legacy on-premises SharePoint 2016 and modern
SharePoint Online, since both expose the same REST surface) and writes a
flat JSON array in exactly the shape #1 above -- `webUrl`, `principalTitle`,
`permissionLevels`, and `objectTitle`/`listName`. It queries the site's own
role assignments plus every non-hidden list/library where
`HasUniqueRoleAssignments` is true (inherited-permission lists have nothing
of their own to report). Read-only -- REST GET calls only, zero tenant
writes.

```bash
pwsh -File scripts/collect-sharepoint-permissions.ps1 -SiteUrl "https://tenant.example.com/sites/Team" -OutputPath permissions.json -UseDefaultCredentials
```

## Usage

```bash
python -c "
from permissions_analysis import run
outcome = run(permissions_path='permissions.json', output_dir='out/')
print(outcome.status, outcome.detail)
"
```

## Scripts

- `scripts/collect-sharepoint-permissions.ps1` -- real, read-only NTLM/REST collector
- `scripts/permissions_analysis.py` -- `run`, `analyse`, `generate_report`
- `scripts/discovery_inputs.py` -- `DiscoveryStatus`, `DiscoveryOutcome`, `load_json_input`, `require_output_dir`

## Provenance

Adapted from `sp-discovering-permissions` in the originating SharePoint
migration repository. See
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`.

