---
name: sharepoint-generate-sharepoint-wave-scripts
plugin: sharepoint-migration-planning
status: implemented
description: >
  Reads dependency-matrix.json (from the dependency-graph analysis) and synthesizes one wave-script skeleton
  per computed wave, plus a single human wave guide, using real object names, types and dependsOn from the
  matrix only. Use as stage 3b after the matrix is computed. Never fabricates field-level schema (the matrix
  does not carry it) and never emits a single unattended run-everything script.
allowed-tools: Bash, Read, Write
examples:
  - "python3 -c \"import sys; sys.path.insert(0, 'scripts'); from wave_script_generation import generate_wave_scripts; r = generate_wave_scripts(matrix); print(r.outcome, len(r.scripts))\""
---

# Generate SharePoint Wave Scripts

Stage 3b. A thin, pure, deterministic templating function (not an AI-model call), so its output is exactly test-verifiable.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Refuse a matrix whose `outcome` is `FAILED`: report `Outcome.FAILED` with the issue; generate nothing.
- Never emit one script that deploys every wave unattended. The guide presents each wave as its own gated test, deploy, retest step.
- Never fabricate field-level schema. Each script's `build_schema()` body is an honest `NotImplementedError` TODO because the matrix carries only `name`, `objectType` and `dependsOn`.
- Never open a new tenant-write path. Each generated script's `main()` needs an injected executor and confirmation token. This skill never executes a generated script.
- Treat the templates in `assets/` as style references only; every real value in the output comes from the matrix.
- Run from this skill's root with `scripts/` on `sys.path`.

## Quick start

```python
import sys; sys.path.insert(0, "scripts")
from wave_script_generation import generate_wave_scripts
result = generate_wave_scripts(dependency_matrix_dict)   # result.scripts (one per wave) and result.guide
```

## Workflow

1. Get a `dependency-matrix.json` dict from `sharepoint-analyze-sharepoint-dependency-graph` with a non-`FAILED` outcome.
2. Call `generate_wave_scripts`.
3. Report one `GeneratedWaveScript` per wave (wave number, object names, filename) and the wave guide.
4. Executors for the writes come from `sharepoint-provisioning` (site columns, content types, lists) and `spo-provision-calendar.ps1` (this plugin); see the details reference.

## Verification

`outcome` is `OBSERVED` (or `EMPTY` for an empty matrix), every wave has a script, and every real object name from the matrix appears in its script's comment block. The guide covers every wave as a discrete step.

## References

- [Generation details](references/wave-script-generation-details.md): read for the full interface, what the skill never does, and the executors table (which plugin owns each script).
- [Test-driven wave deployment](references/test-driven-wave-deployment.md): read for why each wave is a gated step.
- Templates: [wave script](assets/wave-script-template.example.py) and [wave guide](assets/wave-guide-template.md), for shape only.
