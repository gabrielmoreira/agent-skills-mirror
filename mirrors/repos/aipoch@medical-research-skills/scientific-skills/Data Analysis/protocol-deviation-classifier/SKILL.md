---
name: protocol-deviation-classifier
description: Classify clinical trial protocol deviations as major or minor based on ICH E6/GCP guidelines. Three-impact-dimension assessment (safety, data integrity, scientific validity), confidence scoring, and regulatory compliance reporting with recommended actions.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)


# Protocol Deviation Classifier

Clinical trial protocol deviation classification tool, based on GCP and ICH E6 guidelines, automatically determines whether deviations belong to "major deviations" or "minor deviations".

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
python scripts/main.py --input "Audit validation sample with explicit symptoms, history, assessment, and next-step plan." --format json
```

## When to Use

- Use this skill when the task needs Determine whether an incident in a clinical trial is a "major deviation.
- Use this skill for data analysis tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## When NOT to Use

- Do not use for classifying adverse events (use a MedDRA coding tool).
- Do not use as the final authority on deviation severity — classification must be confirmed by clinical QA personnel.
- Do not use for non-clinical-trial compliance issues (e.g., manufacturing, lab QC).
- Do not use when the deviation description is too vague to assess impact on safety, data integrity, or scientific validity — request clarification first.

## Workflow

1. **Receive deviation**: Collect the deviation description, type category, and optional severity factors (safety_impact, data_impact, scientific_impact). If the description is vague, request clarification before proceeding.
2. **Assess impact dimensions**: Evaluate the deviation against three dimensions — Subject Safety (none/low/medium/high), Data Integrity (none/low/medium/high), and Scientific Validity (none/low/medium/high). Use the classification standards tables above as reference.
3. **Apply classification rules**: Any dimension = High → Major Deviation. Safety = Medium AND (Data OR Science) = Medium+ → Major Deviation. Otherwise → Minor Deviation.
4. **Generate output**: Return classification with confidence score, rationale, regulatory basis (ICH E6 section references), and recommended actions. Use the JSON output format for batch processing.
5. **Fallback**: If the deviation type is not in the classification standards table, classify based on the three impact dimensions alone and flag for manual QA review.

## Features

- **Automatic Classification**: Automatically determines severity based on deviation description
- **Risk Assessment**: Assesses impact on subject safety, data integrity, and scientific validity
- **Regulatory Basis**: Classification basis complies with GCP, ICH E6, and FDA/EMA guidelines
- **Report Generation**: Generates deviation classification reports that meet regulatory requirements
- **Chinese Support**: Full support for Chinese clinical trial scenarios

## Deviation Classification Standards

### Major/Critical Deviation

Deviations that may affect trial data integrity, subject safety, or trial scientific validity:

| Category | Examples |
|------|------|
| Informed Consent | Performing research procedures without informed consent, using expired/incorrect informed consent forms |
| Inclusion/Exclusion Criteria | Enrolling subjects who don't meet inclusion criteria, enrolling subjects who meet exclusion criteria |
| Investigational Product | Overdose administration, contraindicated concomitant medication, incorrect route of administration, randomization error |
| Safety | Not performing safety monitoring as required by protocol, missing SAE/SUSAR reports, delayed reporting |
| Blinding | Unblinding by unauthorized personnel, unrecorded emergency unblinding procedures |
| Data Integrity | Falsifying/fabricating data, systematic missing of critical data |
| Prohibited Operations | Violating key operational procedures of trial protocol, not performing key efficacy assessments |

### Minor Deviation

Deviations unlikely to affect trial data integrity, subject safety, or trial scientific validity:

| Category | Examples |
|------|------|
| Visit Window | Slightly exceeding visit time window (e.g., within a few days), delay of non-critical visits |
| Sample Collection | Minor timing deviations in non-critical sample collection, slight delays in sample processing |
| Questionnaire Completion | Quality of life questionnaires/diary cards submitted a few days late |
| Data Recording | Delays in non-critical data recording, spelling/formatting errors |
| Procedure Execution | Adjustment of secondary procedure execution order, omission of non-critical assessments (e.g., height measurement) |
| Documentation | Delays in source document signatures, missing secondary documents (e.g., non-critical examination reports) |

## Usage

### Python API

```python
from scripts.main import DeviationClassifier

# Initialize classifier
classifier = DeviationClassifier()

# Classify single deviation
result = classifier.classify(
    description="Subject visit delayed by 2 days",
    deviation_type="Visit Window"
)
print(result.classification)  # "Minor Deviation"
print(result.confidence)      # 0.92
print(result.rationale)       # Classification rationale explanation

# Batch classification
deviations = [
    {"description": "Blood sample collected without informed consent", "type": "Informed Consent"},
    {"description": "Quality of life questionnaire submitted 3 days late", "type": "Data Collection"}
]
batch_results = classifier.classify_batch(deviations)

# Generate report
report = classifier.generate_report(batch_results)
```

### CLI Usage

```text
# Classify single deviation
python scripts/main.py classify --description "Subject visit delayed by 2 days" --type "Visit Window"

# Batch classification from file
python scripts/main.py batch --input deviations.json --output report.json

# Interactive classification
python scripts/main.py interactive

# Assess deviation impact
python scripts/main.py assess \
  --description "Subject accidentally took double dose of investigational drug" \
  --safety-impact high \
  --data-impact medium \
  --scientific-impact medium
```

### Input Format

**JSON Input File Format:**

```json
[
  {
    "id": "DEV-001",
    "description": "Subject visit delayed by 2 days",
    "type": "Visit Window",
    "occurrence_date": "2024-01-15",
    "severity_factors": {
      "safety_impact": "none",
      "data_impact": "low",
      "scientific_impact": "low"
    }
  },
  {
    "id": "DEV-002",
    "description": "Blood collection performed without informed consent",
    "type": "Informed Consent",
    "severity_factors": {
      "safety_impact": "high",
      "data_impact": "high",
      "scientific_impact": "high"
    }
  }
]
```

### Output Format

**Classification Result:**

```json
{
  "id": "DEV-001",
  "classification": "Minor Deviation",
  "classification_en": "Minor Deviation",
  "confidence": 0.92,
  "rationale": "Visit time window slightly delayed (2 days), does not affect subject safety, data integrity, or trial scientific validity.",
  "risk_factors": {
    "safety_risk": "none",
    "data_integrity_risk": "low",
    "scientific_validity_risk": "none"
  },
  "regulatory_basis": [
    "ICH E6(R2) Section 4.5",
    "GCP Section 6.4.4"
  ],
  "recommended_actions": [
    "Document in file",
    "Track trends"
  ]
}
```

## Classification Algorithm

Classification based on the following assessment dimensions:

1. **Subject Safety Impact** (Safety Impact)
   - None: No impact
   - Low: Minor impact
   - Medium: Moderate impact
   - High: Serious impact

2. **Data Integrity Impact** (Data Integrity Impact)
   - None: No impact
   - Low: Minor impact on non-critical data
   - Medium: Partial impact on critical data
   - High: Serious damage to critical data

3. **Trial Scientific Validity Impact** (Scientific Validity Impact)
   - None: No impact
   - Low: Minor impact on statistical power
   - Medium: May affect primary endpoint
   - High: Seriously affects trial conclusion

**Classification Rules:**
- Any dimension is High → Major Deviation
- Safety dimension is Medium and Data/Science either is Medium+ → Major Deviation
- Other cases → Minor Deviation

## Regulatory Basis

- ICH E6(R2) Good Clinical Practice Guideline
- ICH E6(R3) Good Clinical Practice Guideline (Draft)
- FDA 21 CFR Part 312 (IND Regulations)
- FDA Guidance for Industry: Oversight of Clinical Investigations
- EMA Reflection Paper on Risk Based Quality Management
- NMPA Good Clinical Practice for Drug Clinical Trials

## Dependencies

- Python 3.8+
- No third-party dependencies (pure Python standard library implementation)

## Notes

1. This tool provides classification recommendations, final determination must be confirmed by clinical quality assurance personnel
2. Serious/critical deviations must be reported to sponsor and ethics committee immediately
3. It is recommended to regularly review deviation trends and implement CAPA (Corrective and Preventive Actions)
4. Classification standards may vary by regulatory agency, trial type, and protocol requirements

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python/R scripts executed locally | Medium |
| Network Access | No external API calls | Low |
| File System Access | Read input files, write output files | Medium |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Output files saved to workspace | Low |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (../)
- [ ] Output does not expose sensitive information
- [ ] Prompt injection protections in place
- [ ] Input file paths validated (no ../ traversal)
- [ ] Output directory restricted to workspace
- [ ] Script execution in sandboxed environment
- [ ] Error messages sanitized (no stack traces exposed)
- [ ] Dependencies audited

## Prerequisites

```text
# Python dependencies
pip install -r requirements.txt
```

## Evaluation Criteria

### Success Metrics
- [ ] Successfully executes main functionality
- [ ] Output meets quality standards
- [ ] Handles edge cases gracefully
- [ ] Performance is acceptable

### Test Cases
1. **Basic Functionality**: Standard input → Expected output
2. **Edge Case**: Invalid input → Graceful error handling
3. **Performance**: Large dataset → Acceptable processing time

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-06
- **Known Issues**: None
- **Planned Improvements**: 
  - Performance optimization
  - Additional feature support

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

This skill accepts requests that match the documented purpose of `protocol-deviation-classifier` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `protocol-deviation-classifier` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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


## Inputs to Collect

- Required inputs: the user goal, the primary data or source file, and the requested output format.
- Optional inputs: output directory, formatting preferences, and validation constraints.
- If a required input is unavailable, return a short clarification request before continuing.


## Output Contract

- Return a short summary, the main deliverables, and any assumptions that materially affect interpretation.
- If execution is partial, label what succeeded, what failed, and the next safe recovery step.
- Keep the final answer within the documented scope of the skill.


## Validation and Safety Rules

- Validate identifiers, file paths, and user-provided parameters before execution.
- Do not fabricate results, metrics, citations, or downstream conclusions.
- Use safe fallback behavior when dependencies, credentials, or required inputs are missing.
- Surface any execution failure with a concise diagnosis and recovery path.
