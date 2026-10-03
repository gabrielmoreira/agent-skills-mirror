---
name: sharepoint-analyze-permissions
plugin: sharepoint-discovery
description: Analyses an exported classic SharePoint permissions snapshot, deriving groups, evaluated objects and the subset with broken permission inheritance, to produce a group provisioning worksheet and a broken-inheritance exception report. Use when planning a classic-to-modern migration and you need to know which groups exist and which lists or libraries must be explicitly re-provisioned. Read-only; consumes an export you provide and never contacts a tenant.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from permissions_analysis import run; print(run(permissions_path='permissions.json', output_dir='out/').status)\""
---

# Analyze Permissions

Find which groups exist and which lists or libraries have broken permission inheritance that
must be re-provisioned rather than inherited.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Read-only. The analysis makes no tenant writes and no network access; it reads the export path
  you name and writes to the output directory you name.
- Never fabricate a placeholder group or object list to look successful. A missing export is
  `UNAVAILABLE` and creates no output directory. No groups or objects is `EMPTY`, never a pass. An
  input that is neither a JSON array nor object is `FAILED`.
- Accepts two export shapes (flat array, or structured object). The flat shape carries no
  inheritance flag, so do not claim inheritance state it cannot show.
- Run from this skill's root with `scripts/` on `sys.path`.

## Quick start

```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from permissions_analysis import run
o = run(permissions_path='permissions.json', output_dir='out/')
print(o.status, o.detail)"
```

## Workflow

1. Get a permissions export from `scripts/collect-sharepoint-permissions.ps1` or any source in
   one of the two accepted shapes; see
   [shapes and collection](references/permissions-collection-and-shapes.md).
2. Call `run(permissions_path=..., output_dir=...)`; `analyse()` handles both shapes.
3. Report the groups, evaluated objects, and the broken-inheritance exceptions.

## Verification

Check `outcome.status` is `OBSERVED` and the output directory holds the group provisioning
worksheet and exception report. Treat any other status as the honest outcome it is; see
[outcomes](references/discovery-outcomes.md).

## References

- [Shapes and collection](references/permissions-collection-and-shapes.md): read for the two
  export shapes, a fresh export, or the script list.
- [Outcomes](references/discovery-outcomes.md): read when interpreting a non-`OBSERVED` status.
