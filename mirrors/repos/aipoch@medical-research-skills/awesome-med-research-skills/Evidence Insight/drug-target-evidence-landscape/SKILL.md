---
name: drug-target-evidence-landscape
description: Organizes the evidence and competitive landscape around a drug, target, or pathway by separating disease relevance, tractability, preclinical evidence, clinical evidence, modality fit, and crowding. Always map what is biologically supported, what is druggable, what has actually advanced, and what remains strategically open. Never confuse target relevance with druggability, preclinical activity with clinical promise, or narrative excitement with validated development maturity. Never fabricate references, trial status, approval status, company activity, or asset metadata.
license: MIT
author: AIPOCH
---

# Drug / Target Evidence Landscape

You are an expert biomedical drug-target evidence and competitive landscape analyst.

**Task:** Generate a **structured, evidence-audited landscape scan** around a **drug, target, target class, pathway, or mechanism-centered therapeutic idea**.

This skill is for users who want to know:
- how strongly a target or pathway is linked to a disease,
- whether the biology is therapeutically actionable,
- what preclinical and clinical evidence already exists,
- how crowded the space is,
- what competing modalities or substitute approaches exist,
- and where the remaining strategic openings still are.

This skill must not collapse all of those questions into a single vague judgment such as “promising target” or “hot area.”

The output must separate:
- **disease relevance**
- **mechanistic rationale**
- **druggability / tractability**
- **preclinical evidence**
- **clinical evidence**
- **competitive crowding**
- **development maturity**
- **strategic openness**

This skill is not a prescribing tool, not an investment memo, and not a substitute for direct regulatory or commercial due diligence.

---

## Reference Module Integration

The `references/` directory is not optional background material. It defines the operational rules that must be actively used while running this skill.

Use the reference modules as follows:
- `references/scope-and-input-rules.md` → use when defining whether the user is asking about a drug, target, pathway, target class, or mechanism-centered theme in **Section A**.
- `references/evidence-layer-taxonomy.md` → use when separating biology, preclinical, translational, and clinical evidence in **Sections B–D**.
- `references/druggability-and-modality-rules.md` → use when judging tractability, modality fit, and intervention logic in **Section C**.
- `references/competition-and-crowding-framework.md` → use when mapping competitor density, substitute approaches, and whitespace in **Section E**.
- `references/maturity-and-openness-framework.md` → use when assigning development maturity and strategic openness in **Sections F–G**.
- `references/literature-and-asset-verification-rules.md` → use before naming studies, trials, approvals, or company-linked assets in **Sections B–H**.
- `references/output-section-guidance.md` → use as the section-level formatting and content control standard for **Sections A–I**.
- `references/workflow-step-template.md` → use to keep the reasoning sequence aligned with the required step order.

If any output section is generated without using its corresponding reference module, the output should be treated as incomplete.

---

## Input Validation

**Valid input:** one or more of the following:
- a target in a disease context
- a drug or modality linked to a target or pathway
- a pathway-centered therapeutic area question
- a target class comparison request
- a request to assess competition or whitespace around a target
- a request to compare biological rationale versus development maturity

Optional additions:
- disease subtype or stage
- modality preference (small molecule, antibody, ADC, cell therapy, RNA, degrader, etc.)
- clinical phase interest
- translational vs mechanistic emphasis
- desired depth
- anchor papers, trials, or assets

Examples:
- “Map the evidence landscape around TIGIT in solid tumors.”
- “Assess IL-17 pathway competition and strategic whitespace in psoriasis.”
- “Compare KRAS G12D vs SHP2 as drug targets in pancreatic cancer.”
- “What is the current evidence and crowding around NLRP3 inhibition in inflammatory disease?”
- “I want a target landscape for ferroptosis-related interventions in HCC.”

**Out-of-scope — respond with the redirect below and stop:**
- patient-specific treatment selection
- dosing or prescribing advice
- requests to recommend a commercial asset as investment advice
- requests to invent pipeline data, trial status, approvals, citations, or competitor lists from memory
- requests to treat unverified assets or rumors as established facts

> “This skill maps drug, target, and pathway evidence landscapes. Your request ([restatement]) is outside that scope because it requires patient-specific treatment advice, commercial investment advice, or unverifiable asset/status claims.”

---

## Sample Triggers

- “Map the target landscape before I decide what to work on.”
- “Show me how crowded this pathway already is.”
- “Separate biology strength from real development maturity.”
- “I need a drug / target evidence and competition scan, not a general review.”
- “Tell me whether this target is biologically interesting, druggable, clinically advanced, or still strategically open.”

---

## Core Function

This skill should:
1. define the exact asset / target / pathway scope
2. identify the therapeutic use-case and disease boundary
3. separate evidence layers instead of blending them
4. assess target tractability and modality fit
5. map preclinical support and translational bridge strength
6. map clinical-stage evidence when present
7. identify competitor density and substitute approaches
8. assign development maturity and strategic openness
9. recommend the most defensible next-step interpretation

This skill should **not**:
- treat mechanistic relevance as proof of druggability
- treat preclinical activity as proof of clinical promise
- treat a crowded field as a mature field by default
- treat a sparse field as an attractive opportunity by default
- imply asset, trial, approval, or company status without verification

---

## Execution — 8 Steps (always run in order)

### Step 1 — Define Scope Precisely
Identify:
- whether the user is asking about a **drug**, **target**, **target class**, **pathway**, or **mechanism-centered intervention space**
- disease / indication / subtype / stage
- intended therapeutic use-case
- whether the user wants biology-first, druggability-first, competition-first, or translation-first emphasis

If the prompt mixes multiple scopes, explicitly narrow the dominant scope before proceeding.

### Step 2 — Retrieve and Verify Evidence Before Landscape Claims
Run literature and asset verification using `references/literature-and-asset-verification-rules.md`.

Required priority:
1. peer-reviewed biomedical literature
2. directly verifiable clinical-trial records when trials are discussed
3. directly verifiable regulatory or guideline records when approval or practice status is discussed
4. only clearly labeled secondary summaries when primary verification is unavailable

Do not present trial status, approval status, developer identity, or competitive activity as established fact without direct verification.

### Step 3 — Build the Disease-Relevance and Mechanistic Rationale Layer
Use `references/evidence-layer-taxonomy.md`.

Summarize:
- disease linkage strength
- mechanistic role in the disease process
- subtype / context specificity
- whether evidence is associative, causal-supportive, perturbational, or clinically anchored

### Step 4 — Assess Druggability and Modality Fit
Use `references/druggability-and-modality-rules.md`.

Evaluate:
- whether the target appears therapeutically tractable
- what intervention modes are plausible
- whether the biology fits inhibition, activation, degradation, blocking, delivery, or cell-based strategies
- major tractability barriers

### Step 5 — Separate Preclinical, Translational, and Clinical Evidence
Use `references/evidence-layer-taxonomy.md`.

Map separately:
- preclinical efficacy evidence
- translational biomarker / pharmacology / patient-selection bridge
- clinical evidence, if any
- where the evidence chain is strong, thin, broken, or contradictory

### Step 6 — Map Competition and Substitute Approaches
Use `references/competition-and-crowding-framework.md`.

Must include:
- same-target competition
- same-pathway competition
- modality competition
- substitute mechanism competition
- whether the space is open, moderately crowded, or heavily crowded

### Step 7 — Assign Development Maturity and Strategic Openness
Use `references/maturity-and-openness-framework.md`.

Distinguish:
- biologically compelling but underdeveloped
- tractable but weakly disease-anchored
- clinically advancing but crowded
- differentiated but evidence-thin
- strategically open vs operationally difficult

### Step 8 — Perform Self-Critical Review
Before finalizing, explicitly check:
- strongest evidence-supported layer
- weakest or most assumption-dependent layer
- most likely overinterpretation risk
- biggest verification gap
- biggest competition-mapping uncertainty
- fallback interpretation if the most optimistic reading collapses

---

## Mandatory Output Structure

### A. Scope Framing
Define the exact landscape boundary, intended therapeutic question, disease scope, and assumptions.

### B. Disease Relevance and Mechanistic Rationale
Must separate:
- biological relevance
- mechanistic support type
- disease-context specificity
- strength and limitations of the disease-link evidence

### C. Druggability / Modality Fit
State:
- whether the target/pathway appears tractable
- what modalities fit best
- what the main tractability barriers are
- what would make the target easier or harder to intervene on

### D. Evidence Layer Map
Separate clearly:
- preclinical evidence
- translational bridge evidence
- clinical evidence
- missing evidence links

### E. Competition and Crowding Map
Include:
- same-target competitors
- same-pathway competitors
- substitute therapeutic approaches
- crowding level
- likely differentiation pressure

### F. Development Maturity Summary
Assign a maturity judgment using `references/maturity-and-openness-framework.md`.

### G. Strategic Openness / Whitespace
Explain where the remaining opportunity might still be, and whether that opportunity is scientific, translational, technical, or positioning-based.

### H. Primary Recommended Interpretation
Recommend one best overall reading of the landscape and explain why it is the most defensible conclusion.

### I. Retrieved and Verified References / Asset Notes
Use the verification rules in `references/literature-and-asset-verification-rules.md`.

Formal references, trials, approvals, and company-linked asset statements may appear only when core metadata has been directly verified.

---

## Hard Rules

1. Separate target relevance from druggability every time.
2. Separate preclinical evidence from clinical evidence every time.
3. Separate competition intensity from development maturity every time.
4. Do not present a biologically interesting target as therapeutically actionable unless the tractability logic is explicit.
5. Do not present a tractable target as disease-relevant unless the disease-link evidence is explicit.
6. Do not treat preclinical activity as proof of patient benefit.
7. Do not treat sparse competition as proof of strategic attractiveness.
8. Do not treat a crowded field as automatically closed without checking differentiation logic.
9. Never fabricate references, PMIDs, DOIs, trial identifiers, approval status, company activity, asset stage, or study findings.
10. Never present vague memory, field lore, or rumor as verified evidence.
11. If metadata or status cannot be verified, do not present the item as a formal citation or established asset fact.
12. If evidence is mixed, thin, indirect, or context-specific, downgrade the confidence of the conclusion.
13. When giving a primary interpretation, state clearly whether the limiting factor is biology, tractability, translation, competition, or verification uncertainty.

---

## What This Skill Should Not Do

Do not:
- write a generic pathway review
- recommend a therapy for an individual patient
- turn interesting mechanism papers into implied drug-development proof
- describe “promising target” without specifying why
- blur competitive rumor with verified landscape mapping
- describe trial or approval progress without direct verification
- hide uncertainty behind polished strategic language

---

## Quality Standard

A high-quality output from this skill should feel like an **evidence-grounded target landscape audit**, not a hype memo.

The user should be able to see:
- how strong the disease relevance really is,
- whether the target is truly tractable,
- where the evidence chain is solid versus weak,
- how crowded the space actually is,
- and whether any real strategic opening still remains.
