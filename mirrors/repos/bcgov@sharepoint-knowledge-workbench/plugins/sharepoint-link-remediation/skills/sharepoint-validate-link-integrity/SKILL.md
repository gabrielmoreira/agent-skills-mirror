---
name: sharepoint-validate-link-integrity
plugin: sharepoint-link-remediation
description: Verifies that links resolve after a migration or remediation pass, classifying each as RESOLVED / BROKEN / UNRESOLVABLE / SKIPPED and reporting an honest overall outcome. Read-only, resolver-injected -- ships no network transport, so an unreachable target is reported as unresolvable rather than guessed.
allowed-tools: Bash, Read
examples:
  - "python -c \"from link_integrity import validate_link_integrity, make_local_path_resolver; print(validate_link_integrity(inv, make_local_path_resolver('export/')).to_dict())\""
---

# Validate Link Integrity

## Trigger and Purpose

Use this skill to prove a migration or a `remediate-links` run actually
worked -- that the rewritten links point at things that exist. Final stage
of `extract-links` -> `remediate-links` -> `validate-link-integrity`.

`validate_link_integrity(inventory, resolver)` takes a `LinkInventory` from
`extract-links` and a resolver, returning an `IntegrityReport` of
`LinkFinding` records.

## Resolver injection -- no hidden network access

This module ships **no** HTTP or tenant transport. You inject the resolver,
which makes the check's trust boundary explicit:

- `make_local_path_resolver(root)` -- built in; validates server-relative
  links against an exported local tree. No network access at all.
- A custom resolver -- supply your own callable for live checking.

Without a resolver, links are reported `UNRESOLVABLE`, never assumed good.
This is the deliberate distinction between "verified present" and "not
checked" that makes the report trustworthy.

## Statuses and outcomes

| Status | Meaning |
|---|---|
| `RESOLVED` | Target confirmed to exist |
| `BROKEN` | Target confirmed absent |
| `UNRESOLVABLE` | Could not be determined -- NOT counted as passing |
| `SKIPPED` | Out of scope for the resolver (e.g. `mailto:`, anchors) |

Report-level `outcome` is `OBSERVED`, `EMPTY`, `PARTIAL`, or `FAILED`.
**An empty inventory reports `EMPTY`, never a pass** -- validating nothing is
not the same as validating successfully (Phase 9 spec section 13).

## Usage

```bash
python -c "
from link_extraction import extract_links_from_paths
from link_integrity import validate_link_integrity, make_local_path_resolver
report = validate_link_integrity(
    extract_links_from_paths(['export/page.aspx']),
    make_local_path_resolver('export/'),
)
print(report.outcome, [f.status for f in report.findings])
"
```

## Scripts

- `scripts/link_integrity.py` -- `validate_link_integrity`, `make_local_path_resolver`, `LinkStatus`, `LinkFinding`, `IntegrityReport`
- `scripts/link_extraction.py` -- produces the input inventory
- `scripts/link_outcomes.py` -- shared `Outcome` vocabulary

## Relationship to `sharepoint-content-publication`

That plugin's `reconcile-sharepoint-publication` /
`validate-sharepoint-publication` skills reconcile a *publication map*
against a target library -- a different question from whether individual
hyperlinks inside content resolve. These are complementary, not duplicates.

## Provenance

Adapted from `sp-validating-link-integrity` in the originating SharePoint
migration repository (see
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`).

