---
name: icd10-cpt-coding-assistant
description: Parse clinical notes and recommend ICD-10-CM diagnosis codes and CPT procedure codes with confidence scoring. Cross-references diagnoses with procedure codes, generates alternatives for medium-confidence matches, and produces structured coding reports with human-review flags.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# ICD-10 & CPT Coding Assistant

A medical coding assistant that parses clinical notes and recommends appropriate ICD-10 diagnosis codes and CPT procedure codes with confidence scoring.

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

- Recommending ICD-10 diagnosis codes from clinical documentation
- Suggesting CPT procedure codes for billing and documentation
- Cross-referencing diagnoses with procedure codes
- Quality-checking existing code assignments

## Workflow

1. **Parse clinical note** — Input: clinical note text (free-text, SOAP, discharge summary, progress note) → extract diagnoses, procedures, symptoms → Output: structured clinical entities
2. **Map to ICD-10-CM** — Match diagnoses to ICD-10 codes → compute confidence scores (0.0-1.0) → generate alternatives for medium-confidence codes → Output: ICD-10 recommendation list with evidence
3. **Map to CPT** — Match procedures/services to CPT codes → determine E/M level if applicable → Output: CPT recommendation list with time/complexity
4. **Filter by confidence** — Apply `--confidence-threshold` (default 0.7) → separate high/medium/low confidence recommendations → ⛔ Checkpoint: Present low-confidence codes (<0.7) to user for manual review; confirm all codes before output → Output: filtered code set
5. **Generate report** — Format as JSON or text per `--format` flag → include evidence trail, alternatives, and human-review flags → Output: final coding report

## Overview

This skill analyzes clinical documentation to extract relevant medical information and map it to standardized coding systems:

- **ICD-10-CM**: International Classification of Diseases, 10th Revision, Clinical Modification (diagnosis codes)
- **CPT**: Current Procedural Terminology (procedure/service codes)

## Technical Difficulty: **HIGH** ⚠️

> **⚠️ HUMAN REVIEW REQUIRED**: Medical coding directly impacts billing, reimbursement, and clinical documentation. All recommendations must be verified by a certified medical coder or healthcare provider.

## Usage

```text
python scripts/main.py --input "clinical_note.txt" [--format json|text]
```

Or use programmatically:

```python
from scripts.main import CodingAssistant

assistant = CodingAssistant()
result = assistant.analyze("Patient presents with acute bronchitis...")
print(result.icd10_codes)
print(result.cpt_codes)
```

## Parameters

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `--input`, `-i` | string | - | Yes | Path to clinical note file |
| `--format`, `-f` | string | json | No | Output format (json, text) |
| `--output`, `-o` | string | stdout | No | Output file path |
| `--confidence-threshold` | float | 0.7 | No | Minimum confidence score (0.0-1.0) |
| `--include-alternatives` | flag | false | No | Include alternative code suggestions |

## Input Format

Accepts clinical notes in various formats:
- Free-text narrative
- SOAP notes (Subjective, Objective, Assessment, Plan)
- Discharge summaries
- Progress notes
- Procedure reports

## Output Format

### ICD-10 Recommendations
```json
{
  "icd10_codes": [
    {
      "code": "J20.9",
      "description": "Acute bronchitis, unspecified",
      "confidence": 0.92,
      "evidence": ["cough for 5 days", "wheezing on exam"],
      "alternatives": ["J20.0", "J44.9"]
    }
  ]
}
```

### CPT Recommendations
```json
{
  "cpt_codes": [
    {
      "code": "99213",
      "description": "Office visit, established patient, moderate complexity",
      "confidence": 0.85,
      "evidence": ["detailed history", "low complexity decision making"],
      "time": "20 minutes"
    }
  ]
}
```

## Confidence Scoring

- **0.90-1.00**: High confidence - Clear documentation, unambiguous mapping
- **0.70-0.89**: Medium confidence - Good documentation, some interpretation required
- **0.50-0.69**: Low confidence - Incomplete documentation, multiple possibilities
- **<0.50**: Very low confidence - Insufficient information, manual review essential

## Limitations

1. **No Medical Advice**: This tool does not provide clinical advice or diagnoses
2. **Coding Complexity**: Cannot handle all coding nuances (comorbidities, sequencing, modifiers)
3. **Regional Variations**: May not account for payer-specific coding requirements
4. **Updates**: Code sets may not reflect the latest annual updates

## References

See `references/` folder for:
- `icd10_common_codes.json`: Frequently used ICD-10 codes by specialty
- `cpt_common_codes.json`: Frequently used CPT codes by specialty
- `coding_guidelines.md`: General coding guidelines and conventions

## Safety & Compliance

- **HIPAA Awareness**: Ensure de-identification of PHI before processing
- **Audit Trail**: Maintain records of automated recommendations for compliance
- **Human Oversight**: All codes must be reviewed and approved by qualified personnel

## Dependencies

- Python 3.8+
- See `requirements.txt` for package dependencies

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

This skill accepts requests that match the documented purpose of `icd10-cpt-coding-assistant` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `icd10-cpt-coding-assistant` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
