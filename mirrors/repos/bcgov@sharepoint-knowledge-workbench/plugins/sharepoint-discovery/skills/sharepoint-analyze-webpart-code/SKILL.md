---
name: sharepoint-analyze-webpart-code
plugin: sharepoint-discovery
description: Groups classic SharePoint web parts by functional behaviour (inline script, external helper scripts, text-only, empty, or unretrievable) so near-duplicate instances collapse into a reviewable set. Use when a modernization review should cover each behaviour once instead of each instance. Classification knowledge is caller-supplied via a KnowledgeBase; read-only.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from webpart_code_analysis import run; print(run(extract_path='webparts.json', output_dir='out/').status)\""
---

# Analyze Web Part Code

Collapse an exported web-part content dump into distinct functional groups: a groups JSON, a
Markdown analysis report and a per-instance review CSV.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Read-only. No tenant contact and no writes outside the output directory you name. A missing input
  is `UNAVAILABLE` and creates no output directory.
- An unretrievable web part is `ScriptEditorMissing`: an unknown, not an empty one. Any run
  containing one reports `PARTIAL` with the count, never `OBSERVED`.
- Classification knowledge is caller-supplied through `KnowledgeBase` and `InlineLogicRule`.
  `DEFAULT_KNOWLEDGE_BASE` is deliberately generic; build in no site-specific rules.
- The per-group `businessIntent`, `enforcementLevel` and `spfxAssessment` fields are a
  deterministic starting point, not a disposition.
- Run from this skill's root with `scripts/` on `sys.path`.

## Quick start

```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from webpart_code_analysis import run
o = run(extract_path='webpart-content.json', output_dir='out/')
print(o.status, o.detail)"
```

## Workflow

1. Get a `webpart-content.json` shaped `[{PageUrl, WebPartId, WebPartTitle, Content}]`, or collect
   one; see [categories, collection and Stage 2](references/webpart-code-categories-collection-stage2.md).
2. Supply a `KnowledgeBase` for the site's helper scripts and heuristics, or use the default.
3. Call `run(extract_path=..., output_dir=...)`.
4. For the full disposition, route the grouped output to
   `sharepoint-webpart-modernization-analysis-agent` (in `sharepoint-page-modernization`).

## Verification

Check `outcome.status` and the three output artifacts. `PARTIAL` means some web parts were
unretrievable; report the count. See [outcomes](references/discovery-outcomes.md).

## References

- [Categories, collection and Stage 2](references/webpart-code-categories-collection-stage2.md):
  read for the category table, a fresh export, or the Stage 2 handoff.
- [Outcomes](references/discovery-outcomes.md): read when interpreting a non-`OBSERVED` status.
- [Web part analysis runbook](references/webpart-analysis-runbook.md): the review procedure.
- Assets: `assets/webpart-migration-rules.json` and
  `assets/ALL-UNIQUE-WEBPART-CODE-FOR-REVIEW-template.md`.
