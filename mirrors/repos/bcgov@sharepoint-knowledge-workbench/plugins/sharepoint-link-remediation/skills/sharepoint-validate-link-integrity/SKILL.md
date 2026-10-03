---
name: sharepoint-validate-link-integrity
plugin: sharepoint-link-remediation
description: Verifies that links resolve after a migration or remediation pass, classifying each as RESOLVED, BROKEN, UNRESOLVABLE or SKIPPED with an honest overall outcome. Use last, to prove a migration or remediation actually worked. Read-only and resolver-injected; it ships no network transport, so an unreachable target is reported as unresolvable rather than guessed.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from link_integrity import validate_link_integrity, make_local_path_resolver; print(validate_link_integrity(inv, make_local_path_resolver('export/')).to_dict())\""
---

# Validate Link Integrity

Prove that rewritten or migrated links point at things that exist. Final stage of the extract, remediate, validate pipeline.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- No hidden network access. The resolver is injected; without one, links are `UNRESOLVABLE`, never assumed good. `UNRESOLVABLE` does not count as
  passing.
- An empty inventory reports `EMPTY`, never a pass: validating nothing is not validating successfully.
- `make_local_path_resolver(root)` checks server-relative links against an exported local tree. Live checking needs a caller-supplied resolver.
- Read-only. Run from this skill's root with `scripts/` on `sys.path`.

## Quick start

```python
import sys; sys.path.insert(0, "scripts")
from link_extraction import extract_links_from_paths
from link_integrity import validate_link_integrity, make_local_path_resolver
report = validate_link_integrity(extract_links_from_paths(["export/page.aspx"]), make_local_path_resolver("export/"))
print(report.outcome, [f.status for f in report.findings])
```

## Workflow

1. Build a `LinkInventory` with `sharepoint-extract-links`.
2. Choose the resolver (built-in local-path, or custom) and call `validate_link_integrity(inventory, resolver)`.
3. Report each `LinkFinding` status and the overall `outcome`.

## Verification

Statuses are `RESOLVED` (exists), `BROKEN` (confirmed absent), `UNRESOLVABLE` (could not be determined) and `SKIPPED` (out of scope, such as `mailto:`
and anchors). Treat any `BROKEN` or `UNRESOLVABLE` link as a finding, and the report outcome as `OBSERVED`, `EMPTY`, `PARTIAL` or `FAILED`.

## References

- [Integrity details](references/link-integrity-details.md): read for resolver injection, statuses, usage, and how this differs from publication
  validation.
- [Pipeline, outcomes and write safety](references/link-pipeline-and-write-safety.md): read for the shared outcome vocabulary.
