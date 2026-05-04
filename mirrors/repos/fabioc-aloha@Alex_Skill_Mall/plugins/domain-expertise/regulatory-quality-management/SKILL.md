---
type: skill
lifecycle: stable
inheritance: inheritable
name: capa-officer
description: CAPA system management for medical device QMS. Covers root cause analysis, corrective action planning, effectiveness verification, and CAPA metrics. Use for CAPA investigations, 5-Why analysis, fis...
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# CAPA Officer

Corrective and Preventive Action (CAPA) management within Quality Management Systems, focusing on systematic root cause analysis, action implementation, and effectiveness verification.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-1
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## CAPA Investigation Workflow

Conduct systematic CAPA investigation from initiation through closure:

1. Document trigger event with objective evidence
2. Assess significance and determine CAPA necessity
3. Form investigation team with relevant expertise
4. Collect data and evidence systematically
5. Select and apply appropriate RCA methodology
6. Identify root cause(s) with supporting evidence
7. Develop corrective and preventive actions
8. **Validation:** Root cause explains all symptoms; if eliminated, problem would not recur

### CAPA Necessity Determination

| Trigger Type | CAPA Required | Criteria |
|--------------|---------------|----------|
| Customer complaint (safety) | Yes | Any complaint involving patient/user safety |
| Customer complaint (quality) | Evaluate | Based on severity and frequency |
| Internal audit finding (Major) | Yes | Systematic failure or absence of element |
| Internal audit finding (Minor) | Recommended | Isolated lapse or partial implementation |
| Nonconformance (recurring) | Yes | Same NC type occurring 3+ times |
| Nonconformance (isolated) | Evaluate | Based on severity and risk |
| External audit finding | Yes | All Major and Minor findings |
| Trend analysis | Evaluate | Based on trend significance |

### Investigation Team Composition

| CAPA Severity | Required Team Members |
|---------------|----------------------|
| Critical | CAPA Officer, Process Owner, QA Manager, Subject Matter Expert, Management Rep |
| Major | CAPA Officer, Process Owner, Subject Matter Expert |
| Minor | CAPA Officer, Process Owner |

### Evidence Collection Checklist

- [ ] Problem description with specific details (what, where, when, who, how much)
- [ ] Timeline of events leading to issue
- [ ] Relevant records and documentation
- [ ] Interview notes from involved personnel
- [ ] Photos or physical evidence (if applicable)
- [ ] Related complaints, NCs, or previous CAPAs
- [ ] Process parameters and specifications

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-2
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Corrective Action Planning

Develop effective actions addressing identified root causes:

1. Define immediate containment actions
2. Develop corrective actions targeting root cause
3. Identify preventive actions for similar processes
4. Assign responsibilities and resources
5. Establish timeline with milestones
6. Define success criteria and verification method
7. Document in CAPA action plan
8. **Validation:** Actions directly address root cause; success criteria are measurable

### Action Types

| Type | Purpose | Timeline | Example |
|------|---------|----------|---------|
| Containment | Stop immediate impact | 24-72 hours | Quarantine affected product |
| Correction | Fix the specific occurrence | 1-2 weeks | Rework or replace affected items |
| Corrective | Eliminate root cause | 30-90 days | Revise procedure, add controls |
| Preventive | Prevent in other areas | 60-120 days | Extend solution to similar processes |

### Action Plan Components

```
ACTION PLAN TEMPLATE

CAPA Number: [CAPA-XXXX]
Root Cause: [Identified root cause]

ACTION 1: [Specific action description]
- Type: [ ] Containment [ ] Correction [ ] Corrective [ ] Preventive
- Responsible: [Name, Title]
- Due Date: [YYYY-MM-DD]
- Resources: [Required resources]
- Success Criteria: [Measurable outcome]
- Verification Method: [How success will be verified]

ACTION 2: [Specific action description]
...

IMPLEMENTATION TIMELINE:
Week 1: [Milestone]
Week 2: [Milestone]
Week 4: [Milestone]
Week 8: [Milestone]

APPROVAL:
CAPA Owner: _____________ Date: _______
Process Owner: _____________ Date: _______
QA Manager: _____________ Date: _______
```

### Action Effectiveness Indicators

| Indicator | Target | Red Flag |
|-----------|--------|----------|
| Action scope | Addresses root cause completely | Treats only symptoms |
| Specificity | Measurable deliverables | Vague commitments |
| Timeline | Aggressive but achievable | No due dates or unrealistic |
| Resources | Identified and allocated | Not specified |
| Sustainability | Permanent solution | Temporary fix |

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-3
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## CAPA Metrics and Reporting

Monitor CAPA program performance through key indicators.

### Key Performance Indicators

| Metric | Target | Calculation |
|--------|--------|-------------|
| CAPA cycle time | <60 days average | (Close Date - Open Date) / Number of CAPAs |
| Overdue rate | <10% | Overdue CAPAs / Total Open CAPAs |
| First-time effectiveness | >90% | Effective on first verification / Total verified |
| Recurrence rate | <5% | Recurred issues / Total closed CAPAs |
| Investigation quality | 100% root cause validated | Root causes validated / Total CAPAs |

### Aging Analysis Categories

| Age Bucket | Status | Action Required |
|------------|--------|-----------------|
| 0-30 days | On track | Monitor progress |
| 31-60 days | Monitor | Review for delays |
| 61-90 days | Warning | Escalate to management |
| >90 days | Critical | Management intervention required |

### Management Review Inputs

Monthly CAPA status report includes:
- Open CAPA count by severity and status
- Overdue CAPA list with owners
- Cycle time trends
- Effectiveness rate trends
- Source analysis (complaints, audits, NCs)
- Recommendations for improvement

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-4
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Tools

### CAPA Tracker

```bash
# Generate CAPA status report
python scripts/capa_tracker.py --capas capas.json

# Interactive mode for manual entry
python scripts/capa_tracker.py --interactive

# JSON output for integration
python scripts/capa_tracker.py --capas capas.json --output json

# Generate sample data file
python scripts/capa_tracker.py --sample > sample_capas.json
```

Calculates and reports:
- Summary metrics (open, closed, overdue, cycle time, effectiveness)
- Status distribution
- Severity and source analysis
- Aging report by time bucket
- Overdue CAPA list
- Actionable recommendations

### Sample CAPA Input

```json
{
  "capas": [
    {
      "capa_number": "CAPA-2024-001",
      "title": "Calibration overdue for pH meter",
      "description": "pH meter EQ-042 found 2 months overdue",
      "source": "AUDIT",
      "severity": "MAJOR",
      "status": "VERIFICATION",
      "open_date": "2024-06-15",
      "target_date": "2024-08-15",
      "owner": "J. Smith",
      "root_cause": "Procedure review gap",
      "corrective_action": "Updated SOP-EQ-001"
    }
  ]
}
```

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-5
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

---
type: skill
lifecycle: stable
inheritance: inheritable
name: fda-consultant-specialist
description: FDA regulatory consultant for medical device companies. Provides 510(k)/PMA/De Novo pathway guidance, QSR (21 CFR 820) compliance, HIPAA assessments, and device cybersecurity. Use when user mention...
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# FDA Consultant Specialist

FDA regulatory consulting for medical device manufacturers covering submission pathways, Quality System Regulation (QSR), HIPAA compliance, and device cybersecurity requirements.

## Table of Contents

- [FDA Pathway Selection](#fda-pathway-selection)
- [510(k) Submission Process](#510k-submission-process)
- [QSR Compliance](#qsr-compliance)
- [HIPAA for Medical Devices](#hipaa-for-medical-devices)
- [Device Cybersecurity](#device-cybersecurity)
- [Resources](#resources)

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-7
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## 510(k) Submission Process

### Workflow

```
Phase 1: Planning
├── Step 1: Identify predicate device(s)
├── Step 2: Compare intended use and technology
├── Step 3: Determine testing requirements
└── Checkpoint: SE argument feasible?

Phase 2: Preparation
├── Step 4: Complete performance testing
├── Step 5: Prepare device description
├── Step 6: Document SE comparison
├── Step 7: Finalize labeling
└── Checkpoint: All required sections complete?

Phase 3: Submission
├── Step 8: Assemble submission package
├── Step 9: Submit via eSTAR
├── Step 10: Track acknowledgment
└── Checkpoint: Submission accepted?

Phase 4: Review
├── Step 11: Monitor review status
├── Step 12: Respond to AI requests
├── Step 13: Receive decision
└── Verification: SE letter received?
```

### Required Sections (21 CFR 807.87)

| Section | Content |
|---------|---------|
| Cover Letter | Submission type, device ID, contact info |
| Form 3514 | CDRH premarket review cover sheet |
| Device Description | Physical description, principles of operation |
| Indications for Use | Form 3881, patient population, use environment |
| SE Comparison | Side-by-side comparison with predicate |
| Performance Testing | Bench, biocompatibility, electrical safety |
| Software Documentation | Level of concern, hazard analysis (IEC 62304) |
| Labeling | IFU, package labels, warnings |
| 510(k) Summary | Public summary of submission |

### Common RTA Issues

| Issue | Prevention |
|-------|------------|
| Missing user fee | Verify payment before submission |
| Incomplete Form 3514 | Review all fields, ensure signature |
| No predicate identified | Confirm K-number in FDA database |
| Inadequate SE comparison | Address all technological characteristics |

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-8
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## HIPAA for Medical Devices

HIPAA requirements for devices that create, store, transmit, or access Protected Health Information (PHI).

### Applicability

| Device Type | HIPAA Applies |
|-------------|---------------|
| Standalone diagnostic (no data transmission) | No |
| Connected device transmitting patient data | Yes |
| Device with EHR integration | Yes |
| SaMD storing patient information | Yes |
| Wellness app (no diagnosis) | Only if stores PHI |

### Required Safeguards

```
Administrative (§164.308)
├── Security officer designation
├── Risk analysis and management
├── Workforce training
├── Incident response procedures
└── Business associate agreements

Physical (§164.310)
├── Facility access controls
├── Workstation security
└── Device disposal procedures

Technical (§164.312)
├── Access control (unique IDs, auto-logoff)
├── Audit controls (logging)
├── Integrity controls (checksums, hashes)
├── Authentication (MFA recommended)
└── Transmission security (TLS 1.2+)
```

### Risk Assessment Steps

1. Inventory all systems handling ePHI
2. Document data flows (collection, storage, transmission)
3. Identify threats and vulnerabilities
4. Assess likelihood and impact
5. Determine risk levels
6. Implement controls
7. Document residual risk

**Reference:** See [hipaa_compliance_framework.md](references/hipaa_compliance_framework.md) for implementation checklists and BAA templates.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-9
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Resources

### scripts/

| Script | Purpose |
|--------|---------|
| `fda_submission_tracker.py` | Track 510(k)/PMA/De Novo submission milestones and timelines |
| `qsr_compliance_checker.py` | Assess 21 CFR 820 compliance against project documentation |
| `hipaa_risk_assessment.py` | Evaluate HIPAA safeguards in medical device software |

### references/

| File | Content |
|------|---------|
| `fda_submission_guide.md` | 510(k), De Novo, PMA submission requirements and checklists |
| `qsr_compliance_requirements.md` | 21 CFR 820 implementation guide with templates |
| `hipaa_compliance_framework.md` | HIPAA Security Rule safeguards and BAA requirements |
| `device_cybersecurity_guidance.md` | FDA cybersecurity requirements, SBOM, threat modeling |
| `fda_capa_requirements.md` | CAPA process, root cause analysis, effectiveness verification |

### Usage Examples

```bash
# Track FDA submission status
python scripts/fda_submission_tracker.py /path/to/project --type 510k

# Assess QSR compliance
python scripts/qsr_compliance_checker.py /path/to/project --section 820.30

# Run HIPAA risk assessment
python scripts/hipaa_risk_assessment.py /path/to/project --category technical
```


---
type: skill
lifecycle: stable
inheritance: inheritable
name: gdpr-dsgvo-expert
description: GDPR and German DSGVO compliance automation. Scans codebases for privacy risks, generates DPIA documentation, tracks data subject rights requests. Use for GDPR compliance assessments, privacy audit...
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# GDPR/DSGVO Expert

Tools and guidance for EU General Data Protection Regulation (GDPR) and German Bundesdatenschutzgesetz (BDSG) compliance.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-11
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Tools

### GDPR Compliance Checker

Scans codebases for potential GDPR compliance issues including personal data patterns and risky code practices.

```bash
# Scan a project directory
python scripts/gdpr_compliance_checker.py /path/to/project

# JSON output for CI/CD integration
python scripts/gdpr_compliance_checker.py . --json --output report.json
```

**Detects:**
- Personal data patterns (email, phone, IP addresses)
- Special category data (health, biometric, religion)
- Financial data (credit cards, IBAN)
- Risky code patterns:
  - Logging personal data
  - Missing consent mechanisms
  - Indefinite data retention
  - Unencrypted sensitive data
  - Disabled deletion functionality

**Output:**
- Compliance score (0-100)
- Risk categorization (critical, high, medium)
- Prioritized recommendations with GDPR article references

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-12
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

### Data Subject Rights Tracker

Manages data subject rights requests under GDPR Articles 15-22.

```bash
# Add new request
python scripts/data_subject_rights_tracker.py add \
  --type access --subject "John Doe" --email "john@example.com"

# List all requests
python scripts/data_subject_rights_tracker.py list

# Update status
python scripts/data_subject_rights_tracker.py status --id DSR-202601-0001 --update verified

# Generate compliance report
python scripts/data_subject_rights_tracker.py report --output compliance.json

# Generate response template
python scripts/data_subject_rights_tracker.py template --id DSR-202601-0001
```

**Supported Rights:**

| Right | Article | Deadline |
|-------|---------|----------|
| Access | Art. 15 | 30 days |
| Rectification | Art. 16 | 30 days |
| Erasure | Art. 17 | 30 days |
| Restriction | Art. 18 | 30 days |
| Portability | Art. 20 | 30 days |
| Objection | Art. 21 | 30 days |
| Automated decisions | Art. 22 | 30 days |

**Features:**
- Deadline tracking with overdue alerts
- Identity verification workflow
- Response template generation
- Compliance reporting

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-13
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Workflows

### Workflow 1: New Processing Activity Assessment

```
Step 1: Run compliance checker on codebase
        → python scripts/gdpr_compliance_checker.py /path/to/code

Step 2: Review findings and compliance score
        → Address critical and high issues

Step 3: Determine if DPIA required
        → Check references/dpia_methodology.md threshold criteria

Step 4: If DPIA required, generate assessment
        → python scripts/dpia_generator.py --template > input.json
        → Fill in processing details
        → python scripts/dpia_generator.py --input input.json --output dpia.md

Step 5: Document in records of processing activities
```

### Workflow 2: Data Subject Request Handling

```
Step 1: Log request in tracker
        → python scripts/data_subject_rights_tracker.py add --type [type] ...

Step 2: Verify identity (proportionate measures)
        → python scripts/data_subject_rights_tracker.py status --id [ID] --update verified

Step 3: Gather data from systems
        → python scripts/data_subject_rights_tracker.py status --id [ID] --update in_progress

Step 4: Generate response
        → python scripts/data_subject_rights_tracker.py template --id [ID]

Step 5: Send response and complete
        → python scripts/data_subject_rights_tracker.py status --id [ID] --update completed

Step 6: Monitor compliance
        → python scripts/data_subject_rights_tracker.py report
```

### Workflow 3: German BDSG Compliance Check

```
Step 1: Determine if DPO required
        → 20+ employees processing personal data automatically
        → OR processing requires DPIA
        → OR business involves data transfer/market research

Step 2: If employees involved, review § 26 BDSG
        → Document legal basis for employee data
        → Check works council requirements

Step 3: If video surveillance, comply with § 4 BDSG
        → Install signage
        → Document necessity
        → Limit retention

Step 4: Register DPO with supervisory authority
        → See references/german_bdsg_requirements.md for authority list
```

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-14
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

---
type: skill
lifecycle: stable
inheritance: inheritable
name: information-security-manager-iso27001
description: ISO 27001 ISMS implementation and cybersecurity governance for HealthTech and MedTech companies. Use for ISMS design, security risk assessment, control implementation, ISO 27001 certification, secu...
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Information Security Manager - ISO 27001

Implement and manage Information Security Management Systems (ISMS) aligned with ISO 27001:2022 and healthcare regulatory requirements.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-16
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Trigger Phrases

Use this skill when you hear:
- "implement ISO 27001"
- "ISMS implementation"
- "security risk assessment"
- "information security policy"
- "ISO 27001 certification"
- "security controls implementation"
- "incident response plan"
- "healthcare data security"
- "medical device cybersecurity"
- "security compliance audit"

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-17
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Tools

### risk_assessment.py

Automated security risk assessment following ISO 27001 Clause 6.1.2 methodology.

**Usage:**

```bash
# Full risk assessment
python scripts/risk_assessment.py --scope "cloud-infrastructure" --output risks.json

# Healthcare-specific assessment
python scripts/risk_assessment.py --scope "ehr-system" --template healthcare --output risks.json

# Quick asset-based assessment
python scripts/risk_assessment.py --assets assets.csv --output risks.json
```

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--scope` | Yes | System or area to assess |
| `--template` | No | Assessment template: `general`, `healthcare`, `cloud` |
| `--assets` | No | CSV file with asset inventory |
| `--output` | No | Output file (default: stdout) |
| `--format` | No | Output format: `json`, `csv`, `markdown` |

**Output:**
- Asset inventory with classification
- Threat and vulnerability mapping
- Risk scores (likelihood × impact)
- Treatment recommendations
- Residual risk calculations

### compliance_checker.py

Verify ISO 27001/27002 control implementation status.

**Usage:**

```bash
# Check all ISO 27001 controls
python scripts/compliance_checker.py --standard iso27001

# Gap analysis with recommendations
python scripts/compliance_checker.py --standard iso27001 --gap-analysis

# Check specific control domains
python scripts/compliance_checker.py --standard iso27001 --domains "access-control,cryptography"

# Export compliance report
python scripts/compliance_checker.py --standard iso27001 --output compliance_report.md
```

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--standard` | Yes | Standard to check: `iso27001`, `iso27002`, `hipaa` |
| `--controls-file` | No | CSV with current control status |
| `--gap-analysis` | No | Include remediation recommendations |
| `--domains` | No | Specific control domains to check |
| `--output` | No | Output file path |

**Output:**
- Control implementation status
- Compliance percentage by domain
- Gap analysis with priorities
- Remediation recommendations

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-18
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Reference Guides

### When to Use Each Reference

**references/iso27001-controls.md**
- Control selection for SoA
- Implementation guidance
- Evidence requirements
- Audit preparation

**references/risk-assessment-guide.md**
- Risk methodology selection
- Asset classification criteria
- Threat modeling approaches
- Risk calculation methods

**references/incident-response.md**
- Response procedures
- Escalation matrices
- Communication templates
- Recovery checklists

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-19
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Worked Example: Healthcare Risk Assessment

**Scenario:** Assess security risks for a patient data management system.

### Step 1: Define Assets

```bash
python scripts/risk_assessment.py --scope "patient-data-system" --template healthcare
```

**Asset inventory output:**

| Asset ID | Asset | Type | Owner | Classification |
|----------|-------|------|-------|----------------|
| A001 | Patient database | Information | DBA Team | Confidential |
| A002 | EHR application | Software | App Team | Critical |
| A003 | Database server | Hardware | Infra Team | High |
| A004 | Admin credentials | Access | Security | Critical |

### Step 2: Identify Risks

**Risk register output:**

| Risk ID | Asset | Threat | Vulnerability | L | I | Score |
|---------|-------|--------|---------------|---|---|-------|
| R001 | A001 | Data breach | Weak encryption | 3 | 5 | 15 |
| R002 | A002 | SQL injection | Input validation | 4 | 4 | 16 |
| R003 | A004 | Credential theft | No MFA | 4 | 5 | 20 |

### Step 3: Determine Treatment

| Risk | Treatment | Control | Timeline |
|------|-----------|---------|----------|
| R001 | Mitigate | Implement AES-256 encryption | 30 days |
| R002 | Mitigate | Add input validation, WAF | 14 days |
| R003 | Mitigate | Enforce MFA for all admins | 7 days |

### Step 4: Verify Implementation

```bash
python scripts/compliance_checker.py --controls-file implemented_controls.csv
```

**Verification output:**

```
Control Implementation Status
=============================
Cryptography (A.8.24): IMPLEMENTED
  - AES-256 at rest: YES
  - TLS 1.3 in transit: YES

Access Control (A.8.5): IMPLEMENTED
  - MFA enabled: YES
  - Admin accounts: 100% coverage

Application Security (A.8.26): PARTIAL
  - Input validation: YES
  - WAF deployed: PENDING

Overall Compliance: 87%
```


---
type: skill
lifecycle: stable
inheritance: inheritable
name: isms-audit-expert
description: Information Security Management System (ISMS) audit expert for ISO 27001 compliance verification, security control assessment, and certification support. Use when the user mentions ISO 27001, ISMS ...
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# ISMS Audit Expert

Internal and external ISMS audit management for ISO 27001 compliance verification, security control assessment, and certification support.

## Table of Contents

- [Audit Program Management](#audit-program-management)
- [Audit Execution](#audit-execution)
- [Control Assessment](#control-assessment)
- [Finding Management](#finding-management)
- [Certification Support](#certification-support)
- [Tools](#tools)
- [References](#references)

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-21
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Audit Execution

### Pre-Audit Preparation

1. Review ISMS documentation (policies, SoA, risk assessment)
2. Analyze previous audit reports and open findings
3. Prepare audit plan with interview schedule
4. Notify auditees of audit scope and timing
5. Prepare checklists for controls in scope
6. **Validation:** All documentation received and reviewed before opening meeting

### Audit Conduct Steps

1. **Opening Meeting**
   - Confirm audit scope and objectives
   - Introduce audit team and methodology
   - Agree on communication channels and logistics

2. **Evidence Collection**
   - Interview control owners and operators
   - Review documentation and records
   - Observe processes in operation
   - Inspect technical configurations

3. **Control Verification**
   - Test control design (does it address the risk?)
   - Test control operation (is it working as intended?)
   - Sample transactions and records
   - Document all evidence collected

4. **Closing Meeting**
   - Present preliminary findings
   - Clarify any factual inaccuracies
   - Agree on finding classification
   - Confirm corrective action timelines

5. **Validation:** All controls in scope assessed with documented evidence

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-22
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Finding Management

### Finding Classification

| Severity | Definition | Response Time |
|----------|------------|---------------|
| Major Nonconformity | Control failure creating significant risk | 30 days |
| Minor Nonconformity | Isolated deviation with limited impact | 90 days |
| Observation | Improvement opportunity | Next audit cycle |

### Finding Documentation Template

```
Finding ID: ISMS-[YEAR]-[NUMBER]
Control Reference: A.X.X - [Control Name]
Severity: [Major/Minor/Observation]

Evidence:
- [Specific evidence observed]
- [Records reviewed]
- [Interview statements]

Risk Impact:
- [Potential consequences if not addressed]

Root Cause:
- [Why the nonconformity occurred]

Recommendation:
- [Specific corrective action steps]
```

### Corrective Action Workflow

1. Auditee acknowledges finding and severity
2. Root cause analysis completed within 10 days
3. Corrective action plan submitted with target dates
4. Actions implemented by responsible parties
5. Auditor verifies effectiveness of corrections
6. Finding closed with evidence of resolution
7. **Validation:** Root cause addressed, recurrence prevented

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-23
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Tools

### scripts/

| Script | Purpose | Usage |
|--------|---------|-------|
| `isms_audit_scheduler.py` | Generate risk-based audit plans | `python scripts/isms_audit_scheduler.py --year 2025 --format markdown` |

### Audit Planning Example

```bash
# Generate annual audit plan
python scripts/isms_audit_scheduler.py --year 2025 --output audit_plan.json

# With custom control risk ratings
python scripts/isms_audit_scheduler.py --controls controls.csv --format markdown
```

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-24
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Audit Performance Metrics

| KPI | Target | Measurement |
|-----|--------|-------------|
| Audit plan completion | 100% | Audits completed vs. planned |
| Finding closure rate | >90% within SLA | Closed on time vs. total |
| Major nonconformities | 0 at certification | Count per certification cycle |
| Audit effectiveness | Incidents prevented | Security improvements implemented |


---
type: skill
lifecycle: stable
inheritance: inheritable
name: mdr-745-specialist
description: EU MDR 2017/745 compliance specialist for medical device classification, technical documentation, clinical evidence, and post-market surveillance. Covers Annex VIII classification rules, Annex II/I...
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# MDR 2017/745 Specialist

EU MDR compliance patterns for medical device classification, technical documentation, and clinical evidence.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-26
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Device Classification Workflow

Classify device under MDR Annex VIII:

1. Identify device duration (transient, short-term, long-term)
2. Determine invasiveness level (non-invasive, body orifice, surgical)
3. Assess body system contact (CNS, cardiac, other)
4. Check if active device (energy dependent)
5. Apply classification rules 1-22
6. For software, apply MDCG 2019-11 algorithm
7. Document classification rationale
8. **Validation:** Classification confirmed with Notified Body

### Classification Matrix

| Factor | Class I | Class IIa | Class IIb | Class III |
|--------|---------|-----------|-----------|-----------|
| Duration | Any | Short-term | Long-term | Long-term |
| Invasiveness | Non-invasive | Body orifice | Surgical | Implantable |
| System | Any | Non-critical | Critical organs | CNS/cardiac |
| Risk | Lowest | Low-medium | Medium-high | Highest |

### Software Classification (MDCG 2019-11)

| Information Use | Condition Severity | Class |
|-----------------|-------------------|-------|
| Informs decision | Non-serious | IIa |
| Informs decision | Serious | IIb |
| Drives/treats | Critical | III |

### Classification Examples

**Example 1: Absorbable Surgical Suture**
- Rule 8 (implantable, long-term)
- Duration: > 30 days (absorbed)
- Contact: General tissue
- Classification: **Class IIb**

**Example 2: AI Diagnostic Software**
- Rule 11 + MDCG 2019-11
- Function: Diagnoses serious condition
- Classification: **Class IIb**

**Example 3: Cardiac Pacemaker**
- Rule 8 (implantable)
- Contact: Central circulatory system
- Classification: **Class III**

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-27
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Clinical Evidence

Develop clinical evidence strategy per Annex XIV:

1. Define clinical claims and endpoints
2. Conduct systematic literature search
3. Appraise clinical data quality
4. Assess equivalence (technical, biological, clinical)
5. Identify evidence gaps
6. Determine if clinical investigation required
7. Prepare Clinical Evaluation Report (CER)
8. **Validation:** CER reviewed by qualified evaluator

### Evidence Requirements by Class

| Class | Minimum Evidence | Investigation |
|-------|------------------|---------------|
| I | Risk-benefit analysis | Not typically required |
| IIa | Literature + post-market | May be required |
| IIb | Systematic literature review | Often required |
| III | Comprehensive clinical data | Required (Article 61) |

### Clinical Evaluation Report Structure

```
CER CONTENTS
├── Executive summary
├── Device scope and intended purpose
├── Clinical background (state of the art)
├── Literature search methodology
├── Data appraisal and analysis
├── Safety and performance conclusions
├── Benefit-risk determination
└── PMCF plan summary
```

### Qualified Evaluator Requirements

- Medical degree or equivalent healthcare qualification
- 4+ years clinical experience in relevant field
- Training in clinical evaluation methodology
- Understanding of MDR requirements

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-28
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## EUDAMED and UDI

Implement UDI system per Article 27:

1. Obtain issuing entity code (GS1, HIBCC, ICCBBA)
2. Assign UDI-DI to each device variant
3. Assign UDI-PI (production identifier)
4. Apply UDI carrier to labels (AIDC + HRI)
5. Register actor in EUDAMED
6. Register devices in EUDAMED
7. Upload certificates when available
8. **Validation:** UDI verified on sample labels

### EUDAMED Modules

| Module | Content | Actor |
|--------|---------|-------|
| Actor | Company registration | Manufacturer, AR |
| UDI/Device | Device and variant data | Manufacturer |
| Certificates | NB certificates | Notified Body |
| Clinical Investigation | Study registration | Sponsor |
| Vigilance | Incident reports | Manufacturer |
| Market Surveillance | Authority actions | Competent Authority |

### UDI Label Requirements

Required elements per Article 13:

- [ ] UDI-DI (device identifier)
- [ ] UDI-PI (production identifier) for Class II+
- [ ] AIDC format (barcode/RFID)
- [ ] HRI format (human-readable)
- [ ] Manufacturer name and address
- [ ] Lot/serial number
- [ ] Expiration date (if applicable)

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-29
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Tools

### MDR Gap Analyzer

```bash
# Quick gap analysis
python scripts/mdr_gap_analyzer.py --device "Device Name" --class IIa

# JSON output for integration
python scripts/mdr_gap_analyzer.py --device "Device Name" --class III --output json

# Interactive assessment
python scripts/mdr_gap_analyzer.py --interactive
```

Analyzes device against MDR requirements, identifies compliance gaps, generates prioritized recommendations.

**Output includes:**
- Requirements checklist by category
- Gap identification with priorities
- Critical gap highlighting
- Compliance roadmap recommendations

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-30
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

---
type: skill
lifecycle: stable
inheritance: inheritable
name: qms-audit-expert
description: ISO 13485 internal audit expertise for medical device QMS. Covers audit planning, execution, nonconformity classification, and CAPA verification. Use for internal audit planning, audit execution, f...
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# QMS Audit Expert

ISO 13485 internal audit methodology for medical device quality management systems.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-32
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Audit Planning Workflow

Plan risk-based internal audit program:

1. List all QMS processes requiring audit
2. Assign risk level to each process (High/Medium/Low)
3. Review previous audit findings and trends
4. Determine audit frequency by risk level
5. Assign qualified auditors (verify independence)
6. Create annual audit schedule
7. Communicate schedule to process owners
8. **Validation:** All ISO 13485 clauses covered within cycle

### Risk-Based Audit Frequency

| Risk Level | Frequency | Criteria |
|------------|-----------|----------|
| High | Quarterly | Design control, CAPA, production validation |
| Medium | Semi-annual | Purchasing, training, document control |
| Low | Annual | Infrastructure, management review (if stable) |

### Audit Scope by Clause

| Clause | Process | Focus Areas |
|--------|---------|-------------|
| 4.2 | Document Control | Document approval, distribution, obsolete control |
| 5.6 | Management Review | Inputs complete, decisions documented, actions tracked |
| 6.2 | Training | Competency defined, records complete, effectiveness verified |
| 7.3 | Design Control | Inputs, reviews, V&V, transfer, changes |
| 7.4 | Purchasing | Supplier evaluation, incoming inspection |
| 7.5 | Production | Work instructions, process validation, DHR |
| 7.6 | Calibration | Equipment list, calibration status, out-of-tolerance |
| 8.2.2 | Internal Audit | Schedule compliance, auditor independence |
| 8.3 | NC Product | Identification, segregation, disposition |
| 8.5 | CAPA | Root cause, implementation, effectiveness |

### Auditor Independence

Verify auditor independence before assignment:

- [ ] Auditor not responsible for area being audited
- [ ] No direct reporting relationship to auditee
- [ ] Not involved in recent activities under audit
- [ ] Documented qualification for audit scope

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-33
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Nonconformity Management

Classify and manage audit findings:

1. Evaluate finding against classification criteria
2. Assign severity (Major/Minor/Observation)
3. Document finding with objective evidence
4. Communicate to process owner
5. Initiate CAPA for Major/Minor findings
6. Track to closure
7. Verify effectiveness at follow-up
8. **Validation:** Finding closed only after effective CAPA

### Classification Criteria

| Category | Definition | CAPA Required | Timeline |
|----------|------------|---------------|----------|
| Major | Systematic failure or absence of element | Yes | 30 days |
| Minor | Isolated lapse or partial implementation | Recommended | 60 days |
| Observation | Improvement opportunity | Optional | As appropriate |

### Classification Decision

```
Is required element absent or failed?
├── Yes → Systematic (multiple instances)? → MAJOR
│   └── No → Could affect product safety? → MAJOR
│       └── No → MINOR
└── No → Deviation from procedure?
    ├── Yes → Recurring? → MAJOR
    │   └── No → MINOR
    └── No → Improvement opportunity? → OBSERVATION
```

### CAPA Integration

| Finding Severity | CAPA Depth | Verification |
|------------------|------------|--------------|
| Major | Full root cause analysis (5-Why, Fishbone) | Next audit or within 6 months |
| Minor | Immediate cause identification | Next scheduled audit |
| Observation | Not required | Noted at next audit |

See `references/nonconformity-classification.md` for detailed guidance.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-34
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Reference Documentation

### ISO 13485 Audit Guide

`references/iso13485-audit-guide.md` contains:

- Clause-by-clause audit methodology
- Sample audit questions for each clause
- Evidence collection requirements
- Common nonconformities by clause
- Finding severity classification

### Nonconformity Classification

`references/nonconformity-classification.md` contains:

- Severity classification criteria and decision tree
- Impact vs. occurrence matrix
- CAPA integration requirements
- Finding documentation templates
- Closure requirements by severity

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-35
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Audit Program Metrics

Track audit program effectiveness:

| Metric | Target | Measurement |
|--------|--------|-------------|
| Schedule compliance | >90% | Audits completed on time |
| Finding closure rate | >95% | Findings closed by due date |
| Repeat findings | <10% | Same finding in consecutive audits |
| CAPA effectiveness | >90% | Verified effective at follow-up |
| Auditor utilization | 4 days/month | Audit days per qualified auditor |


---
type: skill
lifecycle: stable
inheritance: inheritable
name: quality-documentation-manager
description: Document control system management for medical device QMS. Covers document numbering, version control, change management, and 21 CFR Part 11 compliance. Use for document control procedures, change ...
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Quality Documentation Manager

Document control system design and management for ISO 13485-compliant quality management systems, including numbering conventions, approval workflows, change control, and electronic record compliance.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-37
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Document Control Workflow

Implement document control from creation through obsolescence:

1. Assign document number per numbering procedure
2. Create document using controlled template
3. Route for review to required reviewers
4. Address review comments and document responses
5. Obtain required approval signatures
6. Assign effective date and distribute
7. Update Document Master List
8. **Validation:** Document accessible at point of use; obsolete versions removed

### Document Lifecycle Stages

| Stage | Definition | Actions Required |
|-------|------------|------------------|
| Draft | Under creation or revision | Author editing, not for use |
| Review | Circulated for review | Reviewers provide feedback |
| Approved | All signatures obtained | Ready for training/distribution |
| Effective | Training complete, released | Available for use |
| Superseded | Replaced by newer revision | Remove from active use |
| Obsolete | No longer applicable | Archive per retention schedule |

### Document Types and Prefixes

| Prefix | Document Type | Typical Content |
|--------|---------------|-----------------|
| QM | Quality Manual | QMS overview, scope, policy |
| SOP | Standard Operating Procedure | Process-level procedures |
| WI | Work Instruction | Task-level step-by-step |
| TF | Template/Form | Controlled forms |
| SPEC | Specification | Product/process specs |
| PLN | Plan | Quality/project plans |

### Required Reviewers by Document Type

| Document Type | Required Reviewers | Required Approvers |
|---------------|-------------------|-------------------|
| SOP | Process Owner, QA | QA Manager, Process Owner |
| WI | Area Supervisor, QA | Area Manager |
| SPEC | Engineering, QA | Engineering Manager, QA |
| TF | Process Owner | QA |
| Design Documents | Design Team, QA | Design Control Authority |

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-38
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Approval and Review Process

Obtain required reviews and approvals before document release.

### Review Workflow

1. Author completes document draft
2. Author submits for review via routing form or DMS
3. Reviewers assigned based on document type
4. Reviewers provide comments within review period (5-10 business days)
5. Author addresses comments and documents responses
6. Author resubmits revised document
7. Approvers sign and date
8. **Validation:** All required reviewers completed; all comments addressed with documented disposition

### Comment Disposition

| Disposition | Action Required |
|-------------|-----------------|
| Accept | Incorporate comment as written |
| Accept with modification | Incorporate with changes, document rationale |
| Reject | Do not incorporate, document justification |
| Defer | Address in future revision, document reason |

### Approval Matrix

```
Document Level 1 (Policy/QM): CEO or delegate + QA Manager
Document Level 2 (SOP): Department Manager + QA Manager
Document Level 3 (WI/TF): Area Supervisor + QA Representative
```

### Signature Requirements

| Element | Requirement |
|---------|-------------|
| Name | Printed name of signer |
| Signature | Handwritten or electronic signature |
| Date | Date signature applied |
| Role | Function/role of signer |

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-39
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## 21 CFR Part 11 Compliance

Implement electronic record and signature controls for FDA compliance.

### Part 11 Scope

| Applies To | Does Not Apply To |
|------------|-------------------|
| Records required by FDA regulations | Paper records |
| Records submitted to FDA | Internal non-regulated documents |
| Electronic signatures on required records | General email communication |

### Electronic Record Controls

1. Validate system for accuracy and reliability
2. Implement secure audit trail for all changes
3. Restrict system access to authorized individuals
4. Generate accurate copies in human-readable format
5. Protect records throughout retention period
6. **Validation:** Audit trail captures who, what, when for all changes

### Audit Trail Requirements

| Requirement | Implementation |
|-------------|----------------|
| Secure | Cannot be modified by users |
| Computer-generated | System creates automatically |
| Time-stamped | Date and time of each action |
| Original values | Previous values retained |
| User identity | Who made each change |

### Electronic Signature Requirements

| Requirement | Implementation |
|-------------|----------------|
| Unique to individual | Not shared between persons |
| At least 2 components | User ID + password minimum |
| Signature manifestation | Name, date/time, meaning displayed |
| Linked to record | Cannot be excised or copied |

### Signature Manifestation

Every electronic signature must display:

| Element | Example |
|---------|---------|
| Printed name | John Smith |
| Date and time | 2024-03-15 14:32:05 EST |
| Meaning | Approved for Release |

### System Controls Checklist

**Access Controls:**
- [ ] Unique user ID for each person
- [ ] Password complexity enforced
- [ ] Account lockout after failed attempts
- [ ] Session timeout after inactivity

**Audit Trail:**
- [ ] All record creation logged
- [ ] All modifications logged with old/new values
- [ ] User identity captured
- [ ] Date/time stamp on all entries

**Security:**
- [ ] Role-based access control
- [ ] Encryption for data at rest and in transit
- [ ] Regular backup and tested recovery

See `references/21cfr11-compliance-guide.md` for detailed compliance requirements.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-40
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Tools

### Document Validator

```bash
# Validate document metadata
python scripts/document_validator.py --doc document.json

# Interactive validation mode
python scripts/document_validator.py --interactive

# JSON output for integration
python scripts/document_validator.py --doc document.json --output json

# Generate sample document JSON
python scripts/document_validator.py --sample > sample_doc.json
```

Validates:
- Document numbering convention compliance
- Title and status requirements
- Date validation (effective, review due)
- Approval requirements by document type
- Change history completeness
- 21 CFR Part 11 controls (audit trail, signatures)

### Sample Document Input

```json
{
  "number": "SOP-02-001",
  "title": "Document Control Procedure",
  "doc_type": "SOP",
  "revision": "03",
  "status": "Effective",
  "effective_date": "2024-01-15",
  "review_date": "2025-01-15",
  "author": "J. Smith",
  "approver": "M. Jones",
  "change_history": [
    {"revision": "01", "date": "2022-01-01", "description": "Initial release"},
    {"revision": "02", "date": "2023-01-15", "description": "Updated workflow"},
    {"revision": "03", "date": "2024-01-15", "description": "Added e-signature requirements"}
  ],
  "has_audit_trail": true,
  "has_electronic_signature": true,
  "signature_components": 2
}
```

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-41
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Regulatory Requirements

### ISO 13485:2016 Clause 4.2

| Sub-clause | Requirement |
|------------|-------------|
| 4.2.1 | Quality management system documentation |
| 4.2.2 | Quality manual |
| 4.2.3 | Medical device file (technical documentation) |
| 4.2.4 | Control of documents |
| 4.2.5 | Control of records |

### FDA 21 CFR 820

| Section | Requirement |
|---------|-------------|
| 820.40 | Document controls |
| 820.180 | General record requirements |
| 820.181 | Device master record |
| 820.184 | Device history record |
| 820.186 | Quality system record |

### Common Audit Findings

| Finding | Prevention |
|---------|------------|
| Obsolete documents in use | Implement distribution control |
| Missing approval signatures | Enforce workflow before release |
| Incomplete change history | Require history update with each revision |
| No periodic review schedule | Establish and enforce review calendar |
| Inadequate audit trail | Validate DMS for Part 11 compliance |


---
type: skill
lifecycle: stable
inheritance: inheritable
name: quality-manager-qmr
description: Senior Quality Manager Responsible Person (QMR) for HealthTech and MedTech companies. Provides quality system governance, management review leadership, regulatory compliance oversight, and quality ...
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Senior Quality Manager Responsible Person (QMR)

Quality system accountability, management review leadership, and regulatory compliance oversight per ISO 13485 Clause 5.5.2 requirements.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-43
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## QMR Responsibilities

### ISO 13485 Clause 5.5.2 Requirements

| Responsibility | Scope | Evidence |
|----------------|-------|----------|
| QMS effectiveness | Monitor system performance and suitability | Management review records |
| Reporting to management | Communicate QMS performance to top management | Quality reports, dashboards |
| Quality awareness | Promote regulatory and quality requirements | Training records, communications |
| Liaison with external parties | Interface with regulators, Notified Bodies | Meeting records, correspondence |

### QMR Accountability Matrix

| Domain | Accountable For | Reports To | Frequency |
|--------|-----------------|------------|-----------|
| Quality Policy | Policy adequacy and communication | CEO/Board | Annual review |
| Quality Objectives | Objective achievement and relevance | Executive Team | Quarterly |
| QMS Performance | System effectiveness metrics | Management | Monthly |
| Regulatory Compliance | Compliance status across jurisdictions | CEO | Quarterly |
| Audit Program | Audit schedule completion, findings closure | Management | Per audit |
| CAPA Oversight | CAPA effectiveness and timeliness | Executive Team | Monthly |

### Authority Boundaries

| Decision Type | QMR Authority | Escalation Required |
|---------------|---------------|---------------------|
| Process changes within QMS | Approve with owner | Major process redesign |
| Document approval | Final QA approval | Policy-level changes |
| Nonconformity disposition | Accept/reject with MRB | Product release decisions |
| Supplier quality actions | Quality holds, audits | Supplier termination |
| Audit scheduling | Adjust internal audit schedule | External audit timing |
| Training requirements | Define quality training needs | Organization-wide training budget |

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-44
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Quality KPI Management Workflow

Establish, monitor, and report quality performance indicators.

### Workflow: Establish Quality KPI Framework

1. Identify quality objectives requiring measurement
2. Select KPIs per objective using SMART criteria:
   - Specific: Clear definition and calculation
   - Measurable: Quantifiable with available data
   - Actionable: Team can influence results
   - Relevant: Aligned to quality objectives
   - Time-bound: Defined measurement frequency
3. Define target values based on baseline data and benchmarks
4. Assign data source and collection responsibility
5. Establish reporting frequency per KPI category
6. Configure dashboard displays and trend analysis
7. Define escalation thresholds and alert triggers
8. **Validation:** Each KPI has owner, target, data source, and escalation criteria

### Core Quality KPIs

| Category | KPI | Target | Calculation |
|----------|-----|--------|-------------|
| Process | First Pass Yield | >95% | (Units passed first time / Total units) × 100 |
| Process | Nonconformance Rate | <1% | (NC count / Total units) × 100 |
| CAPA | CAPA Closure Rate | >90% | (On-time closures / Due closures) × 100 |
| CAPA | CAPA Effectiveness | >85% | (Effective CAPAs / Verified CAPAs) × 100 |
| Audit | Finding Closure Rate | >90% | (On-time closures / Due closures) × 100 |
| Audit | Repeat Finding Rate | <10% | (Repeat findings / Total findings) × 100 |
| Customer | Complaint Rate | <0.1% | (Complaints / Units sold) × 100 |
| Customer | Satisfaction Score | >4.0/5.0 | Average of survey scores |

### KPI Review Frequency

| KPI Type | Review Frequency | Trend Period | Audience |
|----------|------------------|--------------|----------|
| Safety/Compliance | Daily monitoring | Weekly | Operations |
| Production Quality | Weekly | Monthly | Department heads |
| Customer Quality | Monthly | Quarterly | Executive team |
| Strategic Quality | Quarterly | Annual | Board/C-suite |

### Performance Response Matrix

| Performance Level | Status | Action Required |
|-------------------|--------|-----------------|
| >110% of target | Exceeding | Consider raising target |
| 100-110% of target | Meeting | Maintain current approach |
| 90-100% of target | Approaching | Monitor closely |
| 80-90% of target | Below | Improvement plan required |
| <80% of target | Critical | Immediate intervention |

See: [references/quality-kpi-framework.md](references/quality-kpi-framework.md)

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-45
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Quality Culture Assessment Workflow

Assess and improve organizational quality culture.

### Workflow: Annual Quality Culture Assessment

1. Design or select quality culture survey instrument
2. Define survey population (all employees or sample)
3. Communicate survey purpose and confidentiality
4. Administer survey with 2-week response window
5. Analyze results by department, role, and tenure
6. Identify strengths and improvement areas
7. Develop action plan for culture gaps
8. **Validation:** Response rate >60%; action plan addresses bottom 3 scores

### Quality Culture Dimensions

| Dimension | Indicators | Assessment Method |
|-----------|------------|-------------------|
| Leadership commitment | Management visible support for quality | Survey, observation |
| Quality ownership | Employees feel responsible for quality | Survey |
| Communication | Quality information flows effectively | Survey, audit |
| Continuous improvement | Suggestions submitted and implemented | Metrics |
| Training and competence | Employees feel adequately trained | Survey, records |
| Problem solving | Issues addressed at root cause | CAPA analysis |

### Culture Survey Categories

| Category | Sample Questions |
|----------|------------------|
| Leadership | "Management demonstrates commitment to quality" |
| Resources | "I have the tools and training to do quality work" |
| Communication | "Quality expectations are clearly communicated" |
| Empowerment | "I am encouraged to report quality issues" |
| Recognition | "Quality achievements are recognized" |

### Culture Improvement Actions

| Gap Identified | Potential Actions |
|----------------|-------------------|
| Low leadership visibility | Quality gemba walks, all-hands quality updates |
| Inadequate training | Competency-based training program |
| Poor communication | Quality newsletters, department huddles |
| Low reporting | Anonymous reporting system, no-blame culture |
| Lack of recognition | Quality award program, team celebrations |

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-46
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Decision Frameworks

### Escalation Decision Tree

```
Issue Identified
      │
      ▼
Is it a regulatory violation?
      │
  Yes─┴─No
  │      │
  ▼      ▼
Escalate to    Is it a safety issue?
Executive          │
immediately    Yes─┴─No
               │      │
               ▼      ▼
          Escalate to   Does it affect
          Safety Team   multiple departments?
                             │
                         Yes─┴─No
                         │      │
                         ▼      ▼
                    Escalate to  Handle at
                    Executive    department level
```

### Quality Investment Prioritization

| Criteria | Weight | Score Method |
|----------|--------|--------------|
| Regulatory requirement | 30% | Required=10, Recommended=5, Optional=2 |
| Customer impact | 25% | Direct=10, Indirect=5, None=0 |
| Cost savings potential | 20% | >$100K=10, $50-100K=7, <$50K=3 |
| Implementation complexity | 15% | Simple=10, Moderate=5, Complex=2 |
| Strategic alignment | 10% | Core=10, Supporting=5, Peripheral=2 |

### Resource Allocation Matrix

| Resource Type | Allocation Authority | Escalation Threshold |
|---------------|---------------------|---------------------|
| Quality personnel | QMR | >1 FTE addition |
| Quality equipment | QMR | >$25K |
| External consultants | QMR | >$50K or >30 days |
| Quality systems | Executive approval | >$100K |

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-47
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Related Skills

| Skill | Integration Point |
|-------|-------------------|
| [quality-manager-qms-iso13485](../quality-manager-qms-iso13485/) | QMS process management |
| [capa-officer](../capa-officer/) | CAPA system oversight |
| [qms-audit-expert](../qms-audit-expert/) | Internal audit program |
| [quality-documentation-manager](../quality-documentation-manager/) | Document control oversight |


---
type: skill
lifecycle: stable
inheritance: inheritable
name: quality-manager-qms-iso13485
description: ISO 13485 Quality Management System implementation and maintenance for medical device organizations. Provides QMS design, documentation control, internal auditing, CAPA management, and certificatio...
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Quality Manager - QMS ISO 13485 Specialist

ISO 13485:2016 Quality Management System implementation, maintenance, and certification support for medical device organizations.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-49
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## QMS Implementation Workflow

Implement ISO 13485:2016 compliant quality management system from gap analysis through certification.

### Workflow: Initial QMS Implementation

1. Conduct gap analysis against ISO 13485:2016 requirements
2. Document current state vs. required state for each clause
3. Prioritize gaps by:
   - Regulatory criticality
   - Risk to product safety
   - Resource requirements
4. Develop implementation roadmap with milestones
5. Establish Quality Manual per Clause 4.2.2:
   - QMS scope with justified exclusions
   - Process interactions
   - Procedure references
6. Create required documented procedures — see [Mandatory Documented Procedures](#quick-reference-mandatory-documented-procedures) for the full list
7. Deploy processes with training
8. **Validation:** Gap analysis complete; Quality Manual approved; all required procedures documented and trained

> Use the Gap Analysis Matrix template in [qms-process-templates.md](references/qms-process-templates.md) to document clause-by-clause current state, gaps, priority, and actions.

### QMS Structure

| Level | Document Type | Example |
|-------|---------------|---------|
| 1 | Quality Manual | QM-001 |
| 2 | Procedures | SOP-02-001 |
| 3 | Work Instructions | WI-06-012 |
| 4 | Records | Training records |

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-50
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Internal Audit Workflow

Plan and execute internal audits per ISO 13485 Clause 8.2.4.

### Workflow: Annual Audit Program

1. Identify processes and areas requiring audit coverage
2. Assess risk factors for audit frequency:
   - Previous audit findings
   - Regulatory changes
   - Process changes
   - Complaint trends
3. Assign qualified auditors (independent of area audited)
4. Develop annual audit schedule
5. Obtain management approval
6. Communicate schedule to process owners
7. Track completion and reschedule as needed
8. **Validation:** All processes covered; auditors qualified and independent; schedule approved

> Use the Audit Program Template in [qms-process-templates.md](references/qms-process-templates.md) to schedule audits by clause and quarter across processes such as Document Control (4.2.3/4.2.4), Management Review (5.6), Design Control (7.3), Production (7.5), and CAPA (8.5.2/8.5.3).

### Workflow: Individual Audit Execution

1. Prepare audit plan with scope, criteria, and schedule
2. Notify auditee minimum 1 week prior
3. Review procedures and previous audit results
4. Prepare audit checklist
5. Conduct opening meeting
6. Collect evidence through:
   - Document review
   - Record sampling
   - Process observation
   - Personnel interviews
7. Classify findings:
   - Major NC: Absence or breakdown of system
   - Minor NC: Single lapse or deviation
   - Observation: Risk of future NC
8. Conduct closing meeting
9. Issue audit report within 5 business days
10. **Validation:** All checklist items addressed; findings supported by evidence; report distributed

### Auditor Qualification Requirements

| Criterion | Requirement |
|-----------|-------------|
| Training | ISO 13485 awareness + auditor training |
| Experience | Minimum 1 audit as observer |
| Independence | Not auditing own work area |
| Competence | Understanding of audited process |

### Finding Classification Guide

| Classification | Criteria | Response Time |
|----------------|----------|---------------|
| Major NC | System absence, total breakdown, regulatory violation | 30 days for CAPA |
| Minor NC | Single instance, partial compliance | 60 days for CAPA |
| Observation | Potential risk, improvement opportunity | Track in next audit |

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-51
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Supplier Qualification Workflow

Evaluate and approve suppliers per ISO 13485 Clause 7.4.

### Workflow: New Supplier Qualification

1. Identify supplier category:
   - Category A: Critical (affects safety/performance)
   - Category B: Major (affects quality)
   - Category C: Minor (indirect impact)
2. Request supplier information:
   - Quality certifications
   - Product specifications
   - Quality history
3. Evaluate supplier based on:
   - Quality system (ISO certification)
   - Technical capability
   - Quality history
   - Financial stability
4. For Category A suppliers:
   - Conduct on-site audit
   - Require quality agreement
5. Calculate qualification score
6. Make approval decision:
   - >80: Approved
   - 60-80: Conditional approval
   - <60: Not approved
7. Add to Approved Supplier List
8. **Validation:** Evaluation criteria scored; qualification records complete; supplier categorized

### Supplier Evaluation Criteria

| Criterion | Weight | Scoring |
|-----------|--------|---------|
| Quality System | 30% | ISO 13485=30, ISO 9001=20, Documented=10, None=0 |
| Quality History | 25% | Reject rate: <1%=25, 1-3%=15, >3%=0 |
| Delivery | 20% | On-time: >95%=20, 90-95%=10, <90%=0 |
| Technical Capability | 15% | Exceeds=15, Meets=10, Marginal=5 |
| Financial Stability | 10% | Strong=10, Adequate=5, Questionable=0 |

### Supplier Category Requirements

| Category | Qualification | Monitoring | Agreement |
|----------|---------------|------------|-----------|
| A - Critical | On-site audit | Annual review | Quality agreement |
| B - Major | Questionnaire | Semi-annual review | Quality requirements |
| C - Minor | Assessment | Issue-based | Standard terms |

### Supplier Performance Metrics

| Metric | Target | Calculation |
|--------|--------|-------------|
| Accept Rate | >98% | (Accepted lots / Total lots) × 100 |
| On-Time Delivery | >95% | (On-time / Total orders) × 100 |
| Response Time | <5 days | Average days to resolve issues |
| Documentation | 100% | (Complete CoCs / Required CoCs) × 100 |

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-52
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Decision Frameworks

### Exclusion Justification (Clause 4.2.2)

| Clause | Permissible Exclusion | Justification Required |
|--------|----------------------|------------------------|
| 6.4.2 | Contamination control | Product not affected by contamination |
| 7.3 | Design and development | Organization does not design products |
| 7.5.2 | Product cleanliness | No cleanliness requirements |
| 7.5.3 | Installation | No installation activities |
| 7.5.4 | Servicing | No servicing activities |
| 7.5.5 | Sterile products | No sterile products |

### Nonconformity Disposition Decision Tree

```
Nonconforming Product Identified
            │
            ▼
    Can it be reworked?
            │
       Yes──┴──No
        │       │
        ▼       ▼
    Is rework     Can it be used
    procedure     as is?
    available?        │
        │        Yes──┴──No
    Yes─┴─No     │       │
     │    │     ▼       ▼
     ▼    ▼  Concession  Scrap or
  Rework  Create    approval    return to
  per SOP  rework    needed?    supplier
          procedure     │
                    Yes─┴─No
                     │    │
                     ▼    ▼
                 Customer  Use as is
                 approval  with MRB
                          approval
```

### CAPA Initiation Criteria

| Source | Automatic CAPA | Evaluate for CAPA |
|--------|----------------|-------------------|
| Customer complaint | Safety-related | All others |
| External audit | Major NC | Minor NC |
| Internal audit | Major NC | Repeat minor NC |
| Product NC | Field failure | Trend exceeds threshold |
| Process deviation | Safety impact | Repeated deviations |

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-53
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Related Skills

| Skill | Integration Point |
|-------|-------------------|
| [quality-manager-qmr](../quality-manager-qmr/) | Management review, quality policy |
| [capa-officer](../capa-officer/) | CAPA system management |
| [qms-audit-expert](../qms-audit-expert/) | Advanced audit techniques |
| [quality-documentation-manager](../quality-documentation-manager/) | DHF, DMR, DHR management |
| [risk-management-specialist](../risk-management-specialist/) | ISO 14971 integration |


---
type: skill
lifecycle: stable
inheritance: inheritable
name: ra-qm-skills
description: 12 regulatory & QM agent skills and plugins for Claude Code, Codex, Gemini CLI, Cursor, OpenClaw. ISO 13485 QMS, MDR 2017/745, FDA 510(k)/PMA, ISO 27001 ISMS, GDPR/DSGVO, risk management (ISO 14971...
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Regulatory Affairs & Quality Management Skills

12 production-ready compliance skills for HealthTech and MedTech organizations.

## Quick Start

### Claude Code
```
/read ra-qm-team/regulatory-affairs-head/SKILL.md
```

### Codex CLI
```bash
npx agent-skills-cli add alirezarezvani/claude-skills/ra-qm-team
```

## Skills Overview

| Skill | Folder | Focus |
|-------|--------|-------|
| Regulatory Affairs Head | `regulatory-affairs-head/` | FDA/MDR strategy, submissions |
| Quality Manager (QMR) | `quality-manager-qmr/` | QMS governance, management review |
| Quality Manager (ISO 13485) | `quality-manager-qms-iso13485/` | QMS implementation, doc control |
| Risk Management Specialist | `risk-management-specialist/` | ISO 14971, FMEA, risk files |
| CAPA Officer | `capa-officer/` | Root cause analysis, corrective actions |
| Quality Documentation Manager | `quality-documentation-manager/` | Document control, 21 CFR Part 11 |
| QMS Audit Expert | `qms-audit-expert/` | ISO 13485 internal audits |
| ISMS Audit Expert | `isms-audit-expert/` | ISO 27001 security audits |
| Information Security Manager | `information-security-manager-iso27001/` | ISMS implementation |
| MDR 745 Specialist | `mdr-745-specialist/` | EU MDR classification, CE marking |
| FDA Consultant | `fda-consultant-specialist/` | 510(k), PMA, QSR compliance |
| GDPR/DSGVO Expert | `gdpr-dsgvo-expert/` | Privacy compliance, DPIA |

## Python Tools

17 scripts, all stdlib-only:

```bash
python3 risk-management-specialist/scripts/risk_matrix_calculator.py --help
python3 gdpr-dsgvo-expert/scripts/gdpr_compliance_checker.py --help
```

## Rules

- Load only the specific skill SKILL.md you need
- Always verify compliance outputs against current regulations


---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-affairs-head
description: Senior Regulatory Affairs Manager for HealthTech and MedTech companies. Prepares FDA 510(k), De Novo, and PMA submission packages; analyzes regulatory pathways for new medical devices; drafts respo...
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Head of Regulatory Affairs

Regulatory strategy development, submission management, and global market access for medical device organizations.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-56
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Regulatory Strategy Workflow

Develop regulatory strategy aligned with business objectives and product characteristics.

### Workflow: New Product Regulatory Strategy

1. Gather product information:
   - Intended use and indications
   - Device classification (risk level)
   - Technology platform
   - Target markets and timeline
2. Identify applicable regulations per target market:
   - FDA (US): 21 CFR Part 820, 510(k)/PMA/De Novo
   - EU: MDR 2017/745, Notified Body requirements
   - Other markets: Health Canada, PMDA, NMPA, TGA
3. Determine optimal regulatory pathway:
   - Compare submission types (510(k) vs De Novo vs PMA)
   - Assess predicate device availability
   - Evaluate clinical evidence requirements
4. Develop regulatory timeline with milestones
5. Estimate resource requirements and budget
6. Identify regulatory risks and mitigation strategies
7. Obtain stakeholder alignment and approval
8. **Validation:** Strategy document approved; timeline accepted; resources allocated

### Regulatory Pathway Selection Matrix

| Factor | 510(k) | De Novo | PMA |
|--------|--------|---------|-----|
| Predicate Available | Yes | No | N/A |
| Risk Level | Low-Moderate | Low-Moderate | High |
| Clinical Data | Usually not required | May be required | Required |
| Review Time | 90 days (MDUFA) | 150 days | 180 days |
| User Fee | ~$22K (2024) | ~$135K | ~$440K |
| Best For | Me-too devices | Novel low-risk | High-risk, novel |

### Regulatory Strategy Document Template

```
REGULATORY STRATEGY

Product: [Name]   Version: [X.X]   Date: [Date]

1. PRODUCT OVERVIEW
   Intended use: [One-sentence statement of intended patient population, body site, and clinical purpose]
   Device classification: [Class I / II / III]
   Technology: [Brief description, e.g., "AI-powered wound-imaging software, SaMD"]

2. TARGET MARKETS & TIMELINE
   | Market | Pathway        | Priority | Target Date |
   |--------|----------------|----------|-------------|
   | USA    | 510(k) / PMA   | 1        | Q1 20XX     |
   | EU     | Class [X] MDR  | 2        | Q2 20XX     |

3. REGULATORY PATHWAY RATIONALE
   FDA: [510(k) / De Novo / PMA] — Predicate: [K-number or "none"]
   EU:  Class [X] via [Annex IX / X / XI] — NB: [Name or TBD]
   Rationale: [2–3 sentences on key factors driving pathway choice]

4. CLINICAL EVIDENCE STRATEGY
   Requirements: [Summarize what each market needs, e.g., "510(k): bench + usability; EU Class IIb: PMCF study"]
   Approach: [Literature review / Prospective study / Combination]

5. RISKS AND MITIGATION
   | Risk                         | Prob | Impact | Mitigation                        |
   |------------------------------|------|--------|-----------------------------------|
   | Predicate delisted by FDA    | Low  | High   | Identify secondary predicate now  |
   | NB audit backlog             | Med  | Med    | Engage NB 6 months before target  |

6. RESOURCE REQUIREMENTS
   Budget: $[Amount]   Personnel: [FTEs]   External: [Consultants / CRO]
```

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-57
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## EU MDR Submission Workflow

Achieve CE marking under EU MDR 2017/745.

### Workflow: MDR Technical Documentation

1. Confirm device classification per MDR Annex VIII
2. Select conformity assessment route based on class:
   - Class I: Self-declaration
   - Class IIa/IIb: Notified Body involvement
   - Class III: Full NB assessment
3. Select and engage Notified Body (for Class IIa+) — see selection criteria below
4. Compile Technical Documentation per Annex II checklist:
   - [ ] Annex II §1: Device description, intended purpose, UDI
   - [ ] Annex II §2: Design and manufacturing information (drawings, BoM, process flows)
   - [ ] Annex II §3: GSPR checklist — each requirement mapped to evidence (standard, test report, or justification)
   - [ ] Annex II §4: Benefit-risk analysis and risk management file (ISO 14971)
   - [ ] Annex II §5: Product verification and validation (test reports)
   - [ ] Annex II §6: Post-market surveillance plan
   - [ ] Annex XIV: Clinical evaluation report (CER) — literature, clinical data, equivalence justification
5. Establish and document QMS per ISO 13485
6. Submit application to Notified Body
7. Address NB questions and coordinate audit
8. **Validation:** CE certificate issued; Declaration of Conformity signed; EUDAMED registration complete

#### GSPR Checklist Row Example

| GSPR Ref | Requirement | Standard / Guidance | Evidence Document | Status |
|----------|-------------|---------------------|-------------------|--------|
| Annex I §1 | Safe design and manufacture | ISO 14971:2019 | Risk Management File v2.1 | Complete |
| Annex I §11.1 | Devices with measuring function ±accuracy | EN ISO 15223-1 | Performance Test Report PT-003 | Complete |
| Annex I §17 | Cybersecurity | MDCG 2019-16 | Cybersecurity Assessment CS-001 | In progress |

### Clinical Evidence Requirements by Class

| Class | Clinical Requirement | Documentation |
|-------|---------------------|---------------|
| I | Clinical evaluation (CE) | CE report |
| IIa | CE with literature focus | CE report + PMCF plan |
| IIb | CE with clinical data | CE report + PMCF + clinical study (some) |
| III | CE with clinical investigation | CE report + PMCF + clinical investigation |

### Notified Body Selection Criteria

- **Scope:** Designated for your specific device category
- **Capacity:** Confirmed availability within target timeline
- **Experience:** Track record with your technology type
- **Geography:** Proximity for on-site audits
- **Cost:** Fee structure transparency
- **Communication:** Responsiveness and query turnaround

See: [references/eu-mdr-submission-guide.md](references/eu-mdr-submission-guide.md)

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-58
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Regulatory Intelligence Workflow

Monitor and respond to regulatory changes affecting product portfolio.

### Workflow: Regulatory Change Management

1. Monitor regulatory sources:
   - FDA Federal Register, guidance documents
   - EU Official Journal, MDCG guidance
   - Notified Body communications
   - Industry associations (AdvaMed, MedTech Europe)
2. Assess relevance to product portfolio
3. Evaluate impact:
   - Timeline to compliance
   - Resource requirements
   - Product changes needed
4. Develop compliance action plan
5. Communicate to affected stakeholders
6. Implement required changes
7. Document compliance status
8. **Validation:** Compliance action plan approved; changes implemented on schedule

### Regulatory Monitoring Sources

| Source | Type | Frequency |
|--------|------|-----------|
| FDA Federal Register | Regulations, guidance | Daily |
| FDA Device Database | 510(k), PMA, recalls | Weekly |
| EU Official Journal | MDR/IVDR updates | Weekly |
| MDCG Guidance | EU implementation | As published |
| ISO/IEC | Standards updates | Quarterly |
| Notified Body | Audit findings, trends | Per interaction |

### Impact Assessment Template

```
REGULATORY CHANGE IMPACT ASSESSMENT

Change: [Description]   Source: [Regulation/Guidance]
Effective Date: [Date]  Assessment Date: [Date]  Assessed By: [Name]

AFFECTED PRODUCTS
| Product | Impact (H/M/L) | Action Required        | Due Date |
|---------|----------------|------------------------|----------|
| [Name]  | [H/M/L]        | [Specific action]      | [Date]   |

COMPLIANCE ACTIONS
1. [Action] — Owner: [Name] — Due: [Date]
2. [Action] — Owner: [Name] — Due: [Date]

RESOURCE REQUIREMENTS: Budget $[X]  |  Personnel [X] hrs

APPROVAL: Regulatory _____________ Date _______ / Management _____________ Date _______
```

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-59
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Tools and References

### Scripts

| Tool | Purpose | Usage |
|------|---------|-------|
| [regulatory_tracker.py](scripts/regulatory_tracker.py) | Track submission status and timelines | `python regulatory_tracker.py` |

**Regulatory Tracker Features:**
- Track multiple submissions across markets
- Monitor status and target dates
- Identify overdue submissions
- Generate status reports

**Example usage:**
```bash
$ python regulatory_tracker.py --report status
Submission Status Report — 2024-11-01
┌──────────────────┬──────────┬────────────┬─────────────┬──────────┐
│ Product          │ Market   │ Type       │ Target Date │ Status   │
├──────────────────┼──────────┼────────────┼─────────────┼──────────┤
│ WoundScan Pro    │ USA      │ 510(k)     │ 2024-12-01  │ On Track │
│ WoundScan Pro    │ EU       │ MDR IIb    │ 2025-03-01  │ At Risk  │
│ CardioMonitor X1 │ Canada   │ Class II   │ 2025-01-15  │ On Track │
└──────────────────┴──────────┴────────────┴─────────────┴──────────┘
1 submission at risk: WoundScan Pro EU — NB engagement not confirmed.
```

### References

| Document | Content |
|----------|---------|
| [fda-submission-guide.md](references/fda-submission-guide.md) | FDA pathways, requirements, review process |
| [eu-mdr-submission-guide.md](references/eu-mdr-submission-guide.md) | MDR classification, technical documentation, clinical evidence |
| [global-regulatory-pathways.md](references/global-regulatory-pathways.md) | Canada, Japan, China, Australia, Brazil requirements |
| [iso-regulatory-requirements.md](references/iso-regulatory-requirements.md) | ISO 13485, 14971, 10993, IEC 62304, 62366 requirements |

### Key Performance Indicators

| KPI | Target | Calculation |
|-----|--------|-------------|
| First-time approval rate | >85% | (Approved without major deficiency / Total submitted) × 100 |
| On-time submission | >90% | (Submitted by target date / Total submissions) × 100 |
| Review cycle compliance | >95% | (Responses within deadline / Total requests) × 100 |
| Regulatory hold time | <20% | (Days on hold / Total review days) × 100 |

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-60
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

---
type: skill
lifecycle: stable
inheritance: inheritable
name: risk-management-specialist
description: Medical device risk management specialist implementing ISO 14971 throughout product lifecycle. Provides risk analysis, risk evaluation, risk control, and post-production information analysis. Use w...
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Risk Management Specialist

ISO 14971:2019 risk management implementation throughout the medical device lifecycle.

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-62
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Risk Management Planning Workflow

Establish risk management process per ISO 14971.

### Workflow: Create Risk Management Plan

1. Define scope of risk management activities:
   - Medical device identification
   - Lifecycle stages covered
   - Applicable standards and regulations
2. Establish risk acceptability criteria:
   - Define probability categories (P1-P5)
   - Define severity categories (S1-S5)
   - Create risk matrix with acceptance thresholds
3. Assign responsibilities:
   - Risk management lead
   - Subject matter experts
   - Approval authorities
4. Define verification activities:
   - Methods for control verification
   - Acceptance criteria
5. Plan production and post-production activities:
   - Information sources
   - Review triggers
   - Update procedures
6. Obtain plan approval
7. Establish risk management file
8. **Validation:** Plan approved; acceptability criteria defined; responsibilities assigned; file established

### Risk Management Plan Content

| Section | Content | Evidence |
|---------|---------|----------|
| Scope | Device and lifecycle coverage | Scope statement |
| Criteria | Risk acceptability matrix | Risk matrix document |
| Responsibilities | Roles and authorities | RACI chart |
| Verification | Methods and acceptance | Verification plan |
| Production/Post-Production | Monitoring activities | Surveillance plan |

### Risk Acceptability Matrix (5x5)

| Probability \ Severity | Negligible | Minor | Serious | Critical | Catastrophic |
|------------------------|------------|-------|---------|----------|--------------|
| **Frequent (P5)** | Medium | High | High | Unacceptable | Unacceptable |
| **Probable (P4)** | Medium | Medium | High | High | Unacceptable |
| **Occasional (P3)** | Low | Medium | Medium | High | High |
| **Remote (P2)** | Low | Low | Medium | Medium | High |
| **Improbable (P1)** | Low | Low | Low | Medium | Medium |

### Risk Level Actions

| Level | Acceptable | Action Required |
|-------|------------|-----------------|
| Low | Yes | Document and accept |
| Medium | ALARP | Reduce if practicable; document rationale |
| High | ALARP | Reduction required; demonstrate ALARP |
| Unacceptable | No | Design change mandatory |

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-63
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Risk Evaluation Workflow

Evaluate risks against acceptability criteria.

### Workflow: Evaluate Identified Risks

1. Calculate initial risk level from probability × severity
2. Compare to risk acceptability criteria
3. For each risk, determine:
   - Acceptable: Document and accept
   - ALARP: Proceed to risk control
   - Unacceptable: Mandatory risk control
4. Document evaluation rationale
5. Identify risks requiring benefit-risk analysis
6. Complete benefit-risk analysis if applicable
7. Compile risk evaluation summary
8. **Validation:** All risks evaluated; acceptability determined; rationale documented

### Risk Evaluation Decision Tree

```
Risk Estimated
      │
      ▼
Apply Acceptability Criteria
      │
      ├── Low Risk ──────────► Accept and document
      │
      ├── Medium Risk ───────► Consider risk reduction
      │   │                    Document ALARP if not reduced
      │   ▼
      │   Practicable to reduce?
      │   │
      │   Yes──► Implement control
      │   No───► Document ALARP rationale
      │
      ├── High Risk ─────────► Risk reduction required
      │   │                    Must demonstrate ALARP
      │   ▼
      │   Implement control
      │   Verify residual risk
      │
      └── Unacceptable ──────► Design change mandatory
                               Cannot proceed without control
```

### ALARP Demonstration Requirements

| Criterion | Evidence Required |
|-----------|-------------------|
| Technical feasibility | Analysis of alternative controls |
| Proportionality | Cost-benefit of further reduction |
| State of the art | Comparison to similar devices |
| Stakeholder input | Clinical/user perspectives |

### Benefit-Risk Analysis Triggers

| Situation | Benefit-Risk Required |
|-----------|----------------------|
| Residual risk remains high | Yes |
| No feasible risk reduction | Yes |
| Novel device | Yes |
| Unacceptable risk with clinical benefit | Yes |
| All risks low | No |

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-64
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Post-Production Risk Management

Monitor and update risk management throughout product lifecycle.

### Workflow: Post-Production Risk Monitoring

1. Identify information sources:
   - Customer complaints
   - Service reports
   - Vigilance/adverse events
   - Literature monitoring
   - Clinical studies
2. Establish collection procedures
3. Define review triggers:
   - New hazard identified
   - Increased frequency of known hazard
   - Serious incident
   - Regulatory feedback
4. Analyze incoming information for risk relevance
5. Update risk management file as needed
6. Communicate significant findings
7. Conduct periodic risk management review
8. **Validation:** Information sources monitored; file current; reviews completed per schedule

### Information Sources

| Source | Information Type | Review Frequency |
|--------|------------------|------------------|
| Complaints | Use issues, failures | Continuous |
| Service | Field failures, repairs | Monthly |
| Vigilance | Serious incidents | Immediate |
| Literature | Similar device issues | Quarterly |
| Regulatory | Authority feedback | As received |
| Clinical | PMCF data | Per plan |

### Risk Management File Update Triggers

| Trigger | Response Time | Action |
|---------|---------------|--------|
| Serious incident | Immediate | Full risk review |
| New hazard identified | 30 days | Risk analysis update |
| Trend increase | 60 days | Trend analysis |
| Design change | Before implementation | Impact assessment |
| Standards update | Per transition period | Gap analysis |

### Periodic Review Requirements

| Review Element | Frequency |
|----------------|-----------|
| Risk management file completeness | Annual |
| Risk control effectiveness | Annual |
| Post-market information analysis | Quarterly |
| Risk-benefit conclusions | Annual or on new data |

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-65
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Tools and References

### Scripts

| Tool | Purpose | Usage |
|------|---------|-------|
| [risk_matrix_calculator.py](scripts/risk_matrix_calculator.py) | Calculate risk levels and FMEA RPN | `python risk_matrix_calculator.py --help` |

**Risk Matrix Calculator Features:**
- ISO 14971 5x5 risk matrix calculation
- FMEA RPN (Risk Priority Number) calculation
- Interactive mode for guided assessment
- Display risk criteria definitions
- JSON output for integration

### References

| Document | Content |
|----------|---------|
| [iso14971-implementation-guide.md](references/iso14971-implementation-guide.md) | Complete ISO 14971:2019 implementation with templates |
| [risk-analysis-methods.md](references/risk-analysis-methods.md) | FMEA, FTA, HAZOP, Use Error Analysis methods |

### Quick Reference: ISO 14971 Process

| Stage | Key Activities | Output |
|-------|----------------|--------|
| Planning | Define scope, criteria, responsibilities | Risk Management Plan |
| Analysis | Identify hazards, estimate risk | Hazard Analysis |
| Evaluation | Compare to criteria, ALARP assessment | Risk Evaluation |
| Control | Implement hierarchy, verify | Risk Control Records |
| Residual | Overall assessment, benefit-risk | Risk Management Report |
| Production | Monitor, review, update | Updated RM File |

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-66
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

---
type: skill
lifecycle: stable
inheritance: inheritable
name: soc2-compliance
description: Use when the user asks to prepare for SOC 2 audits, map Trust Service Criteria, build control matrices, collect audit evidence, perform gap analysis, or assess SOC 2 Type I vs Type II readiness."
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# SOC 2 Compliance

SOC 2 Type I and Type II compliance preparation for SaaS companies. Covers Trust Service Criteria mapping, control matrix generation, evidence collection, gap analysis, and audit readiness assessment.

## Table of Contents

- [Overview](#overview)
- [Trust Service Criteria](#trust-service-criteria)
- [Control Matrix Generation](#control-matrix-generation)
- [Gap Analysis Workflow](#gap-analysis-workflow)
- [Evidence Collection](#evidence-collection)
- [Audit Readiness Checklist](#audit-readiness-checklist)
- [Vendor Management](#vendor-management)
- [Continuous Compliance](#continuous-compliance)
- [Anti-Patterns](#anti-patterns)
- [Tools](#tools)
- [References](#references)
- [Cross-References](#cross-references)

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-68
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Trust Service Criteria

SOC 2 is organized around five Trust Service Criteria (TSC) categories. **Security** is required for every SOC 2 report; the remaining four are optional and selected based on business need.

### Security (Common Criteria CC1-CC9) — Required

The foundation of every SOC 2 report. Maps to COSO 2013 principles.

| Criteria | Domain | Key Controls |
|----------|--------|-------------|
| **CC1** | Control Environment | Integrity/ethics, board oversight, org structure, competence, accountability |
| **CC2** | Communication & Information | Internal/external communication, information quality |
| **CC3** | Risk Assessment | Risk identification, fraud risk, change impact analysis |
| **CC4** | Monitoring Activities | Ongoing monitoring, deficiency evaluation, corrective actions |
| **CC5** | Control Activities | Policies/procedures, technology controls, deployment through policies |
| **CC6** | Logical & Physical Access | Access provisioning, authentication, encryption, physical restrictions |
| **CC7** | System Operations | Vulnerability management, anomaly detection, incident response |
| **CC8** | Change Management | Change authorization, testing, approval, emergency changes |
| **CC9** | Risk Mitigation | Vendor/business partner risk management |

### Availability (A1) — Optional

| Criteria | Focus | Key Controls |
|----------|-------|-------------|
| **A1.1** | Capacity management | Infrastructure scaling, resource monitoring, capacity planning |
| **A1.2** | Recovery operations | Backup procedures, disaster recovery, BCP testing |
| **A1.3** | Recovery testing | DR drills, failover testing, RTO/RPO validation |

**Select when:** Customers depend on your uptime; you have SLAs; downtime causes direct business impact.

### Confidentiality (C1) — Optional

| Criteria | Focus | Key Controls |
|----------|-------|-------------|
| **C1.1** | Identification | Data classification policy, confidential data inventory |
| **C1.2** | Protection | Encryption at rest and in transit, DLP, access restrictions |
| **C1.3** | Disposal | Secure deletion procedures, media sanitization, retention enforcement |

**Select when:** You handle trade secrets, proprietary data, or contractually confidential information.

### Processing Integrity (PI1) — Optional

| Criteria | Focus | Key Controls |
|----------|-------|-------------|
| **PI1.1** | Accuracy | Input validation, processing checks, output verification |
| **PI1.2** | Completeness | Transaction monitoring, reconciliation, error handling |
| **PI1.3** | Timeliness | SLA monitoring, processing delay alerts, batch job monitoring |
| **PI1.4** | Authorization | Processing authorization controls, segregation of duties |

**Select when:** Data accuracy is critical (financial processing, healthcare records, analytics platforms).

### Privacy (P1-P8) — Optional

| Criteria | Focus | Key Controls |
|----------|-------|-------------|
| **P1** | Notice | Privacy policy, data collection notice, purpose limitation |
| **P2** | Choice & Consent | Opt-in/opt-out, consent management, preference tracking |
| **P3** | Collection | Minimal collection, lawful basis, purpose specification |
| **P4** | Use, Retention, Disposal | Purpose limitation, retention schedules, secure disposal |
| **P5** | Access | Data subject access requests, correction rights |
| **P6** | Disclosure & Notification | Third-party sharing, breach notification |
| **P7** | Quality | Data accuracy verification, correction mechanisms |
| **P8** | Monitoring & Enforcement | Privacy program monitoring, complaint handling |

**Select when:** You process PII and customers expect privacy assurance (complements GDPR compliance).

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-69
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Gap Analysis Workflow

### Phase 1: Current State Assessment

1. **Document existing controls** — inventory all security policies, procedures, and technical controls
2. **Map to TSC** — align existing controls to Trust Service Criteria
3. **Collect evidence samples** — gather proof that controls exist and operate
4. **Interview control owners** — verify understanding and execution

### Phase 2: Gap Identification

Run `gap_analyzer.py` against your current controls to identify:

- **Missing controls** — TSC criteria with no corresponding control
- **Partially implemented** — Control exists but lacks evidence or consistency
- **Design gaps** — Control designed but does not adequately address the criteria
- **Operating gaps** (Type II only) — Control designed correctly but not operating effectively

### Phase 3: Remediation Planning

For each gap, define:

| Field | Description |
|-------|-------------|
| Gap ID | Reference identifier |
| TSC Criteria | Affected criteria |
| Gap Description | What is missing or insufficient |
| Remediation Action | Specific steps to close the gap |
| Owner | Person responsible for remediation |
| Priority | Critical / High / Medium / Low |
| Target Date | Completion deadline |
| Dependencies | Other gaps or projects that must complete first |

### Phase 4: Timeline Planning

| Priority | Target Remediation |
|----------|--------------------|
| Critical | 2-4 weeks |
| High | 4-8 weeks |
| Medium | 8-12 weeks |
| Low | 12-16 weeks |

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-70
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Audit Readiness Checklist

### Pre-Audit Preparation (4-6 Weeks Before)

- [ ] All controls documented with descriptions, owners, and frequencies
- [ ] Evidence collected for the entire observation period (Type II)
- [ ] Control matrix reviewed and gaps remediated
- [ ] Policies signed and distributed within the last 12 months
- [ ] Access reviews completed within the required frequency
- [ ] Vulnerability scans current (no critical/high unpatched > SLA)
- [ ] Incident response plan tested within the last 12 months
- [ ] Vendor risk assessments current for all subservice organizations
- [ ] DR/BCP tested and documented within the last 12 months
- [ ] Employee security training completed for all staff

### Readiness Scoring

| Score | Rating | Meaning |
|-------|--------|---------|
| 90-100% | Audit Ready | Proceed with confidence |
| 75-89% | Minor Gaps | Address before scheduling audit |
| 50-74% | Significant Gaps | Remediation required |
| < 50% | Not Ready | Major program build-out needed |

### Common Audit Findings

| Finding | Root Cause | Prevention |
|---------|-----------|-----------|
| Incomplete access reviews | Manual process, no reminders | Automate quarterly review triggers |
| Missing change approvals | Emergency changes bypass process | Define emergency change procedure with post-hoc approval |
| Stale vulnerability scans | Scanner misconfigured | Automated weekly scans with alerting |
| Policy not acknowledged | No tracking mechanism | Annual e-signature workflow |
| Missing vendor assessments | No vendor inventory | Maintain vendor register with review schedule |

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-71
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Continuous Compliance

### From Point-in-Time to Continuous

| Aspect | Point-in-Time | Continuous |
|--------|---------------|-----------|
| Evidence collection | Manual, before audit | Automated, ongoing |
| Control monitoring | Periodic review | Real-time dashboards |
| Drift detection | Found during audit | Alert-based, immediate |
| Remediation | Reactive | Proactive |
| Audit preparation | 4-8 week scramble | Always ready |

### Implementation Steps

1. **Automate evidence gathering** — cron jobs, API integrations, IaC snapshots
2. **Build control dashboards** — aggregate control status into a single view
3. **Configure drift alerts** — notify when controls fall out of compliance
4. **Establish review cadence** — weekly control owner check-ins, monthly steering
5. **Maintain evidence repository** — centralized, timestamped, auditor-accessible

### Annual Re-Assessment Cycle

| Quarter | Activities |
|---------|-----------|
| Q1 | Annual risk assessment, policy refresh, vendor reassessment launch |
| Q2 | Internal control testing, remediation of findings |
| Q3 | Pre-audit readiness review, evidence completeness check |
| Q4 | External audit, management assertion, report distribution |

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-72
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Tools

### Control Matrix Builder

Generates a SOC 2 control matrix from selected TSC categories.

```bash
# Generate full security matrix in markdown
python scripts/control_matrix_builder.py --categories security --format md

# Generate matrix for multiple categories as JSON
python scripts/control_matrix_builder.py --categories security,availability,confidentiality --format json

# All categories, CSV output
python scripts/control_matrix_builder.py --categories security,availability,confidentiality,processing-integrity,privacy --format csv
```

### Evidence Tracker

Tracks evidence collection status per control.

```bash
# Check evidence status from a control matrix
python scripts/evidence_tracker.py --matrix controls.json --status

# JSON output for integration
python scripts/evidence_tracker.py --matrix controls.json --status --json
```

### Gap Analyzer

Analyzes current controls against SOC 2 requirements and identifies gaps.

```bash
# Type I gap analysis
python scripts/gap_analyzer.py --controls current_controls.json --type type1

# Type II gap analysis (includes operating effectiveness)
python scripts/gap_analyzer.py --controls current_controls.json --type type2 --json
```

---
type: skill
lifecycle: stable
inheritance: inheritable
name: regulatory-quality-management-skill-73
description: Skill from regulatory-quality-management plugin
tier: extended
applyTo: '**/*regulatory*,**/*fda*,**/*iso*,**/*compliance*,**/*capa*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Cross-References

- **[gdpr-dsgvo-expert](../gdpr-dsgvo-expert/SKILL.md)** — SOC 2 Privacy criteria overlaps significantly with GDPR requirements; use together when processing EU personal data
- **[information-security-manager-iso27001](../information-security-manager-iso27001/SKILL.md)** — ISO 27001 Annex A controls map closely to SOC 2 Security criteria; organizations pursuing both can share evidence
- **[isms-audit-expert](../isms-audit-expert/SKILL.md)** — Audit methodology and finding management patterns transfer directly to SOC 2 audit preparation
