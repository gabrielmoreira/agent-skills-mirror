---
name: sharepoint-remediate-field-image-references
plugin: sharepoint-link-remediation
description: Inventory-verified remediation of an embedded img reference inside a rich-text list field. Classifies each item against a real document-library inventory (matched, missing, broken-placeholder-no-src, no-image) and proposes a rewrite ONLY for confirmed-matched items, never a blind regex guess. Use when a rich-text field's image points at a library the file moved out of. Distinct from sharepoint-remediate-links (page-body content) and sharepoint-remediate-document-content-links (Office/PDF files). DRY-RUN BY DEFAULT; applying changes requires BOTH an injected executor AND a confirmation token from the plan.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from field_image_remediation import plan_field_image_remediation; print(plan_field_image_remediation(items, inventory=inventory, ruleset=ruleset).to_dict())\""
---

# Remediate Field Image References

Fix a rich-text field's embedded `img` reference to a file that moved libraries during migration, without hiding files that never migrated.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Never rewrite blindly. Propose a fix only for `matched` items (filename found in the inventory). `missing`, `img_no_src` and `no_img_tag` get no
  fix, but every item is classified and reported; none is silently dropped. A `missing` file is a real data-loss signal.
- Same three write gates: dry-run by default; an `executor(source_id, new_field_value)` must be injected (else `ExecutorRequired`); a real apply
  needs `confirm=plan.confirmation_token`. The PowerShell executor needs `-Execute -ConfirmToken REMEDIATE-SPO-FIELD-IMAGES` and is a live
  tenant write that the user runs. When installed, pass `-ConfigPath` to it.
- Reading the field values and collecting the library inventory are caller-supplied, live-tenant work out of scope here.
- Run from this skill's root with `scripts/` on `sys.path`.

## Quick start

```python
import sys; sys.path.insert(0, "scripts")
from link_rules import load_ruleset
from field_image_remediation import plan_field_image_remediation, generate_gap_report
# items: {source_id: field_value_html}; inventory: {filename.lower(): relative_url}
plan = plan_field_image_remediation(items, inventory=inventory, ruleset=load_ruleset("rules.json"))
print(generate_gap_report(plan))   # reviewer-facing report, before any write
```

## Workflow

1. Get the field values and a destination inventory from the caller.
2. Plan, then show `generate_gap_report(plan)` to the user; it names every `missing` and `matched` item individually.
3. After review, apply: `apply_field_image_remediation(plan, executor=..., dry_run=False, confirm=plan.confirmation_token)`.

## Verification

Confirm the gap report counts match the classifications, then re-run the plan after applying; matched items should no longer propose a change.

## References

- [Field image details](references/field-image-remediation-details.md): read for the rationale, the classification table, the five-step pattern
  and the PowerShell executor.
- [Pipeline, outcomes and write safety](references/link-pipeline-and-write-safety.md): read for the shared gates and outcome table.
