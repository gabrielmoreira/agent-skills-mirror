# Industrial Financing Fit

Identify the most plausible lender categories and financing structures for a U.S. industrial acquisition or recapitalization.

---

## When to Use This Skill

Use this skill when you need to decide whether the subject industrial deal fits bank, life company, CMBS, bridge, or owner-user SBA execution. It is most useful after preliminary underwriting, when lease durability and asset quality are clearer but before formal lender outreach begins.

---

## What You'll Need to Provide

- Property address and subtype
- Occupancy and WALT
- Major tenant and concentration summary
- Purchase price or value
- Requested leverage or equity structure
- Financing objective:
  - cheapest permanent debt
  - flexible transitional debt
  - owner-user financing
- Sponsor profile if known

---

## Mission

Match the subject industrial deal to the most plausible lender categories, explain why, and identify what makes the deal stronger or weaker for each financing path.

---

## Strategy

### Step 1: Classify the Deal

Identify whether the deal is:

- stabilized
- near-roll
- lease-up
- transitional / repositioning
- owner-user

### Step 2: Test Permanent-Debt Fit

Assess:

- lease durability
- tenant quality
- building quality
- market liquidity
- sponsor credibility

### Step 3: Test Transitional-Debt Fit

Assess:

- upcoming rollover
- CapEx plan
- lease-up plan
- timing risk
- need for future funding or structure flexibility

### Step 4: Match to Lender Types

Evaluate fit for:

- bank
- life company
- CMBS
- bridge / debt fund
- SBA 504 owner-user edge case

### Step 5: Compare Execution Tradeoffs

For each lender type, summarize:

- likely fit level
- key strengths
- likely concerns
- why it is or is not a good first-call lender type

---

## Output Format

```markdown
# Industrial Financing Fit
## Property:
## Status: COMPLETE | PARTIAL | FAILED

### Deal Classification
- Stabilized / Transitional / Owner-User:
- Key Drivers:

### Lender Fit Matrix
| Lender Type | Fit | Why It Fits | Key Concern |
|-------------|-----|-------------|-------------|
| Bank | STRONG | | |
| Life Company | MODERATE | | |
| CMBS | MODERATE | | |
| Bridge / Debt Fund | LOW | | |
| SBA 504 | NOT APPLICABLE | | |

### Recommended Path
1. ...
2. ...

### Financing Risks
- ...

### Confidence Level
HIGH | MEDIUM | LOW
```

---

## Quality Checks

- The skill distinguishes stabilized vs transitional execution
- SBA 504 is used only as an owner-user carve-out
- The recommendation explains why the lender fit is strong or weak
- The output addresses both pricing logic and execution certainty

---

## When Data is Missing

- If lease durability is unclear, avoid overcommitting to permanent-debt fit
- If sponsor profile is unknown, frame that as a lender-risk variable
- If requested leverage is unknown, recommend likely lender lanes rather than specific proceeds

---

## Confidence Scoring

| Level | Criteria |
|---|---|
| HIGH | Deal profile, rollover, and financing objective are all clear |
| MEDIUM | Core asset profile is known but some sponsor or lease details are incomplete |
| LOW | Financing fit depends on missing lease, sponsor, or property-quality information |

---

## Related Knowledge Bases

- [Industrial Lender Criteria](knowledge/industrial-lender-criteria.md)
- [Industrial Benchmarks](knowledge/industrial-benchmarks.md)

## Research Basis

- [Industrial Financing Fit Research](research/industrial/industrial-financing-fit-research.md)
