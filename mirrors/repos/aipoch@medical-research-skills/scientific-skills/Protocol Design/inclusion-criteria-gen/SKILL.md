---
name: inclusion-criteria-gen
description: Generate and optimize clinical trial subject inclusion/exclusion criteria to balance scientific rigor with recruitment feasibility.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Inclusion Criteria Generator

Generate and optimize clinical trial subject inclusion/exclusion criteria to balance scientific rigor with recruitment feasibility.

## Quick Check

Use this command to verify that the packaged script entry point can be parsed before deeper execution.

```bash
python -m py_compile scripts/main.py
```

## Audit-Ready Commands

Use these concrete commands for validation. They are intentionally self-contained and avoid placeholder paths.

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
python scripts/main.py generate --help
```

## When to Use

- Use this skill when the task is to Generate and optimize clinical trial subject inclusion/exclusion criteria to balance scientific rigor with recruitment feasibility.
- Use this skill for protocol design tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Use Cases

- **Protocol Design**: Create initial eligibility criteria for new clinical trials
- **Criteria Optimization**: Refine existing criteria to improve enrollment without compromising safety/efficacy
- **Competitive Analysis**: Analyze eligibility patterns across similar trials
- **Recruitment Strategy**: Identify and mitigate barriers to enrollment
- **Feasibility Assessment**: Evaluate if proposed criteria are realistic for target population

## Usage

### CLI Usage

```text
# Generate criteria from study design
python scripts/main.py generate \
  --indication "Type 2 Diabetes" \
  --phase "Phase 2" \
  --population "adults" \
  --duration "24 weeks" \
  --output criteria.json

# Optimize existing criteria
python scripts/main.py optimize \
  --input current_criteria.json \
  --enrollment-target 200 \
  --current-enrollment 120 \
  --output optimized_criteria.json

# Analyze criteria complexity
python scripts/main.py analyze \
  --input criteria.json \
  --output analysis_report.json

# Compare with competitor trials
python scripts/main.py benchmark \
  --input criteria.json \
  --condition "Type 2 Diabetes" \
  --output benchmark_report.json
```

### Python API

```python
from scripts.main import CriteriaGenerator, CriteriaOptimizer

# Generate new criteria
generator = CriteriaGenerator()
criteria = generator.generate(
    indication="Type 2 Diabetes",
    phase="Phase 2",
    population="adults",
    study_duration="24 weeks",
    endpoints=["HbA1c reduction", "weight change"]
)

# Optimize existing criteria
optimizer = CriteriaOptimizer()
optimized = optimizer.optimize(
    criteria=existing_criteria,
    enrollment_target=200,
    current_enrollment=120,
    retention_rate=0.85
)

# Analyze criteria complexity
analysis = optimizer.analyze_complexity(criteria)
```

## Input Format

### Study Design Parameters

```json
{
  "indication": "Type 2 Diabetes Mellitus",
  "phase": "Phase 2",
  "population": "adults",
  "age_range": {"min": 18, "max": 75},
  "study_duration": "24 weeks",
  "treatment_type": "oral",
  "primary_endpoints": ["HbA1c change from baseline"],
  "safety_considerations": ["cardiovascular risk"],
  "concomitant_meds_allowed": ["metformin"]
}
```

### Existing Criteria Format

```json
{
  "inclusion_criteria": [
    {
      "id": "I1",
      "criterion": "Age 18-75 years",
      "rationale": "Adult population per regulatory guidance",
      "category": "demographics"
    }
  ],
  "exclusion_criteria": [
    {
      "id": "E1",
      "criterion": "HbA1c < 7.0% or > 11.0%",
      "rationale": "Ensure measurable treatment effect",
      "category": "disease_severity"
    }
  ]
}
```

## Output Format

### Generated/Optimized Criteria

```json
{
  "inclusion_criteria": [
    {
      "id": "I1",
      "criterion": "Age 18-75 years, inclusive",
      "category": "demographics",
      "rationale": "Adult population; upper limit for safety",
      "priority": "required",
      "impact": "low"
    }
  ],
  "exclusion_criteria": [
    {
      "id": "E1",
      "criterion": "HbA1c < 7.5% or > 10.5% at screening",
      "category": "disease_severity",
      "rationale": "Optimal range for detecting treatment effect",
      "priority": "required",
      "impact": "medium",
      "flexibility": "widen by 0.5% if enrollment slow"
    }
  ],
  "optimization_notes": [
    "Widened HbA1c range from 7.0-11.0% to 7.5-10.5% based on feasibility data"
  ],
  "recruitment_metrics": {
    "estimated_screen_success_rate": 0.35,
    "estimated_enrollment_rate": 0.65,
    "key_barriers": ["HbA1c upper limit", "concomitant medication restrictions"]
  }
}
```

## Criteria Categories

| Category | Description | Examples |
|----------|-------------|----------|
| demographics | Age, sex, race, ethnicity | Age 18-75, women of childbearing potential |
| disease_severity | Disease stage, severity markers | HbA1c range, tumor stage, NYHA class |
| medical_history | Prior conditions, comorbidities | No cardiovascular events within 6 months |
| concomitant_meds | Allowed/prohibited medications | Stable metformin dose allowed |
| laboratory | Lab value requirements | eGFR > 30 mL/min, normal liver function |
| lifestyle | Diet, exercise, habits | Non-smoker, willing to maintain diet |
| compliance | Ability to participate | Able to provide informed consent |
| safety | Risk minimization criteria | No history of severe hypoglycemia |

## Optimization Strategies

### Common Modifications

| Issue | Strategy | Example |
|-------|----------|---------|
| Narrow age range | Widen limits | 18-70 → 18-75 years |
| Restrictive lab values | Adjust thresholds | eGFR > 60 → eGFR > 30 mL/min |
| Comorbidity exclusions | Add time limits | Exclude "current" vs "history of" |
| Medication washouts | Shorten periods | 4 weeks → 2 weeks |
| Geographic barriers | Add telemedicine | Include remote visits option |

### Retention Considerations

- Minimize visit frequency when possible
- Allow window periods for visit timing
- Provide transportation assistance language
- Consider patient-reported outcome burden

## Technical Details

- **Difficulty**: Medium
- **Standards**: ICH E6(R2) GCP, CDISC Protocol Representation Model
- **Data Sources**: ClinicalTrials.gov eligibility patterns, literature feasibility data
- **Dependencies**: None (pure Python)

## References

- `references/criteria_templates.json` - Templates by therapeutic area
- `references/optimization_guidelines.md` - Best practices for criteria optimization
- `references/common_pitfalls.md` - Frequent eligibility design mistakes
- `references/regulatory_guidance.md` - FDA/EMA guidance on eligibility criteria
- `references/feasibility_data.json` - Screen failure rates by criterion type

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (../)
- [ ] Output does not expose sensitive information
- [ ] Prompt injection protections in place
- [ ] API requests use HTTPS only
- [ ] Input validated against allowed patterns
- [ ] API timeout and retry mechanisms implemented
- [ ] Output directory restricted to workspace
- [ ] Script execution in sandboxed environment
- [ ] Error messages sanitized (no internal paths exposed)
- [ ] Dependencies audited
- [ ] No exposure of internal service architecture

## Prerequisites

```text
# Python dependencies
pip install -r requirements.txt
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--indication` | str | Required | Therapeutic indication |
| `--phase` | str | Required |  |
| `--population` | str | "adults" | Target population |
| `--duration` | str | "" | Study duration |
| `--output` | str | Required | Output file path |
| `--age-min` | int | 18 | Minimum age |
| `--age-max` | int | 75 | Maximum age |
| `--input` | str | Required | Input criteria JSON file |
| `--enrollment-target` | int | Required | Target enrollment |
| `--current-enrollment` | int | Required | Current enrollment |
| `--output` | str | Required | Output file path |
| `--input` | str | Required | Input criteria JSON file |
| `--output` | str | Required | Output file path |
| `--input` | str | Required | Input criteria JSON file |
| `--condition` | str | Required | Medical condition |
| `--output` | str | Required | Output file path |

## Output Requirements

Every final response should make these items explicit when they are relevant:

- Objective or requested deliverable
- Inputs used and assumptions introduced
- Workflow or decision path
- Core result, recommendation, or artifact
- Constraints, risks, caveats, or validation needs
- Unresolved items and next-step checks

## Error Handling

- If required inputs are missing, state exactly which fields are missing and request only the minimum additional information.
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If `scripts/main.py` fails, report the failure point, summarize what still can be completed safely, and provide a manual fallback.
- Do not fabricate files, citations, data, search results, or execution outcomes.

## Input Validation

This skill accepts requests that match the documented purpose of `inclusion-criteria-gen` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `inclusion-criteria-gen` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

## Response Template

Use the following fixed structure for non-trivial requests:

1. Objective
2. Inputs Received
3. Assumptions
4. Workflow
5. Deliverable
6. Risks and Limits
7. Next Checks

If the request is simple, you may compress the structure, but still keep assumptions and limits explicit when they affect correctness.

## When Not to Use

- Do not proceed when required input files, identifiers, parameters, or context are missing — ask the user to provide them first.
- Do not assume capabilities beyond this skill's declared scope when the user requests external operations or inferences.
- Do not proceed without user confirmation when overwriting existing results, executing high-cost batch operations, or expanding task scope.

## Required Inputs

| Field | Required | Format/Source | Example | If Missing |
|---|---|---|---|---|
| User task description | Yes | Text | Research question, writing goal, analysis objective | Stop and ask user to provide |
| Primary input material | Depends on task | Text, file path, ID, table, or literature | PMID, PDF, CSV, DOCX, keywords, etc. | Specify which material type is missing |
| Output preference | No | Text | Language, format, target journal, template | Use skill default format |

## Output Contract

- Primary output: Structured result or target file aligned with this skill's objective.
- Optional output: Intermediate check notes, issue list, supplementary suggestions, or generated file paths.
- Format requirement: Unless the user specifies otherwise, prefer stable, reviewable Markdown or JSON; if the skill's bundled script requires a fixed format, use that format.
- If partially complete: Must explicitly mark as PARTIAL and state which steps are completed and which remain.

## Failure Handling

- Missing critical input: Explicitly state which fields, files, or identifiers are missing and pause.
- Script, template, or resource execution failure: Report the failing step, likely cause, and recovery suggestions — do not silently degrade.
- Partial completion only: Return the verified portion first, then list remaining blockers and suggested next steps.

## User Checkpoints

- Before executing batch processing, overwriting files, long-running searches, or multi-stage generation, confirm scope and output format with the user.
- Before proceeding when a key judgment is ambiguous, evidence is insufficient, or the workflow is entering the next stage, confirm with the user.

## Quick Validation

- Check that key scripts, templates, or reference file paths this skill depends on exist.
- Check that the final output contains the core fields, sections, or files specified for this task.
- Check that results clearly mark assumptions, limitations, and incomplete items.
