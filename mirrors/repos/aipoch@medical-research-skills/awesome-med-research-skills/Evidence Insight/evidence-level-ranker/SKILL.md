---
name: evidence-level-ranker
description: Ranks papers by evidence family, methodological quality tier, validation depth, and claim discipline; assigns anchor, context-setting, mechanistic support, or caution citation roles; prevents prestige-based or design-label-based ranking errors.
license: MIT
author: AIPOCH
---

# Evidence Level Ranker | 证据等级排序器

## Task

Use this skill to rank papers by **evidence strength**, **methodological quality**, and **citation priority** within one explicit comparison framework.

This skill should identify what kind of evidence each paper provides, how much methodological trust it deserves, how much validation or corroboration it contains, and whether it should be treated as a **high-priority anchor citation**, **context-setting citation**, **mechanistic support citation**, or **low-priority / caution citation**.

This skill must not equate study design labels with true evidentiary value automatically. A meta-analysis is not automatically decisive, an RCT is not automatically well-conducted, a cohort is not automatically weak, and a mechanism study is not automatically non-informative. The skill must rank literature based on the combination of **design family, execution quality, validation depth, bias control, and claim discipline**.

This skill is especially useful when the user needs to:
- prioritize citations for a manuscript, review, protocol, or slide deck;
- compare reviews, observational studies, interventional studies, mechanism papers, omics studies, and validation studies in one framework;
- identify which papers are most suitable for supporting strong claims versus background framing;
- avoid treating flashy but fragile findings as top-tier evidence.

## Reference Module Integration

Use reference modules as execution dependencies, not decoration.

- `references/evidence-family-taxonomy.md` → use when identifying study design family in **Step 2**.
- `references/methodological-quality-audit-rules.md` → use when assessing execution quality in **Step 3**.
- `references/validation-depth-rules.md` → use when judging internal vs. external vs. orthogonal validation in **Step 4**.
- `references/claim-discipline-rules.md` → use when separating what a paper shows from what it claims in **Step 5**.
- `references/citation-priority-rules.md` → use when assigning citation roles in **Step 6**.
- `references/cross-design-ranking-framework.md` → use when comparing papers across different evidence families in **Steps 6–7**.
- `references/literature-integrity-rules.md` → governs all citation handling and evidence statement accuracy in **Section J**.
- `references/output-section-guidance.md` → enforces section-level output format for **Sections A–J**.
- `references/workflow-step-template.md` → structures the workflow explanation.

If the paper set includes mixed evidence families, this skill should explicitly use all relevant modules rather than collapsing all papers into one generic score.

## Input Validation

This skill accepts: one paper, a set of papers, or a literature shortlist for evidence-strength ranking and citation-priority assignment.

If the user's request does not involve ranking papers by evidence quality — for example, asking to write a literature review, retrieve papers, summarize clinical guidelines, or make treatment recommendations — do not proceed with the ranking pipeline. Instead respond:
> "Evidence Level Ranker is designed to rank a provided set of papers by evidence family, methodological quality, validation depth, and claim discipline, and to assign citation roles. Your request ([restatement]) appears to be outside this scope. Please provide the set of papers you want ranked, or use a more appropriate tool."

Before ranking, confirm what the user is actually asking to compare.

Required or strongly preferred inputs:
- one paper, a set of papers, or a literature shortlist;
- the disease, intervention, target, biomarker, exposure, or question of interest;
- the intended downstream use, if provided: background citation, key evidence citation, manuscript support, protocol support, clinical justification, mechanism support, etc.

If the input is incomplete, this skill should still proceed by ranking based on the available materials, but it must label major uncertainty sources explicitly.

This skill should distinguish between:
- ranking **papers on the same question**;
- ranking **mixed papers across evidence families**;
- ranking for **citation priority**, not for treatment recommendation or clinical decision-making.

## Sample Triggers

- “Help me rank these papers by evidence level.”
- “Which of these studies should I cite first?”
- “Compare this meta-analysis, this cohort, and this mechanism paper in one evidence framework.”
- “Which papers are strongest for supporting my claim?”
- “Please sort these studies by methodological strength and validation depth.”
- “I want to know which of these papers are anchor citations versus background citations.”

## Core Function

The core function of this skill is to convert a mixed literature set into a **transparent evidence ranking**, with each paper positioned on four linked but non-identical dimensions:

1. **Evidence Family** — what kind of study this is.
2. **Methodological Quality** — how well the study was actually executed.
3. **Validation / Corroboration Depth** — how much independent support or replication exists within the study or around it.
4. **Citation Priority** — how appropriate the paper is for strong support, contextual support, mechanistic support, or cautious mention.

This skill should rank papers comparatively, but it must also explain *why* each paper occupies its position. Rankings without explicit reasoning are incomplete.

## Execution

### Step 1 — Identify the comparison scope
Determine whether the papers address:
- the same core question;
- related but not identical questions;
- different evidence roles within one argument.

Do not force a false apples-to-apples comparison when papers are serving different evidentiary purposes.

### Step 2 — Identify the true study design for each paper
For each paper, identify the actual study design using methods, not just the authors’ self-description.

Separate:
- systematic review / meta-analysis;
- randomized trial / non-randomized intervention;
- prospective cohort / retrospective cohort / case-control / cross-sectional / registry / real-world evidence;
- diagnostic / prognostic / predictive / validation study;
- mechanism experiment / animal study / cell study / omics discovery study / computational study.

Do not confuse data source, assay type, model type, or platform type with study design.

### Step 3 — Judge methodological quality
Assess how strong the methods actually are.

Review at least these dimensions when relevant:
- sampling logic and cohort definition;
- inclusion / exclusion logic;
- confounding control and bias handling;
- sample size burden relative to analytical complexity;
- outcome definition and comparator appropriateness;
- statistical discipline, including multiplicity and model burden;
- calibration, robustness, sensitivity analysis, and missing-data handling when relevant;
- reproducibility and transparency of key methods.

**Do not use statistical significance or reported effect size magnitude as evidence of good methods.** Assess sampling logic, bias control, and study design independently of reported p-values. A p < 0.05 result in a poorly executed study is not evidence of methodological strength.

A higher-level design should not be ranked highly if execution is weak.

### Step 4 — Judge validation and corroboration depth
Assess how much the results are supported beyond the initial finding.

Distinguish:
- no meaningful validation;
- internal split / resampling only;
- external validation cohort;
- orthogonal assay confirmation;
- independent replication;
- prospective or implementation-relevant confirmation.

Do not over-credit repeated analysis of closely related datasets as if it were independent validation.

### Step 5 — Judge claim discipline
Check whether the paper’s conclusions stay inside the evidence boundary.

Flag overclaim patterns such as:
- association presented as causation;
- retrospective performance presented as clinical utility;
- exploratory biomarker framed as established marker;
- mechanism signal framed as therapeutic proof;
- subgroup result framed as generalizable finding.

A paper with good methods but overextended conclusions should lose citation priority for strong claims.

### Step 6 — Assign evidence position and citation role
For each paper, assign all of the following:
- evidence family;
- methodological quality tier;
- validation depth tier;
- claim-discipline judgment;
- citation role.

Recommended citation roles:
- **Anchor citation** — strongest paper(s) for supporting a central claim.
- **High-value support citation** — strong support but not the single best anchor.
- **Context-setting citation** — useful for framing the topic or background.
- **Mechanistic support citation** — useful for biological rationale rather than direct clinical inference.
- **Caution citation** — cite only with explicit limitations.

### Step 7 — Produce the comparative ranking
Rank the papers explicitly and explain the ranking logic.

The ranking should reflect not only nominal evidence hierarchy, but also actual execution quality, validation strength, and claim appropriateness.

### Step 8 — State limitations of the ranking itself
Make explicit where the ranking is uncertainty-limited.

Examples:
- incomplete access to methods or supplementary material;
- unclear validation independence;
- mixed study purposes that reduce direct comparability;
- missing statistical detail;
- ambiguous endpoint or cohort definitions.

## Mandatory Output Structure

Use the following structure every time.

### A. Ranking Objective
State what is being ranked, for what question, and for what downstream use.

### B. Evidence Family Map
List each paper with its true study design / evidence family.

### C. Methodological Quality Review
For each paper, summarize the main strengths and weaknesses affecting trustworthiness.

### D. Validation and Corroboration Review
State what validation exists and how much confidence it adds.

### E. Claim Discipline Review
State whether the paper’s stated conclusions stay within the evidence boundary.

### F. Comparative Evidence Ranking
Provide a ranked list from strongest to weakest **for the stated purpose**, with clear reasoning.

### G. Citation Priority Recommendation
For each paper, assign one citation role:
- Anchor citation
- High-value support citation
- Context-setting citation
- Mechanistic support citation
- Caution citation

### H. Key Reasons for the Ranking
State the main factors that drove the order.

### I. Ranking Uncertainties and Caveats
Explain where incomplete information or mixed evidence roles limit certainty.

### J. References and Verification Notes
When the user provides or references specific papers, preserve verified bibliographic details accurately.
If any publication details, PMIDs, DOIs, trial identifiers, or validation claims cannot be verified from the provided material, mark them as **unverified** rather than guessing.

## Hard Rules

1. Always separate **study design label** from **true evidence value**.
2. Never rank papers by journal prestige, citation count, or narrative confidence alone.
3. Never treat statistical significance as equivalent to methodological reliability.
4. Never treat a nominally high-tier design as automatically top-ranked if execution is weak.
5. Always separate **internal validation**, **external validation**, **orthogonal confirmation**, and **independent replication**.
6. Never treat exploratory results as established evidence without appropriate validation.
7. Always distinguish **clinical evidence**, **observational evidence**, **mechanistic evidence**, and **omics / computational evidence**.
8. Never confuse a paper’s usefulness for biological rationale with its usefulness for supporting a strong clinical or causal claim.
9. Never overstate the meaning of subgroup findings, secondary analyses, or post hoc signals.
10. Always evaluate whether the paper’s conclusion language exceeds what the methods support.
11. Never fabricate references, PMIDs, DOIs, trial names, approval status, guideline status, or validation claims.
12. Never present vague memory or field lore as literature-backed fact.
13. If bibliographic or methodological details cannot be verified from the provided material, label them as **unverified**, **unclear**, or **not reported**.
14. Never invent missing sample sizes, model settings, validation cohorts, or effect estimates.
15. Do not collapse heterogeneous papers into a single ladder without explaining the comparison logic.
16. If two papers serve different evidence roles, state that explicitly rather than forcing a simplistic rank order.
17. Treat the output as incomplete if the reasoning behind the ranking is not transparent.

## What This Skill Should Not Do

This skill should not:
- act as a treatment recommendation engine;
- turn evidence ranking into clinical advice;
- assume meta-analysis always outranks all primary research automatically;
- assume mechanism work is low value in every context;
- replace full risk-of-bias appraisal frameworks when a formal systematic review standard is required;
- produce fake precision when the paper set is heterogeneous or incompletely reported.

## Quality Standard

A high-quality output from this skill should:
- correctly identify what each paper actually is;
- explain why some papers deserve stronger citation priority than others;
- separate evidence family, methodological quality, validation depth, and claim discipline clearly;
- avoid flattening mixed literature into a misleading single-number score;
- make the ranking usable for manuscript writing, literature review, protocol framing, or evidence mapping;
- make uncertainty explicit whenever details are missing or not verifiable.
