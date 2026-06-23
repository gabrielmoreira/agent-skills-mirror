# Risk Management System (Art. 9)

## Purpose

Article 9 requires providers of high-risk AI systems to establish, implement, document, and maintain a **risk management system** as a continuous lifecycle process. This is not a one-time risk memo. It must operate from design and development through deployment, post-market monitoring, change management, and corrective action.

For practical readiness, ask one question: **Can the organization show a repeatable process for identifying, evaluating, mitigating, testing, and revisiting AI-specific risks?**

If not, readiness is usually RED or AMBER.

---

## What Article 9 requires in practice

A workable Art. 9 system should cover at least:

1. **Risk identification**
   - known risks
   - reasonably foreseeable risks
   - misuse and foreseeable misuse
   - lifecycle risks, not just model performance risks

2. **Risk analysis and evaluation**
   - likelihood and severity logic
   - affected persons/groups
   - conditions that increase risk
   - special attention to fundamental rights and safety impacts where relevant

3. **Risk treatment / control measures**
   - product/design controls
   - data controls
   - workflow and organizational controls
   - human oversight controls
   - documentation, warnings, and use restrictions

4. **Residual risk evaluation**
   - what remains after controls
   - whether residual risk is acceptable
   - who signs off

5. **Testing and verification**
   - testing linked to identified risks
   - validation of control effectiveness
   - edge cases and foreseeable operating conditions

6. **Continuous updating**
   - incidents, drift, complaints, monitoring findings, and changes feed back into risk decisions

---

## Minimum evidence package

A practical evidence set often includes:
- AI risk management policy or procedure
- system-specific risk register
- harm/scenario inventory
- likelihood/severity methodology
- control library or control mapping
- residual risk assessment record
- validation/test plans linked to risks
- approval/sign-off record
- update log showing periodic review

If the organization says “we discuss risks in meetings,” that is not enough.

---

## Suggested implementation structure

### 1. Create an AI system risk file
For each high-risk system, maintain a dedicated file containing:
- intended purpose
- system boundaries
- user/deployer assumptions
- affected stakeholders
- risk scenarios
- controls
- residual risk decisions
- links to tests and incidents

### 2. Build a risk taxonomy
Use practical categories such as:
- performance / error risk
- bias / discrimination risk
- explainability / interpretability risk
- human factors / automation bias risk
- data quality risk
- cybersecurity / adversarial risk
- logging / traceability risk
- misuse / scope creep risk
- third-party dependency risk
- regulatory / documentation risk

### 3. Use scenario-based risk identification
Don’t write abstract risk bullets only. Use scenarios:
- “False negative in applicant screening causes unjust exclusion.”
- “Operator over-relies on score despite conflicting underlying evidence.”
- “Model performance degrades in a new geography or subgroup.”
- “Prompt/input manipulation triggers unsafe or non-compliant outputs.”

### 4. Tie every material risk to one or more controls
For each risk, specify:
- control description
- control type: preventive / detective / corrective
- owner
- evidence source
- test method
- residual risk result

### 5. Create a review cadence
Recommended minimum triggers:
- before release / market placement
- after major model or workflow changes
- after serious incidents or near misses
- after post-market review cycles
- after material vendor dependency changes

---

## Readiness scoring guide

### RED
- no AI-specific risk process
- no system-level risk register
- risks discussed informally only
- no defined acceptance criteria or residual risk decision logic
- testing not linked to identified risks

### AMBER
- risk register exists but incomplete or static
- some risks documented, but controls/evidence weak
- reviews happen, but not on defined triggers
- residual risk language exists, but sign-off unclear
- testing partly mapped to risks

### GREEN
- risk management is lifecycle-based and documented
- system-specific risk register exists and is current
- controls are assigned and evidenced
- testing validates risk controls
- incidents and monitoring findings feed back into the register

---

## Common pitfalls

### 1. Treating information security risk as the whole answer
A security risk register alone is insufficient. Art. 9 is broader and includes performance, misuse, bias, oversight, and operational harm.

### 2. Keeping the risk register too generic
“Bias risk,” “security risk,” “privacy risk” is too abstract. Risks must be system-specific enough to drive controls and testing.

### 3. No residual risk decision
If every risk is marked “mitigated” without saying what remains, the process is not credible.

### 4. No link to testing
If the risk register and validation reports never meet, the system is likely not defensible.

### 5. No update loop
If post-market issues do not feed back into risk management, the lifecycle element is missing.

---

## Practical next steps to move from RED to GREEN

### If RED
1. Appoint an accountable owner
2. Create a system-specific risk register template
3. Run a structured cross-functional workshop
4. Document top risk scenarios, controls, and evidence
5. Define residual risk approval logic
6. Map risks to testing activities

### If AMBER
1. Add missing risk scenarios and affected groups
2. Tighten control ownership and evidence links
3. Add update triggers and review cadence
4. Integrate incidents and monitoring data
5. Require sign-off before release and major changes

---

## Practical output template

For each risk, document:
- Risk ID
- Risk scenario
- Trigger/condition
- Affected person/group
- Potential harm
- Likelihood
- Severity
- Control(s)
- Evidence
- Validation method
- Residual risk
- Owner
- Review date

---

## What a conformity assessor will care about

They will usually want to see that:
- the process is real, not retrospective window dressing
- risks are tied to the actual intended purpose and operating conditions
- controls are not only technical but also operational where needed
- residual risks are consciously evaluated
- monitoring results and incidents change the system over time

That is the practical heart of Art. 9.
