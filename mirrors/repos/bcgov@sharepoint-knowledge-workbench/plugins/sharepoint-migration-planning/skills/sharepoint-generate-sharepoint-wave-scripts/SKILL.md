---
name: sharepoint-generate-sharepoint-wave-scripts
plugin: sharepoint-migration-planning
status: implemented
description: >
  Reads dependency-matrix.json (from analyze-sharepoint-dependency-graph)
  and synthesizes one wave-script skeleton per computed wave, plus a single
  human wave guide -- real object names/types/dependsOn from the matrix
  only, never fabricated field-level schema (the matrix does not carry
  it) and never a single unattended run-everything script.
allowed-tools: Bash, Read, Write
---

# Generate SharePoint Wave Scripts

Stage 3b. Templating, not full schema synthesis: turning a dependency graph
into deployment scripts and a runbook is a synthesis task with more than one
reasonable shape, but this implementation is deliberately a thin, pure,
deterministic templating function (`generate_wave_scripts`) rather than an
AI-model call, so its output is exactly test-verifiable (real names present,
zero project-specific leakage, honest refusal on a `Failed` matrix).

## Public interface

```python
from wave_script_generation import generate_wave_scripts

result = generate_wave_scripts(dependency_matrix_dict)
# result.outcome: Outcome.OBSERVED | Outcome.EMPTY | Outcome.FAILED
# result.scripts: one GeneratedWaveScript per wave (wave_number, object_names,
#                  source, filename) in matrix wave order
# result.guide: a single Markdown wave guide covering every wave as a
#               discrete test -> deploy -> retest step
```

Each generated script's `ProvisioningSchema`/`build_schema()` body is an
honest `NotImplementedError` TODO: the matrix carries only
`name`/`objectType`/`dependsOn`, not field-level schema, so full schema
synthesis is genuinely not mechanically derivable from the matrix alone and
is never fabricated to fill the gap. Every generated script's comment block
names the wave's real objects (name, objectType, dependsOn) taken directly
from the matrix.

## What this skill never does

- Never generates a script from a matrix whose `outcome` is `Outcome.FAILED`
  (a blocked/invalid dependency graph) -- `generate_wave_scripts` refuses and
  reports `Outcome.FAILED` with an explanatory issue instead.
- Never emits a single script that deploys every wave unattended -- the wave
  guide presents each wave as its own gated step, per
  `../../rules/test-driven-wave-deployment.md`.
- Never opens a new tenant-write path -- each generated script's `main()`
  requires an explicitly injected executor and confirmation token, matching
  `sharepoint-provisioning`'s existing three-gate write safety exactly. This
  skill itself never executes a generated script.
- Never copies content from `../../assets/wave-script-template.example.py` or
  `../../assets/wave-guide-template.md` verbatim -- those are style/shape
  references only; every real value in generated output comes from the
  matrix.

## Real executors now available (2026-08-11)

Each generated wave script's `main()` still requires an injected executor
and confirmation token (see "What this skill never does" above) -- but that
executor no longer has to be hand-written or left as a TODO. Four real,
gated `.ps1` scripts now exist in `../../scripts/` and can be invoked from a
generated wave script's `main()` (or run standalone against a hand-built
plan JSON) to apply exactly the write items `sharepoint-provisioning`'s
planning modules already compute:

| Script | Consumes a plan matching | Confirm token |
|---|---|---|
| `spo-provision-site-columns.ps1` | `field_provisioning.py`'s `FieldAction` list | `PROVISION-SPO-SITE-COLUMNS` |
| `spo-provision-content-types.ps1` | `content_type_provisioning.py`'s `ContentTypeAction` list | `PROVISION-SPO-CONTENT-TYPES` |
| `spo-provision-list.ps1` | `list_provisioning.py`'s `ProvisioningPlan` | `PROVISION-SPO-LIST` |
| `spo-provision-calendar.ps1` | `calendar_provisioning.py`'s `CalendarProvisioningPlan` | `PROVISION-SPO-CALENDAR` |

All four are dry-run by default, require `-Execute` plus their exact
`-ConfirmToken`, and reuse the canonical `Get-WorkbenchConnectionConfig.ps1`
(symlinked into this plugin's `scripts/` root from `workbench-setup`). Each
script's own comment-based help documents its plan JSON shape and any
augmentation the plan needs beyond what the Python module's `to_dict()`
serializes (see each script's `.DESCRIPTION` "Design seam" notes). This
skill's own `generate_wave_scripts` templating logic has not been changed to
reference them automatically -- that remains a real, undone follow-up if a
generated wave script should call these scripts directly rather than
leaving a `build_schema()` TODO.

## Scripts

- `scripts/wave_script_generation.py` -- `generate_wave_scripts`,
  `GeneratedWaveScript`, `WaveGenerationResult`
- `scripts/provisioning_outcomes.py` -- reused via a managed file symlink (see `symlinks.json`)
- `../../scripts/spo-provision-*.ps1` -- the four real executors described
  above (plugin-root, not skill-local; see this plugin's `README.md`)

## Provenance

New design work, generalizing the *shape* of hand-written wave scripts observed
in a separate SharePoint migration repository (e.g. `wave1-zero-deps.ps1`) --
those were written by hand, one at a time, by a person; this automates that
authoring step, it does not port their content.

