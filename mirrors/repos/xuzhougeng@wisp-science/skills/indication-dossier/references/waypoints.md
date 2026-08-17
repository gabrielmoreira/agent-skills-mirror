# Waypoint file contract

Everything under `<workdir>/waypoints/` is resumable state: each phase writes
exactly one of these files, and a later invocation reconstructs progress from
which files exist. Field names below are the contract — keep them stable.

## Shared shapes

Phase waypoints (`epidemiology.json`, `biology_soc.json`,
`regulatory_trials.json`) all follow one pattern:

```json
{
  "subsections": {
    "<subsection>": {
      "content": "distilled findings, prose",
      "sources": ["..."],
      "coverage": "covered | partial | missing"
    }
  },
  "gaps": ["gaps that could not be filled, stated plainly"]
}
```

Subsection keys per file:

| File | Subsection keys |
|---|---|
| `epidemiology.json` | `diagnostic_criteria`, `prevalence_incidence`, `demographics`, `natural_history` |
| `biology_soc.json` | `pathophysiology`, `biomarkers`, `approved_therapies`, `treatment_guidelines`, `unmet_need` |
| `regulatory_trials.json` | `accepted_endpoints`, `fda_guidance`, `trial_parameters`, `landmark_trials`, `notable_failures` |

`regulatory_trials.json` additionally carries the CT.gov scan:

```json
"trial_landscape": {
  "total_trials": 0,
  "by_phase": {"Phase 1": 0, "Phase 2": 0, "Phase 3": 0, "Phase 4": 0},
  "by_status": {"Recruiting": 0, "Completed": 0}
}
```

## meta.json (Phase 1)

```json
{
  "indication_name": "...",
  "parent_indication": "... or null",
  "definition": "...",
  "icd_codes": ["K70"],
  "aliases": ["..."],
  "is_standard_diagnosis": true,
  "notes": "caveats: not ICD-coded, biological state, iatrogenic, etc."
}
```

## sources_evaluated.json (initialized Phase 1, appended every phase)

```json
{
  "sources": [
    {"url": "...", "source_type": "...", "date_accessed": "...", "result": "success | failed | partial"}
  ]
}
```

## progress.json (loop control)

```json
{"complete": false, "output_file": null, "current_phase": "meta_initialization",
 "iteration_notes": "what this iteration accomplished"}
```

Flipping `complete: true` (with `"output_file": "indication_dossier_report.md"`)
is the very last write of the run — after the report exists.

## research_output.json (Phase 5)

Consolidates the run for downstream consumers:

```json
{
  "indication_name": "...",
  "parent_indication": "...",
  "meta": {},
  "epidemiology": {},
  "biology_soc": {},
  "regulatory_trials": {},
  "sources_evaluated": [],
  "coverage_summary": {
    "epidemiology":      {"covered": [], "partial": [], "missing": []},
    "biology_soc":       {"covered": [], "partial": [], "missing": []},
    "regulatory_trials": {"covered": [], "partial": [], "missing": []}
  }
}
```

`indication_dossier_report.md` (the deliverable) is also written to
`waypoints/`; its outline is in `phases.md`.
