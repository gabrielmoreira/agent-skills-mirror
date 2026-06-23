# Quality Management System (Art. 17)

## Purpose

Article 17 requires providers of high-risk AI systems to put in place a **quality management system** in documented form. In practice, this is the governance backbone that keeps all the other obligations from becoming disconnected paperwork.

The core question is:

**Is there a documented management system that assigns responsibilities, controls lifecycle changes, governs evidence, and ensures the system remains compliant after launch?**

---

## What a practical AI Act QMS should cover

A useful Art. 17 QMS often includes these building blocks:

1. **Governance and accountability**
   - roles and responsibilities
   - approval authorities
   - escalation lines

2. **Design and development controls**
   - lifecycle stages
   - reviews and gates
   - validation and release approvals

3. **Data and model/system controls**
   - data governance
   - testing standards
   - retraining/change controls

4. **Documentation and record control**
   - document ownership
   - versioning
   - retention
   - traceability to evidence

5. **Supplier and third-party management**
   - vendor due diligence
   - dependency mapping
   - documentation requirements from suppliers

6. **Incident, nonconformity, and corrective action processes**
   - issue intake
   - root cause analysis
   - corrective and preventive action

7. **Post-market monitoring**
   - monitoring plan ownership
   - review cadence
   - integration with risk management

8. **Authority and external communication readiness**
   - who communicates with authorities
   - who owns registrations, incident reporting, and assessment coordination

9. **Competence and training**
   - training requirements for builders, reviewers, operators, and oversight personnel

---

## Relationship to existing management systems

Many organizations already have ISO-style or regulated management systems. That helps, but the key readiness question is whether those systems have been **adapted for AI-specific obligations**.

A mature baseline in ISO 9001, ISO 27001, medical device QMS, automotive quality, or internal SDLC governance can accelerate readiness - but it does not automatically satisfy Art. 17.

You still need AI-specific controls for:
- intended purpose boundaries
- data governance
- AI risk management
- human oversight
- model/system change effects
- logging and traceability
- post-market AI performance issues

---

## Readiness scoring guide

### RED
- no documented QMS for the high-risk system
- responsibilities unclear
- lifecycle gates informal
- evidence scattered and unmanaged
- no defined incident/corrective action process for the AI system

### AMBER
- strong general management system exists, but AI-specific adaptation incomplete
- some procedures documented, but ownership and integration patchy
- supplier/change/post-market controls not fully connected
- records exist, but not consistently controlled

### GREEN
- documented QMS exists and is applied to the high-risk AI lifecycle
- roles, procedures, approvals, and records are defined
- AI-specific controls are embedded
- incidents, changes, monitoring, and authority-facing steps are governed
- evidence can be produced consistently

---

## Suggested QMS document set

A practical minimum set may include:
- QMS manual / overview
- governance and role matrix
- design and development procedure
- validation/testing procedure
- data governance procedure
- change control procedure
- documentation and records control procedure
- supplier management procedure
- incident/CAPA procedure
- post-market monitoring procedure
- conformity assessment / registration procedure
- training and competence procedure

---

## Common pitfalls

### 1. Treating the QMS as a document dump
A folder of policies without operating mechanisms is not a functioning QMS.

### 2. No owner with authority
If nobody can stop release, require corrective action, or enforce evidence quality, the system is weak.

### 3. Weak supplier governance
Where models, datasets, APIs, or components come from third parties, missing supplier controls can become a major audit problem.

### 4. No change discipline
If major updates happen through ordinary product release without specific AI impact assessment, conformity assumptions can break quickly.

### 5. Post-market monitoring not integrated
Monitoring cannot sit in a separate deck; it must feed into risk, corrective action, and documentation.

---

## Practical next steps

### If RED
1. Name an accountable QMS owner
2. Define the minimum AI lifecycle procedures
3. Create a role matrix and release/control gates
4. Establish document control rules
5. Set up incident and corrective action workflow

### If AMBER
1. Map existing quality processes against Art. 17 requirements
2. Add missing AI-specific procedures
3. Tighten supplier/change/post-market governance
4. Link records to the technical file and risk management
5. Test the system through a mock evidence request

---

## Practical role model

Common owner model:
- Product/AI owner - system scope and release
- Compliance/legal - regulatory interpretation and documentation review
- Engineering/ML - technical evidence and controls
- Security - cybersecurity and vulnerability management
- Operations - live monitoring and incident intake
- Quality/compliance program owner - QMS integrity and readiness tracking

---

## What assessors will care about

They usually want to see that:
- responsibilities are real and assigned
- procedures are written and followed
- records are controlled
- changes are governed
- issues lead to corrective action
- the system remains compliant over time, not only at launch

That is the operational heart of Art. 17.
