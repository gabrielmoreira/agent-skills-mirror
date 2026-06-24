---
name: adverse-event-narrative
description: Generates CIOMS I-compliant ICSR narratives from adverse event case data for FDA and EMA regulatory submission. Includes temporal analysis, MedDRA coding, causality assessment using WHO-UMC or Naranjo criteria, and multi-format output.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Adverse Event Narrative Generator

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
python scripts/main.py --help
python scripts/main.py --validate-only --help
```

## Workflow

1. **Collect case data**: Receive adverse event case data including: patient demographics, medical history, concomitant medications, suspect drug(s) with dosing, adverse event description, diagnostic results, treatment, dechallenge/rechallenge dates, outcome, and causality assessment.
2. **Validate completeness**: Check that required CIOMS I fields are present (case ID, patient age/sex, suspect drug, AE with MedDRA PT, dates). Flag missing fields.
3. **Checkpoint**: Display case summary and list of missing fields to user. Confirm whether to proceed with partial data or wait for complete information.
4. **Reconstruct timeline**: Analyze temporal relationships: time to onset, dechallenge response, rechallenge response, temporal plausibility with known drug profile.
5. **Generate narrative**: Compose CIOMS I-compliant narrative in all 10 standard sections (demographics → causality assessment). Use objective, factual language; reserve opinion for causality section only.
6. **Checkpoint**: User reviews draft narrative for clinical accuracy and verifies that no patient identifiers remain.
7. **Format output**: Generate in requested format (CIOMS I, ICH E2B R3, FDA MedWatch 3500A). Apply MedDRA coding.
8. **Fallback**: If case data is too incomplete for narrative generation, output a structured checklist of required fields with example entries and a partial narrative for completed sections only.

## Overview

Regulatory-grade narrative generation tool that transforms adverse event case data into CIOMS-compliant ICSR narratives suitable for submission to FDA, EMA, and other health authorities.

**Key Capabilities:**
- **CIOMS I Compliance**: Standardized narrative structure per international guidelines
- **ICH E2B Integration**: Electronic submission format compatibility
- **Temporal Analysis**: Timeline reconstruction and causality assessment
- **Medical Accuracy**: Clinical terminology and MedDRA coding
- **Multi-Case Processing**: Batch narrative generation for periodic reporting
- **Quality Validation**: Automated checks for completeness and consistency

## When to Use

- Use this skill when writing adverse event narratives for regulatory submission (FDA, EMA, CIOMS I).
- Use this skill when preparing ICSR reports or generating safety narratives with MedDRA coding and causality assessment.
- Use this skill when the user says "AE narrative", "ICSR", "CIOMS narrative", "safety report", or "MedWatch narrative".

## Core Capabilities

### 1. CIOMS I Narrative Structure

Generate standardized sections per CIOMS guidelines:

```python
from scripts.narrative_generator import NarrativeGenerator

generator = NarrativeGenerator()

# Generate complete narrative
narrative = generator.generate(
    case_data=case_json,
    format="cioms_i",  # or "ich_e2b", "fda_medwatch"
    include_meddra=True
)

narrative.save("ICSR_2024_001_narrative.txt")
```

**Standard Sections:**
1. **Patient Demographics** - Age, sex, weight, relevant characteristics
2. **Medical History** - Significant pre-existing conditions
3. **Concomitant Medications** - Other drugs at time of event
4. **Suspect Drug(s)** - Medication(s) in question with dosing
5. **Adverse Event** - Detailed reaction description with MedDRA terms
6. **Diagnostic Results** - Lab values, imaging, procedures
7. **Treatment** - Medical management of the event
8. **Dechallenge/Rechallenge** - Effect of drug withdrawal/reintroduction
9. **Outcome** - Final patient status and sequelae
10. **Causality Assessment** - Reporter's relationship evaluation

### 2. Temporal Relationship Analysis

Reconstruct timeline and assess temporal plausibility:

```python
# Analyze temporal relationships
timeline = generator.analyze_timeline(
    drug_start="2024-01-15",
    drug_stop="2024-02-01",
    ae_onset="2024-01-28",
    dechallenge_date="2024-02-01",
    rechallenge_date=None
)

# Output shows temporal assessment
# "AE onset 13 days after drug initiation, positive dechallenge within 24h"
```

**Assessments Generated:**
- Time to onset (latency period)
- Dechallenge response (positive/negative/unknown)
- Rechallenge response (if applicable)
- Temporal plausibility (consistent with known drug profile)

### 3. Causality Evaluation Support

Structure causality assessment per WHO-UMC criteria:

```python
# Generate causality section
causality = generator.assess_causality(
    case_data=case,
    criteria="who_umc",  # or "naranjo", "cochrane"
    include_rationale=True
)

# Output structured assessment with points for each criterion
```

**WHO-UMC Categories:**
- **Certain** - Event reproduced on rechallenge
- **Probable/Likely** - Reasonable time, positive dechallenge, alternative causes unlikely
- **Possible** - Compatible time, but alternative causes possible
- **Unlikely** - Incompatible time or alternative cause probable
- **Conditional/Unclassified** - Insufficient information
- **Unassessable/Unclassifiable** - Data contradictory or incomplete

### 4. Multi-Format Output

Generate narratives for different regulatory contexts:

```python
# FDA MedWatch Form 3500A
fda_narrative = generator.generate(
    case_data=case,
    format="fda_medwatch",
    max_length=2000  # Character limit
)

# EMA E2B(R3) electronic format
ema_narrative = generator.generate(
    case_data=case,
    format="ich_e2b",
    version="R3"
)

# CIOMS I paper format
cioms_narrative = generator.generate(
    case_data=case,
    format="cioms_i"
)
```

## Quality Checklist

**Pre-Generation:**
- [ ] Case ID unique and formatted per SOP
- [ ] Patient age/sex complete
- [ ] Suspect drug(s) clearly identified
- [ ] Adverse event(s) coded with MedDRA PT
- [ ] Dates consistent (no future dates)
- [ ] Reporter information included

**Narrative Content:**
- [ ] All CIOMS I sections present
- [ ] Temporal sequence clear and logical
- [ ] Dechallenge/rechallenge described (if applicable)
- [ ] Lab values with reference ranges
- [ ] Concomitant medications listed
- [ ] Medical history relevant to event
- [ ] Outcome clearly stated
- [ ] Causality assessment justified

**Post-Generation:**
- [ ] MedDRA terms accurate and current
- [ ] No contradictory information
- [ ] Language objective and factual
- [ ] No speculation or opinion (except causality section)
- [ ] Patient identifiers removed or de-identified
- [ ] **CRITICAL**: Medical review completed
- [ ] **CRITICAL**: Causality assessment by qualified physician

## Common Pitfalls

**Completeness Issues:**
- ❌ **Missing dechallenge information** → Cannot assess causality
  - ✅ Always document effect after drug discontinuation

- ❌ **Vague temporal information** → "Recently started" vs. specific dates
  - ✅ Use exact dates when available

- ❌ **Incomplete concomitant medication list** → Alternative causes missed
  - ✅ Include all medications within relevant timeframe

**Medical Accuracy Issues:**
- ❌ **Incorrect MedDRA coding** → Wrong medical concept
  - ✅ Use current MedDRA version; verify with medical reviewer

- ❌ **Confusing correlation with causation** → Temporal = causal
  - ✅ Clearly state "temporally associated" vs. "causally related"

- ❌ **Omitting alternative diagnoses** → Biased toward drug causation
  - ✅ Include all differential diagnoses considered

**Regulatory Issues:**
- ❌ **Opinion in narrative body** → "Clearly caused by drug"
  - ✅ Reserve opinion for causality section; narrative should be factual

- ❌ **Patient identifiers** → HIPAA/privacy violation
  - ✅ De-identify per regulatory requirements

- ❌ **Abbreviations not defined** → Assumes reader knowledge
  - ✅ Spell out on first use in each narrative

## References

Available in `references/` directory:

- `cioms_i_guidelines.pdf` - CIOMS I international reporting standards
- `ich_e2b_specifications.md` - ICH E2B(R3) electronic format details
- `meddra_coding_guide.md` - MedDRA terminology and coding principles
- `who_umc_causality.md` - WHO causality assessment criteria
- `fda_medwatch_guide.md` - FDA Form 3500A instructions
- `gvp_module_vi.md` - EU Good Pharmacovigilance Practices
- `narrative_templates.md` - Example narratives by case type

## Scripts

Located in `scripts/` directory:

- `main.py` - CLI interface for narrative generation
- `narrative_generator.py` - Core narrative composition engine
- `temporal_analyzer.py` - Timeline reconstruction and analysis
- `causality_assessor.py` - Causality evaluation support
- `meddra_integrator.py` - Medical terminology and coding
- `validator.py` - Completeness and quality checks
- `format_converter.py` - Convert between CIOMS, E2B, MedWatch formats
- `batch_processor.py` - Multi-case narrative generation

## Limitations

- **Medical Review Required**: Generates draft only; requires physician review before submission
- **Causality Assessment**: Structures reporter's assessment; does not perform independent causality evaluation
- **MedDRA Version**: Uses installed MedDRA version; may not have latest terms
- **Language**: Optimized for English; other languages may need translation
- **Literature Integration**: Does not automatically search literature for similar cases
- **Signal Detection**: Individual case narratives only; aggregate analysis requires other tools
- **Legal Proceedings**: Not suitable for litigation support or expert witness reports

---

**⚠️ CRITICAL: This tool generates draft narratives for efficiency. All adverse event narratives require review by qualified drug safety physicians before regulatory submission. Causality assessment must be performed by healthcare professionals with access to complete medical records.**

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

This skill accepts requests that match the documented purpose of `adverse-event-narrative` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `adverse-event-narrative` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
