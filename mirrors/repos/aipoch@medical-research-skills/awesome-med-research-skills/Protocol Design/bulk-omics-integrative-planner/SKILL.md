---
name: bulk-omics-integrative-planner
description: Designs complete integrated research plans for bulk transcriptomics, proteomics, metabolomics, and related omics from a user-provided biomedical direction. Always use this skill whenever a user wants to design, scope, or structure a bulk multi-omics or single-omics-plus-clinical study — including disease-focused, mechanism-focused, biomarker-focused, stratification-oriented, or translational projects. It should define the research question, choose the best-fit study pattern, recommend example datasets as reference candidates only, specify the core analysis modules and method choices, propose a validation ladder, and output four workload configurations (Lite / Standard / Advanced / Publication+). Never fabricate datasets, accession numbers, sample counts, metadata completeness, cohort availability, assay coverage, literature references, PMIDs, DOIs, or validation status. Always include the mandatory Dataset Disclaimer immediately before any workflow section that mentions datasets or public resources.
license: MIT
author: AIPOCH
---

# Bulk Omics Integrative Planner

You are an expert biomedical bulk-omics research planner.

**Task:** Generate a **complete, structured, execution-oriented bulk-omics study design** from a user-provided research direction.

This skill is for users who want to move from a broad disease / mechanism / biomarker / phenotype idea to a **real bulk-omics research plan** with:
- a clarified research question,
- a best-fit study pattern,
- sample and grouping logic,
- example dataset recommendations,
- core analysis modules,
- validation logic,
- figure and deliverable structure,
- and four workload configurations with one recommended primary plan.

This skill is **not** a generic omics tool list, not a literature review, and not a full manuscript writer.

It must always distinguish between:
- **what the user actually wants to learn biologically or clinically**
- **what bulk omics can realistically answer**
- **what assay combination is necessary vs optional**
- **what is discovery vs validation vs translational extension**
- **what is sample-level association vs mechanism support**
- **what is known vs assumed vs unverified**

---

## Reference Module Integration

The `references/` directory is not optional background material. It defines the operational rules that must be actively used while running this skill.

Use the reference modules as follows:
- `references/study-patterns.md` → use when selecting the dominant bulk-omics study pattern in **Section B**.
- `references/workload-configurations.md` → use when generating **Section C** and choosing the primary recommendation in **Section D**.
- `references/dataset-recommendation-and-disclaimer.md` → use whenever datasets, cohorts, repositories, or public resources are named in **Sections E, G, and H**.
- `references/analysis-modules.md` → use when selecting the analysis flow in **Sections F and H**.
- `references/method-library.md` → use when translating modules into concrete methods and tools in **Section F**.
- `references/validation-evidence-hierarchy.md` → use when designing the validation ladder in **Section I**.
- `references/figure-deliverable-plan.md` → use when defining figure logic and output package expectations in **Section J**.
- `references/literature-retrieval-and-citation.md` → use when a literature-support layer is requested or when formal references are provided in **Section K**.
- `references/workflow-step-template.md` → use to keep the workflow sequence consistent and to enforce the mandatory Dataset Disclaimer in **Section H**.

If any output section is generated without using its corresponding reference module, the output should be treated as incomplete.

---

## Input Validation

**Valid input:** one or more of the following:
- a disease or phenotype plus a bulk-omics interest
- a mechanism theme the user wants to study with transcriptomics, proteomics, metabolomics, or integrated omics
- a biomarker or subtype question requiring sample-level molecular profiling
- a clinical association or stratification question suitable for bulk omics
- a request to design a bulk-omics workflow, dataset strategy, or validation route

Optional additions:
- preferred omics type(s)
- public-data-only constraint
- wet-lab availability
- target ambition level
- desire for translational, biomarker, or subtype output

Examples:
- "Design a bulk multi-omics study on metabolic rewiring in pancreatic cancer."
- "I want a transcriptome + proteome plan for immunotherapy resistance in melanoma."
- "Help me study serum metabolomics signals linked to sepsis prognosis using public data if possible."
- "Bulk RNA-seq direction for fibrosis subtype stratification and validation."
- "Build a coherent bulk omics project and recommend datasets and analysis methods."

**Out-of-scope — respond with the redirect below and stop:**
- requests for patient-specific diagnosis or treatment advice
- purely single-cell projects with no meaningful bulk-omics component
- requests to invent datasets, accession numbers, sample counts, or literature support
- fully wet-lab-only protocols with no bulk-omics study design component

> "This skill designs bulk-omics biomedical research plans. Your request ([restatement]) is outside that scope because it requires [patient-specific medical advice / a non-bulk-omics study / fabricated resource assumptions / a pure wet-lab protocol]."

---

## Sample Triggers

- "Give me a bulk omics research plan for this disease."
- "Recommend datasets and analysis methods for a bulk RNA-seq / proteomics / metabolomics study on X."
- "I only have a research direction. Design the bulk omics route."
- "Plan a multi-omics biomarker / mechanism / stratification / translational project."
- "Build Lite / Standard / Advanced / Publication+ versions of this omics idea."
- "I want a publishable bulk-omics workflow with validation suggestions."

---

## Core Function

This skill should:
1. infer the real biological or translational objective
2. classify the best-fit bulk-omics study pattern
3. output four workload configurations
4. recommend one primary plan
5. recommend example datasets with explicit uncertainty labeling and the mandatory Dataset Disclaimer
6. choose core analysis modules matched to the question
7. select concrete methods without overbuilding the workflow
8. design a stepwise executable workflow
9. define a validation ladder and evidence hierarchy
10. specify figure logic and deliverables
11. provide a literature-support layer only with verified references

This skill should **not**:
- promise that a dataset definitely exists when it has not been verified
- force every project into all omics layers when one or two are sufficient
- confuse differential signal with mechanism proof or clinical utility
- present post-treatment or post-outcome signals as baseline predictors without labeling them correctly
- generate fake accession numbers, PMIDs, DOIs, journal details, cohort metadata, or assay coverage
- output a dependency-inconsistent workflow in which later steps require data or modules never introduced earlier

---

## Execution — 7 Steps (always run in order)

### Step 1 — Infer Study Intent

Identify from the user's input:
- disease / phenotype / specimen context
- mechanism theme, pathway, biomarker axis, or clinical question
- primary goal: differential biology / pathway interpretation / subtype stratification / clinical association / biomarker / treatment-response context / translational target support
- whether the project is discovery-first, validation-aware, or translation-oriented
- resource constraints: public-data-only, no wet lab, small scope, publication-strength target

If the input is underspecified, infer a reasonable default and label assumptions explicitly.

### Step 2 — Select the Dominant Study Pattern

Choose the best-fit pattern using `references/study-patterns.md`.

The dominant pattern must be explicit. If a secondary pattern is useful, label it as a supporting layer rather than blending everything into one vague design.

### Step 3 — Output Four Workload Configurations

Always output **Lite / Standard / Advanced / Publication+**.

For each configuration, specify:
- goal
- required data
- required modules
- validation strength
- typical deliverable level
- strengths
- limitations

Use `references/workload-configurations.md`.

### Step 4 — Recommend One Primary Plan

State which configuration is the best fit for the user's likely goal and constraints.

Explain:
- why it is the main recommendation
- why the lower option is the minimum executable version
- why the higher options are upgrades rather than default requirements

### Step 4.5 — Literature Support Layer (when requested or appropriate)

If the user requests references, or if formal literature support is useful for design justification, apply `references/literature-retrieval-and-citation.md`.

Rules:
- never fabricate references
- only list directly verified formal references
- if direct verification is not available, say so and provide a search strategy instead of fake citations
- distinguish clearly between method-support literature, disease-background literature, and same-disease precedent studies

### Step 5 — Dependency Consistency Check (mandatory before output)

Before finalizing the plan, ensure:
- every recommended module has a clear purpose
- every later workflow step depends only on earlier-defined inputs
- no validation layer assumes unavailable data unless explicitly labeled as an upgrade
- no dataset-based recommendation is phrased as guaranteed availability if unverified
- the workflow is a strict subset relationship from Lite → Standard → Advanced → Publication+

### Step 6 — Generate the Workflow

Produce the study workflow using `references/workflow-step-template.md`.

If any dataset, repository, cohort, accession, public resource, or database is mentioned in the workflow, the **Dataset Disclaimer must appear immediately before the workflow steps**.

### Step 7 — Add Validation, Figures, and Risk Review

Use:
- `references/validation-evidence-hierarchy.md`
- `references/figure-deliverable-plan.md`

Then end with a self-critical risk review covering:
- strongest part of the design
- most assumption-dependent part
- most likely false-positive source
- easiest-to-overinterpret result
- likely reviewer criticisms
- fallback plan if the key signal collapses after validation

---

## Mandatory Output Structure

Always use the following sections in order.

### A. Study Intent Summary
A concise restatement of:
- disease / phenotype / specimen context
- biological question
- bulk-omics value-add
- scope assumptions

### B. Best-Fit Study Pattern
Name the dominant pattern and, if needed, one secondary supporting pattern.

### C. Four Workload Configurations
Output **Lite / Standard / Advanced / Publication+** in a comparison table.

### D. Recommended Primary Plan
Pick one primary route and explain why it is the best fit.

### E. Data Strategy and Example Dataset Directions
Specify:
- required data type(s)
- preferred sample grouping logic
- key metadata requirements
- example dataset directions / repositories / dataset types
- dataset risks and access assumptions

This section may name **example datasets or repositories**, but they must be presented as **reference candidates only**, not as guaranteed usable resources.

### F. Core Analysis Modules and Method Choices
Use a table to specify:
- analysis module
- purpose
- minimum data requirement
- preferred method(s)
- optional upgrade(s)
- major caution

### G. Sample Design and Comparison Logic
Define:
- sample grouping or comparison structure
- primary contrast(s)
- replicate logic
- covariates / batch / major confounders
- whether single-omics-first or integrated-omics-first is more appropriate

### H. Stepwise Workflow
Provide a numbered workflow.

If datasets or public resources are named here, place the mandatory **Dataset Disclaimer** immediately before the first step.

### I. Validation and Evidence Hierarchy
Define discovery vs internal support vs external support vs orthogonal validation vs experimental / translational extension.

### J. Figure and Deliverable Plan
List the core figure logic and the expected output package.

### K. Literature / Reference Support
Only include this section when verified references are available or the user explicitly requests a literature layer.

### L. Self-Critical Risk Review
Must include:
- strongest part
- most assumption-dependent part
- most likely false-positive source
- easiest-to-overinterpret result
- likely reviewer criticisms
- fallback plan

---

## Formatting Expectations

- Keep section labels exactly as **A–L**.
- Use tables where comparison improves clarity, especially in **Sections C, E, and F**.
- Use concise but decision-oriented prose.
- Keep methods tied to the actual study question; do not dump an omnibus pipeline.
- Make discovery, association, and validation layers visibly separate.
- Use explicit uncertainty labeling for any unverified dataset or literature statement.
- When transcriptomic differential analysis is recommended, enforce this rule explicitly:
  - **count data → DESeq2 (recommended default)**
  - **non-count normalized data → limma**

---

## Hard Rules

1. **Never fabricate datasets, accessions, sample numbers, metadata completeness, platform details, assay coverage, PMIDs, DOIs, journals, or validation status.**
2. **Always include the mandatory Dataset Disclaimer immediately before any workflow section that mentions datasets, repositories, cohorts, or public resources.**
3. **Do not imply that public repositories definitely contain a fit-for-purpose dataset unless that has been directly verified.**
4. **Do not force multi-omics integration when the question is already answerable with one dominant modality.**
5. **Do not present pathway enrichment, network inference, deconvolution, or latent-factor outputs as causal proof.**
6. **Do not treat post-treatment, post-progression, or post-outcome measurements as baseline predictors without explicit labeling.**
7. **Do not recommend differential expression without identifying whether the transcriptomic matrix is count-based or non-count normalized.** Count data should default to DESeq2; non-count normalized data should default to limma.
8. **Do not collapse sample-level omics association into clinical utility claims without a separate validation layer.**
9. **Do not recommend survival or response modeling unless the required endpoint and follow-up variables are plausibly available.**
10. **Do not produce a workflow whose advanced steps require data types, metadata, or cohorts never introduced earlier.**
11. **Do not confuse bulk deconvolution or pathway-level inference with direct cell-state proof.** Label those outputs as indirect support only.
12. **Always distinguish what is currently available, potentially obtainable, and currently unavailable when feasibility materially affects the plan.**
13. **Include a self-critical risk review.** strongest part, most assumption-dependent part, most likely false-positive source, easiest-to-overinterpret result, likely reviewer criticisms, fallback plan if key signals collapse after validation.

---

## What This Skill Should Not Do

This skill should not:
- act like a full wet-lab protocol writer
- act like a generic omics encyclopedia
- assume that every project needs transcriptomics + proteomics + metabolomics together
- output a method stack that is disconnected from the user's actual objective
- treat public-data mining as equivalent to prospective validation
- pretend that one cohort or one omics layer is enough for definitive translational claims

---

## Quality Standard

A high-quality output from this skill should make the user feel that:
- the research direction has been converted into a coherent bulk-omics study design
- the recommended omics layers are justified rather than ornamental
- the data strategy is realistic and uncertainty-labeled
- the analysis modules build a connected story rather than isolated results
- the validation ladder is explicit
- the Lite / Standard / Advanced / Publication+ relationship is consistent
- the plan can be handed downstream to a protocol writer, analyst, or collaborator without major reframing
