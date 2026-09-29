---
name: sharepoint-remediate-links
plugin: sharepoint-link-remediation
description: Rewrites legacy SharePoint URLs to their modern targets using a declarative, parameterized rewrite ruleset. DRY-RUN BY DEFAULT -- applying changes requires BOTH an explicitly injected writer AND a confirmation token from the plan. Reports PARTIAL/FORBIDDEN/FAILED honestly and supports rollback.
allowed-tools: Bash, Read
examples:
  - "python -c \"from link_remediation import plan_remediation; print(plan_remediation(docs, ruleset).to_dict())\""
  - "python -c \"from link_rules import load_ruleset; print(load_ruleset('rules.json'))\""
---

# Remediate Links

## Trigger and Purpose

Use this skill to rewrite links after a SharePoint migration has moved
content -- classic `/Pages/` to `/SitePages/`, an old host to a new one,
and so on. It is the only WRITE-capable skill in this plugin, and its
safety gates are structural, not advisory.

Stage two of `extract-links` -> `remediate-links` -> `validate-link-integrity`.

## Write safety -- three independent gates

Per Phase 9 spec section 13, no autonomous production write is reachable:

1. **Dry-run is the default.** `apply_remediation(plan)` with no arguments
   changes nothing and returns `would_change`.
2. **A writer must be injected.** This module ships no tenant transport.
   Without a `writer` callable, it raises `WriterRequired` rather than
   silently no-op'ing or faking success.
3. **A confirmation token is required.** `dry_run=False` additionally
   requires `confirm=plan.confirmation_token`, derived from the plan's own
   content. A stale or absent token raises `ConfirmationRequired`, so a plan
   cannot be applied after the underlying documents have changed.

`rollback_remediation` restores prior content under the same gates.

## Honest outcomes

| Outcome | Meaning |
|---|---|
| `OBSERVED` | All intended writes succeeded |
| `EMPTY` | Nothing matched the ruleset; nothing to do |
| `PARTIAL` | Some writes succeeded, some failed; both lists populated |
| `FORBIDDEN` | The writer raised `PermissionError` |
| `FAILED` | Every write failed |

A partly-failed run is never reported as success, and a permission denial is
never flattened into a generic failure.

## Rulesets are data, not code

`load_ruleset(path)` reads a declarative JSON ruleset of `match` /
`replacement` / `description` entries. **No host, tenant, or project URL is
built in** -- every rewrite target is supplied by you. Malformed rulesets
raise `RulesetError` rather than silently matching nothing.

## Usage

```bash
# 1. Plan (always safe)
python -c "
from link_rules import load_ruleset
from link_remediation import plan_remediation
plan = plan_remediation(documents, load_ruleset('rules.json'))
print(plan.outcome, plan.to_dict()['would_change'])
"
```

Apply only after reviewing the plan, with a real writer and the plan's own
confirmation token.

## Real executor

`scripts/spo-remediate-page-links.ps1` implements the writer role directly:
it reads a `RemediationPlan.to_dict()`-shaped JSON file, resolves each
changed document's `source` (a server-relative path) to a list item in
`-TargetLibrary` via `Get-PnPListItem`, then overwrites `-TargetField`
(default `CanvasContent1`, the modern-page body field) via
`Set-PnPListItem`. Dry run by default; real writes require
`-Execute -ConfirmToken REMEDIATE-SPO-LINKS`.

```bash
pwsh -File scripts/spo-remediate-page-links.ps1 -PlanPath plan.json -TargetLibrary "Site Pages" -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Execute -ConfirmToken REMEDIATE-SPO-LINKS
```

The plan JSON must carry each changed document's already-computed
`remediated_content` text (Python's `RemediationPlan.to_dict()` reports only
`source`/`changed`/`changes`, not the new content -- see the script's
comment-based help for the exact augmentation). It is not wired in as
`link_remediation.py`'s injected `writer` automatically -- Python cannot
call a PowerShell script as an in-process callback, so the two paths are
used independently rather than composed.

## Scripts

- `scripts/link_remediation.py` -- `plan_remediation`, `apply_remediation`, `rollback_remediation`, safety errors
- `scripts/link_rules.py` -- `load_ruleset`, `RewriteRule`, `RewriteRuleset`
- `scripts/link_outcomes.py` -- shared `Outcome` vocabulary
- `scripts/spo-remediate-page-links.ps1` -- real PnP executor (see "Real executor" above)

## Provenance

Adapted from `sp-remediating-links` in the originating SharePoint migration
repository (see `docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`).
The source's hardcoded tenant URLs were replaced by the parameterized ruleset
model; no project-specific literal ships as a live default.

