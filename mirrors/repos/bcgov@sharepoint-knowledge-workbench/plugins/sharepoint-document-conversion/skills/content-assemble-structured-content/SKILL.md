---
name: content-assemble-structured-content
plugin: sharepoint-document-conversion
description: Assembles a validated structured content package from a human-confirmed conversion plan and its source document, with stable identities, source lineage, hashes, manifests and publication mappings. Use after the conversion plan has been confirmed. Does not extract source documents, make unconfirmed topic decisions, render output formats, or publish to SharePoint.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from structured_content_assembly import build_canonical_package; build_canonical_package(plan, source_dir, output_dir)\""
---

# Assemble Structured Content

Turn a confirmed `analysis-plan` v1 dict into a validated structured content package on disk.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Consume only a confirmed plan (`confirmation.status == "confirmed"`). Never construct or confirm a
  plan here; that belongs to the `sharepoint-document-conversion` plugin plus human confirmation.
- A plan that is unconfirmed, whose source fingerprint no longer matches, or that changed after
  confirmation raises `PlanVerificationError`. Do not work around it.
- A `FAIL` validation never promotes. The prior accepted package is left untouched and the failed
  staging directory is kept for diagnosis.
- Out of scope: extracting source documents, unconfirmed topic decisions, rendering output formats,
  publishing to SharePoint.
- `pandoc` (and LibreOffice `soffice` for legacy `.emf` media) must be on `PATH`. Run from this
  skill's root with `scripts/` on `sys.path`.

## Quick start

```python
import sys; sys.path.insert(0, "scripts")
from structured_content_assembly import build_canonical_package
result = build_canonical_package(analysis_plan, source_dir, output_dir)
# {"manifest": ..., "validation_report": ..., "promoted": bool, "package_dir": str}
```

## Workflow

1. Confirm you hold a confirmed plan and the directory with the source `.docx` it references.
2. Call `build_canonical_package(analysis_plan, source_dir, output_dir)`.
3. Report `promoted`, `package_dir` and the validation report. A `grouped` plan also yields a
   validated `publication-map`.

## Verification

Check `result["promoted"]` is true and the validation report is PASS. If it is false, report the
failures and the retained staging directory; do not present the package as accepted.

## References

- [Interface](references/assembly-interface.md): read for arguments, return value, failure
  behavior and external tools.
- [Canonical package contract](references/contracts/canonical-package.md) and
  [publication map contract](references/contracts/publication-map.md): read when checking the
  package or publication-map layout.
