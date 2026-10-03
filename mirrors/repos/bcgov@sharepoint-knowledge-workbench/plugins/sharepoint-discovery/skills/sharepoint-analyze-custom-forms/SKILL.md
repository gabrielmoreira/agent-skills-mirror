---
name: sharepoint-analyze-custom-forms
plugin: sharepoint-discovery
description: Analyses an exported classic SharePoint custom list-form inventory, classifying each form as out-of-box, script-based, or InfoPath/custom-layout, and attaches a caller-supplied modernization strategy per classification. Use when planning a classic-to-modern migration and deciding which list forms carry forward as-is. Read-only; consumes an export you provide and never contacts a tenant.
allowed-tools: Bash, Read
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from forms_analysis import run; print(run(forms_path='forms.json', rules_path='assets/form-classification-rules.json', output_dir='out/').status)\""
---

# Analyze Custom Forms

Decide which classic list forms are safe to carry forward and which need replacing: out-of-box,
inline-script, or InfoPath/custom-layout, each with a recommended modernization strategy.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Read-only. No tenant writes, no network access: it reads the export path you name and writes
  analysis artifacts to the output directory you name.
- Rules are data, not code. Strategy text per classification comes entirely from the
  caller-supplied rules JSON; `assets/form-classification-rules.json` is a neutral default.
  No site-specific migration judgement is built in.
- A missing export or rules file is `UNAVAILABLE` and creates no output directory. An empty
  export is `EMPTY`, never a pass. A non-array input is `FAILED`.
- Run from this skill's root with `scripts/` on `sys.path`. Python is standard library only.

## Quick start

```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from forms_analysis import run
o = run(forms_path='forms.json', rules_path='assets/form-classification-rules.json', output_dir='out/')
print(o.status, o.detail)"
```

## Workflow

1. Get a forms export shaped `[{listName, isCustomized, hasScript, formType}]`, or collect a
   fresh one; see [collection and scripts](references/custom-forms-collection-and-scripts.md).
2. Choose the rules file (default or caller-supplied) and the output directory.
3. Call `run(...)`. `load_rules` reads the rules; `analyse` classifies; `generate_report` writes.
4. Report each form's classification and its recommended strategy.

## Verification

Check `outcome.status` is `OBSERVED` and the output directory holds the report. `EMPTY`,
`PARTIAL`, `UNAVAILABLE`, `FORBIDDEN` and `FAILED` are honest outcomes; report them as such.

## References

- [Collection and scripts](references/custom-forms-collection-and-scripts.md): read when you need
  a fresh export, the outcome status definitions, or the script list.
