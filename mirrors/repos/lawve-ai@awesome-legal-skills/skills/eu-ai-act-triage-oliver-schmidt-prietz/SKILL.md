---
name: eu-ai-act-triage-oliver-schmidt-prietz
description: |
  Fast 15-25 minute triage for preliminary EU AI Act classification and compliance assessment. This skill should be used when the user asks to "do a quick AI Act assessment", "check if the AI Act applies to us", "run a preliminary classification", "do an AI Act triage", "quick check", "preliminary assessment", "Schnellprüfung", "Ersteinschätzung", or needs a fast initial assessment before committing to full analysis.
metadata:
  author: Oliver Schmidt-Prietz
  license: AGPL-3.0
  version: 2026.03.16
---

# EU AI Act Quick Assessment

Fast triage tool (15-25 minutes) for preliminary AI Act classification and compliance assessment. Produces a preliminary output and routes to detailed skills for full analysis.

## LEGAL DISCLAIMER

> **IMPORTANT NOTICE**
> This is a **preliminary assessment** providing initial orientation under the EU AI Act (Regulation (EU) 2024/1689). It is designed for rapid triage and does NOT replace a full assessment. Results should be validated using the detailed assessment skills (/ai-act-classifier, /ai-act-roles, /ai-act-obligations, /ai-act-report) and reviewed by qualified legal counsel.
>
> **Do you acknowledge this and wish to proceed with the quick assessment?**

Wait for acknowledgment before proceeding.

---

## When to Search the Web

**On activation — search for:**
```
EU AI Act latest enforcement updates [current year]
EU AI Act Commission guidelines status [current year]
```

---

## Quick Assessment Workflow

### Phase 1: Quick Context (Adaptive 2-Batch Flow)

Gather context through a conversational 2-batch approach. Maximum 2 interaction turns — 1 if the user is detailed, 2 if gaps remain.

#### Batch 1: Essential Questions (always asked)

Present these three questions with a natural, conversational welcome:

> **Let's get started with a quick EU AI Act assessment.**
>
> You can answer in your own words — a short paragraph, bullet points, whatever works. I'll ask follow-up questions only if I need more detail.
>
> **1. What does the AI system do?** (2-3 sentences: what it does, how it works at a high level, what outputs it produces)
>
> **2. Where is the system deployed?** (For reference: EU/EEA market, Switzerland with EU reach, outside EU but outputs used in EU, or no EU connection)
>
> **3. What is your organization's relationship to it?** (For reference: developed in-house, purchased/licensed, modified/finetuned, distribute/import, or evaluating for acquisition)

#### Coverage Analysis (internal — not shown to user)

After the user responds to Batch 1, silently check whether their answer covers each of the 8 required fields. Be generous with extraction — e.g., "German Mittelstand" covers both jurisdiction (DE) and organization size (medium); "CV screening tool" covers sector (HR/employment) and affected persons (employees/job applicants).

| # | Field | Extract from |
|---|-------|-------------|
| 1 | System description | Batch 1 Q1 |
| 2 | Deployment context | Batch 1 Q2 |
| 3 | Organization role | Batch 1 Q3 |
| 4 | Sector | Often inferable from system description |
| 5 | Affected persons | Often inferable from system description + sector |
| 6 | Modifications | Often inferable from organization role |
| 7 | Organization size | Sometimes mentioned in context |
| 8 | Jurisdiction(s) | Often inferable from deployment context |

Mark each field: **Covered** / **Partially covered** / **Not covered**.

#### Batch 2: Adaptive Follow-Up (only if gaps remain)

- **All 8 fields covered** → Skip Batch 2. Briefly confirm your extractions and proceed to Phase 2.
- **Gaps remain** → Send ONE follow-up message covering ONLY the missing or partially covered fields, conversationally framed. Do not re-ask what was already answered.
- **Partially covered fields** → Use confirmation prompts, not full re-asks. Example: "You mentioned healthcare — is this specifically in the medical devices sector?"
- **Unclear fields** → If still unresolvable after Batch 2, mark as `[UNCLEAR — proceeding with cautious assumptions]` and note the assumption made.

Example follow-up (if sector, size, and jurisdiction are missing):
> **Just a few more details to round out the picture:**
>
> - What sector does this fall into? (e.g., healthcare, financial services, HR/employment, education, public administration, other)
> - Roughly how large is your organization? (e.g., under 50 employees, 50-249, or 250+)
> - Which EU/EEA country or countries are involved?

#### Information Normalization (internal — before Phase 2)

Before proceeding to Phase 2, normalize all gathered information into the structured 8-field format so the Phase 2 gate sequence can reference fields consistently:

1. **System description** — free text
2. **Deployment context** — one of: EU/EEA market, Switzerland with EU reach, Outside EU but outputs used in EU, No EU connection
3. **Organization role** — one of: Developed in-house, Purchased/licensed, Modified/finetuned, Distribute/import, Evaluating
4. **Sector** — mapped to: Healthcare/medical devices, Financial services, HR/employment, Education, Law enforcement/justice, Critical infrastructure, Public administration, Consumer/retail, Other
5. **Affected persons** — one or more of: Employees/workers, Customers/consumers, Citizens/public, Students, Patients, Internal only
6. **Modifications** — one of: No modifications, Configuration within intended range, Finetuning/retraining, Changed intended purpose, Own brand applied
7. **Organization size** — one of: Micro (<10), Small (10-49), Medium (50-249), Large (250+)
8. **Jurisdiction(s)** — list of EU/EEA Member States or Switzerland

---

### Phase 2: Rapid Classification (6-Step Gate Sequence)

Read [references/quick-decision-tree.md](references/quick-decision-tree.md) for the condensed classification logic.

Process the answers through the 6-step gate sequence **internally** (do not ask additional questions unless critical information is missing). Output the result as a single assessment.

**Gate 1: Scope Check (Art. 2)**
- If deployment context is "No EU connection" → likely out of scope → note and proceed cautiously
- Check for military, personal use, pure R&D exclusions based on system description

**Gate 2: AI System Test (Art. 3(1))**
- Quick determination based on system description
- Apply simplified 3-question test: (1) machine-based? (2) infers/generates beyond rules? (3) influences environment?

**Gate 3: Prohibited Practice Screen (Art. 5)**
- Rapid screen based on system description and sector
- Flag any potential Art. 5 concern for detailed review

**Gate 4: High-Risk Assessment (Annex I + III)**
- Map sector + use case to Annex I/III categories
- Use sector answer as primary trigger indicator
- If Annex III triggered: quick Art. 6(3) exception check

**Gate 5: GPAI Check**
- Based on system description: does it use a general-purpose AI model?
- If yes: note GPAI obligations

**Gate 6: Transparency Triggers (Art. 50)**
- Check for direct human interaction, synthetic content generation, emotion recognition, deep fakes

---

### Phase 3: Preliminary Output

Generate a consolidated preliminary assessment using the following structure:

```markdown
## AI Act Quick Assessment — PRELIMINARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠ PRELIMINARY ASSESSMENT — Full analysis required for compliance decisions
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

System:           [name/description]
Date:             [date]
Assessment Type:  PRELIMINARY (Quick Assessment)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CLASSIFICATION SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AI System (Art. 3(1)):     [Likely YES / Likely NO / Unclear — full test needed]
Scope (Art. 2):            [In scope / Likely excluded — Art. 2(x)]
Risk Tier:                 [Likely Prohibited / Likely High-Risk / Likely GPAI / Likely Limited / Likely Minimal / Unclear]
Classification Basis:      [Likely Art. 5(1)(x) / Likely Annex III Nr. X / Likely Art. 50 / Likely minimal]
Confidence:                [High / Medium / Low]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ROLE ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Likely Role:               [Provider / Deployer / Quasi-Provider / Importer / Distributor]
Quasi-Provider Risk:       [None / Possible — [trigger]]
Key Concern:               [if any — e.g., finetuning may trigger Art. 25]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOP OBLIGATIONS (if high-risk or GPAI)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
| # | Obligation | Article | Urgency | Effort Estimate |
|---|-----------|---------|---------|-----------------|
| 1 | [top obligation] | [Art. X] | [Immediate/Short-term/Ongoing] | [Low/Medium/High] |
| 2 | [second obligation] | [Art. X] | [Immediate/Short-term/Ongoing] | [Low/Medium/High] |
| 3 | [third obligation] | [Art. X] | [Immediate/Short-term/Ongoing] | [Low/Medium/High] |
| 4 | [fourth obligation] | [Art. X] | [Immediate/Short-term/Ongoing] | [Low/Medium/High] |
| 5 | [fifth obligation] | [Art. X] | [Immediate/Short-term/Ongoing] | [Low/Medium/High] |

For ALL risk tiers:
| - | AI competence (Art. 4) | Art. 4 | Immediate (since Feb 2025) | Low-Medium |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMPLIANCE TIMELINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Applicable Deadline:       [2 Feb 2025 / 2 Aug 2025 / 2 Aug 2026 / 2 Aug 2027]
Days Remaining:            [X days]
Urgency:                   [OVERDUE / CRITICAL / HIGH / MEDIUM / LOW]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
JURISDICTION FLAGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Jurisdiction-specific flags based on deployment country, e.g.:]
[DE: Works council co-determination likely required (BetrVG §87)]
[FR: CSE consultation required before deployment]
[Finance sector: BaFin/[regulator] AI model governance requirements apply]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FINANCIAL EXPOSURE (PRELIMINARY)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Maximum penalty:           [EUR XM or X% turnover — Art. 99(X)]
SME proportionality:       [Applies / Does not apply]
Penalty tier:              [Tier 1/2/3]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FLAGS & WARNINGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[List any flags, e.g.:]
[PROHIBITED PRACTICE RISK — Art. 5(1)(x) — immediate legal review required]
[QUASI-PROVIDER RISK — finetuning may trigger Art. 25]
[PROFILING DETECTED — may affect Art. 6(3) exception]
[GDPR OVERLAP — DPIA likely required under Art. 35 GDPR]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ASSESSMENT CONTEXT (paste into next skill)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
System: [name]
Classification: [risk tier]
Basis: [legal basis]
Role: [role]
Quasi-Provider: [risk level]
Sector: [sector]
Jurisdiction: [list]
Org Size: [size]
Art. 50: [applicable triggers]
GPAI: [yes/no, systemic risk]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RECOMMENDED NEXT STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. → Run /ai-act-classifier for full classification with documented reasoning
   [Priority: HIGH / MEDIUM — based on preliminary findings]

2. → Run /ai-act-roles for detailed role determination
   [Priority: HIGH if quasi-provider risk detected / MEDIUM otherwise]

3. → Run /ai-act-obligations for complete obligation mapping with RACI
   [Priority: HIGH if high-risk / MEDIUM if limited risk]

4. → Run /ai-act-report to generate formal assessment documentation
   [Priority: HIGH for regulatory files / MEDIUM for internal tracking]

5. → Engage legal counsel for:
   [List specific areas requiring legal judgment]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠ This preliminary assessment was generated using the AI Act Quick
  Assessment tool. It provides directional guidance only. All
  determinations marked "Likely" require validation through the
  detailed assessment skills listed above.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### Phase 4: Template Offer (Optional)

After presenting the preliminary assessment, offer:

> "Would you like me to generate a preliminary version of any of the following templates? These will be marked as preliminary and should be finalized after running the full assessment skills."
>
> 1. **Classification Record (Prüfprotokoll)** — preliminary audit trail
> 2. **Compliance Register Entry** — preliminary obligation tracker
> 3. **Management Briefing (Entscheidungsvorlage)** — preliminary decision document

If requested, use the templates from [/ai-act-report/references/output-templates.md] and mark all outputs prominently as "PRELIMINARY — Full assessment recommended."

---

## Critical Reminders

1. **This is a triage tool** — always recommend running detailed skills for compliance decisions
2. **"Likely" is not "confirmed"** — preliminary determinations require validation
3. **Err on the side of caution** — if uncertain between risk tiers, flag the higher risk tier as possible
4. **Flag uncertainty explicitly** — Low confidence ratings require immediate follow-up with detailed skills
5. **National requirements matter** — always flag jurisdiction-specific obligations using [references/jurisdiction-flags.md]
6. **Compliance timeline** — reference [references/compliance-deadlines.md] for deadline urgency
7. **Enforcement exposure** — reference [/ai-act-classifier/references/enforcement-framework.md] for penalty context
