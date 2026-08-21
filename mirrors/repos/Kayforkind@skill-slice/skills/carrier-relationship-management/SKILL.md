---
name: carrier-relationship-management
description: "Manages freight carrier portfolios: lane RFPs, linehaul/accessorial/FSC negotiation, 3-deep routing guides, five-metric scorecards, FMCSA SAFER vetting, and spot-versus-contract mix. Trigger when awarding lanes, scorecarding carriers, or deciding contract vs spot. Not for ocean or air cargo booking, last-mile courier apps, or building a TMS product."
version: 1.0.1
risk: safe
source: https://github.com/ai-evos/agent-skills
date_added: '2026-02-27'
---

## When to Use

Use this skill when you are **designing or tuning your carrier portfolio, routing guides, and freight procurement strategy**:

- Running freight RFPs, renegotiating contract and fuel tables, or balancing spot vs. contract exposure.
- Building carrier scorecards, exit criteria, and escalation protocols to manage performance and risk.
- Deciding how to allocate lanes across asset carriers, brokers, and regional specialists to protect service while controlling logistics spend.
- Vetting carrier FMCSA compliance, insurance minimums, and safety ratings before onboarding.
- Conducting carrier performance reviews, corrective action discussions, or rate negotiation conversations.

Trigger keywords: carrier RFP, freight rate negotiation, routing guide, carrier scorecard, tender acceptance, FMCSA compliance, spot vs. contract, carrier portfolio, accessorial charges, fuel surcharge, carrier exit, double-brokering, lane allocation.

## Prerequisites

- Access to a TMS (transportation management system) or rate management platform for historical shipment data extraction.
- Market intelligence subscriptions: DAT RateView and/or Greenscreens for lane-level benchmarking.
- FMCSA SAFER portal access (https://safer.fmcsa.dot.gov/) for carrier compliance vetting.
- 12 months of shipment history (lane, volume, spend, service levels) for RFP preparation.
- Carrier onboarding portal or tracking system for document collection (insurance certificates, authority, W-9).

## Procedure

### 1. Carrier Portfolio Assessment

1. **Extract 12 months of shipment data** from your TMS. Group by lane (origin 3-digit zip → destination 3-digit zip), carrier, and equipment type. Capture: total loads, total spend, average rate/mile, OTD %, tender acceptance %, claims $, invoice accuracy %.
2. **Classify each lane** by volume tier:
   - High volume: >10 loads/week
   - Medium volume: 2–10 loads/week
   - Low volume: <2 loads/week
3. **Identify problem lanes** where current rates exceed DAT benchmark by >15%, OTD is below 90%, or tender acceptance is below 80%.
4. **Map carrier concentration** per lane. Flag any lane where a single carrier handles >40% of volume.
5. **Calculate portfolio mix** (asset vs. broker vs. niche). Target: 60–70% asset, 20–30% broker, 5–15% niche/specialty. Flag if outside these ranges.

### 2. Rate Negotiation

1. **Benchmark each lane** against DAT RateView (market average) and Greenscreens (carrier-specific). Record the spread between your current contract rate and benchmark.
2. **Decompose your current rate** into components: base linehaul, fuel surcharge (FSC), accessorials, minimums. Negotiate each independently — bundling obscures overpayment.
3. **Model total cost across diesel price scenarios** ($3.50, $4.00, $4.50/gal) to expose FSC manipulation. A carrier quoting low linehaul with an aggressive FSC table can exceed a higher linehaul with standard DOE-indexed FSC.
4. **Prepare the opening position** with data: "DAT shows this lane averaging $2.15/mile over the last 90 days. Our current contract is $2.45. We'd like to discuss alignment." Never say "your rate is too high."
5. **Negotiate base rate** to within ±8% of DAT benchmark. Meet in the middle on linehaul; negotiate harder on accessorials and FSC table.
6. **Negotiate accessorial free time** aggressively — driver detention is the #1 source of invoice disputes. Standard: 2 hours free, then $50–$100/hr. For LTL, watch reweigh/reclass fees ($25–$75) and cubic capacity surcharges.
7. **Document the FSC table** explicitly: base price trigger (diesel price = 0% FSC), increment (e.g., $0.01/mile per $0.05 diesel increase), index lag (weekly vs. monthly).
8. **For LTL:** negotiate discount off published tariff (typically 70–85% for mid-volume shippers). Negotiate minimum charge ($75–$150) separately for short-haul lanes.

### 3. Freight RFP Execution

1. **Pre-RFP (Weeks 1–2):** Analyze 12 months of shipment data. Identify lanes by volume, spend, and current service levels. Flag underperforming lanes and lanes where rates exceed market benchmarks. Set targets: cost reduction %, service level minimums, carrier diversity goals.
2. **RFP design (Weeks 3–4):** Include lane-level detail (origin/destination zip, volume range, required equipment, special handling), transit time expectations, accessorial requirements, payment terms, insurance minimums ($1M minimum), and evaluation criteria with weightings. Require lane-by-lane bidding — reject portfolio bids ("5% off everything") as they hide cross-subsidization.
3. **Bid distribution (Week 5):** Send to 3–5 carriers per lane (incumbents + prospects). Allow 2 weeks for bid preparation.
4. **Bid evaluation (Weeks 7–8):** Weight cost at 40–50%, service history at 25–30%, capacity commitment at 15–20%, operational fit at 10–15%. A carrier 3% above lowest bid with 97% OTD and 95% tender acceptance is cheaper than the lowest bidder with 85% OTD and 70% tender acceptance.
5. **Award (Week 9):** Award in waves — primary carriers first, then secondary. Give carriers 2–3 weeks to operationalize new lanes before tendering begins.
6. **Implementation (Weeks 10–12):** Run a 30-day parallel period where old and new routing guides overlap. Cut over cleanly after validation.

### 4. Carrier Scorecarding

1. **Track these 5 core metrics** per carrier per lane (do not exceed 5 — a scorecard with 20 metrics gets ignored):
   - **On-time delivery (OTD):** ≥95% target, <90% red flag. Measure pickup and delivery separately.
   - **Tender acceptance rate:** ≥90% for primary carriers, <80% red flag. Below 75% on a contract lane means the rate is below market — renegotiate or reallocate.
   - **Claims ratio:** <0.5% of spend target, >1.0% red flag. Track frequency separately from severity.
   - **Invoice accuracy:** ≥97% target, <93% red flag. Below 90% triggers corrective action.
   - **Tender-to-pickup time:** Within 2 hours of requested pickup for FTL. Late pickups after acceptance indicate "soft rejecting."
2. **Review scorecards monthly** with the carrier management team. Share quarterly with carriers.
3. **Trigger corrective action** when any metric crosses the red flag threshold for 30+ days. Present scorecard, identify specific metrics, request a 30/60/90-day corrective action plan with clear consequences.

### 5. Routing Guide Construction

1. **For lanes with >2 loads/week:** Build a 3-deep routing guide.
   - Primary: target 80%+ tender acceptance, awarded ~60–75% of volume.
   - Secondary: target 70%+ acceptance on overflow.
   - Tertiary: price ceiling — often a broker whose rate is the "do not exceed" for spot procurement.
2. **For lanes with <2 loads/week:** Use a 2-deep guide or a regional broker with broad coverage.
3. **Award enough volume per carrier per lane to matter:** A carrier running 2 loads/week will prioritize you over a shipper giving 2 loads/month.
4. **Never give one carrier more than 40% of any single lane.** For top 20 lanes by volume, maintain at least 3 active carriers.

### 6. FMCSA Compliance Vetting

1. **Verify operating authority** at https://safer.fmcsa.dot.gov/. Check MC (Motor Carrier) or FF (Freight Forwarder) number is active and "authorized for" the correct commodity type (property vs. household goods).
2. **Verify insurance minimums** through the FMCSA Insurance tab — not just the certificate the carrier provides (certificates can be forged or outdated). Require $1M minimum from all carriers regardless of commodity (FMCSA minimum of $750K doesn't cover a serious accident). Hazmat requires $1M; household goods requires $5M per FMCSA §387.9.
3. **Check safety rating:** Never use a carrier with an Unsatisfactory rating. Conditional carriers require case-by-case evaluation. For unrated carriers (the majority), check CSA scores — focus on Unsafe Driving, Hours-of-Service, and Vehicle Maintenance BASICs. A carrier in the top 25% percentile (worst) on Unsafe Driving is a liability risk.
4. **For brokers:** Verify $75K surety bond or trust fund is active via the FMCSA Bond/Trust tab. Verify the broker has contingent cargo insurance.
5. **Re-vet quarterly.** An "authorized" status unchanged for 12+ months may indicate operational inactivity.
6. **Red flags for financial distress:** delayed driver settlements, frequent insurance underwriter changes, bond amount dropping, Carrier411/CarrierOK complaints spiking. Reduce exposure incrementally — don't wait for failure.

### 7. Spot vs. Contract Decision

1. **Stay on contract when:** spread between contract and spot is <10%; volume is consistent and predictable; capacity is tightening (spot rates rising); lane is customer-critical with tight windows.
2. **Go to spot when:** spot rates are >15% below contract rate (soft market); lane is irregular (<1 load/week); you need one-time surge capacity; contract carrier is consistently rejecting tenders (they're pricing you into spot anyway).
3. **Renegotiate contract when:** spread vs. DAT benchmark exceeds 15% for 60+ consecutive days; tender acceptance drops below 75% for 30 days; significant volume change alters lane economics.
4. **Healthy portfolio target:** 75–85% contract, 15–25% spot. More than 30% spot means your routing guide is failing.

### 8. Carrier Exit

Remove a carrier from the active routing guide when any threshold is met **after documented corrective action has failed**:

- OTD below 85% for 60 consecutive days
- Tender acceptance below 70% for 30 consecutive days with no communication
- Claims ratio exceeds 2% of spend for 90 days
- FMCSA authority revoked, insurance lapsed, or safety rating downgraded to Unsatisfactory
- Invoice accuracy below 88% for 90 days after corrective notice
- Discovery of double-brokering your freight
- Evidence of financial distress: bond revocation, driver complaints on CarrierOK or Carrier411, unexplained service collapse

### 9. Communication and Performance Reviews

1. **Rate negotiation tone:** Lead with data, not demands. Frame as partnership alignment, not cost-cutting. Share volume forecasts and growth plans. Ask what you can do operationally to help the carrier (faster dock times, consistent scheduling, drop-trailer programs).
2. **Positive reviews:** Be specific and tie to dollar impact. "Your 97% OTD on Chicago–Dallas saved ~$45K in expedite costs this quarter. We're increasing your allocation from 60% to 75%."
3. **Corrective reviews:** Lead with data, present the scorecard, identify specific metrics below threshold. Request a corrective action plan with 30/60/90-day timeline. Set clear consequence: "If OTD doesn't reach 92% by the 60-day mark, we'll shift 50% of volume to an alternate carrier."

For full communication templates with variables and tone guidance, load [communication-templates.md](references/communication-templates.md) when preparing for a carrier call, rate negotiation, or performance review.

## Pitfalls

- **Bundling rate components:** Negotiating a single "all-in" rate obscures where you overpay. Always decompose into linehaul, FSC, accessorials, and minimums. A low linehaul with an aggressive FSC table can exceed a higher linehaul with standard DOE-indexed FSC.
- **Awarding on price alone:** The lowest bidder with 85% OTD and 70% tender acceptance costs more than a carrier 3% above lowest bid with 97% OTD and 95% tender acceptance. Service failures cost more than rate differences.
- **Single-carrier lane concentration:** Giving one carrier >40% of a critical lane creates catastrophic risk if they exit or fail. For top 20 lanes, maintain at least 3 active carriers.
- **Ignoring FSC table structure:** A carrier quoting a low base rate with an aggressive FSC schedule inflates total cost above market. Always model total cost across $3.50, $4.00, and $4.50/gal diesel scenarios.
- **Accepting carrier-provided insurance certificates without FMCSA verification:** Certificates can be forged or outdated. Always verify through the FMCSA Insurance tab.
- **Treating all claims equally:** A carrier with one $50K claim is different from one with fifty $1K claims. Track claims frequency separately from severity — the latter indicates systemic handling problems.
- **Ignoring "soft rejections":** Carriers that accept tenders but consistently pick up late are holding your load while shopping for better freight. Track tender-to-pickup time, not just acceptance rate.
- **Disputing detention charges without addressing root cause:** When detention charges exceed 5% of a carrier's total billing, the root cause is usually shipper facility operations, not carrier overcharging. Address the operational issue first — or lose the carrier.
- **Letting carriers discover volume shortfalls at invoice time:** If your volume dropped 40%, proactively renegotiate. Letting carriers find out at invoice time destroys trust.
- **Using unrated carriers without checking CSA scores:** The majority of carriers are "unrated" by FMCSA. Use CSA BASICs scores instead — focus on Unsafe Driving, Hours-of-Service, and Vehicle Maintenance.
- **Awarding contracts at cycle peaks or troughs:** Budget RFP timing to award during market transitions for more realistic rates. Awarding at the peak locks in inflated rates; at the trough, carriers may default when the market tightens.
- **Ignoring double-brokering signals:** If the truck that arrives isn't from the carrier on your BOL, the insurance chain may be broken. Do not accept the load if it hasn't departed. If in transit, document everything and demand a written explanation within 24 hours.

For the comprehensive edge case library with full analysis, load [edge-cases.md](references/edge-cases.md) when encountering unusual situations: hurricane capacity squeeze, double-brokering discovery, volume-loss renegotiation, carrier financial distress, mega-carrier acquisition of niche partner, FSC manipulation, or detention disputes at scale.

## Verification

### Portfolio Health Checks

| Metric                                           | Target         | Red Flag                 |
| ------------------------------------------------ | -------------- | ------------------------ |
| Contract rate vs. DAT benchmark                  | Within ±8%     | >15% premium or discount |
| Routing guide compliance (% freight on guide)    | ≥85%           | <70%                     |
| Primary tender acceptance                         | ≥90%           | <80%                     |
| Weighted average OTD across portfolio            | ≥95%           | <90%                     |
| Carrier portfolio claims ratio                   | <0.5% of spend | >1.0%                    |
| Average carrier invoice accuracy                 | ≥97%           | <93%                     |
| Spot freight percentage                          | <20%           | >30%                     |
| RFP cycle time (launch to implementation)        | ≤12 weeks      | >16 weeks                |

### Escalation Triggers

| Trigger                                                           | Action                                           | Timeline        |
| ----------------------------------------------------------------- | ------------------------------------------------ | --------------- |
| Carrier tender acceptance drops below 70% for 2 consecutive weeks | Notify procurement, schedule carrier call        | Within 48 hours |
| Spot spend exceeds 30% of lane budget for any lane                | Review routing guide, initiate carrier sourcing  | Within 1 week   |
| Carrier FMCSA authority or insurance lapses                       | Immediately suspend tendering, notify operations | Within 1 hour   |
| Single carrier controls >50% of a critical lane                   | Initiate secondary carrier qualification         | Within 2 weeks  |
| Claims ratio exceeds 1.5% for any carrier for 60+ days            | Schedule formal performance review               | Within 1 week   |
| Rate variance >20% from DAT benchmark on 5+ lanes                 | Initiate contract renegotiation or mini-bid      | Within 2 weeks  |
| Carrier reports driver shortage or service disruption             | Activate backup carriers, increase monitoring    | Within 4 hours  |
| Double-brokering confirmed on any load                            | Immediate carrier suspension, compliance review  | Within 2 hours  |

### Escalation Chain

Analyst → Transportation Manager (48 hours) → Director of Transportation (1 week) → VP Supply Chain (persistent issue or >$100K exposure)

### Quick Verification Commands

1. **FMCSA authority check:** Navigate to https://safer.fmcsa.dot.gov/ → enter MC/FF/DOT number → verify "Operating Status: AUTHORIZED" and "Authorized for: Property" (or appropriate commodity).
2. **Insurance verification:** Same FMCSA SAFER page → "Insurance" tab → verify active policy with $1M+ coverage and current expiration date.
3. **DAT benchmark comparison:** Pull DAT RateView lane rate → compare to current contract rate → calculate spread: `((contract_rate - dat_rate) / dat_rate) * 100`. Flag if >15%.
4. **Routing guide compliance:** From TMS, run report: loads tendered on-guide vs. off-guide for the period → calculate: `(on_guide_loads / total_loads) * 100`. Flag if <70%.
5. **Carrier concentration check:** From TMS, group loads by lane and carrier → identify any lane where a single carrier's share >40%.

## Additional Resources

- For detailed decision frameworks on rate negotiation, portfolio optimization, and RFP execution, load [decision-frameworks.md](references/decision-frameworks.md) when building a new lane strategy, deciding consolidation vs. diversification, or structuring spot vs. contract allocation.
- For the comprehensive edge case library with full analysis, load [edge-cases.md](references/edge-cases.md) when encountering unusual or high-risk situations (hurricane capacity squeeze, double-brokering, volume-loss renegotiation, carrier financial distress, mega-carrier acquisition, FSC manipulation, detention disputes at scale).
- For complete communication templates with variables and tone guidance, load [communication-templates.md](references/communication-templates.md) when preparing for carrier calls, rate negotiations, performance reviews, or corrective action discussions.

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
