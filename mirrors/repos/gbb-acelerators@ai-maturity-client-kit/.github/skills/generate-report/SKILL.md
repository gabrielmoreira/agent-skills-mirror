---
name: generate-report
description: Renders v2 executive PDFs, or archived v1 PDFs, by invoking reports/scripts/build_payload_and_render.py. Use for "gerar relatorio", "generate report PDFs", "executive report", "PDF final", "generar informe", "informe ejecutivo en PDF".
---

# Skill: Generate reports

Always invoke the report dispatcher. Do not assemble payloads or PDFs by hand.

## Command

```bash
python3 reports/scripts/build_payload_and_render.py
```

`make pipeline` runs scores plus this renderer.

## Required inputs

- `responses.json`
- `output/scores.json`
- `output/gaps.json`
- `output/recommendations.json`

Run `python3 scripts/assessment_engine.py all` first if any are missing.

## v2 outputs

- `output/payload_v2.json`
- `output/v2_assessment_summary.pdf`
- `output/v2_roadmap_g1.pdf`: D1, D2, D9.
- `output/v2_roadmap_g2.pdf`: D3, D4, D5.
- `output/v2_roadmap_g3.pdf`: D6, D7, D8.
- `output/v2_implementation_guide.pdf`: governance, RACI, dimension owners, phased plan, change management, risks, metrics, first 90 days, and references.

## v2 report content to preserve

Surface coverage, bands, weighted priorities, S1 to S7 recommendations, low confidence, amplification risk, perception gap, respondent divergence, scope caveat, unverified L3/L4, persona summaries, backlog questions, Evidence cross-checks, and Developer Survey context when available.

## Comparison PDF

Use `make compare BEFORE=old.json AFTER=responses.json` when the user asks for round comparison. It writes `output/round-comparison.pdf` using the v2 styles.

## v1 behavior

v1 inputs still render the existing 5 PDF report set through the archived flow.

## Chat response

List generated files, framework detected, locale, and warnings. If rendering dependencies are missing, install only existing dependencies documented by the repo.
