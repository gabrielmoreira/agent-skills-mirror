---
type: skill
lifecycle: stable
inheritance: inheritable
name: legal-compliance
description: Legal research, contract analysis, regulatory compliance, and case law citation for legal professionals.
tier: extended
applyTo: '**/*legal*,**/*compliance*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Legal Compliance Skill


> Legal research, contract analysis, regulatory compliance, and case law citation for legal professionals.

## Core Principle

Legal work demands precision. Every clause, citation, and compliance check protects against real-world consequences. The standard is accuracy, not speed.

## Legal Research

### Primary Sources (Binding Authority)

| Source | Scope | Example |
|--------|-------|---------|
| **Statutes** | Legislative law | 26 U.S.C. § 501(c)(3) |
| **Regulations** | Agency rules | 45 C.F.R. § 164.502 (HIPAA) |
| **Case Law** | Court opinions | *Marbury v. Madison*, 5 U.S. 137 (1803) |
| **Constitutional** | Foundational law | U.S. Const. amend. XIV |

### Secondary Sources (Persuasive)

- Legal treatises and hornbooks
- Law review articles
- Restatements of the Law
- Legal encyclopedias (Am. Jur., C.J.S.)

### Citation Format (Bluebook)

```
Case:       Party v. Party, Volume Reporter Page (Court Year)
Statute:    Title Source § Section (Year)
Regulation: Volume C.F.R. § Section (Year)
```

**AI guardrail**: Never fabricate case citations. Always verify case name, volume, reporter, page, court, and year against a legal database.

## Contract Analysis

### Key Contract Elements

1. **Parties** — Who is bound?
2. **Consideration** — What is exchanged?
3. **Terms** — Duration, renewal, termination triggers
4. **Representations & Warranties** — What each party guarantees
5. **Indemnification** — Who bears risk of loss?
6. **Limitation of Liability** — Caps on damages
7. **Governing Law** — Which jurisdiction's law applies
8. **Dispute Resolution** — Litigation vs. arbitration vs. mediation

### Red Flag Checklist

| Red Flag | Risk | Action |
|----------|------|--------|
| Unlimited liability | Uncapped exposure | Negotiate cap |
| Auto-renewal without notice | Lock-in | Add notice period |
| Broad indemnification | Asymmetric risk | Narrow scope |
| Non-compete > 2 years | Enforceability risk | Reduce duration |
| Unilateral amendment rights | Loss of control | Require mutual consent |

### Contract Review Tracker

```json
{
  "contract": "SaaS Agreement v2.1",
  "counterparty": "Vendor Inc.",
  "effective_date": "2026-05-01",
  "review_status": "in_progress",
  "issues": [
    {
      "section": "7.2",
      "clause": "Limitation of Liability",
      "finding": "Cap excludes gross negligence carve-out",
      "severity": "high",
      "recommendation": "Add carve-out for gross negligence and willful misconduct",
      "resolved": false
    },
    {
      "section": "12.1",
      "clause": "Auto-renewal",
      "finding": "30-day notice period too short",
      "severity": "medium",
      "recommendation": "Negotiate to 90 days",
      "resolved": true
    }
  ]
}
```

## Regulatory Compliance Frameworks

### Cross-Industry

| Framework | Domain | Key Requirements |
|-----------|--------|-----------------|
| **GDPR** | Data privacy (EU) | Consent, right to erasure, DPO, 72hr breach notification |
| **CCPA/CPRA** | Data privacy (CA) | Opt-out of sale, right to delete, annual risk assessments |
| **SOX** | Financial reporting | Internal controls, CEO/CFO certification, audit trail |
| **ADA** | Accessibility | Reasonable accommodation, website accessibility |

### Industry-Specific

| Framework | Industry | Focus |
|-----------|----------|-------|
| **HIPAA** | Healthcare | PHI protection, minimum necessary, BAAs |
| **PCI-DSS** | Payments | Cardholder data, encryption, access controls |
| **FERPA** | Education | Student records, directory information |
| **GLBA** | Financial | Customer financial privacy, safeguards |
| **COPPA** | Children's data | Parental consent, data minimization |

## Intellectual Property

### IP Type Quick Reference

| Type | Protects | Duration | Registration |
|------|----------|----------|-------------|
| **Copyright** | Original creative works | Life + 70 years | Automatic (registration strengthens) |
| **Trademark** | Brand identifiers | Indefinite (with use) | Optional but recommended |
| **Patent** | Inventions/processes | 20 years (utility) | Required |
| **Trade Secret** | Confidential business info | Indefinite (if secret) | No registration; protect via NDA |

### AI-Generated Content IP Considerations

- Copyright Office position: AI-generated content without human authorship is not copyrightable
- Works with significant human creative input may qualify
- Always document the human creative contribution in the process

## Legal Document Drafting

### Structure of a Legal Memorandum

1. **Question Presented** — The specific legal issue
2. **Short Answer** — Direct conclusion
3. **Statement of Facts** — Relevant facts only
4. **Discussion** — IRAC analysis (Issue, Rule, Application, Conclusion)
5. **Conclusion** — Recommendation with confidence level

### Plain Language Principles

- Avoid legalese where clarity serves the reader
- Define terms on first use
- Use active voice for obligations ("Licensor shall deliver" not "delivery shall be made")
- One concept per sentence in critical provisions

## Compliance Monitoring

### Compliance Program Elements

1. **Policies & Procedures** — Written, accessible, current
2. **Training** — Role-based, annual, documented
3. **Monitoring** — Regular audits and spot checks
4. **Reporting** — Whistleblower channels, incident response
5. **Enforcement** — Consistent disciplinary actions
6. **Documentation** — Retain records per retention schedule

### Retention Schedule Guidelines

| Document Type | Typical Retention |
|--------------|------------------|
| Contracts | Life of agreement + 6 years |
| Tax records | 7 years |
| Employment records | 7 years post-termination |
| Corporate minutes | Permanent |
| Litigation hold | Until hold lifted |
