# Technical Documentation (Art. 11 + Annex IV)

## Purpose

Article 11 requires technical documentation sufficient to demonstrate that the high-risk AI system complies with the applicable requirements. Annex IV gives the practical content backbone.

The operative question is simple:

**If an authority, assessor, or internal reviewer asked for the technical file tomorrow, could the organization produce one that explains the system end-to-end without guesswork?**

If not, this area is not GREEN.

---

## What should be documented

A workable Annex IV-style file should generally cover:
- general description of the system
- intended purpose and user/deployer context
- version identification and configuration baseline
- design specifications and architecture
- development process and methodology
- model logic / system logic at a level appropriate to the technology
- data used for training/validation/testing where relevant
- performance metrics and validation results
- risk management measures
- human oversight measures
- logging and monitoring capabilities
- cybersecurity and robustness measures
- limitations, assumptions, and known failure modes
- change history / version control
- instructions or references to deployer-facing information

---

## Practical file structure

### Section 1 - System identity
- system name
- version/build
- legal entity/provider
- internal owner
- release date/status

### Section 2 - Intended purpose and scope
- use case
- what decisions or outputs it influences
- target users/deployers
- in-scope/out-of-scope usage
- operating environment and assumptions

### Section 3 - Architecture and components
- system overview
- data flow diagram
- model/component description
- external dependencies and suppliers
- interfaces with other systems

### Section 4 - Development and change methodology
- development lifecycle overview
- testing/validation approach
- release process
- change control logic
- retraining/update logic where relevant

### Section 5 - Data and validation basis
- training/validation/testing datasets or alternative system basis
- suitability rationale
- quality and bias examination summary
- known limitations of the data basis

### Section 6 - Performance and limitations
- accuracy/performance metrics
- robustness and stress testing summary
- subgroup or context limitations where relevant
- conditions under which the system should not be relied on

### Section 7 - Risk management and controls
- main identified risks
- key control measures
- residual risk position
- links to risk register and validation artifacts

### Section 8 - Human oversight, logging, and monitoring
- oversight design
- operator/deployer responsibilities
- logging capabilities
- post-market monitoring capabilities and interfaces

### Section 9 - Cybersecurity and resilience
- relevant threat assumptions
- security measures
- vulnerability management and testing summary

### Section 10 - Document control
- version history
- approvers
- linked annexes/artifacts

---

## Readiness scoring guide

### RED
- no consolidated technical file exists
- documentation is fragmented across slides, tickets, and engineers’ heads
- versioning and intended purpose unclear
- no clear explanation of system limits or control environment

### AMBER
- substantial documentation exists, but not in an Annex IV-ready structure
- key sections incomplete or outdated
- technical details exist without compliance framing
- links to risk management, data governance, or validation are weak

### GREEN
- a current, structured technical file exists
- intended purpose, architecture, risk controls, data basis, validation, limitations, and monitoring are documented clearly
- version control and evidence links are maintained
- the file can realistically support conformity assessment and regulatory review

---

## Common pitfalls

### 1. Confusing product docs with compliance documentation
Engineering docs help, but they often omit intended purpose boundaries, compliance rationale, and evidence traceability.

### 2. No defined intended purpose
Without a precise intended purpose, the rest of the technical file floats.

### 3. No limitations section
Every meaningful system has assumptions and limits. If none are documented, the file looks immature or defensive.

### 4. No change history
Without version/change tracking, it is hard to prove what was assessed and released.

### 5. No document owner
A technical file without an owner decays fast.

---

## Practical Annex IV checklist

Confirm whether the file answers the following:
- What is the system and who provides it?
- What is it intended to do, and in what context?
- What data, logic, and components support it?
- How was it developed and validated?
- What performance and robustness evidence exists?
- What are its limitations and failure conditions?
- What human oversight is required?
- What logs and monitoring exist?
- What risks were identified and how are they controlled?
- What changed over time?

If several answers are “spread across different teams and not assembled,” the documentation is not ready.

---

## Practical next steps

### If RED
1. Name a document owner
2. Create an Annex IV-aligned structure
3. Gather core system, data, test, and risk artifacts
4. Draft intended purpose and limitations first
5. Build version-controlled document governance

### If AMBER
1. Fill gaps in oversight, logging, and monitoring sections
2. Strengthen links to evidence and annexes
3. Add missing change history and control narrative
4. Make limitations and assumptions explicit
5. Review for assessor readability, not just technical accuracy

---

## What assessors will care about

They usually want to see that the file is:
- coherent
- current
- traceable
- understandable by someone other than the original engineers
- able to demonstrate compliance, not merely system existence

That is what makes technical documentation useful under Art. 11 and Annex IV.
