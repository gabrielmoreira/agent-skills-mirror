---
type: skill
lifecycle: stable
inheritance: inheritable
name: journalism
description: News writing, investigative reporting, source verification, editorial standards, and fact-checking for journalists.
tier: extended
applyTo: '**/*journalism*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Journalism Skill


> News writing, investigative reporting, source verification, editorial standards, and fact-checking for journalists.

## Core Principle

Journalism's job is to tell the truth as completely and fairly as possible. Every story serves the public's right to know. Accuracy is non-negotiable — speed is secondary.

## News Writing Fundamentals

### The Inverted Pyramid

1. **Lead (Lede)** — Most important facts: Who, What, When, Where, Why, How
2. **Key details** — Context, quotes, supporting evidence
3. **Background** — History, related events, lesser details

The reader should get the essential story from the first paragraph alone.

### Lead Types

| Type | Use When | Example Pattern |
|------|----------|----------------|
| **Hard news** | Breaking/spot news | WHO did WHAT at WHERE on WHEN |
| **Delayed** | Feature/narrative | Scene-setting, character introduction |
| **Summary** | Complex stories | Synthesize multiple elements |
| **Anecdotal** | Human interest | Start with one person's experience |
| **Question** | Rarely (avoid) | Only when genuinely provocative |

### AP Style Quick Reference

| Rule | Correct | Incorrect |
|------|---------|-----------|
| Numbers < 10 | five people | 5 people |
| Numbers ≥ 10 | 15 people | fifteen people |
| State abbreviations | Calif., Texas | CA, TX (except datelines) |
| Titles before name | President Biden | president Biden |
| Titles after name | Joe Biden, president | Joe Biden, President |
| Time | 3 p.m. | 3 PM, 3:00 p.m. |
| Dates | March 9, 2026 | March 9th, 2026 |

## Source Verification

### Source Hierarchy

| Tier | Source Type | Reliability | Verification Need |
|------|-----------|-------------|-------------------|
| 1 | Primary documents | Highest | Authenticate provenance |
| 2 | Direct witnesses/participants | High | Corroborate with second source |
| 3 | Expert analysis | Medium-High | Confirm credentials, check for conflicts |
| 4 | Secondary reports (other media) | Medium | Verify independently before citing |
| 5 | Anonymous sources | Variable | Editor approval, corroboration required |
| 6 | Social media posts | Low | Verify identity, context, authenticity |

### Two-Source Rule

- Every factual claim should be confirmed by at least two independent sources
- Independent = not derived from the same original source
- Exceptions: official documents, on-record statements, direct observation

### Fact-Check Tracker

```yaml
story: "City council approves budget"
deadline: "2026-04-14 18:00"
claims:
  - claim: "Budget is $4.2 billion"
    sources:
      - type: "Primary document"
        ref: "Budget proposal PDF"
        verified: true
      - type: "Official statement"
        ref: "Finance director quote"
        verified: true
    status: "confirmed"
  - claim: "Largest increase in 10 years"
    sources:
      - type: "City records"
        ref: "Historical budget data"
        verified: true
      - type: "Secondary"
        ref: "2016 Observer article"
        verified: false
    status: "pending verification"
```

### Source Attribution

| Attribution | Use When |
|------------|----------|
| **On the record** | Default — named source, direct quotes |
| **On background** | Information usable, source described but not named |
| **Deep background** | Information usable, no attribution at all |
| **Off the record** | Cannot be used in any form (establish BEFORE conversation) |

**Always**: Clarify attribution terms before the conversation, not after.

## Fact-Checking Protocol

### Pre-Publication Checklist

1. ☐ All names spelled correctly (verify against official sources)
2. ☐ All numbers verified (dates, statistics, amounts, addresses)
3. ☐ All quotes accurate (audio/transcript confirmed)
4. ☐ Claims attributed to sources or verified independently
5. ☐ Headline accurately reflects story content
6. ☐ Context provided for statistics (base rate, time period, methodology)
7. ☐ Opposing viewpoints sought and included where relevant
8. ☐ Potential defamation reviewed (truth, public interest, fair comment)

### Statistical Literacy

| Red Flag | Question to Ask |
|----------|----------------|
| Percentage without base | Percent of what? (10% of 10 vs. 10% of 10M) |
| Correlation claimed as causation | What confounders exist? |
| Cherry-picked time period | What does the full dataset show? |
| Survey results without methodology | Sample size? Margin of error? Who funded it? |
| "Studies show" without citation | Which study? Peer reviewed? Replicable? |

## Investigative Reporting

### Investigation Framework

1. **Hypothesis** — What do you suspect, and why?
2. **Document trail** — FOIA requests, court records, corporate filings, financial disclosures
3. **Human sources** — Insiders, whistleblowers, affected parties, experts
4. **Data analysis** — Public databases, leaked datasets, data journalism tools
5. **Pattern recognition** — Connect dots across documents, timelines, relationships
6. **Confrontation** — Give the subject fair opportunity to respond
7. **Legal review** — Pre-publication review for defamation, privacy, source protection

### Public Records Toolkit

| Record Type | Source |
|------------|--------|
| Corporate filings | SEC EDGAR, state SOS databases |
| Property records | County assessor/recorder |
| Court records | PACER (federal), state court portals |
| Campaign finance | FEC, state election commissions |
| Government contracts | USAspending.gov, SAM.gov |
| Nonprofit finances | IRS Form 990 (ProPublica Nonprofit Explorer) |
| Environmental data | EPA Enforcement, Toxic Release Inventory |

## Ethical Standards

### SPJ Code of Ethics (Four Principles)

1. **Seek truth and report it** — Accuracy, context, transparency about methods
2. **Minimize harm** — Balance public interest against potential damage
3. **Act independently** — Avoid conflicts of interest, refuse gifts
4. **Be accountable** — Acknowledge mistakes, correct promptly

### Correction Protocol

| Severity | Action |
|----------|--------|
| Minor factual error | Correction appended, original text updated |
| Significant factual error | Editor's note at top, original text updated |
| Fundamental error affecting thesis | Retraction or major revision with prominent notice |
| All corrections | Date-stamped, transparent about what changed |

## Digital & Multimedia Journalism

### Verification of Digital Content

- **Reverse image search** — Google Images, TinEye to check origin
- **EXIF data** — Check photo metadata for date, location, device
- **Geolocation** — Cross-reference landmarks, shadows, signs with claimed location
- **Video verification** — Frame analysis, audio consistency, compression artifacts
- **Social media verification** — Account age, posting history, network analysis

### Data Journalism Principles

- Show your work: publish methodology and datasets when possible
- Visualizations must not misrepresent data (avoid truncated axes, misleading scales)
- Acknowledge limitations of the data
- Peer review analysis before publication

## AI in Journalism — Guardrails

- AI can assist with: document analysis, data processing, transcription, translation
- AI must never: fabricate quotes, generate fake sources, write opinion as news
- All AI-assisted reporting must be disclosed to editors and readers
- AI-generated images must never be used as documentary evidence
- Every AI-generated draft must be verified line by line against source material
- The journalist remains solely responsible for accuracy
