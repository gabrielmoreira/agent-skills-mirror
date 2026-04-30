# Call for Offers and Bid Leveling Analyst

Compare seller-side investment sales offers, normalize key terms, and recommend whether to accept, level bidders, run BAFO, or keep backups active.

---

## When to Use This Skill

Use this skill once offers or LOIs have arrived and the seller needs a clean, structured comparison of economics, certainty, and process risk.

---

## What You'll Need to Provide

- Offer or LOI summaries
- Purchase price
- deposit and hard-money timing
- diligence duration
- financing assumptions
- closing timeline
- assignment rights
- requested credits or carveouts
- any known buyer quality / track record context

---

## Mission

Normalize competing bids into a seller decision tool and recommend the best next process step based on both economics and execution quality.

---

## Strategy

### Step 1: Build the Bid Matrix

Compare:

- price
- deposit
- hard money timing
- diligence period
- financing risk
- closing timing
- assignment flexibility
- requested economic givebacks

### Step 2: Score Certainty

Assess:

- proof of funds
- lender support where relevant
- buyer reputation or track record
- likely retrade risk

### Step 3: Recommend the Next Step

Choose:

- accept
- level top bidders
- run best and final
- maintain a backup bidder

### Step 4: Prepare the Seller Guidance

- explain the tradeoffs
- show what matters beyond price
- identify the most likely friction points if the seller picks a weaker-execution buyer

---

## Output Format

```markdown
# Offer and Bid-Leveling Analysis
## Property:
## Status: COMPLETE | PARTIAL | FAILED

### Bid Matrix
| Buyer | Price | Deposit | Hard Money | Diligence | Closing | Financing Risk | Overall View |
|------|-------|---------|------------|-----------|---------|----------------|--------------|

### Top Tradeoffs
- ...

### Recommended Next Step
- ACCEPT | LEVEL | BAFO | BACKUP STRATEGY

### Seller Guidance
- ...

### Confidence Level
HIGH | MEDIUM | LOW
```

---

## Quality Checks

- Bid comparison includes certainty, not just price
- Deposit hardening is separated from total deposit amount
- Recommendation is tied to seller objectives and live process leverage
- Potential retrade risk is explicitly discussed

---

## When Data is Missing

- If buyer quality is unclear, lower confidence and state the missing diligence
- If one or more offers are incomplete, compare only on confirmed fields and call out gaps
- If seller priorities are unclear, assume certainty and clean execution matter alongside price

---

## Confidence Scoring

| Level | Criteria |
|---|---|
| HIGH | Full bid terms and credible buyer context available |
| MEDIUM | Most terms are clear but buyer quality or diligence posture is partially unknown |
| LOW | Material gaps remain in bids or buyer credibility |

---

## Related Knowledge Bases

- [Offer Negotiation and Closing Playbook](knowledge/offer-negotiation-and-closing-playbook.md)
- [Brokerage Investment Sales Process](knowledge/brokerage-investment-sales-process.md)

## Research Basis

- [Call for Offers and Bid Leveling Analyst Research](research/brokerage/call-for-offers-and-bid-leveling-analyst-research.md)
