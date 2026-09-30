---
mode: agent
---

# Pipeline completo: AI Maturity Assessment

Run the complete assessment pipeline. Framework v2 is the default. v1 remains supported when `responses.json` has no `metadata.framework_version` or has a `1.x` version.

## Rules

- Do not compute scores, gaps, recommendations, workbooks, evidence cross-checks, or reports by hand.
- Do not edit framework files, generated question banks, templates, scripts, or `Makefile`.
- Use the deterministic dispatchers. They select v2 or v1 from `responses.json::metadata.framework_version`.
- Keep the agent lean: workflow here, domain knowledge in skills.
- Reply in the user's language (English, Portuguese (Brazil) or Spanish). Render reports in the client's language: check `metadata.language` in `responses.json` (`"en"`, `"pt-BR"` or `"es"`) before step 5.

## Steps

1. Confirm required input:
   - `responses.json` exists, or import from Microsoft Forms with `python3 scripts/import_forms_excel.py <xlsx>`.
   - If respondents used the offline form, merge exports first with `python3 scripts/merge_offline_responses.py <dir>`.
2. Run the deterministic engine:

   ```bash
   python3 scripts/assessment_engine.py all
   ```

3. Populate the auditable workbook:

   ```bash
   python3 scripts/fill_workbook.py
   ```

4. Optional evidence cross-checks:

   ```bash
   make scan-repos REPOS=~/src
   make telemetry METRICS=copilot-usage.json SEATS=200
   make dora DORA=dora-metrics.csv SERVICES=40
   ```

5. Render reports:

   ```bash
   python3 reports/scripts/build_payload_and_render.py
   ```

6. Optional round comparison:

   ```bash
   python3 scripts/compare_rounds.py old.json responses.json --pdf
   ```

7. Report outputs.

## v2 expected outputs

- `output/scores.json`
- `output/gaps.json`
- `output/recommendations.json`
- `output/scoring-v2-<date>.xlsx`
- `output/payload_v2.json`
- `output/v2_assessment_summary.pdf`
- `output/v2_roadmap_g1.pdf`
- `output/v2_roadmap_g2.pdf`
- `output/v2_roadmap_g3.pdf`
- `output/v2_implementation_guide.pdf`
- `output/round-comparison.pdf` when comparison is requested.

## v1 expected outputs

v1 inputs still use the archived 158 question, 3 pillar flow and produce the existing v1 outputs, including the 5 PDF report set.

## Final chat template

```text
Pipeline complete.
Framework: v2.0.2 or v1 archived flow
Coverage: <status> (<answered>/<applicable>)
JSON outputs: scores.json, gaps.json, recommendations.json
Workbook: <file>
Reports: <files>
Evidence: <repo-scan/telemetry/dora-metrics status>
Notes: <flags or blockers from script output>
```
