---
type: skill
inheritance: inheritable
lifecycle: stable
name: healthcare-informatics
description: Clinical terminology, healthcare compliance (HIPAA/HITECH), patient safety, and health data management.
tier: extended
applyTo: '**/*health*,**/*clinical*,**/*medical*,**/*patient*,**/*hipaa*,**/*ehr*,**/*pharma*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Healthcare Informatics Skill

> Clinical terminology, healthcare compliance (HIPAA/HITECH), patient safety, and health data management.

## Core Principle

Healthcare information systems exist to improve patient outcomes. Every data decision balances access (clinicians need information) against privacy (patients deserve protection). When in doubt, protect the patient.

## HIPAA Compliance

### Protected Health Information (PHI)
PHI is any individually identifiable health information. The 18 HIPAA identifiers:

| # | Identifier | Example |
|---|-----------|---------|
| 1 | Names | Full name |
| 2 | Geographic data | Address, ZIP (3-digit OK if population >20K) |
| 3 | Dates | DOB, admission, discharge, death (year OK) |
| 4 | Phone numbers | All |
| 5 | Fax numbers | All |
| 6 | Email addresses | All |
| 7 | SSN | All |
| 8 | Medical record numbers | All |
| 9 | Health plan beneficiary numbers | All |
| 10 | Account numbers | All |
| 11 | Certificate/license numbers | All |
| 12 | Vehicle identifiers | VIN, plates |
| 13 | Device identifiers/serial numbers | All |
| 14 | Web URLs | All |
| 15 | IP addresses | All |
| 16 | Biometric identifiers | Fingerprints, voice |
| 17 | Full-face photographs | All |
| 18 | Any other unique identifying number | All |

### De-identification Methods
| Method | Approach | Use When |
|--------|----------|----------|
| **Safe Harbor** | Remove all 18 identifiers | Standard approach, lower risk |
| **Expert Determination** | Statistical/scientific analysis | Need richer dataset, qualified expert available |

### Minimum Necessary Standard
- Use or disclose only the minimum PHI necessary for the purpose
- Role-based access controls in EHR systems
- Audit logs for every PHI access

## HITECH Act Extensions

| Requirement | Detail |
|------------|--------|
| Breach notification | 60 days for breaches affecting 500+ individuals |
| Business Associate liability | BAs directly liable for HIPAA violations |
| Audit trail | All access to electronic PHI must be logged |
| Encryption safe harbor | Encrypted data breach = not a reportable breach |

### FHIR Patient Resource Example

```json
{
  "resourceType": "Patient",
  "id": "example",
  "identifier": [
    {
      "system": "http://hospital.org/mrn",
      "value": "12345"
    }
  ],
  "name": [
    {
      "use": "official",
      "family": "Doe",
      "given": ["John"]
    }
  ],
  "gender": "male",
  "birthDate": "1985-06-15",
  "address": [
    {
      "use": "home",
      "city": "Springfield",
      "state": "IL",
      "postalCode": "62704"
    }
  ]
}
```

## Clinical Terminology Standards

### Key Coding Systems
| System | Purpose | Example |
|--------|---------|---------|
| **ICD-10** | Diagnosis codes | E11.9 (Type 2 diabetes without complications) |
| **CPT** | Procedure codes | 99213 (Office visit, established patient) |
| **SNOMED CT** | Clinical terms | 73211009 (Diabetes mellitus) |
| **LOINC** | Lab/observation codes | 2345-7 (Glucose, serum/plasma) |
| **RxNorm** | Medications | Metformin 500mg oral tablet |
| **NDC** | Drug packaging | 10-digit national drug code |

### Interoperability Standards
| Standard | Role |
|----------|------|
| **HL7 FHIR** | RESTful API for health data exchange |
| **HL7 v2** | Legacy messaging (ADT, ORM, ORU) |
| **CDA/C-CDA** | Structured clinical documents |
| **DICOM** | Medical imaging format and protocol |
| **X12 EDI** | Insurance claims (837), eligibility (270/271) |

## Electronic Health Records (EHR)

### Core EHR Functions
1. **Clinical Documentation** — Progress notes, assessments, plans
2. **CPOE** — Computerized Provider Order Entry (meds, labs, imaging)
3. **CDS** — Clinical Decision Support (alerts, reminders, pathways)
4. **Results Management** — Lab values, imaging reports
5. **Medication Management** — e-Prescribing, interaction checks, reconciliation

### Patient Safety Checks
| Check | Purpose |
|-------|---------|
| Drug-drug interactions | Prevent harmful combinations |
| Drug-allergy alerts | Match known allergies |
| Dose range checking | Flag outlier dosages |
| Duplicate order detection | Prevent redundant tests/meds |
| Clinical pathway adherence | Evidence-based care protocols |

## Healthcare Data Analytics

### Quality Measures
| Measure Type | Example | Source |
|-------------|---------|--------|
| **Process** | % of diabetics with annual HbA1c | HEDIS |
| **Outcome** | 30-day readmission rate | CMS |
| **Patient Experience** | HCAHPS survey scores | CMS |
| **Structure** | EHR adoption rate, nurse-to-patient ratio | Various |

### Risk Adjustment
- HCC (Hierarchical Condition Categories) for Medicare risk scoring
- Comorbidity indices (Charlson, Elixhauser) for severity adjustment
- Social Determinants of Health (SDOH) as contextual factors

## Research & Clinical Trials

### IRB Requirements
| Element | Requirement |
|---------|------------|
| Informed consent | Written, plain language, voluntary |
| Risk minimization | Reasonable procedures, minimal risk where possible |
| Privacy protections | De-identification or limited datasets |
| Vulnerable populations | Extra safeguards for children, prisoners, pregnant women |

### Clinical Trial Phases
| Phase | Purpose | Size |
|-------|---------|------|
| Phase I | Safety, dosage | 20–100 |
| Phase II | Efficacy, side effects | 100–300 |
| Phase III | Confirm efficacy, monitor adverse | 1,000–3,000 |
| Phase IV | Post-market surveillance | Thousands |

## AI in Healthcare — Guardrails

**Critical**: AI-generated medical information must never be presented as clinical advice.
- Always include disclaimer: "This is informational only. Consult a healthcare professional."
- Never diagnose or recommend treatment
- Flag when confidence is low or data is ambiguous
- Cite clinical guidelines (USPSTF, ACC/AHA, IDSA) when referencing evidence-based practices
- Document provenance of any clinical data used in analysis
