---
name: sharepoint-analyze-site-navigation
plugin: sharepoint-discovery
description: Analyses an exported classic SharePoint site navigation tree (top nav and quick launch) -- flattening it with per-node depth and child counts, and computing max-depth statistics -- to produce a navigation architecture summary. Read-only; consumes an export you provide and never contacts a tenant.
allowed-tools: Bash, Read
examples:
  - "python -c \"from navigation_analysis import run; print(run(navigation_path='nav.json', output_dir='out/').status)\""
---

# Analyze Site Navigation

## Trigger and Purpose

Use this skill when planning a classic-to-modern SharePoint migration and you
need to understand how deep and how wide a site's navigation chrome is before
mapping it onto modern hub/global navigation. It consumes a navigation export
already pulled from a tenant (top navigation bar and quick launch, each an
arbitrarily nested tree) and produces a flattened, depth-annotated summary.

It answers: how many top-level nodes exist, how deep does each tree nest, and
what does the full node list look like with depth and child counts.

## Honest outcomes

Every run returns a `DiscoveryOutcome` carrying a `DiscoveryStatus`:
`OBSERVED`, `EMPTY`, `PARTIAL`, `UNAVAILABLE`, `FORBIDDEN`, or `FAILED`.

A missing input file is `UNAVAILABLE` and **no output directory is created**.
An export with no navigation nodes at all is `EMPTY`, never a pass. An input
that isn't a JSON object (e.g. an array or a scalar) is `FAILED`, since it
cannot be the expected `{topNav, quickLaunch}` shape.

## Read-only guarantee

No writes to any tenant, no network access. It reads the export path you name
and writes analysis artifacts to the output directory you name.

## Usage

```bash
python -c "
from navigation_analysis import run
outcome = run(navigation_path='navigation.json', output_dir='out/')
print(outcome.status, outcome.detail)
"
```

## Collecting a fresh export

`collect-sharepoint-site-navigation.ps1` connects to a live on-prem
SharePoint 2016 site (REST + NTLM/Kerberos, no PnP/CSOM -- see
`.agent/rules/sharepoint-ps1-authentication-convention.md` for why on-prem
uses this auth mechanism instead of `Connect-PnPOnline`) and writes a
`navigation.json` in the exact `{topNav, quickLaunch}` shape
`navigation_analysis.py` consumes, each node shaped
`{title, url, children}`. It also writes a fuller `site-chrome.json`
(site title, logo URL, master page path, locale, breadcrumb ancestor chain)
for reference/reporting -- not consumed by `navigation_analysis.py`, which
reads `navigation.json` only. Read-only: calls only REST GETs, makes zero
writes to the tenant.

```bash
pwsh -File scripts/collect-sharepoint-site-navigation.ps1 -SiteUrl "https://sp2016.example.org/sites/Legacy" -OutputDir ./nav-export -UseDefaultCredentials
```

`assets/site-navigation-chrome-summary-template.md` is a Markdown template
for writing up the collected navigation/chrome data as a reviewer-facing
architecture summary (top nav table, quick launch, master page chrome) --
fill in its `{{...}}` placeholders from `site-chrome.json` and
`navigation-plan.json`.

## Scripts

- `scripts/collect-sharepoint-site-navigation.ps1` -- real, read-only on-prem REST collector
- `scripts/navigation_analysis.py` -- `run`, `analyse`, `generate_report`
- `scripts/discovery_inputs.py` -- `DiscoveryStatus`, `DiscoveryOutcome`, `load_json_input`, `require_output_dir`

## Provenance

Adapted from `sp-discovering-navigation` in the originating SharePoint
migration repository. See
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`.

