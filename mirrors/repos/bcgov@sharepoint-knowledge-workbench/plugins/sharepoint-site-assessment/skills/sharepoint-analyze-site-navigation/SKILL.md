---
name: sharepoint-analyze-site-navigation
plugin: sharepoint-site-assessment
description: Analyses an exported classic SharePoint site navigation tree (top nav and quick launch), flattening it with per-node depth and child counts and computing max-depth statistics, to produce a navigation architecture summary. Use when planning a classic-to-modern migration and sizing navigation before mapping it to hub or global navigation. Read-only; consumes an export you provide and never contacts a tenant.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from navigation_analysis import run; print(run(navigation_path='navigation.json', output_dir='out/').status)\""
---

# Analyze Site Navigation

Answer: how many top-level nodes exist, how deep does each tree nest, and what does the full
node list look like with depth and child counts.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Read-only. No tenant writes, no network access: it reads the export path you name and writes
  analysis artifacts to the output directory you name.
- A missing input file is `UNAVAILABLE` and creates no output directory. An export with no
  navigation nodes is `EMPTY`, never a pass. An input that isn't a JSON object is `FAILED`
  (the expected shape is `{topNav, quickLaunch}`).
- Run from this skill's root with `scripts/` on `sys.path`. Python is standard library only.

## Quick start

```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from navigation_analysis import run
o = run(navigation_path='navigation.json', output_dir='out/')
print(o.status, o.detail)"
```

## Workflow

1. Get a `navigation.json` shaped `{topNav, quickLaunch}`, each node `{title, url, children}`,
   or collect one; see [collection](references/site-navigation-collection.md).
2. Call `run(navigation_path=..., output_dir=...)`.
3. Report node counts, max depth per tree and the flattened node list.
4. Optionally write the reviewer-facing summary from
   `assets/site-navigation-chrome-summary-template.md`.

## Verification

Check `outcome.status` is `OBSERVED` and the output directory holds the report. Treat any other
status as the honest outcome it is; see [outcomes](references/discovery-outcomes.md).

## References

- [Collection](references/site-navigation-collection.md): read when you need a fresh export, the
  summary template, or the script list.
- [Outcomes](references/discovery-outcomes.md): read when interpreting a non-`OBSERVED` status.
