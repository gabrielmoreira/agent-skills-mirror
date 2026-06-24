---
name: regulatory-submission
description: Prepare FDA/EMA regulatory submissions (IND/NDA/BLA/510(k)/PMA/MAA) in CTD format. Generate module outlines (Modules 1-5), run ICH compliance checks (ALCOA+, E6 GCP, Q1-Q12), verify data integrity, and produce submission-ready dossiers with cover letters and checklists.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)


# Regulatory Submission — FDA/EMA Dossier Structure

## When to Use

- Preparing FDA/EMA regulatory submissions (IND/NDA/BLA/510(k)/PMA/MAA)
- The user mentions regulatory submission, FDA, EMA, IND, NDA, BLA, CTD, dossier, or regulatory affairs
- Generating CTD module outlines and compliance checks for dossier assembly

## Workflow

1. **Identify submission type** — Input: product type, development stage, market (US/EU) → Output: submission type (IND/NDA/BLA/510(k)/PMA/MAA)
2. **Generate CTD outline** — Map to Modules 1-5 with required sections → Output: CTD table of contents
3. **Populate Module 2** — Draft Quality Overall Summary, Nonclinical/Clinical Overviews → Output: Module 2 drafts
4. **Verify data integrity** — Check ALCOA+ compliance across all modules → Output: integrity audit report
5. **Run compliance check** — Verify against ICH guidelines (E6 GCP, Q1-Q12) → ⛔ Checkpoint: Review gaps with user, prioritize remediation → Output: compliance gap list
6. **Finalize dossier** — Compile modules, generate cover letters, verify cross-references → Output: submission-ready package

## If Data Incomplete

- Missing CTD sections → generate "[DATA REQUIRED]" placeholders with expected data sources
- ICH compliance gaps → classify critical/major/minor with remediation timeline
- Product type ambiguous → ask user to clarify drug vs. biologic vs. device

## Submission Types

### FDA
| Type | Purpose | Key Sections |
|------|---------|-------------|
| IND | Investigational New Drug | Chemistry, pharmacology, toxicology, clinical protocol |
| NDA | New Drug Application | Full CMC, nonclinical, clinical data |
| BLA | Biologics License | Manufacturing, characterization, clinical |
| 510(k) | Device clearance | Substantial equivalence, performance testing |
| PMA | Device approval | Clinical data, manufacturing |

### EMA: CTA | MAA | Scientific Advice

## CTD Format

- **Module 1**: Administrative (cover letters, forms, labeling)
- **Module 2**: Summaries (quality, nonclinical, clinical overviews)
- **Module 3**: Quality/CMC (drug substance, product, manufacturing)
- **Module 4**: Nonclinical (pharmacology, PK, toxicology)
- **Module 5**: Clinical (study reports, literature)

## Key Principles

- Follow ICH guidelines (E6 GCP, Q1-Q12)
- Data integrity: ALCOA+ (Attributable, Legible, Contemporaneous, Original, Accurate)
- Risk-based approach: prioritize critical quality attributes

## Error Handling

- If required inputs are missing, state exactly which fields are missing and request only the minimum additional information.
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If execution fails, report the failure point, summarize what can still be completed safely, and provide a manual fallback.
- Do not fabricate files, citations, data, search results, or execution outcomes.

## Input Validation

This skill accepts requests that match the documented purpose of `regulatory-submission` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `regulatory-submission` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.
