---
name: sharepoint-update-page-links
plugin: sharepoint-site-migration
description: Rewrites legacy SharePoint URLs in page/HTML body content to their modern targets using a declarative, parameterized rewrite ruleset. Use after a migration has moved content (for example classic /Pages/ to /SitePages/, or an old host to a new one). DRY-RUN BY DEFAULT; applying changes requires BOTH an explicitly injected writer AND a confirmation token from the plan. Reports PARTIAL, FORBIDDEN and FAILED honestly and supports rollback.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from link_remediation import plan_remediation; print(plan_remediation(docs, ruleset).to_dict())\""
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from link_rules import load_ruleset; print(load_ruleset('rules.json'))\""
---

# Remediate Links

Rewrite links in page body content after a migration. Stage two of the extract, remediate, validate pipeline.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Three independent write gates, structural not advisory: dry-run is the default; a `writer` callable must be injected (else
  `WriterRequired`); a real apply needs `confirm=plan.confirmation_token` (else `ConfirmationRequired`, so a stale plan cannot be applied).
- The PowerShell executor `scripts/spo-remediate-page-links.ps1` writes nothing without `-Execute -ConfirmToken REMEDIATE-SPO-LINKS`. A real
  run is a live tenant write that the user runs. When installed, pass `-ConfigPath` (or `-SiteUrl`, `-ClientId`, `-TenantId`).
- Rulesets are data: no host, tenant or project URL is built in. A malformed ruleset raises `RulesetError`.
- Never report a partly-failed run as success, and never flatten a permission denial (`FORBIDDEN`) into a generic failure.
- Run from this skill's root with `scripts/` on `sys.path`.

## Quick start

```python
import sys; sys.path.insert(0, "scripts")
from link_rules import load_ruleset
from link_remediation import plan_remediation
plan = plan_remediation(documents, load_ruleset("rules.json"))   # always safe
print(plan.outcome, plan.to_dict()["would_change"])
```

## Workflow

For site-wide static or modern page remediation, first run the Python bulk CSV exporter in
`sharepoint-extract-links`. Preserve source URLs and review destination mappings before rewriting.
For modern pages, collect stored page fields and use the existing field executor; CSV extraction
does not write changes. Re-extract after applying. See [bulk content workflow](references/bulk-content-link-workflow.md).

1. Load the ruleset and plan: `plan_remediation(documents, ruleset)`. Review `would_change` with the user.
2. Apply only after review, with a real writer and the plan's own token: `apply_remediation(plan, writer=..., dry_run=False,
   confirm=plan.confirmation_token)`; or use the PowerShell executor with an augmented plan JSON.
3. Undo with `rollback_remediation` under the same gates if needed.

## Verification

Check the outcome (`OBSERVED`, `EMPTY`, `PARTIAL`, `FORBIDDEN`, `FAILED`), then run `sharepoint-validate-link-integrity` to confirm the rewritten
links resolve.

## References

- [Remediation details](references/remediate-links-details.md): read for rulesets, apply and rollback, and the real executor.
- [Pipeline, outcomes and write safety](references/link-pipeline-and-write-safety.md): read for the gates, the outcome table and the plan
  JSON augmentation the executor needs.
