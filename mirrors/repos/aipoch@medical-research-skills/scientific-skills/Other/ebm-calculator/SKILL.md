---
name: ebm-calculator
description: Evidence-Based Medicine diagnostic test calculator. Computes sensitivity, specificity, PPV, NPV, likelihood ratios, NNT, and pre/post-test probability.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# EBM Calculator

Evidence-Based Medicine diagnostic test calculator.

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
```

## When to Use

- Use this skill when calculating diagnostic test performance (sensitivity, specificity, PPV, NPV, likelihood ratios).
- Use this skill when converting between pre-test and post-test probability or computing NNT.
- Use this skill when the user says "calculate sensitivity", "EBM calculator", "diagnostic accuracy", or "likelihood ratio".

## Workflow

1. **Identify calculation mode**: Determine mode from user request — `diagnostic` (sensitivity/specificity/PPV/NPV/LR), `nnt` (number needed to treat), or `probability` (pre/post-test probability conversion).
2. **Collect required parameters**:
   - Diagnostic mode: TP, FN, TN, FP counts; optional prevalence for PPV/NPV adjustment
   - NNT mode: control event rate, experimental event rate
   - Probability mode: pre-test probability, likelihood ratio
3. **Validate inputs**: Check that all counts are non-negative integers, rates are between 0 and 1, and denominators are not zero. If invalid, report exact error and stop.
4. **Checkpoint**: Display input summary to user for confirmation before computing results.
5. **Compute results**: Execute calculations per mode. Include interpretation string (e.g., "LR+ of 10 strongly rules in disease").
6. **Output**: Return structured JSON with computed metrics and interpretation.
7. **Fallback**: If a required parameter is missing, output a template showing which fields are needed with example values.

## Features

- Sensitivity / Specificity calculation
- PPV / NPV with prevalence adjustment
- Likelihood ratios (LR+ / LR-)
- Number Needed to Treat (NNT)
- Pre/post-test probability conversion

## Parameters

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `--mode`, `-m` | string | diagnostic | No | Calculation mode (diagnostic, nnt, probability) |
| `--tp`, `--true-pos` | int | - | * | True positives (diagnostic mode) |
| `--fn`, `--false-neg` | int | - | * | False negatives (diagnostic mode) |
| `--tn`, `--true-neg` | int | - | * | True negatives (diagnostic mode) |
| `--fp`, `--false-pos` | int | - | * | False positives (diagnostic mode) |
| `--prevalence`, `-p` | float | - | No | Disease prevalence 0-1 (diagnostic mode) |
| `--control-rate` | float | - | ** | Control event rate 0-1 (nnt mode) |
| `--experimental-rate` | float | - | ** | Experimental event rate 0-1 (nnt mode) |
| `--pretest` | float | - | *** | Pre-test probability 0-1 (probability mode) |
| `--lr` | float | - | *** | Likelihood ratio (probability mode) |
| `--output`, `-o` | string | stdout | No | Output file path |

\* Required for diagnostic mode  
\** Required for nnt mode  
\*** Required for probability mode

## Output Format

```json
{
  "sensitivity": "float",
  "specificity": "float",
  "ppv": "float",
  "npv": "float",
  "lr_positive": "float",
  "lr_negative": "float",
  "interpretation": "string"
}
```

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

No additional Python packages required.

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

This skill accepts requests that match the documented purpose of `ebm-calculator` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `ebm-calculator` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
