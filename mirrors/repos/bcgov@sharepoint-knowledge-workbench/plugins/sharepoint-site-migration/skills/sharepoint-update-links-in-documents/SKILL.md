---
name: sharepoint-update-links-in-documents
plugin: sharepoint-site-migration
description: Rewrites legacy URLs embedded INSIDE Office documents (docx, xlsx, pptx via stdlib zipfile, with no python-docx, openpyxl or python-pptx dependency) and PDFs (through an optional caller-injected handler) stored in a document library. Use when a migrated page links to a document whose own hyperlinks still point at the old site. Distinct from sharepoint-update-page-links, which only rewrites page/HTML body content. DRY-RUN BY DEFAULT; applying changes requires BOTH an injected executor AND a confirmation token from the plan.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from document_link_remediation import plan_document_link_remediation; print(plan_document_link_remediation(documents, ruleset).to_dict())\""
---

# Remediate Document Content Links

Rewrite hyperlinks inside Word, Excel and PowerPoint files (and, with a handler, PDFs) that still point at the old classic site.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Same three write gates as `sharepoint-update-page-links`: dry-run by default; an `executor(source, content: bytes)` must be injected (else
  `ExecutorRequired`); a real apply needs `confirm=plan.confirmation_token`. The PowerShell executor needs
  `-Execute -ConfirmToken REMEDIATE-SPO-DOCUMENT-LINKS` and is a live tenant write that the user runs.
- A PDF is `NOT_SUPPORTED` unless the caller injects `pdf_handler(content, ruleset) -> (bytes, applied_rules)`. Never text-substitute a binary
  PDF stream (it corrupts the file) and never present non-coverage as success.
- Office formats use the standard library's `zipfile`; add no third-party dependency. When installed, pass `-ConfigPath` to the executor.
- Run from this skill's root with `scripts/` on `sys.path`.

## Quick start

```python
import sys; sys.path.insert(0, "scripts")
from link_rules import load_ruleset
from document_link_remediation import plan_document_link_remediation
plan = plan_document_link_remediation(documents, load_ruleset("rules.json"))
print(plan.outcome, plan.change_count)
```

## Workflow

Use the Python bulk CSV exporter in `sharepoint-extract-links` to inventory external Office
relationship links from local copies before planning rewrites. Its supported extraction surfaces
are narrower than all rewritable XML parts; PDFs remain unsupported without a parser. Preserve
originals and re-extract after changes. See [bulk content workflow](references/bulk-content-link-workflow.md).

1. Plan with `plan_document_link_remediation(documents, ruleset)` and review the change count with the user.
2. Apply only after review: `apply_document_link_remediation(plan, executor=..., dry_run=False, confirm=plan.confirmation_token)`.
3. For the PowerShell route, write each changed document's rewritten bytes to disk and add `remediated_content_path` to the plan JSON first.

## Verification

Check the outcome: `OBSERVED`, `EMPTY`, `NOT_SUPPORTED` (a PDF without a handler), `PARTIAL` or `FAILED`. Re-extract the links afterwards to confirm.

## References

- [Document remediation details](references/document-link-remediation-details.md): read for the ZIP/XML approach, the PDF handler, usage and
  the PowerShell executor seam.
- [Pipeline, outcomes and write safety](references/link-pipeline-and-write-safety.md): read for the shared gates and outcome table.
